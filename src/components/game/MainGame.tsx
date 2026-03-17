'use client';

import { useState, useEffect } from 'react';
import { usePlayerData } from '@/hooks/usePlayerData';
import { useBattle } from '@/hooks/useBattle';
import { useSummon } from '@/hooks/useSummon';
import { Stage, OwnedCharacter, DailyTask } from '@/types/growth';
import { BattleCharacter, ELEMENT_COLORS } from '@/types/game';
import { GrowthPanel } from './GrowthPanel';
import { SummonPanel } from './SummonPanel';
import { StagePanel } from './StagePanel';
import { BattleScene } from './BattleScene';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';

type GameTab = 'home' | 'characters' | 'summon' | 'stages' | 'team';
type GameMode = 'main' | 'battle';

export function MainGame() {
  const [activeTab, setActiveTab] = useState<GameTab>('home');
  const [gameMode, setGameMode] = useState<GameMode>('main');
  const [pendingBattle, setPendingBattle] = useState<{
    stage: Stage;
    enemies: BattleCharacter[];
  } | null>(null);
  const [showDaily, setShowDaily] = useState(false);

  const {
    playerData,
    isLoading,
    resetData,
    addResources,
    spendResources,
    hasCharacter,
    getOwnedCharacter,
    obtainCharacter,
    levelUpCharacter,
    breakthroughCharacter,
    setTeam,
    getBattleCharacter,
    completeStage,
    updateDailyTask,
    claimDailyReward,
  } = usePlayerData();

  const {
    battleState,
    isAnimating,
    initBattle,
    executeSkill,
    enemySelectSkill,
    resetBattle,
  } = useBattle();

  // 抽卡系统
  const {
    summonOnce,
    summonTen,
    summonWithTicket,
    isSummoning,
    pity,
    legendaryPity,
    history,
  } = useSummon({
    onObtainCharacter: obtainCharacter,
    spendResources,
    updateDailyTask,
    hasCharacter,
  });

  // 开始副本战斗
  const handleStartStageBattle = (stage: Stage, enemies: BattleCharacter[]) => {
    if (!playerData || playerData.team.length === 0) return;

    const player = getBattleCharacter(playerData.team[0]);
    if (!player) return;

    // 对于多敌人，选择第一个敌人
    const enemy = enemies[0];
    if (!enemy) return;

    setPendingBattle({ stage, enemies });
    initBattle(player, enemy);
    setGameMode('battle');
  };

  // 战斗结束
  const handleBattleEnd = () => {
    if (battleState?.winner === 'player' && pendingBattle) {
      const rewards = pendingBattle.stage.rewards;
      completeStage(pendingBattle.stage.id, {
        gold: rewards.gold,
        gems: rewards.gems || 0,
        exp: rewards.exp,
      });
      updateDailyTask('daily-battle', 1);
    }

    resetBattle();
    setPendingBattle(null);
    setGameMode('main');
  };

  // 每日任务弹窗
  useEffect(() => {
    if (playerData && !isLoading) {
      const unclaimedTasks = playerData.dailyTasks.filter((t) => t.completed && !t.claimed);
      if (unclaimedTasks.length > 0) {
        setShowDaily(true);
      }
    }
  }, [playerData, isLoading]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-white text-xl animate-pulse">加载中...</div>
      </div>
    );
  }

  if (!playerData) return null;

  // 战斗模式
  if (gameMode === 'battle' && battleState) {
    return (
      <div className="min-h-screen bg-slate-950">
        <BattleScene
          battleState={battleState}
          isAnimating={isAnimating}
          onSkillSelect={executeSkill}
          onEnemyTurn={enemySelectSkill}
          onReset={handleBattleEnd}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white pb-20">
      {/* 顶部状态栏 */}
      <header className="sticky top-0 z-40 bg-slate-900 border-b-2 border-slate-700 shadow-xl">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-2xl">⚔️</div>
              <div>
                <div className="font-bold text-white">{playerData.name}</div>
                <div className="text-xs text-slate-400">Lv.{playerData.level}</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1 bg-slate-800 px-3 py-1 rounded-lg">
                <span>💰</span>
                <span className="font-bold text-yellow-400">{playerData.resources.gold}</span>
              </div>
              <div className="flex items-center gap-1 bg-slate-800 px-3 py-1 rounded-lg">
                <span>💎</span>
                <span className="font-bold text-cyan-400">{playerData.resources.gems}</span>
              </div>
              <div className="flex items-center gap-1 bg-slate-800 px-3 py-1 rounded-lg">
                <span>⚡</span>
                <span className="font-bold text-green-400">{playerData.resources.energy}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区域 */}
      <main className="max-w-4xl mx-auto px-4 py-4">
        {activeTab === 'home' && (
          <HomeTab
            playerData={playerData}
            team={playerData.team}
            getBattleCharacter={getBattleCharacter}
            onOpenDaily={() => setShowDaily(true)}
            onNavigate={setActiveTab}
          />
        )}

        {activeTab === 'characters' && (
          <GrowthPanel
            playerData={playerData}
            onLevelUp={levelUpCharacter}
            onBreakthrough={breakthroughCharacter}
            onSetTeam={setTeam}
            getBattleCharacter={getBattleCharacter}
          />
        )}

        {activeTab === 'summon' && (
          <SummonPanel
            gems={playerData.resources.gems}
            summonTickets={playerData.resources.summonTickets}
            pity={pity}
            legendaryPity={legendaryPity}
            isSummoning={isSummoning}
            onSummonOnce={summonOnce}
            onSummonTen={summonTen}
            onSummonWithTicket={summonWithTicket}
          />
        )}

        {activeTab === 'stages' && (
          <StagePanel
            playerLevel={playerData.level}
            energy={playerData.resources.energy}
            completedStages={playerData.completedStages}
            team={playerData.team}
            getBattleCharacter={getBattleCharacter}
            onStartBattle={handleStartStageBattle}
            onSpendEnergy={(amount) => spendResources({ energy: amount })}
          />
        )}

        {activeTab === 'team' && (
          <TeamTab
            playerData={playerData}
            team={playerData.team}
            getBattleCharacter={getBattleCharacter}
            setTeam={setTeam}
          />
        )}
      </main>

      {/* 底部导航 */}
      <nav className="fixed bottom-0 left-0 right-0 bg-slate-900 border-t-2 border-slate-700 z-40">
        <div className="max-w-4xl mx-auto flex">
          {[
            { id: 'home', icon: '🏠', label: '首页' },
            { id: 'characters', icon: '👥', label: '角色' },
            { id: 'summon', icon: '✨', label: '召唤' },
            { id: 'stages', icon: '⚔️', label: '副本' },
            { id: 'team', icon: '🎯', label: '队伍' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as GameTab)}
              className={cn(
                'flex-1 flex flex-col items-center py-2 transition-all',
                activeTab === tab.id
                  ? 'text-yellow-400 bg-slate-800'
                  : 'text-slate-400 hover:text-white'
              )}
            >
              <span className="text-xl">{tab.icon}</span>
              <span className="text-xs mt-1">{tab.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* 每日任务弹窗 */}
      <Dialog open={showDaily} onOpenChange={setShowDaily}>
        <DialogContent className="max-w-md bg-slate-800 border-2 border-slate-600">
          <DialogHeader>
            <DialogTitle className="text-white text-xl">📋 每日任务</DialogTitle>
          </DialogHeader>
          <div className="space-y-3 mt-4">
            {playerData.dailyTasks.map((task) => (
              <Card
                key={task.id}
                className={cn(
                  'border',
                  task.claimed
                    ? 'bg-slate-700 border-slate-600 opacity-50'
                    : task.completed
                    ? 'bg-green-900/30 border-green-500'
                    : 'bg-slate-700 border-slate-600'
                )}
              >
                <CardContent className="p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-white">{task.name}</h4>
                      <p className="text-xs text-slate-400">{task.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Progress value={(task.progress / task.target) * 100} className="h-1.5 w-24" />
                        <span className="text-xs text-slate-400">
                          {task.progress}/{task.target}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      {task.claimed ? (
                        <Badge variant="secondary" className="bg-slate-600">已领取</Badge>
                      ) : task.completed ? (
                        <Button
                          size="sm"
                          onClick={() => claimDailyReward(task.id)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          领取
                        </Button>
                      ) : (
                        <span className="text-xs text-slate-400">进行中</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 mt-2 text-xs">
                    {task.rewards.gold && (
                      <span className="text-yellow-400">💰 {task.rewards.gold}</span>
                    )}
                    {task.rewards.gems && (
                      <span className="text-cyan-400">💎 {task.rewards.gems}</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/** 首页Tab */
function HomeTab({
  playerData,
  team,
  getBattleCharacter,
  onOpenDaily,
  onNavigate,
}: {
  playerData: NonNullable<ReturnType<typeof usePlayerData>['playerData']>;
  team: string[];
  getBattleCharacter: (id: string) => BattleCharacter | null;
  onOpenDaily: () => void;
  onNavigate: (tab: GameTab) => void;
}) {
  const teamLeader = team[0] ? getBattleCharacter(team[0]) : null;
  const completedStagesCount = playerData.completedStages.length;

  return (
    <div className="space-y-4">
      {/* 欢迎横幅 */}
      <Card className="bg-gradient-to-r from-blue-900 to-purple-900 border-2 border-purple-500">
        <CardContent className="p-6 text-center">
          <h2 className="text-2xl font-black text-white mb-2">
            欢迎，{playerData.name}！
          </h2>
          <p className="text-slate-300">今天也要继续变强哦~</p>
          <div className="flex justify-center gap-4 mt-4">
            <Badge className="bg-slate-700 text-white text-sm px-4 py-1">
              游戏天数: {playerData.totalPlayDays}
            </Badge>
            <Badge className="bg-slate-700 text-white text-sm px-4 py-1">
              角色: {playerData.characters.length}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* 快捷入口 */}
      <div className="grid grid-cols-2 gap-3">
        <Card
          className="cursor-pointer hover:shadow-lg transition-all bg-slate-800 border-2 border-purple-500"
          onClick={() => onNavigate('summon')}
        >
          <CardContent className="p-4 text-center">
            <div className="text-4xl mb-2">✨</div>
            <h3 className="font-bold text-white">召唤英雄</h3>
            <p className="text-xs text-slate-400 mt-1">获取新角色</p>
          </CardContent>
        </Card>

        <Card
          className="cursor-pointer hover:shadow-lg transition-all bg-slate-800 border-2 border-orange-500"
          onClick={() => onNavigate('stages')}
        >
          <CardContent className="p-4 text-center">
            <div className="text-4xl mb-2">⚔️</div>
            <h3 className="font-bold text-white">副本挑战</h3>
            <p className="text-xs text-slate-400 mt-1">获取资源奖励</p>
          </CardContent>
        </Card>
      </div>

      {/* 当前队伍 */}
      <Card className="bg-slate-800 border-2 border-slate-600">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-white">当前队伍</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate('team')}
              className="border-slate-600 text-slate-300"
            >
              编辑
            </Button>
          </div>
          {team.length > 0 ? (
            <div className="flex gap-2">
              {team.map((instanceId) => {
                const char = getBattleCharacter(instanceId);
                if (!char) return null;
                return (
                  <div
                    key={instanceId}
                    className="w-16 h-16 rounded-lg overflow-hidden border-2 bg-slate-700"
                    style={{ borderColor: ELEMENT_COLORS[char.element] }}
                  >
                    <img
                      src={char.avatar}
                      alt={char.name}
                      className="w-full h-full object-cover object-top"
                    />
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-4 text-slate-400">
              还没有设置队伍，去角色页面选择出战角色
            </div>
          )}
        </CardContent>
      </Card>

      {/* 每日任务入口 */}
      <Card
        className="cursor-pointer hover:shadow-lg transition-all bg-slate-800 border-2 border-green-500"
        onClick={onOpenDaily}
      >
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-3xl">📋</div>
              <div>
                <h3 className="font-bold text-white">每日任务</h3>
                <p className="text-xs text-slate-400">
                  {playerData.dailyTasks.filter((t) => t.completed).length}/
                  {playerData.dailyTasks.length} 已完成
                </p>
              </div>
            </div>
            {playerData.dailyTasks.filter((t) => t.completed && !t.claimed).length > 0 && (
              <Badge className="bg-yellow-500 text-black">有奖励可领</Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 游戏进度 */}
      <Card className="bg-slate-800 border-2 border-slate-600">
        <CardContent className="p-4">
          <h3 className="font-bold text-white mb-3">📊 游戏进度</h3>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="bg-slate-700 rounded-lg p-3">
              <div className="text-2xl font-bold text-yellow-400">{playerData.characters.length}</div>
              <div className="text-xs text-slate-400">拥有角色</div>
            </div>
            <div className="bg-slate-700 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-400">{completedStagesCount}</div>
              <div className="text-xs text-slate-400">通关关卡</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/** 队伍Tab */
function TeamTab({
  playerData,
  team,
  getBattleCharacter,
  setTeam,
}: {
  playerData: NonNullable<ReturnType<typeof usePlayerData>['playerData']>;
  team: string[];
  getBattleCharacter: (id: string) => BattleCharacter | null;
  setTeam: (ids: string[]) => void;
}) {
  const [selectedIds, setSelectedIds] = useState<string[]>(team);

  const toggleCharacter = (instanceId: string) => {
    if (selectedIds.includes(instanceId)) {
      setSelectedIds(selectedIds.filter((id) => id !== instanceId));
    } else if (selectedIds.length < 4) {
      setSelectedIds([...selectedIds, instanceId]);
    }
  };

  const saveTeam = () => {
    setTeam(selectedIds);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-white">编辑队伍 (最多4人)</h3>
        <Button
          onClick={saveTeam}
          className="bg-green-600 hover:bg-green-700"
        >
          保存队伍
        </Button>
      </div>

      {/* 当前选择 */}
      <Card className="bg-slate-800 border-2 border-yellow-500">
        <CardContent className="p-4">
          <div className="flex gap-2 justify-center">
            {[0, 1, 2, 3].map((index) => {
              const instanceId = selectedIds[index];
              const char = instanceId ? getBattleCharacter(instanceId) : null;
              return (
                <div
                  key={index}
                  className={cn(
                    'w-16 h-16 rounded-lg border-2 flex items-center justify-center',
                    char ? 'bg-slate-700' : 'bg-slate-800 border-dashed border-slate-600'
                  )}
                  style={{ borderColor: char ? ELEMENT_COLORS[char.element] : undefined }}
                >
                  {char ? (
                    <img
                      src={char.avatar}
                      alt={char.name}
                      className="w-full h-full object-cover object-top rounded-md"
                    />
                  ) : (
                    <span className="text-slate-600 text-2xl">+</span>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* 角色列表 */}
      <div className="grid grid-cols-3 gap-3">
        {playerData.characters.map((owned) => {
          const char = getBattleCharacter(owned.id);
          if (!char) return null;
          const isSelected = selectedIds.includes(owned.id);

          return (
            <Card
              key={owned.id}
              className={cn(
                'cursor-pointer transition-all border-2 overflow-hidden',
                isSelected ? 'border-yellow-400 ring-2 ring-yellow-400/30' : 'border-slate-600'
              )}
              onClick={() => toggleCharacter(owned.id)}
            >
              <div className="relative aspect-square">
                <img
                  src={char.avatar}
                  alt={char.name}
                  className="w-full h-full object-cover object-top"
                />
                {isSelected && (
                  <div className="absolute top-1 right-1 bg-yellow-500 text-black text-xs px-1.5 py-0.5 rounded font-bold">
                    {selectedIds.indexOf(owned.id) + 1}
                  </div>
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900 to-transparent p-2">
                  <div className="text-xs font-bold text-white truncate">{char.name}</div>
                  <div className="text-xs text-slate-300">Lv.{char.level}</div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
