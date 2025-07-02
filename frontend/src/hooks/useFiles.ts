import { useState, useEffect } from 'react';
import { useSSE } from '@/contexts/SSEContext';
import type { FileItem } from '@/types/file';

export function useFiles() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastEvent } = useSSE();

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/files`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      const hierarchicalFiles = buildFileHierarchy(data);
      setFiles(hierarchicalFiles);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch files');
      console.error('Error fetching files:', err);
    } finally {
      setLoading(false);
    }
  };

  const buildFileHierarchy = (flatFiles: any[]): FileItem[] => {
    const fileMap = new Map<string, FileItem>();
    const rootFiles: FileItem[] = [];

    flatFiles.forEach(file => {
      const fileItem: FileItem = {
        id: file.id,
        name: file.name,
        type: file.type,
        size: file.size,
        modified: file.updated_at,
        path: file.path,
        children: file.type === 'folder' ? [] : undefined,
        expanded: false
      };
      fileMap.set(file.path, fileItem);
    });

    flatFiles.forEach(file => {
      const fileItem = fileMap.get(file.path)!;
      const parentPath = file.path.substring(0, file.path.lastIndexOf('/'));
      
      if (parentPath && fileMap.has(parentPath)) {
        const parent = fileMap.get(parentPath)!;
        if (parent.children) {
          parent.children.push(fileItem);
        }
      } else {
        rootFiles.push(fileItem);
      }
    });

    return rootFiles;
  };

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'file_created':
        case 'file_deleted':
        case 'file_list':
          fetchFiles();
          break;
      }
    }
  }, [lastEvent]);

  useEffect(() => {
    fetchFiles();
  }, []);

  return {
    files,
    loading,
    error,
    refetch: fetchFiles,
  };
}
