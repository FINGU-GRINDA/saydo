"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, Loader2, ExternalLink, AlertCircle, X } from "lucide-react"
import { useAgentPreferences, useUpdateAgentPreferences } from "@/lib/hooks/use-api"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/lib/contexts/auth-context"
import { apiClient } from "@/lib/api-client"
import {
  Calendar,
  Mail,
  UserPlus,
  FileText,
  ListChecks,
  Slack,
  TrendingUp,
  KanbanSquare,
} from "lucide-react"

const actionCategories = [
  {
    category: "Core AI",
    description: "Essential summaries and data extraction.",
    actions: [
      {
        id: "summary",
        title: "Generate Summary",
        description: "Create a concise summary of any conversation.",
        Icon: FileText,
        defaultConnected: true,
        requiresGoogleAuth: false,
      },
      {
        id: "todo",
        title: "Extract Action Items",
        description: "Pull out clear, actionable tasks from a conversation.",
        Icon: ListChecks,
        defaultConnected: true,
        requiresGoogleAuth: false,
      },
    ],
  },
  {
    category: "Communication",
    description: "Automated emails and team updates.",
    actions: [
      {
        id: "email",
        title: "Draft Follow-up Email",
        description: "Write a draft email based on the conversation.",
        Icon: Mail,
        defaultConnected: true,
        requiresGoogleAuth: true,
      },
      {
        id: "slack",
        title: "Share to Slack",
        description: "Send key summaries or updates to a Slack channel.",
        Icon: Slack,
        defaultConnected: false,
        requiresGoogleAuth: false,
      },
    ],
  },
  {
    category: "Scheduling & Tasks",
    description: "Intelligent meeting and task coordination.",
    actions: [
      {
        id: "calendar",
        title: "Schedule Meeting",
        description: "Identify and suggest meeting times with participants.",
        Icon: Calendar,
        defaultConnected: true,
        requiresGoogleAuth: true,
      },
      {
        id: "sheets",
        title: "Create Project Task",
        description: "Add a new task to a project board like Trello or Asana.",
        Icon: KanbanSquare,
        defaultConnected: false,
        requiresGoogleAuth: true,
      },
    ],
  },
  {
    category: "CRM & Sales",
    description: "Customer relationship and lead management.",
    actions: [
      {
        id: "crm",
        title: "Update CRM Contact",
        description: "Automatically update contact records with conversation notes.",
        Icon: UserPlus,
        defaultConnected: false,
        requiresGoogleAuth: false,
      },
      {
        id: "analytics",
        title: "Log Sales Activity",
        description: "Track call outcomes and update sales pipeline.",
        Icon: TrendingUp,
        defaultConnected: false,
        requiresGoogleAuth: false,
      },
    ],
  },
]

