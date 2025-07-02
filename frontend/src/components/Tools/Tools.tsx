import { useEffect } from 'react';
import { PlanItem } from '@/types/plan';
import { TerminalCommand } from '@/types/terminal';
import { PlanInput } from './PlanInput';
import { PlanItemComponent } from './PlanItem';
import { PlanStats } from './PlanStats';
import { BacklogInput } from './BacklogInput';
import { BacklogItemComponent } from './BacklogItem';
import { TerminalOutput } from './TerminalOutput';
import { ApprovalList } from '../Approval/ApprovalList';
import { CodeInterpreterList } from '../CodeInterpreter/CodeInterpreterList';
import { CodeInterpreterWidget } from '../CodeInterpreter/CodeInterpreterWidget';
import { usePlans } from '@/hooks/usePlans';
import { useApprovals } from '@/hooks/useApprovals';
import { useCodeInterpreter } from '@/hooks/useCodeInterpreter';
import { useSSE } from '@/contexts/SSEContext';
import { FileBrowser } from './FileBrowser';

interface ToolsProps {
  activeTab: 'plan' | 'backlog' | 'terminal' | 'approval' | 'code-interpreter' | 'file-browser';
  setActiveTab: (tab: 'plan' | 'backlog' | 'terminal' | 'approval' | 'code-interpreter' | 'file-browser') => void;
  terminalCommands: TerminalCommand[];
  isConnected: boolean;
}

