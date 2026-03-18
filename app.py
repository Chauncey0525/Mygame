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
from models import db, Player, PlayerCharacter, PlayerTeam, PlayerCompletedStage, PlayerDailyTask, SummonHistory, SmsVerification, CharacterTemplate, Announcement, SevenDayGoal
from game_data import (
    CHAPTERS, RARITY_NAMES, RARITY_COLORS, RARITY_WEIGHTS,
    ELEMENT_NAMES, ELEMENT_COLORS, ROLE_NAMES, DIFFICULTY_NAMES, DIFFICULTY_COLORS,
    DEFAULT_DAILY_TASKS, get_character_by_id, get_characters_by_rarity,
    get_all_characters, get_stage_by_id, calculate_stats,
    CURRENT_UP_CHARACTERS, UP_RATE_MULTIPLIER
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


def ensure_db_migrations():
    """
    轻量迁移（避免引入 Alembic）：
    - 为 players 增加 phone 列（如不存在）
    - 创建 sms_verifications 表（由 create_all 处理）
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
    except Exception as e:
        # 不阻塞应用启动，但会影响 phone 字段写入；打印出来便于排查
        print("[WARN] ensure_db_migrations failed:", type(e).__name__, str(e))


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


@login_manager.user_loader
def load_user(player_id):
    return Player.query.get(int(player_id))


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
            flash(f'欢迎回来，{player.name}！', 'success')
            
            # 更新登录信息
            check_daily_reset(player)
            
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
            name=player_name if player_name else username
        )
        player.set_password(password)
        
        db.session.add(player)
        db.session.commit()
        
        # 创建每日任务
        create_daily_tasks(player)
        
        # 自动登录
        login_user(player)
        flash(f'注册成功！欢迎，{player.name}！', 'success')
        
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


def get_battle_character(character_instance):
    """获取战斗用角色数据"""
    template = get_character_by_id(character_instance.character_id)
    if not template:
        return None
    
    stats = calculate_stats(
        template['stats'],
        character_instance.level,
        character_instance.stars,
        character_instance.breakthrough
    )
    
    return {
        'id': character_instance.id,
        'character_id': template['id'],
        'name': template['name'],
        'title': template['title'],
        'element': template['element'],
        'role_type': template['role_type'],
        'avatar': template['avatar'],
        'rarity': template['rarity'],
        'level': character_instance.level,
        'stars': character_instance.stars,
        'stats': stats,
        'current_stats': stats.copy(),
        'skills': template['skills']
    }


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
    
    return render_template('index.html',
        player=player,
        characters=characters,
        team=team,
        daily_tasks=daily_tasks,
        all_character_templates=all_character_templates,
        owned_character_ids=owned_character_ids,
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
    
    # 获取所有角色
    all_chars = []
    for char in player.characters:
        battle_char = get_battle_character(char)
        if battle_char:
            battle_char['instance_id'] = char.id
            battle_char['breakthrough'] = char.breakthrough
            all_chars.append(battle_char)
    
    # 按稀有度排序
    rarity_order = {'legendary': 0, 'epic': 1, 'rare': 2, 'common': 3}
    all_chars.sort(key=lambda x: rarity_order.get(x['rarity'], 3))
    
    return render_template('characters.html',
        player=player,
        characters=all_chars,
        team_ids=[t.character_instance_id for t in player.team],
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
    
    return render_template('character_detail.html',
        player=player,
        character=battle_char,
        is_in_team=is_in_team,
        team_ids=team_ids,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        role_names=ROLE_NAMES
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
        RARITY_COLORS=RARITY_COLORS
    )


@app.route('/research')
@login_required
def research():
    """研究所页面"""
    return render_template('research.html')


@app.route('/shop')
@login_required
def shop():
    """商会页面"""
    return render_template('shop.html')


@app.route('/inventory')
@login_required
def inventory():
    """仓库页面"""
    return render_template('inventory.html')


@app.route('/arena')
@login_required
def arena():
    """竞技场页面"""
    return render_template('arena.html')


@app.route('/stages')
@login_required
def stages():
    """副本页面"""
    player = current_user
    
    # 获取已通关关卡
    completed = [s.stage_id for s in player.completed_stages]
    
    # 获取关卡星级
    stage_stars = {}
    for s in player.completed_stages:
        stage_stars[s.stage_id] = s.stars if hasattr(s, 'stars') else 1
    
    # 获取队伍
    team = []
    for team_member in player.team:
        char_instance = PlayerCharacter.query.get(team_member.character_instance_id)
        if char_instance:
            battle_char = get_battle_character(char_instance)
            if battle_char:
                team.append(battle_char)
    
    return render_template('stages.html',
        player=player,
        chapters=CHAPTERS,
        completed_stages=completed,
        stage_stars=stage_stars,
        team=team,
        difficulty_names=DIFFICULTY_NAMES,
        difficulty_colors=DIFFICULTY_COLORS,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS,
        get_character_by_id=get_character_by_id
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
    
    # 获取队伍
    team = []
    for team_member in player.team:
        char_instance = PlayerCharacter.query.get(team_member.character_instance_id)
        if char_instance:
            battle_char = get_battle_character(char_instance)
            if battle_char:
                team.append(battle_char)
    
    if not team:
        flash('请先设置队伍', 'error')
        return redirect(url_for('stages'))
    
    # 生成敌人
    enemies = []
    for i, enemy_id in enumerate(stage['enemy_ids']):
        template = get_character_by_id(enemy_id)
        if template:
            level = stage['enemy_levels'][i] if i < len(stage['enemy_levels']) else 1
            stats = calculate_stats(template['stats'], level, 1, 0)
            enemies.append({
                'id': f'enemy-{i}',
                'character_id': template['id'],
                'name': template['name'],
                'element': template['element'],
                'avatar': template['avatar'],
                'level': level,
                'stats': stats,
                'current_stats': stats.copy(),
                'skills': template['skills']
            })
    
    return render_template('battle.html',
        player=player,
        stage=stage,
        team=team,
        enemies=enemies,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS
    )


# ==================== API 路由 ====================

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
            return jsonify({'success': False, 'error': '钻石不足'})
        player.gems -= 100
    elif summon_type == 'ten':
        if player.gems < 900:
            return jsonify({'success': False, 'error': '钻石不足'})
        player.gems -= 900
    elif summon_type == 'ticket':
        if player.summon_tickets < 1:
            return jsonify({'success': False, 'error': '召唤券不足'})
        player.summon_tickets -= 1
    else:
        return jsonify({'success': False, 'error': '无效的召唤类型'})
    
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
            # 增加星级
            existing.stars = min(6, existing.stars + 1)
            is_new = False
            instance_id = existing.id
        else:
            # 创建新角色
            new_char = PlayerCharacter(
                player_id=player.id,
                character_id=char_template['id'],
                stars=2 if rarity == 'legendary' else (1 if rarity == 'epic' else 1)
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
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'results': results,
        'pity': player.pity_count,
        'legendary_pity': player.legendary_pity_count
    })


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
        return jsonify({'success': False, 'error': '无权操作'})
    
    if player.exp_books < exp_amount:
        return jsonify({'success': False, 'error': '经验书不足'})
    
    player.exp_books -= exp_amount
    char.exp += exp_amount
    
    # 计算升级
    exp_needed = int(100 * (1.15 ** (char.level - 1)))
    while char.exp >= exp_needed and char.level < 100:
        char.exp -= exp_needed
        char.level += 1
        exp_needed = int(100 * (1.15 ** (char.level - 1)))
    
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
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_level': char.level,
        'exp': char.exp
    })


@app.route('/api/breakthrough', methods=['POST'])
@login_required
def api_breakthrough():
    """突破角色API"""
    player = current_user
    data = request.get_json()
    instance_id = data.get('instance_id')
    
    char = PlayerCharacter.query.get_or_404(instance_id)
    if char.player_id != player.id:
        return jsonify({'success': False, 'error': '无权操作'})
    
    if char.breakthrough >= 5:
        return jsonify({'success': False, 'error': '已达最大突破次数'})
    
    cost = (char.breakthrough + 1) * 1000
    if player.gold < cost:
        return jsonify({'success': False, 'error': '金币不足'})
    
    player.gold -= cost
    char.breakthrough += 1
    
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
                slot=slot,
                character_instance_id=instance_id
            )
            db.session.add(team_member)
    
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
        return jsonify({'success': False, 'error': '关卡不存在'})
    
    # 消耗体力
    if player.energy < stage['energy_cost']:
        return jsonify({'success': False, 'error': '体力不足'})
    
    player.energy -= stage['energy_cost']
    
    if victory:
        # 发放奖励
        rewards = stage['rewards']
        player.gold += rewards.get('gold', 0)
        player.exp += rewards.get('exp', 0)
        if rewards.get('gems'):
            player.gems += rewards['gems']
        
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
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'victory': victory,
        'rewards': stage['rewards'] if victory else None,
        'stars': stars if victory else 0
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
        return jsonify({'success': False, 'error': '关卡不存在'})
    
    # 检查是否已通关
    completed = PlayerCompletedStage.query.filter_by(
        player_id=player.id,
        stage_id=stage_id
    ).first()
    
    if not completed:
        return jsonify({'success': False, 'error': '未通关该关卡，无法扫荡'})
    
    # 检查体力
    if player.energy < stage['energy_cost']:
        return jsonify({'success': False, 'error': '体力不足'})
    
    # 消耗体力
    player.energy -= stage['energy_cost']
    
    # 发放奖励（与战斗相同）
    rewards = stage['rewards']
    player.gold += rewards.get('gold', 0)
    player.exp += rewards.get('exp', 0)
    if rewards.get('gems'):
        player.gems += rewards['gems']
    
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
        return jsonify({'success': False, 'error': '任务不存在'})
    
    if not task.completed:
        return jsonify({'success': False, 'error': '任务未完成'})
    
    if task.claimed:
        return jsonify({'success': False, 'error': '已领取'})
    
    # 发放奖励
    player.gold += task.reward_gold or 0
    player.gems += task.reward_gems or 0
    task.claimed = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'rewards': {
            'gold': task.reward_gold or 0,
            'gems': task.reward_gems or 0
        }
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


# ==================== 七日目标系统 ====================

DEFAULT_SEVEN_DAY_GOALS = [
    # Day 1
    {'day': 1, 'goal_id': 'day1-login', 'name': '初次登录', 'description': '登录游戏', 'target': 1, 'reward_gold': 500, 'reward_gems': 100},
    {'day': 1, 'goal_id': 'day1-summon', 'name': '首次召唤', 'description': '进行1次召唤', 'target': 1, 'reward_gold': 300, 'reward_gems': 50},
    {'day': 1, 'goal_id': 'day1-battle', 'name': '初战告捷', 'description': '完成1次战斗', 'target': 1, 'reward_gold': 400},
    # Day 2
    {'day': 2, 'goal_id': 'day2-levelup', 'name': '角色强化', 'description': '强化角色1次', 'target': 1, 'reward_gold': 500, 'reward_gems': 50},
    {'day': 2, 'goal_id': 'day2-battle3', 'name': '勇者之路', 'description': '完成3次战斗', 'target': 3, 'reward_gold': 600},
    {'day': 2, 'goal_id': 'day2-team', 'name': '组建队伍', 'description': '设置出战队伍', 'target': 1, 'reward_gold': 400, 'reward_gems': 50},
    # Day 3
    {'day': 3, 'goal_id': 'day3-summon5', 'name': '召唤大师', 'description': '累计召唤5次', 'target': 5, 'reward_gold': 800, 'reward_gems': 100},
    {'day': 3, 'goal_id': 'day3-stage5', 'name': '副本探索', 'description': '通关5个关卡', 'target': 5, 'reward_gold': 1000},
    {'day': 3, 'goal_id': 'day3-char3', 'name': '英雄集结', 'description': '拥有3名角色', 'target': 3, 'reward_gems': 150},
    # Day 4
    {'day': 4, 'goal_id': 'day4-level10', 'name': '实力提升', 'description': '任意角色达到10级', 'target': 1, 'reward_gold': 1000, 'reward_gems': 100},
    {'day': 4, 'goal_id': 'day4-breakthrough', 'name': '突破极限', 'description': '进行1次突破', 'target': 1, 'reward_gold': 800, 'reward_gems': 80},
    {'day': 4, 'goal_id': 'day4-battle10', 'name': '战斗狂人', 'description': '累计完成10次战斗', 'target': 10, 'reward_gold': 1200},
    # Day 5
    {'day': 5, 'goal_id': 'day5-chapter2', 'name': '章节推进', 'description': '通关第2章', 'target': 1, 'reward_gems': 200},
    {'day': 5, 'goal_id': 'day5-char5', 'name': '英雄团', 'description': '拥有5名角色', 'target': 5, 'reward_gems': 200},
    {'day': 5, 'goal_id': 'day5-summon10', 'name': '召唤专家', 'description': '累计召唤10次', 'target': 10, 'reward_gold': 1500, 'reward_gems': 150},
    # Day 6
    {'day': 6, 'goal_id': 'day6-level20', 'name': '精英养成', 'description': '任意角色达到20级', 'target': 1, 'reward_gold': 1500, 'reward_gems': 150},
    {'day': 6, 'goal_id': 'day6-epic', 'name': '史诗英雄', 'description': '获得1名史诗或传说角色', 'target': 1, 'reward_gems': 300},
    {'day': 6, 'goal_id': 'day6-stage20', 'name': '副本达人', 'description': '累计通关20个关卡', 'target': 20, 'reward_gold': 2000},
    # Day 7
    {'day': 7, 'goal_id': 'day7-chapter3', 'name': '传说之路', 'description': '通关第3章', 'target': 1, 'reward_gems': 500},
    {'day': 7, 'goal_id': 'day7-level30', 'name': '英雄成长', 'description': '任意角色达到30级', 'target': 1, 'reward_gold': 2000, 'reward_gems': 200},
    {'day': 7, 'goal_id': 'day7-complete', 'name': '七日毕业', 'description': '完成所有七日目标', 'target': 1, 'reward_gems': 500},
]


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
        return jsonify({'success': False, 'error': '目标不存在'})
    
    if not goal.completed:
        return jsonify({'success': False, 'error': '目标未完成'})
    
    if goal.claimed:
        return jsonify({'success': False, 'error': '已领取'})
    
    # 发放奖励
    player.gold += goal.reward_gold or 0
    player.gems += goal.reward_gems or 0
    goal.claimed = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'rewards': {
            'gold': goal.reward_gold or 0,
            'gems': goal.reward_gems or 0
        }
    })


# ==================== 初始化数据库 ====================

@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成！')


with app.app_context():
    ensure_db_migrations()


if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    app.run(host=host, port=port, debug=True)
