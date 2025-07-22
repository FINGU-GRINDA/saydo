"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Bot } from "lucide-react"

const analysisSteps = [
  "Parsing transcript...",
  "Identifying key entities...",
  "Analyzing sentiment...",
  "Detecting action items...",
  "Drafting follow-ups...",
]

export function GeneratingIndicator() {
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % analysisSteps.length)
    }, 1500)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <motion.div
        animate={{ scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] }}
        transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
      >
        <Bot className="w-12 h-12 text-purple-400" />
      </motion.div>
      <p className="mt-4 text-lg font-medium text-white">AI is thinking</p>
      <div className="h-6 mt-1">
        <AnimatePresence mode="wait">
          <motion.p
            key={currentStep}
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -10, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="text-sm text-zinc-400"
          >
            {analysisSteps[currentStep]}
          </motion.p>
        </AnimatePresence>
      </div>
    </div>
  )
}
