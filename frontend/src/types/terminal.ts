export interface TerminalCommand {
  id: string;
  action: string;
  command: string;
  output: string;
  file?: string;
  timestamp: number;
}
