"""
巅峰对决 - Flask 主应用
"""
import os
import re
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
from sqlalchemy import text

from config import config
from models import (
    db,
    Player,
    PlayerCharacter,
    PlayerTeam,
    PlayerCompletedStage,
    PlayerDailyTask,
    SummonHistory,
    SmsVerification,
    CharacterTemplate,
    PlayerFavoriteCharacter,
    Announcement,
    SevenDayGoal,
    PlayerEquipment,
    PlayerRune,
    PlayerTalent,
    PlayerMainQuest,
    ShopPurchase,
    ArenaRecord,
    SkillTemplate,
    CharacterEquippedSkill,
)
from game_data import (
    CHAPTERS, RARITY_NAMES, RARITY_COLORS, RARITY_WEIGHTS,
    ELEMENT_NAMES, ELEMENT_COLORS, ROLE_NAMES, DIFFICULTY_NAMES, DIFFICULTY_COLORS,
    DEFAULT_DAILY_TASKS, get_character_by_id, get_characters_by_rarity,
    get_all_characters, get_stage_by_id, calculate_stats,
    CURRENT_UP_CHARACTERS, UP_RATE_MULTIPLIER,
    get_exp_to_next_level, get_total_exp_to_level, get_level_from_exp,
    get_chapter_unlock_status, get_stage_unlock_status, get_level_reward,
    get_chapter_by_id, get_starter_character_by_id,
    STARTER_CHARACTERS, DEFAULT_STARTER_CHARACTER, MAX_PLAYER_LEVEL, LEVEL_REWARDS,
    SHOP_ITEMS, MAIN_QUESTS, DEFAULT_ANNOUNCEMENTS, ARENA_BOTS, NEWBIE_PACK,
    FEATURE_UNLOCK, DEFAULT_SEVEN_DAY_GOALS,
    BATTLE_MODES, BATTLE_ITEMS, DAILY_DUNGEONS, HERO_TRIALS, HARD_DUNGEONS,
    get_skills_for_character,
    get_skill_unlock_preview,
    get_skill_icon, SKILL_TYPE_ICONS,
)

# ==================== 账号工具 ====================

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^\+?\d{7,20}$")
# 密码规则：至少8位，至少1个字母+1个数字，可包含常见特殊字符
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&._-]{8,64}$")


def normalize_phone(raw: str) -> str:
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    s = re.sub(r"[\s\-()]", "", s)
    if s.startswith("00"):
        s = "+" + s[2:]
    return s


def is_valid_email(email: str) -> bool:
    if not email:
        return True
    return EMAIL_RE.match(email) is not None


def is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    # 兼容国内 11 位与 E.164（宽松）
    if phone.startswith("+"):
        return PHONE_RE.match(phone) is not None
    return phone.isdigit() and 7 <= len(phone) <= 20


def is_valid_password(pw: str) -> bool:
    if not pw:
        return False
    return PASSWORD_RE.match(pw) is not None


def get_client_ip() -> str:
    # 简单获取；生产环境请在反向代理层正确传递 X-Forwarded-For 并做信任链校验
    return request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr or ""


def gen_sms_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def send_sms_dev(phone: str, code: str) -> None:
    # 开发模式：不真正发短信，只在控制台打印验证码
    print(f"[DEV SMS] phone={phone} code={code}")


def allocate_next_uid() -> str:
    """
    分配下一个 8 位 UID（00000001 起）。
    说明：SQLite 在高并发下仍可能竞争；当前项目为单机/开发用途，已足够。
    """
    # max(uid) 在字符串上可能不可靠，这里转 int 再取最大
    existing = db.session.execute(text("SELECT uid FROM players WHERE uid IS NOT NULL AND uid != ''")).fetchall()
    max_n = 0
    for (u,) in existing:
        try:
            max_n = max(max_n, int(str(u)))
        except Exception:
            continue
    return f"{max_n + 1:08d}"


from typing import Optional


def _favorite_slots_used(player: Player) -> set:
    return set([f.slot for f in player.favorites.all() if f.slot is not None])


def _next_favorite_slot(player: Player, max_slots: int = 6) -> Optional[int]:
    used = _favorite_slots_used(player)
    for s in range(1, max_slots + 1):
        if s not in used:
            return s
    return None


