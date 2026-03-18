# 游戏数据配置
"""
角色、技能、关卡等静态数据
包含经验值升级系统配置
"""

from skill_data import (
    MAX_CHARACTER_LEVEL,
    RARITY_CONFIG,
    ROLE_MODIFIERS,
    get_skills_for_character,
    get_skill_unlock_preview,
    calculate_stats_with_rarity,
    seed_skill_templates,
)

# ==================== 经验值升级系统配置 ====================

# 玩家账号等级上限
MAX_PLAYER_LEVEL = 50

# 玩家等级解锁配置
# 格式: {章节ID: 需要的玩家等级}
CHAPTER_UNLOCK_LEVELS = {
    'chapter-1': 1,   # 第1章默认解锁
    'chapter-2': 10,  # 第2章需要10级
    'chapter-3': 20,  # 第3章需要20级
    'chapter-4': 30,  # 第4章需要30级
}

# 等级礼包奖励
LEVEL_REWARDS = {
    5: {'gold': 1000, 'gems': 50, 'items': []},
    10: {'gold': 5000, 'gems': 100, 'items': [{'id': 'summon_scroll', 'count': 1}]},
    15: {'gold': 10000, 'gems': 150, 'items': []},
    20: {'gold': 20000, 'gems': 200, 'items': [{'id': 'epic_shard', 'count': 10}]},
    25: {'gold': 30000, 'gems': 300, 'items': []},
    30: {'gold': 50000, 'gems': 500, 'items': [{'id': 'legendary_shard', 'count': 5}]},
    40: {'gold': 100000, 'gems': 1000, 'items': []},
    50: {'gold': 200000, 'gems': 2000, 'items': [{'id': 'legendary_shard', 'count': 20}]},
}


def get_exp_to_next_level(level):
    """计算升到下一级所需经验
    
    Args:
        level: 当前等级
        
    Returns:
        升到下一级所需的经验值
    """
    if level >= MAX_PLAYER_LEVEL:
        return 0  # 已满级
    
    if level < 5:
        # 新手期：快速增长
        return 100 + (level - 1) * 50
    elif level < 10:
        # 过渡期
        return 300 + (level - 5) * 100
    elif level < 20:
        # 中期
        return 800 + (level - 10) * 200
    elif level < 30:
        # 后期
        return 3000 + (level - 20) * 300
    elif level < 40:
        # 高级
        return 6000 + (level - 30) * 500
    else:
        # 顶级
        return 12000 + (level - 40) * 1000


def get_total_exp_to_level(level):
    """计算升到指定等级所需的总经验
    
    Args:
        level: 目标等级
        
    Returns:
        从1级升到目标等级所需的总经验
    """
    total = 0
    for i in range(1, level):
        total += get_exp_to_next_level(i)
    return total


def get_level_from_exp(exp):
    """根据总经验值计算当前等级
    
    Args:
        exp: 当前累计经验
        
    Returns:
        当前等级
    """
    level = 1
    while level < MAX_PLAYER_LEVEL:
        exp_needed = get_exp_to_next_level(level)
        if exp < exp_needed:
            break
        exp -= exp_needed
        level += 1
    return level


# ==================== 初始角色配置 ====================

# 初始角色池（新玩家可选择的3个角色）
STARTER_CHARACTERS = [
    {
        'id': 'soldier',
        'name': '步兵',
        'name_en': 'Soldier',
        'title': '基础战士',
        'era': '通用',
        'origin': '训练营',
        'element': 'earth',
        'role_type': 'warrior',
        'description': '训练有素的步兵，攻守兼备，是队伍的中坚力量。',
        'avatar': '/static/images/characters/soldier.jpg',
        'illustration': '/static/images/characters/soldier-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 1000,
            'attack': 80,
            'defense': 60,
            'magic_attack': 30,
            'magic_defense': 40,
            'speed': 70
        },
        'skills': [
            {'id': 'skill-1', 'name': '冲锋斩击', 'type': 'physical', 'power': 100, 'element': 'earth', 'cooldown': 2, 'target': 'single',
             'description': '冲锋向前，对敌方造成物理伤害'},
            {'id': 'skill-2', 'name': '坚守阵地', 'type': 'buff', 'power': 0, 'element': 'earth', 'cooldown': 3, 'target': 'self',
             'description': '提升自身物防'},
        ]
    },
    {
        'id': 'archer',
        'name': '弓箭手',
        'name_en': 'Archer',
        'title': '远程射手',
        'era': '通用',
        'origin': '猎手村',
        'element': 'wind',
        'role_type': 'assassin',
        'description': '敏捷的远程单位，擅长从远处给予敌人致命打击。',
        'avatar': '/static/images/characters/archer.jpg',
        'illustration': '/static/images/characters/archer-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 700,
            'attack': 100,
            'defense': 40,
            'magic_attack': 50,
            'magic_defense': 35,
            'speed': 100
        },
        'skills': [
            {'id': 'skill-1', 'name': '穿云箭', 'type': 'physical', 'power': 120, 'element': 'wind', 'cooldown': 2, 'target': 'single',
             'description': '射出强力一箭，对敌方造成风属性物理伤害'},
            {'id': 'skill-2', 'name': '快速射击', 'type': 'physical', 'power': 60, 'element': 'wind', 'cooldown': 1, 'target': 'single',
             'description': '快速射击，造成物理伤害'},
        ]
    },
    {
        'id': 'mage-apprentice',
        'name': '见习法师',
        'name_en': 'Mage Apprentice',
        'title': '魔法学徒',
        'era': '通用',
        'origin': '魔法学院',
        'element': 'water',
        'role_type': 'mage',
        'description': '初学魔法的学徒，虽然力量有限但潜力无限。',
        'avatar': '/static/images/characters/mage-apprentice.jpg',
        'illustration': '/static/images/characters/mage-apprentice-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 600,
            'attack': 40,
            'defense': 30,
            'magic_attack': 110,
            'magic_defense': 60,
            'speed': 80
        },
        'skills': [
            {'id': 'skill-1', 'name': '水弹术', 'type': 'magic', 'power': 100, 'element': 'water', 'cooldown': 1, 'target': 'single',
             'description': '发射水弹，对敌方造成水属性魔法伤害'},
            {'id': 'skill-2', 'name': '冰霜护盾', 'type': 'buff', 'power': 0, 'element': 'water', 'cooldown': 3, 'target': 'self',
             'description': '提升自身魔防'},
        ]
    }
]

# 默认初始角色（如果玩家不选择）
DEFAULT_STARTER_CHARACTER = 'soldier'


# ==================== 稀有度配置 ====================
RARITY_NAMES = {
    'common': '普通',
    'rare': '稀有',
    'epic': '史诗',
    'legendary': '传说'
}

RARITY_COLORS = {
    'common': '#9ca3af',
    'rare': '#3b82f6',
    'epic': '#a855f7',
    'legendary': '#f59e0b'
}

RARITY_WEIGHTS = {
    'common': 60,
    'rare': 30,
    'epic': 8,
    'legendary': 2
}

# 元素配置
ELEMENT_NAMES = {
    'fire': '火',
    'water': '水',
    'wind': '风',
    'earth': '土',
    'light': '光',
    'dark': '暗'
}

ELEMENT_COLORS = {
    'fire': '#ef4444',
    'water': '#3b82f6',
    'wind': '#22c55e',
    'earth': '#a16207',
    'light': '#fbbf24',
    'dark': '#7c3aed'
}

# 元素克制关系 (攻击方 -> 被克制方)
# 攻击克制属性时造成额外伤害，被克制时减少伤害
ELEMENT_ADVANTAGE = {
    'fire': 'wind',     # 火克风
    'water': 'fire',    # 水克火
    'wind': 'earth',    # 风克土
    'earth': 'water',   # 土克水
    'light': 'dark',    # 光克暗
    'dark': 'light'     # 暗克光
}

# 元素被克制关系 (反向映射)
ELEMENT_DISADVANTAGE = {v: k for k, v in ELEMENT_ADVANTAGE.items()}

# 克制伤害加成
ELEMENT_ADVANTAGE_BONUS = 0.3  # 克制时+30%伤害
ELEMENT_DISADVANTAGE_PENALTY = 0.2  # 被克制时-20%伤害

# UP池配置
# 当前UP角色列表，在UP池中这些角色的概率会提升
CURRENT_UP_CHARACTERS = {
    'legendary': ['zhuge-liang'],  # 传说UP角色
    'epic': ['guan-yu']  # 史诗UP角色
}

# UP池概率提升倍数
UP_RATE_MULTIPLIER = 3  # UP角色概率是普通概率的3倍

# 角色类型
ROLE_NAMES = {
    'warrior': '战士',
    'mage': '法师',
    'assassin': '刺客',
    'tank': '坦克',
    'support': '辅助'
}

# 属性名称配置
STAT_NAMES = {
    'hp': '生命',
    'attack': '物攻',
    'defense': '物防',
    'magic_attack': '魔攻',
    'magic_defense': '魔防',
    'speed': '速度'
}

STAT_COLORS = {
    'hp': '#22c55e',
    'attack': '#ef4444',
    'defense': '#3b82f6',
    'magic_attack': '#a855f7',
    'magic_defense': '#06b6d4',
    'speed': '#fbbf24'
}

