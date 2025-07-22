import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar, Users, Clock } from "lucide-react"
import type { CallAction, MeetingData } from "@/lib/types"

interface MeetingActionCardProps {
  action: CallAction
}

export function MeetingActionCard({ action }: MeetingActionCardProps) {
  const data = action.data as MeetingData

  return (
    <Card className="bg-zinc-800/50 border-zinc-700 text-white">
      <CardHeader>
        <CardTitle className="flex items-center text-base">
          <action.Icon className="w-5 h-5 mr-3 text-purple-400" />
          {action.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="flex items-center">
          <Calendar className="w-4 h-4 mr-3 text-zinc-400" />
          <span>{data.title}</span>
        </div>
        <div className="flex items-center">
          <Users className="w-4 h-4 mr-3 text-zinc-400" />
          <span>{data.participants.join(", ")}</span>
        </div>
        <div className="flex items-center">
          <Clock className="w-4 h-4 mr-3 text-zinc-400" />
          <span>{data.proposedTime}</span>
        </div>
      </CardContent>
      <CardFooter className="flex justify-end space-x-2">
        <Button variant="ghost" size="sm" className="text-zinc-300 hover:bg-zinc-700 hover:text-white">
          Edit
        </Button>
        <Button size="sm" className="bg-purple-600 hover:bg-purple-700 text-white">
          Confirm Meeting
        </Button>
      </CardFooter>
    </Card>
  )
}
