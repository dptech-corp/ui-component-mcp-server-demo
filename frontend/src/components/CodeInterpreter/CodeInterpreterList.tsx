import { CodeInterpreterState } from '@/types/code_interpreter';

interface CodeInterpreterListProps {
  states: CodeInterpreterState[];
  loading: boolean;
  error: string | null;
  onSelectState: (state: CodeInterpreterState) => void;
  selectedState: CodeInterpreterState | null;
}

export function CodeInterpreterList({ 
  states, 
  loading, 
  error, 
  onSelectState, 
  selectedState 
}: CodeInterpreterListProps) {
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

  if (loading && states.length === 0) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">加载中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  if (states.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>暂无代码解释器状态</p>
        <p className="text-sm mt-1">使用 MCP 工具创建一个状态开始吧！</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {states.map((state) => (
        <div
          key={state.id}
          onClick={() => onSelectState(state)}
          className={`bg-white border rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
            selectedState?.id === state.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-900">{state.ticket_id}</span>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(state.status)}`}>
              {getStatusText(state.status)}
            </span>
          </div>
          
          {state.description && (
            <p className="text-sm text-gray-600 mb-2">{state.description}</p>
          )}
          
          <div className="text-xs text-gray-500">
            创建时间: {formatTimestamp(state.created_at)}
          </div>
        </div>
      ))}
    </div>
  );
}
