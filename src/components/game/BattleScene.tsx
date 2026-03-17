'use client';

import { useEffect, useState } from 'react';
import { BattleState, BattleCharacter } from '@/types/game';
import { CharacterCard } from './CharacterCard';
import { SkillButton } from './SkillButton';
import { BattleLogDisplay } from './BattleLog';
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
  const [damageAnimation, setDamageAnimation] = useState<{ targetId: string; damage: number } | null>(null);

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

  // 伤害动画
  useEffect(() => {
    if (battleState.results.length > 0) {
      const lastResult = battleState.results[battleState.results.length - 1];
      if (lastResult.damage > 0) {
        setDamageAnimation({ targetId: lastResult.defenderId, damage: lastResult.damage });
        const timer = setTimeout(() => setDamageAnimation(null), 800);
        return () => clearTimeout(timer);
      }
    }
  }, [battleState.results]);

  return (
    <div className="relative mx-auto flex h-full min-h-[600px] w-full max-w-4xl flex-col gap-4 p-4">
      {/* 战斗背景 */}
      <div className="absolute inset-0 -z-10 overflow-hidden rounded-xl">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-800 via-slate-900 to-slate-950" />
        <div className="absolute inset-0 bg-[url('/battle-bg.svg')] opacity-10" />
        {/* 动态光效 */}
        <div className="absolute left-1/4 top-1/4 h-32 w-32 animate-pulse rounded-full bg-blue-500/20 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-32 w-32 animate-pulse rounded-full bg-red-500/20 blur-3xl" />
      </div>

      {/* 回合指示器 */}
      <div className="flex items-center justify-center">
        <div className="rounded-full bg-slate-800 px-6 py-2 text-center">
          <span className="text-sm text-slate-400">第 </span>
          <span className="font-bold text-white">{battleState.turn}</span>
          <span className="text-sm text-slate-400"> 回合</span>
          <span className="ml-2 text-sm text-slate-400">|</span>
          <span className="ml-2 text-sm">
            {isPlayerTurn ? (
              <span className="text-blue-400">你的回合</span>
            ) : (
              <span className="text-red-400">敌方回合</span>
            )}
          </span>
        </div>
      </div>

      {/* 战斗区域 */}
      <div className="grid flex-1 grid-cols-2 gap-4">
        {/* 玩家区域 */}
        <div className="relative">
          <CharacterCard
            character={battleState.player}
            isActive={isPlayerTurn && canAct}
            isEnemy={false}
          />
          {/* 伤害数字 */}
          {damageAnimation?.targetId === battleState.player.id && (
            <div className="absolute left-1/2 top-0 -translate-x-1/2 animate-bounce text-2xl font-bold text-red-500 drop-shadow-lg">
              -{damageAnimation.damage}
            </div>
          )}
        </div>

        {/* 敌人区域 */}
        <div className="relative">
          <CharacterCard
            character={battleState.enemy}
            isActive={!isPlayerTurn && canAct}
            isEnemy={true}
          />
          {/* 伤害数字 */}
          {damageAnimation?.targetId === battleState.enemy.id && (
            <div className="absolute left-1/2 top-0 -translate-x-1/2 animate-bounce text-2xl font-bold text-red-500 drop-shadow-lg">
              -{damageAnimation.damage}
            </div>
          )}
        </div>
      </div>

      {/* VS标志 */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <div className="text-4xl font-black text-slate-600 opacity-30">VS</div>
      </div>

      {/* 技能面板 */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/90 p-4">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-300">技能</h3>
          {isAnimating && (
            <span className="animate-pulse text-sm text-yellow-400">执行中...</span>
          )}
          {!isPlayerTurn && !isAnimating && !battleState.winner && (
            <span className="animate-pulse text-sm text-red-400">敌方思考中...</span>
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
        <DialogContent className="text-center">
          <DialogHeader>
            <DialogTitle className={cn('text-2xl', battleState.winner === 'player' ? 'text-green-400' : 'text-red-400')}>
              {battleState.winner === 'player' ? '🏆 胜利！' : '💔 失败...'}
            </DialogTitle>
            <DialogDescription className="text-lg">
              {battleState.winner === 'player'
                ? `${battleState.player.name} 击败了 ${battleState.enemy.name}！`
                : `${battleState.player.name} 被 ${battleState.enemy.name} 击败了...`}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            <div className="rounded-lg bg-slate-800 p-4">
              <h4 className="mb-2 font-bold">战斗统计</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">总回合数:</span>
                  <span className="ml-2 font-bold">{battleState.turn}</span>
                </div>
                <div>
                  <span className="text-slate-400">剩余HP:</span>
                  <span className="ml-2 font-bold text-green-400">
                    {Math.floor(battleState.player.currentStats.hp)} / {battleState.player.stats.maxHp}
                  </span>
                </div>
              </div>
            </div>
            <Button onClick={onReset} className="w-full">
              返回选择角色
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
