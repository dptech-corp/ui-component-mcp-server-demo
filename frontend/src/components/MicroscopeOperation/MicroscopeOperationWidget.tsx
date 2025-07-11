import { MicroscopeOperationWorkflow } from '@/types/microscope_operation';

interface MicroscopeOperationWidgetProps {
  workflow: MicroscopeOperationWorkflow;
  onBack: () => void;
}

export function MicroscopeOperationWidget({ workflow, onBack }: MicroscopeOperationWidgetProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          ← 返回列表
        </button>
        <h3 className="text-lg font-medium text-gray-900">{workflow.name}</h3>
      </div>

      {workflow.description && (
        <p className="text-sm text-gray-600">{workflow.description}</p>
      )}

      <div className="text-xs text-gray-500">
        工作流 ID: {workflow.workflow_id} | 状态: {workflow.status}
      </div>

      {workflow.widget_url && (
        <div className="border border-gray-200 rounded-lg overflow-hidden" style={{ height: 'calc(100vh - 300px)' }}>
          <iframe
            src={workflow.widget_url}
            className="w-full h-full"
            title={`Microscope Operation - ${workflow.name}`}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
          />
        </div>
      )}
    </div>
  );
}
