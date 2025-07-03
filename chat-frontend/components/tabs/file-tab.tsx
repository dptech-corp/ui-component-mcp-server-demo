'use client'

import { ScrollArea } from '@/components/ui/scroll-area'
import { Folder } from 'lucide-react'

export function FileTab() {
  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-lg font-semibold mb-4">文件管理</h3>
      
      <ScrollArea className="flex-1">
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <Folder className="w-12 h-12 mb-4" />
          <p>暂无文件</p>
          <p className="text-sm mt-2">代理操作的文件将在此显示</p>
        </div>
      </ScrollArea>
    </div>
  )
}
