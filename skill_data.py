# skill_data.py — 技能系统完整数据
"""
技能体系：
  - 6元素 × 17共通技能 = 102 共通技能
  - 蓝卡3 / 紫卡5 / 金卡5+1觉醒 专属技能
  - 蓝卡及以上各拥有1个被动天赋

解锁规则：
  白卡: Lv1起每5级获得1个共通技能，Lv80全部解锁 (共17个)
  蓝卡: 同白卡 + Lv1/40/80 获得专属技能(3个) + 1被动天赋
  紫卡: 同白卡 + Lv1/20/40/60/80 获得专属技能(5个) + 1被动天赋
  金卡: 同紫卡 + Lv100觉醒技能 + 1被动天赋

角色职业修正：
  同元素共通技能，不同职业使用时威力/效果有差异
"""

import copy

# ==================== 常量 ====================

MAX_CHARACTER_LEVEL = 100

SHARED_SKILL_UNLOCK_LEVELS = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]

# ==================== 品质配置 ====================

RARITY_CONFIG = {
    'common': {
        'name': '白卡', 'color': '#9ca3af',
        'base_stat_mult': 1.0,
        'growth_per_level': 0.03,
        'exclusive_unlock_levels': [],
        'has_passive': False,
        'has_awakening': False,
    },
    'rare': {
        'name': '蓝卡', 'color': '#3b82f6',
        'base_stat_mult': 1.15,
        'growth_per_level': 0.04,
        'exclusive_unlock_levels': [1, 40, 80],
        'has_passive': True,
        'has_awakening': False,
    },
    'epic': {
        'name': '紫卡', 'color': '#a855f7',
        'base_stat_mult': 1.35,
        'growth_per_level': 0.055,
        'exclusive_unlock_levels': [1, 20, 40, 60, 80],
        'has_passive': True,
        'has_awakening': False,
    },
    'legendary': {
        'name': '金卡', 'color': '#f59e0b',
        'base_stat_mult': 1.6,
        'growth_per_level': 0.07,
        'exclusive_unlock_levels': [1, 20, 40, 60, 80],
        'has_passive': True,
        'has_awakening': True,
        'awakening_level': 100,
    },
}

# ==================== 职业修正系数 ====================

ROLE_MODIFIERS = {
    'warrior': {
        'physical': 1.15, 'magic': 0.85, 'heal': 0.7, 'buff': 0.8, 'debuff': 0.8,
        'desc': '物理伤害+15%，魔法-15%',
    },
    'mage': {
        'physical': 0.75, 'magic': 1.20, 'heal': 0.9, 'buff': 1.0, 'debuff': 1.05,
        'desc': '魔法伤害+20%，物理-25%',
    },
    'assassin': {
        'physical': 1.20, 'magic': 0.80, 'heal': 0.5, 'buff': 0.6, 'debuff': 0.7,
        'desc': '物理伤害+20%，暴击增强',
    },
    'tank': {
        'physical': 0.90, 'magic': 0.80, 'heal': 1.0, 'buff': 1.25, 'debuff': 1.0,
        'desc': '增益效果+25%，伤害降低',
    },
    'support': {
        'physical': 0.65, 'magic': 0.85, 'heal': 1.40, 'buff': 1.30, 'debuff': 1.10,
        'desc': '治疗+40%，增益+30%',
    },
}


def _apply_role_mod(skill_dict, role_type):
    """对核心共通技能施加职业修正（仅用于 roles=None 的技能）"""
    mod = ROLE_MODIFIERS.get(role_type)
    if not mod:
        return skill_dict
    s = copy.deepcopy(skill_dict)
    st = s['type']
    if st in ('physical', 'magic') and s['power'] > 0:
        s['power'] = max(1, int(s['power'] * mod.get(st, 1.0)))
    elif st == 'heal':
        s['power'] = max(1, int(s['power'] * mod.get('heal', 1.0)))
    elif st == 'buff':
        s['power'] = max(1, int(s['power'] * mod.get('buff', 1.0)))
    elif st == 'debuff':
        s['power'] = max(1, int(s['power'] * mod.get('debuff', 1.0)))
    return s


# ====================================================================
#  六元素共通技能池  (每元素 ~25 个)
#
#  结构：12 核心技能 (roles=None, 所有职业) + 5 分支等级各 2-3 职业变体
#  分支等级: Lv5, 15, 25, 35, 45
#  核心等级: Lv1, 10, 20, 30, 40, 50, 55, 60, 65, 70, 75, 80
#  每个职业最终学会: 12 核心 + 5 分支 = 17 个技能
#  roles=None 表示所有职业通用; 否则为指定职业列表
# ====================================================================

_W = 'warrior'; _M = 'mage'; _A = 'assassin'; _T = 'tank'; _S = 'support'

