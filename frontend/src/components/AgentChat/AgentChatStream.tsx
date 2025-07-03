import React, { useEffect, useRef } from 'react';
import { AgentMessage } from './AgentMessage';
import { AgentInput } from './AgentInput';
import { useAgentStream } from '../../hooks/useAgentStream';

export const AgentChatStream: React.FC = () => {
  const { messages, loading, error, sendMessage } = useAgentStream();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>开始对话...</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <AgentMessage key={message.id} message={message} />
            ))}
            {loading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                    <span className="text-sm">正在思考...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mx-4 mb-2 rounded">
          <p className="text-sm">{error}</p>
        </div>
      )}
      
      <AgentInput onSendMessage={sendMessage} disabled={loading} />
    </div>
  );
};
