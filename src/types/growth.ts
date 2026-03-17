// 养成系统类型定义

/** 稀有度 */
export type Rarity = 'common' | 'rare' | 'epic' | 'legendary';

/** 稀有度名称 */
export const RARITY_NAMES: Record<Rarity, string> = {
  common: '普通',
  rare: '稀有',
  epic: '史诗',
  legendary: '传说',
};

/** 稀有度颜色 */
export const RARITY_COLORS: Record<Rarity, string> = {
  common: '#9ca3af',
  rare: '#3b82f6',
  epic: '#a855f7',
  legendary: '#f59e0b',
};

/** 稀有度星星数量 */
export const RARITY_STARS: Record<Rarity, number> = {
  common: 1,
  rare: 2,
  epic: 3,
  legendary: 4,
};

/** 玩家资源 */
export interface PlayerResources {
  gold: number; // 金币
  gems: number; // 钻石
  exp: number; // 经验值
  summonTickets: number; // 召唤券
  energy: number; // 体力
  maxEnergy: number; // 最大体力
  lastEnergyUpdate: number; // 上次体力更新时间
}

/** 角色养成数据 */
export interface CharacterGrowth {
  level: number; // 当前等级
  maxLevel: number; // 最大等级（突破可提升）
  exp: number; // 当前经验
  expToNext: number; // 升级所需经验
  stars: number; // 星级（0-5）
  breakthrough: number; // 突破次数
  skillLevels: Record<string, number>; // 技能等级
  bondLevel: number; // 羁绊等级
  bondExp: number; // 羁绊经验
  obtainedAt: number; // 获得时间戳
  copies: number; // 拥有碎片/复制品数量
}

/** 玩家拥有的角色 */
export interface OwnedCharacter {
  id: string;
  characterId: string; // 对应模板角色ID
  growth: CharacterGrowth;
  isFavorite: boolean; // 是否收藏
  isInTeam: boolean; // 是否在队伍中
}

/** 玩家数据 */
export interface PlayerData {
  name: string;
  level: number;
  exp: number;
  expToNext: number;
  resources: PlayerResources;
  characters: OwnedCharacter[];
  team: string[]; // 出战队伍（角色实例ID）
  completedStages: string[]; // 已通关关卡
  dailyTasks: DailyTask[];
  lastLoginDate: string;
  totalPlayDays: number;
}

/** 每日任务 */
export interface DailyTask {
  id: string;
  name: string;
  description: string;
  target: number;
  progress: number;
  rewards: TaskReward;
  completed: boolean;
  claimed: boolean;
}

/** 任务奖励 */
export interface TaskReward {
  gold?: number;
  gems?: number;
  exp?: number;
  items?: string[];
}

/** 关卡配置 */
export interface Stage {
  id: string;
  chapterId: string;
  name: string;
  description: string;
  difficulty: 'easy' | 'normal' | 'hard' | 'hell';
  enemyIds: string[]; // 敌人角色ID列表
  enemyLevels: number[];
  energyCost: number;
  recommendedLevel: number;
  rewards: StageReward;
  firstClearRewards: StageReward;
}

/** 关卡奖励 */
export interface StageReward {
  gold: number;
  exp: number;
  gems?: number;
  characterShards?: string[]; // 角色碎片
  items?: string[];
}

/** 章节 */
export interface Chapter {
  id: string;
  name: string;
  description: string;
  stages: Stage[];
  unlocked: boolean;
}

/** 抽卡结果 */
export interface SummonResult {
  characterId: string;
  rarity: Rarity;
  isNew: boolean;
  shards: number; // 如果已拥有，返回碎片
}

/** 升级结果 */
export interface LevelUpResult {
  success: boolean;
  newLevel: number;
  statsGained: {
    hp: number;
    attack: number;
    defense: number;
    speed: number;
  };
}

/** 计算角色属性（基于等级和突破） */
export function calculateStats(
  baseStats: { hp: number; attack: number; defense: number; speed: number },
  level: number,
  stars: number,
  breakthrough: number
) {
  // 基础成长率
  const levelMultiplier = 1 + (level - 1) * 0.05;
  // 星级加成
  const starMultiplier = 1 + stars * 0.1;
  // 突破加成
  const breakthroughMultiplier = 1 + breakthrough * 0.15;

  return {
    hp: Math.floor(baseStats.hp * levelMultiplier * starMultiplier * breakthroughMultiplier),
    attack: Math.floor(baseStats.attack * levelMultiplier * starMultiplier * breakthroughMultiplier),
    defense: Math.floor(baseStats.defense * levelMultiplier * starMultiplier * breakthroughMultiplier),
    speed: Math.floor(baseStats.speed * levelMultiplier * starMultiplier * breakthroughMultiplier),
  };
}

/** 计算升级所需经验 */
export function calculateExpToNextLevel(level: number): number {
  return Math.floor(100 * Math.pow(1.15, level - 1));
}

/** 计算突破所需材料 */
export function calculateBreakthroughCost(breakthrough: number): { gold: number; shards: number } {
  return {
    gold: 10000 * (breakthrough + 1),
    shards: 50 * (breakthrough + 1),
  };
}
