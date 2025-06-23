import { useState, useCallback, useEffect } from 'react';
import { TodoItem, TodoCreateRequest, TodoUpdateRequest, BacklogItem } from '@/types/todo';
import { useSSE } from './useSSE';

interface UseTodosReturn {
  todos: TodoItem[];
  backlogItems: BacklogItem[];
  loading: boolean;
  error: string | null;
  addTodo: (title: string, description?: string) => Promise<void>;
  updateTodo: (id: string, updates: Partial<TodoItem>) => Promise<void>;
  deleteTodo: (id: string) => Promise<void>;
  toggleTodo: (id: string) => Promise<void>;
  fetchTodos: () => Promise<void>;
  addBacklogItem: (title: string, description?: string) => void;
  updateBacklogItem: (id: string, updates: Partial<BacklogItem>) => void;
  deleteBacklogItem: (id: string) => void;
  moveToTodo: (id: string) => Promise<void>;
}

export function useTodos(): UseTodosReturn {
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [backlogItems, setBacklogItems] = useState<BacklogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastEvent } = useSSE();

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'todo_added':
          if (lastEvent.data.todo) {
            setTodos(prev => {
              const exists = prev.some(todo => todo.id === lastEvent.data.todo.id);
              if (!exists) {
                return [...prev, lastEvent.data.todo];
              }
              return prev;
            });
          }
          break;
          
        case 'todo_updated':
          if (lastEvent.data.todo) {
            setTodos(prev => prev.map(todo => 
              todo.id === lastEvent.data.todo.id ? lastEvent.data.todo : todo
            ));
          }
          break;
          
        case 'todo_deleted':
          if (lastEvent.data.todoId) {
            setTodos(prev => prev.filter(todo => todo.id !== lastEvent.data.todoId));
          }
          break;
          
        case 'todo_list':
          if (lastEvent.data.todos) {
            setTodos(lastEvent.data.todos);
          }
          break;
          
        case 'error':
          setError(lastEvent.data.message || '发生未知错误');
          break;
      }
    }
  }, [lastEvent]);

  const fetchTodos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/todos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTodos(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取 Todo 列表失败';
      setError(errorMessage);
      console.error('Failed to fetch todos:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const addTodo = useCallback(async (title: string, description?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const todoData: TodoCreateRequest = { title, description };
      
      const response = await fetch(`${apiUrl}/api/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(todoData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      await fetchTodos();
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '添加 Todo 失败';
      setError(errorMessage);
      console.error('Failed to add todo:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, fetchTodos]);

  const updateTodo = useCallback(async (id: string, updates: Partial<TodoItem>) => {
    try {
      setLoading(true);
      setError(null);
      
      const updateData: TodoUpdateRequest = {
        title: updates.title,
        description: updates.description,
        completed: updates.completed,
      };
      
      const response = await fetch(`${apiUrl}/api/todos/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      await fetchTodos();
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '更新 Todo 失败';
      setError(errorMessage);
      console.error('Failed to update todo:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, fetchTodos]);

  const deleteTodo = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/todos/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      await fetchTodos();
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '删除 Todo 失败';
      setError(errorMessage);
      console.error('Failed to delete todo:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, fetchTodos]);

  const toggleTodo = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/todos/${id}/toggle`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      await fetchTodos();
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '切换 Todo 状态失败';
      setError(errorMessage);
      console.error('Failed to toggle todo:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, fetchTodos]);

  const addBacklogItem = useCallback((title: string, description?: string) => {
    const newItem: BacklogItem = {
      id: `backlog_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title,
      description,
      created_at: Date.now(),
      updated_at: Date.now(),
    };
    setBacklogItems(prev => [...prev, newItem]);
  }, []);

  const updateBacklogItem = useCallback((id: string, updates: Partial<BacklogItem>) => {
    setBacklogItems(prev => prev.map(item => 
      item.id === id 
        ? { ...item, ...updates, updated_at: Date.now() }
        : item
    ));
  }, []);

  const deleteBacklogItem = useCallback((id: string) => {
    setBacklogItems(prev => prev.filter(item => item.id !== id));
  }, []);

  const moveToTodo = useCallback(async (id: string) => {
    const backlogItem = backlogItems.find(item => item.id === id);
    if (!backlogItem) return;

    try {
      await addTodo(backlogItem.title, backlogItem.description);
      deleteBacklogItem(id);
    } catch (err) {
      console.error('Failed to move backlog item to todo:', err);
    }
  }, [backlogItems, addTodo, deleteBacklogItem]);

  return {
    todos,
    backlogItems,
    loading,
    error,
    addTodo,
    updateTodo,
    deleteTodo,
    toggleTodo,
    fetchTodos,
    addBacklogItem,
    updateBacklogItem,
    deleteBacklogItem,
    moveToTodo,
  };
}
