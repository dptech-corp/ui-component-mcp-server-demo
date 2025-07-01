import { useState, useEffect } from 'react';
import { Tools } from '@/components/Tools/Tools';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useSSE, SSEProvider } from '@/contexts/SSEContext';
import { useTerminal } from '@/hooks/useTerminal';
import './App.css';

function AppContent() {
  const [activeTab, setActiveTab] = useState<'todo' | 'backlog' | 'terminal' | 'approval' | 'code-interpreter'>('todo');
  const { isConnected, lastEvent } = useSSE();
  const { terminalCommands, addTerminalCommand } = useTerminal();

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'component_switch':
          if (lastEvent.data.component) {
            setActiveTab(lastEvent.data.component as 'todo' | 'backlog' | 'terminal' | 'approval' | 'code-interpreter');
          }
          break;
        case 'terminal_command_executed':
          const newCommand = {
            id: `terminal_${lastEvent.data.timestamp}_${lastEvent.data.action}`,
            action: lastEvent.data.action,
            command: lastEvent.data.command,
            output: lastEvent.data.output,
            file: lastEvent.data.file,
            timestamp: lastEvent.data.timestamp || Date.now()
          };
          addTerminalCommand(newCommand);
          break;
      }
    }
  }, [lastEvent, addTerminalCommand]);
  return (
    <div className="h-screen bg-gray-50">
      <PanelGroup direction="horizontal" className="h-full">
        <Panel defaultSize={60} minSize={30}>
          <div className="h-full overflow-auto">
            <div className="container mx-auto px-4 py-8">
              <header className="text-center mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">
                  UI Component MCP Demo
                </h1>
                <p className="text-lg text-gray-600">
                  演示通过 MCP 协议控制前端组件状态的能力
                </p>
              </header>

              <main className="max-w-2xl mx-auto">
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                    工具组件
                  </h2>
                  <p className="text-gray-600 mb-6">
                    这个工具组件包含 Todo、Backlog 和 Terminal 功能，可以通过 MCP 工具进行控制，展示了完整的消息流程：
                    MCP 调用 → Redis 消息 → 后端处理 → SSE 事件 → 前端更新
                  </p>
                  <Tools 
                    activeTab={activeTab}
                    setActiveTab={setActiveTab}
                    terminalCommands={terminalCommands}
                    isConnected={isConnected}
                  />
                </div>
              </main>

              <footer className="text-center mt-12 text-gray-500">
                <p>
                  基于 React + FastAPI + Redis + MCP 的实时组件状态管理演示
                </p>
              </footer>
            </div>
          </div>
        </Panel>

        <PanelResizeHandle className="w-2 bg-gray-300 hover:bg-gray-400 transition-colors cursor-col-resize" />

        <Panel defaultSize={40} minSize={20}>
          <div className="h-full p-4">
            <div className="h-full bg-white rounded-lg shadow-md overflow-hidden">
              <div className="bg-gray-100 px-4 py-2 border-b">
                <h3 className="text-sm font-medium text-gray-700">Dev UI</h3>
              </div>
              <iframe
                src="http://localhost:8002/dev-ui/"
                className="w-full h-full border-0"
                title="Dev UI"
              />
            </div>
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}

function App() {
  return (
    <SSEProvider>
      <AppContent />
    </SSEProvider>
  );
}

export default App;
