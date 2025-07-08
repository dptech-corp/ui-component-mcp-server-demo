import React from 'react';
import { AgentChatStream } from './components/AgentChat';

const ChatApp: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-white">
      <div className="flex-1 overflow-hidden">
        <AgentChatStream />
      </div>
    </div>
  );
};

export default ChatApp;