def ensure_db_migrations():
    """
    轻量迁移（避免引入 Alembic）：
    - 为 players 增加 phone 列（如不存在）
    - 为 players 增加 uid 列（如不存在），并回填旧数据（00000001 起）
    - 为 players 增加 avatar 列（如不存在），并回填默认头像
    - 为 player_completed_stages 增加 stars 列（如不存在）
    - 创建 sms_verifications 等表（由 create_all 处理）
    """
    try:
        with app.app_context():
            db.create_all()
            engine = db.engine
            dialect = engine.dialect.name

            if dialect == "sqlite":
                cols = [row[1] for row in db.session.execute(text("PRAGMA table_info(players)")).fetchall()]
                if "phone" not in cols:
                    db.session.execute(text("ALTER TABLE players ADD COLUMN phone VARCHAR(32)"))
                    db.session.commit()
                # SQLite 的 ALTER TABLE 不支持直接加 UNIQUE，这里用索引兜底
                db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uix_players_phone ON players(phone)"))
                db.session.commit()

                if "uid" not in cols:
                    db.session.execute(text("ALTER TABLE players ADD COLUMN uid VARCHAR(8)"))
                    db.session.commit()
                db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uix_players_uid ON players(uid)"))
                db.session.commit()
                # 回填旧数据：按 id 从 00000001 递增
                rows = db.session.execute(text("SELECT id, uid FROM players ORDER BY id ASC")).fetchall()
                next_n = 1
                for pid, puid in rows:
                    if puid and str(puid).strip():
                        try:
                            next_n = max(next_n, int(str(puid)) + 1)
                        except Exception:
                            pass
                for pid, puid in rows:
                    if not puid or not str(puid).strip():
                        db.session.execute(
                            text("UPDATE players SET uid = :uid WHERE id = :id"),
                            {"uid": f"{next_n:08d}", "id": pid},
                        )
                        next_n += 1
                db.session.commit()

                # players.avatar（头像）
                if "avatar" not in cols:
                    db.session.execute(text("ALTER TABLE players ADD COLUMN avatar VARCHAR(256)"))
                    db.session.commit()
                db.session.execute(
                    text(
                        "UPDATE players SET avatar = :a "
                        "WHERE (avatar IS NULL OR avatar = '')"
                    ),
                    {"a": "/static/images/avatars/avatar_male_01.jpg"},
                )
                db.session.commit()

                # player_completed_stages.stars（关卡星级）
                stage_cols = [row[1] for row in db.session.execute(text("PRAGMA table_info(player_completed_stages)")).fetchall()]
                if "stars" not in stage_cols:
                    db.session.execute(text("ALTER TABLE player_completed_stages ADD COLUMN stars INTEGER DEFAULT 1"))
                    db.session.commit()

                # players.star_soul（历史字段，已弃用：旧版升星材料）
                # 旧库可能存在该字段；新版星魂体系改为“角色独立魂力”，这里不再强制新增

                # 新增字段：新手引导/统计/竞技场/突破石
                cols = [row[1] for row in db.session.execute(text("PRAGMA table_info(players)")).fetchall()]
                new_player_cols = {
                    'tutorial_step': 'INTEGER DEFAULT 0',
                    'newbie_pack_claimed': 'BOOLEAN DEFAULT 0',
                    'total_summon_count': 'INTEGER DEFAULT 0',
                    'total_battle_count': 'INTEGER DEFAULT 0',
                    'arena_score': 'INTEGER DEFAULT 1000',
                    'arena_wins': 'INTEGER DEFAULT 0',
                    'arena_losses': 'INTEGER DEFAULT 0',
                    'breakthrough_stone': 'INTEGER DEFAULT 0',
                }
                for col_name, col_def in new_player_cols.items():
                    if col_name not in cols:
                        db.session.execute(text(f"ALTER TABLE players ADD COLUMN {col_name} {col_def}"))
                        db.session.commit()

                # player_characters.equipped_skills（技能装备栏）
                pc_cols = [row[1] for row in db.session.execute(text("PRAGMA table_info(player_characters)")).fetchall()]
                if "equipped_skills" not in pc_cols:
                    db.session.execute(text("ALTER TABLE player_characters ADD COLUMN equipped_skills TEXT"))

                # player_characters.soul_power（角色独立魂力）
                if "soul_power" not in pc_cols:
                    db.session.execute(text("ALTER TABLE player_characters ADD COLUMN soul_power INTEGER DEFAULT 0"))
                    db.session.commit()

                # 为所有玩家关联表添加 player_uid 冗余字段，用于数据统计
                uid_tables = [
                    'player_characters', 'player_favorite_characters', 'player_team',
                    'player_completed_stages', 'player_daily_tasks', 'player_equipment',
                    'player_runes', 'player_talents', 'summon_history',
                    'seven_day_goals', 'player_main_quests', 'shop_purchases', 'arena_records',
                ]
                for tbl in uid_tables:
                    try:
                        tcols = [r[1] for r in db.session.execute(text(f"PRAGMA table_info({tbl})")).fetchall()]
                    except Exception:
                        continue
                    if 'player_uid' not in tcols:
                        db.session.execute(text(f"ALTER TABLE {tbl} ADD COLUMN player_uid VARCHAR(8)"))
                        db.session.commit()
                    db.session.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{tbl}_player_uid ON {tbl}(player_uid)"))
                    db.session.commit()
                    db.session.execute(text(
                        f"UPDATE {tbl} SET player_uid = ("
                        f"  SELECT p.uid FROM players p WHERE p.id = {tbl}.player_id"
                        f") WHERE player_uid IS NULL OR player_uid = ''"
                    ))
                    db.session.commit()

            elif dialect in ("mysql", "mariadb"):
                # MySQL 简易检查列是否存在
                row = db.session.execute(text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='players' AND COLUMN_NAME='phone'"
                )).scalar()
                if int(row or 0) == 0:
                    db.session.execute(text("ALTER TABLE players ADD COLUMN phone VARCHAR(32) NULL"))
                    db.session.execute(text("CREATE UNIQUE INDEX uix_players_phone ON players(phone)"))
                    db.session.commit()

                row = db.session.execute(text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='players' AND COLUMN_NAME='uid'"
                )).scalar()
                if int(row or 0) == 0:
                    db.session.execute(text("ALTER TABLE players ADD COLUMN uid VARCHAR(8) NULL"))
                    db.session.commit()
                # 唯一索引（如已存在会报错，这里用 TRY 方式；MySQL 需要显式判断）
                idx = db.session.execute(text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='players' AND INDEX_NAME='uix_players_uid'"
                )).scalar()
                if int(idx or 0) == 0:
                    db.session.execute(text("CREATE UNIQUE INDEX uix_players_uid ON players(uid)"))
                    db.session.commit()
                # 回填（按 id）
                rows = db.session.execute(text("SELECT id, uid FROM players ORDER BY id ASC")).fetchall()
                next_n = 1
                for pid, puid in rows:
                    if puid and str(puid).strip():
                        try:
                            next_n = max(next_n, int(str(puid)) + 1)
                        except Exception:
                            pass
                for pid, puid in rows:
                    if not puid or not str(puid).strip():
                        db.session.execute(text("UPDATE players SET uid=%s WHERE id=%s"), (f"{next_n:08d}", pid))
                        next_n += 1
                db.session.commit()
                # players.star_soul（历史字段，已弃用：旧版升星材料）
                # 旧库可能存在该字段；新版星魂体系改为“角色独立魂力”，这里不再强制新增

                row = db.session.execute(text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='players' AND COLUMN_NAME='avatar'"
                )).scalar()
                if int(row or 0) == 0:
                    db.session.execute(text("ALTER TABLE players ADD COLUMN avatar VARCHAR(256) NULL"))
                    db.session.commit()
                db.session.execute(text(
                    "UPDATE players SET avatar=%s WHERE avatar IS NULL OR avatar=''"
                ), ("/static/images/avatars/avatar_male_01.jpg",))
                db.session.commit()
                row = db.session.execute(text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='player_completed_stages' AND COLUMN_NAME='stars'"
                )).scalar()
                if int(row or 0) == 0:
                    db.session.execute(text("ALTER TABLE player_completed_stages ADD COLUMN stars INT DEFAULT 1"))
                    db.session.commit()

                new_player_cols_mysql = {
                    'tutorial_step': 'INT NOT NULL DEFAULT 0',
                    'newbie_pack_claimed': 'TINYINT(1) NOT NULL DEFAULT 0',
                    'total_summon_count': 'INT NOT NULL DEFAULT 0',
                    'total_battle_count': 'INT NOT NULL DEFAULT 0',
                    'arena_score': 'INT NOT NULL DEFAULT 1000',
                    'arena_wins': 'INT NOT NULL DEFAULT 0',
                    'arena_losses': 'INT NOT NULL DEFAULT 0',
                    'breakthrough_stone': 'INT NOT NULL DEFAULT 0',
                }
                for col_name, col_def in new_player_cols_mysql.items():
                    cnt = db.session.execute(text(
                        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='players' AND COLUMN_NAME=:c"
                    ), {'c': col_name}).scalar()
                    if int(cnt or 0) == 0:
                        db.session.execute(text(f"ALTER TABLE players ADD COLUMN {col_name} {col_def}"))
                        db.session.commit()

                uid_tables_mysql = [
                    'player_characters', 'player_favorite_characters', 'player_team',
                    'player_completed_stages', 'player_daily_tasks', 'player_equipment',
                    'player_runes', 'player_talents', 'summon_history',
                    'seven_day_goals', 'player_main_quests', 'shop_purchases', 'arena_records',
                ]
                for tbl in uid_tables_mysql:
                    cnt = db.session.execute(text(
                        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME=:t AND COLUMN_NAME='player_uid'"
                    ), {'t': tbl}).scalar()
                    if int(cnt or 0) == 0:
                        db.session.execute(text(f"ALTER TABLE {tbl} ADD COLUMN player_uid VARCHAR(8) NULL"))
                        db.session.commit()
                    idx_cnt = db.session.execute(text(
                        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS "
                        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME=:t AND INDEX_NAME=:idx"
                    ), {'t': tbl, 'idx': f'idx_{tbl}_player_uid'}).scalar()
                    if int(idx_cnt or 0) == 0:
                        db.session.execute(text(f"CREATE INDEX idx_{tbl}_player_uid ON {tbl}(player_uid)"))
                        db.session.commit()
                    db.session.execute(text(
                        f"UPDATE {tbl} t INNER JOIN players p ON t.player_id = p.id "
                        f"SET t.player_uid = p.uid WHERE t.player_uid IS NULL OR t.player_uid = ''"
                    ))
                    db.session.commit()

        # wind -> flying 元素迁移
        try:
            db.session.execute(text(
                "UPDATE character_templates SET element='flying' WHERE element='wind'"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

    except Exception as e:
        print("[WARN] ensure_db_migrations failed:", type(e).__name__, str(e))


def seed_announcements():
    """如果公告表为空，插入默认公告（需在 app_context 内调用）"""
    try:
        if Announcement.query.count() == 0:
            now = datetime.now()
            for a_data in DEFAULT_ANNOUNCEMENTS:
                ann = Announcement(
                    title=a_data['title'],
                    content=a_data['content'],
                    announcement_type=a_data.get('announcement_type', 'normal'),
                    priority=a_data.get('priority', 0),
                    show_on_login=a_data.get('show_on_login', True),
                    show_on_main=a_data.get('show_on_main', True),
                    start_time=now,
                    is_active=True,
                )
                db.session.add(ann)
            db.session.commit()
    except Exception as e:
        print("[WARN] seed_announcements failed:", type(e).__name__, str(e))


def create_main_quests(player):
    """为玩家初始化主线任务进度"""
    for q in MAIN_QUESTS:
        existing = PlayerMainQuest.query.filter_by(player_id=player.id, quest_id=q['id']).first()
        if not existing:
            mq = PlayerMainQuest(player_id=player.id, player_uid=player.uid, quest_id=q['id'], progress=0)
            db.session.add(mq)
    db.session.commit()


def _ensure_seven_day_goals(player: Player):
    try:
        cnt = SevenDayGoal.query.filter_by(player_id=player.id).count()
        if cnt == 0:
            create_seven_day_goals(player)
    except Exception:
        # 不阻塞主流程
        pass


def _update_goal_progress(player: Player, goal_id: str, delta: int = 1, absolute: Optional[int] = None):
    """
    七日目标进度：既支持累加，也支持按绝对值写入（例如拥有角色数/通关关卡数）。
    """
    try:
        g = SevenDayGoal.query.filter_by(player_id=player.id, goal_id=goal_id).first()
        if not g:
            return
        if absolute is not None:
            g.progress = max(g.progress or 0, int(absolute))
        else:
            g.progress = int(g.progress or 0) + int(delta or 0)
        if g.progress >= g.target:
            g.completed = True
        db.session.commit()
    except Exception:
        db.session.rollback()


def _sync_seven_day_by_event(player: Player, event: str, payload: Optional[dict] = None):
    """
    用最小实现把关键事件映射到七日目标：
    - login, summon(count,new_char), battle(victory,stage_completed_total), levelup, team_set, breakthrough
    """
    payload = payload or {}
    _ensure_seven_day_goals(player)

    try:
        if event == 'login':
            _update_goal_progress(player, 'day1-login', absolute=1)

        elif event == 'summon':
            count = int(payload.get('count') or 1)
            for gid in ('day1-summon', 'day3-summon5', 'day5-summon10'):
                _update_goal_progress(player, gid, delta=count)
            owned = PlayerCharacter.query.filter_by(player_id=player.id).count()
            _update_goal_progress(player, 'day3-char3', absolute=owned)
            _update_goal_progress(player, 'day5-char5', absolute=owned)
            _update_goal_progress(player, 'day7-char8', absolute=owned)

        elif event == 'battle':
            if payload.get('victory'):
                _update_goal_progress(player, 'day1-battle', delta=1)
                _update_goal_progress(player, 'day2-battle3', delta=1)
                _update_goal_progress(player, 'day4-battle10', delta=1)
                cleared = PlayerCompletedStage.query.filter_by(player_id=player.id).count()
                _update_goal_progress(player, 'day3-stage5', absolute=cleared)
                _update_goal_progress(player, 'day6-stage20', absolute=cleared)

        elif event == 'levelup':
            _update_goal_progress(player, 'day2-levelup', delta=1)

        elif event == 'team_set':
            _update_goal_progress(player, 'day2-team', absolute=1)

        elif event == 'breakthrough':
            _update_goal_progress(player, 'day4-breakthrough', delta=1)

        # Sync counters from player stats across all events
        _update_goal_progress(player, 'day7-battle30', absolute=player.total_battle_count or 0)
        _update_goal_progress(player, 'day4-battle10', absolute=player.total_battle_count or 0)
        _update_goal_progress(player, 'day1-summon', absolute=player.total_summon_count or 0)
        _update_goal_progress(player, 'day3-summon5', absolute=player.total_summon_count or 0)
        _update_goal_progress(player, 'day5-summon10', absolute=player.total_summon_count or 0)

        max_lvl_row = db.session.execute(
            text("SELECT MAX(level) FROM player_characters WHERE player_id = :pid"),
            {'pid': player.id}
        ).scalar()
        max_lvl = int(max_lvl_row or 0)
        if max_lvl >= 10:
            _update_goal_progress(player, 'day4-level10', absolute=max_lvl)
        if max_lvl >= 20:
            _update_goal_progress(player, 'day6-level20', absolute=max_lvl)

        if PlayerCompletedStage.query.filter_by(player_id=player.id, stage_id='stage-2-3').first():
            _update_goal_progress(player, 'day5-chapter2', absolute=1)
        if PlayerCompletedStage.query.filter_by(player_id=player.id, stage_id='stage-3-3').first():
            _update_goal_progress(player, 'day7-chapter3', absolute=1)

        epic_chars = db.session.execute(
            text("SELECT character_id FROM player_characters WHERE player_id = :pid"),
            {'pid': player.id}
        ).fetchall()
        for (cid,) in epic_chars:
            tpl = get_character_by_id(cid)
            if tpl and tpl.get('rarity') in ('epic', 'legendary'):
                _update_goal_progress(player, 'day6-epic', absolute=1)
                break

        owned_cnt = PlayerCharacter.query.filter_by(player_id=player.id).count()
        _update_goal_progress(player, 'day7-char8', absolute=owned_cnt)

    except Exception:
        db.session.rollback()


# 创建应用
app = Flask(__name__)
app.config.from_object(config['default'])

# 初始化数据库
db.init_app(app)

# 初始化登录管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.session_protection = 'strong'


@login_manager.unauthorized_handler
def unauthorized_api():
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': '请先登录'}), 401
    return redirect(url_for('login', next=request.url))


@login_manager.user_loader
def load_user(player_id):
    return Player.query.get(int(player_id))


@app.context_processor
def inject_template_globals():
    """让 base.html 等模板在所有页面都能拿到 player 和 rarity_colors，避免登录/注册页报错"""
    from game_data import RARITY_COLORS
    return {
        'rarity_colors': RARITY_COLORS,
        'player': current_user if current_user.is_authenticated else None,
        'get_character_by_id': get_character_by_id,
    }


# ==================== 错误处理（便于排查“打不开”） ====================

@app.errorhandler(500)
def handle_500(e):
    """500 时在 debug 下打印并返回简单错误页"""
    import traceback
    traceback.print_exc()
    if app.debug:
        return f'<h1>服务器错误</h1><pre>{traceback.format_exc()}</pre>', 500
    return '<h1>服务器错误</h1><p>请稍后重试。</p>', 500


@app.errorhandler(Exception)
def handle_exception(e):
    """未捕获异常时打印并返回 500（HTTPException 如 404 不处理，交给 Flask）"""
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    import traceback
    traceback.print_exc()
    if app.debug:
        return f'<h1>异常</h1><pre>{traceback.format_exc()}</pre>', 500
    return '<h1>服务器错误</h1><p>请稍后重试。</p>', 500


# ==================== 认证路由 ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        # 支持用户名或邮箱登录
        player = Player.query.filter(
            (Player.username == username) | (Player.email == username)
        ).first()
        
        if player and player.check_password(password):
            # 登录用户，设置记住我
            login_user(player, remember=True)
            db.session.commit()
            
            # 更新登录信息
            check_daily_reset(player)
            _sync_seven_day_by_event(player, 'login')
            
            # 跳转到之前访问的页面
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = normalize_phone(request.form.get('phone', '').strip())
        sms_code = request.form.get('sms_code', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        player_name = request.form.get('player_name', '勇者').strip()
        avatar = request.form.get('avatar', '/static/images/avatars/avatar_male_01.jpg').strip()
        
        # 验证输入
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('register.html')
        
        if len(username) < 3 or len(username) > 20:
            flash('用户名长度应在3-20个字符之间', 'error')
            return render_template('register.html')
        
        if not is_valid_password(password):
            flash('密码至少8位，且必须包含字母与数字（可含@$!%*?&._-）', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')

        # 邮箱：可选，但必须是合法格式
        if email and not is_valid_email(email):
            flash('邮箱格式不正确', 'error')
            return render_template('register.html')

        # 手机号：必填 + 必须验证码通过
        if not phone:
            flash('手机号不能为空', 'error')
            return render_template('register.html')
        if not is_valid_phone(phone):
            flash('手机号格式不正确', 'error')
            return render_template('register.html')
        if not sms_code or not sms_code.isdigit() or len(sms_code) != 6:
            flash('请输入6位短信验证码', 'error')
            return render_template('register.html')

        # 校验验证码：10 分钟有效，最多 5 次尝试
        now = datetime.now()
        v = (
            SmsVerification.query.filter_by(phone=phone, purpose='register', used_at=None)
            .order_by(SmsVerification.sent_at.desc())
            .first()
        )
        if not v:
            flash('请先获取短信验证码', 'error')
            return render_template('register.html')
        if v.expires_at < now:
            flash('短信验证码已过期，请重新获取', 'error')
            return render_template('register.html')
        if v.attempts >= 5:
            flash('验证码尝试次数过多，请重新获取', 'error')
            return render_template('register.html')

        v.attempts += 1
        ok = v.check_code(sms_code)
        if not ok:
            db.session.commit()
            flash('短信验证码不正确', 'error')
            return render_template('register.html')
        v.used_at = now
        db.session.commit()
        
        # 检查用户名是否已存在
        if Player.query.filter_by(username=username).first():
            flash('用户名已被使用', 'error')
            return render_template('register.html')
        
        # 检查邮箱是否已存在
        if email and Player.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html')

        # 检查手机号是否已存在（手机号唯一，一个手机号一个账号）
        if Player.query.filter_by(phone=phone).first():
            flash('手机号已被注册', 'error')
            return render_template('register.html')
        
        # 创建新玩家
        player = Player(
            username=username,
            email=email if email else None,
            phone=phone,
            name=player_name if player_name else username,
            uid=allocate_next_uid(),
            avatar=avatar,
        )
        player.set_password(password)
        
        db.session.add(player)
        db.session.commit()
        
        # 创建每日任务
        create_daily_tasks(player)
        # 创建主线任务
        create_main_quests(player)
        # 创建七日目标并计入首次登录
        _sync_seven_day_by_event(player, 'login')

        # 新手装备
        seed_starter_equipment(player)
        # 新手符文
        seed_starter_research(player)
        # 新手初始角色
        seed_starter_character(player)
        
        # 自动登录
        login_user(player)
        
        return redirect(url_for('index'))
    
    return render_template('register.html')


@app.route('/api/auth/sms/send', methods=['POST'])
def api_auth_sms_send():
    """
    发送注册短信验证码（开发版：控制台打印验证码）。
    请求 JSON: { "phone": "..." }
    """
    data = request.get_json(silent=True) or {}
    phone = normalize_phone((data.get('phone') or '').strip())
    if not phone or not is_valid_phone(phone):
        return jsonify({'success': False, 'error': '手机号格式不正确'}), 400

    # 已注册的手机号不再发送
    if Player.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'error': '手机号已被注册'}), 400

    ip = get_client_ip()
    now = datetime.now()

    # 简易限流：同手机号 60 秒内不重复发；同 IP 10 分钟内最多 8 次
    last = (
        SmsVerification.query.filter_by(phone=phone, purpose='register')
        .order_by(SmsVerification.sent_at.desc())
        .first()
    )
    if last and (now - last.sent_at).total_seconds() < 60:
        return jsonify({'success': False, 'error': '发送过于频繁，请稍后再试'}), 429

    ip_count = SmsVerification.query.filter(
        SmsVerification.ip == ip,
        SmsVerification.purpose == 'register',
        SmsVerification.sent_at >= (now - timedelta(minutes=10)),
    ).count()
    if ip_count >= 8:
        return jsonify({'success': False, 'error': '请求过于频繁，请稍后再试'}), 429

    code = gen_sms_code()
    v = SmsVerification(
        phone=phone,
        purpose='register',
        ip=ip,
        sent_at=now,
        expires_at=now + timedelta(minutes=10),
    )
    v.set_code(code)
    db.session.add(v)
    db.session.commit()

    send_sms_dev(phone, code)
    return jsonify({'success': True, 'message': '验证码已发送（开发模式：查看服务端控制台输出）'})


@app.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已退出登录', 'success')
    return redirect(url_for('login'))


# ==================== 辅助函数 ====================

def get_or_create_player():
    """获取当前登录玩家"""
    if current_user.is_authenticated:
        return current_user
    return None


def require_player():
    """要求玩家登录"""
    if not current_user.is_authenticated:
        return None
    return current_user


def create_daily_tasks(player):
    """创建每日任务"""
    today = date.today()
    for task_data in DEFAULT_DAILY_TASKS:
        task = PlayerDailyTask(
            player_id=player.id,
            player_uid=player.uid,
            task_id=task_data['task_id'],
            name=task_data['name'],
            description=task_data['description'],
            target=task_data['target'],
            reward_gold=task_data.get('reward_gold', 0),
            reward_gems=task_data.get('reward_gems', 0),
            reward_exp=task_data.get('reward_exp', 0),
            task_date=today,
            completed=(task_data['task_id'] == 'daily-login')
        )
        db.session.add(task)
    db.session.commit()


def update_energy(player):
    """更新体力"""
    now = datetime.now()
    hours_passed = (now - player.last_energy_update).total_seconds() / 3600
    energy_to_recover = min(int(hours_passed * 10), player.max_energy - player.energy)
    
    if energy_to_recover > 0:
        player.energy = min(player.max_energy, player.energy + energy_to_recover)
        player.last_energy_update = now
        db.session.commit()


def check_daily_reset(player):
    """检查每日任务重置"""
    today = date.today()
    if player.last_login_date != today:
        # 删除旧任务
        PlayerDailyTask.query.filter_by(player_id=player.id).delete()
        # 创建新任务
        create_daily_tasks(player)
        # 更新登录信息
        player.last_login_date = today
        player.total_play_days += 1
        db.session.commit()


def grant_player_exp(player, exp_amount, source=''):
    """通用玩家经验发放 + 自动升级检测

    Returns:
        dict: {'level_ups': int, 'new_level': int, 'level_rewards': list}
    """
    if exp_amount <= 0:
        return {'level_ups': 0, 'new_level': player.level, 'level_rewards': []}

    player.exp += exp_amount
    level_ups = 0
    level_rewards = []

    while player.level < MAX_PLAYER_LEVEL:
        exp_needed = get_exp_to_next_level(player.level)
        if exp_needed <= 0 or player.exp < exp_needed:
            break
        player.exp -= exp_needed
        player.level += 1
        level_ups += 1

        reward = get_level_reward(player.level)
        if reward:
            player.gold += reward.get('gold', 0)
            player.gems += reward.get('gems', 0)
            level_rewards.append({'level': player.level, 'reward': reward})

    player.exp_to_next = get_exp_to_next_level(player.level)

    if level_ups > 0 and source:
        try:
            _sync_seven_day_by_event(player, 'levelup', {'level': player.level})
            sync_main_quests(player, 'levelup')
        except Exception:
            pass

    return {'level_ups': level_ups, 'new_level': player.level, 'level_rewards': level_rewards}


def get_battle_character(character_instance):
    """获取战斗用角色数据"""
    template = get_character_by_id(character_instance.character_id)
    if not template:
        return None
    
    rarity = template['rarity']

    # ============ 星魂系统（复用 stars 字段）============
    # 定义：
    # - 2/4星魂：增加属性
    # - 1/3星魂：强化技能
    # - 5星魂：大幅强化被动技能
    raw_star_soul = int(getattr(character_instance, 'stars', 0) or 0)
    star_soul_level = max(0, min(raw_star_soul, 5))
    # 蓝卡以上才有星魂（稀有 rare 及以上；common 视为无星魂）
    if rarity == 'common':
        star_soul_level = 0

    # 属性基数：忽略突破与旧星级倍率，星魂相关属性由下面手动增幅
    stats = calculate_stats(
        template['stats'],
        character_instance.level,
        0,
        0,
        rarity=rarity,
    )

    # 装备加成
    try:
        eqs = PlayerEquipment.query.filter_by(
            player_id=character_instance.player_id,
            equipped_character_instance_id=character_instance.id
        ).all()
        for e in eqs:
            stats['hp'] += e.bonus_hp
            stats['max_hp'] += e.bonus_hp
            stats['attack'] += e.bonus_attack
            stats['defense'] += e.bonus_defense
            stats['magic_attack'] += e.bonus_magic_attack
            stats['magic_defense'] += e.bonus_magic_defense
            stats['speed'] += e.bonus_speed
    except Exception:
        pass

    # 符文加成
    try:
        runes = PlayerRune.query.filter_by(
            player_id=character_instance.player_id,
            equipped_character_instance_id=character_instance.id
        ).all()
        for r in runes:
            stats['hp'] += r.bonus_hp
            stats['max_hp'] += r.bonus_hp
            stats['attack'] += r.bonus_attack
            stats['defense'] += r.bonus_defense
            stats['magic_attack'] += r.bonus_magic_attack
            stats['magic_defense'] += r.bonus_magic_defense
            stats['speed'] += r.bonus_speed
    except Exception:
        pass

    # 天赋加成
    try:
        talents = PlayerTalent.query.filter_by(
            player_id=character_instance.player_id,
            character_instance_id=character_instance.id
        ).all()
        for t in talents:
            if t.node_id == 'atk':
                stats['attack'] += 5 * (t.level or 0)
                stats['magic_attack'] += 5 * (t.level or 0)
            elif t.node_id == 'def':
                stats['defense'] += 4 * (t.level or 0)
                stats['magic_defense'] += 4 * (t.level or 0)
            elif t.node_id == 'hp':
                stats['hp'] += 40 * (t.level or 0)
                stats['max_hp'] += 40 * (t.level or 0)
    except Exception:
        pass

    # 星魂：2/4 星魂增加属性（cumulative）
    attr_bonus_pct = 0.0
    if star_soul_level >= 2:
        attr_bonus_pct += 0.05
    if star_soul_level >= 4:
        attr_bonus_pct += 0.05
    if attr_bonus_pct > 0:
        mult = 1.0 + attr_bonus_pct
        for k in ('hp', 'max_hp', 'attack', 'defense', 'magic_attack', 'magic_defense', 'speed'):
            if k in stats:
                stats[k] = int(round(stats[k] * mult))

    # 动态生成技能列表（新技能系统）
    all_skills = get_skills_for_character(
        template['id'],
        character_instance.level,
        rarity,
        template['role_type'],
        template['element'],
    )
    if not all_skills:
        all_skills = template.get('skills', [])

    # 星魂：每角色 1/3/5 效果（可配置/可覆盖）
    from game_data import get_star_soul_effects
    star_soul_effects = get_star_soul_effects(template)

    def _merge_mods(*mods):
        out = {}
        for m in mods:
            if isinstance(m, dict):
                out.update(m)
        return out

    mods_1 = (star_soul_effects.get(1) or {}).get('modifiers', {}) if star_soul_level >= 1 else {}
    mods_3 = (star_soul_effects.get(3) or {}).get('modifiers', {}) if star_soul_level >= 3 else {}
    mods_5 = (star_soul_effects.get(5) or {}).get('modifiers', {}) if star_soul_level >= 5 else {}
    active_mods = _merge_mods(mods_1, mods_3)
    passive_mods = _merge_mods(mods_5)

    def _scale_effects(effects, factor):
        if not effects or factor == 1.0:
            return
        for eff in effects:
            if not isinstance(eff, dict):
                continue
            # 绝大多数效果在战斗里使用 eff.value 作为百分比增减
            if 'value' in eff and isinstance(eff['value'], (int, float)):
                # 保留为百分比的整数表现（更符合战斗脚本的假设）
                if isinstance(eff['value'], int):
                    eff['value'] = int(round(eff['value'] * factor))
                else:
                    eff['value'] = round(eff['value'] * factor, 3)
            if 'damage_pct' in eff and isinstance(eff['damage_pct'], (int, float)):
                eff['damage_pct'] = int(round(eff['damage_pct'] * factor))
            if 'heal_pct' in eff and isinstance(eff['heal_pct'], (int, float)):
                eff['heal_pct'] = int(round(eff['heal_pct'] * factor))
            if 'shield' in eff and isinstance(eff['shield'], (int, float)):
                eff['shield'] = int(round(eff['shield'] * factor))
            if 'chance' in eff and isinstance(eff['chance'], (int, float)):
                # chance 可能为 0~1，也可能是 0~0.99，做一个上限保护
                eff['chance'] = min(1.0, round(eff['chance'] * factor, 3))

    # 先对 all_skills 做星魂强化（1/3：主动；5：被动），再由后续逻辑分出 passives/equipable
    if star_soul_level > 0:
        cd_delta = int(active_mods.get('cooldown_delta', 0) or 0)
        power_mult = float(active_mods.get('power_mult', 1.0) or 1.0)
        dur_bonus = int(active_mods.get('effect_duration_bonus', 0) or 0)

        passive_mult = float(passive_mods.get('passive_effect_mult', 1.0) or 1.0)

        def _apply_duration_bonus(effects, bonus):
            if not effects or bonus == 0:
                return
            for eff in effects:
                if not isinstance(eff, dict):
                    continue
                if 'duration' in eff and isinstance(eff['duration'], int) and eff['duration'] > 0:
                    eff['duration'] = max(0, eff['duration'] + bonus)

        for sk in all_skills:
            is_passive = bool(sk.get('is_passive') or sk.get('type') == 'passive')
            if is_passive:
                if passive_mult != 1.0:
                    _scale_effects(sk.get('effects'), passive_mult)
                    if sk.get('power') and isinstance(sk.get('power'), (int, float)) and sk['power'] > 0:
                        sk['power'] = int(round(sk['power'] * passive_mult))
                continue

            # 主动技能：CD/威力/持续回合加成（不影响觉醒）
            if not sk.get('is_awakening'):
                if cd_delta != 0 and isinstance(sk.get('cooldown'), int):
                    sk['cooldown'] = max(0, sk['cooldown'] + cd_delta)
                if power_mult != 1.0 and sk.get('power') and isinstance(sk.get('power'), (int, float)) and sk['power'] > 0:
                    sk['power'] = int(round(sk['power'] * power_mult))
                if dur_bonus != 0:
                    _apply_duration_bonus(sk.get('effects'), dur_bonus)

    passives = [s for s in all_skills if s.get('is_passive') or s.get('type') == 'passive']
    awakening = next((s for s in all_skills if s.get('is_awakening')), None)

    # 可装备的主动技能 = 排除被动和觉醒
    equipable = [s for s in all_skills
                 if not s.get('is_passive') and s.get('type') != 'passive'
                 and not s.get('is_awakening')]

    # 从关系表读取已装备的主动技能
    equip_rows = CharacterEquippedSkill.query.filter_by(
        character_instance_id=character_instance.id
    ).order_by(CharacterEquippedSkill.slot).all()
    equipped_ids = [r.skill_id for r in equip_rows]

    if equipped_ids:
        equipped = []
        for sid in equipped_ids:
            for s in equipable:
                if s['id'] == sid:
                    equipped.append(s)
                    break
    else:
        equipped = equipable[:4]

    battle_skills = equipped + passives

    return {
        'id': character_instance.id,
        'character_id': template['id'],
        'name': template['name'],
        'title': template['title'],
        'element': template['element'],
        'role_type': template['role_type'],
        'avatar': template['avatar'],
        'illustration': template.get('illustration', template.get('avatar')),
        'rarity': rarity,
        'level': character_instance.level,
        'stars': star_soul_level,  # 星魂等级（复用 stars 字段语义）
        'soul_power': int(getattr(character_instance, 'soul_power', 0) or 0),
        'star_soul_level': star_soul_level,
        'star_soul_effects': star_soul_effects,
        'stats': stats,
        'current_stats': stats.copy(),
        'skills': battle_skills,
        'all_skills': all_skills,
        'equipped_skill_ids': equipped_ids,
        'awakening_skill': awakening,
    }


def check_feature_unlocked(player, feature_key):
    """检查某功能是否已解锁"""
    cfg = FEATURE_UNLOCK.get(feature_key)
    if not cfg:
        return True
    if player.level < cfg['level']:
        return False
    if cfg['quest']:
        claimed = PlayerMainQuest.query.filter_by(
            player_id=player.id, quest_id=cfg['quest'], claimed=True
        ).first()
        if not claimed:
            return False
    return True


def seed_starter_equipment(player: Player) -> None:
    """给新号发放基础装备（避免仓库空白）"""
    existing = PlayerEquipment.query.filter_by(player_id=player.id).count()
    if existing:
        return
    items = [
        PlayerEquipment(player_id=player.id, player_uid=player.uid, name='新手铁剑', slot_type='weapon', rarity='common', bonus_attack=12),
        PlayerEquipment(player_id=player.id, player_uid=player.uid, name='学徒护甲', slot_type='armor', rarity='common', bonus_defense=10, bonus_hp=60),
        PlayerEquipment(player_id=player.id, player_uid=player.uid, name='训练护符', slot_type='accessory', rarity='common', bonus_speed=6),
    ]
    for it in items:
        db.session.add(it)
    db.session.commit()


def seed_starter_character(player: Player) -> None:
    """给新号发放初始角色"""
    # 检查是否已有角色
    existing = PlayerCharacter.query.filter_by(player_id=player.id).count()
    if existing > 0:
        return
    
    # 获取默认初始角色
    starter_char = get_starter_character_by_id(DEFAULT_STARTER_CHARACTER)
    if not starter_char:
        starter_char = STARTER_CHARACTERS[0] if STARTER_CHARACTERS else None
    
    if not starter_char:
        return
    
    # 创建角色实例
    char_instance = PlayerCharacter(
        player_id=player.id,
        player_uid=player.uid,
        character_id=starter_char['id'],
        level=1,
        exp=0,
        stars=0,
        breakthrough=0
    )
    db.session.add(char_instance)
    db.session.commit()
    
    team_slot = PlayerTeam(
        player_id=player.id,
        player_uid=player.uid,
        slot=0,
        character_instance_id=char_instance.id
    )
    db.session.add(team_slot)
    db.session.commit()


def seed_starter_research(player: Player) -> None:
    """给新号发放基础符文（天赋默认 0 级无需发放）"""
    existing = PlayerRune.query.filter_by(player_id=player.id).count()
    if existing:
        return
    items = [
        PlayerRune(player_id=player.id, player_uid=player.uid, name='微光符文·攻', rarity='common', bonus_attack=8),
        PlayerRune(player_id=player.id, player_uid=player.uid, name='微光符文·守', rarity='common', bonus_defense=8),
        PlayerRune(player_id=player.id, player_uid=player.uid, name='微光符文·生', rarity='common', bonus_hp=80),
    ]
    for it in items:
        db.session.add(it)
    db.session.commit()


# ==================== 路由 ====================

@app.route('/')
@login_required
def index():
    """首页"""
    player = current_user
    update_energy(player)
    check_daily_reset(player)
    
    # 获取角色
    characters = []
    for char in player.characters:
        battle_char = get_battle_character(char)
        if battle_char:
            characters.append(battle_char)
    
    # 获取队伍
    team = []
    for team_member in player.team:
        char_instance = PlayerCharacter.query.get(team_member.character_instance_id)
        if char_instance:
            battle_char = get_battle_character(char_instance)
            if battle_char:
                team.append(battle_char)
    
    # 获取每日任务
    daily_tasks = [task.to_dict() for task in player.daily_tasks.filter_by(task_date=date.today())]
    
    # 图鉴：全角色模板 + 已拥有 id 列表
    all_character_templates = get_all_characters()
    owned_character_ids = [c.character_id for c in player.characters]

    # 图鉴：全技能模板（用于技能图鉴筛选/预览）
    all_skill_templates = []
    skill_kind_order = ['shared', 'exclusive', 'awakening', 'passive']
    # 直接查模板表，按需拼装给前端（这里模板量较小，适合一次性加载）
    for st in SkillTemplate.query.order_by(SkillTemplate.unlock_level.asc()).all():
        d = st.to_skill_dict()
        d['element'] = st.element

        if st.is_passive:
            d['kind'] = 'passive'
        elif st.is_awakening:
            d['kind'] = 'awakening'
        elif st.is_exclusive or st.category == 'exclusive':
            d['kind'] = 'exclusive'
        else:
            d['kind'] = 'shared'

        d['roles'] = st.roles or ''
        d['character_id'] = st.character_id or ''
        all_skill_templates.append(d)

    skill_elements = sorted({s['element'] for s in all_skill_templates if s.get('element')})
    skill_elements_with_all = [''] + skill_elements
    skill_types = sorted({s['type'] for s in all_skill_templates if s.get('type')})
    skill_types_with_all = [''] + skill_types
    skill_targets = sorted({s['target'] for s in all_skill_templates if s.get('target')})
    skill_targets_with_all = [''] + skill_targets
    skill_kinds_with_all = [''] + skill_kind_order
    
    # 计算功能解锁状态
    claimed_quest_ids = set()
    mq_records = PlayerMainQuest.query.filter_by(player_id=player.id, claimed=True).all()
    for r in mq_records:
        claimed_quest_ids.add(r.quest_id)

    unlocked_features = {}
    for feat_key, cfg in FEATURE_UNLOCK.items():
        level_ok = player.level >= cfg['level']
        quest_ok = cfg['quest'] is None or cfg['quest'] in claimed_quest_ids
        unlocked_features[feat_key] = {
            'unlocked': level_ok and quest_ok,
            'name': cfg['name'],
            'level': cfg['level'],
            'quest': cfg['quest'],
            'level_ok': level_ok,
            'quest_ok': quest_ok,
        }

    return render_template('index.html',
        player=player,
        characters=characters,
        team=team,
        daily_tasks=daily_tasks,
        all_character_templates=all_character_templates,
        owned_character_ids=owned_character_ids,
        all_skill_templates=all_skill_templates,
        skill_elements=skill_elements_with_all,
        skill_types=skill_types_with_all,
        skill_targets=skill_targets_with_all,
        skill_kinds=skill_kinds_with_all,
        unlocked_features=unlocked_features,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        role_names=ROLE_NAMES
    )


@app.route('/characters')
@login_required
def characters():
    """角色页面"""
    player = current_user
    
    # 技能类型名称映射
    type_names = {
        'physical': '物理', 'magic': '魔法', 'heal': '治疗',
        'buff': '增益', 'debuff': '减益', 'passive': '被动'
    }
    
    # 元素图标映射
    element_icons = {
        'fire': '/static/images/skills/elements/fire.png',
        'water': '/static/images/skills/elements/water.png',
        'wind': '/static/images/skills/elements/wind.png',
        'earth': '/static/images/skills/elements/earth.png',
        'light': '/static/images/skills/elements/light.png',
        'dark': '/static/images/skills/elements/dark.png',
        'electric': '/static/images/skills/elements/electric.png',
        'fighting': '/static/images/skills/elements/fighting.png',
        'ground': '/static/images/skills/elements/ground.png',
    }
    
    # 获取所有角色
    all_chars = []
    for char in player.characters:
        battle_char = get_battle_character(char)
        if battle_char:
            battle_char['instance_id'] = char.id
            battle_char['breakthrough'] = char.breakthrough
            
            # 为技能添加图标信息
            if 'skills' in battle_char:
                for skill in battle_char['skills']:
                    skill['icon'] = get_skill_icon(skill, battle_char.get('character_id'))
                    skill['type_name'] = type_names.get(skill.get('type', 'physical'), '物理')
                    # 添加元素图标
                    element = skill.get('element')
                    if element and element in element_icons:
                        skill['element_icon'] = element_icons[element]
            
            all_chars.append(battle_char)
    
    # 按稀有度排序
    rarity_order = {'legendary': 0, 'epic': 1, 'rare': 2, 'common': 3}
    all_chars.sort(key=lambda x: rarity_order.get(x['rarity'], 3))
    
    favorites = PlayerFavoriteCharacter.query.filter_by(player_id=player.id).all()
    favorite_ids = [f.character_instance_id for f in favorites]

    return render_template('characters.html',
        player=player,
        characters=all_chars,
        team_ids=[t.character_instance_id for t in player.team],
        favorite_ids=favorite_ids,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        role_names=ROLE_NAMES
    )


@app.route('/character/preview/<character_id>')
@login_required
def character_preview(character_id):
    """角色预览页面 - 根据角色模板ID预览"""
    from game_data import ALL_CHARACTERS, get_skill_icon, SKILL_ELEMENT_ICONS
    
    # 查找角色模板
    char_template = None
    for char in ALL_CHARACTERS:
        if char['id'] == character_id:
            char_template = char.copy()
            break
    
    if not char_template:
        flash('角色不存在', 'error')
        return redirect(url_for('characters'))
    
    player = current_user
    
    # 检查是否已拥有该角色
    owned_char = PlayerCharacter.query.filter_by(
        player_id=player.id,
        character_id=character_id
    ).first()
    
    if owned_char:
        # 如果已拥有，跳转到角色详情
        return redirect(url_for('character_detail', instance_id=owned_char.id))
    
    # 为技能添加图标
    if 'skills' in char_template:
        skills_with_icons = []
        for skill in char_template['skills']:
            skill_copy = skill.copy()
            skill_copy['icon'] = get_skill_icon(skill, character_id)
            skills_with_icons.append(skill_copy)
        char_template['skills'] = skills_with_icons
    
    # 返回预览模板
    return render_template('character_preview.html',
        player=player,
        character=char_template,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        role_names=ROLE_NAMES
    )


@app.route('/character/<int:instance_id>')
@login_required
def character_detail(instance_id):
    """角色详情"""
    player = current_user
    char_instance = PlayerCharacter.query.get_or_404(instance_id)
    
    if char_instance.player_id != player.id:
        flash('无权查看该角色', 'error')
        return redirect(url_for('characters'))
    
    battle_char = get_battle_character(char_instance)
    if not battle_char:
        flash('角色不存在', 'error')
        return redirect(url_for('characters'))
    
    battle_char['instance_id'] = instance_id
    battle_char['breakthrough'] = char_instance.breakthrough
    is_in_team = any(t.character_instance_id == instance_id for t in player.team)
    team_ids = [t.character_instance_id for t in player.team]

    skill_unlock_preview = get_skill_unlock_preview(
        char_instance.character_id,
        battle_char['rarity'],
        battle_char['role_type'],
        battle_char['element'],
    )
    
    return render_template('character_detail.html',
        player=player,
        character=battle_char,
        is_in_team=is_in_team,
        team_ids=team_ids,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        role_names=ROLE_NAMES,
        skill_unlock_preview=skill_unlock_preview,
    )


@app.route('/skill-preview/<string:skill_id>')
@login_required
def skill_preview(skill_id: str):
    """技能预览（模板技能，不依赖玩家拥有/养成状态）"""
    player = current_user
    st = SkillTemplate.query.get_or_404(skill_id)

    d = st.to_skill_dict()
    d['element'] = st.element
    d['roles'] = st.roles or ''
    d['character_id'] = st.character_id or ''
    d['category'] = st.category

    if st.is_passive:
        d['kind'] = 'passive'
    elif st.is_awakening:
        d['kind'] = 'awakening'
    elif st.is_exclusive or st.category == 'exclusive':
        d['kind'] = 'exclusive'
    else:
        d['kind'] = 'shared'

    # 返回链接：尽量回到来源页
    back_url = request.referrer or url_for('index')

    return render_template(
        'skill_preview.html',
        player=player,
        skill=d,
        back_url=back_url,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        role_names=ROLE_NAMES,
    )


@app.route('/character-preview/<string:character_id>')
@login_required
def character_preview(character_id: str):
    """角色预览（不依赖玩家是否拥有，也不含出战/养成状态）"""
    player = current_user
    tpl = get_character_by_id(character_id)
    if not tpl:
        flash('角色不存在', 'error')
        return redirect(url_for('index'))

    skill_unlock_preview = get_skill_unlock_preview(
        character_id=tpl['id'],
        rarity=tpl.get('rarity', 'common'),
        role_type=tpl.get('role_type'),
        element=tpl.get('element'),
    )
    from game_data import get_star_soul_effects
    star_soul_effects = get_star_soul_effects(tpl)

    return render_template(
        'character_preview.html',
        player=player,
        character=tpl,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        role_names=ROLE_NAMES,
        skill_unlock_preview=skill_unlock_preview,
        star_soul_effects=star_soul_effects,
    )


@app.route('/summon')
@login_required
def summon():
    """召唤页面"""
    player = current_user
    
    return render_template('summon.html',
        player=player,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        get_character_by_id=get_character_by_id,
        RARITY_COLORS=RARITY_COLORS,
        current_up_characters=CURRENT_UP_CHARACTERS,
        up_rate_multiplier=UP_RATE_MULTIPLIER,
    )


@app.route('/research')
@login_required
def research():
    """研究所页面"""
    player = current_user
    if not check_feature_unlocked(player, 'research'):
        flash(f'研究所需要 Lv.{FEATURE_UNLOCK["research"]["level"]} 解锁')
        return redirect(url_for('index'))
    runes = PlayerRune.query.filter_by(player_id=player.id).order_by(PlayerRune.id.desc()).all()
    # 角色列表 + 当前天赋
    chars = []
    for ci in player.characters.order_by(PlayerCharacter.id.asc()).all():
        tpl = get_character_by_id(ci.character_id)
        trows = PlayerTalent.query.filter_by(player_id=player.id, character_instance_id=ci.id).all()
        tmap = {t.node_id: (t.level or 0) for t in trows}
        chars.append({
            'instance_id': ci.id,
            'name': tpl.get('name') if tpl else ci.character_id,
            'avatar': tpl.get('avatar') if tpl else None,
            'level': ci.level,
            'talents': {
                'atk': tmap.get('atk', 0),
                'def': tmap.get('def', 0),
                'hp': tmap.get('hp', 0),
            }
        })
    return render_template('research.html', player=player, runes=runes, owned_chars=chars, rarity_names=RARITY_NAMES, rarity_colors=RARITY_COLORS)


@app.route('/api/runes/equip', methods=['POST'])
@login_required
def api_runes_equip():
    player = current_user
    data = request.get_json(silent=True) or {}
    rune_id = data.get('rune_id')
    instance_id = data.get('instance_id')
    slot = data.get('slot')
    try:
        rune_id = int(rune_id)
        instance_id = int(instance_id)
        slot = int(slot)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400
    if slot not in (1, 2):
        return jsonify({'success': False, 'error': '槽位范围为 1-2'}), 400

    r = PlayerRune.query.get(rune_id)
    if not r or r.player_id != player.id:
        return jsonify({'success': False, 'error': '符文不存在'}), 404

    ci = PlayerCharacter.query.get(instance_id)
    if not ci or ci.player_id != player.id:
        return jsonify({'success': False, 'error': '角色不存在'}), 404

    # 同角色同槽位只能装一个：卸下旧的
    PlayerRune.query.filter_by(player_id=player.id, equipped_character_instance_id=instance_id, equipped_slot=slot).update({
        'equipped_character_instance_id': None,
        'equipped_slot': None,
    })
    r.equipped_character_instance_id = instance_id
    r.equipped_slot = slot
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/runes/unequip', methods=['POST'])
@login_required
def api_runes_unequip():
    player = current_user
    data = request.get_json(silent=True) or {}
    rune_id = data.get('rune_id')
    try:
        rune_id = int(rune_id)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400
    r = PlayerRune.query.get(rune_id)
    if not r or r.player_id != player.id:
        return jsonify({'success': False, 'error': '符文不存在'}), 404
    r.equipped_character_instance_id = None
    r.equipped_slot = None
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/talents/upgrade', methods=['POST'])
@login_required
def api_talents_upgrade():
    player = current_user
    data = request.get_json(silent=True) or {}
    instance_id = data.get('instance_id')
    node_id = (data.get('node_id') or '').strip()
    try:
        instance_id = int(instance_id)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400
    if node_id not in ('atk', 'def', 'hp'):
        return jsonify({'success': False, 'error': '无效天赋'}), 400

    ci = PlayerCharacter.query.get(instance_id)
    if not ci or ci.player_id != player.id:
        return jsonify({'success': False, 'error': '角色不存在'}), 404

    t = PlayerTalent.query.filter_by(player_id=player.id, character_instance_id=instance_id, node_id=node_id).first()
    if not t:
        t = PlayerTalent(player_id=player.id, character_instance_id=instance_id, node_id=node_id, level=0)
        db.session.add(t)
        db.session.flush()

    if t.level >= 10:
        return jsonify({'success': False, 'error': '已达最大等级'}), 400

    # 简易升级消耗：金币 = (当前等级+1)*800
    cost = (t.level + 1) * 800
    if player.gold < cost:
        return jsonify({'success': False, 'error': '金币不足'}), 400

    player.gold -= cost
    t.level += 1
    db.session.commit()
    return jsonify({'success': True, 'new_level': t.level, 'cost': cost})


@app.route('/shop')
@login_required
def shop():
    """商会页面"""
    player = current_user
    if not check_feature_unlocked(player, 'shop'):
        flash(f'商会需要 Lv.{FEATURE_UNLOCK["shop"]["level"]} 解锁')
        return redirect(url_for('index'))
    today = date.today()
    purchases = ShopPurchase.query.filter_by(player_id=player.id, purchase_date=today).all()
    purchase_counts = {p.item_id: p.count for p in purchases}
    return render_template('shop.html', player=player, shop_items=SHOP_ITEMS, purchase_counts=purchase_counts)


@app.route('/inventory')
@login_required
def inventory():
    """仓库页面"""
    player = current_user
    equipment = PlayerEquipment.query.filter_by(player_id=player.id).order_by(PlayerEquipment.id.desc()).all()
    owned_chars = []
    for ci in player.characters.order_by(PlayerCharacter.id.asc()).all():
        tpl = get_character_by_id(ci.character_id)
        owned_chars.append({
            'instance_id': ci.id,
            'name': tpl.get('name') if tpl else ci.character_id,
            'avatar': tpl.get('avatar') if tpl else None,
            'level': ci.level,
        })
    return render_template(
        'inventory.html',
        player=player,
        equipment=equipment,
        owned_chars=owned_chars,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
    )


@app.route('/api/equipment/list')
@login_required
def api_equipment_list():
    player = current_user
    items = PlayerEquipment.query.filter_by(player_id=player.id).order_by(PlayerEquipment.id.desc()).all()
    return jsonify({'success': True, 'equipment': [e.to_dict() for e in items]})


@app.route('/api/equipment/equip', methods=['POST'])
@login_required
def api_equipment_equip():
    player = current_user
    data = request.get_json(silent=True) or {}
    eq_id = data.get('equipment_id')
    instance_id = data.get('instance_id')
    try:
        eq_id = int(eq_id)
        instance_id = int(instance_id)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400

    eq = PlayerEquipment.query.get(eq_id)
    if not eq or eq.player_id != player.id:
        return jsonify({'success': False, 'error': '装备不存在'}), 404

    ci = PlayerCharacter.query.get(instance_id)
    if not ci or ci.player_id != player.id:
        return jsonify({'success': False, 'error': '角色不存在'}), 404

    # 同角色同槽位只能穿一件：先卸下旧的
    PlayerEquipment.query.filter_by(
        player_id=player.id,
        equipped_character_instance_id=instance_id,
        slot_type=eq.slot_type
    ).update({'equipped_character_instance_id': None})

    eq.equipped_character_instance_id = instance_id
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/equipment/unequip', methods=['POST'])
@login_required
def api_equipment_unequip():
    player = current_user
    data = request.get_json(silent=True) or {}
    eq_id = data.get('equipment_id')
    try:
        eq_id = int(eq_id)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400

    eq = PlayerEquipment.query.get(eq_id)
    if not eq or eq.player_id != player.id:
        return jsonify({'success': False, 'error': '装备不存在'}), 404

    eq.equipped_character_instance_id = None
    db.session.commit()
    return jsonify({'success': True})


@app.route('/arena')
@login_required
def arena():
    """竞技场页面"""
    player = current_user
    if not check_feature_unlocked(player, 'arena'):
        flash(f'竞技场需要 Lv.{FEATURE_UNLOCK["arena"]["level"]} 解锁')
        return redirect(url_for('index'))
    arena_records = ArenaRecord.query.filter_by(player_id=player.id).order_by(ArenaRecord.created_at.desc()).limit(20).all()
    arena_stats = {
        'arena_score': player.arena_score or 1000,
        'arena_wins': player.arena_wins or 0,
        'arena_losses': player.arena_losses or 0,
    }
    return render_template(
        'arena.html',
        player=player,
        arena_bots=ARENA_BOTS,
        arena_stats=arena_stats,
        arena_records=arena_records,
    )


@app.route('/stages')
@login_required
def stages():
    """副本页面"""
    player = current_user
    if not check_feature_unlocked(player, 'stages'):
        flash(f'演武场需要 Lv.{FEATURE_UNLOCK["stages"]["level"]} 解锁')
        return redirect(url_for('index'))
    
    # 更新玩家经验值到下一级所需经验
    player.exp_to_next = get_exp_to_next_level(player.level)
    
    # 获取已通关关卡
    completed = [s.stage_id for s in player.completed_stages]
    
    # 获取关卡星级
    stage_stars = {}
    for s in player.completed_stages:
        stage_stars[s.stage_id] = s.stars if hasattr(s, 'stars') else 1
    
    # 获取章节解锁状态
    chapter_unlock_status = get_chapter_unlock_status(player.level, completed)
    
    # 获取关卡解锁状态
    stage_unlock_status = {}
    for chapter in CHAPTERS:
        for stage in chapter['stages']:
            stage_unlock_status[stage['id']] = get_stage_unlock_status(
                player.level, completed, stage['id']
            )
    
    # 获取队伍
    team = []
    for team_member in player.team:
        char_instance = PlayerCharacter.query.get(team_member.character_instance_id)
        if char_instance:
            battle_char = get_battle_character(char_instance)
            if battle_char:
                team.append(battle_char)

    # 计算日常副本开放状态（今天星期几，1=周一 7=周日）
    today_weekday = datetime.now().isoweekday()
    daily_dungeons_today = []
    for d in DAILY_DUNGEONS:
        dd = dict(d)
        dd['is_open'] = today_weekday in d['open_days']
        daily_dungeons_today.append(dd)
    
    return render_template('stages.html',
        player=player,
        chapters=CHAPTERS,
        completed_stages=completed,
        stage_stars=stage_stars,
        chapter_unlock_status=chapter_unlock_status,
        stage_unlock_status=stage_unlock_status,
        team=team,
        difficulty_names=DIFFICULTY_NAMES,
        difficulty_colors=DIFFICULTY_COLORS,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        get_character_by_id=get_character_by_id,
        battle_modes=BATTLE_MODES,
        daily_dungeons=daily_dungeons_today,
        hero_trials=HERO_TRIALS,
        hard_dungeons=HARD_DUNGEONS,
    )


@app.route('/battle/<stage_id>')
@login_required
def battle(stage_id):
    """战斗页面"""
    player = current_user
    stage = get_stage_by_id(stage_id)
    
    if not stage:
        flash('关卡不存在', 'error')
        return redirect(url_for('stages'))
    
    # 检查体力
    if player.energy < stage['energy_cost']:
        flash('体力不足', 'error')
        return redirect(url_for('stages'))

    battle_mode = stage.get('battle_mode', '3v3')
    mode_info = BATTLE_MODES.get(battle_mode, BATTLE_MODES['3v3'])
    team_size = mode_info['team_size']
    
    # 获取队伍
    team = []
    for team_member in player.team:
        char_instance = PlayerCharacter.query.get(team_member.character_instance_id)
        if char_instance:
            battle_char = get_battle_character(char_instance)
            if battle_char:
                team.append(battle_char)
                if len(team) >= team_size:
                    break
    
    if not team:
        flash('请先设置队伍', 'error')
        return redirect(url_for('stages'))

    # 章节轻剧情
    chapter_dialogue = {'pre': [], 'post': []}
    dungeon_type = stage.get('dungeon_type', 'main')
    if dungeon_type == 'main':
        try:
            for ch in CHAPTERS:
                if any(s.get('id') == stage_id for s in (ch.get('stages') or [])):
                    chapter_dialogue = ch.get('dialogue') or chapter_dialogue
                    break
        except Exception:
            pass
    
    # 生成敌人（使用新技能系统）
    enemies = []
    for i, enemy_id in enumerate(stage['enemy_ids']):
        template = get_character_by_id(enemy_id)
        if template:
            level = stage['enemy_levels'][i] if i < len(stage['enemy_levels']) else 1
            e_rarity = template.get('rarity', 'common')
            stats = calculate_stats(template['stats'], level, 1, 0, rarity=e_rarity)
            is_boss = bool(
                dungeon_type == 'trial' or
                (str(stage.get('id', '')).endswith('-3') and i == 0)
            )
            e_all_skills = get_skills_for_character(
                template['id'], level, e_rarity,
                template.get('role_type', 'warrior'),
                template.get('element', 'earth'),
            )
            if not e_all_skills:
                e_all_skills = template.get('skills', [])
            e_passives = [s for s in e_all_skills if s.get('is_passive') or s.get('type') == 'passive']
            e_awakening = next((s for s in e_all_skills if s.get('is_awakening')), None)
            e_active = [s for s in e_all_skills
                        if not s.get('is_passive') and s.get('type') != 'passive'
                        and not s.get('is_awakening')]
            e_equipped = (e_active[:4] if len(e_active) <= 4
                          else random.sample(e_active, 4))
            e_skills = e_equipped + e_passives
            enemies.append({
                'id': f'enemy-{i}',
                'character_id': template['id'],
                'name': template['name'],
                'element': template['element'],
                'role_type': template.get('role_type', 'warrior'),
                'avatar': template['avatar'],
                'level': level,
                'stats': stats,
                'current_stats': stats.copy(),
                'skills': e_skills,
                'awakening_skill': e_awakening,
                'is_boss': is_boss,
            })
    
    return render_template('battle.html',
        player=player,
        stage=stage,
        chapter_dialogue=chapter_dialogue,
        team=team,
        enemies=enemies,
        battle_mode=battle_mode,
        mode_info=mode_info,
        battle_items=BATTLE_ITEMS,
        dungeon_type=dungeon_type,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS
    )


# ==================== 主线任务同步 ====================

def sync_main_quests(player, event_type, event_param=None):
    """根据事件类型检查并更新主线任务进度"""
    try:
        quests = PlayerMainQuest.query.filter_by(player_id=player.id, claimed=False).all()
        quest_map = {q.quest_id: q for q in quests}

        for cfg in MAIN_QUESTS:
            mq = quest_map.get(cfg['id'])
            if not mq or mq.claimed:
                continue

            gt = cfg.get('goal_type', '')
            target = cfg.get('goal_target', 1)
            progress = 0

            if gt == 'claim_newbie':
                progress = 1 if player.newbie_pack_claimed else 0
            elif gt == 'summon':
                progress = player.total_summon_count or 0
            elif gt == 'summon_ten':
                progress = (player.total_summon_count or 0) // 10
            elif gt == 'levelup':
                max_lvl_row = db.session.execute(
                    text("SELECT MAX(level) FROM player_characters WHERE player_id = :pid"),
                    {'pid': player.id}
                ).scalar()
                progress = int(max_lvl_row or 0)
            elif gt == 'team_set':
                progress = player.team.count()
            elif gt == 'clear_stage':
                gp = cfg.get('goal_param')
                if gp:
                    if PlayerCompletedStage.query.filter_by(player_id=player.id, stage_id=gp).first():
                        progress = 1
                    elif event_param and event_param == gp:
                        progress = 1
            elif gt == 'breakthrough':
                bt_row = db.session.execute(
                    text("SELECT MAX(breakthrough) FROM player_characters WHERE player_id = :pid"),
                    {'pid': player.id}
                ).scalar()
                progress = int(bt_row or 0)
            elif gt == 'char_level':
                max_lvl_row = db.session.execute(
                    text("SELECT MAX(level) FROM player_characters WHERE player_id = :pid"),
                    {'pid': player.id}
                ).scalar()
                progress = int(max_lvl_row or 0)

            mq.progress = max(mq.progress, progress)
            if mq.progress >= target:
                mq.completed = True

        db.session.commit()
    except Exception:
        db.session.rollback()


# ==================== API 路由 ====================

@app.route('/api/newbie-pack/claim', methods=['POST'])
@login_required
def api_newbie_pack_claim():
    """领取新手礼包"""
    player = current_user
    if player.newbie_pack_claimed:
        return jsonify({'success': False, 'error': '已领取新手礼包'}), 400

    player.gold += NEWBIE_PACK.get('gold', 0)
    player.gems += NEWBIE_PACK.get('gems', 0)
    player.summon_tickets += NEWBIE_PACK.get('summon_tickets', 0)
    player.exp_books += NEWBIE_PACK.get('exp_books', 0)
    player.energy += NEWBIE_PACK.get('energy', 0)
    player.newbie_pack_claimed = True
    player.tutorial_step = max(player.tutorial_step or 0, 1)

    # 新手礼包赠送50玩家经验（足够从Lv1升到Lv2还有富余）
    newbie_exp = 50
    lvl_result = grant_player_exp(player, newbie_exp, source='newbie_pack')

    db.session.commit()
    sync_main_quests(player, 'claim_newbie')

    pack_info = dict(NEWBIE_PACK)
    pack_info['player_exp'] = newbie_exp
    return jsonify({
        'success': True,
        'resources': pack_info,
        'level_up': lvl_result['level_ups'] > 0,
        'new_level': player.level
    })


@app.route('/api/summon', methods=['POST'])
@login_required
def api_summon():
    """抽卡API"""
    player = current_user
    data = request.get_json() or {}
    summon_type = data.get('type', 'once')  # once, ten, ticket
    
    # 计算消耗
    if summon_type == 'once':
        if player.gems < 100:
            return jsonify({'success': False, 'error': '钻石不足'}), 400
        player.gems -= 100
    elif summon_type == 'ten':
        if player.gems < 900:
            return jsonify({'success': False, 'error': '钻石不足'}), 400
        player.gems -= 900
    elif summon_type == 'ticket':
        if player.summon_tickets < 1:
            return jsonify({'success': False, 'error': '召唤券不足'}), 400
        player.summon_tickets -= 1
    else:
        return jsonify({'success': False, 'error': '无效的召唤类型'}), 400
    
    results = []
    count = 10 if summon_type == 'ten' else 1
    
    for _ in range(count):
        # 保底检查
        if player.legendary_pity_count >= 99:
            rarity = 'legendary'
        elif player.pity_count >= 49:
            rarity = 'epic'
        else:
            # 随机稀有度
            roll = random.random() * 100
            if roll < RARITY_WEIGHTS['legendary']:
                rarity = 'legendary'
            elif roll < RARITY_WEIGHTS['legendary'] + RARITY_WEIGHTS['epic']:
                rarity = 'epic'
            elif roll < RARITY_WEIGHTS['legendary'] + RARITY_WEIGHTS['epic'] + RARITY_WEIGHTS['rare']:
                rarity = 'rare'
            else:
                rarity = 'common'
        
        # UP池逻辑：如果该稀有度有UP角色，有概率抽到UP角色
        up_chars = CURRENT_UP_CHARACTERS.get(rarity, [])
        if up_chars:
            # 50%概率抽到UP角色
            if random.random() < 0.5:
                char_template = get_character_by_id(random.choice(up_chars))
                if char_template:
                    # 继续处理
                    pass
                else:
                    # UP角色不存在，从所有角色中随机选择
                    characters = get_characters_by_rarity(rarity)
                    if not characters:
                        characters = get_all_characters()
                    char_template = random.choice(characters)
            else:
                # 从所有该稀有度角色中随机选择
                characters = get_characters_by_rarity(rarity)
                if not characters:
                    characters = get_all_characters()
                char_template = random.choice(characters)
        else:
            # 没有UP角色，正常随机
            characters = get_characters_by_rarity(rarity)
            if not characters:
                characters = get_all_characters()
            char_template = random.choice(characters)
        
        # 检查是否已有该角色
        existing = PlayerCharacter.query.filter_by(
            player_id=player.id,
            character_id=char_template['id']
        ).first()
        
        if existing:
            # 重复获得：给该角色增加魂力（每次+1）
            # 蓝卡以上才有星魂/魂力体系；普通品质重复不计入魂力
            if rarity != 'common':
                existing.soul_power = int(getattr(existing, 'soul_power', 0) or 0) + 1
            is_new = False
            instance_id = existing.id
        else:
            # 创建新角色
            new_char = PlayerCharacter(
                player_id=player.id,
                player_uid=player.uid,
                character_id=char_template['id'],
                stars=0,
                soul_power=0,
            )
            db.session.add(new_char)
            db.session.flush()
            is_new = True
            instance_id = new_char.id
        
        # 更新保底计数
        if rarity == 'legendary':
            player.legendary_pity_count = 0
            player.pity_count = 0
        elif rarity == 'epic':
            player.pity_count = 0
            player.legendary_pity_count += 1
        else:
            player.pity_count += 1
            player.legendary_pity_count += 1
        
        # 记录抽卡历史
        history = SummonHistory(
            player_id=player.id,
            player_uid=player.uid,
            character_id=char_template['id'],
            rarity=rarity
        )
        db.session.add(history)
        
        results.append({
            'character_id': char_template['id'],
            'name': char_template['name'],
            'rarity': rarity,
            'avatar': char_template['avatar'],
            'is_new': is_new,
            'instance_id': instance_id
        })

    # First 10-pull guarantee: if this is a 10-pull and player's total was 0 before, ensure at least 1 epic
    was_first_ten = (summon_type == 'ten' and (player.total_summon_count or 0) == 0)
    if was_first_ten:
        has_epic = any(r['rarity'] in ('epic', 'legendary') for r in results)
        if not has_epic:
            upgrade_idx = random.randint(0, len(results) - 1)
            epic_chars = get_characters_by_rarity('epic')
            if epic_chars:
                epic_pick = random.choice(epic_chars)
                old_result = results[upgrade_idx]
                existing_epic = PlayerCharacter.query.filter_by(
                    player_id=player.id, character_id=epic_pick['id']
                ).first()
                if existing_epic:
                    is_new = False
                    inst_id = existing_epic.id
                    existing_epic.soul_power = int(getattr(existing_epic, 'soul_power', 0) or 0) + 1
                else:
                    new_epic = PlayerCharacter(
                        player_id=player.id,
                        player_uid=player.uid,
                        character_id=epic_pick['id'],
                        stars=0,
                        soul_power=0,
                    )
                    db.session.add(new_epic)
                    db.session.flush()
                    is_new = True
                    inst_id = new_epic.id
                results[upgrade_idx] = {
                    'character_id': epic_pick['id'],
                    'name': epic_pick['name'],
                    'rarity': 'epic',
                    'avatar': epic_pick['avatar'],
                    'is_new': is_new,
                    'instance_id': inst_id,
                }

    player.total_summon_count = (player.total_summon_count or 0) + count

    # 更新每日任务
    task = PlayerDailyTask.query.filter_by(
        player_id=player.id,
        task_id='daily-summon',
        task_date=date.today()
    ).first()
    if task:
        task.progress += 1
        if task.progress >= task.target:
            task.completed = True

    _sync_seven_day_by_event(player, 'summon', {'count': count})
    sync_main_quests(player, 'summon')

    # 召唤给玩家经验：单抽15，十连150
    summon_exp = 15 * count
    lvl_result = grant_player_exp(player, summon_exp, source='summon')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'results': results,
        'pity': player.pity_count,
        'legendary_pity': player.legendary_pity_count,
        'exp_gained': summon_exp,
        'level_up': lvl_result['level_ups'] > 0,
        'new_level': player.level
    })


