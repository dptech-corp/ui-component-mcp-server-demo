export interface TodoItem {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: number;
  updated_at: number;
}

export interface TodoState {
  items: TodoItem[];
  loading: boolean;
  error?: string;
}

export interface TodoCreateRequest {
  title: string;
  description?: string;
}

export interface TodoUpdateRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}
