'use client'

import { ScrollArea } from '@/components/ui/scroll-area'
import { Globe } from 'lucide-react'

export function BrowserTab() {
  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-lg font-semibold mb-4">浏览器</h3>
      
      <ScrollArea className="flex-1">
        <div className="flex flex-col items-center justify-center h-64 text-gray-500">
          <Globe className="w-12 h-12 mb-4" />
          <p>暂无网页内容</p>
          <p className="text-sm mt-2">代理搜索时将显示网页</p>
        </div>
      </ScrollArea>
    </div>
  )
}
