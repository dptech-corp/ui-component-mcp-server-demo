import { useState, useEffect } from 'react';
import { Tools } from '@/components/Tools/Tools';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useSSE, SSEProvider } from '@/contexts/SSEContext';
import { useTerminal } from '@/hooks/useTerminal';
import './App.css';

function AppContent() {
  // hide backlog
  const [activeTab, setActiveTab] = useState<'plan' | 'terminal' | 'approval' | 'code-interpreter' | 'file-browser' | 'microscope-operation'>('plan');
  const { isConnected, lastEvent } = useSSE();
  const { terminalCommands, addTerminalCommand } = useTerminal();

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'component_switch':
          if (lastEvent.data.component) {
            setActiveTab(lastEvent.data.component as 'plan' | 'terminal' | 'approval' | 'code-interpreter' | 'file-browser' | 'microscope-operation');
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
            <div className="px-2 py-4">
              <header className="text-center mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  通用表征代理
                </h1>
                <p className="text-base text-gray-600">
                  具备读算作报能力的智能协作平台，打通多个专业子系统，实现人/代理/工具平等协作
                </p>
              </header>

              <main className="w-full">
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                    协作工具集
                  </h2>
                  <p className="text-gray-600 mb-6">
                    通用表征代理集成了理论专家、电镜操作专家、表征分析专家和软件工程专家等多个子系统，
                    通过 MCP 协议实现智能工具调用，展示完整的协作流程：
                    计划制定 → 专家委托 → 工具执行 → 结果整合 → 进度跟踪
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
                  基于多专家子代理协作的通用表征代理平台 - 人/代理/工具平等协作的智能系统
                </p>
              </footer>
            </div>
          </div>
        </Panel>

        <PanelResizeHandle className="w-2 bg-gray-300 hover:bg-gray-400 transition-colors cursor-col-resize" />

        <Panel defaultSize={40} minSize={20}>
          <div className="h-full p-4">
            <div className="h-full bg-white rounded-lg shadow-md overflow-hidden">
              <iframe
                src="http://localhost:3002/"
                className="w-full h-full border-0"
                title="Chat Interface"
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
