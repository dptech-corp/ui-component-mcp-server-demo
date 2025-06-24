import { useEffect } from 'react';
import { useApprovals } from '@/hooks/useApprovals';
import { ApprovalItem } from './ApprovalItem';

export function ApprovalList() {
  const {
    approvals,
    loading,
    error,
    fetchApprovals,
    approveRequest,
    rejectRequest,
  } = useApprovals();

  useEffect(() => {
    fetchApprovals();
  }, [fetchApprovals]);

  const handleApprove = async (approvalId: string) => {
    await approveRequest(approvalId);
  };

  const handleReject = async (approvalId: string) => {
    await rejectRequest(approvalId);
  };

  if (loading && approvals.length === 0) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading approvals...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {approvals.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No approval requests</p>
            <p className="text-sm mt-1">Approval requests will appear here when agents need user confirmation.</p>
          </div>
        ) : (
          approvals.map((approval) => (
            <ApprovalItem
              key={approval.id}
              approval={approval}
              onApprove={handleApprove}
              onReject={handleReject}
              disabled={loading}
            />
          ))
        )}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Human-in-the-Loop Approval</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                This system allows AI agents to request human approval before executing certain actions.
              </p>
              <ul className="mt-2 list-disc list-inside space-y-1">
                <li>Agents can call <code>wait_for_approval("description")</code> to request approval</li>
                <li>Approval requests appear here in real-time</li>
                <li>Click "Approve" or "Reject" to respond to requests</li>
                <li>Agents can continue execution based on your decision</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
