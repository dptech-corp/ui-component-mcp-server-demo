import React, { useState, useEffect } from 'react';
import { TodoItem } from '@/types/todo';
import { TodoInput } from './TodoInput';
import { TodoItemComponent } from './TodoItem';
import { TodoStats } from './TodoStats';
import { useSSE } from '@/hooks/useSSE';
import { useTodos } from '@/hooks/useTodos';

export function TodoList() {
  const { todos, loading, error, addTodo, updateTodo, deleteTodo, toggleTodo, fetchTodos } = useTodos();
  const { isConnected, lastEvent } = useSSE();

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'todo_added':
          break;
        case 'todo_updated':
          break;
        case 'todo_deleted':
          break;
      }
    }
  }, [lastEvent]);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const handleAddTodo = async (title: string, description?: string) => {
    await addTodo(title, description);
  };

  const handleUpdateTodo = async (id: string, updates: Partial<TodoItem>) => {
    await updateTodo(id, updates);
  };

  const handleDeleteTodo = async (id: string) => {
    await deleteTodo(id);
  };

  const handleToggleTodo = async (id: string) => {
    await toggleTodo(id);
  };

  if (loading && todos.length === 0) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">加载中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 连接状态指示器 */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Todo 列表</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600">
            {isConnected ? '实时连接已建立' : '连接已断开'}
          </span>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">错误</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 添加新 Todo */}
      <TodoInput onAdd={handleAddTodo} disabled={loading} />

      {/* Todo 统计 */}
      <TodoStats todos={todos} />

      {/* Todo 列表 */}
      <div className="space-y-2">
        {todos.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>暂无 Todo 项目</p>
            <p className="text-sm mt-1">添加一个新的 Todo 开始吧！</p>
          </div>
        ) : (
          todos.map((todo) => (
            <TodoItemComponent
              key={todo.id}
              todo={todo}
              onUpdate={handleUpdateTodo}
              onDelete={handleDeleteTodo}
              onToggle={handleToggleTodo}
              disabled={loading}
            />
          ))
        )}
      </div>

      {/* MCP 提示 */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">MCP 控制提示</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                这个 Todo 列表可以通过 MCP 工具进行控制。尝试使用以下 MCP 命令：
              </p>
              <ul className="mt-2 list-disc list-inside space-y-1">
                <li><code>add_todo("学习 MCP", "了解 Model Context Protocol")</code></li>
                <li><code>toggle_todo("todo_id")</code></li>
                <li><code>delete_todo("todo_id")</code></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