export default function AgentSettingsScreen() {
  const { user } = useAuth()
  const { toast } = useToast()
  const { data: preferences, isLoading, error } = useAgentPreferences()
  const updatePreferences = useUpdateAgentPreferences()
  const [isConnectingGoogle, setIsConnectingGoogle] = useState(false)
  const [isDisconnectingGoogle, setIsDisconnectingGoogle] = useState(false)
  const [googleConnected, setGoogleConnected] = useState(false)

  // Check if user has Google credentials
  useEffect(() => {
    if (user) {
      // Check if user has google_credentials set
      setGoogleConnected(!!user.google_credentials)
    }
  }, [user])

  const handleConnectGoogle = async () => {
    setIsConnectingGoogle(true)
    try {
      const response = await apiClient.getGoogleConnectUrl()
      // Redirect to Google OAuth for connecting (not login)
      window.location.href = response.authorization_url
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to connect to Google. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsConnectingGoogle(false)
    }
  }

  const handleDisconnectGoogle = async () => {
    setIsDisconnectingGoogle(true)
    try {
      await apiClient.disconnectGoogle()
      setGoogleConnected(false)
      
      // Refresh user data
      window.location.reload()
      
      toast({
        title: "Success",
        description: "Google account disconnected successfully. Please reconnect to use Google features.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to disconnect Google account. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsDisconnectingGoogle(false)
    }
  }

  const handleToggleCapability = async (capabilityId: string, enabled: boolean) => {
    if (!preferences) return

    const updatedCapabilities = preferences.capabilities.map((cap: any) =>
      cap.id === capabilityId ? { ...cap, enabled } : cap
    )

    try {
      await updatePreferences.mutateAsync({
        capabilities: updatedCapabilities,
      })

      toast({
        title: enabled ? "Capability enabled" : "Capability disabled",
        description: `${capabilityId} has been ${enabled ? "enabled" : "disabled"}.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update capability. Please try again.",
        variant: "destructive",
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Failed to load agent preferences</p>
      </div>
    )
  }

  const getCapabilityStatus = (actionId: string) => {
    return preferences?.capabilities?.find((cap: any) => cap.id === actionId)?.enabled || false
  }

  const canEnableCapability = (action: any) => {
    if (!action.requiresGoogleAuth) return true
    return googleConnected
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">AI Capabilities</h2>
        <p className="text-muted-foreground mt-2">
          Connect new skills to your agent to expand its automation powers.
        </p>
      </div>

      {/* Google OAuth Status */}
      <Card className="border-blue-200 bg-blue-50/50">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Mail className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-lg">Google Account Connection</CardTitle>
              <CardDescription>
                Required for calendar scheduling and email drafting capabilities
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardFooter>
          {googleConnected ? (
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm font-medium">Connected to Google</span>
              </div>
              <Button 
                onClick={handleDisconnectGoogle}
                disabled={isDisconnectingGoogle}
                variant="outline"
                size="sm"
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                {isDisconnectingGoogle ? (
                  <>
                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                    Disconnecting...
                  </>
                ) : (
                  <>
                    <X className="h-3 w-3 mr-1" />
                    Disconnect
                  </>
                )}
              </Button>
            </div>
          ) : (
            <Button 
              onClick={handleConnectGoogle}
              disabled={isConnectingGoogle}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isConnectingGoogle ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Connecting...
                </>
              ) : (
                <>
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Connect Google Account
                </>
              )}
            </Button>
          )}
        </CardFooter>
      </Card>

      {actionCategories.map((category) => (
        <div key={category.category} className="space-y-4">
          <div>
            <h3 className="text-xl font-semibold">{category.category}</h3>
            <p className="text-sm text-muted-foreground">{category.description}</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {category.actions.map((action) => {
              const isEnabled = getCapabilityStatus(action.id)
              const canEnable = canEnableCapability(action)
              const requiresAuth = action.requiresGoogleAuth && !googleConnected

              return (
                <Card key={action.id} className="relative">
                  <CardHeader className="pb-4">
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <action.Icon className="h-5 w-5 text-gray-600" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-base flex items-center gap-2">
                          {action.title}
                          {action.requiresGoogleAuth && (
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                              Google
                            </span>
                          )}
                        </CardTitle>
                        <CardDescription className="text-sm mt-1">
                          {action.description}
                        </CardDescription>
                        {requiresAuth && (
                          <div className="flex items-center gap-1 mt-2 text-amber-600">
                            <AlertCircle className="h-3 w-3" />
                            <span className="text-xs">Requires Google connection</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardHeader>

                  <CardFooter className="pt-0">
                    <Button
                      variant={isEnabled && canEnable ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleToggleCapability(action.id, !isEnabled)}
                      disabled={!canEnable || updatePreferences.isPending}
                      className={isEnabled && canEnable ? "bg-green-600 hover:bg-green-700" : ""}
                    >
                      {updatePreferences.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : (isEnabled && canEnable) ? (
                        <CheckCircle className="h-4 w-4 mr-2" />
                      ) : null}
                      {(isEnabled && canEnable) ? "Connected" : requiresAuth ? "Requires Google" : "Connect"}
                    </Button>
                  </CardFooter>
                </Card>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
