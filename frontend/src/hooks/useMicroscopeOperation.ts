import { useState, useCallback, useEffect } from 'react';
import { MicroscopeOperationWorkflow, MicroscopeOperationHookReturn } from '@/types/microscope_operation';

export function useMicroscopeOperation(): MicroscopeOperationHookReturn {
  const [workflows, setWorkflows] = useState<MicroscopeOperationWorkflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<MicroscopeOperationWorkflow | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mockWorkflows: MicroscopeOperationWorkflow[] = [
    {
      id: '1',
      workflow_id: 'hyper-fib-001',
      name: 'Hyper-Fib 工作流 1',
      description: '显微镜操作工作流程 - 样品分析',
      status: 'completed',
      widget_url: 'http://localhost:3001',
      created_at: Date.now() - 3600000,
      updated_at: Date.now() - 1800000,
    },
    {
      id: '2',
      workflow_id: 'hyper-fib-002',
      name: 'Hyper-Fib 工作流 2',
      description: '显微镜操作工作流程 - 成像分析',
      status: 'running',
      widget_url: 'http://localhost:3001',
      created_at: Date.now() - 7200000,
      updated_at: Date.now() - 900000,
    },
    {
      id: '3',
      workflow_id: 'hyper-fib-003',
      name: 'Hyper-Fib 工作流 3',
      description: '显微镜操作工作流程 - 数据处理',
      status: 'pending',
      widget_url: 'http://localhost:3001',
      created_at: Date.now() - 10800000,
      updated_at: Date.now() - 10800000,
    },
  ];

  const fetchWorkflows = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      setWorkflows(mockWorkflows);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取显微镜操作工作流失败';
      setError(errorMessage);
      console.error('Failed to fetch microscope operation workflows:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createWorkflow = useCallback(async (name: string, description?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const newWorkflow: MicroscopeOperationWorkflow = {
        id: Date.now().toString(),
        workflow_id: `hyper-fib-${Date.now()}`,
        name,
        description,
        status: 'pending',
        widget_url: 'http://localhost:3001',
        created_at: Date.now(),
        updated_at: Date.now(),
      };
      
      setWorkflows(prev => [newWorkflow, ...prev]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '创建显微镜操作工作流失败';
      setError(errorMessage);
      console.error('Failed to create microscope operation workflow:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateWorkflow = useCallback(async (id: string, updates: Partial<MicroscopeOperationWorkflow>) => {
    try {
      setLoading(true);
      setError(null);
      
      setWorkflows(prev => prev.map(workflow => 
        workflow.id === id 
          ? { ...workflow, ...updates, updated_at: Date.now() }
          : workflow
      ));
      
      if (selectedWorkflow?.id === id) {
        setSelectedWorkflow(prev => prev ? { ...prev, ...updates, updated_at: Date.now() } : null);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '更新显微镜操作工作流失败';
      setError(errorMessage);
      console.error('Failed to update microscope operation workflow:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedWorkflow]);

  const deleteWorkflow = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      setWorkflows(prev => prev.filter(workflow => workflow.id !== id));
      
      if (selectedWorkflow?.id === id) {
        setSelectedWorkflow(null);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '删除显微镜操作工作流失败';
      setError(errorMessage);
      console.error('Failed to delete microscope operation workflow:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedWorkflow]);

  const selectWorkflow = useCallback((workflow: MicroscopeOperationWorkflow | null) => {
    setSelectedWorkflow(workflow);
  }, []);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  return {
    workflows,
    selectedWorkflow,
    loading,
    error,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
    fetchWorkflows,
    selectWorkflow,
  };
}
