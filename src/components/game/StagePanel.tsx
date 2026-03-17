'use client';

import Image from 'next/image';
import { useState } from 'react';
import { Stage, Chapter } from '@/types/growth';
import { BattleCharacter, ELEMENT_COLORS, ELEMENT_NAMES } from '@/types/game';
import { CHAPTERS, getStage, isChapterUnlocked, DIFFICULTY_NAMES, DIFFICULTY_COLORS } from '@/data/stages';
import { ALL_CHARACTERS } from '@/data/characters';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface StagePanelProps {
  playerLevel: number;
  energy: number;
  completedStages: string[];
  team: string[];
  getBattleCharacter: (instanceId: string) => BattleCharacter | null;
  onStartBattle: (stage: Stage, enemies: BattleCharacter[]) => void;
  onSpendEnergy: (amount: number) => boolean;
}

export function StagePanel({
  playerLevel,
  energy,
  completedStages,
  team,
  getBattleCharacter,
  onStartBattle,
  onSpendEnergy,
}: StagePanelProps) {
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [selectedStage, setSelectedStage] = useState<Stage | null>(null);

  // 检查章节解锁状态
  const chaptersWithStatus = CHAPTERS.map((chapter) => ({
    ...chapter,
    unlocked: isChapterUnlocked(chapter.id, completedStages),
    progress: chapter.stages.filter((s) => completedStages.includes(s.id)).length,
    total: chapter.stages.length,
  }));

  const handleSelectStage = (stage: Stage) => {
    setSelectedStage(stage);
  };

  const handleStartBattle = () => {
    if (!selectedStage) return;
    
    // 生成敌人
    const enemiesData = selectedStage.enemyIds.map((enemyId, index) => {
      const template = ALL_CHARACTERS.find((c) => c.id === enemyId);
      if (!template) return null;
      
      const level = selectedStage.enemyLevels[index] || 1;
      const multiplier = 1 + (level - 1) * 0.05;
      
      const baseStats = {
        hp: Math.floor(template.stats.hp * multiplier),
        maxHp: Math.floor(template.stats.hp * multiplier),
        attack: Math.floor(template.stats.attack * multiplier),
        defense: Math.floor(template.stats.defense * multiplier),
        specialAttack: Math.floor(template.stats.specialAttack * multiplier),
        specialDefense: Math.floor(template.stats.specialDefense * multiplier),
        speed: Math.floor(template.stats.speed * multiplier),
        critRate: template.stats.critRate,
        critDamage: template.stats.critDamage,
      };
      
      return {
        id: template.id,
        name: template.name,
        nameEn: template.nameEn,
        title: template.title,
        era: template.era,
        origin: template.origin,
        element: template.element,
        roleType: template.roleType,
        description: template.description,
        avatar: template.avatar,
        illustration: template.illustration,
        stats: baseStats,
        skills: template.skills,
        currentStats: { ...baseStats },
        statusEffects: [],
        level,
        exp: 0,
      } as BattleCharacter;
    });
    
    const enemies = enemiesData.filter((e): e is BattleCharacter => e !== null);

    if (onSpendEnergy(selectedStage.energyCost)) {
      onStartBattle(selectedStage, enemies);
      setSelectedStage(null);
    }
  };

  // 获取队伍第一个角色
  const teamLeader = team[0] ? getBattleCharacter(team[0]) : null;

  return (
    <div className="space-y-4">
      {/* 顶部信息栏 */}
      <div className="flex items-center justify-between bg-slate-800 rounded-lg p-4 border border-slate-600">
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-sm text-slate-400">体力</div>
            <div className="text-xl font-bold text-green-400">⚡ {energy}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-slate-400">推荐等级</div>
            <div className="text-xl font-bold text-blue-400">Lv.{playerLevel}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-slate-400">出战角色</div>
          <div className="text-lg font-bold text-yellow-400">
            {team.length > 0 ? `${team.length}/4` : '未设置'}
          </div>
        </div>
      </div>

      {/* 章节选择 或 关卡选择 */}
      {!selectedChapter ? (
        <div className="grid gap-4">
          <h3 className="text-lg font-bold text-white">选择章节</h3>
          {chaptersWithStatus.map((chapter) => (
            <Card
              key={chapter.id}
              className={cn(
                'cursor-pointer transition-all border-2',
                chapter.unlocked
                  ? 'hover:border-yellow-400 hover:shadow-lg bg-slate-800'
                  : 'opacity-50 cursor-not-allowed bg-slate-900'
              )}
              onClick={() => chapter.unlocked && setSelectedChapter(chapter)}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-white text-lg">{chapter.name}</h4>
                    <p className="text-sm text-slate-400 mt-1">{chapter.description}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-400">进度</div>
                    <div className="text-lg font-bold text-yellow-400">
                      {chapter.progress}/{chapter.total}
                    </div>
                  </div>
                </div>
                <Progress
                  value={(chapter.progress / chapter.total) * 100}
                  className="h-2 mt-3"
                />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {/* 返回按钮 */}
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => {
                setSelectedChapter(null);
                setSelectedStage(null);
              }}
              className="border-slate-600 text-slate-300"
            >
              ← 返回章节
            </Button>
            <h3 className="text-lg font-bold text-white">{selectedChapter.name}</h3>
          </div>

          {/* 关卡列表 */}
          <div className="grid gap-3">
            {selectedChapter.stages.map((stage) => {
              const isCompleted = completedStages.includes(stage.id);
              const canEnter = energy >= stage.energyCost && team.length > 0;

              return (
                <Card
                  key={stage.id}
                  className={cn(
                    'cursor-pointer transition-all border-2',
                    isCompleted
                      ? 'bg-green-900/20 border-green-600'
                      : selectedStage?.id === stage.id
                      ? 'bg-blue-900/30 border-blue-400'
                      : 'bg-slate-800 border-slate-600 hover:border-slate-400'
                  )}
                  onClick={() => handleSelectStage(stage)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {/* 状态图标 */}
                        <div className={cn(
                          'w-10 h-10 rounded-full flex items-center justify-center text-lg',
                          isCompleted ? 'bg-green-600' : 'bg-slate-700'
                        )}>
                          {isCompleted ? '✓' : stage.energyCost}
                        </div>
                        <div>
                          <h4 className="font-bold text-white">{stage.name}</h4>
                          <p className="text-xs text-slate-400">{stage.description}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge
                          className="text-xs"
                          style={{ backgroundColor: DIFFICULTY_COLORS[stage.difficulty] }}
                        >
                          {DIFFICULTY_NAMES[stage.difficulty]}
                        </Badge>
                        <div className="text-xs text-slate-400 mt-1">
                          推荐 Lv.{stage.recommendedLevel}
                        </div>
                      </div>
                    </div>

                    {/* 敌人预览 */}
                    <div className="flex gap-2 mt-3">
                      {stage.enemyIds.map((enemyId) => {
                        const enemy = ALL_CHARACTERS.find((c) => c.id === enemyId);
                        return enemy ? (
                          <div
                            key={enemyId}
                            className="w-10 h-10 rounded-full overflow-hidden border-2 bg-slate-700"
                            style={{ borderColor: ELEMENT_COLORS[enemy.element] }}
                          >
                            <Image
                              src={enemy.avatar}
                              alt={enemy.name}
                              width={40}
                              height={40}
                              className="object-cover object-top"
                              unoptimized
                            />
                          </div>
                        ) : null;
                      })}
                    </div>

                    {/* 奖励 */}
                    <div className="flex gap-3 mt-3 text-xs">
                      <span className="text-yellow-400">💰 {stage.rewards.gold}</span>
                      <span className="text-green-400">📖 {stage.rewards.exp}</span>
                      {stage.rewards.gems && (
                        <span className="text-cyan-400">💎 {stage.rewards.gems}</span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* 开始战斗按钮 */}
          {selectedStage && (
            <div className="fixed bottom-20 left-0 right-0 p-4 bg-slate-900/95 border-t border-slate-600">
              <div className="max-w-lg mx-auto flex items-center justify-between">
                <div>
                  <div className="font-bold text-white">{selectedStage.name}</div>
                  <div className="text-sm text-slate-400">
                    消耗 ⚡ {selectedStage.energyCost}
                  </div>
                </div>
                <Button
                  onClick={handleStartBattle}
                  disabled={energy < selectedStage.energyCost || team.length === 0}
                  className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 px-6"
                >
                  开始战斗
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