# 所有角色模板数据
ALL_CHARACTERS = [
    # ========== 普通角色（初始角色） ==========
    {
        'id': 'soldier',
        'name': '步兵',
        'name_en': 'Soldier',
        'title': '基础战士',
        'era': '通用',
        'origin': '训练营',
        'element': 'earth',
        'role_type': 'warrior',
        'description': '训练有素的步兵，攻守兼备，是队伍的中坚力量。',
        'avatar': '/static/images/characters/soldier.jpg',
        'illustration': '/static/images/characters/soldier-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 1000,
            'attack': 80,
            'defense': 60,
            'magic_attack': 30,
            'magic_defense': 40,
            'speed': 70
        },
        'skills': [
            {'id': 'skill-1', 'name': '冲锋斩击', 'type': 'physical', 'power': 100, 'element': 'earth', 'cooldown': 2, 'target': 'single',
             'description': '冲锋向前，对敌方造成物理伤害'},
            {'id': 'skill-2', 'name': '坚守阵地', 'type': 'buff', 'power': 0, 'element': 'earth', 'cooldown': 3, 'target': 'self',
             'description': '提升自身物防'},
        ]
    },
    {
        'id': 'archer',
        'name': '弓箭手',
        'name_en': 'Archer',
        'title': '远程射手',
        'era': '通用',
        'origin': '猎手村',
        'element': 'wind',
        'role_type': 'assassin',
        'description': '敏捷的远程单位，擅长从远处给予敌人致命打击。',
        'avatar': '/static/images/characters/archer.jpg',
        'illustration': '/static/images/characters/archer-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 700,
            'attack': 100,
            'defense': 40,
            'magic_attack': 50,
            'magic_defense': 35,
            'speed': 100
        },
        'skills': [
            {'id': 'skill-1', 'name': '穿云箭', 'type': 'physical', 'power': 120, 'element': 'wind', 'cooldown': 2, 'target': 'single',
             'description': '射出强力一箭，对敌方造成风属性物理伤害'},
            {'id': 'skill-2', 'name': '快速射击', 'type': 'physical', 'power': 60, 'element': 'wind', 'cooldown': 1, 'target': 'single',
             'description': '快速射击，造成物理伤害'},
        ]
    },
    {
        'id': 'mage-apprentice',
        'name': '见习法师',
        'name_en': 'Mage Apprentice',
        'title': '魔法学徒',
        'era': '通用',
        'origin': '魔法学院',
        'element': 'water',
        'role_type': 'mage',
        'description': '初学魔法的学徒，虽然力量有限但潜力无限。',
        'avatar': '/static/images/characters/mage-apprentice.jpg',
        'illustration': '/static/images/characters/mage-apprentice-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 600,
            'attack': 40,
            'defense': 30,
            'magic_attack': 110,
            'magic_defense': 60,
            'speed': 80
        },
        'skills': [
            {'id': 'skill-1', 'name': '水弹术', 'type': 'magic', 'power': 100, 'element': 'water', 'cooldown': 1, 'target': 'single',
             'description': '发射水弹，对敌方造成水属性魔法伤害'},
            {'id': 'skill-2', 'name': '冰霜护盾', 'type': 'buff', 'power': 0, 'element': 'water', 'cooldown': 3, 'target': 'self',
             'description': '提升自身魔防'},
        ]
    },
    {
        'id': 'cavalry',
        'name': '骑兵',
        'name_en': 'Cavalry',
        'title': '冲锋骑士',
        'era': '通用',
        'origin': '骑士团',
        'element': 'fire',
        'role_type': 'warrior',
        'description': '骑乘战马的骑士，冲锋时势不可挡。',
        'avatar': '/static/images/characters/cavalry.jpg',
        'illustration': '/static/images/characters/cavalry-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 900,
            'attack': 90,
            'defense': 50,
            'magic_attack': 40,
            'magic_defense': 35,
            'speed': 120
        },
        'skills': [
            {'id': 'skill-1', 'name': '骑兵冲锋', 'type': 'physical', 'power': 110, 'element': 'fire', 'cooldown': 2, 'target': 'single',
             'description': '骑马冲锋，对敌方造成物理伤害'},
        ]
    },
    {
        'id': 'pikeman',
        'name': '长枪兵',
        'name_en': 'Pikeman',
        'title': '枪阵守卫',
        'era': '通用',
        'origin': '步兵营',
        'element': 'earth',
        'role_type': 'tank',
        'description': '手持长枪的步兵，擅长防御骑兵冲锋。',
        'avatar': '/static/images/characters/pikeman.jpg',
        'illustration': '/static/images/characters/pikeman-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 1200,
            'attack': 70,
            'defense': 80,
            'magic_attack': 20,
            'magic_defense': 50,
            'speed': 60
        },
        'skills': [
            {'id': 'skill-1', 'name': '枪阵', 'type': 'physical', 'power': 90, 'element': 'earth', 'cooldown': 2, 'target': 'single',
             'description': '长枪刺击，对敌方造成物理伤害'},
        ]
    },
    {
        'id': 'healer-apprentice',
        'name': '治疗学徒',
        'name_en': 'Healer Apprentice',
        'title': '见习医者',
        'era': '通用',
        'origin': '修道院',
        'element': 'light',
        'role_type': 'support',
        'description': '学习治疗术的学徒，能为队友恢复生命。',
        'avatar': '/static/images/characters/healer-apprentice.jpg',
        'illustration': '/static/images/characters/healer-apprentice-full.png',
        'rarity': 'common',
        'stats': {
            'hp': 650,
            'attack': 30,
            'defense': 40,
            'magic_attack': 60,
            'magic_defense': 80,
            'speed': 75
        },
        'skills': [
            {'id': 'skill-1', 'name': '治愈之光', 'type': 'heal', 'power': 80, 'element': 'light', 'cooldown': 2, 'target': 'single',
             'description': '为一名队友恢复生命值'},
        ]
    },
    # ========== 传说角色 ==========
    {
        'id': 'zhuge-liang',
        'name': '诸葛亮',
        'name_en': 'Zhuge Liang',
        'title': '卧龙先生',
        'era': '三国',
        'origin': '蜀汉',
        'element': 'water',
        'role_type': 'mage',
        'description': '智计无双，运筹帷幄。三国时期蜀汉丞相，以智谋著称于世。',
        'avatar': '/static/images/characters/zhuge-liang.jpg',
        'illustration': '/static/images/characters/zhuge-liang-full.png',
        'rarity': 'legendary',
        'stats': {
            'hp': 800,
            'attack': 60,
            'defense': 50,
            'magic_attack': 180,
            'magic_defense': 100,
            'speed': 90
        },
        'skills': [
            {'id': 'skill-1', 'name': '八阵图', 'type': 'magic', 'power': 120, 'element': 'water', 'cooldown': 2, 'target': 'single',
             'description': '布下八卦阵，对敌方造成水属性魔法伤害'},
            {'id': 'skill-2', 'name': '火烧连营', 'type': 'magic', 'power': 100, 'element': 'fire', 'cooldown': 3, 'target': 'all',
             'description': '施展火攻计策，对敌方全体造成火焰魔法伤害'},
            {'id': 'skill-3', 'name': '空城计', 'type': 'buff', 'power': 0, 'element': 'wind', 'cooldown': 4, 'target': 'self',
             'description': '虚张声势，提升自身物防和魔防'},
        ]
    },
    {
        'id': 'guan-yu',
        'name': '关羽',
        'name_en': 'Guan Yu',
        'title': '武圣',
        'era': '三国',
        'origin': '蜀汉',
        'element': 'fire',
        'role_type': 'warrior',
        'description': '义薄云天，武艺超群。蜀汉五虎上将之首，忠义无双。',
        'avatar': '/static/images/characters/guan-yu.jpg',
        'illustration': '/static/images/characters/guan-yu-full.png',
        'rarity': 'epic',
        'stats': {
            'hp': 1200,
            'attack': 160,
            'defense': 80,
            'magic_attack': 50,
            'magic_defense': 60,
            'speed': 85
        },
        'skills': [
            {'id': 'skill-1', 'name': '青龙偃月', 'type': 'physical', 'power': 140, 'element': 'fire', 'cooldown': 2, 'target': 'single',
             'description': '挥舞青龙偃月刀，对敌方造成大量物理伤害'},
            {'id': 'skill-2', 'name': '过五关斩六将', 'type': 'physical', 'power': 100, 'element': 'fire', 'cooldown': 1, 'target': 'single',
             'description': '连续攻击，对敌方造成物理伤害'},
            {'id': 'skill-3', 'name': '武圣之威', 'type': 'buff', 'power': 0, 'element': 'fire', 'cooldown': 4, 'target': 'self',
             'description': '提升自身物攻和物防'},
        ]
    },
    {
        'id': 'hua-mulan',
        'name': '花木兰',
        'name_en': 'Hua Mulan',
        'title': '巾帼英雄',
        'era': '北魏',
        'origin': '中国',
        'element': 'wind',
        'role_type': 'warrior',
        'description': '替父从军，英勇善战。中国古代女英雄，忠孝两全。',
        'avatar': '/static/images/characters/hua-mulan.jpg',
        'illustration': '/static/images/characters/hua-mulan-full.png',
        'rarity': 'epic',
        'stats': {
            'hp': 1000,
            'attack': 140,
            'defense': 70,
            'magic_attack': 60,
            'magic_defense': 70,
            'speed': 110
        },
        'skills': [
            {'id': 'skill-1', 'name': '破阵斩将', 'type': 'physical', 'power': 120, 'element': 'wind', 'cooldown': 2, 'target': 'single',
             'description': '冲锋陷阵，对敌方造成风属性物理伤害'},
            {'id': 'skill-2', 'name': '木兰从军', 'type': 'physical', 'power': 90, 'element': 'wind', 'cooldown': 1, 'target': 'single',
             'description': '快速连击，降低敌方物防'},
            {'id': 'skill-3', 'name': '代父从军', 'type': 'buff', 'power': 0, 'element': 'wind', 'cooldown': 3, 'target': 'self',
             'description': '提升自身速度和物防'},
        ]
    },
    {
        'id': 'arthur',
        'name': '亚瑟王',
        'name_en': 'King Arthur',
        'title': '永恒之王',
        'era': '中世纪',
        'origin': '不列颠',
        'element': 'light',
        'role_type': 'warrior',
        'description': '不列颠传说之王，圣剑持有者，骑士精神的象征。',
        'avatar': '/static/images/characters/arthur.jpg',
        'illustration': '/static/images/characters/arthur-full.png',
        'rarity': 'epic',
        'stats': {
            'hp': 1100,
            'attack': 150,
            'defense': 90,
            'magic_attack': 80,
            'magic_defense': 80,
            'speed': 80
        },
        'skills': [
            {'id': 'skill-1', 'name': '圣剑斩击', 'type': 'physical', 'power': 130, 'element': 'light', 'cooldown': 2, 'target': 'single',
             'description': '挥舞圣剑，对敌方造成光属性物理伤害'},
            {'id': 'skill-2', 'name': '王者之剑', 'type': 'magic', 'power': 110, 'element': 'light', 'cooldown': 3, 'target': 'single',
             'description': '释放圣剑之力，对敌方造成光属性魔法伤害'},
            {'id': 'skill-3', 'name': '骑士荣耀', 'type': 'buff', 'power': 0, 'element': 'light', 'cooldown': 4, 'target': 'allies',
             'description': '提升全队物攻和物防'},
        ]
    },
    {
        'id': 'cao-cao',
        'name': '曹操',
        'name_en': 'Cao Cao',
        'title': '乱世枭雄',
        'era': '三国',
        'origin': '曹魏',
        'element': 'dark',
        'role_type': 'warrior',
        'description': '治世之能臣，乱世之枭雄。曹魏奠基者，雄才大略。',
        'avatar': '/static/images/characters/cao-cao.jpg',
        'illustration': '/static/images/characters/cao-cao-full.png',
        'rarity': 'epic',
        'stats': {
            'hp': 1000,
            'attack': 130,
            'defense': 75,
            'magic_attack': 100,
            'magic_defense': 80,
            'speed': 95
        },
        'skills': [
            {'id': 'skill-1', 'name': '霸业之剑', 'type': 'physical', 'power': 110, 'element': 'dark', 'cooldown': 2, 'target': 'single',
             'description': '霸王之剑，对敌方造成暗属性物理伤害'},
            {'id': 'skill-2', 'name': '奸雄之计', 'type': 'magic', 'power': 90, 'element': 'dark', 'cooldown': 3, 'target': 'single',
             'description': '阴险计谋，降低敌方物攻和物防'},
            {'id': 'skill-3', 'name': '唯才是举', 'type': 'buff', 'power': 0, 'element': 'dark', 'cooldown': 4, 'target': 'self',
             'description': '提升自身所有属性'},
        ]
    },
    {
        'id': 'miyamoto',
        'name': '宫本武藏',
        'name_en': 'Miyamoto Musashi',
        'title': '剑圣',
        'era': '江户',
        'origin': '日本',
        'element': 'wind',
        'role_type': 'assassin',
        'description': '日本历史上最伟大的剑豪，二天一流的创始人。',
        'avatar': '/static/images/characters/miyamoto.jpg',
        'illustration': '/static/images/characters/miyamoto-full.png',
        'rarity': 'rare',
        'stats': {
            'hp': 850,
            'attack': 170,
            'defense': 50,
            'magic_attack': 40,
            'magic_defense': 50,
            'speed': 130
        },
        'skills': [
            {'id': 'skill-1', 'name': '二天一流', 'type': 'physical', 'power': 150, 'element': 'wind', 'cooldown': 3, 'target': 'single',
             'description': '双刀流必杀技，对敌方造成大量物理伤害'},
            {'id': 'skill-2', 'name': '燕返', 'type': 'physical', 'power': 80, 'element': 'wind', 'cooldown': 1, 'target': 'single',
             'description': '快速三连斩，必定先手'},
            {'id': 'skill-3', 'name': '剑道极意', 'type': 'buff', 'power': 0, 'element': 'wind', 'cooldown': 4, 'target': 'self',
             'description': '大幅提升物攻和速度'},
        ]
    },
    # ---- 普通角色 ----
    {
        'id': 'soldier',
        'name': '步兵',
        'name_en': 'Soldier',
        'title': '忠诚卫士',
        'era': '中世纪',
        'origin': '大陆',
        'element': 'earth',
        'role_type': 'tank',
        'description': '经验丰富的步兵，手持长矛与盾牌，是战场上最可靠的防线。',
        'avatar': '/static/images/characters/soldier.jpg',
        'illustration': '/static/images/characters/soldier.jpg',
        'rarity': 'common',
        'stats': {'hp': 1200, 'attack': 70, 'defense': 90, 'magic_attack': 20, 'magic_defense': 60, 'speed': 55},
        'skills': [
            {'id': 'skill-1', 'name': '长矛突刺', 'type': 'physical', 'power': 80, 'element': 'earth', 'cooldown': 1, 'target': 'single',
             'description': '用长矛刺击敌人，造成物理伤害'},
            {'id': 'skill-2', 'name': '盾墙', 'type': 'buff', 'power': 0, 'element': 'earth', 'cooldown': 3, 'target': 'self',
             'description': '举起盾牌，大幅提升物防'},
        ]
    },
    {
        'id': 'archer',
        'name': '弓箭手',
        'name_en': 'Archer',
        'title': '百步穿杨',
        'era': '中世纪',
        'origin': '大陆',
        'element': 'wind',
        'role_type': 'assassin',
        'description': '精通弓术的远程射手，擅长在远处精准狙击敌方要害。',
        'avatar': '/static/images/characters/archer.jpg',
        'illustration': '/static/images/characters/archer.jpg',
        'rarity': 'common',
        'stats': {'hp': 700, 'attack': 110, 'defense': 40, 'magic_attack': 30, 'magic_defense': 40, 'speed': 100},
        'skills': [
            {'id': 'skill-1', 'name': '精准射击', 'type': 'physical', 'power': 90, 'element': 'wind', 'cooldown': 1, 'target': 'single',
             'description': '瞄准要害射出一箭，造成物理伤害'},
            {'id': 'skill-2', 'name': '箭雨', 'type': 'physical', 'power': 55, 'element': 'wind', 'cooldown': 3, 'target': 'all',
             'description': '向天空射出箭雨，对全体敌人造成伤害'},
        ]
    },
    {
        'id': 'mage-apprentice',
        'name': '见习法师',
        'name_en': 'Mage Apprentice',
        'title': '魔法学徒',
        'era': '中世纪',
        'origin': '大陆',
        'element': 'fire',
        'role_type': 'mage',
        'description': '刚从法师学院毕业的年轻法师，虽然经验不足但天赋极高。',
        'avatar': '/static/images/characters/mage-apprentice.jpg',
        'illustration': '/static/images/characters/mage-apprentice.jpg',
        'rarity': 'common',
        'stats': {'hp': 650, 'attack': 40, 'defense': 35, 'magic_attack': 120, 'magic_defense': 70, 'speed': 80},
        'skills': [
            {'id': 'skill-1', 'name': '火球术', 'type': 'magic', 'power': 85, 'element': 'fire', 'cooldown': 1, 'target': 'single',
             'description': '释放一颗火球，造成火属性魔法伤害'},
            {'id': 'skill-2', 'name': '冰冻术', 'type': 'magic', 'power': 70, 'element': 'water', 'cooldown': 2, 'target': 'single',
             'description': '冻结敌人，造成水属性魔法伤害并降低速度'},
        ]
    },
    {
        'id': 'cleopatra',
        'name': '克娄巴特拉',
        'name_en': 'Cleopatra',
        'title': '尼罗河女王',
        'era': '古埃及',
        'origin': '埃及',
        'element': 'water',
        'role_type': 'support',
        'description': '古埃及最后的法老，以智慧和美貌闻名于世，精通治愈之术。',
        'avatar': '/static/images/characters/cleopatra.jpg',
        'illustration': '/static/images/characters/cleopatra.jpg',
        'rarity': 'epic',
        'stats': {'hp': 900, 'attack': 50, 'defense': 60, 'magic_attack': 140, 'magic_defense': 110, 'speed': 88},
        'skills': [
            {'id': 'skill-1', 'name': '尼罗之泪', 'type': 'magic', 'power': 100, 'element': 'water', 'cooldown': 2, 'target': 'single',
             'description': '召唤尼罗河之力，对敌方造成水属性魔法伤害'},
            {'id': 'skill-2', 'name': '生命之泉', 'type': 'heal', 'power': 120, 'element': 'water', 'cooldown': 3, 'target': 'allies',
             'description': '治愈全队，恢复生命值'},
            {'id': 'skill-3', 'name': '女王威仪', 'type': 'buff', 'power': 0, 'element': 'water', 'cooldown': 4, 'target': 'allies',
             'description': '提升全队魔攻和魔防'},
        ]
    },
    {
        'id': 'viking-ragnar',
        'name': '拉格纳',
        'name_en': 'Ragnar',
        'title': '北海之王',
        'era': '维京时代',
        'origin': '斯堪的纳维亚',
        'element': 'earth',
        'role_type': 'warrior',
        'description': '传说中的维京国王，率领龙头战船征服四方海域。',
        'avatar': '/static/images/characters/viking-ragnar.jpg',
        'illustration': '/static/images/characters/viking-ragnar.jpg',
        'rarity': 'rare',
        'stats': {'hp': 1100, 'attack': 140, 'defense': 70, 'magic_attack': 30, 'magic_defense': 50, 'speed': 85},
        'skills': [
            {'id': 'skill-1', 'name': '维京战斧', 'type': 'physical', 'power': 120, 'element': 'earth', 'cooldown': 2, 'target': 'single',
             'description': '挥舞巨斧猛击敌人，造成土属性物理伤害'},
            {'id': 'skill-2', 'name': '狂战士之怒', 'type': 'buff', 'power': 0, 'element': 'earth', 'cooldown': 3, 'target': 'self',
             'description': '进入狂暴状态，大幅提升物攻但降低物防'},
        ]
    },
    {
        'id': 'robin-hood',
        'name': '罗宾汉',
        'name_en': 'Robin Hood',
        'title': '侠盗义士',
        'era': '中世纪',
        'origin': '英格兰',
        'element': 'wind',
        'role_type': 'assassin',
        'description': '劫富济贫的传奇侠盗，箭无虚发，行踪如风。',
        'avatar': '/static/images/characters/robin-hood.jpg',
        'illustration': '/static/images/characters/robin-hood.jpg',
        'rarity': 'rare',
        'stats': {'hp': 800, 'attack': 155, 'defense': 45, 'magic_attack': 40, 'magic_defense': 50, 'speed': 125},
        'skills': [
            {'id': 'skill-1', 'name': '穿心箭', 'type': 'physical', 'power': 140, 'element': 'wind', 'cooldown': 2, 'target': 'single',
             'description': '一箭穿心，对单体造成巨大物理伤害'},
            {'id': 'skill-2', 'name': '丛林伏击', 'type': 'physical', 'power': 65, 'element': 'wind', 'cooldown': 1, 'target': 'single',
             'description': '从暗处突袭，有概率附加减速效果'},
            {'id': 'skill-3', 'name': '义贼之风', 'type': 'buff', 'power': 0, 'element': 'wind', 'cooldown': 4, 'target': 'self',
             'description': '提升自身闪避率和速度'},
        ]
    },
    {
        'id': 'joan-of-arc',
        'name': '贞德',
        'name_en': 'Joan of Arc',
        'title': '圣女',
        'era': '中世纪',
        'origin': '法兰西',
        'element': 'light',
        'role_type': 'support',
        'description': '法兰西的救世圣女，以不屈的信念引领军队走向胜利。',
        'avatar': '/static/images/characters/joan-of-arc.jpg',
        'illustration': '/static/images/characters/joan-of-arc.jpg',
        'rarity': 'legendary',
        'stats': {'hp': 1000, 'attack': 80, 'defense': 90, 'magic_attack': 160, 'magic_defense': 120, 'speed': 85},
        'skills': [
            {'id': 'skill-1', 'name': '圣光审判', 'type': 'magic', 'power': 130, 'element': 'light', 'cooldown': 2, 'target': 'single',
             'description': '召唤圣光降罚敌人，造成光属性魔法伤害'},
            {'id': 'skill-2', 'name': '圣女祈祷', 'type': 'heal', 'power': 150, 'element': 'light', 'cooldown': 3, 'target': 'allies',
             'description': '祈祷圣光，治愈全队并清除减益'},
            {'id': 'skill-3', 'name': '不灭军旗', 'type': 'buff', 'power': 0, 'element': 'light', 'cooldown': 5, 'target': 'allies',
             'description': '举起军旗鼓舞全队，大幅提升全队所有属性'},
        ]
    },
    {
        'id': 'genghis-khan',
        'name': '成吉思汗',
        'name_en': 'Genghis Khan',
        'title': '草原雄鹰',
        'era': '蒙古帝国',
        'origin': '蒙古',
        'element': 'earth',
        'role_type': 'warrior',
        'description': '蒙古帝国的缔造者，征服了横跨欧亚的辽阔疆域。',
        'avatar': '/static/images/characters/genghis-khan.jpg',
        'illustration': '/static/images/characters/genghis-khan.jpg',
        'rarity': 'legendary',
        'stats': {'hp': 1100, 'attack': 170, 'defense': 80, 'magic_attack': 60, 'magic_defense': 70, 'speed': 100},
        'skills': [
            {'id': 'skill-1', 'name': '铁骑冲锋', 'type': 'physical', 'power': 145, 'element': 'earth', 'cooldown': 2, 'target': 'single',
             'description': '率领铁骑冲锋，造成毁灭性物理伤害'},
            {'id': 'skill-2', 'name': '万马奔腾', 'type': 'physical', 'power': 90, 'element': 'earth', 'cooldown': 3, 'target': 'all',
             'description': '召唤万骑践踏，对全体敌人造成物理伤害'},
            {'id': 'skill-3', 'name': '大汗威压', 'type': 'buff', 'power': 0, 'element': 'earth', 'cooldown': 4, 'target': 'self',
             'description': '释放帝王气场，大幅提升物攻和速度'},
        ]
    },
]

