"use client"

import { Mail } from "lucide-react"
import type { CallAction, EmailData } from "@/lib/types"

interface EmailActionCardProps {
  action: CallAction & { data: EmailData }
}

export function EmailActionCard({ action }: EmailActionCardProps) {
  const { data } = action

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
          <Mail className="w-4 h-4 text-green-600" />
        </div>
        <h3 className="font-medium text-gray-900">{action.title}</h3>
      </div>
      
      <div className="space-y-2 mb-4">
        <p className="text-sm text-gray-500">
          <span className="font-medium">To:</span> {data.recipient}
        </p>
        <p className="text-sm text-gray-500">
          <span className="font-medium">Subject:</span> {data.subject}
        </p>
        <div className="bg-gray-50 p-3 rounded-md">
          <p className="text-sm text-gray-600 whitespace-pre-line">{data.body}</p>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
          Send Email
        </button>
      </div>
    </div>
  )
}
