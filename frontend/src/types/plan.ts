export interface PlanItem {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: number;
  updated_at: number;
}

export interface PlanState {
  items: PlanItem[];
  loading: boolean;
  error?: string;
}

export interface PlanCreateRequest {
  title: string;
  description?: string;
}

export interface PlanUpdateRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}
