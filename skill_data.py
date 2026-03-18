# skill_data.py — 技能系统（数据库驱动）
"""
技能数据存储在 skill_templates 表中，本模块提供：
  - RARITY_CONFIG / ROLE_MODIFIERS 等配置常量
  - seed_skill_templates()  将种子数据写入数据库
  - get_skills_for_character()  运行时从数据库查询
  - calculate_stats_with_rarity()  品质感知属性计算
"""

import copy, json

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
    s = copy.deepcopy(skill_dict) if isinstance(skill_dict, dict) else skill_dict.copy()
    st = s.get('type', 'physical')
    if st in ('physical', 'magic') and s.get('power', 0) > 0:
        s['power'] = max(1, int(s['power'] * mod.get(st, 1.0)))
    elif st == 'heal':
        s['power'] = max(1, int(s['power'] * mod.get('heal', 1.0)))
    elif st == 'buff':
        s['power'] = max(1, int(s['power'] * mod.get('buff', 1.0)))
    elif st == 'debuff':
        s['power'] = max(1, int(s['power'] * mod.get('debuff', 1.0)))
    return s


# ====================================================================
#  属性计算（含品质加成）
# ====================================================================

def calculate_stats_with_rarity(base_stats, level, stars, breakthrough, rarity):
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
#  数据库查询函数
# ====================================================================

def get_skills_for_character(character_id, level, rarity, role_type, element):
    """从数据库查询角色当前等级可用的全部技能"""
    from models import SkillTemplate
    skills = []
    cfg = RARITY_CONFIG.get(rarity, RARITY_CONFIG['common'])

    # 1. 共通元素技能
    shared = SkillTemplate.query.filter(
        SkillTemplate.category == 'shared',
        SkillTemplate.element == element,
        SkillTemplate.unlock_level <= level,
    ).order_by(SkillTemplate.unlock_level).all()

    for sk in shared:
        if sk.roles and role_type not in sk.roles.split(','):
            continue
        d = sk.to_skill_dict()
        d['element'] = element
        if not sk.roles:
            d = _apply_role_mod(d, role_type)
        skills.append(d)

    # 2. 专属技能
    excl = SkillTemplate.query.filter(
        SkillTemplate.category == 'exclusive',
        SkillTemplate.character_id == character_id,
    ).order_by(SkillTemplate.unlock_level).all()
    for sk in excl:
        if level >= sk.unlock_level:
            d = sk.to_skill_dict()
            d['element'] = element
            skills.append(d)

    # 3. 觉醒技能
    if cfg.get('has_awakening') and level >= cfg.get('awakening_level', 999):
        awaken = SkillTemplate.query.filter(
            SkillTemplate.category == 'awakening',
            SkillTemplate.character_id == character_id,
        ).first()
        if awaken:
            d = awaken.to_skill_dict()
            d['element'] = element
            skills.append(d)

    # 4. 被动天赋
    if cfg['has_passive']:
        passive = SkillTemplate.query.filter(
            SkillTemplate.category == 'passive',
            SkillTemplate.character_id == character_id,
        ).first()
        if passive:
            d = passive.to_skill_dict()
            d['element'] = element
            skills.append(d)

    return skills


def get_skill_unlock_preview(character_id, rarity, role_type, element):
    """返回角色全部技能的解锁预览"""
    from models import SkillTemplate
    result = []
    cfg = RARITY_CONFIG.get(rarity, RARITY_CONFIG['common'])

    shared = SkillTemplate.query.filter(
        SkillTemplate.category == 'shared',
        SkillTemplate.element == element,
    ).order_by(SkillTemplate.unlock_level).all()
    for sk in shared:
        if sk.roles and role_type not in sk.roles.split(','):
            continue
        d = sk.to_skill_dict()
        d['element'] = element
        if not sk.roles:
            d = _apply_role_mod(d, role_type)
        result.append({'unlock_level': sk.unlock_level, 'skill': d, 'source': 'shared'})

    excl = SkillTemplate.query.filter(
        SkillTemplate.category == 'exclusive',
        SkillTemplate.character_id == character_id,
    ).order_by(SkillTemplate.unlock_level).all()
    for sk in excl:
        d = sk.to_skill_dict()
        d['element'] = element
        result.append({'unlock_level': sk.unlock_level, 'skill': d, 'source': 'exclusive'})

    if cfg.get('has_awakening'):
        awaken = SkillTemplate.query.filter(
            SkillTemplate.category == 'awakening',
            SkillTemplate.character_id == character_id,
        ).first()
        if awaken:
            d = awaken.to_skill_dict()
            d['element'] = element
            result.append({'unlock_level': awaken.unlock_level, 'skill': d, 'source': 'awakening'})

    if cfg['has_passive']:
        passive = SkillTemplate.query.filter(
            SkillTemplate.category == 'passive',
            SkillTemplate.character_id == character_id,
        ).first()
        if passive:
            d = passive.to_skill_dict()
            d['element'] = element
            result.append({'unlock_level': 1, 'skill': d, 'source': 'passive'})

    result.sort(key=lambda x: x['unlock_level'])
    return result


# ====================================================================
#  种子数据 + 初始化函数
# ====================================================================

_W = 'warrior'; _M = 'mage'; _A = 'assassin'; _T = 'tank'; _S = 'support'

