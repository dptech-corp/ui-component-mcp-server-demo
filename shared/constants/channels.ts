/**
 * Redis channel constants
 */

export const REDIS_CHANNELS = {
  PLAN_ACTIONS: 'plan:actions',
  PLAN_EVENTS: 'plan:events',
  COMPONENT_STATE: 'component:state',
} as const;

export const SSE_EVENTS = {
  PLAN_ADDED: 'plan_added',
  PLAN_UPDATED: 'plan_updated',
  PLAN_DELETED: 'plan_deleted',
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