@app.route('/api/starup', methods=['POST'])
@login_required
def api_starup():
    """星魂提升：消耗该角色魂力，提升星魂等级"""
    player = current_user
    data = request.get_json(silent=True) or {}
    instance_id = data.get('instance_id')
    try:
        instance_id = int(instance_id)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400

    char = PlayerCharacter.query.get_or_404(instance_id)
    if char.player_id != player.id:
        return jsonify({'success': False, 'error': '无权操作'}), 403

    tpl = get_character_by_id(char.character_id) or {}
    rarity = tpl.get('rarity') or 'common'

    # 星魂系统：普通品质没有星魂
    if rarity == 'common':
        return jsonify({'success': False, 'error': '普通品质无法提升星魂'}), 400

    if char.stars >= 5:
        return jsonify({'success': False, 'error': '已达最大星魂等级'}), 400

    # 消耗：每个魂力提升一次星魂
    cur_power = int(getattr(char, 'soul_power', 0) or 0)
    if cur_power < 1:
        return jsonify({'success': False, 'error': '魂力不足（需要 1）'}), 400

    char.soul_power = cur_power - 1
    char.stars += 1
    db.session.commit()

    return jsonify({
        'success': True,
        'stars': char.stars,
        'soul_power': char.soul_power,
        'cost': 1,
    })