ELEMENT_SKILL_POOL = {

    # ==================== 火 (24) ====================
    'fire': [
        # --- 核心 (12, 全职业) ---
        {'id': 'fire_01', 'name': '烈焰突刺',   'power': 90,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以火焰覆盖武器突刺敌人', 'effects': []},
        {'id': 'fire_03', 'name': '火焰护盾',   'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 10, 'roles': None,
         'description': '用火焰凝聚护盾，提升防御', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        {'id': 'fire_05', 'name': '焰爆术',     'power': 160, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '凝聚火焰能量爆发', 'effects': [{'type': 'burn', 'chance': 0.4, 'damage_pct': 6, 'duration': 2}]},
        {'id': 'fire_07', 'name': '火龙卷',     'power': 150, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '召唤火焰龙卷席卷敌方全体', 'effects': []},
        {'id': 'fire_09', 'name': '业火焚身',   'power': 250, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '业火缠身，造成大量魔法伤害', 'effects': [{'type': 'burn', 'chance': 0.5, 'damage_pct': 8, 'duration': 2}]},
        {'id': 'fire_11', 'name': '凤凰冲击',   'power': 300, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '化身凤凰猛冲', 'effects': []},
        {'id': 'fire_12', 'name': '灼热领域',   'power': 250, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '展开灼热力场，降低全体攻击', 'effects': [{'type': 'debuff_atk', 'value': 15, 'duration': 2}]},
        {'id': 'fire_13', 'name': '火神之怒',   'power': 380, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '引动火神之力倾注于一点', 'effects': []},
        {'id': 'fire_14', 'name': '不灭之焰',   'power': 35,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '不灭圣火治愈友方', 'effects': [{'type': 'shield', 'value': 15, 'duration': 2}]},
        {'id': 'fire_15', 'name': '烈焰风暴',   'power': 350, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '引爆烈焰风暴席卷全场', 'effects': [{'type': 'burn', 'chance': 0.6, 'damage_pct': 8, 'duration': 3}]},
        {'id': 'fire_16', 'name': '焚天灭地',   'power': 450, 'type': 'physical', 'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '焚天之力无视部分防御', 'effects': [{'type': 'ignore_def', 'value': 30}]},
        {'id': 'fire_17', 'name': '涅槃之焰',   'power': 400, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '涅槃烈焰焚烧一切', 'effects': [{'type': 'lifesteal', 'value': 20}]},
        # --- Lv5 分支 ---
        {'id': 'fire_02a', 'name': '灼烧打击',  'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '灼热近战攻击，有概率灼烧', 'effects': [{'type': 'burn', 'chance': 0.3, 'damage_pct': 5, 'duration': 2}]},
        {'id': 'fire_02b', 'name': '火焰弹',    'power': 115, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射火焰弹远程轰炸目标', 'effects': [{'type': 'burn', 'chance': 0.25, 'damage_pct': 5, 'duration': 2}]},
        # --- Lv15 分支 ---
        {'id': 'fire_04a', 'name': '烈焰斩',    'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _T],
         'description': '火焰附着的大力劈砍', 'effects': []},
        {'id': 'fire_04b', 'name': '烈焰箭',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S],
         'description': '射出烈焰之箭', 'effects': []},
        # --- Lv25 分支 ---
        {'id': 'fire_06a', 'name': '焰爆连击',  'power': 180, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '火焰附着的连续打击', 'effects': []},
        {'id': 'fire_06b', 'name': '烈焰灵波',  'power': 190, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_M],
         'description': '凝聚灵力化为烈焰波动', 'effects': [{'type': 'burn', 'chance': 0.35, 'damage_pct': 6, 'duration': 2}]},
        {'id': 'fire_06c', 'name': '烈焰守护',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '以烈焰守护全队，提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        # --- Lv35 分支 ---
        {'id': 'fire_08a', 'name': '烈焰之心',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '点燃心火大幅提升攻击力', 'effects': [{'type': 'buff_atk', 'value': 30, 'duration': 3}]},
        {'id': 'fire_08b', 'name': '火焰治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '以温暖的火焰治愈友方', 'effects': []},
        # --- Lv45 分支 ---
        {'id': 'fire_10a', 'name': '火墙术',    'power': 200, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '烈火之墙横扫战场', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}]},
        {'id': 'fire_10b', 'name': '烈焰庇护',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队获得烈焰护盾减伤', 'effects': [{'type': 'shield', 'value': 20, 'duration': 3}]},
        {'id': 'fire_10c', 'name': '影焰突袭',  'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '暗影火焰加持的暴击突袭', 'effects': [{'type': 'ignore_def', 'value': 20}]},
    ],

    # ==================== 水 (24) ====================
    'water': [
        # --- 核心 (12) ---
        {'id': 'water_01', 'name': '水流斩',     'power': 85,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以高压水流强化的武器劈砍', 'effects': []},
        {'id': 'water_03', 'name': '水盾术',     'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 10, 'roles': None,
         'description': '凝聚水盾提升防御并微量回复', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}, {'type': 'heal_pct', 'value': 8}]},
        {'id': 'water_05', 'name': '潮汐之力',   'power': 160, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '引动潮汐之力冲击目标', 'effects': []},
        {'id': 'water_07', 'name': '暴风雪',     'power': 145, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '降下暴风雪覆盖全场', 'effects': [{'type': 'slow', 'chance': 0.4, 'value': 10, 'duration': 2}]},
        {'id': 'water_09', 'name': '冰霜囚笼',   'power': 240, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '冰霜牢笼囚禁目标', 'effects': [{'type': 'freeze', 'chance': 0.35, 'duration': 1}]},
        {'id': 'water_11', 'name': '水龙弹',     'power': 290, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '化水为龙轰击目标', 'effects': []},
        {'id': 'water_12', 'name': '冰封领域',   'power': 240, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '展开绝对冰域冻结全场', 'effects': [{'type': 'freeze', 'chance': 0.4, 'duration': 1}]},
        {'id': 'water_13', 'name': '深海之怒',   'power': 370, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '引动深海之力碾碎目标', 'effects': []},
        {'id': 'water_14', 'name': '治愈之雨',   'power': 30,  'type': 'heal',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '降下治愈甘霖治愈全体', 'effects': []},
        {'id': 'water_15', 'name': '海啸冲击',   'power': 340, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '掀起滔天巨浪淹没全场', 'effects': []},
        {'id': 'water_16', 'name': '绝对零度',   'power': 440, 'type': 'magic',    'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '将目标冷冻至绝对零度', 'effects': [{'type': 'freeze', 'chance': 0.6, 'duration': 2}]},
        {'id': 'water_17', 'name': '沧海横流',   'power': 400, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '沧海之力倾泻而出', 'effects': [{'type': 'freeze', 'chance': 0.5, 'duration': 1}]},
        # --- Lv5 分支 ---
        {'id': 'water_02a', 'name': '寒冰打击',  'power': 105, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '寒冰附体的近战攻击', 'effects': [{'type': 'slow', 'chance': 0.3, 'value': 15, 'duration': 2}]},
        {'id': 'water_02b', 'name': '冰霜射线',  'power': 110, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射冰霜射线远程冻结目标', 'effects': [{'type': 'freeze', 'chance': 0.2, 'duration': 1}]},
        # --- Lv15 分支 ---
        {'id': 'water_04a', 'name': '寒冰护甲',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 15, 'roles': [_W, _T],
         'description': '冰晶覆体，大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}, {'type': 'buff_mdef', 'value': 20, 'duration': 3}]},
        {'id': 'water_04b', 'name': '冰刺术',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S],
         'description': '从地面升起冰刺贯穿目标', 'effects': []},
        # --- Lv25 分支 ---
        {'id': 'water_06a', 'name': '冰封打击',  'power': 175, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '冰封之拳有概率冻结目标', 'effects': [{'type': 'freeze', 'chance': 0.25, 'duration': 1}]},
        {'id': 'water_06b', 'name': '冰晶爆破',  'power': 170, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '引爆冰晶碎片横扫全场', 'effects': [{'type': 'slow', 'chance': 0.4, 'value': 15, 'duration': 2}]},
        {'id': 'water_06c', 'name': '潮汐祝福',  'power': 20,  'type': 'heal',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '潮汐之力祝福全体回复', 'effects': []},
        # --- Lv35 分支 ---
        {'id': 'water_08a', 'name': '寒冰武装',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A],
         'description': '冰晶强化武器提升攻击与暴击', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}, {'type': 'buff_crit', 'value': 20, 'duration': 3}]},
        {'id': 'water_08b', 'name': '治愈之泉',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T, _M],
         'description': '召唤清泉治愈一名友方', 'effects': []},
        # --- Lv45 分支 ---
        {'id': 'water_10a', 'name': '潮汐涌动',  'power': 200, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '潮汐涌动冲刷全体敌人', 'effects': [{'type': 'slow', 'chance': 0.5, 'value': 15, 'duration': 2}]},
        {'id': 'water_10b', 'name': '冰甲术',    'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队覆盖冰甲大幅减伤', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}]},
        {'id': 'water_10c', 'name': '冰影连刺',  'power': 240, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '冰影闪烁中的连续穿刺', 'effects': [{'type': 'freeze', 'chance': 0.3, 'duration': 1}]},
    ],

    # ==================== 风 (25) ====================
    'wind': [
        # --- 核心 (12) ---
        {'id': 'wind_01', 'name': '风刃',       'power': 80,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以风之力强化的利刃斩击', 'effects': []},
        {'id': 'wind_03', 'name': '旋风斩',     'power': 100, 'type': 'physical', 'target': 'all',        'cooldown': 2, 'unlock_level': 10, 'roles': None,
         'description': '旋转武器形成风刃切割全体', 'effects': []},
        {'id': 'wind_05', 'name': '真空刃',     'power': 170, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '压缩空气形成真空斩击', 'effects': []},
        {'id': 'wind_07', 'name': '龙卷风',     'power': 155, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '召唤龙卷风席卷全场', 'effects': []},
        {'id': 'wind_09', 'name': '裂空斩',     'power': 260, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '斩裂天空的强力一击', 'effects': []},
        {'id': 'wind_11', 'name': '暴风连斩',   'power': 280, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '风速下的连续利刃斩击', 'effects': [{'type': 'buff_crit', 'value': 15, 'duration': 1}]},
        {'id': 'wind_12', 'name': '风神之怒',   'power': 250, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '风神震怒狂风横扫全场', 'effects': []},
        {'id': 'wind_13', 'name': '天翔百裂',   'power': 360, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '翔于天际的百连斩击', 'effects': []},
        {'id': 'wind_14', 'name': '瞬步',       'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '极速瞬移回避并反击', 'effects': [{'type': 'evasion_up', 'value': 100, 'duration': 1}, {'type': 'counter', 'value': 50}]},
        {'id': 'wind_15', 'name': '风暴领域',   'power': 330, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '展开风暴领域吞噬全场', 'effects': [{'type': 'debuff_spd', 'value': 20, 'duration': 2}]},
        {'id': 'wind_16', 'name': '神风',       'power': 430, 'type': 'physical', 'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '化身神风一击贯穿', 'effects': [{'type': 'ignore_def', 'value': 30}]},
        {'id': 'wind_17', 'name': '天风归一',   'power': 400, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '天地之风归于一体毁灭一切', 'effects': []},
        # --- Lv5 分支 ---
        {'id': 'wind_02a', 'name': '疾风步',    'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 2, 'unlock_level': 5,  'roles': [_A, _W, _M],
         'description': '提升自身速度先发制人', 'effects': [{'type': 'buff_spd', 'value': 20, 'duration': 3}]},
        {'id': 'wind_02b', 'name': '风盾术',    'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 5,  'roles': [_T, _S],
         'description': '风之护盾包裹自身提升防御与闪避', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 3}, {'type': 'evasion_up', 'value': 15, 'duration': 3}]},
        # --- Lv15 分支 ---
        {'id': 'wind_04a', 'name': '穿透之风',  'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A],
         'description': '风之刃穿透护甲', 'effects': [{'type': 'ignore_def', 'value': 15}]},
        {'id': 'wind_04b', 'name': '风之治愈',  'power': 20,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 15, 'roles': [_S],
         'description': '以清风治愈友方伤痛', 'effects': []},
        {'id': 'wind_04c', 'name': '风暴之矛',  'power': 140, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _T],
         'description': '凝聚风暴化为魔法矛刺', 'effects': []},
        # --- Lv25 分支 ---
        {'id': 'wind_06a', 'name': '风暴之眼',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 25, 'roles': [_A, _W],
         'description': '立于风暴中心提升闪避与暴击', 'effects': [{'type': 'buff_crit', 'value': 25, 'duration': 3}, {'type': 'evasion_up', 'value': 20, 'duration': 3}]},
        {'id': 'wind_06b', 'name': '疾风守护',  'power': 20,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '全队获得风之守护提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'wind_06c', 'name': '风刃连斩',  'power': 180, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '无数风刃切割全体', 'effects': []},
        # --- Lv35 分支 ---
        {'id': 'wind_08a', 'name': '迅捷之风',  'power': 20,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 35, 'roles': [_S, _M],
         'description': '全队速度提升', 'effects': [{'type': 'buff_spd', 'value': 20, 'duration': 3}]},
        {'id': 'wind_08b', 'name': '烈风斩',    'power': 220, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 35, 'roles': [_W, _A, _T],
         'description': '以烈风强化的重斩', 'effects': []},
        # --- Lv45 分支 ---
        {'id': 'wind_10a', 'name': '风之结界',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '风之结界庇护全队提升闪避', 'effects': [{'type': 'evasion_up', 'value': 25, 'duration': 3}]},
        {'id': 'wind_10b', 'name': '真空斩击',  'power': 260, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_W, _A],
         'description': '真空压缩的极致一刀', 'effects': [{'type': 'ignore_def', 'value': 15}]},
        {'id': 'wind_10c', 'name': '飓风术',    'power': 250, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M],
         'description': '召唤飓风席卷全场', 'effects': [{'type': 'debuff_spd', 'value': 15, 'duration': 2}]},
    ],

    # ==================== 土 (25) ====================
    'earth': [
        # --- 核心 (12) ---
        {'id': 'earth_01', 'name': '岩石打击',   'power': 95,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以岩石硬化的拳头打击', 'effects': []},
        {'id': 'earth_03', 'name': '地刺术',     'power': 115, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None,
         'description': '从地面升起尖刺贯穿目标', 'effects': []},
        {'id': 'earth_05', 'name': '地裂波',     'power': 150, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 20, 'roles': None,
         'description': '震裂大地波及全体', 'effects': []},
        {'id': 'earth_07', 'name': '巨岩崩落',   'power': 200, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 30, 'roles': None,
         'description': '召唤巨岩从天而降', 'effects': []},
        {'id': 'earth_09', 'name': '山崩地裂',   'power': 230, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 40, 'roles': None,
         'description': '山崩地裂冲击全体', 'effects': []},
        {'id': 'earth_11', 'name': '地龙翻身',   'power': 280, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '地龙翻身引发大范围地震', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'earth_12', 'name': '磐石之心',   'power': 35,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 55, 'roles': None,
         'description': '磐石般的意志大幅减伤', 'effects': [{'type': 'shield', 'value': 35, 'duration': 3}]},
        {'id': 'earth_13', 'name': '天崩地裂',   'power': 350, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 60, 'roles': None,
         'description': '天崩地裂之力撕碎战场', 'effects': []},
        {'id': 'earth_14', 'name': '泰山压顶',   'power': 400, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 65, 'roles': None,
         'description': '以泰山之重压碎目标', 'effects': [{'type': 'stun', 'chance': 0.4, 'duration': 1}]},
        {'id': 'earth_15', 'name': '山岳镇压',   'power': 320, 'type': 'physical', 'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '以山岳之力镇压全体', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'earth_16', 'name': '不动如山',   'power': 40,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 75, 'roles': None,
         'description': '不动如山反弹伤害免疫控制', 'effects': [{'type': 'shield', 'value': 40, 'duration': 3}, {'type': 'counter', 'value': 30}]},
        {'id': 'earth_17', 'name': '开天辟地',   'power': 420, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '开天辟地之力重塑战场', 'effects': [{'type': 'stun', 'chance': 0.4, 'duration': 1}]},
        # --- Lv5 分支 ---
        {'id': 'earth_02a', 'name': '大地之盾',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 5,  'roles': [_T, _W, _S],
         'description': '召唤大地之力形成护盾', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        {'id': 'earth_02b', 'name': '岩石射击',  'power': 105, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _A],
         'description': '投射岩石碎片远程打击', 'effects': []},
        # --- Lv15 分支 ---
        {'id': 'earth_04a', 'name': '岩铠',      'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 15, 'roles': [_T, _W],
         'description': '披上岩石铠甲大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}, {'type': 'buff_mdef', 'value': 30, 'duration': 3}]},
        {'id': 'earth_04b', 'name': '地裂矛',    'power': 125, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _S],
         'description': '凝聚大地之力形成魔法矛', 'effects': []},
        {'id': 'earth_04c', 'name': '沙暴突袭',  'power': 130, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_A],
         'description': '借沙暴掩护突袭目标', 'effects': [{'type': 'evasion_up', 'value': 15, 'duration': 1}]},
        # --- Lv25 分支 ---
        {'id': 'earth_06a', 'name': '石化打击',  'power': 180, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '石化之拳有概率眩晕', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'earth_06b', 'name': '大地祝福',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 25, 'roles': [_S],
         'description': '大地祝福治愈友方', 'effects': [{'type': 'buff_def', 'value': 10, 'duration': 2}]},
        {'id': 'earth_06c', 'name': '岩壁术',    'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 25, 'roles': [_T, _M],
         'description': '为全队构筑岩壁防御', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        # --- Lv35 分支 ---
        {'id': 'earth_08a', 'name': '大地恩赐',  'power': 25,  'type': 'heal',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_T, _S],
         'description': '大地馈赠回复并提升防御', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 2}]},
        {'id': 'earth_08b', 'name': '巨石拳',    'power': 215, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '以巨石之力猛击目标', 'effects': []},
        # --- Lv45 分支 ---
        {'id': 'earth_10a', 'name': '钢铁之壁',  'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队构筑钢铁之壁', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}]},
        {'id': 'earth_10b', 'name': '崩岩击',    'power': 270, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_W, _A],
         'description': '以岩石崩裂之力重击目标', 'effects': [{'type': 'stun', 'chance': 0.25, 'duration': 1}]},
        {'id': 'earth_10c', 'name': '大地之怒',  'power': 260, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M],
         'description': '大地之力震怒全场', 'effects': []},
    ],

    # ==================== 光 (24) ====================
    'light': [
        # --- 核心 (12) ---
        {'id': 'light_01', 'name': '圣光斩',     'power': 85,  'type': 'magic',    'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '圣光加持的斩击', 'effects': []},
        {'id': 'light_03', 'name': '审判之光',   'power': 120, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None,
         'description': '光之审判降于敌人', 'effects': []},
        {'id': 'light_05', 'name': '光明祝福',   'power': 15,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 20, 'roles': None,
         'description': '光之祝福提升全队属性', 'effects': [{'type': 'buff_atk', 'value': 10, 'duration': 3}, {'type': 'buff_def', 'value': 10, 'duration': 3}]},
        {'id': 'light_07', 'name': '光明审判',   'power': 160, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '圣光从天而降审判全体', 'effects': []},
        {'id': 'light_09', 'name': '天使之翼',   'power': 20,  'type': 'heal',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 40, 'roles': None,
         'description': '天使双翼全队回复并获得护盾', 'effects': [{'type': 'shield', 'value': 10, 'duration': 2}]},
        {'id': 'light_11', 'name': '神圣惩戒',   'power': 300, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '天罚降下惩戒邪恶', 'effects': []},
        {'id': 'light_12', 'name': '圣域展开',   'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '展开圣域全队减伤', 'effects': [{'type': 'shield', 'value': 25, 'duration': 3}]},
        {'id': 'light_13', 'name': '天堂制裁',   'power': 360, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 60, 'roles': None,
         'description': '天堂之力制裁全体敌人', 'effects': []},
        {'id': 'light_14', 'name': '复活之光',   'power': 50,  'type': 'heal',     'target': 'ally_single','cooldown': 5, 'unlock_level': 65, 'roles': None,
         'description': '强大圣光使濒死者重获新生', 'effects': [{'type': 'revive_pct', 'value': 30}]},
        {'id': 'light_15', 'name': '圣光风暴',   'power': 340, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '圣光风暴横扫全场', 'effects': []},
        {'id': 'light_16', 'name': '天使降临',   'power': 40,  'type': 'heal',     'target': 'ally_all',   'cooldown': 5, 'unlock_level': 75, 'roles': None,
         'description': '天使降临全队大幅治愈', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}]},
        {'id': 'light_17', 'name': '创世之光',   'power': 420, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '创世之光焚灭一切暗影', 'effects': []},
        # --- Lv5 分支 ---
        {'id': 'light_02a', 'name': '圣光术',    'power': 15,  'type': 'heal',     'target': 'ally_single','cooldown': 2, 'unlock_level': 5,  'roles': [_S, _M, _T],
         'description': '基础圣光治愈术', 'effects': []},
        {'id': 'light_02b', 'name': '圣光打击',  'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A],
         'description': '圣光附着的近战打击', 'effects': []},
        # --- Lv15 分支 ---
        {'id': 'light_04a', 'name': '圣盾术',    'power': 20,  'type': 'buff',     'target': 'ally_single','cooldown': 3, 'unlock_level': 15, 'roles': [_T, _S],
         'description': '为友方赋予圣光护盾', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'light_04b', 'name': '审判斩',    'power': 140, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A],
         'description': '圣光审判化为物理利刃', 'effects': []},
        {'id': 'light_04c', 'name': '光明箭',    'power': 135, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M],
         'description': '凝聚光明化为魔法箭矢', 'effects': []},
        # --- Lv25 分支 ---
        {'id': 'light_06a', 'name': '神圣一击',  'power': 185, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _M, _A],
         'description': '集中圣光的强力一击', 'effects': []},
        {'id': 'light_06b', 'name': '圣光护盾',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '全队获得圣光护盾减伤', 'effects': [{'type': 'shield', 'value': 20, 'duration': 3}]},
        # --- Lv35 分支 ---
        {'id': 'light_08a', 'name': '净化之光',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _M],
         'description': '净化之光治愈并清除异常', 'effects': [{'type': 'cleanse'}]},
        {'id': 'light_08b', 'name': '圣光剑气',  'power': 230, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 35, 'roles': [_W, _A, _T],
         'description': '将圣光化为剑气猛击', 'effects': []},
        # --- Lv45 分支 ---
        {'id': 'light_10a', 'name': '圣光洗礼',  'power': 25,  'type': 'heal',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_S, _M],
         'description': '圣光洗礼全队恢复大量生命', 'effects': []},
        {'id': 'light_10b', 'name': '神圣冲击',  'power': 260, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_W, _A],
         'description': '圣光化为冲击波猛击目标', 'effects': []},
        {'id': 'light_10c', 'name': '圣光壁垒',  'power': 35,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 45, 'roles': [_T],
         'description': '构筑圣光壁垒大幅减伤', 'effects': [{'type': 'shield', 'value': 35, 'duration': 3}, {'type': 'counter', 'value': 20}]},
    ],

    # ==================== 暗 (25) ====================
    'dark': [
        # --- 核心 (12) ---
        {'id': 'dark_01', 'name': '暗影斩',     'power': 90,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '暗影附着的武器斩击', 'effects': []},
        {'id': 'dark_03', 'name': '暗影刺',     'power': 120, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None,
         'description': '暗影之刺附带剧毒', 'effects': [{'type': 'poison', 'chance': 0.3, 'damage_pct': 4, 'duration': 3}]},
        {'id': 'dark_05', 'name': '暗影爆发',   'power': 160, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 20, 'roles': None,
         'description': '暗影能量爆发冲击全体', 'effects': []},
        {'id': 'dark_07', 'name': '暗黑之刃',   'power': 200, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 30, 'roles': None,
         'description': '暗黑之刃斩断一切', 'effects': []},
        {'id': 'dark_09', 'name': '暗影领域',   'power': 240, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 40, 'roles': None,
         'description': '展开暗影领域侵蚀全体', 'effects': [{'type': 'debuff_atk', 'value': 10, 'duration': 2}]},
        {'id': 'dark_11', 'name': '暗影风暴',   'power': 270, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '暗影风暴席卷全场', 'effects': []},
        {'id': 'dark_12', 'name': '腐蚀之雾',   'power': 230, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '弥漫腐蚀之雾毒害全体', 'effects': [{'type': 'poison', 'chance': 0.6, 'damage_pct': 6, 'duration': 3}]},
        {'id': 'dark_13', 'name': '冥界之门',   'power': 370, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 60, 'roles': None,
         'description': '开启冥界之门释放亡灵之力', 'effects': []},
        {'id': 'dark_14', 'name': '灵魂收割',   'power': 400, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 65, 'roles': None,
         'description': '收割灵魂对低血量目标倍增', 'effects': [{'type': 'execute', 'threshold': 30, 'bonus_mult': 1.5}]},
        {'id': 'dark_15', 'name': '黑暗吞噬',   'power': 350, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '黑暗吞噬一切光明', 'effects': [{'type': 'lifesteal', 'value': 20}]},
        {'id': 'dark_16', 'name': '末日审判',   'power': 450, 'type': 'magic',    'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '末日降临毁灭性暗影', 'effects': []},
        {'id': 'dark_17', 'name': '深渊降临',   'power': 420, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '深渊之力降临人间', 'effects': [{'type': 'debuff_def', 'value': 25, 'duration': 3}]},
        # --- Lv5 分支 ---
        {'id': 'dark_02a', 'name': '生命汲取',  'power': 100, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _A, _W],
         'description': '汲取生命力为自身回复', 'effects': [{'type': 'lifesteal', 'value': 30}]},
        {'id': 'dark_02b', 'name': '暗影守护',  'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 5,  'roles': [_T, _S],
         'description': '暗影凝聚为护盾提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        # --- Lv15 分支 ---
        {'id': 'dark_04a', 'name': '恐惧术',    'power': 15,  'type': 'debuff',   'target': 'single',     'cooldown': 3, 'unlock_level': 15, 'roles': [_M, _S],
         'description': '释放恐惧降低目标攻击', 'effects': [{'type': 'debuff_atk', 'value': 20, 'duration': 2}]},
        {'id': 'dark_04b', 'name': '暗影刺击',  'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A],
         'description': '暗影刺击要害', 'effects': [{'type': 'poison', 'chance': 0.25, 'damage_pct': 4, 'duration': 2}]},
        {'id': 'dark_04c', 'name': '暗影壁垒',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 15, 'roles': [_T],
         'description': '暗影化为壁垒大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}, {'type': 'buff_mdef', 'value': 25, 'duration': 3}]},
        # --- Lv25 分支 ---
        {'id': 'dark_06a', 'name': '诅咒之术',  'power': 20,  'type': 'debuff',   'target': 'all',        'cooldown': 4, 'unlock_level': 25, 'roles': [_M, _S],
         'description': '诅咒全体降低双防', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}, {'type': 'debuff_mdef', 'value': 15, 'duration': 2}]},
        {'id': 'dark_06b', 'name': '暗影连斩',  'power': 195, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '暗影中的连续利刃斩击', 'effects': []},
        {'id': 'dark_06c', 'name': '暗影吸收',  'power': 20,  'type': 'heal',     'target': 'self',       'cooldown': 4, 'unlock_level': 25, 'roles': [_T],
         'description': '吸收暗影能量转化为生命', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 2}]},
        # --- Lv35 分支 ---
        {'id': 'dark_08a', 'name': '灵魂汲取',  'power': 180, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 35, 'roles': [_M, _A, _W],
         'description': '汲取全体灵魂为自身回复', 'effects': [{'type': 'lifesteal', 'value': 25}]},
        {'id': 'dark_08b', 'name': '暗影祝福',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '暗影的另一面——全队增益', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}]},
        # --- Lv45 分支 ---
        {'id': 'dark_10a', 'name': '死亡凝视',  'power': 260, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_M, _A],
         'description': '死亡凝视削弱目标防御', 'effects': [{'type': 'debuff_def', 'value': 20, 'duration': 2}]},
        {'id': 'dark_10b', 'name': '暗影堡垒',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 45, 'roles': [_T],
         'description': '暗影化为堡垒极大减伤', 'effects': [{'type': 'shield', 'value': 35, 'duration': 3}]},
        {'id': 'dark_10c', 'name': '暗影治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 45, 'roles': [_S, _W],
         'description': '以暗影之力治愈友方', 'effects': []},
    ],
}


