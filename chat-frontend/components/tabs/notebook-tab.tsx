'use client'

import { ScrollArea } from '@/components/ui/scroll-area'
import { BookOpen } from 'lucide-react'

export function NotebookTab() {
  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-lg font-semibold mb-4">笔记本</h3>
      
      <ScrollArea className="flex-1">
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <BookOpen className="w-12 h-12 mb-4" />
          <p>暂无笔记本</p>
          <p className="text-sm mt-2">代码执行和分析结果将在此显示</p>
        </div>
      </ScrollArea>
    </div>
  )
}
