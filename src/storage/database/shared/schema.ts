import { sql } from "drizzle-orm";
import {
  pgTable,
  text,
  varchar,
  timestamp,
  boolean,
  integer,
  jsonb,
  index,
  serial,
} from "drizzle-orm/pg-core";

// ==================== 系统健康检查表（保留，禁止删除） ====================
export const healthCheck = pgTable("health_check", {
  id: serial().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }).defaultNow(),
});

// ==================== 玩家基础信息表 ====================
export const players = pgTable(
  "players",
  {
    id: varchar("id", { length: 36 })
      .primaryKey()
      .default(sql`gen_random_uuid()`),
    name: varchar("name", { length: 128 }).notNull().default("勇者"),
    level: integer("level").notNull().default(1),
    exp: integer("exp").notNull().default(0),
    expToNext: integer("exp_to_next").notNull().default(100),
    
    // 资源
    gold: integer("gold").notNull().default(10000),
    gems: integer("gems").notNull().default(1000),
    expBooks: integer("exp_books").notNull().default(0),
    summonTickets: integer("summon_tickets").notNull().default(10),
    energy: integer("energy").notNull().default(100),
    maxEnergy: integer("max_energy").notNull().default(100),
    lastEnergyUpdate: timestamp("last_energy_update", { withTimezone: true, mode: 'string' }).defaultNow(),
    
    // 抽卡保底计数
    pityCount: integer("pity_count").notNull().default(0),
    legendaryPityCount: integer("legendary_pity_count").notNull().default(0),
    
    // 游戏进度
    totalPlayDays: integer("total_play_days").notNull().default(1),
    lastLoginDate: varchar("last_login_date", { length: 10 }).notNull().default(sql`to_char(now(), 'YYYY-MM-DD')`),
    
    createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }),
  },
  (table) => [
    index("players_last_login_idx").on(table.lastLoginDate),
  ]
);

// ==================== 玩家角色表 ====================
export const playerCharacters = pgTable(
  "player_characters",
  {
    id: serial().notNull().primaryKey(),
    playerId: varchar("player_id", { length: 36 }).notNull(),
    characterId: varchar("character_id", { length: 64 }).notNull(), // 角色模板ID
    
    // 养成数据
    level: integer("level").notNull().default(1),
    exp: integer("exp").notNull().default(0),
    stars: integer("stars").notNull().default(1),
    breakthrough: integer("breakthrough").notNull().default(0),
    
    // 羁绊
    bondLevel: integer("bond_level").notNull().default(1),
    bondExp: integer("bond_exp").notNull().default(0),
    
    // 时间戳
    obtainedAt: timestamp("obtained_at", { withTimezone: true, mode: 'string' })
      .defaultNow()
      .notNull(),
    createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }),
  },
  (table) => [
    index("player_characters_player_idx").on(table.playerId),
    index("player_characters_character_idx").on(table.characterId),
  ]
);

// ==================== 玩家队伍配置表 ====================
export const playerTeam = pgTable(
  "player_team",
  {
    id: serial().notNull().primaryKey(),
    playerId: varchar("player_id", { length: 36 }).notNull(),
    slot: integer("slot").notNull(), // 队伍位置 0-3
    characterInstanceId: integer("character_instance_id").notNull(), // player_characters 表的 id
    
    createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }),
  },
  (table) => [
    index("player_team_player_idx").on(table.playerId),
  ]
);

// ==================== 玩家已通关关卡表 ====================
export const playerCompletedStages = pgTable(
  "player_completed_stages",
  {
    id: serial().notNull().primaryKey(),
    playerId: varchar("player_id", { length: 36 }).notNull(),
    stageId: varchar("stage_id", { length: 64 }).notNull(),
    
    completedAt: timestamp("completed_at", { withTimezone: true, mode: 'string' })
      .defaultNow()
      .notNull(),
  },
  (table) => [
    index("player_completed_stages_player_idx").on(table.playerId),
  ]
);

// ==================== 玩家每日任务表 ====================
export const playerDailyTasks = pgTable(
  "player_daily_tasks",
  {
    id: serial().notNull().primaryKey(),
    playerId: varchar("player_id", { length: 36 }).notNull(),
    taskId: varchar("task_id", { length: 64 }).notNull(), // 任务ID
    
    name: varchar("name", { length: 128 }).notNull(),
    description: text("description").notNull(),
    target: integer("target").notNull().default(1),
    progress: integer("progress").notNull().default(0),
    
    // 奖励
    rewardGold: integer("reward_gold").default(0),
    rewardGems: integer("reward_gems").default(0),
    rewardExp: integer("reward_exp").default(0),
    
    completed: boolean("completed").notNull().default(false),
    claimed: boolean("claimed").notNull().default(false),
    
    taskDate: varchar("task_date", { length: 10 }).notNull(), // 任务所属日期 YYYY-MM-DD
    
    createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }),
  },
  (table) => [
    index("player_daily_tasks_player_idx").on(table.playerId),
    index("player_daily_tasks_date_idx").on(table.taskDate),
  ]
);

// ==================== 抽卡历史记录表 ====================
export const summonHistory = pgTable(
  "summon_history",
  {
    id: serial().notNull().primaryKey(),
    playerId: varchar("player_id", { length: 36 }).notNull(),
    characterId: varchar("character_id", { length: 64 }).notNull(),
    rarity: varchar("rarity", { length: 16 }).notNull(), // common, rare, epic, legendary
    
    summonedAt: timestamp("summoned_at", { withTimezone: true, mode: 'string' })
      .defaultNow()
      .notNull(),
  },
  (table) => [
    index("summon_history_player_idx").on(table.playerId),
  ]
);

// ==================== TypeScript 类型定义 ====================
export type Player = typeof players.$inferSelect;
export type PlayerCharacter = typeof playerCharacters.$inferSelect;
export type PlayerTeam = typeof playerTeam.$inferSelect;
export type PlayerCompletedStage = typeof playerCompletedStages.$inferSelect;
export type PlayerDailyTask = typeof playerDailyTasks.$inferSelect;
export type SummonHistoryRecord = typeof summonHistory.$inferSelect;