# ====================================================================
#  角色专属技能  (蓝卡3个 / 紫卡5个 / 金卡5个+1觉醒)
# ====================================================================

CHARACTER_EXCLUSIVE_SKILLS = {

    # ---------- 蓝卡 (rare) - 3 专属技能 ----------

    'miyamoto': [
        {'id': 'miyamoto_ex1', 'name': '二天一流',   'power': 150, 'type': 'physical', 'target': 'single',   'cooldown': 2, 'unlock_level': 1,
         'description': '双刀流秘技，同时双刀斩击', 'effects': [], 'is_exclusive': True},
        {'id': 'miyamoto_ex2', 'name': '无念无想',   'power': 30,  'type': 'buff',     'target': 'self',     'cooldown': 4, 'unlock_level': 40,
         'description': '进入无念境界，暴击率与攻击力大幅提升', 'effects': [{'type': 'buff_atk', 'value': 35, 'duration': 3}, {'type': 'buff_crit', 'value': 40, 'duration': 3}], 'is_exclusive': True},
        {'id': 'miyamoto_ex3', 'name': '最终之剑',   'power': 500, 'type': 'physical', 'target': 'single',   'cooldown': 4, 'unlock_level': 80,
         'description': '悟道之后的最终一剑，斩断一切', 'effects': [{'type': 'ignore_def', 'value': 30}], 'is_exclusive': True},
    ],

    'viking-ragnar': [
        {'id': 'ragnar_ex1', 'name': '维京冲锋',   'power': 140, 'type': 'physical', 'target': 'single',   'cooldown': 2, 'unlock_level': 1,
         'description': '狂暴的维京冲锋攻击', 'effects': [], 'is_exclusive': True},
        {'id': 'ragnar_ex2', 'name': '狂战士之怒', 'power': 35,  'type': 'buff',     'target': 'self',     'cooldown': 4, 'unlock_level': 40,
         'description': '进入狂暴状态，攻击与速度大幅提升', 'effects': [{'type': 'buff_atk', 'value': 40, 'duration': 3}, {'type': 'buff_spd', 'value': 30, 'duration': 3}], 'is_exclusive': True},
        {'id': 'ragnar_ex3', 'name': '诸神黄昏',   'power': 480, 'type': 'physical', 'target': 'all',      'cooldown': 5, 'unlock_level': 80,
         'description': '北欧末日降临，毁灭全体敌人', 'effects': [], 'is_exclusive': True},
    ],

    'robin-hood': [
        {'id': 'robin_ex1', 'name': '精准射击',   'power': 145, 'type': 'physical', 'target': 'single',   'cooldown': 2, 'unlock_level': 1,
         'description': '必定暴击的精准一箭', 'effects': [{'type': 'guaranteed_crit'}], 'is_exclusive': True},
        {'id': 'robin_ex2', 'name': '箭雨',       'power': 250, 'type': 'physical', 'target': 'all',      'cooldown': 3, 'unlock_level': 40,
         'description': '漫天箭雨覆盖战场', 'effects': [], 'is_exclusive': True},
        {'id': 'robin_ex3', 'name': '百步穿杨',   'power': 520, 'type': 'physical', 'target': 'single',   'cooldown': 4, 'unlock_level': 80,
         'description': '传说中百步穿杨的一箭，无视护甲', 'effects': [{'type': 'ignore_def', 'value': 50}], 'is_exclusive': True},
    ],

    # ---------- 紫卡 (epic) - 5 专属技能 ----------

    'guan-yu': [
        {'id': 'guanyu_ex1', 'name': '青龙偃月斩', 'power': 160, 'type': 'physical', 'target': 'single',   'cooldown': 2, 'unlock_level': 1,
         'description': '挥舞青龙偃月刀的强力斩击', 'effects': [], 'is_exclusive': True},
        {'id': 'guanyu_ex2', 'name': '过五关斩六将','power': 25,  'type': 'buff',     'target': 'self',     'cooldown': 3, 'unlock_level': 20,
         'description': '战意高涨，攻防双提升', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}, {'type': 'buff_def', 'value': 20, 'duration': 3}], 'is_exclusive': True},
        {'id': 'guanyu_ex3', 'name': '忠义之魂',   'power': 20,  'type': 'buff',     'target': 'ally_all', 'cooldown': 4, 'unlock_level': 40,
         'description': '忠义之魂鼓舞全队，提升攻击力', 'effects': [{'type': 'buff_atk', 'value': 20, 'duration': 3}], 'is_exclusive': True},
        {'id': 'guanyu_ex4', 'name': '武圣之威',   'power': 420, 'type': 'physical', 'target': 'single',   'cooldown': 3, 'unlock_level': 60,
         'description': '武圣全力一击，震慑天地', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}], 'is_exclusive': True},
        {'id': 'guanyu_ex5', 'name': '关公显圣',   'power': 380, 'type': 'physical', 'target': 'all',      'cooldown': 4, 'unlock_level': 80,
         'description': '武圣显灵，横扫全场并回复自身', 'effects': [{'type': 'lifesteal', 'value': 25}], 'is_exclusive': True},
    ],

    'hua-mulan': [
        {'id': 'mulan_ex1', 'name': '从军斩',     'power': 150, 'type': 'physical', 'target': 'single',   'cooldown': 2, 'unlock_level': 1,
         'description': '木兰英姿飒爽的利落斩击', 'effects': [], 'is_exclusive': True},
        {'id': 'mulan_ex2', 'name': '替父从军',   'power': 20,  'type': 'buff',     'target': 'self',     'cooldown': 3, 'unlock_level': 20,
         'description': '坚定信念提升防御与速度', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}, {'type': 'buff_spd', 'value': 25, 'duration': 3}], 'is_exclusive': True},
        {'id': 'mulan_ex3', 'name': '花舞连斩',   'power': 300, 'type': 'physical', 'target': 'single',   'cooldown': 3, 'unlock_level': 40,
         'description': '如花瓣飞舞般的连续斩击', 'effects': [], 'is_exclusive': True},
        {'id': 'mulan_ex4', 'name': '巾帼之怒',   'power': 380, 'type': 'physical', 'target': 'all',      'cooldown': 4, 'unlock_level': 60,
         'description': '巾帼不让须眉的全力爆发', 'effects': [], 'is_exclusive': True},
        {'id': 'mulan_ex5', 'name': '木兰无双',   'power': 450, 'type': 'physical', 'target': 'single',   'cooldown': 4, 'unlock_level': 80,
         'description': '木兰武技的极致，附带全队增益', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 2, 'target_scope': 'ally_all'}], 'is_exclusive': True},
    ],

    'arthur': [
        {'id': 'arthur_ex1', 'name': '誓约胜利之剑','power': 170, 'type': 'magic',   'target': 'single',   'cooldown': 2, 'unlock_level': 1,
         'description': 'Excalibur——圣剑的神圣斩击', 'effects': [], 'is_exclusive': True},
        {'id': 'arthur_ex2', 'name': '圆桌骑士',   'power': 20,  'type': 'buff',     'target': 'ally_all', 'cooldown': 3, 'unlock_level': 20,
         'description': '圆桌骑士之誓，全队防御提升', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}], 'is_exclusive': True},
        {'id': 'arthur_ex3', 'name': '圣剑光辉',   'power': 320, 'type': 'magic',    'target': 'all',      'cooldown': 3, 'unlock_level': 40,
         'description': 'Excalibur绽放光辉，圣光席卷全场', 'effects': [], 'is_exclusive': True},
        {'id': 'arthur_ex4', 'name': '不列颠守护', 'power': 30,  'type': 'buff',     'target': 'ally_all', 'cooldown': 4, 'unlock_level': 60,
         'description': '不列颠之王的守护，全队回复并获得护盾', 'effects': [{'type': 'shield', 'value': 20, 'duration': 3}], 'is_exclusive': True},
        {'id': 'arthur_ex5', 'name': '王之军势',   'power': 460, 'type': 'magic',    'target': 'all',      'cooldown': 4, 'unlock_level': 80,
         'description': '王之军势——圣光终焉之一击', 'effects': [], 'is_exclusive': True},
    ],

    'cao-cao': [
        {'id': 'caocao_ex1', 'name': '奸雄之刃',   'power': 155, 'type': 'physical', 'target': 'single',   'cooldown': 2, 'unlock_level': 1,
         'description': '暗影缠绕的枭雄之刃', 'effects': [], 'is_exclusive': True},
        {'id': 'caocao_ex2', 'name': '挟天子令诸侯','power': 20,  'type': 'debuff',   'target': 'all',      'cooldown': 4, 'unlock_level': 20,
         'description': '枭雄威压，削弱全体敌人攻防', 'effects': [{'type': 'debuff_atk', 'value': 15, 'duration': 2}, {'type': 'debuff_def', 'value': 15, 'duration': 2}], 'is_exclusive': True},
        {'id': 'caocao_ex3', 'name': '乱世奸雄',   'power': 30,  'type': 'buff',     'target': 'self',     'cooldown': 3, 'unlock_level': 40,
         'description': '枭雄觉醒，大幅提升攻击并附带吸血', 'effects': [{'type': 'buff_atk', 'value': 35, 'duration': 3}, {'type': 'lifesteal', 'value': 20}], 'is_exclusive': True},
        {'id': 'caocao_ex4', 'name': '魏武挥鞭',   'power': 400, 'type': 'physical', 'target': 'all',      'cooldown': 4, 'unlock_level': 60,
         'description': '魏武帝挥鞭而战，横扫全场吸取生命', 'effects': [{'type': 'lifesteal', 'value': 20}], 'is_exclusive': True},
        {'id': 'caocao_ex5', 'name': '天下归心',   'power': 460, 'type': 'physical', 'target': 'all',      'cooldown': 4, 'unlock_level': 80,
         'description': '天下归心——终极枭雄之力', 'effects': [{'type': 'lifesteal', 'value': 25}], 'is_exclusive': True},
    ],

    'cleopatra': [
        {'id': 'cleo_ex1', 'name': '尼罗河祝福',   'power': 30,  'type': 'heal',     'target': 'ally_single','cooldown': 2, 'unlock_level': 1,
         'description': '尼罗河之水的祝福治愈', 'effects': [], 'is_exclusive': True},
        {'id': 'cleo_ex2', 'name': '女王魅惑',     'power': 25,  'type': 'debuff',   'target': 'single',     'cooldown': 3, 'unlock_level': 20,
         'description': '女王的魅惑大幅削弱目标攻击', 'effects': [{'type': 'debuff_atk', 'value': 30, 'duration': 2}], 'is_exclusive': True},
        {'id': 'cleo_ex3', 'name': '王权之光',     'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 40,
         'description': '女王权杖之光，全队全属性提升', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}, {'type': 'buff_spd', 'value': 10, 'duration': 3}], 'is_exclusive': True},
        {'id': 'cleo_ex4', 'name': '尼罗河之怒',   'power': 350, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 60,
         'description': '尼罗河泛滥之力冲刷全场', 'effects': [], 'is_exclusive': True},
        {'id': 'cleo_ex5', 'name': '永恒女王',     'power': 40,  'type': 'heal',     'target': 'ally_all',   'cooldown': 5, 'unlock_level': 80,
         'description': '永恒女王的恩泽，全队大幅治愈并强化', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}], 'is_exclusive': True},
    ],

    # ---------- 金卡 (legendary) - 5专属 + 1觉醒 ----------

    'zhuge-liang': [
        {'id': 'zgl_ex1', 'name': '八卦阵',       'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 1,
         'description': '布下八卦阵法，全队防御大幅提升', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}], 'is_exclusive': True},
        {'id': 'zgl_ex2', 'name': '草船借箭',     'power': 280, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 20,
         'description': '以智谋借敌之箭反击，并提升自身', 'effects': [{'type': 'buff_atk', 'value': 20, 'duration': 2}], 'is_exclusive': True},
        {'id': 'zgl_ex3', 'name': '火烧赤壁',     'power': 400, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 40,
         'description': '赤壁之火重现，烈焰与洪水的双重毁灭', 'effects': [{'type': 'burn', 'chance': 0.6, 'damage_pct': 8, 'duration': 2}], 'is_exclusive': True},
        {'id': 'zgl_ex4', 'name': '空城计',       'power': 35,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 60,
         'description': '空城退敌，大幅提升闪避并反击', 'effects': [{'type': 'evasion_up', 'value': 80, 'duration': 2}, {'type': 'counter', 'value': 40}], 'is_exclusive': True},
        {'id': 'zgl_ex5', 'name': '七星灯',       'power': 50,  'type': 'heal',     'target': 'ally_all',   'cooldown': 5, 'unlock_level': 80,
         'description': '七星续命灯，全队大幅回复生命', 'effects': [], 'is_exclusive': True},
        {'id': 'zgl_awakening', 'name': '卧龙出山', 'power': 600, 'type': 'magic',   'target': 'all',        'cooldown': 6, 'unlock_level': 100,
         'description': '卧龙出山，天地变色！对全体敌人造成毁灭性伤害并强化全队',
         'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3, 'target_scope': 'ally_all'}, {'type': 'buff_def', 'value': 25, 'duration': 3, 'target_scope': 'ally_all'}],
         'is_exclusive': True, 'is_awakening': True},
    ],

    'joan-of-arc': [
        {'id': 'joan_ex1', 'name': '圣女祈祷',     'power': 25,  'type': 'heal',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 1,
         'description': '虔诚祈祷治愈全体友方', 'effects': [], 'is_exclusive': True},
        {'id': 'joan_ex2', 'name': '神启',         'power': 20,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 20,
         'description': '上天启示，全队全属性提升', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}, {'type': 'buff_spd', 'value': 10, 'duration': 3}], 'is_exclusive': True},
        {'id': 'joan_ex3', 'name': '圣旗飘扬',     'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 40,
         'description': '圣旗之下，全队攻防大幅提升并净化', 'effects': [{'type': 'buff_atk', 'value': 20, 'duration': 3}, {'type': 'buff_def', 'value': 20, 'duration': 3}, {'type': 'cleanse'}], 'is_exclusive': True},
        {'id': 'joan_ex4', 'name': '殉道之光',     'power': 45,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 60,
         'description': '以殉道精神治愈友方并赋予强力护盾', 'effects': [{'type': 'shield', 'value': 30, 'duration': 3}], 'is_exclusive': True},
        {'id': 'joan_ex5', 'name': '圣女降临',     'power': 380, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 80,
         'description': '圣女降临审判邪恶并治愈全队', 'effects': [{'type': 'lifesteal', 'value': 30}], 'is_exclusive': True},
        {'id': 'joan_awakening', 'name': '奇迹之火','power': 500, 'type': 'magic',    'target': 'all',        'cooldown': 6, 'unlock_level': 100,
         'description': '圣火燃烧一切不义！全队完全治愈，全体敌人遭受神圣裁决',
         'effects': [{'type': 'heal_all_pct', 'value': 100}],
         'is_exclusive': True, 'is_awakening': True},
    ],

    'genghis-khan': [
        {'id': 'khan_ex1', 'name': '铁骑冲锋',     'power': 180, 'type': 'physical', 'target': 'all',        'cooldown': 3, 'unlock_level': 1,
         'description': '蒙古铁骑冲锋践踏全体敌人', 'effects': [], 'is_exclusive': True},
        {'id': 'khan_ex2', 'name': '草原之王',     'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 20,
         'description': '草原之王的霸气，大幅提升攻击与速度', 'effects': [{'type': 'buff_atk', 'value': 35, 'duration': 3}, {'type': 'buff_spd', 'value': 30, 'duration': 3}], 'is_exclusive': True},
        {'id': 'khan_ex3', 'name': '万箭齐发',     'power': 350, 'type': 'physical', 'target': 'all',        'cooldown': 4, 'unlock_level': 40,
         'description': '万箭齐发覆盖战场', 'effects': [], 'is_exclusive': True},
        {'id': 'khan_ex4', 'name': '征服者之威',   'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 60,
         'description': '征服者的威势鼓舞全军', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}, {'type': 'buff_crit', 'value': 20, 'duration': 3}], 'is_exclusive': True},
        {'id': 'khan_ex5', 'name': '蒙古铁骑',     'power': 450, 'type': 'physical', 'target': 'all',        'cooldown': 4, 'unlock_level': 80,
         'description': '蒙古铁骑万马奔腾，全场毁灭', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}], 'is_exclusive': True},
        {'id': 'khan_awakening', 'name': '天之骄子','power': 650, 'type': 'physical', 'target': 'all',        'cooldown': 6, 'unlock_level': 100,
         'description': '长生天之子降世！全场毁灭性冲击并全队获得最强增益',
         'effects': [{'type': 'buff_atk', 'value': 30, 'duration': 3, 'target_scope': 'ally_all'}, {'type': 'buff_spd', 'value': 30, 'duration': 3, 'target_scope': 'ally_all'}],
         'is_exclusive': True, 'is_awakening': True},
    ],
}


