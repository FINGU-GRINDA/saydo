"use client"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface SettingsModalProps {
  isOpen: boolean
  onOpenChange: (isOpen: boolean) => void
}

export function SettingsModal({ isOpen, onOpenChange }: SettingsModalProps) {
  const [enableAiOffHours, setEnableAiOffHours] = useState(true)

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="bg-white text-gray-900">
        <DialogHeader>
          <DialogTitle>Call Routing Rules</DialogTitle>
          <DialogDescription>Define when the AI Agent handles inbound calls.</DialogDescription>
        </DialogHeader>
        <div className="pt-4 space-y-6">
          <div className="flex items-center justify-between space-x-2 p-4 rounded-lg bg-gray-50 border">
            <Label htmlFor="ai-off-hours" className="flex flex-col space-y-1 cursor-pointer">
              <span>Enable AI for Off-Hours</span>
              <span className="font-normal leading-snug text-gray-500 text-sm">
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
            className={`space-y-4 transition-opacity ${
              enableAiOffHours ? "opacity-100" : "opacity-50 pointer-events-none"
            }`}
          >
            <Label>Business Hours</Label>
            <div className="flex items-center gap-4">
              <Input type="time" defaultValue="09:00" className="bg-gray-100" disabled={!enableAiOffHours} />
              <span className="text-gray-500">to</span>
              <Input type="time" defaultValue="18:00" className="bg-gray-100" disabled={!enableAiOffHours} />
            </div>
          </div>
        </div>
        <DialogFooter className="pt-6">
          <Button onClick={() => onOpenChange(false)} className="bg-purple-600 hover:bg-purple-700 text-white">
            Save Settings
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