@app.route('/api/equip_skills', methods=['POST'])
@login_required
def api_equip_skills():
    """装备技能API——最多4个主动技能（关系表存储）"""
    player = current_user
    data = request.get_json(force=True)
    instance_id = data.get('instance_id')
    skill_ids = data.get('skill_ids', [])

    if not instance_id:
        return jsonify({'success': False, 'error': '缺少角色ID'})

    char_inst = PlayerCharacter.query.get(instance_id)
    if not char_inst or char_inst.player_id != player.id:
        return jsonify({'success': False, 'error': '角色不存在'})

    if not isinstance(skill_ids, list):
        return jsonify({'success': False, 'error': '技能列表格式错误'})

    MAX_EQUIP = 4
    skill_ids = skill_ids[:MAX_EQUIP]

    template = get_character_by_id(char_inst.character_id)
    if template:
        all_skills = get_skills_for_character(
            template['id'], char_inst.level,
            template.get('rarity', 'common'),
            template.get('role_type', 'warrior'),
            template.get('element', 'earth'),
        )
        valid_ids = set(s['id'] for s in all_skills
                        if not s.get('is_passive') and s.get('type') != 'passive'
                        and not s.get('is_awakening'))
        skill_ids = [sid for sid in skill_ids if sid in valid_ids]

    CharacterEquippedSkill.query.filter_by(character_instance_id=instance_id).delete()
    for slot, sid in enumerate(skill_ids, 1):
        db.session.add(CharacterEquippedSkill(
            player_id=player.id,
            character_instance_id=instance_id,
            skill_id=sid,
            slot=slot,
        ))
    db.session.commit()

    return jsonify({'success': True, 'equipped': skill_ids})


