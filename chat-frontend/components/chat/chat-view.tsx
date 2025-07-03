'use client'

import { useRef, useEffect, useState } from 'react'
import { nanoid } from 'nanoid'
import { ChatMessage } from './chat-message'
import { ChatInput } from './chat-input'
import { useChatStore } from '@/store/chat-store'
import { useChat } from 'ai/react'

export function ChatView() {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [inputValue, setInputValue] = useState('')
  const { sessionId, setSessionId } = useChatStore()

  useEffect(() => {
    if (!sessionId) {
      setSessionId(nanoid())
    }
  }, [sessionId, setSessionId])

  const { messages, isLoading, append, setMessages } = useChat({
    api: '/api/chat',
    id: sessionId,
    onFinish() {
      scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
    },
  })

  const handleMessageSubmit = async (content: string) => {
    if (!content.trim()) return
    
    setInputValue('')
    const message = {
      id: nanoid(),
      role: 'user' as const,
      content,
      createdAt: new Date(),
    }
    
    await append(message)
  }

  const handleInputChange = (value: string) => {
    setInputValue(value)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white border-b px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">通用表征代理</h1>
        <p className="text-gray-600">具备读算作报能力的智能协作平台</p>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-auto p-6"
      >
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-700 mb-2">
                欢迎使用通用表征代理
              </h2>
              <p className="text-gray-500">
                开始对话，我将协助您完成各种表征分析任务
              </p>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, i) => (
              <ChatMessage key={i} message={message} />
            ))}
          </div>
        )}
      </div>

      <div className="bg-white border-t p-6">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            value={inputValue}
            onChange={handleInputChange}
            onSubmit={handleMessageSubmit}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  )
}
