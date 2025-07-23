"use client"

import { useState, useEffect, useRef } from "react"
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
}

export default function RecordMeetingPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  
  const [meetUrl, setMeetUrl] = useState("")
  const [session, setSession] = useState<MeetingSession | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [isRetryingAI, setIsRetryingAI] = useState(false)
  
  // WebRTC and WebSocket connections
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const websocketRef = useRef<WebSocket | null>(null)
  const audioWebSocketRef = useRef<WebSocket | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // WebSocket for real-time transcription
  const connectWebSocket = (sessionId: string) => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const wsUrl = `ws://${apiUrl.replace('http://', '')}/ws/transcription/${sessionId}`
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected for transcription')
      toast({
        title: "Connected",
        description: "AI transcription service connected.",
      })
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch (data.type) {
        case 'transcript':
          handleTranscriptUpdate(data.data)
          break
        case 'speaker_change':
          handleSpeakerChange(data.data)
          break
        case 'final_transcript':
          handleFinalTranscript(data.data)
          break
        case 'error':
          toast({
            title: "Transcription Error",
            description: data.message,
            variant: "destructive"
          })
          break
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      toast({
        title: "Connection Error",
        description: "Lost connection to transcription service.",
        variant: "destructive"
      })
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }
    
    websocketRef.current = ws
  }

  const handleTranscriptUpdate = (data: any) => {
    if (data.is_final && data.transcript) {
      // Format with speaker information
      const formattedText = data.speaker_segments
        ? data.speaker_segments.map((seg: any) => 
            `Speaker ${seg.speaker + 1}: ${seg.text}`
          ).join('\n')
        : data.transcript
      
      setTranscript(prev => prev + '\n' + formattedText)
    }
  }

  const handleSpeakerChange = (data: any) => {
    console.log('Speaker change:', data)
    toast({
      title: "New Speaker Detected",
      description: `${data.speaker_label} joined the conversation`,
    })
  }

  const handleFinalTranscript = (data: any) => {
    console.log('Final transcript received:', data)
    setTranscript(data.formatted_transcript || transcript)
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

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create meeting session.",
        variant: "destructive"
      })
    }
  }

  const startRecording = async () => {
    if (!session) return

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000, // Match Deepgram requirements
          channelCount: 1    // Mono audio
        } 
      })

      // Start recording session via API
      await apiClient.request(`/bot/sessions/${session.id}/start`, {
        method: 'POST'
      })

      // Connect audio WebSocket for streaming to Deepgram
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const audioWsUrl = `ws://${apiUrl.replace('http://', '')}/ws/meeting/${session.id}/audio`
      const audioWs = new WebSocket(audioWsUrl)
      
      audioWs.onopen = () => {
        console.log('Audio WebSocket connected')
      }
      
      audioWs.onerror = (error) => {
        console.error('Audio WebSocket error:', error)
      }
      
      audioWebSocketRef.current = audioWs

      // Use MediaRecorder to stream audio in real-time
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0 && audioWs.readyState === WebSocket.OPEN) {
          // Convert blob to array buffer and send to WebSocket
          const arrayBuffer = await event.data.arrayBuffer()
          audioWs.send(arrayBuffer)
        }
      }

      // Start recording with frequent data chunks
      mediaRecorder.start(250) // Send audio every 250ms for real-time transcription
      mediaRecorderRef.current = mediaRecorder

      setIsRecording(true)
      setSession(prev => prev ? { ...prev, status: 'recording' } : null)
      
      toast({
        title: "Recording Started",
        description: "AI bot is listening with Deepgram transcription and speaker identification.",
      })

    } catch (error) {
      console.error('Recording error:', error)
      toast({
        title: "Recording Error",
        description: "Unable to access microphone or start transcription. Please check permissions.",
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
    if (!session || !session.transcript || isRetryingAI) return

    setIsRetryingAI(true)
    
    try {
      // Call the process transcript API
      const result = await apiClient.processTranscript(session.id, { text: session.transcript })
      
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

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
            <ArrowLeft className="h-6 w-6" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Saydo in Google Meet</h1>
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
                      Automated tasks generated from the meeting
                    </CardDescription>
                  </div>
                  {session?.transcript && (
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
                    <p className="text-sm text-blue-800">{session.summary}</p>
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
                        {action.type === 'calendar' && <Calendar className="h-4 w-4 text-green-600" />}
                        <div>
                          <p className="text-sm text-gray-900">{action.description}</p>
                          <p className="text-xs text-gray-500">{action.type}</p>
                        </div>
                      </div>
                      
                      {action.status === 'completed' ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => executeAction(action.id)}
                          className="text-xs"
                        >
                          Execute
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