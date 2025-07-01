export interface CodeInterpreterState {
  id: string;
  ticket_id: string;
  code: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  result?: string;
  widget_url?: string;
  created_at: number;
  updated_at: number;
}

export interface CodeInterpreterCreateRequest {
  code: string;
  description?: string;
}

export interface CodeInterpreterUpdateRequest {
  status?: 'pending' | 'running' | 'completed' | 'error';
  result?: string;
}

export interface CodeInterpreterHookReturn {
  states: CodeInterpreterState[];
  loading: boolean;
  error: string | null;
  selectedState: CodeInterpreterState | null;
  createState: (code: string, description?: string) => Promise<void>;
  updateState: (id: string, updates: Partial<CodeInterpreterState>) => Promise<void>;
  getState: (id: string) => Promise<void>;
  fetchStates: () => Promise<void>;
  selectState: (state: CodeInterpreterState | null) => void;
}
