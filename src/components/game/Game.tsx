'use client';

import { useState } from 'react';
import { BattleCharacter } from '@/types/game';
import { ALL_CHARACTERS, getRandomCharacter } from '@/data/characters';
import { useBattle } from '@/hooks/useBattle';
import { CharacterSelect } from './CharacterSelect';
import { BattleScene } from './BattleScene';
import { Button } from '@/components/ui/button';

type GamePhase = 'select' | 'battle';

export function Game() {
  const [phase, setPhase] = useState<GamePhase>('select');
  const [selectedCharacter, setSelectedCharacter] = useState<BattleCharacter | null>(null);
  const [enemy, setEnemy] = useState<BattleCharacter | null>(null);

  const { battleState, isAnimating, initBattle, executeSkill, enemySelectSkill, resetBattle } = useBattle();

  const handleSelectCharacter = (character: BattleCharacter) => {
    setSelectedCharacter(character);
  };

  const handleRandomSelect = () => {
    const randomChar = ALL_CHARACTERS[Math.floor(Math.random() * ALL_CHARACTERS.length)];
    setSelectedCharacter(randomChar);
  };

  const handleStartBattle = () => {
    if (!selectedCharacter) return;

    // 随机选择敌人（排除玩家选择的角色）
    const enemyChar = getRandomCharacter([selectedCharacter.id]);
    setEnemy(enemyChar);

    // 初始化战斗
    initBattle(selectedCharacter, enemyChar);
    setPhase('battle');
  };

  const handleBackToSelect = () => {
    resetBattle();
    setPhase('select');
    setSelectedCharacter(null);
    setEnemy(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* 顶部导航 */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚔️</span>
            <h1 className="text-xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
              历史英雄对决
            </h1>
          </div>
          {phase === 'battle' && (
            <Button variant="ghost" onClick={handleBackToSelect} className="text-slate-400 hover:text-white">
              ← 返回选择
            </Button>
          )}
        </div>
      </header>

      {/* 主内容区域 */}
      <main className="py-6">
        {phase === 'select' && (
          <CharacterSelect
            characters={ALL_CHARACTERS}
            selectedCharacter={selectedCharacter}
            onSelect={handleSelectCharacter}
            onStartBattle={handleStartBattle}
            onRandomSelect={handleRandomSelect}
          />
        )}

        {phase === 'battle' && battleState && (
          <BattleScene
            battleState={battleState}
            isAnimating={isAnimating}
            onSkillSelect={executeSkill}
            onEnemyTurn={enemySelectSkill}
            onReset={handleBackToSelect}
          />
        )}
      </main>

      {/* 底部信息 */}
      <footer className="border-t border-slate-800 bg-slate-900/50 py-4">
        <div className="mx-auto max-w-5xl px-4 text-center text-xs text-slate-500">
          <p>历史英雄对决 - 以古今中外历史人物为背景的回合制战斗游戏</p>
          <p className="mt-1">所有角色数据由AI生成，仅供娱乐</p>
        </div>
      </footer>
    </div>
  );
}
