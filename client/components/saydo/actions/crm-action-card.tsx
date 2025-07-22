import { Button } from "@/components/ui/button"
import type { CallAction, CrmData } from "@/lib/types"

export function CrmActionCard({ action }: { action: CallAction }) {
  const data = action.data as CrmData
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-4">
      <div className="flex items-center font-semibold text-gray-900">
        <action.Icon className="w-5 h-5 mr-3 text-purple-600" />
        {action.title}
      </div>
      <div className="space-y-2 text-sm pl-8">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between">
            <span className="text-gray-500 capitalize">{key.replace(/([A-Z])/g, " $1")}:</span>
            <span className="font-medium text-gray-800 text-right">{value}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-end space-x-2 pl-8">
        <Button variant="ghost" size="sm">
          Edit
        </Button>
        <Button size="sm" className="bg-purple-600 hover:bg-purple-700 text-white">
          Add to CRM
        </Button>
      </div>
    </div>
  )
}
