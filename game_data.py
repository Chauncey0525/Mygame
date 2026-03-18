"""
游戏数据配置
角色、技能、关卡等静态数据
"""

# 稀有度配置
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
                'enemy_ids': ['miyamoto'],
                'enemy_levels': [1],
                'energy_cost': 5,
                'recommended_level': 1,
                'rewards': {'gold': 100, 'exp': 50},
                'first_clear_rewards': {'gold': 500, 'gems': 50}
            },
            {
                'id': 'stage-1-2',
                'name': '遭遇强敌',
                'description': '遭遇敌方斥候，击退他们',
                'difficulty': 'easy',
                'enemy_ids': ['hua-mulan'],
                'enemy_levels': [3],
                'energy_cost': 6,
                'recommended_level': 3,
                'rewards': {'gold': 150, 'exp': 80},
                'first_clear_rewards': {'gold': 600, 'gems': 60}
            },
            {
                'id': 'stage-1-3',
                'name': '首战告捷',
                'description': '击败敌方先锋大将',
                'difficulty': 'normal',
                'enemy_ids': ['cao-cao'],
                'enemy_levels': [5],
                'energy_cost': 8,
                'recommended_level': 5,
                'rewards': {'gold': 200, 'exp': 100},
                'first_clear_rewards': {'gold': 800, 'gems': 80}
            }
        ]
    },
    {
        'id': 'chapter-2',
        'name': '名将云集',
        'description': '各路名将齐聚，展现你的真正实力',
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
                'rewards': {'gold': 500, 'exp': 250, 'gems': 30},
                'first_clear_rewards': {'gold': 1500, 'gems': 150}
            }
        ]
    },
    {
        'id': 'chapter-3',
        'name': '传说之战',
        'description': '传说级英雄的挑战，证明你是真正的英雄',
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
                'rewards': {'gold': 1000, 'exp': 500, 'gems': 100},
                'first_clear_rewards': {'gold': 5000, 'gems': 500}
            }
        ]
    }
    ,
    {
        'id': 'chapter-4',
        'name': '暗潮涌动',
        'description': '暗影势力浮出水面，战场规则开始改变',
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
