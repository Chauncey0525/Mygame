"""
数据库模型定义
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Player(db.Model, UserMixin):
    """玩家表"""
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(8), unique=True, nullable=True, index=True)  # 8位UID：00000001 起
    
    # 用户认证字段
    username = db.Column(db.String(64), unique=True, nullable=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(32), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(256), nullable=True)
    
    # 玩家信息
    name = db.Column(db.String(128), nullable=False, default='勇者')
    avatar = db.Column(db.String(256), nullable=True, default='/static/images/avatars/avatar_male_01.jpg')
    level = db.Column(db.Integer, nullable=False, default=1)
    exp = db.Column(db.Integer, nullable=False, default=0)
    exp_to_next = db.Column(db.Integer, nullable=False, default=100)
    
    # 资源
    gold = db.Column(db.Integer, nullable=False, default=10000)
    gems = db.Column(db.Integer, nullable=False, default=1000)
    exp_books = db.Column(db.Integer, nullable=False, default=100)
    summon_tickets = db.Column(db.Integer, nullable=False, default=10)
    energy = db.Column(db.Integer, nullable=False, default=100)
    max_energy = db.Column(db.Integer, nullable=False, default=100)
    last_energy_update = db.Column(db.DateTime, default=datetime.now)
    
    # 抽卡保底计数
    pity_count = db.Column(db.Integer, nullable=False, default=0)
    legendary_pity_count = db.Column(db.Integer, nullable=False, default=0)
    
    # 游戏进度
    total_play_days = db.Column(db.Integer, nullable=False, default=1)
    last_login_date = db.Column(db.Date, default=date.today)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    characters = db.relationship('PlayerCharacter', backref='player', lazy='dynamic')
    team = db.relationship('PlayerTeam', backref='player', lazy='dynamic', order_by='PlayerTeam.slot')
    completed_stages = db.relationship('PlayerCompletedStage', backref='player', lazy='dynamic')
    daily_tasks = db.relationship('PlayerDailyTask', backref='player', lazy='dynamic')
    summon_history = db.relationship('SummonHistory', backref='player', lazy='dynamic')
    favorites = db.relationship(
        'PlayerFavoriteCharacter',
        backref='player',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='PlayerFavoriteCharacter.slot',
    )
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'name': self.name,
            'avatar': self.avatar,
            'level': self.level,
            'exp': self.exp,
            'exp_to_next': self.exp_to_next,
            'gold': self.gold,
            'gems': self.gems,
            'exp_books': self.exp_books,
            'summon_tickets': self.summon_tickets,
            'energy': self.energy,
            'max_energy': self.max_energy,
            'pity_count': self.pity_count,
            'legendary_pity_count': self.legendary_pity_count,
            'total_play_days': self.total_play_days,
        }


class SmsVerification(db.Model):
    """短信验证码（开发环境可用；生产建议接入短信服务+独立限流）"""
    __tablename__ = 'sms_verifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(32), nullable=False, index=True)
    code_hash = db.Column(db.String(256), nullable=False)

    purpose = db.Column(db.String(32), nullable=False, default='register', index=True)
    ip = db.Column(db.String(64), nullable=True)

    sent_at = db.Column(db.DateTime, default=datetime.now, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used_at = db.Column(db.DateTime, nullable=True, index=True)

    attempts = db.Column(db.Integer, nullable=False, default=0)

    def set_code(self, code: str):
        self.code_hash = generate_password_hash(code)

    def check_code(self, code: str) -> bool:
        return check_password_hash(self.code_hash, code)


class PlayerCharacter(db.Model):
    """玩家角色表"""
    __tablename__ = 'player_characters'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    character_id = db.Column(db.String(64), nullable=False)
    
    # 养成数据
    level = db.Column(db.Integer, nullable=False, default=1)
    exp = db.Column(db.Integer, nullable=False, default=0)
    stars = db.Column(db.Integer, nullable=False, default=1)
    breakthrough = db.Column(db.Integer, nullable=False, default=0)
    
    # 羁绊
    bond_level = db.Column(db.Integer, nullable=False, default=1)
    bond_exp = db.Column(db.Integer, nullable=False, default=0)
    
    obtained_at = db.Column(db.DateTime, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.Index('idx_player_character', 'player_id', 'character_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'character_id': self.character_id,
            'level': self.level,
            'exp': self.exp,
            'stars': self.stars,
            'breakthrough': self.breakthrough,
            'bond_level': self.bond_level,
        }


class PlayerFavoriteCharacter(db.Model):
    """玩家常用/收藏角色（可为空，最多 6 个）"""
    __tablename__ = 'player_favorite_characters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False, index=True)
    character_instance_id = db.Column(db.Integer, db.ForeignKey('player_characters.id'), nullable=False, index=True)
    slot = db.Column(db.Integer, nullable=False, default=1)  # 1-6
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint('player_id', 'character_instance_id', name='uix_fav_player_instance'),
        db.UniqueConstraint('player_id', 'slot', name='uix_fav_player_slot'),
        db.Index('idx_fav_player', 'player_id'),
    )


class PlayerTeam(db.Model):
    """玩家队伍配置表"""
    __tablename__ = 'player_team'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    slot = db.Column(db.Integer, nullable=False)  # 队伍位置 0-3
    character_instance_id = db.Column(db.Integer, db.ForeignKey('player_characters.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.Index('idx_player_team', 'player_id'),
    )


class PlayerCompletedStage(db.Model):
    """已通关关卡表"""
    __tablename__ = 'player_completed_stages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    stage_id = db.Column(db.String(64), nullable=False)
    stars = db.Column(db.Integer, default=1)  # 关卡星级 1-3
    completed_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.Index('idx_player_stages', 'player_id'),
        db.UniqueConstraint('player_id', 'stage_id', name='uix_player_stage'),
    )


class PlayerDailyTask(db.Model):
    """每日任务表"""
    __tablename__ = 'player_daily_tasks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    task_id = db.Column(db.String(64), nullable=False)
    
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target = db.Column(db.Integer, nullable=False, default=1)
    progress = db.Column(db.Integer, nullable=False, default=0)
    
    # 奖励
    reward_gold = db.Column(db.Integer, default=0)
    reward_gems = db.Column(db.Integer, default=0)
    reward_exp = db.Column(db.Integer, default=0)
    
    completed = db.Column(db.Boolean, nullable=False, default=False)
    claimed = db.Column(db.Boolean, nullable=False, default=False)
    
    task_date = db.Column(db.Date, nullable=False, default=date.today)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.Index('idx_daily_tasks', 'player_id', 'task_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.task_id,
            'name': self.name,
            'description': self.description,
            'target': self.target,
            'progress': self.progress,
            'rewards': {
                'gold': self.reward_gold or 0,
                'gems': self.reward_gems or 0,
                'exp': self.reward_exp or 0,
            },
            'completed': self.completed,
            'claimed': self.claimed,
        }


class SummonHistory(db.Model):
    """抽卡历史记录表"""
    __tablename__ = 'summon_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    character_id = db.Column(db.String(64), nullable=False)
    rarity = db.Column(db.String(16), nullable=False)
    
    summoned_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.Index('idx_summon_history', 'player_id'),
    )


class CharacterTemplate(db.Model):
    """角色模板表 - 存储所有英雄的基础数据"""
    __tablename__ = 'character_templates'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    character_id = db.Column(db.String(64), unique=True, nullable=False, index=True)  # 唯一标识
    
    # 基本信息
    name = db.Column(db.String(64), nullable=False)
    name_en = db.Column(db.String(64), nullable=True)
    title = db.Column(db.String(64), nullable=True)
    era = db.Column(db.String(32), nullable=True)
    origin = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # 属性配置
    element = db.Column(db.String(16), nullable=False, default='fire')
    role_type = db.Column(db.String(16), nullable=False, default='warrior')
    rarity = db.Column(db.String(16), nullable=False, default='common')
    
    # 资源路径
    avatar = db.Column(db.String(256), nullable=True)
    illustration = db.Column(db.String(256), nullable=True)
    
    # 基础属性
    base_hp = db.Column(db.Integer, nullable=False, default=1000)
    base_attack = db.Column(db.Integer, nullable=False, default=100)
    base_defense = db.Column(db.Integer, nullable=False, default=50)
    base_magic_attack = db.Column(db.Integer, nullable=False, default=100)
    base_magic_defense = db.Column(db.Integer, nullable=False, default=50)
    base_speed = db.Column(db.Integer, nullable=False, default=100)
    
    # 技能数据 (JSON格式存储)
    skills = db.Column(db.Text, nullable=True)  # JSON字符串
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        import json
        return {
            'id': self.character_id,
            'name': self.name,
            'name_en': self.name_en,
            'title': self.title,
            'era': self.era,
            'origin': self.origin,
            'description': self.description,
            'element': self.element,
            'role_type': self.role_type,
            'rarity': self.rarity,
            'avatar': self.avatar,
            'illustration': self.illustration,
            'stats': {
                'hp': self.base_hp,
                'attack': self.base_attack,
                'defense': self.base_defense,
                'magic_attack': self.base_magic_attack,
                'magic_defense': self.base_magic_defense,
                'speed': self.base_speed,
            },
            'skills': json.loads(self.skills) if self.skills else [],
        }
    
    @staticmethod
    def from_dict(data):
        """从字典创建角色模板"""
        import json
        return CharacterTemplate(
            character_id=data['id'],
            name=data['name'],
            name_en=data.get('name_en'),
            title=data.get('title'),
            era=data.get('era'),
            origin=data.get('origin'),
            description=data.get('description'),
            element=data.get('element', 'fire'),
            role_type=data.get('role_type', 'warrior'),
            rarity=data.get('rarity', 'common'),
            avatar=data.get('avatar'),
            illustration=data.get('illustration'),
            base_hp=data['stats'].get('hp', 1000),
            base_attack=data['stats'].get('attack', 100),
            base_defense=data['stats'].get('defense', 50),
            base_magic_attack=data['stats'].get('magic_attack', 100),
            base_magic_defense=data['stats'].get('magic_defense', 50),
            base_speed=data['stats'].get('speed', 100),
            skills=json.dumps(data.get('skills', []), ensure_ascii=False),
        )


class Announcement(db.Model):
    """公告表"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    announcement_type = db.Column(db.String(32), default='normal')  # normal, event, maintenance, update
    priority = db.Column(db.Integer, default=0)  # 优先级，数字越大越靠前
    
    # 显示时间范围
    start_time = db.Column(db.DateTime, default=datetime.now)
    end_time = db.Column(db.DateTime, nullable=True)
    
    # 显示配置
    show_on_login = db.Column(db.Boolean, default=True)  # 登录时显示
    show_on_main = db.Column(db.Boolean, default=True)  # 主界面显示
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.announcement_type,
            'priority': self.priority,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'show_on_login': self.show_on_login,
            'show_on_main': self.show_on_main,
        }


