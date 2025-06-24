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
    setTerminalCommands(prev => [command, ...prev]);
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
