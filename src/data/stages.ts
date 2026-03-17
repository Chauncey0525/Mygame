import { Stage, Chapter } from '@/types/growth';

/** 关卡配置 */
export const CHAPTERS: Chapter[] = [
  {
    id: 'chapter-1',
    name: '初入乱世',
    description: '历史的大门缓缓打开，英雄们的故事即将开始...',
    unlocked: true,
    stages: [
      {
        id: 'stage-1-1',
        chapterId: 'chapter-1',
        name: '新手试炼',
        description: '与神秘战士进行首次对决',
        difficulty: 'easy',
        enemyIds: ['hua-mulan'],
        enemyLevels: [1],
        energyCost: 5,
        recommendedLevel: 1,
        rewards: {
          gold: 100,
          exp: 50,
        },
        firstClearRewards: {
          gold: 500,
          exp: 200,
          gems: 50,
        },
      },
      {
        id: 'stage-1-2',
        chapterId: 'chapter-1',
        name: '初露锋芒',
        description: '证明你的实力',
        difficulty: 'easy',
        enemyIds: ['caesar'],
        enemyLevels: [3],
        energyCost: 5,
        recommendedLevel: 3,
        rewards: {
          gold: 150,
          exp: 80,
        },
        firstClearRewards: {
          gold: 600,
          exp: 300,
          gems: 50,
        },
      },
      {
        id: 'stage-1-3',
        chapterId: 'chapter-1',
        name: '勇者之路',
        description: '挑战更强的对手',
        difficulty: 'normal',
        enemyIds: ['arthur'],
        enemyLevels: [5],
        energyCost: 8,
        recommendedLevel: 5,
        rewards: {
          gold: 200,
          exp: 100,
        },
        firstClearRewards: {
          gold: 800,
          exp: 400,
          gems: 100,
        },
      },
    ],
  },
  {
    id: 'chapter-2',
    name: '群雄逐鹿',
    description: '更强的对手出现了，准备好迎接挑战了吗？',
    unlocked: false,
    stages: [
      {
        id: 'stage-2-1',
        chapterId: 'chapter-2',
        name: '智者之战',
        description: '面对智慧的化身',
        difficulty: 'normal',
        enemyIds: ['zhuge-liang'],
        enemyLevels: [10],
        energyCost: 10,
        recommendedLevel: 10,
        rewards: {
          gold: 300,
          exp: 150,
        },
        firstClearRewards: {
          gold: 1000,
          exp: 500,
          gems: 150,
        },
      },
      {
        id: 'stage-2-2',
        chapterId: 'chapter-2',
        name: '女帝之威',
        description: '挑战历史上唯一的女皇帝',
        difficulty: 'normal',
        enemyIds: ['wu-zetian'],
        enemyLevels: [12],
        energyCost: 10,
        recommendedLevel: 12,
        rewards: {
          gold: 350,
          exp: 180,
        },
        firstClearRewards: {
          gold: 1200,
          exp: 600,
          gems: 150,
        },
      },
      {
        id: 'stage-2-3',
        chapterId: 'chapter-2',
        name: '征服者',
        description: '与法兰西皇帝一决高下',
        difficulty: 'hard',
        enemyIds: ['napoleon'],
        enemyLevels: [15],
        energyCost: 12,
        recommendedLevel: 15,
        rewards: {
          gold: 400,
          exp: 200,
        },
        firstClearRewards: {
          gold: 1500,
          exp: 800,
          gems: 200,
        },
      },
    ],
  },
  {
    id: 'chapter-3',
    name: '史诗对决',
    description: '传说级别的战斗，只有真正的强者才能胜出',
    unlocked: false,
    stages: [
      {
        id: 'stage-3-1',
        chapterId: 'chapter-3',
        name: '三英会',
        description: '连续挑战三位英雄',
        difficulty: 'hard',
        enemyIds: ['arthur', 'wu-zetian', 'hua-mulan'],
        enemyLevels: [18, 18, 18],
        energyCost: 15,
        recommendedLevel: 20,
        rewards: {
          gold: 500,
          exp: 300,
        },
        firstClearRewards: {
          gold: 2000,
          exp: 1000,
          gems: 300,
        },
      },
      {
        id: 'stage-3-2',
        chapterId: 'chapter-3',
        name: '东西对决',
        description: '东方智将VS西方战神',
        difficulty: 'hard',
        enemyIds: ['zhuge-liang', 'napoleon'],
        enemyLevels: [22, 22],
        energyCost: 18,
        recommendedLevel: 25,
        rewards: {
          gold: 600,
          exp: 400,
        },
        firstClearRewards: {
          gold: 2500,
          exp: 1200,
          gems: 400,
        },
      },
      {
        id: 'stage-3-3',
        chapterId: 'chapter-3',
        name: '最终试炼',
        description: '历史最强之战',
        difficulty: 'hell',
        enemyIds: ['zhuge-liang', 'napoleon', 'arthur', 'wu-zetian'],
        enemyLevels: [30, 30, 30, 30],
        energyCost: 25,
        recommendedLevel: 30,
        rewards: {
          gold: 1000,
          exp: 600,
        },
        firstClearRewards: {
          gold: 5000,
          exp: 3000,
          gems: 1000,
        },
      },
    ],
  },
];

/** 获取所有章节 */
export function getAllChapters(): Chapter[] {
  return CHAPTERS;
}

/** 获取关卡 */
export function getStage(stageId: string): Stage | undefined {
  for (const chapter of CHAPTERS) {
    const stage = chapter.stages.find((s) => s.id === stageId);
    if (stage) return stage;
  }
  return undefined;
}

/** 获取章节 */
export function getChapter(chapterId: string): Chapter | undefined {
  return CHAPTERS.find((c) => c.id === chapterId);
}

/** 检查章节是否解锁 */
export function isChapterUnlocked(chapterId: string, completedStages: string[]): boolean {
  const chapterIndex = CHAPTERS.findIndex((c) => c.id === chapterId);
  if (chapterIndex === 0) return true;
  
  const prevChapter = CHAPTERS[chapterIndex - 1];
  if (!prevChapter) return false;
  
  // 上一章节所有关卡都通关
  return prevChapter.stages.every((s) => completedStages.includes(s.id));
}

/** 获取下一章节 */
export function getNextChapter(chapterId: string): Chapter | undefined {
  const index = CHAPTERS.findIndex((c) => c.id === chapterId);
  return CHAPTERS[index + 1];
}

/** 难度名称 */
export const DIFFICULTY_NAMES: Record<string, string> = {
  easy: '简单',
  normal: '普通',
  hard: '困难',
  hell: '地狱',
};

/** 难度颜色 */
export const DIFFICULTY_COLORS: Record<string, string> = {
  easy: '#22c55e',
  normal: '#3b82f6',
  hard: '#f59e0b',
  hell: '#ef4444',
};
