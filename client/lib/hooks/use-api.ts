import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// Query Keys
export const queryKeys = {
  user: ['user'] as const,
  meetings: ['meetings'] as const,
  meeting: (id: string) => ['meeting', id] as const,
  meetingActions: (meetingId: string) => ['meeting-actions', meetingId] as const,
  agentPreferences: ['agent-preferences'] as const,
  pendingActions: ['pending-actions'] as const,
}

// Auth Hooks
export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.user,
    queryFn: () => apiClient.getCurrentUser(),
    retry: false,
  })
}

export function useGoogleAuth() {
  return useMutation({
    mutationFn: () => apiClient.getGoogleAuthUrl(),
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: () => apiClient.logout(),
    onSuccess: () => {
      queryClient.clear()
    },
  })
}

// Meeting Hooks
export function useMeetings() {
  return useQuery({
    queryKey: queryKeys.meetings,
    queryFn: () => apiClient.getMeetings(),
  })
}

export function useMeeting(meetingId: string) {
  return useQuery({
    queryKey: queryKeys.meeting(meetingId),
    queryFn: () => apiClient.getMeeting(meetingId),
    enabled: !!meetingId,
  })
}

export function useCreateMeeting() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (meeting: any) => apiClient.createMeeting(meeting),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.meetings })
    },
  })
}

export function useProcessTranscript() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ meetingId, transcript }: { meetingId: string; transcript: { text: string } }) =>
      apiClient.processTranscript(meetingId, transcript),
    onSuccess: (_, { meetingId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.meeting(meetingId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.meetingActions(meetingId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.pendingActions })
    },
  })
}

export function useExecuteAction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ meetingId, actionId }: { meetingId: string; actionId: string }) =>
      apiClient.executeAction(meetingId, actionId),
    onSuccess: (_, { meetingId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.meeting(meetingId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.meetingActions(meetingId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.pendingActions })
    },
  })
}

export function useMeetingActions(meetingId: string) {
  return useQuery({
    queryKey: queryKeys.meetingActions(meetingId),
    queryFn: () => apiClient.getMeetingActions(meetingId),
    enabled: !!meetingId,
  })
}

// Agent Hooks
export function useAgentPreferences() {
  return useQuery({
    queryKey: queryKeys.agentPreferences,
    queryFn: () => apiClient.getAgentPreferences(),
  })
}

export function useUpdateAgentPreferences() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (preferences: any) => apiClient.updateAgentPreferences(preferences),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agentPreferences })
    },
  })
}

export function usePendingActions() {
  return useQuery({
    queryKey: queryKeys.pendingActions,
    queryFn: () => apiClient.getPendingActions(),
  })
}

export function useApproveAction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (actionId: string) => apiClient.approveAction(actionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.pendingActions })
    },
  })
}

export function useRejectAction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (actionId: string) => apiClient.rejectAction(actionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.pendingActions })
    },
  })
} 