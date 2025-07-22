import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import type { CallAction, EmailData } from "@/lib/types"

export function EmailActionCard({ action }: { action: CallAction }) {
  const data = action.data as EmailData
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-4">
      <div className="flex items-center font-semibold text-gray-900">
        <action.Icon className="w-5 h-5 mr-3 text-purple-600" />
        {action.title}
      </div>
      <div className="space-y-3 text-sm pl-8">
        <div className="grid grid-cols-[auto_1fr] items-center gap-x-3 gap-y-2">
          <label className="text-gray-500">To:</label>
          <Input defaultValue={data.recipient} className="bg-gray-100 border-gray-300" />
          <label className="text-gray-500">Subject:</label>
          <Input defaultValue={data.subject} className="bg-gray-100 border-gray-300" />
        </div>
        <Textarea defaultValue={data.body} className="bg-gray-100 border-gray-300 h-32" />
      </div>
      <div className="flex justify-end space-x-2 pl-8">
        <Button variant="ghost" size="sm">
          Discard
        </Button>
        <Button size="sm" className="bg-purple-600 hover:bg-purple-700 text-white">
          Send Email
        </Button>
      </div>
    </div>
  )
}
