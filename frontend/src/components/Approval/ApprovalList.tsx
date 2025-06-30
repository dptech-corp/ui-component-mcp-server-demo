// @ts-ignore - 忽略 React 模块类型声明错误
import { ApprovalItem } from './ApprovalItem';
import type { Approval } from '@/types/approval';

interface ApprovalListProps {
  approvals: Approval[];
  loading: boolean;
  error: string | null;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function ApprovalList({ approvals, loading, error, onApprove, onReject }: ApprovalListProps) {

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading approvals...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="text-red-800">Error: {error}</div>
      </div>
    );
  }

  if (approvals.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="text-gray-500 mb-2">No approval requests</div>
        <div className="text-sm text-gray-400">
          Approval requests will appear here when the agent needs human confirmation.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Approval Requests ({approvals.length})
        </h2>
      </div>
      
      <div className="space-y-3">
        {approvals.map((approval) => (
          <ApprovalItem
            key={approval.id}
            approval={approval}
            onApprove={() => onApprove(approval.id)}
            onReject={() => onReject(approval.id)}
          />
        ))}
      </div>
    </div>
  );
}