@app.route('/api/levelup', methods=['POST'])
@login_required
def api_levelup():
    """升级角色API"""
    player = current_user
    data = request.get_json()
    instance_id = data.get('instance_id')
    exp_amount = data.get('exp', 100)
    
    char = PlayerCharacter.query.get_or_404(instance_id)
    if char.player_id != player.id:
        return jsonify({'success': False, 'error': '无权操作'}), 403
    
    if player.exp_books < exp_amount:
        return jsonify({'success': False, 'error': '经验书不足'}), 400
    
    player.exp_books -= exp_amount
    char.exp += exp_amount
    
    old_level = char.level

    # 计算升级
    exp_needed = int(100 * (1.15 ** (char.level - 1)))
    while char.exp >= exp_needed and char.level < 100:
        char.exp -= exp_needed
        char.level += 1
        exp_needed = int(100 * (1.15 ** (char.level - 1)))

    new_level = char.level

    # 检测新解锁的技能
    new_skills = []
    _tmpl = None
    if new_level > old_level:
        _tmpl = get_character_by_id(char.character_id)
        if _tmpl:
            rarity = _tmpl.get('rarity', 'common')
            role_type = _tmpl.get('role_type', 'warrior')
            element = _tmpl.get('element', 'earth')
            old_skills = get_skills_for_character(
                _tmpl['id'], old_level, rarity, role_type, element)
            cur_skills = get_skills_for_character(
                _tmpl['id'], new_level, rarity, role_type, element)
            old_ids = set(s['id'] for s in old_skills)
            for s in cur_skills:
                if s['id'] not in old_ids and not s.get('is_passive') and s.get('type') != 'passive':
                    new_skills.append(s)

    # 更新每日任务
    task = PlayerDailyTask.query.filter_by(
        player_id=player.id,
        task_id='daily-levelup',
        task_date=date.today()
    ).first()
    if task:
        task.progress += 1
        if task.progress >= task.target:
            task.completed = True

    _sync_seven_day_by_event(player, 'levelup')

    # 强化角色给玩家经验：每消耗100经验书=10玩家经验
    player_exp_gain = max(5, exp_amount // 10)
    lvl_result = grant_player_exp(player, player_exp_gain, source='levelup')
    
    db.session.commit()
    
    resp = {
        'success': True,
        'new_level': char.level,
        'exp': char.exp,
        'player_exp_gained': player_exp_gain,
        'player_level_up': lvl_result['level_ups'] > 0,
        'player_new_level': player.level,
        'new_skills': new_skills,
    }
    if new_skills and _tmpl:
        all_sk = get_skills_for_character(
            _tmpl['id'], new_level,
            _tmpl.get('rarity', 'common'),
            _tmpl.get('role_type', 'warrior'),
            _tmpl.get('element', 'earth'))
        resp['all_skills'] = all_sk
        equip_rows = CharacterEquippedSkill.query.filter_by(
            character_instance_id=char.id
        ).order_by(CharacterEquippedSkill.slot).all()
        resp['equipped_skill_ids'] = [r.skill_id for r in equip_rows]
    return jsonify(resp)


@app.route('/api/breakthrough', methods=['POST'])
@login_required
def api_breakthrough():
    """突破角色API"""
    player = current_user
    data = request.get_json()
    instance_id = data.get('instance_id')
    
    char = PlayerCharacter.query.get_or_404(instance_id)
    if char.player_id != player.id:
        return jsonify({'success': False, 'error': '无权操作'}), 403
    
    if char.breakthrough >= 5:
        return jsonify({'success': False, 'error': '已达最大突破次数'}), 400
    
    cost = (char.breakthrough + 1) * 1000
    if player.gold < cost:
        return jsonify({'success': False, 'error': '金币不足'}), 400
    
    player.gold -= cost
    char.breakthrough += 1
    
    _sync_seven_day_by_event(player, 'breakthrough')
    db.session.commit()
    
    return jsonify({
        'success': True,
        'breakthrough': char.breakthrough
    })


@app.route('/api/team', methods=['POST'])
@login_required
def api_team():
    """设置队伍API"""
    player = current_user
    data = request.get_json()
    team_ids = data.get('team', [])  # [instance_id, ...]
    
    # 删除旧队伍
    PlayerTeam.query.filter_by(player_id=player.id).delete()
    
    # 创建新队伍
    for slot, instance_id in enumerate(team_ids[:4]):
        if instance_id:
            team_member = PlayerTeam(
                player_id=player.id,
                player_uid=player.uid,
                slot=slot,
                character_instance_id=instance_id
            )
            db.session.add(team_member)
    
    _sync_seven_day_by_event(player, 'team_set')
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/battle/complete', methods=['POST'])
@login_required
def api_battle_complete():
    """完成战斗API"""
    player = current_user
    data = request.get_json()
    stage_id = data.get('stage_id')
    victory = data.get('victory', False)
    turns = data.get('turns', 0)  # 战斗回合数
    casualties = data.get('casualties', 0)  # 阵亡人数
    
    stage = get_stage_by_id(stage_id)
    if not stage:
        return jsonify({'success': False, 'error': '关卡不存在'}), 404
    
    # 消耗体力
    if player.energy < stage['energy_cost']:
        return jsonify({'success': False, 'error': '体力不足'}), 400
    
    player.energy -= stage['energy_cost']
    
    if victory:
        # 发放奖励
        rewards = stage['rewards']
        player.gold += rewards.get('gold', 0)
        if rewards.get('gems'):
            player.gems += rewards['gems']
        if rewards.get('exp_books'):
            player.exp_books = (player.exp_books or 0) + rewards['exp_books']
        if rewards.get('breakthrough_stone'):
            player.breakthrough_stone = (player.breakthrough_stone or 0) + rewards['breakthrough_stone']
        
        # 发放玩家经验 + 自动升级
        exp_gained = rewards.get('exp', 0)
        lvl_result = grant_player_exp(player, exp_gained, source='battle')
        
        # 计算星级
        # 1星：通关
        # 2星：无人阵亡
        # 3星：5回合内通关 + 无人阵亡
        stars = 1
        if casualties == 0:
            stars = 2
        if casualties == 0 and turns <= 5:
            stars = 3
        
        # 记录通关
        existing = PlayerCompletedStage.query.filter_by(
            player_id=player.id,
            stage_id=stage_id
        ).first()
        
        if existing:
            # 更新最高星级
            existing.stars = max(existing.stars, stars)
        else:
            completed = PlayerCompletedStage(
                player_id=player.id,
                player_uid=player.uid,
                stage_id=stage_id,
                stars=stars
            )
            db.session.add(completed)
            
            # 首次通关奖励
            first_rewards = stage.get('first_clear_rewards', {})
            player.gold += first_rewards.get('gold', 0)
            if first_rewards.get('gems'):
                player.gems += first_rewards['gems']
        
        # 更新每日任务
        task = PlayerDailyTask.query.filter_by(
            player_id=player.id,
            task_id='daily-battle',
            task_date=date.today()
        ).first()
        if task:
            task.progress += 1
            if task.progress >= task.target:
                task.completed = True

        player.total_battle_count = (player.total_battle_count or 0) + 1
        _sync_seven_day_by_event(player, 'battle', {'victory': True})
        sync_main_quests(player, 'battle', event_param=stage_id)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'victory': victory,
        'rewards': stage['rewards'] if victory else None,
        'stars': stars if victory else 0,
        'level_up': lvl_result['level_ups'] > 0 if victory else False,
        'level_ups': lvl_result['level_ups'] if victory else 0,
        'new_level': player.level,
        'level_rewards': lvl_result['level_rewards'] if victory else []
    })