# 关卡配置
CHAPTERS = [
    {
        'id': 'chapter-1',
        'name': '初入战场',
        'description': '新手村，开始你的冒险之旅',
        'required_level': 1,  # 解锁需要的玩家等级
        # 轻量剧情：关卡前/后对话（支持跳过；前端展示）
        'dialogue': {
            'pre': [
                {'speaker': '旁白', 'text': '号角响起，你踏入演武场。真正的考验，从现在开始。'},
                {'speaker': '教官', 'text': '先从基础开始——稳住阵脚，瞄准目标。'},
            ],
            'post': [
                {'speaker': '教官', 'text': '不错。记住：胜利不是运气，是选择与节奏。'},
            ],
        },
        'stages': [
            {
                'id': 'stage-1-1',
                'name': '初次试炼',
                'description': '击败训练假人，证明你的实力',
                'difficulty': 'easy',
                'enemy_ids': ['soldier'],
                'enemy_levels': [1],
                'energy_cost': 5,
                'recommended_level': 1,
                'required_level': 1,  # 进入需要的玩家等级
                'rewards': {'gold': 100, 'exp': 50},
                'first_clear_rewards': {'gold': 500, 'gems': 50}
            },
            {
                'id': 'stage-1-2',
                'name': '遭遇强敌',
                'description': '遭遇敌方斥候，击退他们',
                'difficulty': 'easy',
                'enemy_ids': ['archer'],
                'enemy_levels': [2],
                'energy_cost': 5,
                'recommended_level': 2,
                'required_level': 1,
                'rewards': {'gold': 120, 'exp': 60},
                'first_clear_rewards': {'gold': 600, 'gems': 50}
            },
            {
                'id': 'stage-1-3',
                'name': '首战告捷',
                'description': '击败敌方先锋',
                'difficulty': 'normal',
                'enemy_ids': ['mage-apprentice'],
                'enemy_levels': [3],
                'energy_cost': 6,
                'recommended_level': 3,
                'required_level': 2,
                'rewards': {'gold': 150, 'exp': 80},
                'first_clear_rewards': {'gold': 800, 'gems': 80}
            }
        ]
    },
    {
        'id': 'chapter-2',
        'name': '名将云集',
        'description': '各路名将齐聚，展现你的真正实力',
        'required_level': 10,  # 需要10级解锁
        'dialogue': {
            'pre': [
                {'speaker': '旁白', 'text': '名将的气息在场中交错，你能听见刀锋与誓言的回响。'},
                {'speaker': '神秘使者', 'text': '想走得更远？就拿下他们的认可。'},
            ],
            'post': [
                {'speaker': '神秘使者', 'text': '很好。你的名字，开始被人记住了。'},
            ],
        },
        'stages': [
            {
                'id': 'stage-2-1',
                'name': '武圣之威',
                'description': '面对武圣关羽的挑战',
                'difficulty': 'normal',
                'enemy_ids': ['guan-yu'],
                'enemy_levels': [10],
                'energy_cost': 10,
                'recommended_level': 10,
                'required_level': 8,
                'rewards': {'gold': 300, 'exp': 150, 'gems': 20},
                'first_clear_rewards': {'gold': 1000, 'gems': 100}
            },
            {
                'id': 'stage-2-2',
                'name': '骑士传说',
                'description': '与不列颠之王对决',
                'difficulty': 'normal',
                'enemy_ids': ['arthur'],
                'enemy_levels': [12],
                'energy_cost': 12,
                'recommended_level': 12,
                'required_level': 10,
                'rewards': {'gold': 350, 'exp': 180, 'gems': 25},
                'first_clear_rewards': {'gold': 1200, 'gems': 120}
            },
            {
                'id': 'stage-2-3',
                'name': '巾帼不让须眉',
                'description': '挑战女中豪杰花木兰',
                'difficulty': 'hard',
                'enemy_ids': ['hua-mulan', 'miyamoto'],
                'enemy_levels': [15, 12],
                'energy_cost': 15,
                'recommended_level': 15,
                'required_level': 12,
                'rewards': {'gold': 500, 'exp': 250, 'gems': 30},
                'first_clear_rewards': {'gold': 1500, 'gems': 150}
            }
        ]
    },
    {
        'id': 'chapter-3',
        'name': '传说之战',
        'description': '传说级英雄的挑战，证明你是真正的英雄',
        'required_level': 20,  # 需要20级解锁
        'dialogue': {
            'pre': [
                {'speaker': '旁白', 'text': '传说站在你面前。你能做的，只有向前。'},
                {'speaker': '诸葛亮', 'text': '胜负不在刀剑，在你心中那一念取舍。'},
            ],
            'post': [
                {'speaker': '诸葛亮', 'text': '棋局已开。下一步，就看你如何落子。'},
            ],
        },
        'stages': [
            {
                'id': 'stage-3-1',
                'name': '卧龙出山',
                'description': '面对智谋无双的诸葛亮',
                'difficulty': 'hard',
                'enemy_ids': ['zhuge-liang'],
                'enemy_levels': [20],
                'energy_cost': 15,
                'recommended_level': 20,
                'required_level': 18,
                'rewards': {'gold': 500, 'exp': 300, 'gems': 50},
                'first_clear_rewards': {'gold': 2000, 'gems': 200}
            },
            {
                'id': 'stage-3-2',
                'name': '英雄会战',
                'description': '同时面对多位英雄',
                'difficulty': 'hard',
                'enemy_ids': ['guan-yu', 'arthur'],
                'enemy_levels': [18, 18],
                'energy_cost': 18,
                'recommended_level': 22,
                'required_level': 20,
                'rewards': {'gold': 600, 'exp': 350, 'gems': 60},
                'first_clear_rewards': {'gold': 2500, 'gems': 250}
            },
            {
                'id': 'stage-3-3',
                'name': '最终决战',
                'description': '传说级终极挑战',
                'difficulty': 'hell',
                'enemy_ids': ['zhuge-liang', 'guan-yu', 'arthur'],
                'enemy_levels': [25, 25, 25],
                'energy_cost': 20,
                'recommended_level': 25,
                'required_level': 22,
                'rewards': {'gold': 1000, 'exp': 500, 'gems': 100},
                'first_clear_rewards': {'gold': 5000, 'gems': 500}
            }
        ]
    },
    {
        'id': 'chapter-4',
        'name': '暗潮涌动',
        'description': '暗影势力浮出水面，战场规则开始改变',
        'required_level': 30,  # 需要30级解锁
        'dialogue': {
            'pre': [
                {'speaker': '旁白', 'text': '胜利带来的喧嚣尚未散去，新的阴影已在城外蔓延。'},
                {'speaker': '神秘使者', 'text': '别被掌声迷了眼——真正的敌人，才刚刚入局。'},
            ],
            'post': [
                {'speaker': '神秘使者', 'text': '你已触到暗潮的边缘。下一战，不再只是较量。'},
            ],
        },
        'stages': [
            {
                'id': 'stage-4-1',
                'name': '夜行斥候',
                'description': '击退潜入的暗影斥候',
                'difficulty': 'normal',
                'enemy_ids': ['miyamoto', 'archer'],
                'enemy_levels': [26, 26],
                'energy_cost': 18,
                'recommended_level': 26,
                'required_level': 25,
                'rewards': {'gold': 900, 'exp': 450, 'gems': 40},
                'first_clear_rewards': {'gold': 2800, 'gems': 200}
            },
            {
                'id': 'stage-4-2',
                'name': '破阵之谋',
                'description': '识破敌方诡计，守住阵线',
                'difficulty': 'hard',
                'enemy_ids': ['cao-cao', 'mage-apprentice'],
                'enemy_levels': [28, 27],
                'energy_cost': 20,
                'recommended_level': 28,
                'required_level': 27,
                'rewards': {'gold': 1100, 'exp': 520, 'gems': 50},
                'first_clear_rewards': {'gold': 3200, 'gems': 250}
            },
            {
                'id': 'stage-4-3',
                'name': '暗影统领',
                'description': '击败暗影统领，阻止其召集援军',
                'difficulty': 'hell',
                'enemy_ids': ['cao-cao', 'guan-yu', 'arthur'],
                'enemy_levels': [30, 29, 29],
                'energy_cost': 22,
                'recommended_level': 30,
                'required_level': 28,
                'rewards': {'gold': 1500, 'exp': 650, 'gems': 80},
                'first_clear_rewards': {'gold': 4200, 'gems': 350}
            }
        ]
    }
]

