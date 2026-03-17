'use client';

import { useState, useCallback } from 'react';
import {
  BattleCharacter,
  BattleState,
  BattleResult,
  BattleLog,
  Skill,
  StatusEffect,
  ELEMENT_ADVANTAGE,
  ELEMENT_NAMES,
} from '@/types/game';

/** 深拷贝角色 */
function cloneCharacter(char: BattleCharacter): BattleCharacter {
  return JSON.parse(JSON.stringify(char));
}

/** 计算属性克制倍率 */
function calculateElementMultiplier(attackerElement: string, defenderElement: string): number {
  const advantages = ELEMENT_ADVANTAGE[attackerElement as keyof typeof ELEMENT_ADVANTAGE] || [];
  if (advantages.includes(defenderElement as any)) {
    return 1.5; // 克制
  }
  return 1.0;
}

/** 应用状态效果到属性 */
function applyStatusEffects(char: BattleCharacter): BattleCharacter {
  const result = { ...char, currentStats: { ...char.currentStats } };
  
  char.statusEffects.forEach((effect) => {
    switch (effect.type) {
      case 'buff_attack':
        result.currentStats.attack = Math.floor(result.currentStats.attack * (1 + effect.value / 100));
        break;
      case 'buff_defense':
        result.currentStats.defense = Math.floor(result.currentStats.defense * (1 + effect.value / 100));
        break;
      case 'debuff_attack':
        result.currentStats.attack = Math.floor(result.currentStats.attack * (1 - effect.value / 100));
        break;
      case 'debuff_defense':
        result.currentStats.defense = Math.floor(result.currentStats.defense * (1 - effect.value / 100));
        break;
    }
  });
  
  return result;
}

/** 计算伤害 */
function calculateDamage(
  attacker: BattleCharacter,
  defender: BattleCharacter,
  skill: Skill
): { damage: number; isCritical: boolean; isEffective: boolean; isMiss: boolean } {
  // 命中判定
  const hitRoll = Math.random() * 100;
  if (hitRoll > skill.accuracy) {
    return { damage: 0, isCritical: false, isEffective: false, isMiss: true };
  }

  // 属性克制
  const elementMultiplier = calculateElementMultiplier(skill.element, defender.element);
  const isEffective = elementMultiplier > 1;

  // 基础伤害计算
  const isSpecialMove = skill.type === 'special' || skill.type === 'debuff';
  const attackStat = isSpecialMove ? attacker.currentStats.specialAttack : attacker.currentStats.attack;
  const defenseStat = isSpecialMove ? defender.currentStats.specialDefense : defender.currentStats.defense;

  // 伤害公式：(攻击力 * 技能威力 / 100 - 防御力 * 0.5) * 属性克制 * 随机浮动
  let baseDamage = Math.max(1, (attackStat * skill.power / 100) - (defenseStat * 0.4));
  const randomMultiplier = 0.85 + Math.random() * 0.3; // 0.85-1.15
  baseDamage = baseDamage * elementMultiplier * randomMultiplier;

  // 暴击判定
  const critRoll = Math.random() * 100;
  const isCritical = critRoll < attacker.currentStats.critRate;
  if (isCritical) {
    baseDamage *= attacker.currentStats.critDamage;
  }

  return {
    damage: Math.floor(baseDamage),
    isCritical,
    isEffective,
    isMiss: false,
  };
}

/** 处理持续伤害效果 */
function processStatusEffects(char: BattleCharacter): { char: BattleCharacter; damage: number; effects: string[] } {
  let totalDamage = 0;
  const effects: string[] = [];
  const newEffects: StatusEffect[] = [];

  char.statusEffects.forEach((effect) => {
    // 持续伤害
    if (effect.type === 'burn') {
      totalDamage += effect.value;
      effects.push(`灼烧造成了 ${effect.value} 点伤害`);
    } else if (effect.type === 'poison') {
      totalDamage += effect.value;
      effects.push(`中毒造成了 ${effect.value} 点伤害`);
    }

    // 减少持续回合
    if (effect.duration > 1) {
      newEffects.push({ ...effect, duration: effect.duration - 1 });
    }
  });

  const newChar = {
    ...char,
    statusEffects: newEffects,
    currentStats: {
      ...char.currentStats,
      hp: Math.max(0, char.currentStats.hp - totalDamage),
    },
  };

  return { char: newChar, damage: totalDamage, effects };
}

