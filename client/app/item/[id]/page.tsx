"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { ArrowLeft, Bot, Calendar, Mail, UserPlus, User } from "lucide-react"
import { AgentTypingIndicator } from "@/components/call-ops/agent-typing-indicator"
import { MeetingActionCard } from "@/components/call-ops/actions/meeting-action-card"
import { EmailActionCard } from "@/components/call-ops/actions/email-action-card"
import { CrmActionCard } from "@/components/call-ops/actions/crm-action-card"
import type { CallAction, TranscriptMessage } from "@/lib/types"

const mockTranscript: TranscriptMessage[] = [
  {
    type: "message",
    speaker: "agent",
    content:
      "Hi Alex, this is the Saydo AI assistant. I see you have an inquiry about our AI solutions. How can I help?",
    timestamp: "00:12",
  },
  {
    type: "message",
    speaker: "user",
    content:
      "Hey. We're looking to move our on-prem LLM to the cloud for better cost-efficiency. Can Vercel's AI SDK help?",
    timestamp: "00:31",
  },
  {
    type: "message",
    speaker: "agent",
    content:
      "Yes, the Vercel AI SDK is ideal for that. It's optimized for serverless environments, ensuring you only pay for what you use.",
    timestamp: "00:55",
  },
  {
    type: "message",
    speaker: "user",
    content:
      "That sounds promising. Could we get a technical demo? I'd like to have my dev team join. Would sometime next Wednesday afternoon work?",
    timestamp: "01:15",
  },
  {
    type: "message",
    speaker: "agent",
    content:
      "Of course. How about next Wednesday at 2:00 PM? I can send over a meeting invitation and some preliminary info. Is your email still alex.kim@example.com?",
    timestamp: "01:30",
  },
  {
    type: "message",
    speaker: "user",
    content: "Yes, that's correct. That time works for us. I'll look for your email.",
    timestamp: "01:42",
  },
]

const mockActions: CallAction[] = [
  {
    id: "1",
    type: "meeting",
    title: "Schedule a follow-up meeting",
    Icon: Calendar,
    data: {
      title: "Technical Demo for Vercel AI SDK",
      participants: ["You", "Alex Kim"],
      proposedTime: "Next Wednesday, 2:00 PM",
    },
  },
  {
    id: "2",
    type: "email",
    title: "Draft a follow-up email",
    Icon: Mail,
    data: {
      recipient: "alex.kim@example.com",
      subject: "Follow-up: Vercel AI SDK Technical Demo",
      body: "Hi Alex,\n\nFollowing up on our conversation, I'd like to confirm our technical demo for the Vercel AI SDK...",
    },
  },
  {
    id: "3",
    type: "crm",
    title: "Create new CRM contact",
    Icon: UserPlus,
    data: {
      name: "Alex Kim",
      email: "alex.kim@example.com",
      company: "Example Corp",
      interest: "Vercel AI SDK, Cloud Migration",
    },
  },
]

export default function CallDetailPage() {
  const [actions, setActions] = useState<CallAction[] | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(true)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const scrollToBottom = () => {
      scrollAreaRef.current?.scrollTo({ top: scrollAreaRef.current.scrollHeight, behavior: "smooth" })
    }

    // Simulate AI analysis after the transcript is displayed
    const analysisTimer = setTimeout(() => {
      setIsAnalyzing(false)
      setActions(mockActions)
      setTimeout(scrollToBottom, 100) // Scroll after actions are rendered
    }, 3000) // 3-second analysis time

    return () => clearTimeout(analysisTimer)
  }, [])

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200 p-4 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto flex items-center gap-4">
          <Link
            href="/"
            className="p-2 rounded-full text-gray-500 hover:bg-gray-100 hover:text-gray-800 transition-colors"
            aria-label="Back to call log"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="font-semibold text-gray-900">Call with Alex Kim</h1>
            <p className="text-sm text-gray-500">Today at 3:45 PM</p>
          </div>
        </div>
      </header>

      <main ref={scrollAreaRef} className="flex-1 overflow-y-auto p-4">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Render Transcript */}
          {mockTranscript.map((message, index) => {
            const isUser = message.speaker === "user"
            return (
              <div key={`msg-${index}`} className={`flex items-end gap-2 ${isUser ? "justify-end" : ""}`}>
                {!isUser && (
                  <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-gray-200">
                    <Bot className="w-5 h-5 text-gray-600" />
                  </div>
                )}
                {isUser && (
                  <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-purple-100">
                    <User className="w-5 h-5 text-purple-600" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    isUser ? "bg-purple-600 text-white" : "bg-gray-200 text-gray-800"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
              </div>
            )
          })}

          {/* Divider */}
          <div className="text-center text-xs text-gray-400 py-4">Call Ended</div>

          {/* AI Analysis and Actions */}
          {isAnalyzing && <AgentTypingIndicator />}

          {actions && (
            <div className="flex items-end gap-2">
              <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-gray-200">
                <Bot className="w-5 h-5 text-gray-600" />
              </div>
              <div className="space-y-3 flex-1">
                <p className="text-sm text-gray-600">Here are the post-call actions I've prepared:</p>
                {actions.map((action) => {
                  if (action.type === "meeting") return <MeetingActionCard key={action.id} action={action} />
                  if (action.type === "email") return <EmailActionCard key={action.id} action={action} />
                  if (action.type === "crm") return <CrmActionCard key={action.id} action={action} />
                  return null
                })}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
