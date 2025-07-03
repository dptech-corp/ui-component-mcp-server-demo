'use client'

import { ChatView } from '@/components/chat/chat-view'
import { SSEProvider } from '@/contexts/sse-context'

export default function HomePage() {
  return (
    <SSEProvider>
      <div className="h-screen bg-gray-50">
        <ChatView />
      </div>
    </SSEProvider>
  )
}
