export interface Approval {
  id: string;
  session_id: string;
  function_call_id: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: number;
  updated_at: number;
}

export interface ApprovalState {
  approvals: Approval[];
  loading: boolean;
  error: string | null;
}

export interface ApprovalResponse {
  success: boolean;
  message: string;
  approval?: Approval;
}
