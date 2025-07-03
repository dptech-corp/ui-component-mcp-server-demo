'use client'

import { ScrollArea } from '@/components/ui/scroll-area'

export function TerminalTab() {
  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-lg font-semibold mb-4">终端</h3>
      
      <ScrollArea className="flex-1">
        <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm">
          <div className="mb-2">$ 等待命令执行...</div>
          <div className="opacity-60">
            终端将显示代理执行的命令和输出结果
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