export function Tools({ activeTab, setActiveTab, terminalCommands, isConnected }: ToolsProps) {
  const { 
    plans, 
    backlogItems, 
    loading, 
    error, 
    addPlan, 
    updatePlan, 
    deletePlan, 
    togglePlan, 
    fetchPlans,
    addBacklogItem,
    updateBacklogItem,
    deleteBacklogItem,
    moveToTodo
  } = usePlans();
  const { lastEvent } = useSSE();
  const { approvals, loading: approvalsLoading, error: approvalsError, approveRequest, rejectRequest, deleteApproval, refetch: refetchApprovals } = useApprovals();
  const { states: codeInterpreterStates, selectedState, loading: codeInterpreterLoading, error: codeInterpreterError, selectState, deleteState } = useCodeInterpreter();

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'plan_added':
          fetchPlans();
          setActiveTab('plan');
          break;
        case 'plan_updated':
          fetchPlans();
          setActiveTab('plan');
          break;
        case 'plan_deleted':
          fetchPlans();
          setActiveTab('plan');
          break;
        case 'approval_request':
          if (lastEvent.data?.approval) {
            refetchApprovals();
            setActiveTab('approval');
          }
          break;
        case 'approval_updated':
          if (lastEvent.data?.approval) {
            refetchApprovals();
          }
          break;
        case 'code_interpreter_state_created':
          if (lastEvent.data?.state) {
            setActiveTab('code-interpreter');
          }
          break;
      }
    }
  }, [lastEvent, setActiveTab]);

  useEffect(() => {
    fetchPlans();
  }, [fetchPlans]);

  const handleAddPlan = async (title: string, description?: string) => {
    await addPlan(title, description);
  };

  const handleUpdatePlan = async (id: string, updates: Partial<PlanItem>) => {
    await updatePlan(id, updates);
  };

  const handleDeletePlan = async (id: string) => {
    await deletePlan(id);
  };

  const handleTogglePlan = async (id: string) => {
    await togglePlan(id);
  };

  const handleAddBacklogItem = (title: string, description?: string) => {
    addBacklogItem(title, description);
  };

  const handleUpdateBacklogItem = (id: string, updates: Partial<any>) => {
    updateBacklogItem(id, updates);
  };

  const handleDeleteBacklogItem = (id: string) => {
    deleteBacklogItem(id);
  };

  const handleMoveToTodo = async (id: string) => {
    await moveToTodo(id);
  };

  const handleSummarizePlan = async (plan: PlanItem) => {
    try {
      const message = `分析 ${plan.title} 任务花了多久完成`;
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/agent/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          sessionId: null
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message to agent');
      }

      const result = await response.json();
      console.log('Agent response:', result);
      
      alert(`Agent 响应: ${JSON.stringify(result.response)}`);
    } catch (error) {
      console.error('Error calling agent:', error);
      alert('调用 Agent 失败，请稍后重试');
    }
  };

  if (loading && plans.length === 0) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">加载中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 连接状态指示器 */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Plan 列表</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600">
            {isConnected ? '实时连接已建立' : '连接已断开'}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('plan')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
            activeTab === 'plan'
              ? 'bg-white border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Plan
        </button>
        <button
          onClick={() => setActiveTab('backlog')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
            activeTab === 'backlog'
              ? 'bg-white border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Backlog
        </button>
        <button
          onClick={() => setActiveTab('terminal')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
            activeTab === 'terminal'
              ? 'bg-white border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Terminal
        </button>
        <button
          onClick={() => setActiveTab('approval')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
            activeTab === 'approval'
              ? 'bg-white border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Approval
        </button>
        <button
          onClick={() => setActiveTab('code-interpreter')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
            activeTab === 'code-interpreter'
              ? 'bg-white border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Code Interpreter
        </button>
        <button
          onClick={() => setActiveTab('file-browser')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
            activeTab === 'file-browser'
              ? 'bg-white border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          File Browser
        </button>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">错误</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Content */}
      {activeTab === 'plan' ? (
        <>
          {/* 添加新 Plan */}
          <PlanInput onAdd={handleAddPlan} disabled={loading} />

          {/* Plan 统计 */}
          <PlanStats plans={plans} />

          {/* Plan 列表 */}
          <div className="space-y-2">
            {plans.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>暂无 Plan 项目</p>
                <p className="text-sm mt-1">添加一个新的 Plan 开始吧！</p>
              </div>
            ) : (
              plans.map((plan) => (
                <PlanItemComponent
                  key={plan.id}
                  plan={plan}
                  onUpdate={handleUpdatePlan}
                  onDelete={handleDeletePlan}
                  onToggle={handleTogglePlan}
                  onSummarize={handleSummarizePlan}
                  disabled={loading}
                />
              ))
            )}
          </div>
        </>
      ): activeTab === 'backlog' ? (
        <>
          {/* 添加新 Backlog */}
          <BacklogInput onAdd={handleAddBacklogItem} disabled={loading} />

          {/* Backlog 列表 */}
          <div className="space-y-2">
            {backlogItems.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>暂无 Backlog 项目</p>
                <p className="text-sm mt-1">添加一个新的 Backlog 开始吧！</p>
              </div>
            ) : (
              backlogItems.map((item) => (
                <BacklogItemComponent
                  key={item.id}
                  item={item}
                  onUpdate={handleUpdateBacklogItem}
                  onDelete={handleDeleteBacklogItem}
                  onAddToTodo={handleMoveToTodo}
                  disabled={loading}
                />
              ))
            )}
          </div>
        </>
      ) : activeTab === 'terminal' ? (
        <>
          <TerminalOutput commands={terminalCommands} disabled={loading} />
        </>
      ) : activeTab === 'code-interpreter' ? (
        <>
          {selectedState ? (
            <CodeInterpreterWidget 
              state={selectedState}
              onBack={() => selectState(null)}
            />
          ) : (
            <CodeInterpreterList
              states={codeInterpreterStates}
              loading={codeInterpreterLoading}
              error={codeInterpreterError}
              onSelectState={selectState}
              onDeleteState={deleteState}
              selectedState={selectedState}
            />
          )}
        </>
      ) : activeTab === 'file-browser' ? (
        <>
          <FileBrowser disabled={loading || !isConnected} />
        </>
      ) : (
        <>
          <ApprovalList 
            approvals={approvals}
            loading={approvalsLoading}
            error={approvalsError}
            onApprove={approveRequest}
            onReject={rejectRequest}
            onDelete={deleteApproval}
          />
        </>
      )}

      {activeTab === 'plan' && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">MCP 控制提示</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>
                  这个 Plan 列表可以通过 MCP 工具进行控制。尝试使用以下 MCP 命令：
                </p>
                <ul className="mt-2 list-disc list-inside space-y-1">
                  <li><code>add_plan("学习 MCP", "了解 Model Context Protocol")</code></li>
                  <li><code>toggle_plan("plan_id")</code></li>
                  <li><code>delete_plan("plan_id")</code></li>
                  <li><code>update_plan("plan_id", "新的标题", "新的描述")</code></li>
                  <li><code>list_plan()</code></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'terminal' && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Terminal MCP 工具提示</h3>
              <div className="mt-2 text-sm text-green-700">
                <p>
                  这个 Terminal 组件可以通过 MCP 工具执行 Linux 命令。尝试使用以下 MCP 命令：
                </p>
                <ul className="mt-2 list-disc list-inside space-y-1">
                  <li><code>ls()</code> - 列出当前目录文件</li>
                  <li><code>cat_run_sh()</code> - 查看 run.sh 文件内容</li>
                  <li><code>bash_run_sh()</code> - 执行 run.sh 脚本</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'code-interpreter' && (
        <div className="bg-purple-50 border border-purple-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-purple-800">Code Interpreter MCP 工具提示</h3>
              <div className="mt-2 text-sm text-purple-700">
                <p>
                  这个 Code Interpreter 组件可以通过 MCP 工具执行代码。尝试使用以下 MCP 命令：
                </p>
                <ul className="mt-2 list-disc list-inside space-y-1">
                  <li><code>create_python_notebook("print('Hello World')", "测试代码")</code></li>
                  <li><code>get_notebook_state("state_id")</code></li>
                </ul>
                <p className="mt-2">
                  创建状态后，点击列表中的条目查看 widget iframe 来实际执行代码。
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
