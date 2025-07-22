"use client"

import { Home, Bot } from "lucide-react"
import { SaydoCommandIcon } from "@/components/icons/saydo-command-icon"
import type { ActiveTab } from "@/app/page"

interface BottomNavBarProps {
  activeTab: ActiveTab
  setActiveTab: (tab: ActiveTab) => void
  onCommandClick: () => void
}

export function BottomNavBar({ activeTab, setActiveTab, onCommandClick }: BottomNavBarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 h-20 bg-transparent z-10">
      <div className="absolute bottom-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-lg border-t border-gray-200" />
      <div className="relative max-w-2xl mx-auto flex justify-around items-center h-full">
        <button
          onClick={() => setActiveTab("home")}
          className={`flex flex-col items-center justify-center gap-1 w-24 transition-colors duration-200 z-10 ${
            activeTab === "home" ? "text-purple-600" : "text-gray-500 hover:text-purple-600"
          }`}
        >
          <Home className="w-6 h-6" />
          <span className="text-xs font-medium">Home</span>
        </button>

        <button
          onClick={onCommandClick}
          className="absolute top-0 w-16 h-16 rounded-full bg-black hover:bg-gray-800 text-white flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 z-20"
          aria-label="Open AI Command"
        >
          <SaydoCommandIcon />
        </button>

        <button
          onClick={() => setActiveTab("agent")}
          className={`flex flex-col items-center justify-center gap-1 w-24 transition-colors duration-200 z-10 ${
            activeTab === "agent" ? "text-purple-600" : "text-gray-500 hover:text-purple-600"
          }`}
        >
          <Bot className="w-6 h-6" />
          <span className="text-xs font-medium">AI Agent</span>
        </button>
      </div>
    </div>
  )
}
