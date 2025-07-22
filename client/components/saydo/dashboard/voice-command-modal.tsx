"use client"

import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { VisuallyHidden } from "@radix-ui/react-visually-hidden"
import Link from "next/link"
import { Phone, Users, MousePointerClick } from "lucide-react"
import { motion } from "framer-motion"

interface VoiceCommandModalProps {
  isOpen: boolean
  onOpenChange: (isOpen: boolean) => void
}

export function VoiceCommandModal({ isOpen, onOpenChange }: VoiceCommandModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="bg-black/80 backdrop-blur-lg border-0 text-white p-0 w-full h-full max-w-full sm:max-w-lg sm:h-auto sm:rounded-2xl">
        <VisuallyHidden>
          <DialogTitle>Voice Command Interface</DialogTitle>
        </VisuallyHidden>
        <div className="flex flex-col items-center justify-center p-8 sm:p-12 h-full">
          <h2 className="text-2xl font-bold text-white mb-6 tracking-tight">Say It, Saydo It.</h2>

          <div className="relative w-48 h-48 flex items-center justify-center mb-8">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-full h-full rounded-full border border-purple-500/30"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 2,
                  ease: "easeInOut",
                  repeat: Number.POSITIVE_INFINITY,
                  delay: i * 0.3,
                }}
              />
            ))}
            <motion.div
              className="w-24 h-24 bg-purple-600 rounded-full shadow-2xl shadow-purple-600/50"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 1.5, ease: "easeInOut", repeat: Number.POSITIVE_INFINITY }}
            />
          </div>

          <p className="text-gray-400 mb-8">Listening for a command...</p>

          <div className="flex items-center justify-center gap-4 sm:gap-6">
            <Link
              href="/call/1"
              className="flex flex-col items-center gap-2 text-gray-300 hover:text-white transition-colors"
              onClick={() => onOpenChange(false)}
            >
              <div className="w-12 h-12 rounded-full border border-gray-700 flex items-center justify-center bg-gray-800/50">
                <Phone className="w-5 h-5" />
              </div>
              <span className="text-xs">Record Call</span>
            </Link>
            <Link
              href="/call/new"
              className="flex flex-col items-center gap-2 text-gray-300 hover:text-white transition-colors"
              onClick={() => onOpenChange(false)}
            >
              <div className="w-12 h-12 rounded-full border border-gray-700 flex items-center justify-center bg-gray-800/50">
                <Users className="w-5 h-5" />
              </div>
              <span className="text-xs">Record Meeting</span>
            </Link>
            <Link
              href="/call/3"
              className="flex flex-col items-center gap-2 text-gray-300 hover:text-white transition-colors"
              onClick={() => onOpenChange(false)}
            >
              <div className="w-12 h-12 rounded-full border border-gray-700 flex items-center justify-center bg-gray-800/50">
                <MousePointerClick className="w-5 h-5" />
              </div>
              <span className="text-xs">Automate Task</span>
            </Link>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