class SevenDayGoal(db.Model):
    """七日目标表"""
    __tablename__ = 'seven_day_goals'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    day = db.Column(db.Integer, nullable=False)  # 第几天 (1-7)
    goal_id = db.Column(db.String(64), nullable=False)  # 目标ID
    
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target = db.Column(db.Integer, nullable=False, default=1)
    progress = db.Column(db.Integer, nullable=False, default=0)
    
    # 奖励
    reward_gold = db.Column(db.Integer, default=0)
    reward_gems = db.Column(db.Integer, default=0)
    reward_items = db.Column(db.Text, nullable=True)  # JSON格式道具奖励
    
    completed = db.Column(db.Boolean, nullable=False, default=False)
    claimed = db.Column(db.Boolean, nullable=False, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        db.Index('idx_seven_day_goals', 'player_id', 'day'),
    )
    
    def to_dict(self):
        import json
        return {
            'id': self.goal_id,
            'day': self.day,
            'name': self.name,
            'description': self.description,
            'target': self.target,
            'progress': self.progress,
            'rewards': {
                'gold': self.reward_gold or 0,
                'gems': self.reward_gems or 0,
                'items': json.loads(self.reward_items) if self.reward_items else [],
            },
            'completed': self.completed,
            'claimed': self.claimed,
        }
