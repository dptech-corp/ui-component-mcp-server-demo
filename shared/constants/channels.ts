/**
 * Redis channel constants
 */

export const REDIS_CHANNELS = {
  TODO_ACTIONS: 'todo:actions',
  TODO_EVENTS: 'todo:events',
  COMPONENT_STATE: 'component:state',
} as const;

export const SSE_EVENTS = {
  TODO_ADDED: 'todo_added',
  TODO_UPDATED: 'todo_updated',
  TODO_DELETED: 'todo_deleted',
  BACKLOG_DELETED: 'backlog_deleted',
  APPROVAL_DELETED: 'approval_deleted',
  CODE_INTERPRETER_STATE_DELETED: 'code_interpreter_state_deleted',
  COMPONENT_STATE_CHANGED: 'component_state_changed',
  COMPONENT_SWITCH: 'component_switch',
  TERMINAL_COMMAND_EXECUTED: 'terminal_command_executed',
  CODE_INTERPRETER_STATE_CREATED: 'code_interpreter_state_created',
  CODE_INTERPRETER_STATE_UPDATED: 'code_interpreter_state_updated',
  CODE_INTERPRETER_STATE_RETRIEVED: 'code_interpreter_state_retrieved',
  HEARTBEAT: 'heartbeat',
} as const;
