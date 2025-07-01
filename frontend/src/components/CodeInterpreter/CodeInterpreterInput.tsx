import { useState } from 'react';

interface CodeInterpreterInputProps {
  onSubmit: (sessionId: string, code: string, description?: string) => Promise<void>;
  disabled?: boolean;
}

export function CodeInterpreterInput({ onSubmit, disabled }: CodeInterpreterInputProps) {
  const [sessionId, setSessionId] = useState('default_session');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim() || !sessionId.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(sessionId.trim(), code.trim(), description.trim() || undefined);
      setCode('');
      setDescription('');
    } catch (error) {
      console.error('Failed to submit code:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-gray-50 rounded-lg">
      <div>
        <label htmlFor="sessionId" className="block text-sm font-medium text-gray-700 mb-1">
          会话 ID
        </label>
        <input
          type="text"
          id="sessionId"
          value={sessionId}
          onChange={(e) => setSessionId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="输入会话 ID"
          disabled={disabled || isSubmitting}
        />
      </div>
      
      <div>
        <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
          代码 *
        </label>
        <textarea
          id="code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="输入要执行的代码..."
          disabled={disabled || isSubmitting}
          required
        />
      </div>
      
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          描述
        </label>
        <input
          type="text"
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="代码描述（可选）"
          disabled={disabled || isSubmitting}
        />
      </div>
      
      <button
        type="submit"
        disabled={!code.trim() || !sessionId.trim() || disabled || isSubmitting}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSubmitting ? '提交中...' : '提交代码'}
      </button>
    </form>
  );
}
