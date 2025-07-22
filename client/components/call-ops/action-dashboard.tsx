"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { MeetingActionCard } from "./meeting-action-card"
import { EmailActionCard } from "./email-action-card"
import { CrmActionCard } from "./crm-action-card"
import { GeneratingIndicator } from "./generating-indicator"
import type { CallAction } from "@/lib/types"

interface ActionDashboardProps {
  actions: CallAction[]
  isCallComplete: boolean
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 100,
    },
  },
}

export function ActionDashboard({ actions, isCallComplete }: ActionDashboardProps) {
  const [isGenerating, setIsGenerating] = useState(true)

  useEffect(() => {
    if (isCallComplete) {
      const timer = setTimeout(() => setIsGenerating(false), 8000) // Simulate AI thinking time
      return () => clearTimeout(timer)
    } else {
      setIsGenerating(true)
    }
  }, [isCallComplete])

  const renderActionCard = (action: CallAction) => {
    switch (action.type) {
      case "meeting":
        return <MeetingActionCard action={action} />
      case "email":
        return <EmailActionCard action={action} />
      case "crm":
        return <CrmActionCard action={action} />
      default:
        return null
    }
  }

  return (
    <div className="w-full md:w-96 lg:w-[450px] bg-zinc-900 border-l border-zinc-800 flex flex-col">
      <div className="p-4 sm:p-6 border-b border-zinc-800">
        <h2 className="text-lg font-semibold text-white">Post-Call Actions</h2>
        <p className="text-sm text-zinc-400 mt-1">AI-generated follow-ups.</p>
      </div>

      <ScrollArea className="flex-1 p-4">
        {isGenerating ? (
          <GeneratingIndicator />
        ) : (
          <motion.div className="space-y-4" variants={containerVariants} initial="hidden" animate="visible">
            {actions.map((action) => (
              <motion.div key={action.id} variants={itemVariants}>
                {renderActionCard(action)}
              </motion.div>
            ))}
          </motion.div>
        )}
      </ScrollArea>

      <div className="p-4 border-t border-zinc-800">
        <Button
          className="w-full bg-zinc-800 text-zinc-300 hover:bg-zinc-700 border border-zinc-700"
          disabled={isGenerating}
        >
          Mark as Reviewed
        </Button>
      </div>
    </div>
  )
}
