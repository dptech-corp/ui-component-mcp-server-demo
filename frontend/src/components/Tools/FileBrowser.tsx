import { useState } from 'react';
import { Folder, File, FolderOpen, ChevronRight, ChevronDown } from 'lucide-react';
import { FileItem } from '@/types/file';

interface FileBrowserProps {
  disabled?: boolean;
}

const mockFileStructure: FileItem[] = [
  {
    id: '1',
    name: 'src',
    type: 'folder',
    modified: Date.now() - 86400000,
    path: '/src',
    expanded: true,
    children: [
      {
        id: '2',
        name: 'components',
        type: 'folder',
        modified: Date.now() - 3600000,
        path: '/src/components',
        expanded: false,
        children: [
          {
            id: '3',
            name: 'Button.tsx',
            type: 'file',
            size: 2048,
            modified: Date.now() - 1800000,
            path: '/src/components/Button.tsx'
          },
          {
            id: '4',
            name: 'Input.tsx',
            type: 'file',
            size: 1536,
            modified: Date.now() - 3600000,
            path: '/src/components/Input.tsx'
          }
        ]
      },
      {
        id: '5',
        name: 'utils',
        type: 'folder',
        modified: Date.now() - 7200000,
        path: '/src/utils',
        expanded: false,
        children: [
          {
            id: '6',
            name: 'helpers.ts',
            type: 'file',
            size: 1024,
            modified: Date.now() - 7200000,
            path: '/src/utils/helpers.ts'
          }
        ]
      },
      {
        id: '7',
        name: 'App.tsx',
        type: 'file',
        size: 4096,
        modified: Date.now() - 1800000,
        path: '/src/App.tsx'
      },
      {
        id: '8',
        name: 'index.ts',
        type: 'file',
        size: 512,
        modified: Date.now() - 86400000,
        path: '/src/index.ts'
      }
    ]
  },
  {
    id: '9',
    name: 'public',
    type: 'folder',
    modified: Date.now() - 172800000,
    path: '/public',
    expanded: false,
    children: [
      {
        id: '10',
        name: 'index.html',
        type: 'file',
        size: 1024,
        modified: Date.now() - 172800000,
        path: '/public/index.html'
      },
      {
        id: '11',
        name: 'favicon.ico',
        type: 'file',
        size: 256,
        modified: Date.now() - 172800000,
        path: '/public/favicon.ico'
      }
    ]
  },
  {
    id: '12',
    name: 'package.json',
    type: 'file',
    size: 2048,
    modified: Date.now() - 86400000,
    path: '/package.json'
  },
  {
    id: '13',
    name: 'README.md',
    type: 'file',
    size: 3072,
    modified: Date.now() - 259200000,
    path: '/README.md'
  }
];

export function FileBrowser({ disabled }: FileBrowserProps) {
  const [fileStructure, setFileStructure] = useState<FileItem[]>(mockFileStructure);
  const [selectedItem, setSelectedItem] = useState<FileItem | null>(null);

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString();
  };

  const toggleFolder = (itemId: string, items: FileItem[]): FileItem[] => {
    return items.map(item => {
      if (item.id === itemId && item.type === 'folder') {
        return { ...item, expanded: !item.expanded };
      }
      if (item.children) {
        return { ...item, children: toggleFolder(itemId, item.children) };
      }
      return item;
    });
  };

  const handleItemClick = (item: FileItem) => {
    if (disabled) return;
    
    if (item.type === 'folder') {
      setFileStructure(prev => toggleFolder(item.id, prev));
    } else {
      setSelectedItem(item);
    }
  };

  const renderFileItem = (item: FileItem, depth: number = 0) => {
    const isSelected = selectedItem?.id === item.id;
    
    return (
      <div key={item.id}>
        <div
          className={`flex items-center py-2 px-2 hover:bg-gray-100 cursor-pointer ${
            isSelected ? 'bg-blue-50 border-l-2 border-blue-500' : ''
          }`}
          style={{ paddingLeft: `${depth * 20 + 8}px` }}
          onClick={() => handleItemClick(item)}
        >
          <div className="flex items-center flex-1 min-w-0">
            {item.type === 'folder' ? (
              <>
                {item.expanded ? (
                  <ChevronDown className="w-4 h-4 mr-1 text-gray-500" />
                ) : (
                  <ChevronRight className="w-4 h-4 mr-1 text-gray-500" />
                )}
                {item.expanded ? (
                  <FolderOpen className="w-4 h-4 mr-2 text-blue-500" />
                ) : (
                  <Folder className="w-4 h-4 mr-2 text-blue-500" />
                )}
              </>
            ) : (
              <>
                <div className="w-4 h-4 mr-1" />
                <File className="w-4 h-4 mr-2 text-gray-500" />
              </>
            )}
            <span className="text-sm text-gray-900 truncate">{item.name}</span>
          </div>
          
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            {item.type === 'file' && item.size && (
              <span>{formatFileSize(item.size)}</span>
            )}
            <span>{formatTimestamp(item.modified)}</span>
          </div>
        </div>
        
        {item.type === 'folder' && item.expanded && item.children && (
          <div>
            {item.children.map(child => renderFileItem(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
          <h4 className="text-sm font-medium text-gray-700">文件浏览器</h4>
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {fileStructure.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <File className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p>暂无文件</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {fileStructure.map(item => renderFileItem(item))}
            </div>
          )}
        </div>
      </div>

      {selectedItem && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">文件详情</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p><strong>名称:</strong> {selectedItem.name}</p>
                <p><strong>路径:</strong> {selectedItem.path}</p>
                {selectedItem.size && (
                  <p><strong>大小:</strong> {formatFileSize(selectedItem.size)}</p>
                )}
                <p><strong>修改时间:</strong> {formatTimestamp(selectedItem.modified)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-gray-800">文件浏览器提示</h3>
            <div className="mt-2 text-sm text-gray-700">
              <p>
                这是一个模拟的文件浏览器，展示了典型的项目文件结构。
              </p>
              <ul className="mt-2 list-disc list-inside space-y-1">
                <li>点击文件夹可以展开/收起</li>
                <li>点击文件可以查看详细信息</li>
                <li>支持嵌套文件夹结构</li>
                <li>显示文件大小和修改时间</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
