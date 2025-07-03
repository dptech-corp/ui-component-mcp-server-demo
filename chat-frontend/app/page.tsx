'use client'

import { ChatView } from '@/components/chat/chat-view'
import { TabLayout } from '@/components/tabs/tab-layout'
import { SSEProvider } from '@/contexts/sse-context'

export default function HomePage() {
  return (
    <SSEProvider>
      <div className="h-screen bg-gray-50">
        <div className="h-full flex">
          <div className="flex-1">
            <ChatView />
          </div>
          <div className="w-96 border-l bg-white">
            <TabLayout />
          </div>
        </div>
      </div>
    </SSEProvider>
  )
}
