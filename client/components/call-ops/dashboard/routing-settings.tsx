"use client"

import { useState } from "react"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function RoutingSettings() {
  const [enableAiOffHours, setEnableAiOffHours] = useState(true)

  return (
    <div className="bg-zinc-900/50 text-white">
      <h3 className="text-lg font-semibold mb-4">Call Routing Rules</h3>
      <div className="space-y-6">
        <div className="flex items-center justify-between space-x-2 p-4 rounded-lg bg-zinc-800/50 border border-zinc-700">
          <Label htmlFor="ai-off-hours" className="flex flex-col space-y-1 cursor-pointer">
            <span>Enable AI for Off-Hours</span>
            <span className="font-normal leading-snug text-zinc-400 text-sm">
              Route calls to AI outside of business hours.
            </span>
          </Label>
          <Switch
            id="ai-off-hours"
            checked={enableAiOffHours}
            onCheckedChange={setEnableAiOffHours}
            aria-label="Enable AI for Off-Hours"
          />
        </div>
        <div
          className={`space-y-4 transition-opacity ${enableAiOffHours ? "opacity-100" : "opacity-50 pointer-events-none"}`}
        >
          <Label>Business Hours</Label>
          <div className="flex items-center gap-4">
            <Input
              type="time"
              defaultValue="09:00"
              className="bg-zinc-800 border-zinc-700"
              disabled={!enableAiOffHours}
            />
            <span className="text-zinc-400">to</span>
            <Input
              type="time"
              defaultValue="18:00"
              className="bg-zinc-800 border-zinc-700"
              disabled={!enableAiOffHours}
            />
          </div>
        </div>
        <div className="flex justify-end pt-4">
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">Save Settings</Button>
        </div>
      </div>
    </div>
  )
}
