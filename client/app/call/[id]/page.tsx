"use client"

import { useState, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/lib/contexts/auth-context"
import { apiClient } from "@/lib/api-client"
import { ArrowLeft, Mic, MicOff, Square, Play, Upload, Calendar, Mail, CheckCircle, Clock, Users, ExternalLink, RefreshCw } from "lucide-react"
import Link from "next/link"
import ReactMarkdown from "react-markdown"

interface MeetingSession {
  id: string
  meetUrl: string
  status: 'preparing' | 'recording' | 'processing' | 'completed'
  startTime: Date
  endTime?: Date
  transcript: string
  summary?: string
  actions: Array<{
    id: string
    type: string
    description: string
    status: 'pending' | 'completed'
    details?: any
  }>
  meetingId?: string  // Add meeting ID field
}

export default function CallPage() {
  const params = useParams()
  const sessionId = params.id as string
  const { user } = useAuth()
  const { toast } = useToast()
  
  const [meetUrl, setMeetUrl] = useState("")
  const [session, setSession] = useState<MeetingSession | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [isRetryingAI, setIsRetryingAI] = useState(false)
  const [loading, setLoading] = useState(true)
  
  // WebRTC and WebSocket connections
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const websocketRef = useRef<WebSocket | null>(null)
  const audioWebSocketRef = useRef<WebSocket | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // Load existing session on mount
  useEffect(() => {
    if (sessionId && sessionId !== 'new') {
      loadSession(sessionId)
    } else {
      setLoading(false)
    }
  }, [sessionId])

  const loadSession = async (id: string) => {
    try {
      setLoading(true)
      const sessionData = await apiClient.getSession(id)
      
      // Convert date strings to Date objects
      const processedSession = {
        ...sessionData,
        startTime: sessionData.startTime ? new Date(sessionData.startTime) : new Date(),
        endTime: sessionData.endTime ? new Date(sessionData.endTime) : undefined,
        meetingId: sessionData.meetingId  // Include meeting ID
      }
      
      setSession(processedSession)
      if (sessionData.transcript) {
        setTranscript(sessionData.transcript)
      }
      if (sessionData.status === 'recording') {
        setIsRecording(true)
      }
    } catch (error) {
      console.error('Failed to load session:', error)
      toast({
        title: "Session Not Found",
        description: "The requested session could not be found.",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    return () => {
      // Cleanup WebSocket connections
      if (websocketRef.current) {
        websocketRef.current.close()
      }
      if (audioWebSocketRef.current) {
        audioWebSocketRef.current.close()
      }
    }
  }, [])

  const handleJoinMeeting = async () => {
    if (!meetUrl.trim()) {
      toast({
        title: "Missing Meeting URL",
        description: "Please enter a Google Meet URL to join.",
        variant: "destructive"
      })
      return
    }

    try {
      // Create meeting bot session via API
      const response = await apiClient.createBotSession(meetUrl.trim())

      const newSession: MeetingSession = {
        id: response.session_id,
        meetUrl: meetUrl.trim(),
        status: 'preparing',
        startTime: new Date(),
        transcript: '',
        actions: []
      }

      setSession(newSession)
      
      // The bot is automatically joining the meeting and starting recording
      setIsRecording(true)
      
      toast({
        title: "AI Bot Joining Meeting",
        description: "Your AI assistant is joining the Google Meet and will start recording automatically.",
      })

      // Redirect to the session-specific URL
      window.history.replaceState(null, '', `/call/${response.session_id}`)

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create meeting session.",
        variant: "destructive"
      })
    }
  }

  const stopRecording = async () => {
    if (!session) return

    try {
      setIsRecording(false)
      setSession(prev => prev ? { ...prev, status: 'processing', endTime: new Date() } : null)

      toast({
        title: "Stopping AI Bot",
        description: "AI assistant is leaving the meeting and processing transcript...",
      })

      // Stop the bot session via API
      const result = await apiClient.stopBotSession(session.id)
      
      // Update session with results
      setSession(prev => prev ? {
        ...prev,
        status: 'completed',
        summary: result.summary,
        actions: result.actions || []
      } : null)

      setTranscript(result.transcript || "")

      toast({
        title: "Meeting Processed",
        description: `Generated summary and ${result.actions?.length || 0} AI-suggested actions.`,
      })

    } catch (error) {
      toast({
        title: "Processing Error",
        description: "Failed to process meeting. Please try again.",
        variant: "destructive"
      })
      console.error('Stop recording error:', error)
    }
  }

  const executeAction = async (actionId: string) => {
    if (!session) return

    try {
      // Execute action via bot API
      const result = await apiClient.executeBotAction(session.id, actionId)
      
      toast({
        title: "Action Executed",
        description: result.message || "AI action completed successfully.",
      })
      
      // Update action status
      setSession(prev => prev ? {
        ...prev,
        actions: prev.actions.map(action => 
          action.id === actionId 
            ? { ...action, status: result.status || 'completed' }
            : action
        )
      } : null)

    } catch (error) {
      toast({
        title: "Execution Error",
        description: "Failed to execute action.",
        variant: "destructive"
      })
    }
  }

  const retryAIProcessing = async () => {
    const transcriptText = session?.transcript || transcript
    if (!session || !transcriptText || isRetryingAI) return

    setIsRetryingAI(true)
    
    try {
      // Reload session to get the meeting ID
      const sessionData = await apiClient.getSession(sessionId)
      const meetingId = sessionData.meetingId
      
      if (!meetingId) {
        throw new Error("Meeting ID not found in session data")
      }
      
      // Call the process transcript API with the meeting ID
      const result = await apiClient.processTranscript(meetingId, { text: transcriptText })
      
      // Update session with new summary and actions
      setSession(prev => prev ? {
        ...prev,
        summary: result.summary,
        actions: result.actions || []
      } : null)

      toast({
        title: "AI Processing Complete",
        description: "Successfully regenerated summary and actions.",
      })
      
    } catch (error) {
      console.error('Failed to retry AI processing:', error)
      toast({
        title: "Processing Failed",
        description: "Failed to regenerate summary and actions. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsRetryingAI(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading session...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
            <ArrowLeft className="h-6 w-6" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Google Meet AI Bot</h1>
            <p className="text-gray-600">Join meetings and automate follow-ups</p>
          </div>
        </div>

        {!session ? (
          /* Join Meeting Form */
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Join Google Meet
              </CardTitle>
              <CardDescription>
                Enter a Google Meet URL to have your AI agent join and record
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Input
                  placeholder="https://meet.google.com/xxx-xxxx-xxx"
                  value={meetUrl}
                  onChange={(e) => setMeetUrl(e.target.value)}
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button 
                onClick={handleJoinMeeting}
                className="w-full"
                disabled={!meetUrl.trim()}
              >
                Deploy AI Bot to Meeting
              </Button>
            </CardFooter>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {/* Recording Controls */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {isRecording ? <Mic className="h-5 w-5 text-red-500" /> : <MicOff className="h-5 w-5 text-gray-500" />}
                  Meeting Recording
                </CardTitle>
                <CardDescription>
                  Status: <Badge variant={session.status === 'recording' ? 'default' : 'secondary'}>
                    {session.status}
                  </Badge>
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm text-gray-600">
                  <p>Meeting URL: <span className="text-blue-600 break-all">{session.meetUrl}</span></p>
                  <p>Started: {session.startTime.toLocaleTimeString()}</p>
                  {session.endTime && <p>Ended: {session.endTime.toLocaleTimeString()}</p>}
                </div>
                
                {transcript && (
                  <div className="bg-gray-100 p-3 rounded max-h-40 overflow-y-auto border">
                    <p className="text-sm text-gray-800 font-mono">{transcript}</p>
                  </div>
                )}
              </CardContent>
              <CardFooter className="gap-2">
                {isRecording && session.status !== 'completed' ? (
                  <Button 
                    onClick={stopRecording}
                    className="flex-1 bg-red-600 hover:bg-red-700"
                    variant="destructive"
                  >
                    <Square className="h-4 w-4 mr-2" />
                    Stop Bot & Process
                  </Button>
                ) : session.status === 'completed' ? (
                  <div className="flex-1 flex items-center justify-center gap-2 text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-sm">Bot Session Complete</span>
                  </div>
                ) : null}
                
                <Button 
                  variant="outline" 
                  onClick={() => window.open(session.meetUrl, '_blank')}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open Meet
                </Button>
              </CardFooter>
            </Card>

            {/* AI Actions */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>AI Actions</CardTitle>
                    <CardDescription>
                      Review and approve AI-suggested actions from the meeting
                    </CardDescription>
                  </div>
                  {(session?.transcript || transcript) && (
                    <Button
                      onClick={retryAIProcessing}
                      disabled={isRetryingAI}
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-2"
                    >
                      <RefreshCw className={`h-4 w-4 ${isRetryingAI ? 'animate-spin' : ''}`} />
                      {isRetryingAI ? 'Processing...' : 'Retry AI'}
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {session.summary && (
                  <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
                    <h4 className="font-medium text-blue-900 mb-2">Meeting Summary</h4>
                    <div className="text-sm text-blue-800 prose prose-sm max-w-none">
                      <ReactMarkdown>{session.summary}</ReactMarkdown>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  {session.actions.length === 0 && session.status !== 'completed' && (
                    <p className="text-gray-500 text-sm">Actions will appear after processing...</p>
                  )}
                  
                  {session.actions.map((action) => (
                    <div key={action.id} className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                      <div className="flex items-center gap-2">
                        {action.type === 'email' && <Mail className="h-4 w-4 text-blue-600" />}
                        {action.type === 'calendar_event' && <Calendar className="h-4 w-4 text-green-600" />}
                        {action.type === 'todo' && <CheckCircle className="h-4 w-4 text-purple-600" />}
                        {action.type === 'sheet_update' && <Clock className="h-4 w-4 text-orange-600" />}
                        {action.type === 'document_create' && <ExternalLink className="h-4 w-4 text-indigo-600" />}
                        <div className="flex-1">
                          <p className="text-sm text-gray-900">{action.description}</p>
                          <p className="text-xs text-gray-500">{action.type.replace('_', ' ')}</p>
                        </div>
                      </div>
                      
                      {action.status === 'completed' ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => executeAction(action.id)}
                          className={`text-xs ${
                            action.type === 'calendar_event' ? 'bg-green-600 hover:bg-green-700' :
                            action.type === 'email' ? 'bg-blue-600 hover:bg-blue-700' :
                            action.type === 'todo' ? 'bg-purple-600 hover:bg-purple-700' :
                            action.type === 'sheet_update' ? 'bg-orange-600 hover:bg-orange-700' :
                            action.type === 'document_create' ? 'bg-indigo-600 hover:bg-indigo-700' :
                            ''
                          } text-white`}
                        >
                          {action.type === 'calendar_event' && '📅 Add to Calendar'}
                          {action.type === 'email' && '📧 Send Email'}
                          {action.type === 'todo' && '✅ Create Task'}
                          {action.type === 'sheet_update' && '📊 Update Sheet'}
                          {action.type === 'document_create' && '📄 Create Doc'}
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Instructions */}
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="p-4">
            <h4 className="font-medium text-gray-900 mb-2">How the AI Bot works:</h4>
            <div className="grid gap-2 text-sm text-gray-600 md:grid-cols-2">
              <div>• Enter Google Meet URL</div>
              <div>• AI Bot joins meeting automatically as participant</div>
              <div>• Bot uses Deepgram for real-time transcription</div>
              <div>• Speaker identification tracks who says what</div>
              <div>• Click "Stop Bot" when meeting ends</div>
              <div>• AI generates summary and executes enabled actions</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}