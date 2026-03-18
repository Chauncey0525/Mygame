# 游戏数据配置
"""
角色、技能、关卡等静态数据
包含经验值升级系统配置
"""

# ==================== 经验值升级系统配置 ====================

# 等级上限
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
    'hell': '地狱'
}

DIFFICULTY_COLORS = {
    'easy': '#22c55e',
    'normal': '#3b82f6',
    'hard': '#f59e0b',
    'hell': '#ef4444'
}

# 默认每日任务
DEFAULT_DAILY_TASKS = [
    {
        'task_id': 'daily-login',
        'name': '每日签到',
        'description': '登录游戏',
        'target': 1,
        'reward_gold': 500,
        'reward_gems': 50
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
        'reward_gems': 20
    },
    {
        'task_id': 'daily-levelup',
        'name': '强化角色',
        'description': '强化任意角色1次',
        'target': 1,
        'reward_gold': 400,
        'reward_exp': 50
    }
]


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
    """根据ID获取关卡配置"""
    for chapter in CHAPTERS:
        for stage in chapter['stages']:
            if stage['id'] == stage_id:
                return stage
    return None


def calculate_stats(base_stats, level, stars, breakthrough):
    """计算角色属性
    
    Args:
        base_stats: 基础属性字典，支持两种格式：
            - 直接属性字典: {'hp': 800, 'attack': 60, ...}
            - 角色数据字典: {'stats': {'hp': 800, ...}}
        level: 等级
        stars: 星级
        breakthrough: 突破等级
    """
    # 兼容传入完整角色数据的情况
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
