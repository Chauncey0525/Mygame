'use client';

import { BattleLog as BattleLogType } from '@/types/game';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface BattleLogProps {
  logs: BattleLogType[];
}

const LOG_TYPE_STYLES: Record<string, string> = {
  info: 'text-slate-200 bg-slate-700/80',
  damage: 'text-red-400 bg-red-900/30',
  heal: 'text-green-400 bg-green-900/30',
  effect: 'text-purple-400 bg-purple-900/30',
  critical: 'text-yellow-400 font-bold bg-yellow-900/30',
  miss: 'text-slate-400 italic bg-slate-700/50',
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
    <div className="rounded-xl border-2 border-slate-600 bg-slate-800 p-3 shadow-lg">
      <h3 className="mb-2 text-sm font-bold text-white flex items-center gap-2">
        📋 战斗日志
      </h3>
      <ScrollArea className="h-36">
        <div className="space-y-1">
          {logs.map((log, index) => (
            <div
              key={index}
              className={cn(
                'flex items-start gap-2 rounded-lg px-3 py-1.5 text-sm transition-all',
                LOG_TYPE_STYLES[log.type],
                log.type === 'critical' && 'animate-pulse'
              )}
            >
              <span className="flex-shrink-0">{LOG_TYPE_ICONS[log.type]}</span>
              <span className="font-medium">{log.message}</span>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
