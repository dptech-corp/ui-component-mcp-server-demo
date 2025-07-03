'use client'

import { useSSE } from '@/contexts/sse-context'
import { ScrollArea } from '@/components/ui/scroll-area'

export function PlanTab() {
  const { isConnected, lastEvent } = useSSE()

  return (
    <div className="h-full flex flex-col p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">执行计划</h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-xs text-gray-600">
            {isConnected ? '已连接' : '未连接'}
          </span>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="space-y-3">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h4 className="font-medium text-blue-900 mb-2">当前任务</h4>
            <p className="text-sm text-blue-700">
              等待用户输入任务指令...
            </p>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <h4 className="font-medium text-gray-900 mb-2">执行步骤</h4>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-300" />
                <span>分析任务需求</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-300" />
                <span>制定执行计划</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-300" />
                <span>调用专家子代理</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-300" />
                <span>执行工具操作</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-300" />
                <span>整合结果反馈</span>
              </div>
            </div>
          </div>

          {lastEvent && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <h4 className="font-medium text-green-900 mb-2">最新事件</h4>
              <p className="text-sm text-green-700">
                {lastEvent.event}: {JSON.stringify(lastEvent.data)}
              </p>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
