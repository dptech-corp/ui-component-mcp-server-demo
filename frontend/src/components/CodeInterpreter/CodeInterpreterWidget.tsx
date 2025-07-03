import { useState } from 'react';
import { CodeInterpreterState } from '@/types/code_interpreter';

interface CodeInterpreterWidgetProps {
  state: CodeInterpreterState;
  onBack: () => void;
  onUpdateState: (id: string, updates: Partial<CodeInterpreterState>) => Promise<void>;
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

export function CodeInterpreterWidget({ state, onBack, onUpdateState }: CodeInterpreterWidgetProps) {
  const [confirmDialog, setConfirmDialog] = useState({
    isOpen: false
  });
  const [isConfirming, setIsConfirming] = useState(false);

  const handleConfirm = () => {
    setConfirmDialog({ isOpen: true });
  };

  const confirmAction = async () => {
    setIsConfirming(true);
    setConfirmDialog({ isOpen: false });

    try {
      await onUpdateState(state.id, { status: 'approved' });
    } catch (error) {
      console.error('Failed to update state:', error);
      setIsConfirming(false);
    }
  };

  const cancelAction = () => {
    setConfirmDialog({ isOpen: false });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          ← 返回列表
        </button>
        <h3 className="text-lg font-medium text-gray-900">{state.ticket_id}</h3>
      </div>

      {state.description && (
        <p className="text-sm text-gray-600">{state.description}</p>
      )}


      {state.result && (
        <div className="bg-green-50 border border-green-200 rounded p-3">
          <h4 className="text-sm font-medium text-green-800 mb-1">执行结果:</h4>
          <pre className="text-sm text-green-700 whitespace-pre-wrap font-mono">
            {state.result}
          </pre>
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={state.status === 'approved' || isConfirming ? undefined : handleConfirm}
          disabled={state.status === 'approved' || isConfirming}
          className={`px-4 py-2 rounded focus:outline-none focus:ring-2 ${
            state.status === 'approved' || isConfirming
              ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500'
          }`}
        >
          {state.status === 'approved' ? '已确认' : isConfirming ? '确认中...' : '确认'}
        </button>
      </div>

      {state.widget_url && (
        <div className="border rounded-lg overflow-hidden" style={{ height: '500px' }}>
          <iframe
            src={state.widget_url}
            className="w-full h-full border-0"
            title={`Code Interpreter Widget - ${state.ticket_id}`}
          />
        </div>
      )}

      <ConfirmationDialog
        isOpen={confirmDialog.isOpen}
        title="确认操作"
        message={`确定要确认这个 Code Interpreter 状态吗？\n\n确认后将触发 agent 继续执行。\n\n"${state.description || state.ticket_id}"`}
        confirmText="确认"
        cancelText="取消"
        onConfirm={confirmAction}
        onCancel={cancelAction}
        confirmButtonClass="bg-green-600 hover:bg-green-700 focus:ring-green-500"
      />
    </div>
  );
}
