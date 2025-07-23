"use client"

import { Calendar } from "lucide-react"
import type { CallAction, MeetingData } from "@/lib/types"

interface MeetingActionCardProps {
  action: CallAction & { data: MeetingData }
}

export function MeetingActionCard({ action }: MeetingActionCardProps) {
  const { data } = action

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
          <Calendar className="w-4 h-4 text-blue-600" />
        </div>
        <h3 className="font-medium text-gray-900">{action.title}</h3>
      </div>
      
      <div className="space-y-2 mb-4">
        <p className="text-sm font-medium text-gray-900">{data.title}</p>
        <p className="text-sm text-gray-500">
          <span className="font-medium">When:</span> {data.proposedTime}
        </p>
        <p className="text-sm text-gray-500">
          <span className="font-medium">Who:</span> {data.participants.join(", ")}
        </p>
      </div>
      
      <div className="flex justify-end">
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
          Schedule Meeting
        </button>
      </div>
    </div>
  )
}
