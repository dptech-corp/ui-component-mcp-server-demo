/**
 * Shared message types for communication between components
 */

export interface BaseMessage {
  id: string;
  type: string;
  timestamp: number;
  source: 'mcp' | 'backend' | 'frontend';
  target: string;
  component?: 'todo' | 'backlog' | 'terminal' | 'approval';
  payload: any;
}

export interface TodoActionMessage extends BaseMessage {
  type: 'todo_action';
  target: 'todo_component';
  payload: {
    action: 'add' | 'delete' | 'update' | 'toggle';
    todoId?: string;
    data?: {
      title?: string;
      description?: string;
      completed?: boolean;
    };
  };
}

export interface ComponentStateMessage extends BaseMessage {
  type: 'component_state';
  payload: {
    componentId: string;
    state: any;
  };
}

export interface ApprovalRequestMessage extends BaseMessage {
  type: 'approval_request';
  target: 'approval_component';
  payload: {
    session_id: string;
    function_call_id: string;
    description: string;
  };
}

export type MessageType = 'todo_action' | 'backlog_action' | 'terminal_action' | 'approval_request';

export interface SSEEvent {
  event: string;
  data: {
    messageId?: string;
    type: string;
    payload: any;
  };
}
