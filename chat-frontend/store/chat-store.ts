import { create } from 'zustand'

interface ChatState {
  sessionId: string | undefined
  setSessionId: (sessionId: string | undefined) => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId: undefined,
  setSessionId: (sessionId) => set({ sessionId }),
}))
