'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PlanTab } from './plan-tab'
import { TerminalTab } from './terminal-tab'
import { PDFTab } from './pdf-tab'
import { BrowserTab } from './browser-tab'
import { FileTab } from './file-tab'
import { ToolsTab } from './tools-tab'
import { NotebookTab } from './notebook-tab'
import { Star, Terminal, FileText, Globe, Folder, Wrench, BookOpen } from 'lucide-react'

export function TabLayout() {
  const [activeTab, setActiveTab] = useState('plan')

  return (
    <div className="h-full flex flex-col">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
        <TabsList className="grid w-full grid-cols-7 gap-1 p-1">
          <TabsTrigger value="plan" className="flex items-center gap-1 text-xs">
            <Star className="w-3 h-3" />
            Plan
          </TabsTrigger>
          <TabsTrigger value="terminal" className="flex items-center gap-1 text-xs">
            <Terminal className="w-3 h-3" />
            终端
          </TabsTrigger>
          <TabsTrigger value="pdf" className="flex items-center gap-1 text-xs">
            <FileText className="w-3 h-3" />
            PDF
          </TabsTrigger>
          <TabsTrigger value="browser" className="flex items-center gap-1 text-xs">
            <Globe className="w-3 h-3" />
            浏览器
          </TabsTrigger>
          <TabsTrigger value="file" className="flex items-center gap-1 text-xs">
            <Folder className="w-3 h-3" />
            文件
          </TabsTrigger>
          <TabsTrigger value="tools" className="flex items-center gap-1 text-xs">
            <Wrench className="w-3 h-3" />
            工具
          </TabsTrigger>
          <TabsTrigger value="notebook" className="flex items-center gap-1 text-xs">
            <BookOpen className="w-3 h-3" />
            笔记本
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-hidden">
          <TabsContent value="plan" className="h-full">
            <PlanTab />
          </TabsContent>
          <TabsContent value="terminal" className="h-full">
            <TerminalTab />
          </TabsContent>
          <TabsContent value="pdf" className="h-full">
            <PDFTab />
          </TabsContent>
          <TabsContent value="browser" className="h-full">
            <BrowserTab />
          </TabsContent>
          <TabsContent value="file" className="h-full">
            <FileTab />
          </TabsContent>
          <TabsContent value="tools" className="h-full">
            <ToolsTab />
          </TabsContent>
          <TabsContent value="notebook" className="h-full">
            <NotebookTab />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  )
}
