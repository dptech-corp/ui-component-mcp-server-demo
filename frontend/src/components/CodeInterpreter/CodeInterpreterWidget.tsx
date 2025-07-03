import { CodeInterpreterState } from '@/types/code_interpreter';

interface CodeInterpreterWidgetProps {
  state: CodeInterpreterState;
  onBack: () => void;
  onUpdateState: (id: string, updates: Partial<CodeInterpreterState>) => Promise<void>;
}

export function CodeInterpreterWidget({ state, onBack, onUpdateState }: CodeInterpreterWidgetProps) {
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
      
      {state.status !== 'approved' && (
        <div className="flex justify-end">
          <button
            onClick={() => onUpdateState(state.id, { status: 'approved' })}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            确认
          </button>
        </div>
      )}
      
      {state.widget_url && (
        <div className="border rounded-lg overflow-hidden" style={{ height: '500px' }}>
          <iframe
            src={state.widget_url}
            className="w-full h-full border-0"
            title={`Code Interpreter Widget - ${state.ticket_id}`}
          />
        </div>
      )}
    </div>
  );
}
