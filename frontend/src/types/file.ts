export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size?: number;
  modified: number;
  path: string;
  children?: FileItem[];
  expanded?: boolean;
}

export interface FileBrowserState {
  items: FileItem[];
  selectedItem?: FileItem;
  loading: boolean;
  error?: string;
}