# 难度配置
DIFFICULTY_NAMES = {
    'easy': '简单',
    'normal': '普通',
    'hard': '困难',
    'hell': '地狱',
    'nightmare': '噩梦'
}

DIFFICULTY_COLORS = {
    'easy': '#22c55e',
    'normal': '#3b82f6',
    'hard': '#f59e0b',
    'hell': '#ef4444',
    'nightmare': '#9333ea'
}

# ==================== 战斗模式 ====================
BATTLE_MODES = {
    '1v1': {'name': '单挑', 'team_size': 1, 'icon': '⚔️', 'description': '一对一英雄对决'},
    '3v3': {'name': '鏖战', 'team_size': 3, 'icon': '🗡️', 'description': '三人小队作战'},
    '5v5': {'name': '大战', 'team_size': 5, 'icon': '⚔️🛡️', 'description': '五人团队决战'},
}

# ==================== 战斗道具 ====================
BATTLE_ITEMS = [
    {'id': 'potion-hp-s',   'name': '小回复药水', 'icon': '🧪', 'description': '恢复30%最大生命值',    'effect': 'heal',       'value': 0.3,  'max_per_battle': 3},
    {'id': 'potion-hp-l',   'name': '大回复药水', 'icon': '🧴', 'description': '恢复60%最大生命值',    'effect': 'heal',       'value': 0.6,  'max_per_battle': 1},
    {'id': 'potion-atk',    'name': '力量药剂',   'icon': '💪', 'description': '提升攻击力25%持续3回合','effect': 'buff_atk',   'value': 0.25, 'max_per_battle': 2, 'duration': 3},
    {'id': 'potion-def',    'name': '铁壁药剂',   'icon': '🛡️', 'description': '提升防御力30%持续3回合','effect': 'buff_def',   'value': 0.3,  'max_per_battle': 2, 'duration': 3},
    {'id': 'potion-speed',  'name': '疾风药剂',   'icon': '💨', 'description': '提升速度20%持续3回合',  'effect': 'buff_speed', 'value': 0.2,  'max_per_battle': 2, 'duration': 3},
    {'id': 'potion-revive', 'name': '复活卷轴',   'icon': '📜', 'description': '复活一名阵亡角色(50%HP)','effect': 'revive',   'value': 0.5,  'max_per_battle': 1},
]

