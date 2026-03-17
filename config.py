"""
Flask 应用配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'history-heroes-secret-key-2024')
    
    # MySQL 数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'history_heroes')
    
    # 优先使用 DATABASE_URL，否则使用 MySQL 配置，最后回退到 SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif MYSQL_PASSWORD:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    else:
        # 回退到 SQLite（用于开发/测试）
        SQLALCHEMY_DATABASE_URI = 'sqlite:///history_heroes.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # 游戏配置
    MAX_TEAM_SIZE = 4
    MAX_ENERGY = 100
    ENERGY_RECOVERY_RATE = 10  # 每小时恢复
    PITY_EPIC = 50  # 史诗保底
    PITY_LEGENDARY = 100  # 传说保底


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
