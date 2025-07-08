import React from 'react';
import { TodoItem } from '../../types/plan';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { Trash2, ArrowLeft } from 'lucide-react';

interface TodoListProps {
  todos: TodoItem[];
  loading: boolean;
  error: string | null;
  onToggleTodo: (id: string) => void;
  onDeleteTodo: (id: string) => void;
  onBack: () => void;
  planTitle: string;
}

export function TodoList({ 
  todos, 
  loading, 
  error, 
  onToggleTodo, 
  onDeleteTodo,
  onBack,
  planTitle
}: TodoListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading todos...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="text-red-800">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={onBack}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Plans
        </Button>
        <h2 className="text-lg font-semibold text-gray-900">
          {planTitle} - Todos ({todos.length})
        </h2>
      </div>
      
      {todos.length === 0 ? (
        <div className="p-8 text-center">
          <div className="text-gray-500 mb-2">No todos in this plan</div>
          <div className="text-sm text-gray-400">
            Todos will appear here when created through MCP tools.
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {todos.map((todo) => (
            <div
              key={todo.id}
              className={`bg-white border rounded-lg p-4 ${
                todo.completed ? 'bg-gray-50' : 'bg-white'
              }`}
            >
              <div className="flex items-start gap-3">
                <Checkbox
                  checked={todo.completed}
                  onCheckedChange={() => onToggleTodo(todo.id)}
                  className="mt-1"
                />
                
                <div className="flex-1 min-w-0">
                  <h4 className={`font-medium ${
                    todo.completed ? 'line-through text-gray-500' : 'text-gray-900'
                  }`}>
                    {todo.title}
                  </h4>
                  
                  {todo.description && (
                    <p className={`text-sm mt-1 ${
                      todo.completed ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {todo.description}
                    </p>
                  )}
                  
                  <div className="text-xs text-gray-500 mt-2">
                    Created: {new Date(todo.created_at).toLocaleString()}
                  </div>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDeleteTodo(todo.id)}
                  className="h-6 w-6 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
