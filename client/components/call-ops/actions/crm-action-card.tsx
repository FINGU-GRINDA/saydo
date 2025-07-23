"use client"

import { UserPlus } from "lucide-react"
import type { CallAction, CrmData } from "@/lib/types"

interface CrmActionCardProps {
  action: CallAction & { data: CrmData }
}

export function CrmActionCard({ action }: CrmActionCardProps) {
  const { data } = action

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
          <UserPlus className="w-4 h-4 text-purple-600" />
        </div>
        <h3 className="font-medium text-gray-900">{action.title}</h3>
      </div>
      
      <div className="space-y-2 mb-4">
        <p className="text-sm text-gray-500">
          <span className="font-medium">Name:</span> {data.name}
        </p>
        <p className="text-sm text-gray-500">
          <span className="font-medium">Email:</span> {data.email}
        </p>
        <p className="text-sm text-gray-500">
          <span className="font-medium">Company:</span> {data.company}
        </p>
        <p className="text-sm text-gray-500">
          <span className="font-medium">Interest:</span> {data.interest}
        </p>
      </div>
      
      <div className="flex justify-end">
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
          Add to CRM
        </button>
      </div>
    </div>
  )
}
