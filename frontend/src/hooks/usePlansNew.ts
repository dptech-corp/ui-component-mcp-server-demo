import { useState, useCallback, useEffect } from 'react';
import { Plan, PlanCreateRequest } from '../types/plan';
import { useSSE } from '../contexts/SSEContext';

export function usePlansNew() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastEvent } = useSSE();

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'plan_created':
          if (lastEvent.data.plan) {
            setPlans(prev => {
              const exists = prev.some(plan => plan.id === lastEvent.data.plan.id);
              if (!exists) {
                return [lastEvent.data.plan, ...prev];
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
      }
    }
  }, [lastEvent]);

  const fetchPlans = useCallback(async (sessionId?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const url = sessionId 
        ? `/api/plans?session_id=${encodeURIComponent(sessionId)}`
        : '/api/plans';
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch plans: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPlans(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch plans';
      setError(errorMessage);
      console.error('Error fetching plans:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createPlan = useCallback(async (planData: PlanCreateRequest) => {
    setError(null);
    
    try {
      const response = await fetch('/api/plans', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(planData),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create plan: ${response.statusText}`);
      }
      
      const newPlan = await response.json();
      return newPlan;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create plan';
      setError(errorMessage);
      console.error('Error creating plan:', err);
      throw err;
    }
  }, []);

  const deletePlan = useCallback(async (planId: string) => {
    setError(null);
    
    try {
      const response = await fetch(`/api/plans/${planId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete plan: ${response.statusText}`);
      }
      
      setPlans(prev => prev.filter(plan => plan.id !== planId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete plan';
      setError(errorMessage);
      console.error('Error deleting plan:', err);
      throw err;
    }
  }, []);

  const updatePlan = useCallback(async (planId: string, updates: Partial<Plan>) => {
    setError(null);
    
    try {
      const response = await fetch(`/api/plans/${planId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update plan: ${response.statusText}`);
      }
      
      const updatedPlan = await response.json();
      setPlans(prev => prev.map(plan => 
        plan.id === planId ? updatedPlan : plan
      ));
      
      return updatedPlan;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update plan';
      setError(errorMessage);
      console.error('Error updating plan:', err);
      throw err;
    }
  }, []);

  return {
    plans,
    loading,
    error,
    fetchPlans,
    createPlan,
    deletePlan,
    updatePlan,
  };
}