# ==================== 日常材料副本 ====================
DAILY_DUNGEONS = [
    {
        'id': 'daily-forge',
        'name': '铸魂熔炉',
        'icon': '🔥',
        'description': '在烈火中锤炼英雄之魂，获取大量经验书',
        'reward_type': 'exp_books',
        'battle_mode': '3v3',
        'open_days': [1, 3, 5, 7],  # 周一三五日
        'levels': [
            {'id': 'forge-1', 'name': '初级熔炉', 'difficulty': 'easy',   'recommended_level': 5,  'energy_cost': 10, 'enemy_ids': ['soldier', 'soldier', 'archer'],        'enemy_levels': [5, 5, 4],    'rewards': {'exp_books': 10, 'gold': 200}},
            {'id': 'forge-2', 'name': '中级熔炉', 'difficulty': 'normal', 'recommended_level': 15, 'energy_cost': 15, 'enemy_ids': ['hua-mulan', 'miyamoto', 'archer'],      'enemy_levels': [15, 14, 13], 'rewards': {'exp_books': 25, 'gold': 500}},
            {'id': 'forge-3', 'name': '高级熔炉', 'difficulty': 'hard',   'recommended_level': 25, 'energy_cost': 20, 'enemy_ids': ['guan-yu', 'arthur', 'cao-cao'],         'enemy_levels': [25, 24, 23], 'rewards': {'exp_books': 50, 'gold': 1000}},
        ]
    },
    {
        'id': 'daily-treasure',
        'name': '聚宝秘窟',
        'icon': '💰',
        'description': '深入宝藏洞窟，搜刮堆积如山的金币',
        'reward_type': 'gold',
        'battle_mode': '3v3',
        'open_days': [2, 4, 6, 7],  # 周二四六日
        'levels': [
            {'id': 'treasure-1', 'name': '秘窟外围', 'difficulty': 'easy',   'recommended_level': 5,  'energy_cost': 10, 'enemy_ids': ['soldier', 'archer', 'soldier'],          'enemy_levels': [5, 5, 4],    'rewards': {'gold': 3000}},
            {'id': 'treasure-2', 'name': '秘窟深层', 'difficulty': 'normal', 'recommended_level': 15, 'energy_cost': 15, 'enemy_ids': ['cao-cao', 'mage-apprentice', 'soldier'], 'enemy_levels': [15, 14, 13], 'rewards': {'gold': 8000}},
            {'id': 'treasure-3', 'name': '秘窟宝库', 'difficulty': 'hard',   'recommended_level': 25, 'energy_cost': 20, 'enemy_ids': ['zhuge-liang', 'guan-yu', 'hua-mulan'],  'enemy_levels': [25, 24, 23], 'rewards': {'gold': 20000}},
        ]
    },
    {
        'id': 'daily-starpath',
        'name': '星辉之径',
        'icon': '⭐',
        'description': '追寻星辉的轨迹，收集珍贵的星魂碎片',
        'reward_type': 'star_soul',
        'battle_mode': '3v3',
        'open_days': [1, 4, 7],  # 周一四日
        'levels': [
            {'id': 'star-1', 'name': '微光小径', 'difficulty': 'easy',   'recommended_level': 10, 'energy_cost': 12, 'enemy_ids': ['miyamoto', 'archer', 'soldier'],           'enemy_levels': [10, 9, 8],   'rewards': {'star_soul': 3, 'gold': 300}},
            {'id': 'star-2', 'name': '星河走廊', 'difficulty': 'normal', 'recommended_level': 20, 'energy_cost': 18, 'enemy_ids': ['arthur', 'hua-mulan', 'cao-cao'],           'enemy_levels': [20, 19, 18], 'rewards': {'star_soul': 6, 'gold': 600}},
            {'id': 'star-3', 'name': '星辉圣殿', 'difficulty': 'hard',   'recommended_level': 28, 'energy_cost': 22, 'enemy_ids': ['zhuge-liang', 'guan-yu', 'genghis-khan'],  'enemy_levels': [28, 27, 26], 'rewards': {'star_soul': 12, 'gold': 1200}},
        ]
    },
    {
        'id': 'daily-mine',
        'name': '灵石矿脉',
        'icon': '💎',
        'description': '深入矿脉采掘灵石，用于英雄突破',
        'reward_type': 'breakthrough_stone',
        'battle_mode': '3v3',
        'open_days': [2, 5, 7],  # 周二五日
        'levels': [
            {'id': 'mine-1', 'name': '浅层矿道', 'difficulty': 'easy',   'recommended_level': 10, 'energy_cost': 12, 'enemy_ids': ['soldier', 'soldier', 'mage-apprentice'],         'enemy_levels': [10, 9, 8],   'rewards': {'breakthrough_stone': 2, 'gold': 300}},
            {'id': 'mine-2', 'name': '深层矿道', 'difficulty': 'normal', 'recommended_level': 20, 'energy_cost': 18, 'enemy_ids': ['viking-ragnar', 'robin-hood', 'archer'],         'enemy_levels': [20, 19, 18], 'rewards': {'breakthrough_stone': 5, 'gold': 600}},
            {'id': 'mine-3', 'name': '矿脉核心', 'difficulty': 'hard',   'recommended_level': 28, 'energy_cost': 22, 'enemy_ids': ['joan-of-arc', 'genghis-khan', 'cleopatra'],      'enemy_levels': [28, 27, 26], 'rewards': {'breakthrough_stone': 10, 'gold': 1200}},
        ]
    },
]

