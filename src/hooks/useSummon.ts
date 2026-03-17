'use client';

import { useState, useCallback } from 'react';
import { Rarity, RARITY_WEIGHTS, RARITY_NAMES, RARITY_COLORS, RARITY_STARS } from '@/types/growth';
import { ALL_CHARACTERS } from '@/data/characters';

interface UseSummonProps {
  onObtainCharacter: (characterId: string) => Promise<any>;
  spendResources: (resources: { gems?: number; summonTickets?: number }) => Promise<boolean>;
  updateDailyTask: (taskId: string, progress?: number) => Promise<void>;
  hasCharacter: (characterId: string) => boolean;
}

interface SummonResult {
  characterId: string;
  name: string;
  rarity: Rarity;
  avatar: string;
  isNew: boolean;
  stars: number;
}

export function useSummon({
  onObtainCharacter,
  spendResources,
  updateDailyTask,
  hasCharacter,
}: UseSummonProps) {
  const [isSummoning, setIsSummoning] = useState(false);
  const [results, setResults] = useState<SummonResult[]>([]);
  const [pity, setPity] = useState(0);
  const [legendaryPity, setLegendaryPity] = useState(0);
  const [history, setHistory] = useState<SummonResult[]>([]);

  /** 获取随机稀有度 */
  const getRandomRarity = useCallback((currentPity: number, currentLegendaryPity: number): Rarity => {
    // 保底检查
    if (currentLegendaryPity >= 99) return 'legendary';
    if (currentPity >= 49) return 'epic';

    const roll = Math.random() * 100;
    
    if (roll < RARITY_WEIGHTS.legendary) return 'legendary';
    if (roll < RARITY_WEIGHTS.legendary + RARITY_WEIGHTS.epic) return 'epic';
    if (roll < RARITY_WEIGHTS.legendary + RARITY_WEIGHTS.epic + RARITY_WEIGHTS.rare) return 'rare';
    return 'common';
  }, []);

  /** 获取随机角色 */
  const getRandomCharacter = useCallback((rarity: Rarity) => {
    const charactersOfRarity = ALL_CHARACTERS.filter((c) => {
      const charRarity = getCharacterRarity(c.id);
      return charRarity === rarity;
    });
    
    if (charactersOfRarity.length === 0) {
      // 如果该稀有度没有角色，返回一个随机角色
      return ALL_CHARACTERS[Math.floor(Math.random() * ALL_CHARACTERS.length)];
    }
    
    return charactersOfRarity[Math.floor(Math.random() * charactersOfRarity.length)];
  }, []);

  /** 执行单次召唤 */
  const performSummon = useCallback(async (
    currentPity: number,
    currentLegendaryPity: number
  ): Promise<{ result: SummonResult; newPity: number; newLegendaryPity: number }> => {
    const rarity = getRandomRarity(currentPity, currentLegendaryPity);
    const character = getRandomCharacter(rarity);
    const isNew = !hasCharacter(character.id);
    
    // 调用数据库添加角色
    const dbResult = await onObtainCharacter(character.id);
    
    const stars = dbResult?.stars || (rarity === 'legendary' ? 2 : rarity === 'epic' ? 1 : 1);
    
    const result: SummonResult = {
      characterId: character.id,
      name: character.name,
      rarity,
      avatar: character.avatar,
      isNew,
      stars,
    };

    // 更新保底计数
    let newPity = currentPity + 1;
    let newLegendaryPity = currentLegendaryPity + 1;
    
    if (rarity === 'legendary') {
      newLegendaryPity = 0;
      newPity = 0;
    } else if (rarity === 'epic') {
      newPity = 0;
    }

    return { result, newPity, newLegendaryPity };
  }, [getRandomRarity, getRandomCharacter, hasCharacter, onObtainCharacter]);

  /** 单抽 */
  const summonOnce = useCallback(async () => {
    if (isSummoning) return null;
    
    const success = await spendResources({ gems: 100 });
    if (!success) return null;

    setIsSummoning(true);
    try {
      const { result, newPity, newLegendaryPity } = await performSummon(pity, legendaryPity);
      
      setResults([result]);
      setPity(newPity);
      setLegendaryPity(newLegendaryPity);
      setHistory((prev) => [result, ...prev.slice(0, 19)]);
      
      await updateDailyTask('daily-summon', 1);
      
      return result;
    } finally {
      setIsSummoning(false);
    }
  }, [isSummoning, pity, legendaryPity, performSummon, spendResources, updateDailyTask]);

  /** 十连 */
  const summonTen = useCallback(async () => {
    if (isSummoning) return [];
    
    const success = await spendResources({ gems: 900 });
    if (!success) return [];

    setIsSummoning(true);
    try {
      const newResults: SummonResult[] = [];
      let currentPity = pity;
      let currentLegendaryPity = legendaryPity;

      for (let i = 0; i < 10; i++) {
        const { result, newPity, newLegendaryPity } = await performSummon(currentPity, currentLegendaryPity);
        newResults.push(result);
        currentPity = newPity;
        currentLegendaryPity = newLegendaryPity;
      }

      setResults(newResults);
      setPity(currentPity);
      setLegendaryPity(currentLegendaryPity);
      setHistory((prev) => [...newResults.reverse(), ...prev.slice(0, 10)]);
      
      await updateDailyTask('daily-summon', 1);
      
      return newResults;
    } finally {
      setIsSummoning(false);
    }
  }, [isSummoning, pity, legendaryPity, performSummon, spendResources, updateDailyTask]);

  /** 使用召唤券 */
  const summonWithTicket = useCallback(async () => {
    if (isSummoning) return null;
    
    const success = await spendResources({ summonTickets: 1 });
    if (!success) return null;

    setIsSummoning(true);
    try {
      const { result, newPity, newLegendaryPity } = await performSummon(pity, legendaryPity);
      
      setResults([result]);
      setPity(newPity);
      setLegendaryPity(newLegendaryPity);
      setHistory((prev) => [result, ...prev.slice(0, 19)]);
      
      await updateDailyTask('daily-summon', 1);
      
      return result;
    } finally {
      setIsSummoning(false);
    }
  }, [isSummoning, pity, legendaryPity, performSummon, spendResources, updateDailyTask]);

  return {
    summonOnce,
    summonTen,
    summonWithTicket,
    isSummoning,
    results,
    pity,
    legendaryPity,
    history,
    setResults,
  };
}

/** 获取角色稀有度 */
function getCharacterRarity(characterId: string): Rarity {
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
