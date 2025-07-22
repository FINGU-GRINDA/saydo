import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import type { CallAction, EmailData } from "@/lib/types"

interface EmailActionCardProps {
  action: CallAction
}

export function EmailActionCard({ action }: EmailActionCardProps) {
  const data = action.data as EmailData

  return (
    <Card className="bg-zinc-800/50 border-zinc-700 text-white">
      <CardHeader>
        <CardTitle className="flex items-center text-base">
          <action.Icon className="w-5 h-5 mr-3 text-sky-400" />
          {action.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="grid grid-cols-[auto_1fr] items-center gap-x-3 gap-y-2">
          <label className="text-zinc-400">To:</label>
          <Input defaultValue={data.recipient} className="bg-zinc-900 border-zinc-700" />
          <label className="text-zinc-400">Subject:</label>
          <Input defaultValue={data.subject} className="bg-zinc-900 border-zinc-700" />
        </div>
        <Textarea defaultValue={data.body} className="bg-zinc-900 border-zinc-700 h-32" />
      </CardContent>
      <CardFooter className="flex justify-end space-x-2">
        <Button variant="ghost" size="sm" className="text-zinc-300 hover:bg-zinc-700 hover:text-white">
          Discard
        </Button>
        <Button size="sm" className="bg-sky-600 hover:bg-sky-700 text-white">
          Send Email
        </Button>
      </CardFooter>
    </Card>
  )
}
