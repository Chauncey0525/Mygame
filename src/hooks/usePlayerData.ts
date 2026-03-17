'use client';

import { useState, useCallback, useEffect } from 'react';
import {
  PlayerData,
  OwnedCharacter,
  PlayerResources,
  DailyTask,
  calculateStats,
  calculateExpToNextLevel,
  Rarity,
  RARITY_STARS,
} from '@/types/growth';
import { BattleCharacter } from '@/types/game';
import { ALL_CHARACTERS } from '@/data/characters';

/** 初始玩家数据 */
function createInitialPlayerData(): PlayerData {
  return {
    name: '勇者',
    level: 1,
    exp: 0,
    expToNext: 100,
    resources: {
      gold: 10000,
      gems: 1000,
      exp: 0,
      summonTickets: 10,
      energy: 100,
      maxEnergy: 100,
      lastEnergyUpdate: Date.now(),
    },
    characters: [],
    team: [],
    completedStages: [],
    dailyTasks: createDefaultDailyTasks(),
    lastLoginDate: new Date().toISOString().split('T')[0],
    totalPlayDays: 1,
  };
}

/** 默认每日任务 */
function createDefaultDailyTasks(): DailyTask[] {
  return [
    {
      id: 'daily-login',
      name: '每日签到',
      description: '登录游戏',
      target: 1,
      progress: 1,
      rewards: { gold: 500, gems: 50 },
      completed: true,
      claimed: false,
    },
    {
      id: 'daily-battle',
      name: '每日战斗',
      description: '完成3次战斗',
      target: 3,
      progress: 0,
      rewards: { gold: 300, exp: 100 },
      completed: false,
      claimed: false,
    },
    {
      id: 'daily-summon',
      name: '每日召唤',
      description: '进行1次召唤',
      target: 1,
      progress: 0,
      rewards: { gold: 200, gems: 20 },
      completed: false,
      claimed: false,
    },
    {
      id: 'daily-levelup',
      name: '强化角色',
      description: '强化任意角色1次',
      target: 1,
      progress: 0,
      rewards: { gold: 400, exp: 50 },
      completed: false,
      claimed: false,
    },
  ];
}

/** 角色稀有度映射 */
const CHARACTER_RARITY: Record<string, Rarity> = {
  'zhuge-liang': 'legendary',
  'napoleon': 'legendary',
  'arthur': 'epic',
  'wu-zetian': 'epic',
  'hua-mulan': 'rare',
  'caesar': 'rare',
};

const STORAGE_KEY = 'history_heroes_game_data';