# ====================================================================
#  角色被动天赋  (蓝卡及以上各拥有 1 个)
# ====================================================================

CHARACTER_PASSIVES = {
    # 蓝卡
    'miyamoto': {
        'id': 'miyamoto_passive', 'name': '剑圣之道',
        'description': '暴击率+15%，暴击伤害+30%',
        'effects': [{'type': 'passive_crit_rate', 'value': 15}, {'type': 'passive_crit_dmg', 'value': 30}],
    },
    'viking-ragnar': {
        'id': 'ragnar_passive', 'name': '北欧战魂',
        'description': 'HP低于30%时攻击力+40%',
        'effects': [{'type': 'passive_low_hp_atk', 'threshold': 30, 'value': 40}],
    },
    'robin-hood': {
        'id': 'robin_passive', 'name': '百发百中',
        'description': '对单体目标造成的伤害+20%',
        'effects': [{'type': 'passive_single_dmg', 'value': 20}],
    },
    # 紫卡
    'guan-yu': {
        'id': 'guanyu_passive', 'name': '武圣之躯',
        'description': 'HP+20%；受到致命伤害时有30%概率保留1HP',
        'effects': [{'type': 'passive_hp_pct', 'value': 20}, {'type': 'passive_endure', 'chance': 30}],
    },
    'hua-mulan': {
        'id': 'mulan_passive', 'name': '巾帼之志',
        'description': '速度+15%；击杀敌人后回复15%最大HP',
        'effects': [{'type': 'passive_spd_pct', 'value': 15}, {'type': 'passive_kill_heal', 'value': 15}],
    },
    'arthur': {
        'id': 'arthur_passive', 'name': '王者之气',
        'description': '全队防御+10%；自身光属性伤害+25%',
        'effects': [{'type': 'passive_team_def', 'value': 10}, {'type': 'passive_elem_dmg', 'element': 'light', 'value': 25}],
    },
    'cao-cao': {
        'id': 'caocao_passive', 'name': '乱世枭雄',
        'description': '攻击时有20%概率吸取伤害30%为HP',
        'effects': [{'type': 'passive_lifesteal', 'chance': 20, 'value': 30}],
    },
    'cleopatra': {
        'id': 'cleo_passive', 'name': '女王的庇护',
        'description': '治疗效果+30%；被治疗角色获得10%防御提升(2回合)',
        'effects': [{'type': 'passive_heal_boost', 'value': 30}, {'type': 'passive_heal_def', 'value': 10, 'duration': 2}],
    },
    # 金卡
    'zhuge-liang': {
        'id': 'zgl_passive', 'name': '卧龙之智',
        'description': '魔法攻击+25%；所有技能冷却-1回合',
        'effects': [{'type': 'passive_matk_pct', 'value': 25}, {'type': 'passive_cd_reduce', 'value': 1}],
    },
    'joan-of-arc': {
        'id': 'joan_passive', 'name': '圣女之光',
        'description': '全队最大HP+15%；每回合开始全队回复5%最大HP',
        'effects': [{'type': 'passive_team_hp', 'value': 15}, {'type': 'passive_regen', 'value': 5}],
    },
    'genghis-khan': {
        'id': 'khan_passive', 'name': '征服者之魂',
        'description': '攻击力+20%，速度+20%；击杀敌人后可额外行动一次',
        'effects': [{'type': 'passive_atk_pct', 'value': 20}, {'type': 'passive_spd_pct', 'value': 20}, {'type': 'passive_extra_turn_on_kill'}],
    },
}


