import { CallLogItem } from "./call-log-item"
import type { Call } from "@/lib/types"

const now = new Date()
const mockCalls: Call[] = [
  {
    id: "1",
    caller: "Alex Kim (Vercel Inquiry)",
    timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000), // 2 hours ago
    duration: "8m 42s",
    handlerType: "ai",
    status: "Completed",
    businessHours: false,
  },
  {
    id: "2",
    caller: "Samantha Lee (Enterprise Pricing)",
    timestamp: new Date(now.getTime() - 5 * 60 * 60 * 1000), // 5 hours ago
    duration: "12m 15s",
    handlerType: "human",
    status: "Completed",
    businessHours: true,
  },
  {
    id: "3",
    caller: "David Chen (Support Question)",
    timestamp: new Date(now.getTime() - 25 * 60 * 60 * 1000), // 25 hours ago
    duration: "5m 30s",
    handlerType: "human",
    status: "Completed",
    businessHours: true,
  },
  {
    id: "4",
    caller: "Unknown Number",
    timestamp: new Date(now.getTime() - 48 * 60 * 60 * 1000), // 2 days ago
    duration: "1m 05s",
    handlerType: "ai",
    status: "Completed",
    businessHours: false,
  },
]

const groupCallsByDate = (calls: Call[]) => {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  return calls.reduce(
    (acc, call) => {
      const callDate = call.timestamp
      let key = "Older"
      if (callDate.toDateString() === today.toDateString()) {
        key = "Today"
      } else if (callDate.toDateString() === yesterday.toDateString()) {
        key = "Yesterday"
      }
      if (!acc[key]) {
        acc[key] = []
      }
      acc[key].push(call)
      return acc
    },
    {} as Record<string, Call[]>,
  )
}

export function CallLog() {
  const groupedCalls = groupCallsByDate(mockCalls)
  const dateGroups = ["Today", "Yesterday", "Older"]

  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-4">Recent Calls</h2>
      <div className="space-y-6">
        {dateGroups.map(
          (group) =>
            groupedCalls[group] && (
              <div key={group}>
                <h3 className="text-sm font-medium text-zinc-400 mb-3">{group}</h3>
                <div className="space-y-3">
                  {groupedCalls[group].map((call) => (
                    <CallLogItem key={call.id} call={call} />
                  ))}
                </div>
              </div>
            ),
        )}
      </div>
    </div>
  )
}
