'use client';

import Image from 'next/image';
import { BattleCharacter, ELEMENT_COLORS, ELEMENT_NAMES, ROLE_NAMES } from '@/types/game';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface CharacterCardProps {
  character: BattleCharacter;
  isEnemy?: boolean;
  isActive?: boolean;
  showFullStats?: boolean;
  showIllustration?: boolean;
}

export function CharacterCard({ 
  character, 
  isEnemy = false, 
  isActive = false, 
  showFullStats = true,
  showIllustration = false 
}: CharacterCardProps) {
  const hpPercent = (character.currentStats.hp / character.stats.maxHp) * 100;
  const hpColor = hpPercent > 50 ? 'bg-green-500' : hpPercent > 25 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div
      className={cn(
        'relative rounded-xl border-2 p-4 transition-all duration-300',
        isActive
          ? 'border-yellow-400 shadow-lg shadow-yellow-400/30 ring-2 ring-yellow-400/50'
          : 'border-slate-700 bg-slate-800/80',
        isEnemy ? 'bg-gradient-to-b from-red-900/30 to-slate-800/80' : 'bg-gradient-to-b from-blue-900/30 to-slate-800/80'
      )}
    >
      {/* 活动指示器 */}
      {isActive && (
        <div className="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-yellow-400 text-xs font-bold text-black animate-pulse">
          ▶
        </div>
      )}

      {/* 立绘模式 */}
      {showIllustration && (
        <div className="absolute inset-0 -z-10 overflow-hidden rounded-xl">
          <Image
            src={character.illustration}
            alt={character.name}
            fill
            className={cn(
              'object-cover object-top transition-all duration-500',
              isEnemy ? 'scale-x-[-1]' : ''
            )}
            style={{ opacity: 0.3 }}
            unoptimized
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/50 to-transparent" />
        </div>
      )}

      <div className="flex gap-4">
        {/* 角色头像区域 */}
        <div className="relative flex-shrink-0">
          <div
            className={cn(
              'h-20 w-20 rounded-lg border-2 overflow-hidden',
              showIllustration ? 'bg-slate-700' : 'bg-slate-700'
            )}
            style={{ borderColor: ELEMENT_COLORS[character.element] }}
          >
            {character.avatar ? (
              <Image
                src={character.avatar}
                alt={character.name}
                width={80}
                height={80}
                className="object-cover object-top"
                unoptimized
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-3xl">
                {character.id === 'zhuge-liang' && '🪭'}
                {character.id === 'napoleon' && '⚔️'}
                {character.id === 'arthur' && '🗡️'}
                {character.id === 'wu-zetian' && '👑'}
                {character.id === 'hua-mulan' && '🌸'}
                {character.id === 'caesar' && '🦅'}
              </div>
            )}
          </div>
          {/* 元素标记 */}
          <div
            className="absolute -bottom-1 left-1/2 -translate-x-1/2 rounded-full px-2 py-0.5 text-xs font-bold text-white shadow-lg"
            style={{ backgroundColor: ELEMENT_COLORS[character.element] }}
          >
            {ELEMENT_NAMES[character.element]}
          </div>
        </div>

        {/* 角色信息 */}
        <div className="flex-1 space-y-2">
          <div>
            <h3 className="text-lg font-bold text-white drop-shadow-lg">{character.name}</h3>
            <p className="text-xs text-slate-300">{character.title}</p>
          </div>

          {/* HP条 */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-red-400">HP</span>
              <span className="text-white font-medium">
                {Math.floor(character.currentStats.hp)} / {character.stats.maxHp}
              </span>
            </div>
            <div className="relative h-3 overflow-hidden rounded-full bg-slate-700 shadow-inner">
              <div
                className={cn('absolute left-0 top-0 h-full transition-all duration-500', hpColor)}
                style={{ width: `${hpPercent}%` }}
              />
              {/* HP条闪光效果 */}
              <div
                className="absolute top-0 h-full w-full animate-pulse bg-gradient-to-r from-transparent via-white/20 to-transparent"
                style={{ width: `${hpPercent}%` }}
              />
            </div>
          </div>

          {/* 状态效果 */}
          {character.statusEffects.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {character.statusEffects.map((effect, i) => (
                <Badge key={i} variant="outline" className="text-xs bg-slate-800/80">
                  {effect.type === 'burn' && '🔥灼烧'}
                  {effect.type === 'poison' && '☠️中毒'}
                  {effect.type === 'stun' && '💫眩晕'}
                  {effect.type === 'buff_attack' && '⬆️攻击↑'}
                  {effect.type === 'buff_defense' && '🛡️防御↑'}
                  {effect.type === 'debuff_attack' && '⬇️攻击↓'}
                  {effect.type === 'debuff_defense' && '🔻防御↓'}
                  <span className="ml-1 text-yellow-400">({effect.duration})</span>
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 详细属性 */}
      {showFullStats && (
        <div className="mt-3 grid grid-cols-3 gap-2 border-t border-slate-700 pt-3">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <div className="text-center">
                  <div className="text-xs text-slate-400">ATK</div>
                  <div className="font-bold text-orange-400">{character.currentStats.attack}</div>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>攻击力: {character.stats.attack}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <div className="text-center">
                  <div className="text-xs text-slate-400">DEF</div>
                  <div className="font-bold text-blue-400">{character.currentStats.defense}</div>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>防御力: {character.stats.defense}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <div className="text-center">
                  <div className="text-xs text-slate-400">SPD</div>
                  <div className="font-bold text-green-400">{character.currentStats.speed}</div>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>速度: {character.stats.speed}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      )}
    </div>
  );
}
