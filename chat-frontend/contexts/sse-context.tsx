'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

interface SSEEvent {
  event: string
  data: any
}

interface SSEContextType {
  isConnected: boolean
  lastEvent: SSEEvent | null
}

const SSEContext = createContext<SSEContextType>({
  isConnected: false,
  lastEvent: null,
})

export function useSSE() {
  return useContext(SSEContext)
}

interface SSEProviderProps {
  children: ReactNode
}

export function SSEProvider({ children }: SSEProviderProps) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null)

  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/events')
    
    eventSource.onopen = () => {
      setIsConnected(true)
    }
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastEvent({
          event: event.type || 'message',
          data,
        })
      } catch (error) {
        console.error('Error parsing SSE event:', error)
      }
    }
    
    eventSource.onerror = () => {
      setIsConnected(false)
    }
    
    return () => {
      eventSource.close()
    }
  }, [])

  return (
    <SSEContext.Provider value={{ isConnected, lastEvent }}>
      {children}
    </SSEContext.Provider>
  )
}
