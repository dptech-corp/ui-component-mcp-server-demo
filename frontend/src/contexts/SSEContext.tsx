import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import type { Approval } from '@/types/approval';

interface SSEEvent {
  event: string;
  data: any;
}

interface SSEContextType {
  isConnected: boolean;
  lastEvent: SSEEvent | null;
  error: string | null;
  approvals: Approval[];
  addApproval: (approval: Approval) => void;
  updateApproval: (approval: Approval) => void;
  setApprovals: (approvals: Approval[]) => void;
}

const SSEContext = createContext<SSEContextType | undefined>(undefined);

export function SSEProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const sseUrl = `${import.meta.env.VITE_SSE_URL || 'http://localhost:8000/events'}`;

  const connect = () => {
    try {
      const eventSource = new EventSource(sseUrl);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('SSE connection established');
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastEvent(data);
          console.log('SSE event received:', data);
          
          if (data.type === 'approval_request' && data.data?.approval) {
            setApprovals(prev => [...prev, data.data.approval]);
          } else if (data.type === 'approval_updated' && data.data?.approval) {
            setApprovals(prev => 
              prev.map(approval => 
                approval.id === data.data.approval.id ? data.data.approval : approval
              )
            );
          }
        } catch (err) {
          console.error('Failed to parse SSE event data:', err);
        }
      };

      eventSource.onerror = (event) => {
        console.error('SSE connection error:', event);
        setIsConnected(false);
        setError('连接错误，正在尝试重连...');
        
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        
        reconnectTimeoutRef.current = setTimeout(() => {
          if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
            connect();
          }
        }, 3000) as unknown as number;
      };

      eventSource.addEventListener('close', () => {
        setIsConnected(false);
        console.log('SSE connection closed');
      });

    } catch (err) {
      console.error('Failed to create SSE connection:', err);
      setError('无法建立连接');
    }
  };

  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    setIsConnected(false);
  };

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [sseUrl]);

  const addApproval = (approval: Approval) => {
    setApprovals(prev => [...prev, approval]);
  };

  const updateApproval = (updatedApproval: Approval) => {
    setApprovals(prev => 
      prev.map(approval => 
        approval.id === updatedApproval.id ? updatedApproval : approval
      )
    );
  };

  return (
    <SSEContext.Provider value={{ 
      isConnected, 
      lastEvent, 
      error, 
      approvals, 
      addApproval, 
      updateApproval, 
      setApprovals 
    }}>
      {children}
    </SSEContext.Provider>
  );
}

export function useSSE() {
  const context = useContext(SSEContext);
  if (context === undefined) {
    throw new Error('useSSE must be used within an SSEProvider');
  }
  return context;
}
