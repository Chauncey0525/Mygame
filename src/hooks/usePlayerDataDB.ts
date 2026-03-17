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

/** 玩家ID存储键 */
const PLAYER_ID_KEY = 'history_heroes_player_id';

/** 从 localStorage 获取或创建玩家ID */
function getPlayerId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(PLAYER_ID_KEY);
}

/** 保存玩家ID到 localStorage */
function savePlayerId(id: string) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(PLAYER_ID_KEY, id);
}

/** 数据库版本的玩家数据管理 Hook */
export function usePlayerData() {
  const [playerData, setPlayerData] = useState<PlayerData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [playerId, setPlayerId] = useState<string | null>(null);

  // 初始化/加载数据
  useEffect(() => {
    const loadData = async () => {
      try {
        const storedPlayerId = getPlayerId();
        const headers: HeadersInit = {};
        
        if (storedPlayerId) {
          headers['x-player-id'] = storedPlayerId;
        }

        const response = await fetch('/api/player', { headers });
        const data = await response.json();

        if (data.error) {
          console.error('Failed to load player data:', data.error);
          setIsLoading(false);
          return;
        }

        // 保存玩家ID
        if (data.player?.id) {
          savePlayerId(data.player.id);
          setPlayerId(data.player.id);
        }

        // 转换为前端数据格式
        const formattedData: PlayerData = {
          id: data.player.id,
          name: data.player.name,
          level: data.player.level,
          exp: data.player.exp,
          expToNext: data.player.exp_to_next,
          resources: {
            gold: data.player.gold,
            gems: data.player.gems,
            exp: data.player.exp_books,
            summonTickets: data.player.summon_tickets,
            energy: data.player.energy,
            maxEnergy: data.player.max_energy,
            lastEnergyUpdate: new Date(data.player.last_energy_update).getTime(),
          },
          characters: data.characters.map((c: any) => ({
            id: c.id.toString(),
            characterId: c.character_id,
            level: c.level,
            exp: c.exp,
            stars: c.stars,
            rarity: getRarityFromCharacterId(c.character_id),
            breakthrough: c.breakthrough,
            bondLevel: c.bond_level,
            bondExp: c.bond_exp,
            obtainedAt: new Date(c.obtained_at),
          })),
          team: data.team || [],
          completedStages: data.completedStages || [],
          dailyTasks: data.dailyTasks.map((t: any) => ({
            id: t.task_id,
            name: t.name,
            description: t.description,
            target: t.target,
            progress: t.progress,
            rewards: {
              gold: t.reward_gold || 0,
              gems: t.reward_gems || 0,
              exp: t.reward_exp || 0,
            },
            completed: t.completed,
            claimed: t.claimed,
          })),
          lastLoginDate: data.player.last_login_date,
          totalPlayDays: data.player.total_play_days,
          pityCount: data.player.pity_count,
          legendaryPityCount: data.player.legendary_pity_count,
        };

        setPlayerData(formattedData);
      } catch (error) {
        console.error('Failed to load player data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  /** 更新玩家数据到数据库 */
  const updatePlayerInDB = useCallback(async (updates: Partial<PlayerData>) => {
    if (!playerId) return;

    const dbUpdates: Record<string, any> = {};
    if (updates.name) dbUpdates.name = updates.name;
    if (updates.level) dbUpdates.level = updates.level;
    if (updates.exp !== undefined) dbUpdates.exp = updates.exp;
    if (updates.expToNext) dbUpdates.exp_to_next = updates.expToNext;
    if (updates.resources) {
      if (updates.resources.gold !== undefined) dbUpdates.gold = updates.resources.gold;
      if (updates.resources.gems !== undefined) dbUpdates.gems = updates.resources.gems;
      if (updates.resources.exp !== undefined) dbUpdates.exp_books = updates.resources.exp;
      if (updates.resources.summonTickets !== undefined) dbUpdates.summon_tickets = updates.resources.summonTickets;
      if (updates.resources.energy !== undefined) dbUpdates.energy = updates.resources.energy;
      if (updates.resources.maxEnergy !== undefined) dbUpdates.max_energy = updates.resources.maxEnergy;
      if (updates.resources.lastEnergyUpdate) dbUpdates.last_energy_update = new Date(updates.resources.lastEnergyUpdate).toISOString();
    }
    if (updates.pityCount !== undefined) dbUpdates.pity_count = updates.pityCount;
    if (updates.legendaryPityCount !== undefined) dbUpdates.legendary_pity_count = updates.legendaryPityCount;

    await fetch('/api/player', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerId, updates: dbUpdates }),
    });
  }, [playerId]);

  /** 重置游戏数据 */
  const resetData = useCallback(async () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(PLAYER_ID_KEY);
    }
    setPlayerId(null);
    window.location.reload();
  }, []);

  /** 添加资源 */
  const addResources = useCallback(async (resources: Partial<PlayerResources>) => {
    if (!playerData) return;
    
    const newResources = { ...playerData.resources };
    if (resources.gold) newResources.gold += resources.gold;
    if (resources.gems) newResources.gems += resources.gems;
    if (resources.exp) newResources.exp += resources.exp;
    if (resources.summonTickets) newResources.summonTickets += resources.summonTickets;

    setPlayerData((prev) => {
      if (!prev) return null;
      return { ...prev, resources: newResources };
    });

    await updatePlayerInDB({ resources: newResources });
  }, [playerData, updatePlayerInDB]);

  /** 消耗资源 */
  const spendResources = useCallback(async (resources: Partial<PlayerResources>) => {
    if (!playerData) return false;

    // 检查资源是否足够
    if (resources.gold && playerData.resources.gold < resources.gold) return false;
    if (resources.gems && playerData.resources.gems < resources.gems) return false;
    if (resources.summonTickets && playerData.resources.summonTickets < resources.summonTickets) return false;
    if (resources.energy && playerData.resources.energy < resources.energy) return false;

    const newResources = { ...playerData.resources };
    if (resources.gold) newResources.gold -= resources.gold;
    if (resources.gems) newResources.gems -= resources.gems;
    if (resources.summonTickets) newResources.summonTickets -= resources.summonTickets;
    if (resources.energy) newResources.energy -= resources.energy;

    setPlayerData((prev) => {
      if (!prev) return null;
      return { ...prev, resources: newResources };
    });

    await updatePlayerInDB({ resources: newResources });
    return true;
  }, [playerData, updatePlayerInDB]);

  /** 检查是否拥有角色 */
  const hasCharacter = useCallback((characterId: string) => {
    if (!playerData) return false;
    return playerData.characters.some((c) => c.characterId === characterId);
  }, [playerData]);

  /** 获取拥有的角色 */
  const getOwnedCharacter = useCallback((instanceId: string) => {
    if (!playerData) return null;
    return playerData.characters.find((c) => c.id === instanceId) || null;
  }, [playerData]);

  /** 获取新角色 */
  const obtainCharacter = useCallback(async (characterId: string) => {
    if (!playerId) return null;

    const response = await fetch('/api/player/characters', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerId, characterId }),
    });

    const data = await response.json();
    if (data.error) {
      console.error('Failed to obtain character:', data.error);
      return null;
    }

    // 更新本地状态
    if (data.isNew) {
      const newCharacter: OwnedCharacter = {
        id: data.character.id.toString(),
        characterId: data.character.character_id,
        level: data.character.level,
        exp: data.character.exp,
        stars: data.character.stars,
        rarity: getRarityFromCharacterId(data.character.character_id),
        breakthrough: data.character.breakthrough,
        bondLevel: data.character.bond_level,
        bondExp: data.character.bond_exp,
        obtainedAt: new Date(data.character.obtained_at),
      };

      setPlayerData((prev) => {
        if (!prev) return null;
        return { ...prev, characters: [...prev.characters, newCharacter] };
      });
    } else {
      // 更新星级
      setPlayerData((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          characters: prev.characters.map((c) =>
            c.characterId === characterId
              ? { ...c, stars: Math.min(6, c.stars + 1) }
              : c
          ),
        };
      });
    }

    return data.character;
  }, [playerId]);

  /** 升级角色 */
  const levelUpCharacter = useCallback(async (instanceId: string, expAmount: number) => {
    if (!playerData) return false;

    const character = getOwnedCharacter(instanceId);
    if (!character) return false;

    // 检查资源
    if (playerData.resources.exp < expAmount) return false;

    // 消耗资源
    await spendResources({ exp: expAmount });

    // 计算新等级
    let newExp = character.exp + expAmount;
    let newLevel = character.level;
    let newExpToNext = calculateExpToNextLevel(newLevel);

    while (newExp >= newExpToNext && newLevel < 100) {
      newExp -= newExpToNext;
      newLevel++;
      newExpToNext = calculateExpToNextLevel(newLevel);
    }

    // 更新数据库
    await fetch('/api/player/characters', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        characterInstanceId: parseInt(instanceId),
        updates: { level: newLevel, exp: newExp },
      }),
    });

    // 更新本地状态
    setPlayerData((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        characters: prev.characters.map((c) =>
          c.id === instanceId ? { ...c, level: newLevel, exp: newExp } : c
        ),
      };
    });

    return true;
  }, [playerData, getOwnedCharacter, spendResources]);

  /** 突破角色 */
  const breakthroughCharacter = useCallback(async (instanceId: string) => {
    if (!playerData) return false;

    const character = getOwnedCharacter(instanceId);
    if (!character || character.breakthrough >= 5) return false;

    // 突破消耗 (金币 + 同角色碎片)
    const cost = (character.breakthrough + 1) * 1000;
    if (playerData.resources.gold < cost) return false;

    await spendResources({ gold: cost });

    // 更新数据库
    await fetch('/api/player/characters', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        characterInstanceId: parseInt(instanceId),
        updates: { breakthrough: character.breakthrough + 1 },
      }),
    });

    // 更新本地状态
    setPlayerData((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        characters: prev.characters.map((c) =>
          c.id === instanceId ? { ...c, breakthrough: c.breakthrough + 1 } : c
        ),
      };
    });

    return true;
  }, [playerData, getOwnedCharacter, spendResources]);

  /** 设置队伍 */
  const setTeam = useCallback(async (characterInstanceIds: string[]) => {
    if (!playerId) return;

    await fetch('/api/player/team', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerId, team: characterInstanceIds.map(Number) }),
    });

    setPlayerData((prev) => {
      if (!prev) return null;
      return { ...prev, team: characterInstanceIds };
    });
  }, [playerId]);

  /** 获取战斗角色数据 */
  const getBattleCharacter = useCallback((instanceId: string): BattleCharacter | null => {
    const owned = getOwnedCharacter(instanceId);
    if (!owned) return null;

    const template = ALL_CHARACTERS.find((c) => c.id === owned.characterId);
    if (!template) return null;

    const stats = calculateStats(template.stats, owned.level, owned.stars, owned.breakthrough);

    return {
      ...template,
      stats,
      currentStats: { ...stats },
      level: owned.level,
      statusEffects: [],
      exp: owned.exp,
    };
  }, [getOwnedCharacter]);

  /** 完成关卡 */
  const completeStage = useCallback(async (stageId: string, rewards: { gold?: number; gems?: number; exp?: number }) => {
    if (!playerId) return;

    await fetch('/api/player/stages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerId, stageId, rewards }),
    });

    // 更新本地状态
    setPlayerData((prev) => {
      if (!prev) return null;
      const newCompletedStages = prev.completedStages.includes(stageId)
        ? prev.completedStages
        : [...prev.completedStages, stageId];
      const newResources = { ...prev.resources };
      if (rewards.gold) newResources.gold += rewards.gold;
      if (rewards.gems) newResources.gems += rewards.gems;
      if (rewards.exp) newResources.exp += rewards.exp;
      return { ...prev, completedStages: newCompletedStages, resources: newResources };
    });
  }, [playerId]);

  /** 更新每日任务 */
  const updateDailyTask = useCallback(async (taskId: string, progress: number = 1) => {
    if (!playerId) return;

    await fetch('/api/player/daily-tasks', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerId, taskId, progress }),
    });

    setPlayerData((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        dailyTasks: prev.dailyTasks.map((t) =>
          t.id === taskId
            ? { ...t, progress: Math.min(t.progress + progress, t.target), completed: t.progress + progress >= t.target }
            : t
        ),
      };
    });
  }, [playerId]);

  /** 领取每日任务奖励 */
  const claimDailyReward = useCallback(async (taskId: string) => {
    if (!playerId) return;

    const response = await fetch('/api/player/daily-tasks/claim', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ playerId, taskId }),
    });

    const data = await response.json();
    if (data.success && data.rewards) {
      setPlayerData((prev) => {
        if (!prev) return null;
        const newResources = { ...prev.resources };
        if (data.rewards.gold) newResources.gold += data.rewards.gold;
        if (data.rewards.gems) newResources.gems += data.rewards.gems;
        return {
          ...prev,
          resources: newResources,
          dailyTasks: prev.dailyTasks.map((t) =>
            t.id === taskId ? { ...t, claimed: true } : t
          ),
        };
      });
    }
  }, [playerId]);

  return {
    playerData,
    playerId,
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
    updatePlayerInDB,
  };
}

/** 根据角色ID获取稀有度 */
function getRarityFromCharacterId(characterId: string): Rarity {
  const CHARACTER_RARITY: Record<string, Rarity> = {
    'zhuge-liang': 'legendary',
    'napoleon': 'legendary',
    'arthur': 'epic',
    'wu-zetian': 'epic',
    'hua-mulan': 'rare',
    'caesar': 'rare',
  };
  return CHARACTER_RARITY[characterId] || 'common';
}
