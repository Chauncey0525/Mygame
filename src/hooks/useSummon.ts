'use client';

import { useState, useCallback } from 'react';
import { Rarity, SummonResult, RARITY_NAMES, RARITY_COLORS } from '@/types/growth';
import { ALL_CHARACTERS } from '@/data/characters';

/** 角色稀有度映射 */
const CHARACTER_RARITY: Record<string, Rarity> = {
  'zhuge-liang': 'legendary',
  'napoleon': 'legendary',
  'arthur': 'epic',
  'wu-zetian': 'epic',
  'hua-mulan': 'rare',
  'caesar': 'rare',
};

/** 抽卡概率 */
const SUMMON_RATES: Record<Rarity, number> = {
  common: 0,
  rare: 0.60,
  epic: 0.30,
  legendary: 0.10,
};

/** 保底机制 */
const PITY_THRESHOLD = 50; // 50抽必出史诗
const LEGENDARY_PITY = 100; // 100抽必出传说

interface UseSummonOptions {
  onObtainCharacter: (characterId: string) => { instanceId: string; isNew: boolean };
  spendResources: (resources: { gems?: number; summonTickets?: number }) => boolean;
  updateDailyTask: (taskId: string, progress: number) => void;
  hasCharacter: (characterId: string) => boolean;
}

interface SummonState {
  pity: number; // 当前抽卡次数（用于保底）
  legendaryPity: number; // 传说保底计数
  lastRarity: Rarity | null;
  history: SummonResult[];
}

export function useSummon(options: UseSummonOptions) {
  const { onObtainCharacter, spendResources, updateDailyTask, hasCharacter } = options;

  const [state, setState] = useState<SummonState>({
    pity: 0,
    legendaryPity: 0,
    lastRarity: null,
    history: [],
  });

  const [isSummoning, setIsSummoning] = useState(false);

  /** 单抽 */
  const summonOnce = useCallback((): SummonResult | null => {
    if (!spendResources({ gems: 150 })) {
      return null;
    }

    setIsSummoning(true);

    // 更新每日任务
    updateDailyTask('daily-summon', 1);

    const result = performSummon(state.pity, state.legendaryPity, hasCharacter);

    setState((prev) => ({
      ...prev,
      pity: result.rarity === 'epic' ? 0 : prev.pity + 1,
      legendaryPity: result.rarity === 'legendary' ? 0 : prev.legendaryPity + 1,
      lastRarity: result.rarity,
      history: [result, ...prev.history].slice(0, 50),
    }));

    // 获得角色
    const obtainResult = onObtainCharacter(result.characterId);
    result.isNew = obtainResult.isNew;

    setTimeout(() => setIsSummoning(false), 500);

    return result;
  }, [state.pity, state.legendaryPity, spendResources, updateDailyTask, hasCharacter, onObtainCharacter]);

  /** 十连抽 */
  const summonTen = useCallback((): SummonResult[] => {
    if (!spendResources({ gems: 1350 })) { // 10连9折
      return [];
    }

    setIsSummoning(true);

    // 更新每日任务
    updateDailyTask('daily-summon', 10);

    const results: SummonResult[] = [];
    let currentPity = state.pity;
    let currentLegendaryPity = state.legendaryPity;

    for (let i = 0; i < 10; i++) {
      const result = performSummon(currentPity, currentLegendaryPity, hasCharacter);
      results.push(result);

      if (result.rarity === 'epic') {
        currentPity = 0;
      } else {
        currentPity++;
      }

      if (result.rarity === 'legendary') {
        currentLegendaryPity = 0;
      } else {
        currentLegendaryPity++;
      }

      // 获得角色
      const obtainResult = onObtainCharacter(result.characterId);
      result.isNew = obtainResult.isNew;
    }

    setState((prev) => ({
      ...prev,
      pity: currentPity,
      legendaryPity: currentLegendaryPity,
      lastRarity: results[results.length - 1].rarity,
      history: [...results.reverse(), ...prev.history].slice(0, 50),
    }));

    setTimeout(() => setIsSummoning(false), 1500);

    return results;
  }, [state.pity, state.legendaryPity, spendResources, updateDailyTask, hasCharacter, onObtainCharacter]);

  /** 使用召唤券 */
  const summonWithTicket = useCallback((): SummonResult | null => {
    if (!spendResources({ summonTickets: 1 })) {
      return null;
    }

    setIsSummoning(true);

    const result = performSummon(state.pity, state.legendaryPity, hasCharacter);

    setState((prev) => ({
      ...prev,
      pity: result.rarity === 'epic' ? 0 : prev.pity + 1,
      legendaryPity: result.rarity === 'legendary' ? 0 : prev.legendaryPity + 1,
      lastRarity: result.rarity,
      history: [result, ...prev.history].slice(0, 50),
    }));

    const obtainResult = onObtainCharacter(result.characterId);
    result.isNew = obtainResult.isNew;

    setTimeout(() => setIsSummoning(false), 500);

    return result;
  }, [state.pity, state.legendaryPity, spendResources, hasCharacter, onObtainCharacter]);

  return {
    summonOnce,
    summonTen,
    summonWithTicket,
    isSummoning,
    pity: state.pity,
    legendaryPity: state.legendaryPity,
    history: state.history,
  };
}

/** 执行抽卡 */
function performSummon(
  currentPity: number,
  legendaryPity: number,
  hasCharacter: (id: string) => boolean
): SummonResult {
  let rarity: Rarity;

  // 检查传说保底
  if (legendaryPity >= LEGENDARY_PITY - 1) {
    rarity = 'legendary';
  }
  // 检查史诗保底
  else if (currentPity >= PITY_THRESHOLD - 1) {
    rarity = 'epic';
  }
  // 正常概率
  else {
    const roll = Math.random();
    if (roll < SUMMON_RATES.legendary) {
      rarity = 'legendary';
    } else if (roll < SUMMON_RATES.legendary + SUMMON_RATES.epic) {
      rarity = 'epic';
    } else {
      rarity = 'rare';
    }
  }

  // 根据稀有度选择角色
  const candidates = ALL_CHARACTERS.filter((c) => CHARACTER_RARITY[c.id] === rarity);
  const selected = candidates[Math.floor(Math.random() * candidates.length)];

  return {
    characterId: selected.id,
    rarity,
    isNew: !hasCharacter(selected.id),
    shards: hasCharacter(selected.id) ? 30 : 0,
  };
}

/** 获取角色稀有度 */
export function getCharacterRarity(characterId: string): Rarity {
  return CHARACTER_RARITY[characterId] || 'rare';
}
