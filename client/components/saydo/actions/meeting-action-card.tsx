import { Button } from "@/components/ui/button"
import { Calendar, Users, Clock } from "lucide-react"
import type { CallAction, MeetingData } from "@/lib/types"

export function MeetingActionCard({ action }: { action: CallAction }) {
  const data = action.data as MeetingData
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-4">
      <div className="flex items-center font-semibold text-gray-900">
        <action.Icon className="w-5 h-5 mr-3 text-purple-600" />
        {action.title}
      </div>
      <div className="space-y-3 text-sm pl-8 text-gray-700">
        <div className="flex items-center">
          <Calendar className="w-4 h-4 mr-3 text-gray-400" />
          <span>{data.title}</span>
        </div>
        <div className="flex items-center">
          <Users className="w-4 h-4 mr-3 text-gray-400" />
          <span>{data.participants.join(", ")}</span>
        </div>
        <div className="flex items-center">
          <Clock className="w-4 h-4 mr-3 text-gray-400" />
          <span>{data.proposedTime}</span>
        </div>
      </div>
      <div className="flex justify-end space-x-2 pl-8">
        <Button variant="ghost" size="sm">
          Edit
        </Button>
        <Button size="sm" className="bg-purple-600 hover:bg-purple-700 text-white">
          Confirm Meeting
        </Button>
      </div>
    </div>
  )
}
