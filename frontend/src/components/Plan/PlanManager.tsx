import { useState, useEffect } from 'react';
import { Plan, TodoItem } from '../../types/plan';
import { PlanList } from './PlanList';
import { TodoList } from './TodoList';
import { usePlansNew } from '../../hooks/usePlansNew';
import { useTodos } from '../../hooks/useTodos';
import { useSSE } from '../../contexts/SSEContext';

interface PlanManagerProps {
  sessionId?: string;
}

export function PlanManager({ sessionId = "default_session" }: PlanManagerProps) {
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [todosLoading] = useState(false);
  const [todosError] = useState<string | null>(null);
  
  const { plans, loading, error, fetchPlans, deletePlan } = usePlansNew();
  const { todos: allTodos, fetchTodos, toggleTodo, deleteTodo } = useTodos();
  const { lastEvent } = useSSE();

  useEffect(() => {
    fetchPlans(sessionId);
  }, [fetchPlans, sessionId]);

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'todo_added':
        case 'todo_updated':
        case 'todo_deleted':
          if (selectedPlan) {
            fetchTodos(sessionId);
          }
          break;
      }
    }
  }, [lastEvent, selectedPlan, fetchTodos, sessionId]);

  useEffect(() => {
    if (selectedPlan) {
      const planTodos = allTodos.filter((todo: TodoItem) => todo.plan_id === selectedPlan.id);
      setTodos(planTodos);
    }
  }, [allTodos, selectedPlan]);

  const handleSelectPlan = (plan: Plan) => {
    setSelectedPlan(plan);
    fetchTodos(sessionId);
  };

  const handleBackToPlans = () => {
    setSelectedPlan(null);
    setTodos([]);
  };

  const handleDeletePlan = async (planId: string) => {
    try {
      await deletePlan(planId);
      if (selectedPlan?.id === planId) {
        setSelectedPlan(null);
        setTodos([]);
      }
    } catch (error) {
      console.error('Failed to delete plan:', error);
    }
  };

  const handleToggleTodo = async (todoId: string) => {
    try {
      await toggleTodo(todoId);
    } catch (error) {
      console.error('Failed to toggle todo:', error);
    }
  };

  const handleDeleteTodo = async (todoId: string) => {
    try {
      await deleteTodo(todoId);
    } catch (error) {
      console.error('Failed to delete todo:', error);
    }
  };

  if (selectedPlan) {
    return (
      <TodoList
        todos={todos}
        loading={todosLoading}
        error={todosError}
        onToggleTodo={handleToggleTodo}
        onDeleteTodo={handleDeleteTodo}
        onBack={handleBackToPlans}
        planTitle={selectedPlan.title}
      />
    );
  }

  return (
    <PlanList
      plans={plans}
      loading={loading}
      error={error}
      onSelectPlan={handleSelectPlan}
      onDeletePlan={handleDeletePlan}
      selectedPlan={selectedPlan}
    />
  );
}