# ==================== 英雄试炼（1v1 单挑副本）====================
HERO_TRIALS = {
    'id': 'hero-trials',
    'name': '武神殿',
    'icon': '🏛️',
    'description': '与传说中的武神一对一对决，证明你是真正的强者',
    'battle_mode': '1v1',
    'bosses': [
        {'id': 'trial-1',  'name': '剑圣试炼',     'boss_id': 'miyamoto',      'boss_level': 8,  'difficulty': 'easy',   'energy_cost': 10, 'recommended_level': 8,  'rewards': {'gold': 1000, 'gems': 30,  'exp_books': 5}},
        {'id': 'trial-2',  'name': '花木兰的考验',  'boss_id': 'hua-mulan',     'boss_level': 15, 'difficulty': 'normal', 'energy_cost': 15, 'recommended_level': 15, 'rewards': {'gold': 2000, 'gems': 50,  'exp_books': 10}},
        {'id': 'trial-3',  'name': '奸雄之刃',     'boss_id': 'cao-cao',       'boss_level': 18, 'difficulty': 'normal', 'energy_cost': 15, 'recommended_level': 18, 'rewards': {'gold': 2500, 'gems': 60,  'star_soul': 3}},
        {'id': 'trial-4',  'name': '圆桌骑士的荣耀','boss_id': 'arthur',        'boss_level': 22, 'difficulty': 'hard',   'energy_cost': 18, 'recommended_level': 22, 'rewards': {'gold': 3000, 'gems': 80,  'star_soul': 5}},
        {'id': 'trial-5',  'name': '武圣降临',     'boss_id': 'guan-yu',       'boss_level': 25, 'difficulty': 'hard',   'energy_cost': 18, 'recommended_level': 25, 'rewards': {'gold': 4000, 'gems': 100, 'star_soul': 8}},
        {'id': 'trial-6',  'name': '卧龙绝智',     'boss_id': 'zhuge-liang',   'boss_level': 28, 'difficulty': 'hell',   'energy_cost': 20, 'recommended_level': 28, 'rewards': {'gold': 5000, 'gems': 120, 'star_soul': 10}},
        {'id': 'trial-7',  'name': '圣女之怒',     'boss_id': 'joan-of-arc',   'boss_level': 30, 'difficulty': 'hell',   'energy_cost': 22, 'recommended_level': 30, 'rewards': {'gold': 6000, 'gems': 150, 'breakthrough_stone': 5}},
        {'id': 'trial-8',  'name': '天可汗',       'boss_id': 'genghis-khan',  'boss_level': 35, 'difficulty': 'nightmare','energy_cost': 25,'recommended_level': 35, 'rewards': {'gold': 8000, 'gems': 200, 'breakthrough_stone': 8}},
    ]
}

# ==================== 高难度副本 ====================
HARD_DUNGEONS = [
    {
        'id': 'abyss-gate',
        'name': '深渊之门',
        'icon': '🌀',
        'description': '来自深渊的怪物蜂拥而出，只有最强的团队才能封印裂缝',
        'battle_mode': '5v5',
        'levels': [
            {
                'id': 'abyss-1', 'name': '深渊裂隙·壹层', 'difficulty': 'hard',
                'recommended_level': 20, 'energy_cost': 25,
                'enemy_ids': ['soldier', 'archer', 'mage-apprentice', 'viking-ragnar', 'robin-hood'],
                'enemy_levels': [20, 20, 19, 19, 18],
                'rewards': {'gold': 5000, 'gems': 80, 'star_soul': 5}
            },
            {
                'id': 'abyss-2', 'name': '深渊裂隙·贰层', 'difficulty': 'hell',
                'recommended_level': 25, 'energy_cost': 30,
                'enemy_ids': ['cao-cao', 'hua-mulan', 'miyamoto', 'arthur', 'guan-yu'],
                'enemy_levels': [25, 25, 24, 24, 23],
                'rewards': {'gold': 10000, 'gems': 150, 'star_soul': 10}
            },
            {
                'id': 'abyss-3', 'name': '深渊裂隙·叁层', 'difficulty': 'nightmare',
                'recommended_level': 30, 'energy_cost': 35,
                'enemy_ids': ['zhuge-liang', 'guan-yu', 'arthur', 'joan-of-arc', 'genghis-khan'],
                'enemy_levels': [30, 30, 29, 29, 28],
                'rewards': {'gold': 20000, 'gems': 300, 'star_soul': 20, 'breakthrough_stone': 5}
            },
        ]
    },
    {
        'id': 'purgatory-tower',
        'name': '炼狱之塔',
        'icon': '🗼',
        'description': '登上无尽的炼狱之塔，每十层一个关卡BOSS，奖励随层数倍增',
        'battle_mode': '5v5',
        'levels': [
            {
                'id': 'tower-10',  'name': '炼狱之塔·第10层', 'difficulty': 'normal',
                'recommended_level': 15, 'energy_cost': 20,
                'enemy_ids': ['miyamoto', 'soldier', 'archer', 'mage-apprentice', 'soldier'],
                'enemy_levels': [15, 14, 13, 13, 12],
                'rewards': {'gold': 3000, 'gems': 50, 'exp_books': 15}
            },
            {
                'id': 'tower-20',  'name': '炼狱之塔·第20层', 'difficulty': 'hard',
                'recommended_level': 22, 'energy_cost': 25,
                'enemy_ids': ['cao-cao', 'hua-mulan', 'robin-hood', 'viking-ragnar', 'archer'],
                'enemy_levels': [22, 21, 21, 20, 20],
                'rewards': {'gold': 6000, 'gems': 100, 'exp_books': 30, 'star_soul': 5}
            },
            {
                'id': 'tower-30',  'name': '炼狱之塔·第30层', 'difficulty': 'hell',
                'recommended_level': 28, 'energy_cost': 30,
                'enemy_ids': ['guan-yu', 'arthur', 'zhuge-liang', 'joan-of-arc', 'cao-cao'],
                'enemy_levels': [28, 27, 27, 26, 26],
                'rewards': {'gold': 12000, 'gems': 200, 'breakthrough_stone': 8, 'star_soul': 10}
            },
            {
                'id': 'tower-50',  'name': '炼狱之塔·第50层', 'difficulty': 'nightmare',
                'recommended_level': 35, 'energy_cost': 35,
                'enemy_ids': ['genghis-khan', 'joan-of-arc', 'zhuge-liang', 'guan-yu', 'arthur'],
                'enemy_levels': [35, 34, 34, 33, 33],
                'rewards': {'gold': 25000, 'gems': 500, 'breakthrough_stone': 15, 'star_soul': 20}
            },
        ]
    },
]

# 默认每日任务
DEFAULT_DAILY_TASKS = [
    {
        'task_id': 'daily-login',
        'name': '每日签到',
        'description': '登录游戏',
        'target': 1,
        'reward_gold': 500,
        'reward_gems': 50,
        'reward_exp': 30
    },
    {
        'task_id': 'daily-battle',
        'name': '每日战斗',
        'description': '完成3次战斗',
        'target': 3,
        'reward_gold': 300,
        'reward_exp': 100
    },
    {
        'task_id': 'daily-summon',
        'name': '每日召唤',
        'description': '进行1次召唤',
        'target': 1,
        'reward_gold': 200,
        'reward_gems': 20,
        'reward_exp': 20
    },
    {
        'task_id': 'daily-levelup',
        'name': '强化角色',
        'description': '强化任意角色1次',
        'target': 1,
        'reward_gold': 400,
        'reward_exp': 50
    },
    {
        'task_id': 'daily-sweep',
        'name': '扫荡关卡',
        'description': '扫荡任意关卡1次',
        'target': 1,
        'reward_gold': 300,
        'reward_gems': 15,
        'reward_exp': 25
    },
    {
        'task_id': 'daily-team',
        'name': '调整队伍',
        'description': '编辑或更换队伍阵容1次',
        'target': 1,
        'reward_gold': 200,
        'reward_exp': 30
    }
]

