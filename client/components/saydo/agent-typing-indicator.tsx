"use client"

import { motion } from "framer-motion"
import { Bot } from "lucide-react"

const containerVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
}

const dotVariants = {
  initial: { y: "0%" },
  animate: { y: "-100%" },
}

export function AgentTypingIndicator() {
  return (
    <motion.div
      className="flex items-end space-x-3 max-w-[85%]"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-gray-200">
        <Bot className="w-5 h-5 text-gray-600" />
      </div>
      <div className="rounded-2xl px-4 py-3 bg-gray-200">
        <div className="flex items-center justify-center space-x-1 h-5">
          <motion.span
            className="w-1.5 h-1.5 bg-gray-500 rounded-full"
            variants={dotVariants}
            transition={{ duration: 0.4, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <motion.span
            className="w-1.5 h-1.5 bg-gray-500 rounded-full"
            variants={dotVariants}
            transition={{ duration: 0.4, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut", delay: 0.1 }}
          />
          <motion.span
            className="w-1.5 h-1.5 bg-gray-500 rounded-full"
            variants={dotVariants}
            transition={{ duration: 0.4, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut", delay: 0.2 }}
          />
        </div>
      </div>
    </motion.div>
  )
}
