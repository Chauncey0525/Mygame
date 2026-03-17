'use client';

import Image from 'next/image';
import { useState, useEffect } from 'react';
import { SKILL_EFFECTS } from '@/data/assets';
import { cn } from '@/lib/utils';

interface SkillEffectProps {
  element: string;
  type?: 'attack' | 'heal' | 'buff' | 'critical';
  onComplete?: () => void;
  damage?: number;
}

export function SkillEffect({ element, type = 'attack', onComplete, damage }: SkillEffectProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onComplete?.();
    }, 800);

    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!isVisible) return null;

  const effectUrl = type === 'critical' 
    ? SKILL_EFFECTS.critical 
    : type === 'heal' 
    ? SKILL_EFFECTS.heal 
    : type === 'buff' 
    ? SKILL_EFFECTS.buff
    : SKILL_EFFECTS[element as keyof typeof SKILL_EFFECTS] || SKILL_EFFECTS.fire;

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center pointer-events-none">
      {/* 特效背景遮罩 */}
      <div className="absolute inset-0 bg-black/60 animate-pulse" />
      
      {/* 特效图片 */}
      <div className="relative animate-bounce">
        <Image
          src={effectUrl}
          alt="Skill Effect"
          width={280}
          height={280}
          className="animate-pulse drop-shadow-2xl rounded-xl"
          unoptimized
        />
        
        {/* 伤害数字 */}
        {damage && damage > 0 && (
          <div className={cn(
            'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
            'text-5xl font-black drop-shadow-[0_4px_8px_rgba(0,0,0,0.9)]',
            type === 'critical' && 'text-yellow-400 text-6xl animate-pulse',
            type === 'heal' ? 'text-green-400' : 'text-white'
          )}>
            {type === 'heal' ? '+' : '-'}{damage}
            {type === 'critical' && <span className="block text-lg text-center">暴击!</span>}
          </div>
        )}
      </div>
      
      {/* 光效动画 */}
      <div className={cn(
        'absolute inset-0 animate-ping opacity-20',
        type === 'critical' && 'bg-yellow-500',
        type === 'heal' && 'bg-green-500',
        type === 'attack' && 'bg-red-500'
      )} />
    </div>
  );
}

/** 小型浮动伤害数字 */
interface DamageNumberProps {
  damage: number;
  isCritical?: boolean;
  isHeal?: boolean;
}

export function DamageNumber({ damage, isCritical, isHeal }: DamageNumberProps) {
  return (
    <div
      className={cn(
        'absolute left-1/2 top-0 -translate-x-1/2 -translate-y-4',
        'text-3xl font-black animate-bounce drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]',
        isHeal ? 'text-green-400' : isCritical ? 'text-yellow-400 text-4xl' : 'text-red-400'
      )}
    >
      {isHeal ? '+' : '-'}{damage}
      {isCritical && <span className="ml-1 text-sm text-yellow-300">暴击!</span>}
    </div>
  );
}
