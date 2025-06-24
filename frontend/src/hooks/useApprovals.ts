import { useState, useCallback } from 'react';
import { Approval, ApprovalState } from '@/types/approval';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useApprovals() {
  const [state, setState] = useState<ApprovalState>({
    approvals: [],
    loading: false,
    error: null,
  });

  const fetchApprovals = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(`${API_URL}/api/approvals`);
      if (!response.ok) {
        throw new Error('Failed to fetch approvals');
      }
      
      const approvals = await response.json();
      setState(prev => ({ ...prev, approvals, loading: false }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }));
    }
  }, []);

  const approveRequest = useCallback(async (approvalId: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(`${API_URL}/api/approvals/${approvalId}/approve`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to approve request');
      }
      
      await fetchApprovals();
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }));
    }
  }, [fetchApprovals]);

  const rejectRequest = useCallback(async (approvalId: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(`${API_URL}/api/approvals/${approvalId}/reject`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to reject request');
      }
      
      await fetchApprovals();
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }));
    }
  }, [fetchApprovals]);

  const addApproval = useCallback((approval: Approval) => {
    setState(prev => ({
      ...prev,
      approvals: [approval, ...prev.approvals]
    }));
  }, []);

  const updateApproval = useCallback((updatedApproval: Approval) => {
    setState(prev => ({
      ...prev,
      approvals: prev.approvals.map(approval =>
        approval.id === updatedApproval.id ? updatedApproval : approval
      )
    }));
  }, []);

  return {
    ...state,
    fetchApprovals,
    approveRequest,
    rejectRequest,
    addApproval,
    updateApproval,
  };
}
