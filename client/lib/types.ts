import type { LucideIcon } from "lucide-react"

export type CallHandlerType = "ai" | "human"
export type CallStatus = "Completed" | "In Progress" | "Missed"
export type RecordingType = "call" | "meeting" | "browser_task"

export interface Call {
  id: string
  caller: string
  timestamp: Date
  duration: string
  handlerType: CallHandlerType
  status: CallStatus
  summary: string
  pendingActions: boolean
}

export interface HistoryItem {
  id: string
  title: string
  timestamp: Date
  duration: string
  type: RecordingType
  summary: string
  pendingActions: boolean
}

export interface Message {
  speaker: "user" | "agent"
  content: string
  timestamp: string
}

export interface MeetingData {
  title: string
  participants: string[]
  proposedTime: string
}

export interface EmailData {
  recipient: string
  subject: string
  body: string
}

export interface CrmData {
  name: string
  email: string
  company: string
  interest: string
}

export interface CallAction {
  id: string
  type: "meeting" | "email" | "crm"
  title: string
  Icon: LucideIcon
  data: MeetingData | EmailData | CrmData
}
