export interface Plan {
  id: string;
  session_id: string;
  title: string;
  description?: string;
  status: 'active' | 'completed' | 'archived';
  created_at: number;
  updated_at: number;
}

export interface TodoItem {
  id: string;
  plan_id?: string;
  title: string;
  description?: string;
  completed: boolean;
  session_id?: string;
  created_at: number;
  updated_at: number;
}

export interface PlanItem {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  session_id?: string;
  created_at: number;
  updated_at: number;
}

export interface PlanState {
  items: PlanItem[];
  loading: boolean;
  error?: string;
}

export interface PlanCreateRequest {
  session_id: string;
  title: string;
  description?: string;
}

export interface PlanUpdateRequest {
  title?: string;
  description?: string;
  completed?: boolean;
  session_id?: string;
}

export interface BacklogItem {
  id: string;
  title: string;
  description?: string;
  created_at: number;
  updated_at: number;
}

export interface BacklogCreateRequest {
  title: string;
  description?: string;
}
