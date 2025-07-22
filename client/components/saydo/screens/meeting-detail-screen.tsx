"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Calendar, 
  Mail, 
  FileText, 
  ListChecks,
  Users,
  Loader2,
  Play,
  X,
  Check
} from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

interface Meeting {
  id: string
  title: string
  start_time: string
  participants: string[]
  transcript: string
  summary: string
  created_at: string
}

interface Action {
  id: string
  action_type: string
  description: string
  status: "pending" | "executing" | "completed" | "failed"
  details: {
    function: string
    arguments: any
  }
  created_at: string
  result?: any
}

const getActionIcon = (actionType: string) => {
  switch (actionType) {
    case "calendar_event":
      return Calendar
    case "email":
      return Mail
    case "todo":
      return ListChecks
    case "document_create":
      return FileText
    default:
      return FileText
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "pending":
      return "bg-yellow-100 text-yellow-800"
    case "executing":
      return "bg-blue-100 text-blue-800"
    case "completed":
      return "bg-green-100 text-green-800"
    case "failed":
      return "bg-red-100 text-red-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case "pending":
      return Clock
    case "executing":
      return Loader2
    case "completed":
      return CheckCircle
    case "failed":
      return AlertCircle
    default:
      return Clock
  }
}

interface MeetingDetailScreenProps {
  meetingId: string
  onBack: () => void
}

export function MeetingDetailScreen({ meetingId, onBack }: MeetingDetailScreenProps) {
  const [meeting, setMeeting] = useState<Meeting | null>(null)
  const [actions, setActions] = useState<Action[]>([])
  const [loading, setLoading] = useState(true)
  const [executingActions, setExecutingActions] = useState<Set<string>>(new Set())
  const { toast } = useToast()

  useEffect(() => {
    loadMeetingData()
  }, [meetingId])

  const loadMeetingData = async () => {
    try {
      setLoading(true)
      const [meetingData, actionsData] = await Promise.all([
        apiClient.getMeeting(meetingId),
        apiClient.getMeetingActions(meetingId)
      ])
      
      setMeeting(meetingData)
      setActions(actionsData)
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load meeting details",
        variant: "destructive",
      })
      console.error("Error loading meeting:", error)
    } finally {
      setLoading(false)
    }
  }

  const executeAction = async (actionId: string) => {
    try {
      setExecutingActions(prev => new Set(prev).add(actionId))
      
      const result = await apiClient.executeAction(meetingId, actionId)
      
      toast({
        title: "Action Executed",
        description: result.message,
      })
      
      // Refresh actions to get updated status
      await loadMeetingData()
      
    } catch (error: any) {
      toast({
        title: "Execution Failed",
        description: error.message || "Failed to execute action",
        variant: "destructive",
      })
    } finally {
      setExecutingActions(prev => {
        const newSet = new Set(prev)
        newSet.delete(actionId)
        return newSet
      })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (!meeting) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Meeting not found</p>
        <Button variant="outline" onClick={onBack} className="mt-4">
          Go Back
        </Button>
      </div>
    )
  }

  const pendingActions = actions.filter(action => action.status === "pending")
  const completedActions = actions.filter(action => action.status === "completed")

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack}>
          ← Back to Meetings
        </Button>
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-gray-500" />
          <span className="text-sm text-gray-500">
            {meeting.participants.length} participants
          </span>
        </div>
      </div>

      {/* Meeting Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            {meeting.title}
          </CardTitle>
          <CardDescription>
            {new Date(meeting.start_time).toLocaleDateString()} at{" "}
            {new Date(meeting.start_time).toLocaleTimeString()}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Participants</h4>
            <div className="flex flex-wrap gap-2">
              {meeting.participants.map((participant, index) => (
                <Badge key={index} variant="secondary">
                  {participant}
                </Badge>
              ))}
            </div>
          </div>
          
          {meeting.summary && (
            <div>
              <h4 className="font-medium mb-2">Summary</h4>
              <p className="text-sm text-gray-600 leading-relaxed">
                {meeting.summary}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pending Actions */}
      {pendingActions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-yellow-600" />
              Pending Actions ({pendingActions.length})
            </CardTitle>
            <CardDescription>
              Review and approve these AI-suggested actions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {pendingActions.map((action) => {
              const ActionIcon = getActionIcon(action.action_type)
              const isExecuting = executingActions.has(action.id)
              
              return (
                <div key={action.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <ActionIcon className="h-4 w-4 text-gray-600" />
                    </div>
                    <div className="flex-1">
                      <h5 className="font-medium">{action.description}</h5>
                      <p className="text-sm text-gray-500 capitalize">
                        {action.action_type.replace("_", " ")}
                      </p>
                      {action.details.arguments && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-400 cursor-pointer">
                            View details
                          </summary>
                          <pre className="text-xs bg-gray-50 p-2 rounded mt-1 overflow-auto">
                            {JSON.stringify(action.details.arguments, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        onClick={() => executeAction(action.id)}
                        disabled={isExecuting}
                        className={`${
                          action.action_type === 'calendar_event' ? 'bg-green-600 hover:bg-green-700' :
                          action.action_type === 'email' ? 'bg-blue-600 hover:bg-blue-700' :
                          action.action_type === 'todo' ? 'bg-purple-600 hover:bg-purple-700' :
                          action.action_type === 'sheet_update' ? 'bg-orange-600 hover:bg-orange-700' :
                          action.action_type === 'document_create' ? 'bg-indigo-600 hover:bg-indigo-700' :
                          'bg-green-600 hover:bg-green-700'
                        } text-white`}
                      >
                        {isExecuting ? (
                          <>
                            <Loader2 className="h-3 w-3 animate-spin mr-1" />
                            Executing...
                          </>
                        ) : (
                          <>
                            {action.action_type === 'calendar_event' && '📅 Add to Calendar'}
                            {action.action_type === 'email' && '📧 Send Email'}
                            {action.action_type === 'todo' && '✅ Create Task'}
                            {action.action_type === 'sheet_update' && '📊 Update Sheet'}
                            {action.action_type === 'document_create' && '📄 Create Doc'}
                            {!['calendar_event', 'email', 'todo', 'sheet_update', 'document_create'].includes(action.action_type) && (
                              <>
                                <Play className="h-3 w-3 mr-1" />
                                Execute
                              </>
                            )}
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>
      )}

      {/* Completed Actions */}
      {completedActions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Completed Actions ({completedActions.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {completedActions.map((action) => {
              const ActionIcon = getActionIcon(action.action_type)
              const StatusIcon = getStatusIcon(action.status)
              
              return (
                <div key={action.id} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <ActionIcon className="h-4 w-4 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h5 className="font-medium text-green-800">{action.description}</h5>
                    <p className="text-sm text-green-600">Completed successfully</p>
                    {action.result && action.result.message && (
                      <p className="text-xs text-green-600 mt-1">
                        {action.result.message}
                      </p>
                    )}
                  </div>
                  <StatusIcon className="h-4 w-4 text-green-600" />
                </div>
              )
            })}
          </CardContent>
        </Card>
      )}

      {/* Transcript */}
      {meeting.transcript && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Transcript
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {meeting.transcript}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 