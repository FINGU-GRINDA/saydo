import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { CallAction, CrmData } from "@/lib/types"

interface CrmActionCardProps {
  action: CallAction
}

export function CrmActionCard({ action }: CrmActionCardProps) {
  const data = action.data as CrmData

  return (
    <Card className="bg-zinc-800/50 border-zinc-700 text-white">
      <CardHeader>
        <CardTitle className="flex items-center text-base">
          <action.Icon className="w-5 h-5 mr-3 text-emerald-400" />
          {action.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between">
            <span className="text-zinc-400 capitalize">{key.replace(/([A-Z])/g, " $1")}:</span>
            <span className="font-medium text-right">{value}</span>
          </div>
        ))}
      </CardContent>
      <CardFooter className="flex justify-end space-x-2">
        <Button variant="ghost" size="sm" className="text-zinc-300 hover:bg-zinc-700 hover:text-white">
          Edit
        </Button>
        <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white">
          Add to CRM
        </Button>
      </CardFooter>
    </Card>
  )
}
