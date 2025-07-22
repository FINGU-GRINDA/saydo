"use client"

import { useState, useEffect } from "react"
import { DashboardHeader } from "@/components/saydo/dashboard/dashboard-header"
import { BottomNavBar } from "@/components/saydo/layout/bottom-nav-bar"
import { HomeScreen } from "@/components/saydo/screens/home-screen"
import AgentSettingsScreen from "@/components/saydo/screens/agent-settings-screen"
import { VoiceCommandModal } from "@/components/saydo/dashboard/voice-command-modal"
import { LoginModal } from "@/components/auth/login-modal"
import { useAuth } from "@/lib/contexts/auth-context"
import { useMeetings } from "@/lib/hooks/use-api"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"
import type { HistoryItem } from "@/lib/types"

export type ActiveTab = "home" | "agent"

// Convert meeting data to history items
function convertMeetingsToHistory(meetings: any[]): HistoryItem[] {
  return meetings.map(meeting => ({
    id: meeting.session_id || meeting.id, // Use session_id for the link, fallback to meeting id
    title: meeting.title || 'Untitled Meeting',
    timestamp: new Date(meeting.created_at || meeting.createdAt),
    duration: calculateDuration(meeting.start_time, meeting.end_time),
    type: 'meeting' as const,
    summary: meeting.summary || 'No summary available',
    pendingActions: meeting.actions?.some((action: any) => action.status === 'pending') || false
  }))
}

function calculateDuration(startTime?: string, endTime?: string): string {
  if (!startTime || !endTime) return '0m'
  
  const start = new Date(startTime)
  const end = new Date(endTime)
  const diffMs = end.getTime() - start.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  
  if (diffMins < 60) {
    return `${diffMins}m`
  } else {
    const hours = Math.floor(diffMins / 60)
    const mins = diffMins % 60
    return `${hours}h ${mins}m`
  }
}

export default function SaydoApp() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("home")
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false)
  const [showLoginModal, setShowLoginModal] = useState(false)
  
  const { user, isLoading: authLoading, isAuthenticated } = useAuth()
  const { data: meetings = [], isLoading: meetingsLoading } = useMeetings()
  const { toast } = useToast()

  // Show login modal when not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      setShowLoginModal(true)
    } else {
      setShowLoginModal(false)
    }
  }, [authLoading, isAuthenticated])

  // Handle Google connection success redirect
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const connected = urlParams.get('connected')
      const status = urlParams.get('status')
      
      if (connected === 'google' && status === 'success') {
        toast({
          title: "Google Account Connected!",
          description: "You can now use Calendar, Gmail, and other Google services.",
        })
        
        // Switch to agent settings to show the connected state
        setActiveTab('agent')
        
        // Clean up URL parameters
        window.history.replaceState({}, '', window.location.pathname)
      }
    }
  }, [toast])

  // Convert meetings to history format
  const history = convertMeetingsToHistory(meetings)

  const renderContent = () => {
    if (meetingsLoading) {
      return (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading your meetings...</span>
        </div>
      )
    }

    switch (activeTab) {
      case "agent":
        return <AgentSettingsScreen />
      case "home":
      default:
        return <HomeScreen history={history} />
    }
  }

  // Show loading screen while auth is loading
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading Saydo...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <div className="max-w-2xl mx-auto p-4 sm:p-6 pb-24">
          <DashboardHeader 
            onOpenSettings={() => setActiveTab("agent")}
            user={user}
          />
          {renderContent()}
        </div>
        <BottomNavBar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onCommandClick={() => setIsVoiceModalOpen(true)}
        />
        <VoiceCommandModal isOpen={isVoiceModalOpen} onOpenChange={setIsVoiceModalOpen} />
      </div>
      
      <LoginModal 
        isOpen={showLoginModal} 
        onOpenChange={setShowLoginModal}
      />
    </>
  )
}
