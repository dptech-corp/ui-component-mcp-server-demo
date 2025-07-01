import { CodeInterpreterState } from '@/types/code_interpreter';

interface CodeInterpreterItemProps {
  state: CodeInterpreterState;
  onUpdate?: (id: string, updates: Partial<CodeInterpreterState>) => Promise<void>;
  disabled?: boolean;
}

export function CodeInterpreterItem({ state, onUpdate, disabled }: CodeInterpreterItemProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '等待中';
      case 'running':
        return '运行中';
      case 'completed':
        return '已完成';
      case 'error':
        return '错误';
      default:
        return status;
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString('zh-CN');
  };

  const handleOpenWidget = () => {
    if (state.widget_url) {
      window.open(state.widget_url, '_blank');
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-medium text-gray-900">
              {state.ticket_id}
            </span>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(state.status)}`}>
              {getStatusText(state.status)}
            </span>
          </div>
          
          {state.description && (
            <p className="text-sm text-gray-600 mb-2">{state.description}</p>
          )}
          
          <div className="bg-gray-50 rounded p-3 mb-3">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
              {state.code}
            </pre>
          </div>
          
          {state.result && (
            <div className="bg-green-50 border border-green-200 rounded p-3 mb-3">
              <h4 className="text-sm font-medium text-green-800 mb-1">执行结果：</h4>
              <pre className="text-sm text-green-700 whitespace-pre-wrap font-mono">
                {state.result}
              </pre>
            </div>
          )}
          
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>会话: {state.session_id}</span>
            <span>创建时间: {formatTimestamp(state.created_at)}</span>
          </div>
        </div>
      </div>
      
      <div className="flex space-x-2">
        {state.widget_url && state.status === 'pending' && (
          <button
            onClick={handleOpenWidget}
            disabled={disabled}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            打开执行界面
          </button>
        )}
        
        {state.status === 'pending' && onUpdate && (
          <button
            onClick={() => onUpdate(state.id, { status: 'running' })}
            disabled={disabled}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            标记为运行中
          </button>
        )}
      </div>
    </div>
  );
}
