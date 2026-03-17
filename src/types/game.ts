// 游戏核心类型定义

/** 元素属性 - 类似宝可梦的属性系统 */
export type Element = 'fire' | 'water' | 'earth' | 'wind' | 'light' | 'dark' | 'neutral';

/** 角色定位 */
export type RoleType = 'warrior' | 'mage' | 'assassin' | 'tank' | 'support' | 'ranger';

/** 技能类型 */
export type SkillType = 'attack' | 'defense' | 'buff' | 'debuff' | 'heal' | 'special';

/** 技能定义 */
export interface Skill {
  id: string;
  name: string;
  nameEn: string;
  description: string;
  type: SkillType;
  element: Element;
  power: number; // 技能威力 0-200
  accuracy: number; // 命中率 0-100
  pp: number; // 技能点数
  maxPp: number;
  effect?: {
    type: 'burn' | 'freeze' | 'poison' | 'stun' | 'heal' | 'buff_attack' | 'buff_defense' | 'debuff_attack' | 'debuff_defense';
    chance: number; // 触发概率 0-100
    value: number; // 效果数值
    duration: number; // 持续回合
  };
}

/** 角色属性 */
export interface CharacterStats {
  hp: number;
  maxHp: number;
  attack: number;
  defense: number;
  specialAttack: number;
  specialDefense: number;
  speed: number;
  critRate: number; // 暴击率
  critDamage: number; // 暴击伤害倍率
}

/** 技能效果类型（包含即时效果） */
export type EffectType = 'burn' | 'freeze' | 'poison' | 'stun' | 'heal' | 'buff_attack' | 'buff_defense' | 'debuff_attack' | 'debuff_defense';

/** 状态效果 */
export interface StatusEffect {
  type: 'burn' | 'freeze' | 'poison' | 'stun' | 'buff_attack' | 'buff_defense' | 'debuff_attack' | 'debuff_defense';
  value: number;
  duration: number;
}

/** 战斗中的角色 */
export interface BattleCharacter {
  id: string;
  name: string;
  nameEn: string;
  title: string; // 称号 如 "卧龙先生"
  era: string; // 时代
  origin: string; // 出处/国家
  element: Element;
  roleType: RoleType;
  description: string;
  avatar: string; // 头像URL
  illustration: string; // 立绘URL
  stats: CharacterStats;
  skills: Skill[];
  currentStats: CharacterStats; // 战斗中实时属性
  statusEffects: StatusEffect[];
  level: number;
  exp: number;
}

/** 玩家角色（包含养成数据） */
export interface PlayerCharacter extends BattleCharacter {
  obtainedAt: Date;
  bondLevel: number; // 羁绊等级
  bondExp: number;
}

/** 战斗动作 */
export interface BattleAction {
  type: 'skill' | 'item' | 'flee';
  actorId: string;
  targetId: string;
  skillId?: string;
  itemId?: string;
}

/** 战斗结果 */
export interface BattleResult {
  attackerId: string;
  defenderId: string;
  skillUsed: Skill;
  damage: number;
  isCritical: boolean;
  isEffective: boolean; // 是否属性克制
  isMiss: boolean;
  effectsApplied: Array<{ type: EffectType; value: number; duration: number }>;
  remainingHp: number;
}

/** 战斗状态 */
export interface BattleState {
  phase: 'select' | 'execute' | 'result' | 'end';
  turn: number;
  currentTurnId: string; // 当前行动角色ID
  player: BattleCharacter;
  enemy: BattleCharacter;
  actions: BattleAction[];
  results: BattleResult[];
  logs: BattleLog[];
  winner: 'player' | 'enemy' | null;
}

/** 战斗日志 */
export interface BattleLog {
  turn: number;
  message: string;
  type: 'info' | 'damage' | 'heal' | 'effect' | 'critical' | 'miss';
}

/** 元素克制关系 */
export const ELEMENT_ADVANTAGE: Record<Element, Element[]> = {
  fire: ['wind', 'earth'],
  water: ['fire', 'light'],
  earth: ['water', 'dark'],
  wind: ['earth', 'light'],
  light: ['dark'],
  dark: ['light', 'fire'],
  neutral: [],
};

/** 元素被克制关系 */
export const ELEMENT_DISADVANTAGE: Record<Element, Element[]> = {
  fire: ['water', 'dark'],
  water: ['earth', 'wind'],
  earth: ['fire', 'wind'],
  wind: ['fire', 'water'],
  light: ['water', 'wind'],
  dark: ['light', 'earth'],
  neutral: [],
};

/** 元素中文名称 */
export const ELEMENT_NAMES: Record<Element, string> = {
  fire: '火',
  water: '水',
  earth: '土',
  wind: '风',
  light: '光',
  dark: '暗',
  neutral: '无',
};

/** 元素颜色 */
export const ELEMENT_COLORS: Record<Element, string> = {
  fire: '#ef4444',
  water: '#3b82f6',
  earth: '#a16207',
  wind: '#22c55e',
  light: '#fbbf24',
  dark: '#6b21a8',
  neutral: '#6b7280',
};

/** 角色定位中文名称 */
export const ROLE_NAMES: Record<RoleType, string> = {
  warrior: '战士',
  mage: '法师',
  assassin: '刺客',
  tank: '坦克',
  support: '辅助',
  ranger: '射手',
};