# 七日目标
DEFAULT_SEVEN_DAY_GOALS = [
    {'day': 1, 'goal_id': 'day1-login',    'name': '首次登录',   'description': '登录游戏', 'target': 1, 'reward_gold': 1000, 'reward_gems': 100},
    {'day': 1, 'goal_id': 'day1-summon',   'name': '初次召唤',   'description': '完成1次召唤', 'target': 1, 'reward_gold': 500, 'reward_gems': 50},
    {'day': 1, 'goal_id': 'day1-battle',   'name': '初战告捷',   'description': '完成1次战斗', 'target': 1, 'reward_gold': 500, 'reward_gems': 50},
    {'day': 2, 'goal_id': 'day2-battle3',  'name': '战场老手',   'description': '累计完成3次战斗', 'target': 3, 'reward_gold': 800, 'reward_gems': 80},
    {'day': 2, 'goal_id': 'day2-levelup',  'name': '强化英雄',   'description': '强化任意角色1次', 'target': 1, 'reward_gold': 600, 'reward_gems': 50},
    {'day': 2, 'goal_id': 'day2-team',     'name': '组建队伍',   'description': '编辑你的战斗队伍', 'target': 1, 'reward_gold': 500, 'reward_gems': 50},
    {'day': 3, 'goal_id': 'day3-summon5',  'name': '召唤达人',   'description': '累计完成5次召唤', 'target': 5, 'reward_gold': 1200, 'reward_gems': 120},
    {'day': 3, 'goal_id': 'day3-char3',    'name': '英雄集结',   'description': '拥有3个不同角色', 'target': 3, 'reward_gold': 800, 'reward_gems': 80},
    {'day': 3, 'goal_id': 'day3-stage5',   'name': '关卡先锋',   'description': '通关5个关卡', 'target': 5, 'reward_gold': 1000, 'reward_gems': 100},
    {'day': 4, 'goal_id': 'day4-battle10', 'name': '百战不殆',   'description': '累计完成10次战斗', 'target': 10, 'reward_gold': 1500, 'reward_gems': 150},
    {'day': 4, 'goal_id': 'day4-level10',  'name': '初露锋芒',   'description': '将任意角色提升到10级', 'target': 10, 'reward_gold': 1000, 'reward_gems': 100},
    {'day': 4, 'goal_id': 'day4-breakthrough', 'name': '突破极限', 'description': '突破任意角色1次', 'target': 1, 'reward_gold': 1200, 'reward_gems': 120},
    {'day': 5, 'goal_id': 'day5-summon10', 'name': '召唤大师',   'description': '累计完成10次召唤', 'target': 10, 'reward_gold': 2000, 'reward_gems': 200},
    {'day': 5, 'goal_id': 'day5-char5',    'name': '群英荟萃',   'description': '拥有5个不同角色', 'target': 5, 'reward_gold': 1500, 'reward_gems': 150},
    {'day': 5, 'goal_id': 'day5-chapter2', 'name': '勇闯名将',   'description': '通关第2章全部关卡', 'target': 1, 'reward_gold': 2000, 'reward_gems': 200},
    {'day': 6, 'goal_id': 'day6-stage20',  'name': '身经百战',   'description': '累计通关20个关卡', 'target': 20, 'reward_gold': 2500, 'reward_gems': 250},
    {'day': 6, 'goal_id': 'day6-level20',  'name': '渐入佳境',   'description': '将任意角色提升到20级', 'target': 20, 'reward_gold': 2000, 'reward_gems': 200},
    {'day': 6, 'goal_id': 'day6-epic',     'name': '史诗英雄',   'description': '拥有至少1个史诗角色', 'target': 1, 'reward_gold': 1500, 'reward_gems': 150},
    {'day': 7, 'goal_id': 'day7-battle30', 'name': '战神降临',   'description': '累计完成30次战斗', 'target': 30, 'reward_gold': 3000, 'reward_gems': 300},
    {'day': 7, 'goal_id': 'day7-char8',    'name': '名将云集',   'description': '拥有8个不同角色', 'target': 8, 'reward_gold': 2500, 'reward_gems': 250},
    {'day': 7, 'goal_id': 'day7-chapter3', 'name': '传说之路',   'description': '通关第3章全部关卡', 'target': 1, 'reward_gold': 5000, 'reward_gems': 500},
]

# 商店商品配置
SHOP_ITEMS = [
    {'id': 'shop-gold-1',    'name': '金币小包',   'description': '获得 5000 金币', 'price_type': 'gems', 'price': 50,  'reward_type': 'gold',          'reward_amount': 5000,  'daily_limit': 5, 'category': 'resource'},
    {'id': 'shop-gold-2',    'name': '金币大包',   'description': '获得 25000 金币', 'price_type': 'gems', 'price': 200, 'reward_type': 'gold',          'reward_amount': 25000, 'daily_limit': 3, 'category': 'resource'},
    {'id': 'shop-exp-1',     'name': '经验书小包', 'description': '获得 20 本经验书', 'price_type': 'gold', 'price': 2000, 'reward_type': 'exp_books',    'reward_amount': 20,    'daily_limit': 5, 'category': 'resource'},
    {'id': 'shop-exp-2',     'name': '经验书大包', 'description': '获得 100 本经验书', 'price_type': 'gold', 'price': 8000, 'reward_type': 'exp_books',   'reward_amount': 100,   'daily_limit': 3, 'category': 'resource'},
    {'id': 'shop-energy-1',  'name': '体力药水',   'description': '恢复 50 点体力', 'price_type': 'gems', 'price': 30,  'reward_type': 'energy',         'reward_amount': 50,    'daily_limit': 5, 'category': 'resource'},
    {'id': 'shop-ticket-1',  'name': '召唤券',     'description': '获得 1 张召唤券', 'price_type': 'gems', 'price': 80,  'reward_type': 'summon_tickets', 'reward_amount': 1,     'daily_limit': 3, 'category': 'summon'},
    {'id': 'shop-ticket-5',  'name': '召唤券礼包', 'description': '获得 5 张召唤券', 'price_type': 'gems', 'price': 350, 'reward_type': 'summon_tickets', 'reward_amount': 5,     'daily_limit': 1, 'category': 'summon'},
    {'id': 'shop-starsoul-1','name': '星魂碎片',   'description': '获得 5 个星魂', 'price_type': 'gold', 'price': 10000, 'reward_type': 'star_soul',     'reward_amount': 5,     'daily_limit': 3, 'category': 'upgrade'},
]

