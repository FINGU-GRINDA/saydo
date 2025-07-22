"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"

interface CallHeaderProps {
  isCallLive: boolean
  callStartTime: Date
}

export function CallHeader({ isCallLive, callStartTime }: CallHeaderProps) {
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    if (isCallLive) {
      const interval = setInterval(() => {
        const now = new Date()
        const diff = now.getTime() - callStartTime.getTime()
        setElapsedTime(Math.floor(diff / 1000))
      }, 1000)

      return () => clearInterval(interval)
    }
  }, [isCallLive, callStartTime])

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = time % 60
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`
  }

  return (
    <div className="bg-zinc-900/50 border-b border-zinc-800 p-4 backdrop-blur-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Live Call</h2>
        {isCallLive && <Badge className="bg-emerald-900 text-emerald-300">Live • {formatTime(elapsedTime)}</Badge>}
      </div>
    </div>
  )
}
