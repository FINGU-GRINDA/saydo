import Link from "next/link"
import { Phone, Users, ChevronRight, MessageSquare, MousePointerClick } from "lucide-react"
import type { HistoryItem } from "@/lib/types"

function formatRelativeTime(date: Date) {
  const now = new Date()
  const diffSeconds = Math.round((now.getTime() - date.getTime()) / 1000)
  const diffMinutes = Math.round(diffSeconds / 60)
  const diffHours = Math.round(diffMinutes / 60)
  const diffDays = Math.round(diffHours / 24)

  if (diffSeconds < 60) return `${diffSeconds}s ago`
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays === 1) return `Yesterday`
  return date.toLocaleDateString()
}

export function CallLogItem({ item }: { item: HistoryItem }) {
  let TypeIcon
  let iconBgColor
  let iconColor

  switch (item.type) {
    case "meeting":
      TypeIcon = Users
      iconBgColor = "bg-purple-100"
      iconColor = "text-purple-600"
      break
    case "browser_task":
      TypeIcon = MousePointerClick
      iconBgColor = "bg-orange-100"
      iconColor = "text-orange-600"
      break
    case "call":
    default:
      TypeIcon = Phone
      iconBgColor = "bg-sky-100"
      iconColor = "text-sky-600"
      break
  }

  return (
    <Link href={`/call/${item.id}`} className="block">
      <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-4 hover:bg-gray-50 hover:border-gray-300 transition-all cursor-pointer shadow-sm">
        <div className="flex items-start gap-3">
          <MessageSquare className="w-4 h-4 text-gray-400 mt-1 flex-shrink-0" />
          <p className="text-sm text-gray-600">{item.summary}</p>
        </div>
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${iconBgColor}`}>
              <TypeIcon className={`w-5 h-5 ${iconColor}`} />
            </div>
            <div>
              <p className="font-semibold text-sm text-gray-800">{item.title}</p>
              <p className="text-xs text-gray-500">{formatRelativeTime(item.timestamp)}</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </div>
      </div>
    </Link>
  )
}