# ====================================================================
#  计算属性（含品质加成）
# ====================================================================

def calculate_stats_with_rarity(base_stats, level, stars, breakthrough, rarity):
    """品质感知的属性计算
    Args:
        base_stats: {'hp':..., 'attack':..., ...} 或 {'stats': {...}}
        level: 角色等级 (1-100)
        stars: 星级
        breakthrough: 突破等级
        rarity: 'common' | 'rare' | 'epic' | 'legendary'
    """
    if 'stats' in base_stats:
        base_stats = base_stats['stats']

    cfg = RARITY_CONFIG.get(rarity, RARITY_CONFIG['common'])
    base_mult = cfg['base_stat_mult']
    growth = cfg['growth_per_level']

    level_mult = 1 + (level - 1) * growth
    star_mult = 1 + stars * 0.1
    bt_mult = 1 + breakthrough * 0.15

    total_mult = base_mult * level_mult * star_mult * bt_mult

    return {
        'hp': int(base_stats.get('hp', 1000) * total_mult),
        'max_hp': int(base_stats.get('hp', 1000) * total_mult),
        'attack': int(base_stats.get('attack', 100) * total_mult),
        'defense': int(base_stats.get('defense', 50) * total_mult),
        'magic_attack': int(base_stats.get('magic_attack', base_stats.get('attack', 100)) * total_mult),
        'magic_defense': int(base_stats.get('magic_defense', base_stats.get('defense', 50)) * total_mult),
        'speed': int(base_stats.get('speed', 100) * total_mult),
    }


