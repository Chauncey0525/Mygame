'use client';

import { Skill, ELEMENT_COLORS, ELEMENT_NAMES } from '@/types/game';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface SkillButtonProps {
  skill: Skill;
  disabled?: boolean;
  onClick?: () => void;
  isActive?: boolean;
}

const SKILL_TYPE_ICONS: Record<string, string> = {
  attack: '⚔️',
  defense: '🛡️',
  buff: '⬆️',
  debuff: '⬇️',
  heal: '💚',
  special: '✨',
};

const SKILL_TYPE_NAMES: Record<string, string> = {
  attack: '攻击',
  defense: '防御',
  buff: '增益',
  debuff: '减益',
  heal: '治疗',
  special: '必杀',
};

export function SkillButton({ skill, disabled = false, onClick, isActive = false }: SkillButtonProps) {
  const isAvailable = skill.pp > 0 && !disabled;
  const ppPercent = (skill.pp / skill.maxPp) * 100;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="outline"
            disabled={!isAvailable}
            onClick={onClick}
            className={cn(
              'relative h-auto w-full flex-col items-start gap-1 p-3 transition-all',
              isActive && 'ring-2 ring-yellow-400',
              !isAvailable && 'opacity-50',
              skill.type === 'special' && 'border-yellow-500 bg-yellow-900/20 hover:bg-yellow-900/40'
            )}
            style={{
              borderColor: isAvailable ? ELEMENT_COLORS[skill.element] : undefined,
            }}
          >
            {/* 技能名称行 */}
            <div className="flex w-full items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">{SKILL_TYPE_ICONS[skill.type]}</span>
                <span className="font-bold">{skill.name}</span>
              </div>
              <Badge
                variant="outline"
                className="text-xs"
                style={{
                  borderColor: ELEMENT_COLORS[skill.element],
                  color: ELEMENT_COLORS[skill.element],
                }}
              >
                {ELEMENT_NAMES[skill.element]}
              </Badge>
            </div>

            {/* 技能信息行 */}
            <div className="flex w-full items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-2">
                {skill.power > 0 && <span className="text-orange-400">威力: {skill.power}</span>}
                <span>命中: {skill.accuracy}%</span>
              </div>
              <div className="flex items-center gap-1">
                <span className={cn(skill.pp <= 0 ? 'text-red-400' : skill.pp <= 2 ? 'text-yellow-400' : 'text-blue-400')}>
                  PP: {skill.pp}/{skill.maxPp}
                </span>
              </div>
            </div>

            {/* PP条 */}
            <div className="h-1 w-full overflow-hidden rounded-full bg-slate-700">
              <div
                className={cn(
                  'h-full transition-all',
                  ppPercent > 50 ? 'bg-blue-500' : ppPercent > 0 ? 'bg-yellow-500' : 'bg-red-500'
                )}
                style={{ width: `${ppPercent}%` }}
              />
            </div>
          </Button>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">{SKILL_TYPE_ICONS[skill.type]}</span>
              <span className="font-bold">{skill.name}</span>
              <span className="text-xs text-slate-400">({skill.nameEn})</span>
            </div>
            <p className="text-sm text-slate-300">{skill.description}</p>
            <div className="flex gap-3 text-xs">
              <span className="text-orange-400">威力: {skill.power}</span>
              <span>命中: {skill.accuracy}%</span>
              <span className="text-blue-400">PP: {skill.pp}/{skill.maxPp}</span>
            </div>
            {skill.effect && (
              <div className="text-xs text-purple-400">
                附加效果: {skill.effect.type} ({skill.effect.chance}%概率)
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
