import { useState, useEffect } from 'react';
import { Approval } from '@/types/approval';

export function useApprovals() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/approvals');
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
      const response = await fetch(`/api/approvals/${approvalId}/approve`, {
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
      const response = await fetch(`/api/approvals/${approvalId}/reject`, {
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

  useEffect(() => {
    const eventSource = new EventSource('/api/events');
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'approval_request' || data.type === 'approval_updated') {
          fetchApprovals(); // Refresh approvals when new ones arrive or are updated
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const addApproval = (approval: Approval) => {
    setApprovals(prev => [...prev, approval]);
  };

  const updateApproval = (updatedApproval: Approval) => {
    setApprovals(prev => 
      prev.map(approval => 
        approval.id === updatedApproval.id ? updatedApproval : approval
      )
    );
  };

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
