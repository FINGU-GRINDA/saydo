const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  headers?: Record<string, string>
  body?: any
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    this.loadToken()
  }

  private loadToken() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token')
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = `${this.baseUrl}/api${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const config: RequestInit = {
      method: options.method || 'GET',
      headers,
      ...options.body && { body: JSON.stringify(options.body) },
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Auth endpoints
  async getGoogleAuthUrl() {
    return this.request<{ authorization_url: string; state: string }>('/auth/google')
  }

  async getGoogleConnectUrl() {
    return this.request<{ authorization_url: string; state: string }>('/auth/google/connect')
  }

  async handleGoogleCallback(code: string, state: string) {
    return this.request<{ message: string; user: any }>('/auth/google/callback', {
      method: 'POST',
      body: { code, state }
    })
  }

  async getCurrentUser() {
    return this.request<any>('/auth/me')
  }

  async disconnectGoogle() {
    return this.request<{ success: boolean; message: string }>('/auth/disconnect-google', { 
      method: 'POST' 
    })
  }

  async logout() {
    const result = await this.request<{ message: string }>('/auth/logout', { method: 'POST' })
    this.clearToken()
    return result
  }

  // Demo auth endpoint
  async demoLogin(username: string, password: string) {
    return this.request<{
      access_token: string
      token_type: string
      user: any
    }>('/demo/login', {
      method: 'POST',
      body: { username, password }
    })
  }

  // Meeting endpoints
  async getMeetings() {
    return this.request<any[]>('/meetings')
  }

  async getMeeting(meetingId: string) {
    return this.request<any>(`/meetings/${meetingId}`)
  }

  async createMeeting(meeting: any) {
    return this.request<any>('/meetings', {
      method: 'POST',
      body: meeting,
    })
  }

  async processTranscript(meetingId: string, transcript: { text: string }) {
    return this.request<any>(`/meetings/${meetingId}/transcript`, {
      method: 'POST',
      body: transcript,
    })
  }

  async getSession(sessionId: string) {
    return this.request<any>(`/bot/sessions/${sessionId}`)
  }

  async executeAction(meetingId: string, actionId: string) {
    return this.request<any>(`/meetings/${meetingId}/actions/${actionId}/execute`, {
      method: 'POST',
    })
  }

  async getMeetingActions(meetingId: string) {
    return this.request<any[]>(`/meetings/${meetingId}/actions`)
  }

  // Agent endpoints
  async getAgentPreferences() {
    return this.request<any>('/agent/preferences')
  }

  async updateAgentPreferences(preferences: any) {
    return this.request<any>('/agent/preferences', {
      method: 'PUT',
      body: preferences,
    })
  }

  async getPendingActions() {
    return this.request<any[]>('/agent/actions/pending')
  }

  async approveAction(actionId: string) {
    return this.request<any>(`/agent/actions/${actionId}/approve`, {
      method: 'POST',
    })
  }

  async rejectAction(actionId: string) {
    return this.request<any>(`/agent/actions/${actionId}/reject`, {
      method: 'POST',
    })
  }

  // Bot endpoints
  async createBotSession(meetUrl: string) {
    return this.request<any>('/bot/create-session', {
      method: 'POST',
      body: { meetUrl }
    })
  }

  async stopBotSession(sessionId: string) {
    return this.request<any>(`/bot/sessions/${sessionId}/stop`, {
      method: 'POST'
    })
  }

  async executeBotAction(sessionId: string, actionId: string) {
    return this.request<any>(`/bot/sessions/${sessionId}/execute-action/${actionId}`, {
      method: 'POST'
    })
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
export default apiClient 