# ====================================================================
#  核心函数：根据角色信息动态生成技能列表
# ====================================================================

def get_skills_for_character(character_id, level, rarity, role_type, element):
    """根据角色 ID / 等级 / 品质 / 职业 / 元素，返回当前等级可用的全部技能列表。

    返回格式: [{'id', 'name', 'power', 'type', 'element', 'target', 'cooldown', 'description', 'effects', ...}, ...]
    """
    skills = []
    cfg = RARITY_CONFIG.get(rarity, RARITY_CONFIG['common'])

    # --- 1. 共通元素技能 (按等级 + 职业过滤) ---
    pool = ELEMENT_SKILL_POOL.get(element, [])
    for sk in pool:
        if level < sk['unlock_level']:
            continue
        sk_roles = sk.get('roles')
        if sk_roles is not None and role_type not in sk_roles:
            continue
        if sk_roles is None:
            s = _apply_role_mod(sk, role_type)
        else:
            s = copy.deepcopy(sk)
        s['element'] = element
        s.pop('unlock_level', None)
        s.pop('roles', None)
        skills.append(s)

    # --- 2. 专属技能 (根据品质解锁表) ---
    excl_list = CHARACTER_EXCLUSIVE_SKILLS.get(character_id, [])
    unlock_levels = cfg['exclusive_unlock_levels'][:]
    if cfg.get('has_awakening') and cfg.get('awakening_level'):
        unlock_levels.append(cfg['awakening_level'])

    for idx, sk in enumerate(excl_list):
        if sk.get('is_awakening'):
            if cfg.get('has_awakening') and level >= cfg.get('awakening_level', 999):
                s = copy.deepcopy(sk)
                s['element'] = element
                s.pop('unlock_level', None)
                skills.append(s)
        else:
            req_lv = sk.get('unlock_level', 999)
            if level >= req_lv:
                s = copy.deepcopy(sk)
                s['element'] = element
                s.pop('unlock_level', None)
                skills.append(s)

    # --- 3. 被动天赋 (蓝卡+) ---
    if cfg['has_passive'] and character_id in CHARACTER_PASSIVES:
        passive = copy.deepcopy(CHARACTER_PASSIVES[character_id])
        passive['type'] = 'passive'
        passive['power'] = 0
        passive['element'] = element
        passive['target'] = 'self'
        passive['cooldown'] = 0
        passive['is_passive'] = True
        skills.append(passive)

    return skills


