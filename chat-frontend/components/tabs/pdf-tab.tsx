'use client'

import { ScrollArea } from '@/components/ui/scroll-area'
import { FileText } from 'lucide-react'

export function PDFTab() {
  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-lg font-semibold mb-4">PDF 查看器</h3>
      
      <ScrollArea className="flex-1">
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <FileText className="w-12 h-12 mb-4" />
          <p>暂无 PDF 文档</p>
          <p className="text-sm mt-2">文档将在代理处理时显示</p>
        </div>
      </ScrollArea>
    </div>
  )
}
