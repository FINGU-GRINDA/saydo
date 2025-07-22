"use client"

import { useRef, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { User, Bot } from "lucide-react"
import type { Message } from "@/lib/types"

interface CallTranscriptProps {
  messages: Message[]
}

export function CallTranscript({ messages }: CallTranscriptProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector("div")
      if (viewport) {
        viewport.scrollTop = viewport.scrollHeight
      }
    }
  }, [messages])

  return (
    <ScrollArea className="flex-1 p-4 sm:p-6" ref={scrollAreaRef}>
      <div className="space-y-6 max-w-4xl mx-auto">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.speaker === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`flex items-start space-x-3 max-w-[85%] ${
                message.speaker === "user" ? "flex-row-reverse space-x-reverse" : ""
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.speaker === "user" ? "bg-white text-black" : "bg-gradient-to-r from-purple-600 to-indigo-600"
                }`}
              >
                {message.speaker === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-white" />}
              </div>
              <div className="flex flex-col space-y-1">
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    message.speaker === "user"
                      ? "bg-white text-black ml-auto"
                      : "bg-zinc-800 text-white border border-zinc-700"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
                <p
                  className={`text-xs px-2 ${
                    message.speaker === "user" ? "text-right text-zinc-500" : "text-zinc-500"
                  }`}
                >
                  {message.timestamp}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  )
}