def get_skill_unlock_preview(character_id, rarity, role_type, element):
    """返回角色全部技能的解锁预览（用于前端展示）。
    格式: [{'unlock_level': N, 'skill': {...}, 'source': 'shared'|'exclusive'|'awakening'|'passive'}, ...]
    """
    result = []
    cfg = RARITY_CONFIG.get(rarity, RARITY_CONFIG['common'])

    pool = ELEMENT_SKILL_POOL.get(element, [])
    for sk in pool:
        sk_roles = sk.get('roles')
        if sk_roles is not None and role_type not in sk_roles:
            continue
        if sk_roles is None:
            s = _apply_role_mod(sk, role_type)
        else:
            s = copy.deepcopy(sk)
        s['element'] = element
        result.append({'unlock_level': sk['unlock_level'], 'skill': s, 'source': 'shared'})

    excl_list = CHARACTER_EXCLUSIVE_SKILLS.get(character_id, [])
    for sk in excl_list:
        s = copy.deepcopy(sk)
        s['element'] = element
        src = 'awakening' if sk.get('is_awakening') else 'exclusive'
        result.append({'unlock_level': sk.get('unlock_level', 1), 'skill': s, 'source': src})

    if cfg['has_passive'] and character_id in CHARACTER_PASSIVES:
        passive = copy.deepcopy(CHARACTER_PASSIVES[character_id])
        passive['type'] = 'passive'
        passive['power'] = 0
        passive['element'] = element
        passive['target'] = 'self'
        passive['cooldown'] = 0
        passive['is_passive'] = True
        result.append({'unlock_level': 1, 'skill': passive, 'source': 'passive'})

    result.sort(key=lambda x: x['unlock_level'])
    return result
