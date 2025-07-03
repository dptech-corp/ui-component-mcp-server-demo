import { useState, useCallback, useEffect } from 'react';
import { PlanItem, PlanCreateRequest, PlanUpdateRequest } from '@/types/plan';
import { useSSE } from '@/contexts/SSEContext';

interface UsePlansReturn {
  plans: PlanItem[];
  loading: boolean;
  error: string | null;
  addPlan: (title: string, description?: string) => Promise<void>;
  updatePlan: (id: string, updates: Partial<PlanItem>) => Promise<void>;
  deletePlan: (id: string) => Promise<void>;
  togglePlan: (id: string) => Promise<void>;
  fetchPlans: () => Promise<void>;
}

export function usePlans(): UsePlansReturn {
  const [plans, setPlans] = useState<PlanItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastEvent } = useSSE();

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'plan_added':
          if (lastEvent.data.plan) {
            setPlans(prev => {
              const exists = prev.some(plan => plan.id === lastEvent.data.plan.id);
              if (!exists) {
                return [...prev, lastEvent.data.plan];
              }
              return prev;
            });
          }
          break;
          
        case 'plan_updated':
          if (lastEvent.data.plan) {
            setPlans(prev => prev.map(plan => 
              plan.id === lastEvent.data.plan.id ? lastEvent.data.plan : plan
            ));
          }
          break;
          
        case 'plan_deleted':
          if (lastEvent.data.planId) {
            setPlans(prev => prev.filter(plan => plan.id !== lastEvent.data.planId));
          }
          break;
          
        case 'plan_list':
          if (lastEvent.data.plans) {
            setPlans(lastEvent.data.plans);
          }
          break;
          
          
        case 'error':
          setError(lastEvent.data.message || '发生未知错误');
          setLoading(false);
          break;
      }
    }
  }, [lastEvent]);

  const fetchPlans = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/todos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setPlans(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取 Plan 列表失败';
      setError(errorMessage);
      console.error('Failed to fetch plans:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const addPlan = useCallback(async (title: string, description?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const planData: PlanCreateRequest = { title, description };
      
      const response = await fetch(`${apiUrl}/api/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(planData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '添加 Plan 失败';
      setError(errorMessage);
      console.error('Failed to add plan:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const updatePlan = useCallback(async (id: string, updates: Partial<PlanItem>) => {
    try {
      setLoading(true);
      setError(null);
      
      const updateData: PlanUpdateRequest = {
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
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '更新 Plan 失败';
      setError(errorMessage);
      console.error('Failed to update plan:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const deletePlan = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/todos/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '删除 Plan 失败';
      setError(errorMessage);
      console.error('Failed to delete plan:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  const togglePlan = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/api/todos/${id}/toggle`, {
        method: 'PATCH',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '切换 Plan 状态失败';
      setError(errorMessage);
      console.error('Failed to toggle plan:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);


  useEffect(() => {
    fetchPlans();
  }, [fetchPlans]);



  return {
    plans,
    loading,
    error,
    addPlan,
    updatePlan,
    deletePlan,
    togglePlan,
    fetchPlans,
  };
}