_SEED_ELEMENT_SKILLS = {
    'fire': [
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
        {'id': 'fire_02a', 'name': '灼烧打击',  'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '灼热近战攻击，有概率灼烧', 'effects': [{'type': 'burn', 'chance': 0.3, 'damage_pct': 5, 'duration': 2}]},
        {'id': 'fire_02b', 'name': '火焰弹',    'power': 115, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射火焰弹远程轰炸目标', 'effects': [{'type': 'burn', 'chance': 0.25, 'damage_pct': 5, 'duration': 2}]},
        {'id': 'fire_04a', 'name': '烈焰斩',    'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _T],
         'description': '火焰附着的大力劈砍', 'effects': []},
        {'id': 'fire_04b', 'name': '烈焰箭',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S],
         'description': '射出烈焰之箭', 'effects': []},
        {'id': 'fire_06a', 'name': '焰爆连击',  'power': 180, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '火焰附着的连续打击', 'effects': []},
        {'id': 'fire_06b', 'name': '烈焰灵波',  'power': 190, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_M],
         'description': '凝聚灵力化为烈焰波动', 'effects': [{'type': 'burn', 'chance': 0.35, 'damage_pct': 6, 'duration': 2}]},
        {'id': 'fire_06c', 'name': '烈焰守护',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '以烈焰守护全队，提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'fire_08a', 'name': '烈焰之心',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '点燃心火大幅提升攻击力', 'effects': [{'type': 'buff_atk', 'value': 30, 'duration': 3}]},
        {'id': 'fire_08b', 'name': '火焰治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '以温暖的火焰治愈友方', 'effects': []},
        {'id': 'fire_10a', 'name': '火墙术',    'power': 200, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '烈火之墙横扫战场', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}]},
        {'id': 'fire_10b', 'name': '烈焰庇护',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队获得烈焰护盾减伤', 'effects': [{'type': 'shield', 'value': 20, 'duration': 3}]},
        {'id': 'fire_10c', 'name': '影焰突袭',  'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '暗影火焰加持的暴击突袭', 'effects': [{'type': 'ignore_def', 'value': 20}]},
    ],
    'water': [
        {'id': 'water_01', 'name': '水流斩',     'power': 85,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None, 'description': '以高压水流强化的武器劈砍', 'effects': []},
        {'id': 'water_03', 'name': '水盾术',     'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 10, 'roles': None, 'description': '凝聚水盾提升防御并微量回复', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}, {'type': 'heal_pct', 'value': 8}]},
        {'id': 'water_05', 'name': '潮汐之力',   'power': 160, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None, 'description': '引动潮汐之力冲击目标', 'effects': []},
        {'id': 'water_07', 'name': '急流漩涡',   'power': 150, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None, 'description': '召唤急流漩涡席卷全场', 'effects': [{'type': 'debuff_spd', 'value': 10, 'duration': 2}]},
        {'id': 'water_09', 'name': '怒涛冲击',   'power': 245, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None, 'description': '激发怒涛之力猛击目标', 'effects': []},
        {'id': 'water_11', 'name': '水龙弹',     'power': 290, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None, 'description': '化水为龙轰击目标', 'effects': []},
        {'id': 'water_12', 'name': '水牢术',     'power': 240, 'type': 'magic',    'target': 'single',     'cooldown': 4, 'unlock_level': 55, 'roles': None, 'description': '以水牢困住目标并持续伤害', 'effects': [{'type': 'debuff_spd', 'value': 20, 'duration': 2}]},
        {'id': 'water_13', 'name': '深海之怒',   'power': 370, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None, 'description': '引动深海之力碾碎目标', 'effects': []},
        {'id': 'water_14', 'name': '治愈之雨',   'power': 30,  'type': 'heal',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 65, 'roles': None, 'description': '降下治愈甘霖治愈全体', 'effects': []},
        {'id': 'water_15', 'name': '海啸冲击',   'power': 340, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None, 'description': '掀起滔天巨浪淹没全场', 'effects': []},
        {'id': 'water_16', 'name': '深渊水压',   'power': 440, 'type': 'magic',    'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None, 'description': '深渊级水压碾压目标', 'effects': [{'type': 'ignore_def', 'value': 25}]},
        {'id': 'water_17', 'name': '沧海横流',   'power': 400, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None, 'description': '沧海之力倾泻而出', 'effects': [{'type': 'debuff_def', 'value': 20, 'duration': 2}]},
        {'id': 'water_02a', 'name': '水流打击',  'power': 105, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T], 'description': '水流加持的近战攻击', 'effects': []},
        {'id': 'water_02b', 'name': '水弹术',    'power': 110, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S], 'description': '发射高压水弹远程轰击目标', 'effects': []},
        {'id': 'water_04a', 'name': '水甲术',    'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 15, 'roles': [_W, _T], 'description': '水流凝聚铠甲大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}, {'type': 'buff_mdef', 'value': 20, 'duration': 3}]},
        {'id': 'water_04b', 'name': '水柱术',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S], 'description': '喷射高压水柱冲击目标', 'effects': []},
        {'id': 'water_06a', 'name': '激流拳',    'power': 175, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A], 'description': '激流加持的连续拳击', 'effects': []},
        {'id': 'water_06b', 'name': '水幕弹幕',  'power': 170, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M], 'description': '水幕弹幕覆盖全场', 'effects': [{'type': 'debuff_spd', 'value': 10, 'duration': 2}]},
        {'id': 'water_06c', 'name': '潮汐祝福',  'power': 20,  'type': 'heal',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S], 'description': '潮汐之力祝福全体回复', 'effects': []},
        {'id': 'water_08a', 'name': '水流武装',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A], 'description': '水流强化武器提升攻击与速度', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}, {'type': 'buff_spd', 'value': 15, 'duration': 3}]},
        {'id': 'water_08b', 'name': '治愈之泉',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T, _M], 'description': '召唤清泉治愈一名友方', 'effects': []},
        {'id': 'water_10a', 'name': '潮汐涌动',  'power': 260, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W], 'description': '潮汐涌动冲刷全体敌人', 'effects': [{'type': 'debuff_spd', 'value': 15, 'duration': 2}]},
        {'id': 'water_10b', 'name': '水盾庇护',  'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S], 'description': '全队获得水盾大幅减伤', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}]},
        {'id': 'water_10c', 'name': '水影连刺',  'power': 240, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A], 'description': '水影闪烁中的连续穿刺', 'effects': []},
    ],
    'flying': [
        {'id': 'fly_01', 'name': '风刃突袭',   'power': 85,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None, 'description': '以风之力强化的利刃突袭', 'effects': []},
        {'id': 'fly_03', 'name': '滑翔斩',     'power': 115, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None, 'description': '从空中滑翔而下的高速斩击', 'effects': []},
        {'id': 'fly_05', 'name': '俯冲打击',   'power': 165, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None, 'description': '从高空俯冲而下重击目标', 'effects': []},
        {'id': 'fly_07', 'name': '旋风之翼',   'power': 155, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None, 'description': '展开双翼掀起旋风席卷全场', 'effects': [{'type': 'debuff_spd', 'value': 10, 'duration': 2}]},
        {'id': 'fly_09', 'name': '天空利刃',   'power': 255, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None, 'description': '凝聚风刃从天而降斩裂目标', 'effects': []},
        {'id': 'fly_11', 'name': '暴风突袭',   'power': 285, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None, 'description': '化身暴风猛冲目标', 'effects': [{'type': 'buff_spd', 'value': 15, 'duration': 1}]},
        {'id': 'fly_12', 'name': '飓风领域',   'power': 245, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None, 'description': '展开飓风领域撕裂全场', 'effects': [{'type': 'debuff_spd', 'value': 15, 'duration': 2}]},
        {'id': 'fly_13', 'name': '天翔龙闪',   'power': 360, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None, 'description': '翱翔天际的龙形闪击', 'effects': []},
        {'id': 'fly_14', 'name': '御风术',     'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 65, 'roles': None, 'description': '御风而行提升速度与闪避', 'effects': [{'type': 'buff_spd', 'value': 25, 'duration': 3}, {'type': 'evasion_up', 'value': 30, 'duration': 2}]},
        {'id': 'fly_15', 'name': '龙卷天降',   'power': 335, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None, 'description': '从天而降的巨型龙卷吞噬全场', 'effects': [{'type': 'debuff_spd', 'value': 20, 'duration': 2}]},
        {'id': 'fly_16', 'name': '天坠一击',   'power': 435, 'type': 'physical', 'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None, 'description': '从苍穹之巅坠击贯穿一切', 'effects': [{'type': 'ignore_def', 'value': 30}]},
        {'id': 'fly_17', 'name': '苍穹覆灭',   'power': 405, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None, 'description': '天空之力倾泻而下毁灭一切', 'effects': [{'type': 'debuff_spd', 'value': 25, 'duration': 2}]},
        {'id': 'fly_02a', 'name': '疾风步法',  'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 2, 'unlock_level': 5,  'roles': [_A, _W, _M], 'description': '提升自身速度先发制人', 'effects': [{'type': 'buff_spd', 'value': 20, 'duration': 3}]},
        {'id': 'fly_02b', 'name': '风之护佑',  'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 5,  'roles': [_T, _S], 'description': '风之护盾提升防御与闪避', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 3}, {'type': 'evasion_up', 'value': 15, 'duration': 3}]},
        {'id': 'fly_04a', 'name': '空中斩击',  'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A], 'description': '从空中急坠的穿甲斩击', 'effects': [{'type': 'ignore_def', 'value': 10}]},
        {'id': 'fly_04b', 'name': '风刃术',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _S, _T], 'description': '凝聚风刃远程切割目标', 'effects': []},
        {'id': 'fly_06a', 'name': '鹰眼聚焦',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 25, 'roles': [_A, _W], 'description': '鹰眼锁定提升暴击与闪避', 'effects': [{'type': 'buff_crit', 'value': 25, 'duration': 3}, {'type': 'evasion_up', 'value': 20, 'duration': 3}]},
        {'id': 'fly_06b', 'name': '风之守护',  'power': 20,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 25, 'roles': [_T, _S], 'description': '全队获得风之守护提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'fly_06c', 'name': '风暴连射',  'power': 185, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M], 'description': '连续发射风暴弹幕横扫全场', 'effects': []},
        {'id': 'fly_08a', 'name': '追风之术',  'power': 20,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 35, 'roles': [_S, _M], 'description': '全队速度大幅提升', 'effects': [{'type': 'buff_spd', 'value': 20, 'duration': 3}]},
        {'id': 'fly_08b', 'name': '猛禽突击',  'power': 220, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 35, 'roles': [_W, _A, _T], 'description': '如猛禽般高速突击目标', 'effects': []},
        {'id': 'fly_10a', 'name': '飞翼结界',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S], 'description': '全队获得风之结界提升闪避', 'effects': [{'type': 'evasion_up', 'value': 25, 'duration': 3}]},
        {'id': 'fly_10b', 'name': '裂空斩',    'power': 260, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_W, _A], 'description': '斩裂天空的极致一击', 'effects': [{'type': 'ignore_def', 'value': 15}]},
        {'id': 'fly_10c', 'name': '暴风肆虐',  'power': 255, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M], 'description': '召唤暴风肆虐全场', 'effects': [{'type': 'debuff_spd', 'value': 15, 'duration': 2}]},
    ],
    'earth': [
        {'id': 'earth_01', 'name': '岩石打击',   'power': 95,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None, 'description': '以岩石硬化的拳头打击', 'effects': []},
        {'id': 'earth_03', 'name': '地刺术',     'power': 115, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None, 'description': '从地面升起尖刺贯穿目标', 'effects': []},
        {'id': 'earth_05', 'name': '地裂波',     'power': 150, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 20, 'roles': None, 'description': '震裂大地波及全体', 'effects': []},
        {'id': 'earth_07', 'name': '巨岩崩落',   'power': 200, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 30, 'roles': None, 'description': '召唤巨岩从天而降', 'effects': []},
        {'id': 'earth_09', 'name': '山崩地裂',   'power': 230, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 40, 'roles': None, 'description': '山崩地裂冲击全体', 'effects': []},
        {'id': 'earth_11', 'name': '地龙翻身',   'power': 280, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 50, 'roles': None, 'description': '地龙翻身引发大范围地震', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'earth_12', 'name': '磐石之心',   'power': 35,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 55, 'roles': None, 'description': '磐石般的意志大幅减伤', 'effects': [{'type': 'shield', 'value': 35, 'duration': 3}]},
        {'id': 'earth_13', 'name': '天崩地裂',   'power': 350, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 60, 'roles': None, 'description': '天崩地裂之力撕碎战场', 'effects': []},
        {'id': 'earth_14', 'name': '泰山压顶',   'power': 400, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 65, 'roles': None, 'description': '以泰山之重压碎目标', 'effects': [{'type': 'stun', 'chance': 0.4, 'duration': 1}]},
        {'id': 'earth_15', 'name': '山岳镇压',   'power': 320, 'type': 'physical', 'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None, 'description': '以山岳之力镇压全体', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'earth_16', 'name': '不动如山',   'power': 40,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 75, 'roles': None, 'description': '不动如山反弹伤害免疫控制', 'effects': [{'type': 'shield', 'value': 40, 'duration': 3}, {'type': 'counter', 'value': 30}]},
        {'id': 'earth_17', 'name': '开天辟地',   'power': 420, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None, 'description': '开天辟地之力重塑战场', 'effects': [{'type': 'stun', 'chance': 0.4, 'duration': 1}]},
        {'id': 'earth_02a', 'name': '大地之盾',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 5,  'roles': [_T, _W, _S], 'description': '召唤大地之力形成护盾', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        {'id': 'earth_02b', 'name': '岩石射击',  'power': 105, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _A], 'description': '投射岩石碎片远程打击', 'effects': []},
        {'id': 'earth_04a', 'name': '岩铠',      'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 15, 'roles': [_T, _W], 'description': '披上岩石铠甲大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}, {'type': 'buff_mdef', 'value': 30, 'duration': 3}]},
        {'id': 'earth_04b', 'name': '地裂矛',    'power': 125, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _S], 'description': '凝聚大地之力形成魔法矛', 'effects': []},
        {'id': 'earth_04c', 'name': '沙暴突袭',  'power': 130, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_A], 'description': '借沙暴掩护突袭目标', 'effects': [{'type': 'evasion_up', 'value': 15, 'duration': 1}]},
        {'id': 'earth_06a', 'name': '石化打击',  'power': 180, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A], 'description': '石化之拳有概率眩晕', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'earth_06b', 'name': '大地祝福',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 25, 'roles': [_S], 'description': '大地祝福治愈友方', 'effects': [{'type': 'buff_def', 'value': 10, 'duration': 2}]},
        {'id': 'earth_06c', 'name': '岩壁术',    'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 25, 'roles': [_T, _M], 'description': '为全队构筑岩壁防御', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        {'id': 'earth_08a', 'name': '大地恩赐',  'power': 25,  'type': 'heal',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_T, _S], 'description': '大地馈赠回复并提升防御', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 2}]},
        {'id': 'earth_08b', 'name': '巨石拳',    'power': 215, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 35, 'roles': [_W, _A, _M], 'description': '以巨石之力猛击目标', 'effects': []},
        {'id': 'earth_10a', 'name': '钢铁之壁',  'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S], 'description': '全队构筑钢铁之壁', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}]},
        {'id': 'earth_10b', 'name': '崩岩击',    'power': 270, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_W, _A], 'description': '岩石崩裂之力重击目标', 'effects': [{'type': 'stun', 'chance': 0.25, 'duration': 1}]},
        {'id': 'earth_10c', 'name': '大地之怒',  'power': 260, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M], 'description': '大地之力震怒全场', 'effects': []},
    ],
    'light': [
        {'id': 'light_01', 'name': '圣光斩',     'power': 85,  'type': 'magic',    'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None, 'description': '圣光加持的斩击', 'effects': []},
        {'id': 'light_03', 'name': '审判之光',   'power': 120, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None, 'description': '光之审判降于敌人', 'effects': []},
        {'id': 'light_05', 'name': '光明祝福',   'power': 15,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 20, 'roles': None, 'description': '光之祝福提升全队属性', 'effects': [{'type': 'buff_atk', 'value': 10, 'duration': 3}, {'type': 'buff_def', 'value': 10, 'duration': 3}]},
        {'id': 'light_07', 'name': '光明审判',   'power': 160, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None, 'description': '圣光从天而降审判全体', 'effects': []},
        {'id': 'light_09', 'name': '天使之翼',   'power': 20,  'type': 'heal',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 40, 'roles': None, 'description': '天使双翼全队回复并获得护盾', 'effects': [{'type': 'shield', 'value': 10, 'duration': 2}]},
        {'id': 'light_11', 'name': '神圣惩戒',   'power': 300, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None, 'description': '天罚降下惩戒邪恶', 'effects': []},
        {'id': 'light_12', 'name': '圣域展开',   'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 55, 'roles': None, 'description': '展开圣域全队减伤', 'effects': [{'type': 'shield', 'value': 25, 'duration': 3}]},
        {'id': 'light_13', 'name': '天堂制裁',   'power': 360, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 60, 'roles': None, 'description': '天堂之力制裁全体敌人', 'effects': []},
        {'id': 'light_14', 'name': '复活之光',   'power': 50,  'type': 'heal',     'target': 'ally_single','cooldown': 5, 'unlock_level': 65, 'roles': None, 'description': '强大圣光使濒死者重获新生', 'effects': [{'type': 'revive_pct', 'value': 30}]},
        {'id': 'light_15', 'name': '圣光风暴',   'power': 340, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None, 'description': '圣光风暴横扫全场', 'effects': []},
        {'id': 'light_16', 'name': '天使降临',   'power': 40,  'type': 'heal',     'target': 'ally_all',   'cooldown': 5, 'unlock_level': 75, 'roles': None, 'description': '天使降临全队大幅治愈', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}]},
        {'id': 'light_17', 'name': '创世之光',   'power': 420, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None, 'description': '创世之光焚灭一切暗影', 'effects': []},
        {'id': 'light_02a', 'name': '圣光术',    'power': 15,  'type': 'heal',     'target': 'ally_single','cooldown': 2, 'unlock_level': 5,  'roles': [_S, _M, _T], 'description': '基础圣光治愈术', 'effects': []},
        {'id': 'light_02b', 'name': '圣光打击',  'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A], 'description': '圣光附着的近战打击', 'effects': []},
        {'id': 'light_04a', 'name': '圣盾术',    'power': 20,  'type': 'buff',     'target': 'ally_single','cooldown': 3, 'unlock_level': 15, 'roles': [_T, _S], 'description': '为友方赋予圣光护盾', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'light_04b', 'name': '审判斩',    'power': 140, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A], 'description': '圣光审判化为物理利刃', 'effects': []},
        {'id': 'light_04c', 'name': '光明箭',    'power': 135, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M], 'description': '凝聚光明化为魔法箭矢', 'effects': []},
        {'id': 'light_06a', 'name': '神圣一击',  'power': 185, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _M, _A], 'description': '集中圣光的强力一击', 'effects': []},
        {'id': 'light_06b', 'name': '圣光护盾',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 25, 'roles': [_T, _S], 'description': '全队获得圣光护盾减伤', 'effects': [{'type': 'shield', 'value': 20, 'duration': 3}]},
        {'id': 'light_08a', 'name': '净化之光',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _M], 'description': '净化之光治愈并清除异常', 'effects': [{'type': 'cleanse'}]},
        {'id': 'light_08b', 'name': '圣光剑气',  'power': 230, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 35, 'roles': [_W, _A, _T], 'description': '将圣光化为剑气猛击', 'effects': []},
        {'id': 'light_10a', 'name': '圣光洗礼',  'power': 25,  'type': 'heal',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_S, _M], 'description': '圣光洗礼全队恢复大量生命', 'effects': []},
        {'id': 'light_10b', 'name': '神圣冲击',  'power': 260, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_W, _A], 'description': '圣光化为冲击波猛击目标', 'effects': []},
        {'id': 'light_10c', 'name': '圣光壁垒',  'power': 35,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 45, 'roles': [_T], 'description': '构筑圣光壁垒大幅减伤', 'effects': [{'type': 'shield', 'value': 35, 'duration': 3}, {'type': 'counter', 'value': 20}]},
    ],
    'dark': [
        {'id': 'dark_01', 'name': '暗影斩',     'power': 90,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None, 'description': '暗影附着的武器斩击', 'effects': []},
        {'id': 'dark_03', 'name': '暗影刺',     'power': 120, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None, 'description': '暗影之刺附带剧毒', 'effects': [{'type': 'poison', 'chance': 0.3, 'damage_pct': 4, 'duration': 3}]},
        {'id': 'dark_05', 'name': '暗影爆发',   'power': 160, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 20, 'roles': None, 'description': '暗影能量爆发冲击全体', 'effects': []},
        {'id': 'dark_07', 'name': '暗黑之刃',   'power': 200, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 30, 'roles': None, 'description': '暗黑之刃斩断一切', 'effects': []},
        {'id': 'dark_09', 'name': '暗影领域',   'power': 240, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 40, 'roles': None, 'description': '展开暗影领域侵蚀全体', 'effects': [{'type': 'debuff_atk', 'value': 10, 'duration': 2}]},
        {'id': 'dark_11', 'name': '暗影风暴',   'power': 270, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 50, 'roles': None, 'description': '暗影风暴席卷全场', 'effects': []},
        {'id': 'dark_12', 'name': '腐蚀之雾',   'power': 230, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None, 'description': '弥漫腐蚀之雾毒害全体', 'effects': [{'type': 'poison', 'chance': 0.6, 'damage_pct': 6, 'duration': 3}]},
        {'id': 'dark_13', 'name': '冥界之门',   'power': 370, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 60, 'roles': None, 'description': '开启冥界之门释放亡灵之力', 'effects': []},
        {'id': 'dark_14', 'name': '灵魂收割',   'power': 400, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 65, 'roles': None, 'description': '收割灵魂对低血量目标倍增', 'effects': [{'type': 'execute', 'threshold': 30, 'bonus_mult': 1.5}]},
        {'id': 'dark_15', 'name': '黑暗吞噬',   'power': 350, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None, 'description': '黑暗吞噬一切光明', 'effects': [{'type': 'lifesteal', 'value': 20}]},
        {'id': 'dark_16', 'name': '末日审判',   'power': 450, 'type': 'magic',    'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None, 'description': '末日降临毁灭性暗影', 'effects': []},
        {'id': 'dark_17', 'name': '深渊降临',   'power': 420, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None, 'description': '深渊之力降临人间', 'effects': [{'type': 'debuff_def', 'value': 25, 'duration': 3}]},
        {'id': 'dark_02a', 'name': '生命汲取',  'power': 100, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _A, _W], 'description': '汲取生命力为自身回复', 'effects': [{'type': 'lifesteal', 'value': 30}]},
        {'id': 'dark_02b', 'name': '暗影守护',  'power': 20,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 5,  'roles': [_T, _S], 'description': '暗影凝聚为护盾提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'dark_04a', 'name': '恐惧术',    'power': 15,  'type': 'debuff',   'target': 'single',     'cooldown': 3, 'unlock_level': 15, 'roles': [_M, _S], 'description': '释放恐惧降低目标攻击', 'effects': [{'type': 'debuff_atk', 'value': 20, 'duration': 2}]},
        {'id': 'dark_04b', 'name': '暗影刺击',  'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A], 'description': '暗影刺击要害', 'effects': [{'type': 'poison', 'chance': 0.25, 'damage_pct': 4, 'duration': 2}]},
        {'id': 'dark_04c', 'name': '暗影壁垒',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 15, 'roles': [_T], 'description': '暗影化为壁垒大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}, {'type': 'buff_mdef', 'value': 25, 'duration': 3}]},
        {'id': 'dark_06a', 'name': '诅咒之术',  'power': 20,  'type': 'debuff',   'target': 'all',        'cooldown': 4, 'unlock_level': 25, 'roles': [_M, _S], 'description': '诅咒全体降低双防', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}, {'type': 'debuff_mdef', 'value': 15, 'duration': 2}]},
        {'id': 'dark_06b', 'name': '暗影连斩',  'power': 195, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A], 'description': '暗影中的连续利刃斩击', 'effects': []},
        {'id': 'dark_06c', 'name': '暗影吸收',  'power': 20,  'type': 'heal',     'target': 'self',       'cooldown': 4, 'unlock_level': 25, 'roles': [_T], 'description': '吸收暗影能量转化为生命', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 2}]},
        {'id': 'dark_08a', 'name': '灵魂汲取',  'power': 180, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 35, 'roles': [_M, _A, _W], 'description': '汲取全体灵魂为自身回复', 'effects': [{'type': 'lifesteal', 'value': 25}]},
        {'id': 'dark_08b', 'name': '暗影祝福',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 35, 'roles': [_S, _T], 'description': '暗影的另一面——全队增益', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}]},
        {'id': 'dark_10a', 'name': '死亡凝视',  'power': 260, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_M, _A], 'description': '死亡凝视削弱目标防御', 'effects': [{'type': 'debuff_def', 'value': 20, 'duration': 2}]},
        {'id': 'dark_10b', 'name': '暗影堡垒',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 45, 'roles': [_T], 'description': '暗影化为堡垒极大减伤', 'effects': [{'type': 'shield', 'value': 35, 'duration': 3}]},
        {'id': 'dark_10c', 'name': '暗影治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 45, 'roles': [_S, _W], 'description': '以暗影之力治愈友方', 'effects': []},
    ],
    'ice': [
        {'id': 'ice_01', 'name': '冰霜突刺',   'power': 90,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以冰霜覆盖武器突刺敌人', 'effects': []},
        {'id': 'ice_03', 'name': '冰霜护盾',   'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 10, 'roles': None,
         'description': '凝聚冰霜护盾提升防御', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        {'id': 'ice_05', 'name': '冰刺术',     'power': 160, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '从地面升起冰刺贯穿目标', 'effects': [{'type': 'freeze', 'chance': 0.3, 'duration': 1}]},
        {'id': 'ice_07', 'name': '暴风雪',     'power': 150, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '降下暴风雪覆盖全场', 'effects': [{'type': 'slow', 'chance': 0.4, 'value': 15, 'duration': 2}]},
        {'id': 'ice_09', 'name': '冰霜囚笼',   'power': 250, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '冰霜牢笼囚禁目标', 'effects': [{'type': 'freeze', 'chance': 0.4, 'duration': 1}]},
        {'id': 'ice_11', 'name': '冰川冲击',   'power': 290, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '化冰为剑猛力冲击', 'effects': []},
        {'id': 'ice_12', 'name': '冰封领域',   'power': 245, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '展开绝对冰域冻结全场', 'effects': [{'type': 'freeze', 'chance': 0.4, 'duration': 1}]},
        {'id': 'ice_13', 'name': '冰神之怒',   'power': 370, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '引动冰神之力碾碎目标', 'effects': [{'type': 'freeze', 'chance': 0.35, 'duration': 1}]},
        {'id': 'ice_14', 'name': '冰晶治愈',   'power': 35,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '冰晶共鸣治愈友方', 'effects': [{'type': 'shield', 'value': 15, 'duration': 2}]},
        {'id': 'ice_15', 'name': '极寒风暴',   'power': 340, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '释放极寒风暴席卷全场', 'effects': [{'type': 'slow', 'chance': 0.5, 'value': 20, 'duration': 2}]},
        {'id': 'ice_16', 'name': '绝对零度',   'power': 440, 'type': 'magic',    'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '将目标冷冻至绝对零度', 'effects': [{'type': 'freeze', 'chance': 0.6, 'duration': 2}]},
        {'id': 'ice_17', 'name': '永冻极地',   'power': 410, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '极地寒流吞噬一切', 'effects': [{'type': 'freeze', 'chance': 0.5, 'duration': 1}, {'type': 'slow', 'chance': 1.0, 'value': 20, 'duration': 2}]},
        {'id': 'ice_02a', 'name': '寒冰打击',  'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '寒冰附体的近战攻击', 'effects': [{'type': 'slow', 'chance': 0.3, 'value': 15, 'duration': 2}]},
        {'id': 'ice_02b', 'name': '冰霜射线',  'power': 115, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射冰霜射线远程冻结目标', 'effects': [{'type': 'freeze', 'chance': 0.2, 'duration': 1}]},
        {'id': 'ice_04a', 'name': '寒冰护甲',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 15, 'roles': [_W, _T],
         'description': '冰晶覆体大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}, {'type': 'buff_mdef', 'value': 20, 'duration': 3}]},
        {'id': 'ice_04b', 'name': '冰锥术',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S],
         'description': '发射锋利冰锥刺穿目标', 'effects': []},
        {'id': 'ice_06a', 'name': '冰封打击',  'power': 180, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '冰封之拳有概率冻结目标', 'effects': [{'type': 'freeze', 'chance': 0.25, 'duration': 1}]},
        {'id': 'ice_06b', 'name': '冰晶爆破',  'power': 185, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '引爆冰晶碎片横扫全场', 'effects': [{'type': 'slow', 'chance': 0.4, 'value': 15, 'duration': 2}]},
        {'id': 'ice_06c', 'name': '霜冻祝福',  'power': 20,  'type': 'heal',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '寒冰之力祝福全体回复', 'effects': []},
        {'id': 'ice_08a', 'name': '寒冰武装',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '冰晶强化武器提升攻击与暴击', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}, {'type': 'buff_crit', 'value': 20, 'duration': 3}]},
        {'id': 'ice_08b', 'name': '冰泉治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '召唤冰泉治愈一名友方', 'effects': []},
        {'id': 'ice_10a', 'name': '冰晶风暴',  'power': 260, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '冰晶风暴冲刷全体敌人', 'effects': [{'type': 'slow', 'chance': 0.5, 'value': 15, 'duration': 2}]},
        {'id': 'ice_10b', 'name': '冰甲术',    'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队覆盖冰甲大幅减伤', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}]},
        {'id': 'ice_10c', 'name': '冰影连刺',  'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '冰影闪烁中的连续穿刺', 'effects': [{'type': 'freeze', 'chance': 0.3, 'duration': 1}]},
    ],
    'metal': [
        {'id': 'metal_01', 'name': '钢刃斩击',   'power': 95,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以精钢锻造的利刃斩击', 'effects': []},
        {'id': 'metal_03', 'name': '铁壁防御',   'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 10, 'roles': None,
         'description': '金属凝聚形成铁壁提升防御', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        {'id': 'metal_05', 'name': '金属风暴',   'power': 160, 'type': 'physical', 'target': 'all',        'cooldown': 3, 'unlock_level': 20, 'roles': None,
         'description': '无数金属碎片横扫全场', 'effects': []},
        {'id': 'metal_07', 'name': '利刃贯穿',   'power': 200, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 30, 'roles': None,
         'description': '以极锋利刃贯穿目标护甲', 'effects': [{'type': 'ignore_def', 'value': 15}]},
        {'id': 'metal_09', 'name': '钢铁洪流',   'power': 250, 'type': 'physical', 'target': 'all',        'cooldown': 3, 'unlock_level': 40, 'roles': None,
         'description': '钢铁洪流冲击全体敌人', 'effects': []},
        {'id': 'metal_11', 'name': '锻造之力',   'power': 300, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '锻造极致之力猛击目标', 'effects': [{'type': 'ignore_def', 'value': 15}]},
        {'id': 'metal_12', 'name': '金刚不坏',   'power': 35,  'type': 'buff',     'target': 'self',       'cooldown': 5, 'unlock_level': 55, 'roles': None,
         'description': '金刚不坏之躯大幅减伤', 'effects': [{'type': 'shield', 'value': 35, 'duration': 3}]},
        {'id': 'metal_13', 'name': '万刃齐发',   'power': 360, 'type': 'physical', 'target': 'all',        'cooldown': 4, 'unlock_level': 60, 'roles': None,
         'description': '万把金属利刃齐发横扫', 'effects': []},
        {'id': 'metal_14', 'name': '金属修复',   'power': 35,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '以金属之力修复友方', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 2}]},
        {'id': 'metal_15', 'name': '钢铁审判',   'power': 340, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 70, 'roles': None,
         'description': '以钢铁之力审判目标', 'effects': [{'type': 'ignore_def', 'value': 20}]},
        {'id': 'metal_16', 'name': '神兵天降',   'power': 450, 'type': 'physical', 'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '天降神兵无视一切防御', 'effects': [{'type': 'ignore_def', 'value': 30}]},
        {'id': 'metal_17', 'name': '金属帝王',   'power': 420, 'type': 'physical', 'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '帝王级金属之力碾碎一切', 'effects': [{'type': 'ignore_def', 'value': 25}]},
        {'id': 'metal_02a', 'name': '铸刃打击',  'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '以锻铸利刃的重击', 'effects': []},
        {'id': 'metal_02b', 'name': '金属弹射',  'power': 120, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射高速金属弹片打击目标', 'effects': []},
        {'id': 'metal_04a', 'name': '钢铠附体',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 15, 'roles': [_W, _T],
         'description': '钢铠覆体大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}, {'type': 'buff_mdef', 'value': 25, 'duration': 3}]},
        {'id': 'metal_04b', 'name': '金属飞刃',  'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S],
         'description': '操控金属飞刃攻击目标', 'effects': [{'type': 'ignore_def', 'value': 10}]},
        {'id': 'metal_06a', 'name': '破甲连击',  'power': 185, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '连续破甲攻击削弱防御', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}]},
        {'id': 'metal_06b', 'name': '金属之雨',  'power': 180, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '召唤金属之雨覆盖全场', 'effects': []},
        {'id': 'metal_06c', 'name': '铁壁守护',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '以铁壁守护全队提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'metal_08a', 'name': '锻造强化',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '锻造之力大幅提升攻击', 'effects': [{'type': 'buff_atk', 'value': 30, 'duration': 3}]},
        {'id': 'metal_08b', 'name': '金属治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '以金属之力修复友方伤痕', 'effects': []},
        {'id': 'metal_10a', 'name': '钢铁之雨',  'power': 260, 'type': 'physical', 'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '漫天钢铁倾泻而下', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}]},
        {'id': 'metal_10b', 'name': '铁壁阵',    'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队构筑铁壁阵大幅减伤', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}, {'type': 'shield', 'value': 20, 'duration': 3}]},
        {'id': 'metal_10c', 'name': '刺钢突袭',  'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '暗影中的高速钢刃突袭', 'effects': [{'type': 'ignore_def', 'value': 20}]},
    ],
    'wood': [
        {'id': 'wood_01', 'name': '荆棘抽打',   'power': 85,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以荆棘缠绕的藤鞭抽打', 'effects': []},
        {'id': 'wood_03', 'name': '自然护盾',   'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 10, 'roles': None,
         'description': '大自然之力凝聚护盾', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}, {'type': 'heal_pct', 'value': 8}]},
        {'id': 'wood_05', 'name': '藤蔓缠绕',   'power': 160, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '召唤藤蔓缠绕束缚目标', 'effects': [{'type': 'slow', 'chance': 0.4, 'value': 15, 'duration': 2}]},
        {'id': 'wood_07', 'name': '孢子毒雾',   'power': 155, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '释放有毒孢子弥漫全场', 'effects': [{'type': 'poison', 'chance': 0.5, 'damage_pct': 5, 'duration': 3}]},
        {'id': 'wood_09', 'name': '巨木冲击',   'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '召唤巨木猛力撞击目标', 'effects': []},
        {'id': 'wood_11', 'name': '荆棘风暴',   'power': 280, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '荆棘旋风席卷全场', 'effects': [{'type': 'poison', 'chance': 0.4, 'damage_pct': 6, 'duration': 2}]},
        {'id': 'wood_12', 'name': '瘴气领域',   'power': 240, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '展开瘴气领域侵蚀全体', 'effects': [{'type': 'poison', 'chance': 0.6, 'damage_pct': 6, 'duration': 3}]},
        {'id': 'wood_13', 'name': '自然之怒',   'power': 360, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '大自然之怒倾注于一点', 'effects': [{'type': 'poison', 'chance': 0.5, 'damage_pct': 8, 'duration': 2}]},
        {'id': 'wood_14', 'name': '花愈之术',   'power': 35,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '繁花绽放的治愈之术', 'effects': [{'type': 'regen', 'value': 10, 'duration': 3}]},
        {'id': 'wood_15', 'name': '万木回春',   'power': 340, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '万木苏醒释放自然之力', 'effects': [{'type': 'lifesteal', 'value': 20}]},
        {'id': 'wood_16', 'name': '参天巨木',   'power': 440, 'type': 'physical', 'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '召唤参天巨木碾压目标', 'effects': [{'type': 'ignore_def', 'value': 25}]},
        {'id': 'wood_17', 'name': '自然轮回',   'power': 410, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '自然轮回毒噬万物', 'effects': [{'type': 'poison', 'chance': 0.7, 'damage_pct': 8, 'duration': 3}, {'type': 'lifesteal', 'value': 15}]},
        {'id': 'wood_02a', 'name': '毒藤鞭击',  'power': 105, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '以毒藤缠绕的鞭击', 'effects': [{'type': 'poison', 'chance': 0.3, 'damage_pct': 4, 'duration': 2}]},
        {'id': 'wood_02b', 'name': '孢子弹',    'power': 110, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射有毒孢子弹打击目标', 'effects': [{'type': 'poison', 'chance': 0.25, 'damage_pct': 4, 'duration': 2}]},
        {'id': 'wood_04a', 'name': '树皮铠甲',  'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 15, 'roles': [_W, _T],
         'description': '树皮凝聚为铠甲大幅提升双防', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}, {'type': 'buff_mdef', 'value': 20, 'duration': 3}]},
        {'id': 'wood_04b', 'name': '毒刺术',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S],
         'description': '发射淬毒荆刺攻击目标', 'effects': [{'type': 'poison', 'chance': 0.35, 'damage_pct': 5, 'duration': 2}]},
        {'id': 'wood_06a', 'name': '藤蔓连击',  'power': 175, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '藤蔓加持的连续打击', 'effects': []},
        {'id': 'wood_06b', 'name': '剧毒绽放',  'power': 185, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '毒花剧烈绽放毒害全场', 'effects': [{'type': 'poison', 'chance': 0.45, 'damage_pct': 6, 'duration': 2}]},
        {'id': 'wood_06c', 'name': '自然祝福',  'power': 20,  'type': 'heal',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '大自然的祝福全体回复', 'effects': [{'type': 'regen', 'value': 5, 'duration': 2}]},
        {'id': 'wood_08a', 'name': '自然之力',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '汲取大自然力量强化攻击', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}]},
        {'id': 'wood_08b', 'name': '花愈泉',    'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '召唤花之泉水治愈友方', 'effects': [{'type': 'regen', 'value': 8, 'duration': 2}]},
        {'id': 'wood_10a', 'name': '荆棘之雨',  'power': 260, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '荆棘之雨倾泻而下', 'effects': [{'type': 'poison', 'chance': 0.5, 'damage_pct': 5, 'duration': 2}]},
        {'id': 'wood_10b', 'name': '生命之树',  'power': 30,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '生命之树庇护全队', 'effects': [{'type': 'regen', 'value': 8, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}]},
        {'id': 'wood_10c', 'name': '毒影刺杀',  'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '淬毒暗器的连续暗杀', 'effects': [{'type': 'poison', 'chance': 0.6, 'damage_pct': 8, 'duration': 2}]},
    ],
    'electric': [
        {'id': 'elec_01', 'name': '雷电打击',   'power': 85,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以雷电强化的武器打击', 'effects': []},
        {'id': 'elec_03', 'name': '电磁护盾',   'power': 25,  'type': 'buff',     'target': 'self',       'cooldown': 3, 'unlock_level': 10, 'roles': None,
         'description': '电磁场凝聚护盾提升防御', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'elec_05', 'name': '雷球术',     'power': 165, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '凝聚雷电能量发射雷球', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'elec_07', 'name': '连锁闪电',   'power': 155, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '闪电在敌群中连锁弹射', 'effects': [{'type': 'stun', 'chance': 0.25, 'duration': 1}]},
        {'id': 'elec_09', 'name': '雷霆万钧',   'power': 260, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '万钧雷霆倾泻于目标', 'effects': [{'type': 'stun', 'chance': 0.35, 'duration': 1}]},
        {'id': 'elec_11', 'name': '闪电冲锋',   'power': 300, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '化身闪电猛冲目标', 'effects': [{'type': 'buff_spd', 'value': 15, 'duration': 1}]},
        {'id': 'elec_12', 'name': '电磁脉冲',   'power': 245, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '释放电磁脉冲削弱全体', 'effects': [{'type': 'debuff_atk', 'value': 15, 'duration': 2}]},
        {'id': 'elec_13', 'name': '雷神之怒',   'power': 370, 'type': 'magic',    'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '雷神之力降于目标', 'effects': [{'type': 'stun', 'chance': 0.4, 'duration': 1}]},
        {'id': 'elec_14', 'name': '电磁修复',   'power': 30,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '电磁场共振修复友方', 'effects': [{'type': 'buff_spd', 'value': 15, 'duration': 2}]},
        {'id': 'elec_15', 'name': '雷暴领域',   'power': 350, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '展开雷暴领域电击全场', 'effects': [{'type': 'stun', 'chance': 0.35, 'duration': 1}]},
        {'id': 'elec_16', 'name': '天雷灭世',   'power': 450, 'type': 'magic',    'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '天降灭世之雷', 'effects': [{'type': 'ignore_def', 'value': 25}]},
        {'id': 'elec_17', 'name': '雷帝降临',   'power': 420, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '雷帝之力降临人间', 'effects': [{'type': 'stun', 'chance': 0.5, 'duration': 1}]},
        {'id': 'elec_02a', 'name': '电击拳',    'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '以雷电缠绕的拳头猛击', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'elec_02b', 'name': '闪电箭',    'power': 120, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射闪电箭远程电击目标', 'effects': [{'type': 'stun', 'chance': 0.15, 'duration': 1}]},
        {'id': 'elec_04a', 'name': '雷光斩',    'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A],
         'description': '雷光附着的高速斩击', 'effects': []},
        {'id': 'elec_04b', 'name': '雷电射线',  'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _T, _S],
         'description': '发射高压雷电射线', 'effects': []},
        {'id': 'elec_06a', 'name': '雷拳连击',  'power': 180, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '雷电加持的连续拳击', 'effects': [{'type': 'stun', 'chance': 0.25, 'duration': 1}]},
        {'id': 'elec_06b', 'name': '电磁风暴',  'power': 190, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '释放电磁风暴冲击全场', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'elec_06c', 'name': '电磁守护',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '电磁场守护全队提升速度', 'effects': [{'type': 'buff_spd', 'value': 20, 'duration': 3}]},
        {'id': 'elec_08a', 'name': '闪电之心',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '激发闪电之心提升速度与暴击', 'effects': [{'type': 'buff_spd', 'value': 25, 'duration': 3}, {'type': 'buff_crit', 'value': 20, 'duration': 3}]},
        {'id': 'elec_08b', 'name': '电磁治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '以电磁波共振治愈友方', 'effects': []},
        {'id': 'elec_10a', 'name': '落雷阵',    'power': 260, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '连续落雷轰击全体敌人', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'elec_10b', 'name': '电磁庇护',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队获得电磁护盾加速', 'effects': [{'type': 'buff_spd', 'value': 20, 'duration': 3}, {'type': 'shield', 'value': 15, 'duration': 3}]},
        {'id': 'elec_10c', 'name': '雷影突袭',  'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '闪电速度的暗杀突袭', 'effects': [{'type': 'stun', 'chance': 0.35, 'duration': 1}]},
    ],
    'fighting': [
        {'id': 'fight_01', 'name': '裂拳突击',   'power': 90,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以强化拳劲突击敌人', 'effects': []},
        {'id': 'fight_03', 'name': '铁山靠',     'power': 115, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None,
         'description': '以肩部猛力撞击目标', 'effects': [{'type': 'stun', 'chance': 0.15, 'duration': 1}]},
        {'id': 'fight_05', 'name': '碎地拳',     'power': 160, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '蓄力重拳砸裂大地击碎护甲', 'effects': [{'type': 'ignore_def', 'value': 10}]},
        {'id': 'fight_07', 'name': '旋风连腿',   'power': 155, 'type': 'physical', 'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '旋身连腿横扫全体敌人', 'effects': []},
        {'id': 'fight_09', 'name': '百裂拳',     'power': 250, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '拳影如暴雨般倾泻于目标', 'effects': [{'type': 'ignore_def', 'value': 15}]},
        {'id': 'fight_11', 'name': '霸体冲拳',   'power': 290, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '霸体状态下发动毁灭性冲拳', 'effects': [{'type': 'stun', 'chance': 0.25, 'duration': 1}]},
        {'id': 'fight_12', 'name': '气合爆发',   'power': 240, 'type': 'physical', 'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '爆发全身斗气冲击全场', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 2}]},
        {'id': 'fight_13', 'name': '龙虎乱舞',   'power': 365, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '龙虎双形拳法倾注一身', 'effects': []},
        {'id': 'fight_14', 'name': '气功回复',   'power': 30,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '以内气导引修复友方伤势', 'effects': [{'type': 'buff_atk', 'value': 10, 'duration': 2}]},
        {'id': 'fight_15', 'name': '无双连击',   'power': 340, 'type': 'physical', 'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '无双拳脚连击横扫全场', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'fight_16', 'name': '一击必杀',   'power': 440, 'type': 'physical', 'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '凝聚全力的极致一拳无视防御', 'effects': [{'type': 'ignore_def', 'value': 35}]},
        {'id': 'fight_17', 'name': '格斗极意',   'power': 410, 'type': 'physical', 'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '领悟格斗极意拳破万法', 'effects': [{'type': 'ignore_def', 'value': 20}, {'type': 'buff_atk', 'value': 20, 'duration': 2}]},
        {'id': 'fight_02a', 'name': '重拳猛击',  'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '蓄力重拳猛力打击目标', 'effects': [{'type': 'stun', 'chance': 0.15, 'duration': 1}]},
        {'id': 'fight_02b', 'name': '气功弹',    'power': 100, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '将斗气凝为弹丸远程射出', 'effects': []},
        {'id': 'fight_04a', 'name': '膝击破甲',  'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _A],
         'description': '飞膝直击破坏护甲', 'effects': [{'type': 'ignore_def', 'value': 10}]},
        {'id': 'fight_04b', 'name': '气功掌',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _S, _T],
         'description': '以内劲催动气功掌击出', 'effects': []},
        {'id': 'fight_06a', 'name': '连环踢',    'power': 185, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '高速连环踢击令敌眩晕', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'fight_06b', 'name': '气功炮',    'power': 175, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '凝聚斗气化为炮弹轰击全场', 'effects': []},
        {'id': 'fight_06c', 'name': '斗志鼓舞',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '以战吼鼓舞全队提升攻击', 'effects': [{'type': 'buff_atk', 'value': 20, 'duration': 3}]},
        {'id': 'fight_08a', 'name': '战意昂扬',  'power': 30,  'type': 'buff',     'target': 'self',       'cooldown': 4, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '激发战意大幅提升攻击力', 'effects': [{'type': 'buff_atk', 'value': 30, 'duration': 3}]},
        {'id': 'fight_08b', 'name': '气功治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '以内气导引治愈友方', 'effects': []},
        {'id': 'fight_10a', 'name': '升龙拳',    'power': 260, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_W, _M],
         'description': '腾空而起的升龙拳击飞目标', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'fight_10b', 'name': '铁壁架势',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队进入铁壁防御架势', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}, {'type': 'shield', 'value': 15, 'duration': 3}]},
        {'id': 'fight_10c', 'name': '暗杀拳',    'power': 255, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '要害精准打击无视防御', 'effects': [{'type': 'ignore_def', 'value': 25}]},
    ],
    'ground': [
        {'id': 'gnd_01', 'name': '大地踏击',   'power': 90,  'type': 'physical', 'target': 'single',     'cooldown': 0, 'unlock_level': 1,  'roles': None,
         'description': '以大地之力强化的踏击', 'effects': []},
        {'id': 'gnd_03', 'name': '泥沼陷阱',   'power': 115, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 10, 'roles': None,
         'description': '在目标脚下展开泥沼降低速度', 'effects': [{'type': 'debuff_spd', 'value': 15, 'duration': 2}]},
        {'id': 'gnd_05', 'name': '地裂冲击',   'power': 160, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 20, 'roles': None,
         'description': '撕裂地面冲击目标', 'effects': []},
        {'id': 'gnd_07', 'name': '地震波',     'power': 155, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 30, 'roles': None,
         'description': '引发地震波震荡全体敌人', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'gnd_09', 'name': '流沙漩涡',   'power': 250, 'type': 'magic',    'target': 'single',     'cooldown': 2, 'unlock_level': 40, 'roles': None,
         'description': '召唤流沙漩涡吞噬目标', 'effects': [{'type': 'debuff_spd', 'value': 20, 'duration': 2}]},
        {'id': 'gnd_11', 'name': '大地震击',   'power': 285, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 50, 'roles': None,
         'description': '引发大地震击冲击全场', 'effects': [{'type': 'stun', 'chance': 0.25, 'duration': 1}]},
        {'id': 'gnd_12', 'name': '沙暴领域',   'power': 245, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 55, 'roles': None,
         'description': '展开沙暴领域侵蚀全体防御', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}]},
        {'id': 'gnd_13', 'name': '地裂天崩',   'power': 365, 'type': 'physical', 'target': 'single',     'cooldown': 3, 'unlock_level': 60, 'roles': None,
         'description': '撕裂大地的毁灭性一击', 'effects': []},
        {'id': 'gnd_14', 'name': '大地恩泽',   'power': 30,  'type': 'heal',     'target': 'ally_single','cooldown': 4, 'unlock_level': 65, 'roles': None,
         'description': '大地馈赠的治愈之泉', 'effects': [{'type': 'buff_def', 'value': 15, 'duration': 2}]},
        {'id': 'gnd_15', 'name': '震源爆发',   'power': 340, 'type': 'magic',    'target': 'all',        'cooldown': 4, 'unlock_level': 70, 'roles': None,
         'description': '引爆震源冲击波横扫全场', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'gnd_16', 'name': '断层粉碎',   'power': 440, 'type': 'physical', 'target': 'single',     'cooldown': 4, 'unlock_level': 75, 'roles': None,
         'description': '制造断层粉碎目标防御', 'effects': [{'type': 'ignore_def', 'value': 30}]},
        {'id': 'gnd_17', 'name': '末日地裂',   'power': 410, 'type': 'magic',    'target': 'all',        'cooldown': 5, 'unlock_level': 80, 'roles': None,
         'description': '末日般的大地裂变吞噬一切', 'effects': [{'type': 'stun', 'chance': 0.4, 'duration': 1}, {'type': 'debuff_def', 'value': 20, 'duration': 2}]},
        {'id': 'gnd_02a', 'name': '地裂踏',    'power': 110, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_W, _A, _T],
         'description': '猛力踏地引发裂缝打击目标', 'effects': [{'type': 'stun', 'chance': 0.15, 'duration': 1}]},
        {'id': 'gnd_02b', 'name': '砂砾弹',    'power': 105, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 5,  'roles': [_M, _S],
         'description': '发射高速砂砾弹打击目标', 'effects': []},
        {'id': 'gnd_04a', 'name': '泥岩拳',    'power': 135, 'type': 'physical', 'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_W, _T],
         'description': '泥岩凝聚于拳的重击', 'effects': []},
        {'id': 'gnd_04b', 'name': '流沙术',    'power': 130, 'type': 'magic',    'target': 'single',     'cooldown': 1, 'unlock_level': 15, 'roles': [_M, _A, _S],
         'description': '操控流沙束缚并伤害目标', 'effects': [{'type': 'debuff_spd', 'value': 10, 'duration': 2}]},
        {'id': 'gnd_06a', 'name': '地动连击',  'power': 185, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 25, 'roles': [_W, _A],
         'description': '引发地动的连续打击', 'effects': [{'type': 'stun', 'chance': 0.2, 'duration': 1}]},
        {'id': 'gnd_06b', 'name': '砂尘暴',    'power': 180, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 25, 'roles': [_M],
         'description': '召唤砂尘暴侵蚀全体', 'effects': [{'type': 'debuff_def', 'value': 10, 'duration': 2}]},
        {'id': 'gnd_06c', 'name': '大地庇护',  'power': 20,  'type': 'heal',     'target': 'ally_all',   'cooldown': 3, 'unlock_level': 25, 'roles': [_T, _S],
         'description': '大地之力庇护全体回复', 'effects': [{'type': 'buff_def', 'value': 10, 'duration': 2}]},
        {'id': 'gnd_08a', 'name': '地裂重击',  'power': 220, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 35, 'roles': [_W, _A, _M],
         'description': '以地裂之力猛击目标', 'effects': []},
        {'id': 'gnd_08b', 'name': '泥泉治愈',  'power': 25,  'type': 'heal',     'target': 'ally_single','cooldown': 3, 'unlock_level': 35, 'roles': [_S, _T],
         'description': '召唤泥泉治愈友方伤痕', 'effects': []},
        {'id': 'gnd_10a', 'name': '震源崩裂',  'power': 265, 'type': 'magic',    'target': 'all',        'cooldown': 3, 'unlock_level': 45, 'roles': [_M, _W],
         'description': '引爆地底震源冲击全场', 'effects': [{'type': 'debuff_def', 'value': 15, 'duration': 2}]},
        {'id': 'gnd_10b', 'name': '大地之壁',  'power': 25,  'type': 'buff',     'target': 'ally_all',   'cooldown': 4, 'unlock_level': 45, 'roles': [_T, _S],
         'description': '全队构筑大地之壁大幅减伤', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}]},
        {'id': 'gnd_10c', 'name': '地刺暗袭',  'power': 255, 'type': 'physical', 'target': 'single',     'cooldown': 2, 'unlock_level': 45, 'roles': [_A],
         'description': '操控地刺从暗处突袭要害', 'effects': [{'type': 'ignore_def', 'value': 20}]},
    ],
}

_SEED_EXCLUSIVE_SKILLS = {
    'miyamoto': [
        {'id': 'miyamoto_ex1', 'name': '二天一流', 'power': 150, 'type': 'physical', 'target': 'single', 'cooldown': 2, 'unlock_level': 1, 'description': '双刀流秘技，同时双刀斩击', 'effects': []},
        {'id': 'miyamoto_ex2', 'name': '无念无想', 'power': 30, 'type': 'buff', 'target': 'self', 'cooldown': 4, 'unlock_level': 40, 'description': '进入无念境界，暴击率与攻击力大幅提升', 'effects': [{'type': 'buff_atk', 'value': 35, 'duration': 3}, {'type': 'buff_crit', 'value': 40, 'duration': 3}]},
        {'id': 'miyamoto_ex3', 'name': '最终之剑', 'power': 500, 'type': 'physical', 'target': 'single', 'cooldown': 4, 'unlock_level': 80, 'description': '悟道之后的最终一剑', 'effects': [{'type': 'ignore_def', 'value': 30}]},
    ],
    'viking-ragnar': [
        {'id': 'ragnar_ex1', 'name': '维京冲锋', 'power': 140, 'type': 'physical', 'target': 'single', 'cooldown': 2, 'unlock_level': 1, 'description': '狂暴的维京冲锋攻击', 'effects': []},
        {'id': 'ragnar_ex2', 'name': '狂战士之怒', 'power': 35, 'type': 'buff', 'target': 'self', 'cooldown': 4, 'unlock_level': 40, 'description': '进入狂暴状态', 'effects': [{'type': 'buff_atk', 'value': 40, 'duration': 3}, {'type': 'buff_spd', 'value': 30, 'duration': 3}]},
        {'id': 'ragnar_ex3', 'name': '诸神黄昏', 'power': 480, 'type': 'physical', 'target': 'all', 'cooldown': 5, 'unlock_level': 80, 'description': '北欧末日降临', 'effects': []},
    ],
    'robin-hood': [
        {'id': 'robin_ex1', 'name': '精准射击', 'power': 145, 'type': 'physical', 'target': 'single', 'cooldown': 2, 'unlock_level': 1, 'description': '必定暴击的精准一箭', 'effects': [{'type': 'guaranteed_crit'}]},
        {'id': 'robin_ex2', 'name': '箭雨', 'power': 250, 'type': 'physical', 'target': 'all', 'cooldown': 3, 'unlock_level': 40, 'description': '漫天箭雨覆盖战场', 'effects': []},
        {'id': 'robin_ex3', 'name': '百步穿杨', 'power': 520, 'type': 'physical', 'target': 'single', 'cooldown': 4, 'unlock_level': 80, 'description': '百步穿杨无视护甲', 'effects': [{'type': 'ignore_def', 'value': 50}]},
    ],
    'guan-yu': [
        {'id': 'guanyu_ex1', 'name': '青龙偃月斩', 'power': 160, 'type': 'physical', 'target': 'single', 'cooldown': 2, 'unlock_level': 1, 'description': '挥舞青龙偃月刀', 'effects': []},
        {'id': 'guanyu_ex2', 'name': '过五关斩六将', 'power': 25, 'type': 'buff', 'target': 'self', 'cooldown': 3, 'unlock_level': 20, 'description': '战意高涨攻防双提升', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}, {'type': 'buff_def', 'value': 20, 'duration': 3}]},
        {'id': 'guanyu_ex3', 'name': '忠义之魂', 'power': 20, 'type': 'buff', 'target': 'ally_all', 'cooldown': 4, 'unlock_level': 40, 'description': '忠义之魂鼓舞全队', 'effects': [{'type': 'buff_atk', 'value': 20, 'duration': 3}]},
        {'id': 'guanyu_ex4', 'name': '武圣之威', 'power': 420, 'type': 'physical', 'target': 'single', 'cooldown': 3, 'unlock_level': 60, 'description': '武圣全力一击', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
        {'id': 'guanyu_ex5', 'name': '关公显圣', 'power': 380, 'type': 'physical', 'target': 'all', 'cooldown': 4, 'unlock_level': 80, 'description': '武圣显灵横扫全场', 'effects': [{'type': 'lifesteal', 'value': 25}]},
    ],
    'hua-mulan': [
        {'id': 'mulan_ex1', 'name': '从军斩', 'power': 150, 'type': 'physical', 'target': 'single', 'cooldown': 2, 'unlock_level': 1, 'description': '木兰英姿飒爽的利落斩击', 'effects': []},
        {'id': 'mulan_ex2', 'name': '替父从军', 'power': 20, 'type': 'buff', 'target': 'self', 'cooldown': 3, 'unlock_level': 20, 'description': '坚定信念提升防御与速度', 'effects': [{'type': 'buff_def', 'value': 20, 'duration': 3}, {'type': 'buff_spd', 'value': 25, 'duration': 3}]},
        {'id': 'mulan_ex3', 'name': '花舞连斩', 'power': 300, 'type': 'physical', 'target': 'single', 'cooldown': 3, 'unlock_level': 40, 'description': '如花瓣飞舞般的连续斩击', 'effects': []},
        {'id': 'mulan_ex4', 'name': '巾帼之怒', 'power': 380, 'type': 'physical', 'target': 'all', 'cooldown': 4, 'unlock_level': 60, 'description': '巾帼不让须眉的全力爆发', 'effects': []},
        {'id': 'mulan_ex5', 'name': '木兰无双', 'power': 450, 'type': 'physical', 'target': 'single', 'cooldown': 4, 'unlock_level': 80, 'description': '木兰武技的极致', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 2, 'target_scope': 'ally_all'}]},
    ],
    'arthur': [
        {'id': 'arthur_ex1', 'name': '誓约胜利之剑', 'power': 170, 'type': 'magic', 'target': 'single', 'cooldown': 2, 'unlock_level': 1, 'description': 'Excalibur圣剑斩击', 'effects': []},
        {'id': 'arthur_ex2', 'name': '圆桌骑士', 'power': 20, 'type': 'buff', 'target': 'ally_all', 'cooldown': 3, 'unlock_level': 20, 'description': '圆桌骑士之誓全队防御提升', 'effects': [{'type': 'buff_def', 'value': 25, 'duration': 3}]},
        {'id': 'arthur_ex3', 'name': '圣剑光辉', 'power': 320, 'type': 'magic', 'target': 'all', 'cooldown': 3, 'unlock_level': 40, 'description': 'Excalibur绽放光辉', 'effects': []},
        {'id': 'arthur_ex4', 'name': '不列颠守护', 'power': 30, 'type': 'buff', 'target': 'ally_all', 'cooldown': 4, 'unlock_level': 60, 'description': '不列颠之王的守护', 'effects': [{'type': 'shield', 'value': 20, 'duration': 3}]},
        {'id': 'arthur_ex5', 'name': '王之军势', 'power': 460, 'type': 'magic', 'target': 'all', 'cooldown': 4, 'unlock_level': 80, 'description': '王之军势圣光终焉', 'effects': []},
    ],
    'cao-cao': [
        {'id': 'caocao_ex1', 'name': '奸雄之刃', 'power': 155, 'type': 'physical', 'target': 'single', 'cooldown': 2, 'unlock_level': 1, 'description': '暗影缠绕的枭雄之刃', 'effects': []},
        {'id': 'caocao_ex2', 'name': '挟天子令诸侯', 'power': 20, 'type': 'debuff', 'target': 'all', 'cooldown': 4, 'unlock_level': 20, 'description': '枭雄威压削弱全体', 'effects': [{'type': 'debuff_atk', 'value': 15, 'duration': 2}, {'type': 'debuff_def', 'value': 15, 'duration': 2}]},
        {'id': 'caocao_ex3', 'name': '乱世奸雄', 'power': 30, 'type': 'buff', 'target': 'self', 'cooldown': 3, 'unlock_level': 40, 'description': '枭雄觉醒大幅提升攻击', 'effects': [{'type': 'buff_atk', 'value': 35, 'duration': 3}, {'type': 'lifesteal', 'value': 20}]},
        {'id': 'caocao_ex4', 'name': '魏武挥鞭', 'power': 400, 'type': 'physical', 'target': 'all', 'cooldown': 4, 'unlock_level': 60, 'description': '魏武帝挥鞭横扫全场', 'effects': [{'type': 'lifesteal', 'value': 20}]},
        {'id': 'caocao_ex5', 'name': '天下归心', 'power': 460, 'type': 'physical', 'target': 'all', 'cooldown': 4, 'unlock_level': 80, 'description': '天下归心终极枭雄之力', 'effects': [{'type': 'lifesteal', 'value': 25}]},
    ],
    'cleopatra': [
        {'id': 'cleo_ex1', 'name': '尼罗河祝福', 'power': 30, 'type': 'heal', 'target': 'ally_single', 'cooldown': 2, 'unlock_level': 1, 'description': '尼罗河之水的祝福治愈', 'effects': []},
        {'id': 'cleo_ex2', 'name': '女王魅惑', 'power': 25, 'type': 'debuff', 'target': 'single', 'cooldown': 3, 'unlock_level': 20, 'description': '女王的魅惑大幅削弱目标', 'effects': [{'type': 'debuff_atk', 'value': 30, 'duration': 2}]},
        {'id': 'cleo_ex3', 'name': '王权之光', 'power': 25, 'type': 'buff', 'target': 'ally_all', 'cooldown': 4, 'unlock_level': 40, 'description': '女王权杖之光全队全属性提升', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}, {'type': 'buff_spd', 'value': 10, 'duration': 3}]},
        {'id': 'cleo_ex4', 'name': '尼罗河之怒', 'power': 350, 'type': 'magic', 'target': 'all', 'cooldown': 4, 'unlock_level': 60, 'description': '尼罗河泛滥冲刷全场', 'effects': []},
        {'id': 'cleo_ex5', 'name': '永恒女王', 'power': 40, 'type': 'heal', 'target': 'ally_all', 'cooldown': 5, 'unlock_level': 80, 'description': '永恒女王全队大幅治愈', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}]},
    ],
    'zhuge-liang': [
        {'id': 'zgl_ex1', 'name': '八卦阵', 'power': 25, 'type': 'buff', 'target': 'ally_all', 'cooldown': 4, 'unlock_level': 1, 'description': '布下八卦阵法全队防御提升', 'effects': [{'type': 'buff_def', 'value': 30, 'duration': 3}]},
        {'id': 'zgl_ex2', 'name': '草船借箭', 'power': 280, 'type': 'magic', 'target': 'all', 'cooldown': 3, 'unlock_level': 20, 'description': '以智谋借敌之箭反击', 'effects': [{'type': 'buff_atk', 'value': 20, 'duration': 2}]},
        {'id': 'zgl_ex3', 'name': '火烧赤壁', 'power': 400, 'type': 'magic', 'target': 'all', 'cooldown': 4, 'unlock_level': 40, 'description': '赤壁之火重现', 'effects': [{'type': 'burn', 'chance': 0.6, 'damage_pct': 8, 'duration': 2}]},
        {'id': 'zgl_ex4', 'name': '空城计', 'power': 35, 'type': 'buff', 'target': 'self', 'cooldown': 4, 'unlock_level': 60, 'description': '空城退敌大幅提升闪避', 'effects': [{'type': 'evasion_up', 'value': 80, 'duration': 2}, {'type': 'counter', 'value': 40}]},
        {'id': 'zgl_ex5', 'name': '七星灯', 'power': 50, 'type': 'heal', 'target': 'ally_all', 'cooldown': 5, 'unlock_level': 80, 'description': '七星续命灯全队回复', 'effects': []},
    ],
    'joan-of-arc': [
        {'id': 'joan_ex1', 'name': '圣女祈祷', 'power': 25, 'type': 'heal', 'target': 'ally_all', 'cooldown': 3, 'unlock_level': 1, 'description': '虔诚祈祷治愈全体', 'effects': []},
        {'id': 'joan_ex2', 'name': '神启', 'power': 20, 'type': 'buff', 'target': 'ally_all', 'cooldown': 3, 'unlock_level': 20, 'description': '上天启示全队全属性提升', 'effects': [{'type': 'buff_atk', 'value': 15, 'duration': 3}, {'type': 'buff_def', 'value': 15, 'duration': 3}, {'type': 'buff_spd', 'value': 10, 'duration': 3}]},
        {'id': 'joan_ex3', 'name': '圣旗飘扬', 'power': 30, 'type': 'buff', 'target': 'ally_all', 'cooldown': 4, 'unlock_level': 40, 'description': '圣旗之下全队攻防大幅提升', 'effects': [{'type': 'buff_atk', 'value': 20, 'duration': 3}, {'type': 'buff_def', 'value': 20, 'duration': 3}, {'type': 'cleanse'}]},
        {'id': 'joan_ex4', 'name': '殉道之光', 'power': 45, 'type': 'heal', 'target': 'ally_single', 'cooldown': 4, 'unlock_level': 60, 'description': '殉道精神治愈并赋予护盾', 'effects': [{'type': 'shield', 'value': 30, 'duration': 3}]},
        {'id': 'joan_ex5', 'name': '圣女降临', 'power': 380, 'type': 'magic', 'target': 'all', 'cooldown': 4, 'unlock_level': 80, 'description': '圣女降临审判并治愈全队', 'effects': [{'type': 'lifesteal', 'value': 30}]},
    ],
    'genghis-khan': [
        {'id': 'khan_ex1', 'name': '铁骑冲锋', 'power': 180, 'type': 'physical', 'target': 'all', 'cooldown': 3, 'unlock_level': 1, 'description': '蒙古铁骑冲锋践踏全体', 'effects': []},
        {'id': 'khan_ex2', 'name': '草原之王', 'power': 30, 'type': 'buff', 'target': 'self', 'cooldown': 3, 'unlock_level': 20, 'description': '草原之王大幅提升攻击与速度', 'effects': [{'type': 'buff_atk', 'value': 35, 'duration': 3}, {'type': 'buff_spd', 'value': 30, 'duration': 3}]},
        {'id': 'khan_ex3', 'name': '万箭齐发', 'power': 350, 'type': 'physical', 'target': 'all', 'cooldown': 4, 'unlock_level': 40, 'description': '万箭齐发覆盖战场', 'effects': []},
        {'id': 'khan_ex4', 'name': '征服者之威', 'power': 25, 'type': 'buff', 'target': 'ally_all', 'cooldown': 4, 'unlock_level': 60, 'description': '征服者的威势鼓舞全军', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3}, {'type': 'buff_crit', 'value': 20, 'duration': 3}]},
        {'id': 'khan_ex5', 'name': '蒙古铁骑', 'power': 450, 'type': 'physical', 'target': 'all', 'cooldown': 4, 'unlock_level': 80, 'description': '蒙古铁骑万马奔腾', 'effects': [{'type': 'stun', 'chance': 0.3, 'duration': 1}]},
    ],
}

_SEED_AWAKENING_SKILLS = {
    'zhuge-liang': {'id': 'zgl_awakening', 'name': '卧龙出山', 'power': 600, 'type': 'magic', 'target': 'all', 'cooldown': 6, 'unlock_level': 100, 'description': '卧龙出山天地变色！毁灭性伤害并强化全队', 'effects': [{'type': 'buff_atk', 'value': 25, 'duration': 3, 'target_scope': 'ally_all'}, {'type': 'buff_def', 'value': 25, 'duration': 3, 'target_scope': 'ally_all'}]},
    'joan-of-arc': {'id': 'joan_awakening', 'name': '奇迹之火', 'power': 500, 'type': 'magic', 'target': 'all', 'cooldown': 6, 'unlock_level': 100, 'description': '圣火燃烧一切不义！全队完全治愈', 'effects': [{'type': 'heal_all_pct', 'value': 100}]},
    'genghis-khan': {'id': 'khan_awakening', 'name': '天之骄子', 'power': 650, 'type': 'physical', 'target': 'all', 'cooldown': 6, 'unlock_level': 100, 'description': '长生天之子降世！全场毁灭性冲击', 'effects': [{'type': 'buff_atk', 'value': 30, 'duration': 3, 'target_scope': 'ally_all'}, {'type': 'buff_spd', 'value': 30, 'duration': 3, 'target_scope': 'ally_all'}]},
}

_SEED_PASSIVE_SKILLS = {
    'miyamoto':      {'id': 'miyamoto_passive', 'name': '剑圣之道', 'description': '暴击率+15%，暴击伤害+30%', 'effects': [{'type': 'passive_crit_rate', 'value': 15}, {'type': 'passive_crit_dmg', 'value': 30}]},
    'viking-ragnar': {'id': 'ragnar_passive',   'name': '北欧战魂', 'description': 'HP低于30%时攻击力+40%', 'effects': [{'type': 'passive_low_hp_atk', 'threshold': 30, 'value': 40}]},
    'robin-hood':    {'id': 'robin_passive',    'name': '百发百中', 'description': '对单体目标伤害+20%', 'effects': [{'type': 'passive_single_dmg', 'value': 20}]},
    'guan-yu':       {'id': 'guanyu_passive',   'name': '武圣之躯', 'description': 'HP+20%；致命伤害30%概率保留1HP', 'effects': [{'type': 'passive_hp_pct', 'value': 20}, {'type': 'passive_endure', 'chance': 30}]},
    'hua-mulan':     {'id': 'mulan_passive',    'name': '巾帼之志', 'description': '速度+15%；击杀回复15%最大HP', 'effects': [{'type': 'passive_spd_pct', 'value': 15}, {'type': 'passive_kill_heal', 'value': 15}]},
    'arthur':        {'id': 'arthur_passive',   'name': '王者之气', 'description': '全队防御+10%；光属性伤害+25%', 'effects': [{'type': 'passive_team_def', 'value': 10}, {'type': 'passive_elem_dmg', 'element': 'light', 'value': 25}]},
    'cao-cao':       {'id': 'caocao_passive',   'name': '乱世枭雄', 'description': '攻击20%概率吸取伤害30%', 'effects': [{'type': 'passive_lifesteal', 'chance': 20, 'value': 30}]},
    'cleopatra':     {'id': 'cleo_passive',     'name': '女王的庇护', 'description': '治疗效果+30%', 'effects': [{'type': 'passive_heal_boost', 'value': 30}, {'type': 'passive_heal_def', 'value': 10, 'duration': 2}]},
    'zhuge-liang':   {'id': 'zgl_passive',      'name': '卧龙之智', 'description': '魔攻+25%；技能冷却-1回合', 'effects': [{'type': 'passive_matk_pct', 'value': 25}, {'type': 'passive_cd_reduce', 'value': 1}]},
    'joan-of-arc':   {'id': 'joan_passive',     'name': '圣女之光', 'description': '全队最大HP+15%；每回合回复5%HP', 'effects': [{'type': 'passive_team_hp', 'value': 15}, {'type': 'passive_regen', 'value': 5}]},
    'genghis-khan':  {'id': 'khan_passive',     'name': '征服者之魂', 'description': '攻击+20%速度+20%；击杀额外行动', 'effects': [{'type': 'passive_atk_pct', 'value': 20}, {'type': 'passive_spd_pct', 'value': 20}, {'type': 'passive_extra_turn_on_kill'}]},
}


def seed_skill_templates(db_session, force=False):
    """将种子数据写入 skill_templates 表（仅在表为空或 force 时执行）"""
    from models import SkillTemplate

    existing = db_session.query(SkillTemplate).first()
    if existing is not None and not force:
        return 0

    if force and existing:
        from models import CharacterEquippedSkill
        db_session.query(CharacterEquippedSkill).delete()
        db_session.query(SkillTemplate).delete()
        db_session.commit()

    count = 0

    # 共通元素技能
    for element, pool in _SEED_ELEMENT_SKILLS.items():
        for sk in pool:
            roles_val = ','.join(sk['roles']) if sk.get('roles') else None
            row = SkillTemplate(
                id=sk['id'], name=sk['name'], power=sk['power'],
                skill_type=sk['type'], target=sk['target'],
                cooldown=sk['cooldown'], element=element,
                unlock_level=sk['unlock_level'],
                description=sk.get('description', ''),
                effects_json=json.dumps(sk.get('effects', []), ensure_ascii=False),
                roles=roles_val, category='shared',
                character_id=None, is_exclusive=False,
                is_passive=False, is_awakening=False,
            )
            db_session.add(row)
            count += 1

    # 专属技能
    for char_id, skills in _SEED_EXCLUSIVE_SKILLS.items():
        for sk in skills:
            row = SkillTemplate(
                id=sk['id'], name=sk['name'], power=sk['power'],
                skill_type=sk['type'], target=sk['target'],
                cooldown=sk['cooldown'], element=None,
                unlock_level=sk['unlock_level'],
                description=sk.get('description', ''),
                effects_json=json.dumps(sk.get('effects', []), ensure_ascii=False),
                roles=None, category='exclusive',
                character_id=char_id, is_exclusive=True,
                is_passive=False, is_awakening=False,
            )
            db_session.add(row)
            count += 1

    # 觉醒技能
    for char_id, sk in _SEED_AWAKENING_SKILLS.items():
        row = SkillTemplate(
            id=sk['id'], name=sk['name'], power=sk['power'],
            skill_type=sk['type'], target=sk['target'],
            cooldown=sk['cooldown'], element=None,
            unlock_level=sk.get('unlock_level', 100),
            description=sk.get('description', ''),
            effects_json=json.dumps(sk.get('effects', []), ensure_ascii=False),
            roles=None, category='awakening',
            character_id=char_id, is_exclusive=True,
            is_passive=False, is_awakening=True,
        )
        db_session.add(row)
        count += 1

    # 被动天赋
    for char_id, sk in _SEED_PASSIVE_SKILLS.items():
        row = SkillTemplate(
            id=sk['id'], name=sk['name'], power=0,
            skill_type='passive', target='self',
            cooldown=0, element=None, unlock_level=1,
            description=sk.get('description', ''),
            effects_json=json.dumps(sk.get('effects', []), ensure_ascii=False),
            roles=None, category='passive',
            character_id=char_id, is_exclusive=False,
            is_passive=True, is_awakening=False,
        )
        db_session.add(row)
        count += 1

    db_session.commit()
    return count