# 主线任务配置
MAIN_QUESTS = [
    {'id': 'mq-1-1', 'chapter': 1, 'order': 1, 'name': '领取新手补给',   'description': '领取新手礼包中的资源',              'goal_type': 'claim_newbie',  'goal_target': 1, 'reward_gold': 500,  'reward_gems': 50},
    {'id': 'mq-1-2', 'chapter': 1, 'order': 2, 'name': '召唤你的第一位英雄', 'description': '前往群英馆进行一次召唤',       'goal_type': 'summon',        'goal_target': 1, 'reward_gold': 300,  'reward_gems': 30},
    {'id': 'mq-1-3', 'chapter': 1, 'order': 3, 'name': '强化英雄',       'description': '在军营中强化任意角色1次',           'goal_type': 'levelup',       'goal_target': 1, 'reward_gold': 500,  'reward_gems': 0},
    {'id': 'mq-1-4', 'chapter': 1, 'order': 4, 'name': '组建你的队伍',   'description': '在队伍中编辑你的战斗阵容',          'goal_type': 'team_set',      'goal_target': 1, 'reward_gold': 300,  'reward_gems': 30},
    {'id': 'mq-1-5', 'chapter': 1, 'order': 5, 'name': '初次试炼',       'description': '通关演武场关卡 1-1',               'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 800,  'reward_gems': 80,  'goal_param': 'stage-1-1'},
    {'id': 'mq-1-6', 'chapter': 1, 'order': 6, 'name': '通关第一章',     'description': '通关第一章全部关卡',                'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 1500, 'reward_gems': 150, 'goal_param': 'stage-1-3'},
    {'id': 'mq-2-1', 'chapter': 2, 'order': 1, 'name': '十连召唤',       'description': '完成一次十连召唤',                  'goal_type': 'summon_ten',    'goal_target': 1, 'reward_gold': 1000, 'reward_gems': 100},
    {'id': 'mq-2-2', 'chapter': 2, 'order': 2, 'name': '角色突破',       'description': '突破任意角色1次',                   'goal_type': 'breakthrough',  'goal_target': 1, 'reward_gold': 800,  'reward_gems': 80},
    {'id': 'mq-2-3', 'chapter': 2, 'order': 3, 'name': '挑战名将',       'description': '通关关卡 2-1',                     'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 1000, 'reward_gems': 100, 'goal_param': 'stage-2-1'},
    {'id': 'mq-2-4', 'chapter': 2, 'order': 4, 'name': '通关第二章',     'description': '通关第二章全部关卡',                'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 2000, 'reward_gems': 200, 'goal_param': 'stage-2-3'},
    {'id': 'mq-3-1', 'chapter': 3, 'order': 1, 'name': '角色升至15级',   'description': '将任意角色提升到15级',              'goal_type': 'char_level',    'goal_target': 15, 'reward_gold': 1200, 'reward_gems': 120},
    {'id': 'mq-3-2', 'chapter': 3, 'order': 2, 'name': '挑战传说',       'description': '通关关卡 3-1',                     'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 1500, 'reward_gems': 150, 'goal_param': 'stage-3-1'},
    {'id': 'mq-3-3', 'chapter': 3, 'order': 3, 'name': '通关第三章',     'description': '通关第三章全部关卡',                'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 3000, 'reward_gems': 300, 'goal_param': 'stage-3-3'},
    {'id': 'mq-4-1', 'chapter': 4, 'order': 1, 'name': '角色升至25级',   'description': '将任意角色提升到25级',              'goal_type': 'char_level',    'goal_target': 25, 'reward_gold': 2000, 'reward_gems': 200},
    {'id': 'mq-4-2', 'chapter': 4, 'order': 2, 'name': '暗影降临',       'description': '通关关卡 4-1',                     'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 2000, 'reward_gems': 200, 'goal_param': 'stage-4-1'},
    {'id': 'mq-4-3', 'chapter': 4, 'order': 3, 'name': '通关第四章',     'description': '通关第四章全部关卡',                'goal_type': 'clear_stage',   'goal_target': 1, 'reward_gold': 5000, 'reward_gems': 500, 'goal_param': 'stage-4-3'},
]

# 公告种子数据
DEFAULT_ANNOUNCEMENTS = [
    {'title': '欢迎来到巅峰对决！',        'content': '亲爱的勇者，欢迎加入巅峰对决！\n\n在这里，你将召唤古今中外的传奇英雄，组建你的最强战队。\n\n- 完成新手引导领取丰厚奖励\n- 每日签到获取免费资源\n- 七日目标助你快速成长\n\n祝你游戏愉快！', 'announcement_type': 'normal', 'priority': 10, 'show_on_login': True},
    {'title': '新手福利大放送',            'content': '新玩家专属福利：\n\n🎁 注册即送：金币20000 + 钻石500 + 召唤券10张\n⭐ 首次十连必得史诗英雄\n📋 七日目标累计可领取超过50000金币和3000钻石\n\n快来开启你的英雄之旅吧！', 'announcement_type': 'event', 'priority': 9, 'show_on_login': True},
    {'title': 'UP池：诸葛亮 & 关羽概率提升', 'content': '限时UP池开启！\n\n🌟 传说UP：诸葛亮（水属性法师）\n💜 史诗UP：关羽（火属性战士）\n\nUP角色在对应稀有度中出现概率大幅提升，不要错过！', 'announcement_type': 'event', 'priority': 8, 'show_on_login': True},
    {'title': '游戏更新 v2.1.0',           'content': '本次更新内容：\n\n✅ 新增角色：贞德、成吉思汗、克娄巴特拉等\n✅ 商会系统正式开放\n✅ 竞技场系统上线\n✅ 任务中心全面升级\n✅ 公告与七日目标系统完善\n\n感谢大家的支持！', 'announcement_type': 'update', 'priority': 7, 'show_on_login': False, 'show_on_main': True},
]

# 竞技场机器人
ARENA_BOTS = [
    {'name': '训练假人',       'level': 5,  'character_ids': ['soldier'],                     'rank_score': 800},
    {'name': '新手剑客',       'level': 8,  'character_ids': ['miyamoto'],                    'rank_score': 900},
    {'name': '守城卫兵',       'level': 10, 'character_ids': ['soldier', 'archer'],            'rank_score': 1000},
    {'name': '游荡猎人',       'level': 12, 'character_ids': ['robin-hood', 'archer'],         'rank_score': 1100},
    {'name': '维京掠夺者',     'level': 15, 'character_ids': ['viking-ragnar', 'soldier'],     'rank_score': 1200},
    {'name': '骑士团长',       'level': 18, 'character_ids': ['arthur', 'soldier'],            'rank_score': 1400},
    {'name': '蜀汉先锋',       'level': 20, 'character_ids': ['guan-yu', 'hua-mulan'],        'rank_score': 1600},
    {'name': '暗影将军',       'level': 25, 'character_ids': ['cao-cao', 'miyamoto', 'archer'],'rank_score': 1800},
    {'name': '传说挑战者',     'level': 28, 'character_ids': ['zhuge-liang', 'guan-yu', 'arthur'], 'rank_score': 2000},
    {'name': '巅峰王者',       'level': 30, 'character_ids': ['joan-of-arc', 'genghis-khan', 'zhuge-liang', 'guan-yu'], 'rank_score': 2500},
]

# 新手福利包内容
NEWBIE_PACK = {
    'gold': 20000,
    'gems': 500,
    'summon_tickets': 10,
    'exp_books': 20,
    'energy': 50,
}

# 功能解锁配置 (纯等级解锁，主线任务引导但不阻塞)
FEATURE_UNLOCK = {
    'summon':    {'quest': None, 'level': 1,  'name': '群英馆'},
    'characters':{'quest': None, 'level': 1,  'name': '军营'},
    'stages':    {'quest': None, 'level': 1,  'name': '副本大厅'},
    'shop':      {'quest': None, 'level': 5,  'name': '商会'},
    'research':  {'quest': None, 'level': 10, 'name': '研究所'},
    'arena':     {'quest': None, 'level': 15, 'name': '竞技场'},
}


def get_character_by_id(character_id):
    """根据ID获取角色模板 - 优先从数据库读取"""
    from models import CharacterTemplate
    
    # 尝试从数据库获取
    from flask import has_app_context
    if has_app_context():
        char = CharacterTemplate.query.filter_by(character_id=character_id).first()
        if char:
            return char.to_dict()
    
    # 降级到静态数据
    for char in ALL_CHARACTERS:
        if char['id'] == character_id:
            return char
    return None


def get_characters_by_rarity(rarity):
    """根据稀有度获取角色列表 - 优先从数据库读取"""
    from models import CharacterTemplate
    
    # 尝试从数据库获取
    from flask import has_app_context
    if has_app_context():
        chars = CharacterTemplate.query.filter_by(rarity=rarity).all()
        if chars:
            return [c.to_dict() for c in chars]
    
    # 降级到静态数据
    return [char for char in ALL_CHARACTERS if char['rarity'] == rarity]


def get_all_characters():
    """获取所有角色 - 优先从数据库读取"""
    from models import CharacterTemplate
    
    # 尝试从数据库获取
    from flask import has_app_context
    if has_app_context():
        chars = CharacterTemplate.query.all()
        if chars:
            return [c.to_dict() for c in chars]
    
    # 降级到静态数据
    return ALL_CHARACTERS


def get_stage_by_id(stage_id):
    """根据ID获取关卡配置（搜索所有副本类型）"""
    # 主线副本
    for chapter in CHAPTERS:
        for stage in chapter['stages']:
            if stage['id'] == stage_id:
                stage_copy = dict(stage)
                stage_copy['dungeon_type'] = 'main'
                stage_copy['battle_mode'] = '3v3'
                return stage_copy

    # 日常材料副本
    for dungeon in DAILY_DUNGEONS:
        for level in dungeon['levels']:
            if level['id'] == stage_id:
                level_copy = dict(level)
                level_copy['dungeon_type'] = 'daily'
                level_copy['battle_mode'] = dungeon['battle_mode']
                level_copy['dungeon_name'] = dungeon['name']
                return level_copy

    # 英雄试炼
    for boss in HERO_TRIALS['bosses']:
        if boss['id'] == stage_id:
            boss_copy = dict(boss)
            boss_copy['dungeon_type'] = 'trial'
            boss_copy['battle_mode'] = '1v1'
            boss_copy['enemy_ids'] = [boss['boss_id']]
            boss_copy['enemy_levels'] = [boss['boss_level']]
            boss_copy['dungeon_name'] = HERO_TRIALS['name']
            return boss_copy

    # 高难度副本
    for dungeon in HARD_DUNGEONS:
        for level in dungeon['levels']:
            if level['id'] == stage_id:
                level_copy = dict(level)
                level_copy['dungeon_type'] = 'hard'
                level_copy['battle_mode'] = dungeon['battle_mode']
                level_copy['dungeon_name'] = dungeon['name']
                return level_copy

    return None


def calculate_stats(base_stats, level, stars, breakthrough, rarity=None):
    """计算角色属性（兼容旧接口，新增 rarity 参数）

    Args:
        base_stats: 基础属性字典 或 {'stats': {...}}
        level: 等级
        stars: 星级
        breakthrough: 突破等级
        rarity: 'common'|'rare'|'epic'|'legendary'（可选，传入后使用品质成长体系）
    """
    if rarity:
        return calculate_stats_with_rarity(base_stats, level, stars, breakthrough, rarity)

    if 'stats' in base_stats:
        base_stats = base_stats['stats']

    level_multiplier = 1 + (level - 1) * 0.05
    star_multiplier = 1 + stars * 0.1
    breakthrough_multiplier = 1 + breakthrough * 0.15

    multiplier = level_multiplier * star_multiplier * breakthrough_multiplier

    return {
        'hp': int(base_stats.get('hp', 1000) * multiplier),
        'max_hp': int(base_stats.get('hp', 1000) * multiplier),
        'attack': int(base_stats.get('attack', 100) * multiplier),
        'defense': int(base_stats.get('defense', 50) * multiplier),
        'magic_attack': int(base_stats.get('magic_attack', base_stats.get('attack', 100)) * multiplier),
        'magic_defense': int(base_stats.get('magic_defense', base_stats.get('defense', 50)) * multiplier),
        'speed': int(base_stats.get('speed', 100) * multiplier),
    }


def get_chapter_unlock_status(player_level, completed_stages):
    """获取章节解锁状态
    
    Args:
        player_level: 玩家等级
        completed_stages: 已通关关卡ID列表
        
    Returns:
        dict: {章节ID: {'unlocked': bool, 'reason': str}}
    """
    status = {}
    
    for chapter in CHAPTERS:
        chapter_id = chapter['id']
        required_level = chapter.get('required_level', 1)
        
        # 检查前置章节是否完成
        prev_chapter_completed = True
        if chapter_id != 'chapter-1':
            # 找到前置章节
            prev_chapter_id = None
            for ch in CHAPTERS:
                if ch['id'] == chapter_id:
                    break
                prev_chapter_id = ch['id']
            
            if prev_chapter_id:
                # 检查前置章节的最后一关是否完成
                prev_chapter = get_chapter_by_id(prev_chapter_id)
                if prev_chapter and prev_chapter['stages']:
                    last_stage = prev_chapter['stages'][-1]['id']
                    prev_chapter_completed = last_stage in completed_stages
        
        unlocked = player_level >= required_level and prev_chapter_completed
        
        if not unlocked:
            if player_level < required_level:
                reason = f'需要玩家等级 {required_level} 级'
            elif not prev_chapter_completed:
                reason = '需要通关前置章节'
            else:
                reason = ''
        else:
            reason = ''
        
        status[chapter_id] = {
            'unlocked': unlocked,
            'required_level': required_level,
            'reason': reason
        }
    
    return status


def get_chapter_by_id(chapter_id):
    """根据ID获取章节配置"""
    for chapter in CHAPTERS:
        if chapter['id'] == chapter_id:
            return chapter
    return None


def get_stage_unlock_status(player_level, completed_stages, stage_id):
    """获取关卡解锁状态
    
    Args:
        player_level: 玩家等级
        completed_stages: 已通关关卡ID列表
        stage_id: 关卡ID
        
    Returns:
        dict: {'unlocked': bool, 'reason': str}
    """
    stage = get_stage_by_id(stage_id)
    if not stage:
        return {'unlocked': False, 'reason': '关卡不存在'}
    
    required_level = stage.get('required_level', 1)
    
    # 检查玩家等级
    if player_level < required_level:
        return {'unlocked': False, 'reason': f'需要玩家等级 {required_level} 级'}
    
    # 检查前置关卡（同一章节内的上一关）
    chapter = None
    for ch in CHAPTERS:
        if any(s['id'] == stage_id for s in ch['stages']):
            chapter = ch
            break
    
    if chapter:
        stages = chapter['stages']
        stage_index = next((i for i, s in enumerate(stages) if s['id'] == stage_id), -1)
        
        if stage_index > 0:
            prev_stage_id = stages[stage_index - 1]['id']
            if prev_stage_id not in completed_stages:
                return {'unlocked': False, 'reason': '需要通关前置关卡'}
    
    return {'unlocked': True, 'reason': ''}


def get_level_reward(level):
    """获取等级奖励
    
    Args:
        level: 等级
        
    Returns:
        dict or None: 奖励配置
    """
    return LEVEL_REWARDS.get(level)


def get_starter_character_by_id(character_id):
    """根据ID获取初始角色配置"""
    for char in STARTER_CHARACTERS:
        if char['id'] == character_id:
            return char
    return None
