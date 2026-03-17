'use client';

import { BattleLog as BattleLogType } from '@/types/game';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface BattleLogProps {
  logs: BattleLogType[];
}

const LOG_TYPE_STYLES: Record<string, string> = {
  info: 'text-slate-400',
  damage: 'text-red-400',
  heal: 'text-green-400',
  effect: 'text-purple-400',
  critical: 'text-yellow-400 font-bold',
  miss: 'text-slate-500 italic',
};

const LOG_TYPE_ICONS: Record<string, string> = {
  info: '📜',
  damage: '💥',
  heal: '💚',
  effect: '✨',
  critical: '⚡',
  miss: '💨',
};

export function BattleLogDisplay({ logs }: BattleLogProps) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900/80 p-3">
      <h3 className="mb-2 text-sm font-bold text-slate-300">战斗日志</h3>
      <ScrollArea className="h-40">
        <div className="space-y-1">
          {logs.map((log, index) => (
            <div
              key={index}
              className={cn(
                'flex items-start gap-2 rounded px-2 py-1 text-sm transition-all',
                LOG_TYPE_STYLES[log.type],
                log.type === 'critical' && 'animate-pulse bg-yellow-900/20'
              )}
            >
              <span className="flex-shrink-0">{LOG_TYPE_ICONS[log.type]}</span>
              <span>{log.message}</span>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