@app.route('/api/sweep', methods=['POST'])
@login_required
def api_sweep():
    """扫荡已通关关卡API"""
    player = current_user
    data = request.get_json()
    stage_id = data.get('stage_id')
    
    stage = get_stage_by_id(stage_id)
    if not stage:
        return jsonify({'success': False, 'error': '关卡不存在'}), 404
    
    # 检查是否已通关
    completed = PlayerCompletedStage.query.filter_by(
        player_id=player.id,
        stage_id=stage_id
    ).first()
    
    if not completed:
        return jsonify({'success': False, 'error': '未通关该关卡，无法扫荡'}), 400

    # 满星解锁扫荡：需达到 3 星
    if (completed.stars or 0) < 3:
        return jsonify({'success': False, 'error': '扫荡需该关卡满星（3★）'}), 400
    
    # 检查体力
    if player.energy < stage['energy_cost']:
        return jsonify({'success': False, 'error': '体力不足'}), 400
    
    # 消耗体力
    player.energy -= stage['energy_cost']
    
    # 发放奖励（与战斗相同）
    rewards = stage['rewards']
    player.gold += rewards.get('gold', 0)
    if rewards.get('gems'):
        player.gems += rewards['gems']
    if rewards.get('exp_books'):
        player.exp_books = (player.exp_books or 0) + rewards['exp_books']
    if rewards.get('breakthrough_stone'):
        player.breakthrough_stone = (player.breakthrough_stone or 0) + rewards['breakthrough_stone']
    grant_player_exp(player, rewards.get('exp', 0), source='sweep')
    
    # 更新每日任务
    task = PlayerDailyTask.query.filter_by(
        player_id=player.id,
        task_id='daily-battle',
        task_date=date.today()
    ).first()
    if task:
        task.progress += 1
        if task.progress >= task.target:
            task.completed = True

    # 七日目标：扫荡等同于胜利完成战斗（计入累计）
    _sync_seven_day_by_event(player, 'battle', {'victory': True})
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'rewards': rewards
    })


