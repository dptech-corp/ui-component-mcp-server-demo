import { useState, useCallback } from 'react';
import { AgentMessage, AgentMessageRequest, AgentResponse } from '../types/agent';

export const useAgent = () => {
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

  const sendMessage = useCallback(async (text: string, sessionId?: string) => {
    if (!text.trim()) return;

    setError(null);
    setLoading(true);

    addMessage(text, 'user');

    try {
      const requestData: AgentMessageRequest = {
        message: text,
        sessionId: sessionId || 'demo'
      };

      const response = await fetch(`${(import.meta.env as any).VITE_API_URL || 'http://localhost:8000'}/api/agent/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: AgentResponse = await response.json();

      if (result.success && result.response) {
        let responseText = '';
        
        if (Array.isArray(result.response)) {
          responseText = result.response
            .map(item => {
              if (item.type === 'text' && item.text) {
                return item.text;
              } else if (item.type === 'function_call' && item.function_call) {
                return `调用函数: ${item.function_call.name}`;
              }
              return '';
            })
            .filter(Boolean)
            .join('\n');
        } else if (typeof result.response === 'string') {
          responseText = result.response;
        } else if (result.response.text) {
          responseText = result.response.text;
        } else {
          responseText = JSON.stringify(result.response);
        }

        if (responseText) {
          addMessage(responseText, 'agent');
        } else {
          addMessage('收到响应，但内容为空', 'agent');
        }
      } else {
        throw new Error(result.error || 'Agent 响应失败');
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
    sendMessage,
    clearMessages,
  };
};
