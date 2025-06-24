import { Approval } from '@/types/approval';

interface ApprovalItemProps {
  approval: Approval;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  disabled?: boolean;
}

export function ApprovalItem({ approval, onApprove, onReject, disabled }: ApprovalItemProps) {
  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(approval.status)}`}>
              {approval.status.toUpperCase()}
            </span>
            <span className="text-xs text-gray-500">
              Session: {approval.session_id}
            </span>
          </div>
          
          <p className="text-gray-900 mb-2">{approval.description}</p>
          
          <div className="text-xs text-gray-500 space-y-1">
            <div>Function Call ID: {approval.function_call_id}</div>
            <div>Created: {formatDate(approval.created_at)}</div>
            {approval.updated_at !== approval.created_at && (
              <div>Updated: {formatDate(approval.updated_at)}</div>
            )}
          </div>
        </div>
        
        {approval.status === 'pending' && (
          <div className="flex space-x-2 ml-4">
            <button
              onClick={() => onApprove(approval.id)}
              disabled={disabled}
              className="px-3 py-1 text-sm font-medium text-white bg-green-600 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Approve
            </button>
            <button
              onClick={() => onReject(approval.id)}
              disabled={disabled}
              className="px-3 py-1 text-sm font-medium text-white bg-red-600 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Reject
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
