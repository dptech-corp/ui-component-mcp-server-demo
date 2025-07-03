import { useState, useCallback } from 'react';
import { AgentMessage, AgentStreamRequest } from '../types/agent';

export const useAgentStream = () => {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addMessage = useCallback((text: string, role: 'user' | 'agent') => {
    const message: AgentMessage = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      text,
      role,
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, message]);
    return message;
  }, []);

  const sendStreamMessage = useCallback(async (text: string, sessionId?: string) => {
    if (!text.trim()) return;

    setError(null);
    setLoading(true);

    addMessage(text, 'user');

    try {
      const requestData: AgentStreamRequest = {
        message: text,
        sessionId: sessionId || 'demo'
      };

      const response = await fetch(`${(import.meta.env as any).VITE_API_URL || 'http://localhost:8000'}/api/agent/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      let agentMessageId = '';
      let agentMessageText = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.error) {
                  throw new Error(data.error);
                }
                
                if (data.content && data.content.parts && data.content.parts.length > 0) {
                  const text = data.content.parts[0].text;
                  if (text) {
                    if (!agentMessageId) {
                      const agentMessage = addMessage('', 'agent');
                      agentMessageId = agentMessage.id;
                    }
                    
                    if (data.partial) {
                      agentMessageText += text;
                    } else {
                      agentMessageText += text;
                    }
                    
                    setMessages(prev => prev.map(msg => 
                      msg.id === agentMessageId 
                        ? { ...msg, text: agentMessageText }
                        : msg
                    ));
                  }
                } else if (data.text) {
                  if (!agentMessageId) {
                    const agentMessage = addMessage('', 'agent');
                    agentMessageId = agentMessage.id;
                  }
                  
                  agentMessageText += data.text;
                  
                  setMessages(prev => prev.map(msg => 
                    msg.id === agentMessageId 
                      ? { ...msg, text: agentMessageText }
                      : msg
                  ));
                }
                
                if (data.done) {
                  break;
                }
              } catch (parseError) {
                console.warn('Failed to parse SSE data:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      if (!agentMessageText) {
        addMessage('收到响应，但内容为空', 'agent');
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '发送消息失败';
      setError(errorMessage);
      addMessage(`错误: ${errorMessage}`, 'agent');
    } finally {
      setLoading(false);
    }
  }, [addMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage: sendStreamMessage,
    clearMessages,
  };
};