export function useBattle() {
  const [battleState, setBattleState] = useState<BattleState | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  /** 初始化战斗 */
  const initBattle = useCallback((player: BattleCharacter, enemy: BattleCharacter) => {
    const playerClone = cloneCharacter(player);
    const enemyClone = cloneCharacter(enemy);

    // 重置战斗属性
    playerClone.currentStats = { ...playerClone.stats };
    playerClone.statusEffects = [];
    enemyClone.currentStats = { ...enemyClone.stats };
    enemyClone.statusEffects = [];

    // 重置技能PP
    playerClone.skills.forEach((s) => (s.pp = s.maxPp));
    enemyClone.skills.forEach((s) => (s.pp = s.maxPp));

    // 根据速度决定先手
    const firstTurn = playerClone.stats.speed >= enemyClone.stats.speed ? playerClone.id : enemyClone.id;

    setBattleState({
      phase: 'select',
      turn: 1,
      currentTurnId: firstTurn,
      player: playerClone,
      enemy: enemyClone,
      actions: [],
      results: [],
      logs: [
        {
          turn: 0,
          message: `战斗开始！${playerClone.name} VS ${enemyClone.name}`,
          type: 'info',
        },
        {
          turn: 0,
          message: `${firstTurn === playerClone.id ? playerClone.name : enemyClone.name} 先手行动！`,
          type: 'info',
        },
      ],
      winner: null,
    });
  }, []);

  /** 执行技能 */
  const executeSkill = useCallback(
    async (skillId: string) => {
      if (!battleState || isAnimating) return;
      if (battleState.phase !== 'select') return;

      setIsAnimating(true);

      const isPlayerTurn = battleState.currentTurnId === battleState.player.id;
      const attacker = isPlayerTurn ? battleState.player : battleState.enemy;
      const defender = isPlayerTurn ? battleState.enemy : battleState.player;

      // 查找技能
      const skill = attacker.skills.find((s) => s.id === skillId);
      if (!skill || skill.pp <= 0) {
        setIsAnimating(false);
        return;
      }

      // 消耗PP
      skill.pp -= 1;

      // 应用状态效果后的属性
      const effectiveAttacker = applyStatusEffects(attacker);
      const effectiveDefender = applyStatusEffects(defender);

      // 创建战斗结果
      const result: BattleResult = {
        attackerId: attacker.id,
        defenderId: defender.id,
        skillUsed: skill,
        damage: 0,
        isCritical: false,
        isEffective: false,
        isMiss: false,
        effectsApplied: [],
        remainingHp: defender.currentStats.hp,
      };

      const newLogs: BattleLog[] = [];

      // 处理不同技能类型
      if (skill.type === 'heal') {
        // 治疗技能
        const healAmount = skill.effect?.value || 0;
        attacker.currentStats.hp = Math.min(
          attacker.stats.maxHp,
          attacker.currentStats.hp + healAmount
        );
        newLogs.push({
          turn: battleState.turn,
          message: `${attacker.name} 使用了 ${skill.name}！`,
          type: 'heal',
        });
        newLogs.push({
          turn: battleState.turn,
          message: `${attacker.name} 恢复了 ${healAmount} 点生命值！`,
          type: 'heal',
        });
      } else if (skill.type === 'buff') {
        // 增益技能
        if (skill.effect) {
          // 只有状态效果类型才添加到 statusEffects
          const validStatusTypes = ['burn', 'freeze', 'poison', 'stun', 'buff_attack', 'buff_defense', 'debuff_attack', 'debuff_defense'] as const;
          if (validStatusTypes.includes(skill.effect.type as typeof validStatusTypes[number])) {
            attacker.statusEffects.push({
              type: skill.effect.type as typeof validStatusTypes[number],
              value: skill.effect.value,
              duration: skill.effect.duration,
            });
          }
          newLogs.push({
            turn: battleState.turn,
            message: `${attacker.name} 使用了 ${skill.name}！`,
            type: 'effect',
          });
          const statName = skill.effect.type.includes('attack') ? '攻击力' : '防御力';
          newLogs.push({
            turn: battleState.turn,
            message: `${attacker.name} 的 ${statName} 提升了 ${skill.effect.value}%！`,
            type: 'effect',
          });
        }
      } else if (skill.type === 'debuff') {
        // 减益技能
        const { damage, isCritical, isEffective, isMiss } = calculateDamage(
          effectiveAttacker,
          effectiveDefender,
          skill
        );

        if (!isMiss) {
          defender.currentStats.hp = Math.max(0, defender.currentStats.hp - damage);
          result.damage = damage;
          result.isCritical = isCritical;
          result.isEffective = isEffective;
          result.remainingHp = defender.currentStats.hp;

          newLogs.push({
            turn: battleState.turn,
            message: `${attacker.name} 使用了 ${skill.name}！`,
            type: 'damage',
          });

          if (skill.effect && Math.random() * 100 < skill.effect.chance) {
            // 只有状态效果类型才添加到 statusEffects
            const validStatusTypes = ['burn', 'freeze', 'poison', 'stun', 'buff_attack', 'buff_defense', 'debuff_attack', 'debuff_defense'] as const;
            if (validStatusTypes.includes(skill.effect.type as typeof validStatusTypes[number])) {
              defender.statusEffects.push({
                type: skill.effect.type as typeof validStatusTypes[number],
                value: skill.effect.value,
                duration: skill.effect.duration,
              });
            }
            result.effectsApplied.push({ ...skill.effect, duration: skill.effect.duration });
            newLogs.push({
              turn: battleState.turn,
              message: `${defender.name} 的攻击力下降了！`,
              type: 'effect',
            });
          }

          if (damage > 0) {
            newLogs.push({
              turn: battleState.turn,
              message: `${isEffective ? '效果拔群！' : ''}${defender.name} 受到了 ${damage} 点伤害！${isCritical ? ' 暴击！' : ''}`,
              type: isCritical ? 'critical' : 'damage',
            });
          }
        } else {
          result.isMiss = true;
          newLogs.push({
            turn: battleState.turn,
            message: `${attacker.name} 使用了 ${skill.name}...但是没有命中！`,
            type: 'miss',
          });
        }
      } else {
        // 攻击/特殊技能
        const { damage, isCritical, isEffective, isMiss } = calculateDamage(
          effectiveAttacker,
          effectiveDefender,
          skill
        );

        if (!isMiss) {
          defender.currentStats.hp = Math.max(0, defender.currentStats.hp - damage);
          result.damage = damage;
          result.isCritical = isCritical;
          result.isEffective = isEffective;
          result.remainingHp = defender.currentStats.hp;

          newLogs.push({
            turn: battleState.turn,
            message: `${attacker.name} 使用了 ${skill.name}！`,
            type: 'damage',
          });

          // 属性克制提示
          if (isEffective) {
            newLogs.push({
              turn: battleState.turn,
              message: `${ELEMENT_NAMES[skill.element]}属性克制！效果拔群！`,
              type: 'info',
            });
          }

          // 处理附加效果
          if (skill.effect && Math.random() * 100 < skill.effect.chance) {
            if (skill.effect.type === 'burn') {
              defender.statusEffects.push({
                type: 'burn',
                value: skill.effect.value,
                duration: skill.effect.duration,
              });
              newLogs.push({
                turn: battleState.turn,
                message: `${defender.name} 陷入了灼烧状态！`,
                type: 'effect',
              });
            } else if (skill.effect.type === 'poison') {
              defender.statusEffects.push({
                type: 'poison',
                value: skill.effect.value,
                duration: skill.effect.duration,
              });
              newLogs.push({
                turn: battleState.turn,
                message: `${defender.name} 中毒了！`,
                type: 'effect',
              });
            } else if (skill.effect.type === 'stun') {
              defender.statusEffects.push({
                type: 'stun',
                value: 0,
                duration: skill.effect.duration,
              });
              newLogs.push({
                turn: battleState.turn,
                message: `${defender.name} 被眩晕了！`,
                type: 'effect',
              });
            }
            result.effectsApplied.push({ ...skill.effect, duration: skill.effect.duration });
          }

          newLogs.push({
            turn: battleState.turn,
            message: `${defender.name} 受到了 ${damage} 点伤害！${isCritical ? ' 暴击！' : ''}`,
            type: isCritical ? 'critical' : 'damage',
          });
        } else {
          result.isMiss = true;
          newLogs.push({
            turn: battleState.turn,
            message: `${attacker.name} 使用了 ${skill.name}...但是没有命中！`,
            type: 'miss',
          });
        }
      }

      // 更新状态
      setBattleState((prev) => {
        if (!prev) return null;

        const newPlayer = isPlayerTurn ? { ...prev.player } : { ...attacker };
        const newEnemy = isPlayerTurn ? { ...defender } : { ...prev.enemy };

        // 同步血量
        if (isPlayerTurn) {
          newPlayer.currentStats = { ...prev.player.currentStats };
          newPlayer.statusEffects = [...prev.player.statusEffects];
          newPlayer.skills = [...prev.player.skills];
          newEnemy.currentStats = { ...defender.currentStats };
          newEnemy.statusEffects = [...defender.statusEffects];
        } else {
          newEnemy.currentStats = { ...prev.enemy.currentStats };
          newEnemy.statusEffects = [...prev.enemy.statusEffects];
          newEnemy.skills = [...prev.enemy.skills];
          newPlayer.currentStats = { ...defender.currentStats };
          newPlayer.statusEffects = [...defender.statusEffects];
        }

        // 检查胜负
        let winner: 'player' | 'enemy' | null = null;
        if (newPlayer.currentStats.hp <= 0) {
          winner = 'enemy';
          newLogs.push({
            turn: prev.turn,
            message: `${newPlayer.name} 被击败了！`,
            type: 'info',
          });
        } else if (newEnemy.currentStats.hp <= 0) {
          winner = 'player';
          newLogs.push({
            turn: prev.turn,
            message: `${newEnemy.name} 被击败了！`,
            type: 'info',
          });
        }

        return {
          ...prev,
          phase: winner ? 'end' : 'execute',
          player: newPlayer,
          enemy: newEnemy,
          results: [...prev.results, result],
          logs: [...prev.logs, ...newLogs],
          winner,
        };
      });

      // 动画延迟
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // 如果战斗未结束，切换回合
      setBattleState((prev) => {
        if (!prev || prev.winner) return prev;

        // 处理状态效果
        let { player, enemy } = prev;
        
        // 处理持续伤害
        const playerStatusResult = processStatusEffects(player);
        const enemyStatusResult = processStatusEffects(enemy);

        player = playerStatusResult.char;
        enemy = enemyStatusResult.char;

        const statusLogs: BattleLog[] = [];
        if (playerStatusResult.damage > 0) {
          statusLogs.push({
            turn: prev.turn,
            message: playerStatusResult.effects.join(' '),
            type: 'damage',
          });
        }
        if (enemyStatusResult.damage > 0) {
          statusLogs.push({
            turn: prev.turn,
            message: enemyStatusResult.effects.join(' '),
            type: 'damage',
          });
        }

        // 检查持续伤害导致的胜负
        let winner: 'player' | 'enemy' | null = prev.winner;
        if (player.currentStats.hp <= 0) {
          winner = 'enemy';
        } else if (enemy.currentStats.hp <= 0) {
          winner = 'player';
        }

        const nextTurnId = prev.currentTurnId === prev.player.id ? prev.enemy.id : prev.player.id;
        const newTurn = nextTurnId === prev.player.id ? prev.turn + 1 : prev.turn;

        if (!winner) {
          statusLogs.push({
            turn: newTurn,
            message: `--- 第 ${newTurn} 回合 ---`,
            type: 'info',
          });
        }

        return {
          ...prev,
          phase: 'select',
          turn: newTurn,
          currentTurnId: nextTurnId,
          player,
          enemy,
          logs: [...prev.logs, ...statusLogs],
          winner,
        };
      });

      setIsAnimating(false);
    },
    [battleState, isAnimating]
  );

  /** 敌人AI选择技能 */
  const enemySelectSkill = useCallback((): string | null => {
    if (!battleState) return null;

    const enemy = battleState.enemy;
    const availableSkills = enemy.skills.filter((s) => s.pp > 0);
    if (availableSkills.length === 0) return null;

    // 简单AI：优先使用高威力技能，低血量时使用治疗
    if (enemy.currentStats.hp < enemy.stats.maxHp * 0.3) {
      const healSkill = availableSkills.find((s) => s.type === 'heal');
      if (healSkill) return healSkill.id;
    }

    // 随机选择，但偏向高威力技能
    const weights = availableSkills.map((s) => s.power + 50);
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    let random = Math.random() * totalWeight;

    for (let i = 0; i < availableSkills.length; i++) {
      random -= weights[i];
      if (random <= 0) {
        return availableSkills[i].id;
      }
    }

    return availableSkills[0].id;
  }, [battleState]);

  /** 重置战斗 */
  const resetBattle = useCallback(() => {
    setBattleState(null);
    setIsAnimating(false);
  }, []);

  return {
    battleState,
    isAnimating,
    initBattle,
    executeSkill,
    enemySelectSkill,
    resetBattle,
  };
}
