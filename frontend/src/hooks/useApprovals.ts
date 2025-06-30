// @ts-ignore - 忽略 React 模块类型声明错误
import { useState, useEffect } from 'react';
import { useSSE } from '@/contexts/SSEContext';

export function useApprovals() {
  const { approvals, setApprovals, addApproval, updateApproval } = useSSE();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/approvals`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setApprovals(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch approvals');
      console.error('Error fetching approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  const approveRequest = async (approvalId: string) => {
    try {
      const response = await fetch(`${apiUrl}/api/approvals/${approvalId}/approve`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await fetchApprovals(); // Refresh the list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve request');
      console.error('Error approving request:', err);
    }
  };

  const rejectRequest = async (approvalId: string) => {
    try {
      const response = await fetch(`${apiUrl}/api/approvals/${approvalId}/reject`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await fetchApprovals(); // Refresh the list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject request');
      console.error('Error rejecting request:', err);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  return {
    approvals,
    loading,
    error,
    approveRequest,
    rejectRequest,
    refetch: fetchApprovals,
    addApproval,
    updateApproval,
  };
}