@app.route('/api/daily/claim', methods=['POST'])
@login_required
def api_daily_claim():
    """领取每日任务奖励API"""
    player = current_user
    data = request.get_json()
    task_id = data.get('task_id')
    
    task = PlayerDailyTask.query.filter_by(
        player_id=player.id,
        task_id=task_id,
        task_date=date.today()
    ).first()
    
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    if not task.completed:
        return jsonify({'success': False, 'error': '任务未完成'}), 400
    
    if task.claimed:
        return jsonify({'success': False, 'error': '已领取'}), 400
    
    # 发放奖励
    player.gold += task.reward_gold or 0
    player.gems += task.reward_gems or 0
    exp_reward = task.reward_exp or 0
    lvl_result = grant_player_exp(player, exp_reward, source='daily_task')
    task.claimed = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'rewards': {
            'gold': task.reward_gold or 0,
            'gems': task.reward_gems or 0,
            'exp': exp_reward
        },
        'level_up': lvl_result['level_ups'] > 0,
        'new_level': player.level
    })


@app.route('/api/favorites/toggle', methods=['POST'])
@login_required
def api_favorites_toggle():
    """常用角色：切换收藏（最多 6 个，可为空）"""
    player = current_user
    data = request.get_json(silent=True) or {}
    instance_id = data.get('instance_id')
    try:
        instance_id = int(instance_id)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400

    ci = PlayerCharacter.query.get(instance_id)
    if not ci or ci.player_id != player.id:
        return jsonify({'success': False, 'error': '角色不存在'}), 404

    existing = PlayerFavoriteCharacter.query.filter_by(player_id=player.id, character_instance_id=instance_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'favorited': False})

    if player.favorites.count() >= 6:
        return jsonify({'success': False, 'error': '常用角色最多 6 个'}), 400

    slot = _next_favorite_slot(player, 6)
    if slot is None:
        return jsonify({'success': False, 'error': '常用角色已满'}), 400

    fav = PlayerFavoriteCharacter(player_id=player.id, player_uid=player.uid, character_instance_id=instance_id, slot=slot)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'success': True, 'favorited': True, 'slot': slot})


@app.route('/api/favorites/set', methods=['POST'])
@login_required
def api_favorites_set():
    """常用角色槽位：设置/清空（固定 5 个槽位，可为空，不可重复）"""
    player = current_user
    data = request.get_json(silent=True) or {}
    slot = data.get('slot')
    instance_id = data.get('instance_id', None)

    try:
        slot = int(slot)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400

    if slot < 1 or slot > 5:
        return jsonify({'success': False, 'error': '槽位范围为 1-5'}), 400

    # 清空槽位
    if instance_id in (None, '', 0, '0'):
        existing_slot = PlayerFavoriteCharacter.query.filter_by(player_id=player.id, slot=slot).first()
        if existing_slot:
            db.session.delete(existing_slot)
            db.session.commit()
        return jsonify({'success': True, 'cleared': True, 'slot': slot})

    try:
        instance_id = int(instance_id)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400

    ci = PlayerCharacter.query.get(instance_id)
    if not ci or ci.player_id != player.id:
        return jsonify({'success': False, 'error': '角色不存在'}), 404

    # 不允许重复：该角色是否已被其它槽位使用
    dup = PlayerFavoriteCharacter.query.filter_by(player_id=player.id, character_instance_id=instance_id).first()
    if dup and dup.slot != slot:
        return jsonify({'success': False, 'error': '该角色已放在其它槽位'}), 400

    # 如果槽位已有角色，替换之
    existing_slot = PlayerFavoriteCharacter.query.filter_by(player_id=player.id, slot=slot).first()
    if existing_slot:
        existing_slot.character_instance_id = instance_id
    else:
        db.session.add(PlayerFavoriteCharacter(player_id=player.id, player_uid=player.uid, character_instance_id=instance_id, slot=slot))
    db.session.commit()
    return jsonify({'success': True, 'slot': slot, 'instance_id': instance_id})


