import { create } from 'zustand'
import { Message } from 'ai'

interface ChatState {
  sessionId: string | undefined
  setSessionId: (sessionId: string | undefined) => void
  loadChatHistory: () => Promise<Message[]>
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: undefined,
  setSessionId: (sessionId) => set({ sessionId }),
  loadChatHistory: async () => {
    const { sessionId } = get()
    if (!sessionId) return []
    
    try {
      const response = await fetch(`http://localhost:8002/apps/representation/users/demo/sessions/${sessionId}`, {
        method: 'GET',
        headers: {
          'accept': 'application/json'
        }
      })
      
      if (!response.ok) {
        console.warn('Failed to load chat history:', response.status)
        return []
      }
      
      const data = await response.json()
      
      const messages: Message[] = []
      if (data.events && Array.isArray(data.events)) {
        data.events.forEach((event: any) => {
          if (event.content && event.content.parts && Array.isArray(event.content.parts)) {
            const content = event.content.parts
              .map((part: any) => part.text || '')
              .filter((text: string) => text.length > 0)
              .join(' ')
            
            if (content) {
              messages.push({
                id: event.id || `msg-${Date.now()}-${Math.random()}`,
                role: event.content.role === 'user' ? 'user' : 'assistant',
                content: content,
                createdAt: event.timestamp ? new Date(event.timestamp * 1000) : new Date()
              })
            }
          }
        })
      }
      
      return messages
    } catch (error) {
      console.error('Error loading chat history:', error)
      return []
    }
  }
}))
