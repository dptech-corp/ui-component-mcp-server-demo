import { useState } from 'react';
import { TerminalCommand } from '@/types/terminal';

interface UseTerminalReturn {
  terminalCommands: TerminalCommand[];
  addTerminalCommand: (command: TerminalCommand) => void;
  clearTerminalCommands: () => void;
}

export function useTerminal(): UseTerminalReturn {
  const [terminalCommands, setTerminalCommands] = useState<TerminalCommand[]>([]);

  const addTerminalCommand = (command: TerminalCommand) => {
    setTerminalCommands(prev => {
      const exists = prev.some(cmd => 
        cmd.timestamp === command.timestamp && cmd.action === command.action
      );
      if (exists) {
        return prev;
      }
      return [command, ...prev];
    });
  };

  const clearTerminalCommands = () => {
    setTerminalCommands([]);
  };

  return {
    terminalCommands,
    addTerminalCommand,
    clearTerminalCommands,
  };
}
