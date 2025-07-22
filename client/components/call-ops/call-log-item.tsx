import Link from "next/link"
import { Bot, User, ChevronRight } from "lucide-react"
import type { CallLogItemProps } from "@/lib/types" // Declare the variable before using it

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

export function CallLogItem({ call }: CallLogItemProps) {
  const HandlerIcon = call.handlerType === "ai" ? Bot : User

  return (
    <Link href={`/call/${call.id}`} className="block">
      <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between hover:bg-gray-50 hover:border-gray-300 transition-all cursor-pointer shadow-sm">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <div
            className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center ${
              call.handlerType === "ai" ? "bg-purple-100" : "bg-sky-100"
            }`}
          >
            <HandlerIcon className={`w-6 h-6 ${call.handlerType === "ai" ? "text-purple-600" : "text-sky-600"}`} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-gray-900 truncate">{call.caller}</p>
            <div className="flex items-center gap-2 text-sm text-gray-500 mt-1 flex-wrap">
              <span>{formatRelativeTime(call.timestamp)}</span>
              <span className="text-gray-300">·</span>
              <span>{call.duration}</span>
            </div>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400 ml-4" />
      </div>
    </Link>
  )
}
