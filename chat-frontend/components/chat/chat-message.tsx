'use client'

import { Message } from 'ai'

interface ChatMessageProps {
  message: Message & { messageType?: 'function' | 'text' }
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const isFunction = message.messageType === 'function'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : isFunction
            ? 'bg-amber-50 border border-amber-200 text-amber-800'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {isFunction && (
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
            <span className="text-xs font-medium text-amber-700">Function Call</span>
          </div>
        )}
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  )
}
