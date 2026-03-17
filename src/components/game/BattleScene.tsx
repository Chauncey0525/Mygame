'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { BattleState, BattleCharacter } from '@/types/game';
import { CharacterCard } from './CharacterCard';
import { SkillButton } from './SkillButton';
import { BattleLogDisplay } from './BattleLog';
import { SkillEffect, DamageNumber } from './SkillEffect';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';

interface BattleSceneProps {
  battleState: BattleState;
  isAnimating: boolean;
  onSkillSelect: (skillId: string) => void;
  onEnemyTurn: () => string | null;
  onReset: () => void;
}

export function BattleScene({
  battleState,
  isAnimating,
  onSkillSelect,
  onEnemyTurn,
  onReset,
}: BattleSceneProps) {
  const [showResult, setShowResult] = useState(false);
  const [showSkillEffect, setShowSkillEffect] = useState<{ element: string; type: string; damage: number } | null>(null);
  const [damageAnimation, setDamageAnimation] = useState<{ targetId: string; damage: number; isCritical: boolean; isHeal: boolean } | null>(null);

  const isPlayerTurn = battleState.currentTurnId === battleState.player.id;
  const canAct = !isAnimating && battleState.phase === 'select';

  // 敌人AI行动
  useEffect(() => {
    if (battleState.phase === 'select' && !isPlayerTurn && !isAnimating && !battleState.winner) {
      const timer = setTimeout(() => {
        const skillId = onEnemyTurn();
        if (skillId) {
          onSkillSelect(skillId);
        }
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [battleState.phase, isPlayerTurn, isAnimating, battleState.winner, onEnemyTurn, onSkillSelect]);

  // 显示结果对话框
  useEffect(() => {
    if (battleState.winner) {
      const timer = setTimeout(() => setShowResult(true), 500);
      return () => clearTimeout(timer);
    }
  }, [battleState.winner]);

  // 伤害动画和技能特效
  useEffect(() => {
    if (battleState.results.length > 0) {
      const lastResult = battleState.results[battleState.results.length - 1];
      if (lastResult.damage > 0 || lastResult.skillUsed.type === 'heal') {
        const effectType = lastResult.isCritical ? 'critical' : lastResult.skillUsed.type;
        setShowSkillEffect({
          element: lastResult.skillUsed.element,
          type: effectType,
          damage: lastResult.damage,
        });

        setTimeout(() => {
          setDamageAnimation({
            targetId: lastResult.defenderId,
            damage: lastResult.damage,
            isCritical: lastResult.isCritical,
            isHeal: lastResult.skillUsed.type === 'heal',
          });
        }, 400);

        const timer = setTimeout(() => {
          setDamageAnimation(null);
          setShowSkillEffect(null);
        }, 1000);
        return () => clearTimeout(timer);
      }
    }
  }, [battleState.results]);

  return (
    <div className="relative mx-auto flex h-full min-h-[700px] w-full max-w-5xl flex-col gap-4 p-4">
      {/* 战斗背景 */}
      <div className="absolute inset-0 -z-10 overflow-hidden rounded-xl bg-slate-900">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-800 via-slate-900 to-slate-950" />
      </div>

      {/* 技能特效层 */}
      {showSkillEffect && (
        <SkillEffect
          element={showSkillEffect.element}
          type={showSkillEffect.type as 'attack' | 'heal' | 'buff' | 'critical'}
          damage={showSkillEffect.damage}
        />
      )}

      {/* 回合指示器 */}
      <div className="flex items-center justify-center">
        <div className="rounded-full bg-slate-700 px-6 py-2 text-center border-2 border-slate-600 shadow-lg">
          <span className="text-sm text-slate-300">第 </span>
          <span className="font-bold text-white">{battleState.turn}</span>
          <span className="text-sm text-slate-300"> 回合</span>
          <span className="mx-2 text-slate-500">|</span>
          <span className="text-sm font-bold">
            {isPlayerTurn ? (
              <span className="text-blue-400">▶ 你的回合</span>
            ) : (
              <span className="text-red-400">▶ 敌方回合</span>
            )}
          </span>
        </div>
      </div>

      {/* 战斗区域 - 角色立绘 + 卡片 */}
      <div className="relative grid flex-1 grid-cols-2 gap-6 py-4">
        {/* 玩家区域 */}
        <div className="relative flex flex-col items-center gap-4">
          {/* 立绘背景 */}
          <div className="absolute inset-0 -z-5 overflow-hidden rounded-xl">
            <Image
              src={battleState.player.illustration}
              alt={battleState.player.name}
              fill
              className="object-cover object-top scale-110"
              style={{ opacity: 0.12 }}
              unoptimized
            />
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-slate-900/80 to-slate-900" />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/60 to-slate-900/30" />
          </div>
          
          {/* 角色卡片 */}
          <div className="relative w-full mt-auto">
            <CharacterCard
              character={battleState.player}
              isActive={isPlayerTurn && canAct}
              isEnemy={false}
            />
            {damageAnimation?.targetId === battleState.player.id && (
              <DamageNumber
                damage={damageAnimation.damage}
                isCritical={damageAnimation.isCritical}
                isHeal={damageAnimation.isHeal}
              />
            )}
          </div>
        </div>

        {/* 敌人区域 */}
        <div className="relative flex flex-col items-center gap-4">
          {/* 立绘背景 - 水平翻转 */}
          <div className="absolute inset-0 -z-5 overflow-hidden rounded-xl">
            <Image
              src={battleState.enemy.illustration}
              alt={battleState.enemy.name}
              fill
              className="object-cover object-top scale-110 scale-x-[-1]"
              style={{ opacity: 0.12 }}
              unoptimized
            />
            <div className="absolute inset-0 bg-gradient-to-l from-transparent via-slate-900/80 to-slate-900" />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/60 to-slate-900/30" />
          </div>
          
          {/* 角色卡片 */}
          <div className="relative w-full mt-auto">
            <CharacterCard
              character={battleState.enemy}
              isActive={!isPlayerTurn && canAct}
              isEnemy={true}
            />
            {damageAnimation?.targetId === battleState.enemy.id && (
              <DamageNumber
                damage={damageAnimation.damage}
                isCritical={damageAnimation.isCritical}
                isHeal={damageAnimation.isHeal}
              />
            )}
          </div>
        </div>

        {/* VS标志 */}
        <div className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
          <div className="text-5xl font-black text-slate-500 drop-shadow-lg">VS</div>
        </div>
      </div>

      {/* 技能面板 */}
      <div className="rounded-xl border-2 border-slate-600 bg-slate-800 p-4 shadow-xl">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-base font-bold text-white">⚔️ 技能选择</h3>
          {isAnimating && (
            <span className="animate-pulse text-sm text-yellow-400 font-medium">⚡ 执行中...</span>
          )}
          {!isPlayerTurn && !isAnimating && !battleState.winner && (
            <span className="animate-pulse text-sm text-red-400 font-medium">🎯 敌方思考中...</span>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
          {battleState.player.skills.map((skill) => (
            <SkillButton
              key={skill.id}
              skill={skill}
              disabled={!canAct || !isPlayerTurn}
              onClick={() => onSkillSelect(skill.id)}
              isActive={isPlayerTurn && canAct}
            />
          ))}
        </div>
      </div>

      {/* 战斗日志 */}
      <BattleLogDisplay logs={battleState.logs.slice(-10)} />

      {/* 战斗结果对话框 */}
      <Dialog open={showResult} onOpenChange={setShowResult}>
        <DialogContent className="text-center max-w-md bg-slate-800 border-2 border-slate-600">
          <DialogHeader>
            <DialogTitle className={cn('text-3xl font-black', battleState.winner === 'player' ? 'text-green-400' : 'text-red-400')}>
              {battleState.winner === 'player' ? '🏆 胜利！' : '💔 失败...'}
            </DialogTitle>
            <DialogDescription className="text-lg pt-2 text-slate-200">
              {battleState.winner === 'player'
                ? `${battleState.player.name} 击败了 ${battleState.enemy.name}！`
                : `${battleState.player.name} 被 ${battleState.enemy.name} 击败了...`}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            {/* 胜利角色立绘 */}
            {battleState.winner === 'player' && (
              <div className="relative h-40 w-full overflow-hidden rounded-lg border-2 border-slate-600">
                <Image
                  src={battleState.player.illustration}
                  alt={battleState.player.name}
                  fill
                  className="object-cover object-top"
                  unoptimized
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />
              </div>
            )}
            
            <div className="rounded-lg bg-slate-700 p-4 border border-slate-600">
              <h4 className="mb-2 font-bold text-yellow-400">📊 战斗统计</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-300">总回合数:</span>
                  <span className="ml-2 font-bold text-white">{battleState.turn}</span>
                </div>
                <div>
                  <span className="text-slate-300">剩余HP:</span>
                  <span className="ml-2 font-bold text-green-400">
                    {Math.floor(battleState.player.currentStats.hp)} / {battleState.player.stats.maxHp}
                  </span>
                </div>
              </div>
            </div>
            <Button onClick={onReset} className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-6">
              🔄 返回选择角色
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
