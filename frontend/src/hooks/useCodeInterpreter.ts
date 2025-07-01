import { useState, useCallback, useEffect } from 'react';
import { CodeInterpreterState, CodeInterpreterCreateRequest, CodeInterpreterUpdateRequest, CodeInterpreterHookReturn } from '@/types/code_interpreter';
import { useSSE } from '@/contexts/SSEContext';

export function useCodeInterpreter(): CodeInterpreterHookReturn {
  const [states, setStates] = useState<CodeInterpreterState[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastEvent } = useSSE();

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'code_interpreter_state_created':
          if (lastEvent.data.state) {
            setStates((prev: CodeInterpreterState[]) => {
              const exists = prev.some((state: CodeInterpreterState) => state.id === lastEvent.data.state.id);
              if (!exists) {
                return [lastEvent.data.state, ...prev];
              }
              return prev;
            });
          }
          break;
          
        case 'code_interpreter_state_updated':
          if (lastEvent.data.state) {
            setStates((prev: CodeInterpreterState[]) => prev.map((state: CodeInterpreterState) => 
              state.id === lastEvent.data.state.id ? lastEvent.data.state : state
            ));
          }
          break;
          
        case 'code_interpreter_state_retrieved':
          if (lastEvent.data.state) {
            setStates((prev: CodeInterpreterState[]) => {
              const exists = prev.some((state: CodeInterpreterState) => state.id === lastEvent.data.state.id);
              if (!exists) {
                return [lastEvent.data.state, ...prev];
              }
              return prev.map((state: CodeInterpreterState) => 
                state.id === lastEvent.data.state.id ? lastEvent.data.state : state
              );
            });
          }
          break;
          
        case 'error':
          setError(lastEvent.data.message || '发生未知错误');
          setLoading(false);
          break;
      }
    }
  }, [lastEvent]);

  const fetchStates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/code-interpreter/states`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setStates(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取代码解释器状态失败';
      setError(errorMessage);
      console.error('Failed to fetch code interpreter states:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const createState = useCallback(async (sessionId: string, code: string, description?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const stateData: CodeInterpreterCreateRequest = { session_id: sessionId, code, description };
      
      const response = await fetch(`${apiUrl}/api/code-interpreter/states`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(stateData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '创建代码解释器状态失败';
      setError(errorMessage);
      console.error('Failed to create code interpreter state:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const updateState = useCallback(async (id: string, updates: Partial<CodeInterpreterState>) => {
    try {
      setLoading(true);
      setError(null);
      
      const updateData: CodeInterpreterUpdateRequest = {
        status: updates.status,
        result: updates.result,
      };
      
      const response = await fetch(`${apiUrl}/api/code-interpreter/states/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '更新代码解释器状态失败';
      setError(errorMessage);
      console.error('Failed to update code interpreter state:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const getState = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/code-interpreter/states/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const state = await response.json();
      setStates((prev: CodeInterpreterState[]) => {
        const exists = prev.some((s: CodeInterpreterState) => s.id === state.id);
        if (!exists) {
          return [state, ...prev];
        }
        return prev.map((s: CodeInterpreterState) => s.id === state.id ? state : s);
      });
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取代码解释器状态失败';
      setError(errorMessage);
      console.error('Failed to get code interpreter state:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    fetchStates();
  }, [fetchStates]);

  return {
    states,
    loading,
    error,
    createState,
    updateState,
    getState,
    fetchStates,
  };
}
