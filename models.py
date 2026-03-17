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
    
    # 用户认证字段
    username = db.Column(db.String(64), unique=True, nullable=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(256), nullable=True)
    
    # 玩家信息
    name = db.Column(db.String(128), nullable=False, default='勇者')
    level = db.Column(db.Integer, nullable=False, default=1)
    exp = db.Column(db.Integer, nullable=False, default=0)
    exp_to_next = db.Column(db.Integer, nullable=False, default=100)
    
    # 资源
    gold = db.Column(db.Integer, nullable=False, default=10000)
    gems = db.Column(db.Integer, nullable=False, default=1000)
    exp_books = db.Column(db.Integer, nullable=False, default=0)
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
            'name': self.name,
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
