"use client"

import { useState, useMemo } from "react"
import { SummaryMetrics } from "../dashboard/summary-metrics"
import { CallLogItem } from "../dashboard/call-log-item"
import type { HistoryItem } from "@/lib/types"

type FilterType = "all" | "today" | "pending" | "ai_handled"

const groupHistoryByDate = (items: HistoryItem[]) => {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  return items.reduce(
    (acc, item) => {
      const itemDate = item.timestamp
      let key = "Older"
      if (itemDate.toDateString() === today.toDateString()) {
        key = "Today"
      } else if (itemDate.toDateString() === yesterday.toDateString()) {
        key = "Yesterday"
      }
      if (!acc[key]) {
        acc[key] = []
      }
      acc[key].push(item)
      return acc
    },
    {} as Record<string, HistoryItem[]>,
  )
}

export function HomeScreen({ history }: { history: HistoryItem[] }) {
  const [filter, setFilter] = useState<FilterType>("all")

  const filteredHistory = useMemo(() => {
    const today = new Date().toDateString()
    switch (filter) {
      case "today":
        return history.filter((item) => item.timestamp.toDateString() === today)
      case "pending":
        return history.filter((item) => item.pendingActions)
      case "all":
      default:
        return history
    }
  }, [history, filter])

  const groupedHistory = groupHistoryByDate(filteredHistory)
  const dateGroups = ["Today", "Yesterday", "Older"]

  return (
    <div className="space-y-8">
      <SummaryMetrics
        history={history}
        activeFilter={filter}
        onFilterChange={(newFilter) => setFilter(filter === newFilter ? "all" : newFilter)}
      />
      <main>
        <div className="space-y-6">
          {dateGroups.map(
            (group) =>
              groupedHistory[group] && (
                <div key={group}>
                  <h3 className="text-sm font-semibold text-gray-500 mb-3 px-1">{group}</h3>
                  <div className="space-y-3">
                    {groupedHistory[group].map((item) => (
                      <CallLogItem key={item.id} item={item} />
                    ))}
                  </div>
                </div>
              ),
          )}
        </div>
      </main>
    </div>
  )
}
