import { useState } from 'react';
import { Approval } from '@/types/approval';

interface ApprovalItemProps {
  approval: Approval;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  disabled?: boolean;
}

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText: string;
  cancelText: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmButtonClass: string;
}

const ConfirmationDialog = ({ 
  isOpen, 
  title, 
  message, 
  confirmText, 
  cancelText, 
  onConfirm, 
  onCancel, 
  confirmButtonClass 
}: ConfirmationDialogProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
        <p className="text-sm text-gray-600 mb-6 whitespace-pre-line">{message}</p>
        <div className="flex space-x-3">
          <button
            onClick={onConfirm}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 ${confirmButtonClass}`}
          >
            {confirmText}
          </button>
          <button
            onClick={onCancel}
            className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            {cancelText}
          </button>
        </div>
      </div>
    </div>
  );
};

export function ApprovalItem({ approval, onApprove, onReject, disabled }: ApprovalItemProps) {
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject';
  }>({
    isOpen: false,
    type: 'approve'
  });
  
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

  const handleApprove = () => {
    setConfirmDialog({ isOpen: true, type: 'approve' });
  };

  const handleReject = () => {
    setConfirmDialog({ isOpen: true, type: 'reject' });
  };

  const confirmAction = () => {
    if (confirmDialog.type === 'approve') {
      onApprove(approval.id);
    } else {
      onReject(approval.id);
    }
    setConfirmDialog({ isOpen: false, type: 'approve' });
  };

  const cancelAction = () => {
    setConfirmDialog({ isOpen: false, type: 'approve' });
  };

  return (
    <>
      <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(approval.status)}`}>
                {approval.status.toUpperCase()}
              </span>
              <span className="text-xs text-gray-500">
                {formatDate(approval.created_at)}
              </span>
            </div>
            
            <p className="text-sm text-gray-900 mb-2">{approval.description}</p>
            
            <div className="text-xs text-gray-500 space-y-1">
              <div>Session: {approval.session_id}</div>
              <div>Function Call: {approval.function_call_id}</div>
              {approval.result && (
                <div>Result: {approval.result}</div>
              )}
            </div>
          </div>
          
          {approval.status === 'pending' && (
            <div className="flex space-x-2 ml-4">
              <button
                onClick={handleApprove}
                disabled={disabled}
                className="px-3 py-1 text-sm font-medium text-white bg-green-600 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Approve
              </button>
              <button
                onClick={handleReject}
                disabled={disabled}
                className="px-3 py-1 text-sm font-medium text-white bg-red-600 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Reject
              </button>
            </div>
          )}
        </div>
      </div>

      <ConfirmationDialog
        isOpen={confirmDialog.isOpen}
        title={confirmDialog.type === 'approve' ? 'Confirm Approval' : 'Confirm Rejection'}
        message={`Are you sure you want to ${confirmDialog.type} this request?\n\n"${approval.description}"`}
        confirmText={confirmDialog.type === 'approve' ? 'Approve' : 'Reject'}
        cancelText="Cancel"
        onConfirm={confirmAction}
        onCancel={cancelAction}
        confirmButtonClass={
          confirmDialog.type === 'approve' 
            ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
            : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
        }
      />
    </>
  );
}
