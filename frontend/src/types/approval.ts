export interface Approval {
  id: string;
  session_id: string;
  function_call_id: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: number;
  updated_at: number;
  result?: string;
}

export interface ApprovalRequest {
  session_id: string;
  function_call_id: string;
  description: string;
}

export interface ApprovalResponse {
  id: string;
  status: string;
  result?: string;
}