export function usePlayerData() {
  const [playerData, setPlayerData] = useState<PlayerData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 初始化/加载数据
  useEffect(() => {
    const savedData = localStorage.getItem(STORAGE_KEY);
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData) as PlayerData;
        // 恢复体力
        const now = Date.now();
        const hoursPassed = (now - parsed.resources.lastEnergyUpdate) / (1000 * 60 * 60);
        const energyToRecover = Math.min(
          Math.floor(hoursPassed * 10), // 每小时恢复10点
          parsed.resources.maxEnergy - parsed.resources.energy
        );
        parsed.resources.energy = Math.min(
          parsed.resources.maxEnergy,
          parsed.resources.energy + energyToRecover
        );
        parsed.resources.lastEnergyUpdate = now;
        
        // 检查每日任务重置
        const today = new Date().toISOString().split('T')[0];
        if (parsed.lastLoginDate !== today) {
          parsed.dailyTasks = createDefaultDailyTasks();
          parsed.lastLoginDate = today;
          parsed.totalPlayDays += 1;
        }
        
        setPlayerData(parsed);
      } catch {
        setPlayerData(createInitialPlayerData());
      }
    } else {
      setPlayerData(createInitialPlayerData());
    }
    setIsLoading(false);
  }, []);

  // 保存数据
  useEffect(() => {
    if (playerData) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(playerData));
    }
  }, [playerData]);

  /** 重置游戏数据 */
  const resetData = useCallback(() => {
    const newData = createInitialPlayerData();
    setPlayerData(newData);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newData));
  }, []);

  /** 添加资源 */
  const addResources = useCallback((resources: Partial<PlayerResources>) => {
    setPlayerData((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        resources: {
          ...prev.resources,
          gold: prev.resources.gold + (resources.gold || 0),
          gems: prev.resources.gems + (resources.gems || 0),
          exp: prev.resources.exp + (resources.exp || 0),
          summonTickets: prev.resources.summonTickets + (resources.summonTickets || 0),
        },
      };
    });
  }, []);

  /** 消耗资源 */
  const spendResources = useCallback((resources: Partial<PlayerResources>): boolean => {
    let success = true;
    setPlayerData((prev) => {
      if (!prev) return null;
      
      if (resources.gold && prev.resources.gold < resources.gold) success = false;
      if (resources.gems && prev.resources.gems < resources.gems) success = false;
      if (resources.energy && prev.resources.energy < resources.energy) success = false;
      if (resources.summonTickets && prev.resources.summonTickets < resources.summonTickets) success = false;
      
      if (!success) return prev;
      
      return {
        ...prev,
        resources: {
          ...prev.resources,
          gold: prev.resources.gold - (resources.gold || 0),
          gems: prev.resources.gems - (resources.gems || 0),
          energy: prev.resources.energy - (resources.energy || 0),
          summonTickets: prev.resources.summonTickets - (resources.summonTickets || 0),
        },
      };
    });
    return success;
  }, []);

  /** 检查是否拥有角色 */
  const hasCharacter = useCallback((characterId: string): boolean => {
    return playerData?.characters.some((c) => c.characterId === characterId) ?? false;
  }, [playerData]);

  /** 获取拥有角色 */
  const getOwnedCharacter = useCallback((instanceId: string): OwnedCharacter | undefined => {
    return playerData?.characters.find((c) => c.id === instanceId);
  }, [playerData]);

  /** 获得新角色 */
  const obtainCharacter = useCallback((characterId: string): { instanceId: string; isNew: boolean } => {
    const template = ALL_CHARACTERS.find((c) => c.id === characterId);
    if (!template) throw new Error('角色不存在');

    const existing = playerData?.characters.find((c) => c.characterId === characterId);
    
    if (existing) {
      // 已拥有，增加碎片
      setPlayerData((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          characters: prev.characters.map((c) =>
            c.characterId === characterId
              ? { ...c, growth: { ...c.growth, copies: c.growth.copies + 30 } }
              : c
          ),
        };
      });
      return { instanceId: existing.id, isNew: false };
    }

    // 新角色
    const newInstance: OwnedCharacter = {
      id: `owned_${characterId}_${Date.now()}`,
      characterId,
      growth: {
        level: 1,
        maxLevel: 30,
        exp: 0,
        expToNext: calculateExpToNextLevel(1),
        stars: RARITY_STARS[CHARACTER_RARITY[characterId] || 'rare'],
        breakthrough: 0,
        skillLevels: {},
        bondLevel: 1,
        bondExp: 0,
        obtainedAt: Date.now(),
        copies: 0,
      },
      isFavorite: false,
      isInTeam: false,
    };

    setPlayerData((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        characters: [...prev.characters, newInstance],
      };
    });

    return { instanceId: newInstance.id, isNew: true };
  }, [playerData]);

  /** 角色升级 */
  const levelUpCharacter = useCallback((instanceId: string): { success: boolean; newLevel?: number } => {
    const cost = 500; // 升级金币消耗
    
    setPlayerData((prev) => {
      if (!prev) return null;
      
      const character = prev.characters.find((c) => c.id === instanceId);
      if (!character || character.growth.level >= character.growth.maxLevel) return null;
      if (prev.resources.gold < cost) return null;

      const newLevel = character.growth.level + 1;
      const newExp = 0;
      const newExpToNext = calculateExpToNextLevel(newLevel);

      return {
        ...prev,
        resources: {
          ...prev.resources,
          gold: prev.resources.gold - cost,
        },
        characters: prev.characters.map((c) =>
          c.id === instanceId
            ? {
                ...c,
                growth: {
                  ...c.growth,
                  level: newLevel,
                  exp: newExp,
                  expToNext: newExpToNext,
                },
              }
            : c
        ),
      };
    });

    return { success: true };
  }, []);

  /** 角色突破 */
  const breakthroughCharacter = useCallback((instanceId: string): boolean => {
    setPlayerData((prev) => {
      if (!prev) return null;

      const character = prev.characters.find((c) => c.id === instanceId);
      if (!character || character.growth.breakthrough >= 5) return null;

      const cost = {
        gold: 10000 * (character.growth.breakthrough + 1),
        shards: 50 * (character.growth.breakthrough + 1),
      };

      if (prev.resources.gold < cost.gold || character.growth.copies < cost.shards) return null;

      return {
        ...prev,
        resources: {
          ...prev.resources,
          gold: prev.resources.gold - cost.gold,
        },
        characters: prev.characters.map((c) =>
          c.id === instanceId
            ? {
                ...c,
                growth: {
                  ...c.growth,
                  breakthrough: c.growth.breakthrough + 1,
                  maxLevel: c.growth.maxLevel + 10,
                  copies: c.growth.copies - cost.shards,
                },
              }
            : c
        ),
      };
    });

    return true;
  }, []);

  /** 设置队伍 */
  const setTeam = useCallback((characterIds: string[]) => {
    setPlayerData((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        team: characterIds.slice(0, 4), // 最多4人队伍
        characters: prev.characters.map((c) => ({
          ...c,
          isInTeam: characterIds.includes(c.id),
        })),
      };
    });
  }, []);

  /** 获取战斗角色（应用养成属性） */
  const getBattleCharacter = useCallback((instanceId: string): BattleCharacter | null => {
    const owned = playerData?.characters.find((c) => c.id === instanceId);
    if (!owned) return null;

    const template = ALL_CHARACTERS.find((c) => c.id === owned.characterId);
    if (!template) return null;

    const calculatedStats = calculateStats(
      {
        hp: template.stats.hp,
        attack: template.stats.attack,
        defense: template.stats.defense,
        speed: template.stats.speed,
      },
      owned.growth.level,
      owned.growth.stars,
      owned.growth.breakthrough
    );

    return {
      ...template,
      id: instanceId,
      stats: {
        ...calculatedStats,
        maxHp: calculatedStats.hp,
        specialAttack: Math.floor(template.stats.specialAttack * (1 + owned.growth.level * 0.03)),
        specialDefense: Math.floor(template.stats.specialDefense * (1 + owned.growth.level * 0.03)),
        critRate: template.stats.critRate + owned.growth.stars * 2,
        critDamage: template.stats.critDamage + owned.growth.breakthrough * 0.1,
      },
      currentStats: {
        ...calculatedStats,
        maxHp: calculatedStats.hp,
        specialAttack: Math.floor(template.stats.specialAttack * (1 + owned.growth.level * 0.03)),
        specialDefense: Math.floor(template.stats.specialDefense * (1 + owned.growth.level * 0.03)),
        critRate: template.stats.critRate + owned.growth.stars * 2,
        critDamage: template.stats.critDamage + owned.growth.breakthrough * 0.1,
      },
      level: owned.growth.level,
    };
  }, [playerData]);

  /** 完成关卡 */
  const completeStage = useCallback((stageId: string, rewards: { gold: number; gems: number; exp: number }) => {
    setPlayerData((prev) => {
      if (!prev) return null;
      
      const isFirstClear = !prev.completedStages.includes(stageId);
      
      return {
        ...prev,
        completedStages: isFirstClear
          ? [...prev.completedStages, stageId]
          : prev.completedStages,
        resources: {
          ...prev.resources,
          gold: prev.resources.gold + rewards.gold * (isFirstClear ? 2 : 1),
          gems: prev.resources.gems + rewards.gems * (isFirstClear ? 2 : 1),
          exp: prev.resources.exp + rewards.exp,
        },
      };
    });
  }, []);

  /** 更新每日任务进度 */
  const updateDailyTask = useCallback((taskId: string, progress: number) => {
    setPlayerData((prev) => {
      if (!prev) return null;
      
      return {
        ...prev,
        dailyTasks: prev.dailyTasks.map((task) =>
          task.id === taskId
            ? {
                ...task,
                progress: Math.min(task.progress + progress, task.target),
                completed: task.progress + progress >= task.target,
              }
            : task
        ),
      };
    });
  }, []);

  /** 领取每日任务奖励 */
  const claimDailyReward = useCallback((taskId: string) => {
    setPlayerData((prev) => {
      if (!prev) return null;
      
      const task = prev.dailyTasks.find((t) => t.id === taskId);
      if (!task || !task.completed || task.claimed) return prev;

      return {
        ...prev,
        resources: {
          ...prev.resources,
          gold: prev.resources.gold + (task.rewards.gold || 0),
          gems: prev.resources.gems + (task.rewards.gems || 0),
          exp: prev.resources.exp + (task.rewards.exp || 0),
        },
        dailyTasks: prev.dailyTasks.map((t) =>
          t.id === taskId ? { ...t, claimed: true } : t
        ),
      };
    });
  }, []);

  return {
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
  };
}
