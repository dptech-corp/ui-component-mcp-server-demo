'use client'

import { ScrollArea } from '@/components/ui/scroll-area'
import { Wrench } from 'lucide-react'

export function ToolsTab() {
  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-lg font-semibold mb-4">工具集</h3>
      
      <ScrollArea className="flex-1">
        <div className="space-y-3">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <h4 className="font-medium text-gray-900 mb-2">MCP 工具</h4>
            <div className="space-y-1 text-sm text-gray-600">
              <div>• 计划管理工具</div>
              <div>• 终端执行工具</div>
              <div>• 代码解释器</div>
              <div>• 文件操作工具</div>
              <div>• 审批流程工具</div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h4 className="font-medium text-blue-900 mb-2">专家子代理</h4>
            <div className="space-y-1 text-sm text-blue-700">
              <div>• 理论专家</div>
              <div>• 电镜操作专家</div>
              <div>• 表征分析专家</div>
              <div>• 软件工程专家</div>
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
