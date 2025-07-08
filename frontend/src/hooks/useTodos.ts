import { useState, useCallback, useEffect } from 'react';
import { TodoItem } from '../types/plan';
import { useSSE } from '../contexts/SSEContext';

export function useTodos() {
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastEvent } = useSSE();

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'todo_added':
          if (lastEvent.data.todo) {
            setTodos(prev => {
              const exists = prev.some(todo => todo.id === lastEvent.data.todo.id);
              if (!exists) {
                return [lastEvent.data.todo, ...prev];
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
      }
    }
  }, [lastEvent]);

  const fetchTodos = useCallback(async (sessionId?: string, planId?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      let url = '/api/todos';
      const params = new URLSearchParams();
      
      if (sessionId) {
        params.append('session_id', sessionId);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch todos: ${response.statusText}`);
      }
      
      const data = await response.json();
      let filteredTodos = data;
      
      if (planId) {
        filteredTodos = data.filter((todo: TodoItem) => todo.plan_id === planId);
      }
      
      setTodos(filteredTodos);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch todos';
      setError(errorMessage);
      console.error('Error fetching todos:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleTodo = useCallback(async (todoId: string) => {
    setError(null);
    
    try {
      const response = await fetch(`/api/todos/${todoId}/toggle`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to toggle todo: ${response.statusText}`);
      }
      
      const updatedTodo = await response.json();
      setTodos(prev => prev.map(todo => 
        todo.id === todoId ? updatedTodo : todo
      ));
      
      return updatedTodo;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to toggle todo';
      setError(errorMessage);
      console.error('Error toggling todo:', err);
      throw err;
    }
  }, []);

  const deleteTodo = useCallback(async (todoId: string) => {
    setError(null);
    
    try {
      const response = await fetch(`/api/todos/${todoId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete todo: ${response.statusText}`);
      }
      
      setTodos(prev => prev.filter(todo => todo.id !== todoId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete todo';
      setError(errorMessage);
      console.error('Error deleting todo:', err);
      throw err;
    }
  }, []);

  return {
    todos,
    loading,
    error,
    fetchTodos,
    toggleTodo,
    deleteTodo,
  };
}
