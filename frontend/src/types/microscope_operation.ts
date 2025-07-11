export interface MicroscopeOperationWorkflow {
  id: string;
  workflow_id: string;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  widget_url?: string;
  created_at: number;
  updated_at: number;
}

export interface MicroscopeOperationCreateRequest {
  name: string;
  description?: string;
}

export interface MicroscopeOperationUpdateRequest {
  status?: 'pending' | 'running' | 'completed' | 'error';
}

export interface MicroscopeOperationHookReturn {
  workflows: MicroscopeOperationWorkflow[];
  loading: boolean;
  error: string | null;
  selectedWorkflow: MicroscopeOperationWorkflow | null;
  createWorkflow: (name: string, description?: string) => Promise<void>;
  updateWorkflow: (id: string, updates: Partial<MicroscopeOperationWorkflow>) => Promise<void>;
  deleteWorkflow: (id: string) => Promise<void>;
  fetchWorkflows: () => Promise<void>;
  selectWorkflow: (workflow: MicroscopeOperationWorkflow | null) => void;
}
