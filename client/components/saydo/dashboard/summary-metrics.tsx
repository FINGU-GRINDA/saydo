"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Calendar, ListTodo } from "lucide-react"
import type { HistoryItem } from "@/lib/types"

type FilterType = "all" | "today" | "pending"

interface SummaryMetricsProps {
  history: HistoryItem[]
  activeFilter: FilterType
  onFilterChange: (filter: FilterType) => void
}

export function SummaryMetrics({ history, activeFilter, onFilterChange }: SummaryMetricsProps) {
  const today = new Date().toDateString()
  const eventsTodayCount = history.filter((item) => item.timestamp.toDateString() === today).length
  const pendingActionsCount = history.filter((item) => item.pendingActions).length

  const metrics = [
    { id: "today", label: "Today's Events", value: eventsTodayCount, Icon: Calendar },
    { id: "pending", label: "Pending Actions", value: pendingActionsCount, Icon: ListTodo },
  ]

  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-8">
      {metrics.map((metric) => (
        <button key={metric.id} onClick={() => onFilterChange(metric.id as FilterType)}>
          <Card
            className={`shadow-sm border transition-all h-full ${
              activeFilter === metric.id
                ? "bg-purple-50 border-purple-200"
                : "bg-white border-gray-200 hover:border-gray-300"
            }`}
          >
            <CardContent className="p-3 sm:p-4 flex flex-col items-center justify-center text-center">
              <metric.Icon
                className={`w-6 h-6 mb-2 transition-colors ${
                  activeFilter === metric.id ? "text-purple-600" : "text-gray-500"
                }`}
              />
              <p
                className={`text-xl sm:text-2xl font-bold transition-colors ${
                  activeFilter === metric.id ? "text-purple-700" : "text-gray-900"
                }`}
              >
                {metric.value}
              </p>
              <p
                className={`text-xs transition-colors ${
                  activeFilter === metric.id ? "text-purple-600" : "text-gray-500"
                }`}
              >
                {metric.label}
              </p>
            </CardContent>
          </Card>
        </button>
      ))}
    </div>
  )
}
