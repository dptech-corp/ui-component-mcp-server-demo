export interface AgentMessage {
  id: string;
  text: string;
  role: 'user' | 'agent';
  timestamp: number;
}

export interface AgentMessageRequest {
  message: string;
  sessionId?: string;
}

export interface AgentResponse {
  success: boolean;
  response: any;
  error?: string;
}

export interface AgentStreamRequest {
  message: string;
  sessionId?: string;
}

export interface AgentStreamResponse {
  text?: string;
  done?: boolean;
  error?: string;
}
