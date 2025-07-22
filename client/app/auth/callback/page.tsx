'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { apiClient } from '@/lib/api-client'
import { useAuth } from '@/lib/contexts/auth-context'
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react'

export default function AuthCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing')
  const [message, setMessage] = useState('Completing authentication...')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const token = searchParams.get('token')

      try {
        if (code && state) {
          // Google OAuth callback
          setMessage('Connecting to Google...')
          const response = await apiClient.handleGoogleCallback(code, state)
          setStatus('success')
          setMessage('Successfully connected to Google!')
          
          // Redirect to agent settings after a short delay
          setTimeout(() => {
            router.push('/?screen=agent-settings')
          }, 2000)
          
        } else if (token) {
          // JWT token callback
          apiClient.setToken(token)
          setStatus('success')
          setMessage('Authentication successful!')
          
          setTimeout(() => {
            router.push('/')
          }, 1500)
          
        } else {
          // No valid parameters
          throw new Error('Invalid callback parameters')
        }
      } catch (error: any) {
        console.error('Auth callback error:', error)
        setStatus('error')
        setMessage(error.message || 'Authentication failed')
        
        // Redirect to home after error
        setTimeout(() => {
          router.push('/')
        }, 3000)
      }
    }

    handleCallback()
  }, [router, searchParams])

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      case 'success':
        return <CheckCircle className="h-8 w-8 text-green-600" />
      case 'error':
        return <AlertCircle className="h-8 w-8 text-red-600" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'text-blue-600'
      case 'success':
        return 'text-green-600'
      case 'error':
        return 'text-red-600'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center max-w-md mx-auto p-6">
        <div className="mb-4 flex justify-center">
          {getStatusIcon()}
        </div>
        <h1 className="text-xl font-semibold mb-2">
          {status === 'processing' && 'Processing...'}
          {status === 'success' && 'Success!'}
          {status === 'error' && 'Error'}
        </h1>
        <p className={`${getStatusColor()} mb-4`}>{message}</p>
        
        {status === 'success' && (
          <p className="text-sm text-gray-500">
            Redirecting you back to the app...
          </p>
        )}
        
        {status === 'error' && (
          <p className="text-sm text-gray-500">
            You will be redirected to the home page shortly.
          </p>
        )}
      </div>
    </div>
  )
} 