@app.route('/api/characters/owned', methods=['GET'])
@login_required
def api_characters_owned():
    """返回玩家已拥有角色列表（用于常用角色选择器）"""
    player = current_user
    items = []
    for ci in player.characters.order_by(PlayerCharacter.id.asc()).all():
        tpl = get_character_by_id(ci.character_id)
        if not tpl:
            continue
        # 优先使用原画 illustration，其次 avatar
        art = tpl.get('illustration') or tpl.get('avatar')
        items.append({
            'instance_id': ci.id,
            'character_id': ci.character_id,
            'name': tpl.get('name') or ci.character_id,
            'level': ci.level,
            'rarity': tpl.get('rarity'),
            'art': art,
            'avatar': tpl.get('avatar'),
        })
    return jsonify({'success': True, 'characters': items})


@app.route('/api/favorites/list', methods=['GET'])
@login_required
def api_favorites_list():
    """返回常用角色 instance_id 列表（按 slot 排序）"""
    player = current_user
    favs = PlayerFavoriteCharacter.query.filter_by(player_id=player.id).order_by(PlayerFavoriteCharacter.slot.asc()).all()
    return jsonify({
        'success': True,
        'favorites': [{'instance_id': f.character_instance_id, 'slot': f.slot} for f in favs]
    })


# ==================== 公告系统API ====================

@app.route('/api/announcements')
@login_required
def api_announcements():
    """获取公告列表"""
    now = datetime.now()
    
    announcements = Announcement.query.filter(
        Announcement.is_active == True,
        Announcement.start_time <= now,
        (Announcement.end_time == None) | (Announcement.end_time > now)
    ).order_by(Announcement.priority.desc(), Announcement.created_at.desc()).limit(10).all()
    
    return jsonify({
        'success': True,
        'announcements': [a.to_dict() for a in announcements]
    })


@app.route('/api/announcements/login')
@login_required
def api_login_announcements():
    """获取登录时显示的公告"""
    now = datetime.now()
    
    announcements = Announcement.query.filter(
        Announcement.is_active == True,
        Announcement.show_on_login == True,
        Announcement.start_time <= now,
        (Announcement.end_time == None) | (Announcement.end_time > now)
    ).order_by(Announcement.priority.desc(), Announcement.created_at.desc()).limit(5).all()
    
    return jsonify({
        'success': True,
        'announcements': [a.to_dict() for a in announcements]
    })


# ==================== 主线任务API ====================

@app.route('/api/main-quests', methods=['GET'])
@login_required
def api_main_quests():
    """获取主线任务列表"""
    player = current_user
    existing = PlayerMainQuest.query.filter_by(player_id=player.id).count()
    if existing == 0:
        create_main_quests(player)
    sync_main_quests(player, 'check')

    records = PlayerMainQuest.query.filter_by(player_id=player.id).all()
    rec_map = {r.quest_id: r for r in records}

    result = []
    for cfg in MAIN_QUESTS:
        rec = rec_map.get(cfg['id'])
        result.append({
            **cfg,
            'progress': rec.progress if rec else 0,
            'completed': rec.completed if rec else False,
            'claimed': rec.claimed if rec else False,
        })
    return jsonify({'success': True, 'quests': result})


@app.route('/api/main-quests/claim', methods=['POST'])
@login_required
def api_main_quest_claim():
    """领取主线任务奖励"""
    player = current_user
    data = request.get_json(silent=True) or {}
    quest_id = data.get('quest_id')
    if not quest_id:
        return jsonify({'success': False, 'error': '缺少 quest_id'}), 400

    mq = PlayerMainQuest.query.filter_by(player_id=player.id, quest_id=quest_id).first()
    if not mq:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    if not mq.completed:
        return jsonify({'success': False, 'error': '任务未完成'}), 400
    if mq.claimed:
        return jsonify({'success': False, 'error': '已领取'}), 400

    cfg = next((q for q in MAIN_QUESTS if q['id'] == quest_id), None)
    if not cfg:
        return jsonify({'success': False, 'error': '任务配置不存在'}), 404

    player.gold += cfg.get('reward_gold', 0)
    player.gems += cfg.get('reward_gems', 0)
    quest_exp = cfg.get('reward_exp', 0)
    if quest_exp <= 0:
        quest_exp = 30 + cfg.get('reward_gold', 0) // 20
    lvl_result = grant_player_exp(player, quest_exp, source='main_quest')
    mq.claimed = True
    db.session.commit()

    return jsonify({
        'success': True,
        'rewards': {
            'gold': cfg.get('reward_gold', 0),
            'gems': cfg.get('reward_gems', 0),
            'exp': quest_exp,
        },
        'level_up': lvl_result['level_ups'] > 0,
        'new_level': player.level
    })


# ==================== 商店API ====================

@app.route('/api/shop/buy', methods=['POST'])
@login_required
def api_shop_buy():
    """商店购买"""
    player = current_user
    data = request.get_json(silent=True) or {}
    item_id = data.get('item_id')
    if not item_id:
        return jsonify({'success': False, 'error': '缺少 item_id'}), 400

    item_cfg = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
    if not item_cfg:
        return jsonify({'success': False, 'error': '商品不存在'}), 404

    today = date.today()
    purchase = ShopPurchase.query.filter_by(
        player_id=player.id, item_id=item_id, purchase_date=today
    ).first()
    bought_today = purchase.count if purchase else 0

    if bought_today >= item_cfg.get('daily_limit', 99):
        return jsonify({'success': False, 'error': '今日购买已达上限'}), 400

    price_type = item_cfg['price_type']
    price = item_cfg['price']
    if price_type == 'gold':
        if player.gold < price:
            return jsonify({'success': False, 'error': '金币不足'}), 400
        player.gold -= price
    elif price_type == 'gems':
        if player.gems < price:
            return jsonify({'success': False, 'error': '钻石不足'}), 400
        player.gems -= price
    else:
        return jsonify({'success': False, 'error': '未知货币类型'}), 400

    reward_type = item_cfg['reward_type']
    reward_amount = item_cfg['reward_amount']
    if reward_type == 'star_soul':
        return jsonify({'success': False, 'error': '该道具已弃用：星魂体系改为“重复角色→角色魂力”'}), 400
    if reward_type == 'gold':
        player.gold += reward_amount
    elif reward_type == 'gems':
        player.gems += reward_amount
    elif reward_type == 'exp_books':
        player.exp_books += reward_amount
    elif reward_type == 'summon_tickets':
        player.summon_tickets += reward_amount
    elif reward_type == 'energy':
        player.energy += reward_amount

    if purchase:
        purchase.count += 1
    else:
        purchase = ShopPurchase(player_id=player.id, player_uid=player.uid, item_id=item_id, purchase_date=today, count=1)
        db.session.add(purchase)

    db.session.commit()
    return jsonify({
        'success': True,
        'reward_type': reward_type,
        'reward_amount': reward_amount,
        'gold': player.gold,
        'gems': player.gems,
        'exp_books': player.exp_books,
        'summon_tickets': player.summon_tickets,
        'energy': player.energy,
    })


# ==================== 竞技场API ====================

@app.route('/api/arena/challenge', methods=['POST'])
@login_required
def api_arena_challenge():
    """竞技场挑战"""
    player = current_user
    data = request.get_json(silent=True) or {}
    bot_index = data.get('bot_index')
    try:
        bot_index = int(bot_index)
    except Exception:
        return jsonify({'success': False, 'error': '参数错误'}), 400

    if bot_index < 0 or bot_index >= len(ARENA_BOTS):
        return jsonify({'success': False, 'error': '对手不存在'}), 404

    bot = ARENA_BOTS[bot_index]

    max_lvl_row = db.session.execute(
        text("SELECT MAX(level) FROM player_characters WHERE player_id = :pid"),
        {'pid': player.id}
    ).scalar()
    player_max_lvl = int(max_lvl_row or 1)

    level_diff = player_max_lvl - bot['level']
    base_rate = 0.6
    win_rate = max(0.3, min(0.9, base_rate + level_diff * 0.02))
    victory = random.random() < win_rate

    if victory:
        score_change = random.randint(10, 25)
        player.arena_score = (player.arena_score or 1000) + score_change
        player.arena_wins = (player.arena_wins or 0) + 1
    else:
        score_change = -random.randint(5, 15)
        player.arena_score = max(0, (player.arena_score or 1000) + score_change)
        player.arena_losses = (player.arena_losses or 0) + 1

    record = ArenaRecord(
        player_id=player.id,
        player_uid=player.uid,
        opponent_name=bot['name'],
        opponent_score=bot['rank_score'],
        victory=victory,
        score_change=score_change,
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'success': True,
        'victory': victory,
        'score_change': score_change,
        'arena_score': player.arena_score,
        'arena_wins': player.arena_wins,
        'arena_losses': player.arena_losses,
    })


# ==================== 七日目标系统 ====================


def create_seven_day_goals(player):
    """创建七日目标"""
    for goal_data in DEFAULT_SEVEN_DAY_GOALS:
        existing = SevenDayGoal.query.filter_by(
            player_id=player.id,
            goal_id=goal_data['goal_id']
        ).first()
        
        if not existing:
            goal = SevenDayGoal(
                player_id=player.id,
                player_uid=player.uid,
                day=goal_data['day'],
                goal_id=goal_data['goal_id'],
                name=goal_data['name'],
                description=goal_data['description'],
                target=goal_data['target'],
                reward_gold=goal_data.get('reward_gold', 0),
                reward_gems=goal_data.get('reward_gems', 0),
            )
            db.session.add(goal)
    db.session.commit()


@app.route('/api/seven-day-goals')
@login_required
def api_seven_day_goals():
    """获取七日目标"""
    player = current_user
    
    # 确保七日目标已创建
    goals_count = SevenDayGoal.query.filter_by(player_id=player.id).count()
    if goals_count == 0:
        create_seven_day_goals(player)
    
    # 获取当前天数（从首次登录开始计算）
    day_played = min(7, player.total_play_days)
    
    goals = SevenDayGoal.query.filter_by(player_id=player.id).order_by(SevenDayGoal.day, SevenDayGoal.id).all()
    
    # 按天分组
    goals_by_day = {}
    for goal in goals:
        if goal.day not in goals_by_day:
            goals_by_day[goal.day] = []
        goals_by_day[goal.day].append(goal.to_dict())
    
    return jsonify({
        'success': True,
        'current_day': day_played,
        'goals_by_day': goals_by_day
    })


@app.route('/api/seven-day-goals/claim', methods=['POST'])
@login_required
def api_seven_day_claim():
    """领取七日目标奖励"""
    player = current_user
    data = request.get_json()
    goal_id = data.get('goal_id')
    
    goal = SevenDayGoal.query.filter_by(
        player_id=player.id,
        goal_id=goal_id
    ).first()
    
    if not goal:
        return jsonify({'success': False, 'error': '目标不存在'}), 404
    
    if not goal.completed:
        return jsonify({'success': False, 'error': '目标未完成'}), 400
    
    if goal.claimed:
        return jsonify({'success': False, 'error': '已领取'}), 400
    
    # 发放奖励
    player.gold += goal.reward_gold or 0
    player.gems += goal.reward_gems or 0
    # 七日目标额外给经验：与金币奖励等比
    goal_exp = max(20, (goal.reward_gold or 0) // 10)
    lvl_result = grant_player_exp(player, goal_exp, source='seven_day')
    goal.claimed = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'rewards': {
            'gold': goal.reward_gold or 0,
            'gems': goal.reward_gems or 0,
            'exp': goal_exp
        },
        'level_up': lvl_result['level_ups'] > 0,
        'new_level': player.level
    })


@app.route('/api/player/avatar', methods=['POST'])
@login_required
def api_update_avatar():
    """更新玩家头像"""
    player = current_user
    data = request.get_json()
    avatar = data.get('avatar', '').strip()
    
    if not avatar:
        return jsonify({'success': False, 'error': '头像不能为空'}), 400
    
    # 验证头像路径是否合法（只允许选择预设头像）
    valid_prefix = '/static/images/avatars/avatar_'
    if not avatar.startswith(valid_prefix):
        return jsonify({'success': False, 'error': '无效的头像路径'}), 400
    
    # 更新头像
    player.avatar = avatar
    db.session.commit()
    
    return jsonify({
        'success': True,
        'avatar': avatar
    })


# ==================== 初始化数据库 ====================

@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成！')


with app.app_context():
    ensure_db_migrations()
    seed_announcements()
    from skill_data import seed_skill_templates
    from models import SkillTemplate
    _need_reseed = db.session.query(SkillTemplate).filter(
        SkillTemplate.element == 'ice'
    ).first() is None
    n = seed_skill_templates(db.session, force=_need_reseed)
    if n:
        print(f"[INFO] Seeded {n} skill templates into DB (reseed={_need_reseed})")


if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    app.run(host=host, port=port, debug=True)
