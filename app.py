"""
历史英雄对决 - Flask 主应用
"""
import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random

from config import config
from models import db, Player, PlayerCharacter, PlayerTeam, PlayerCompletedStage, PlayerDailyTask, SummonHistory
from game_data import (
    ALL_CHARACTERS, CHAPTERS, RARITY_NAMES, RARITY_COLORS, RARITY_WEIGHTS,
    ELEMENT_NAMES, ELEMENT_COLORS, ROLE_NAMES, DIFFICULTY_NAMES, DIFFICULTY_COLORS,
    DEFAULT_DAILY_TASKS, get_character_by_id, get_characters_by_rarity,
    get_stage_by_id, calculate_stats
)

# 创建应用
app = Flask(__name__)
app.config.from_object(config['default'])

# 初始化数据库
db.init_app(app)

# 初始化登录管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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
            login_user(player)
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
        
        if len(password) < 6:
            flash('密码长度至少6个字符', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
        
        # 检查用户名是否已存在
        if Player.query.filter_by(username=username).first():
            flash('用户名已被使用', 'error')
            return render_template('register.html')
        
        # 检查邮箱是否已存在
        if email and Player.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html')
        
        # 创建新玩家
        player = Player(
            username=username,
            email=email if email else None,
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
    
    return render_template('index.html',
        player=player,
        characters=characters,
        team=team,
        daily_tasks=daily_tasks,
        rarity_names=RARITY_NAMES,
        rarity_colors=RARITY_COLORS,
        element_names=ELEMENT_NAMES,
        element_colors=ELEMENT_COLORS
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
    
    return render_template('character_detail.html',
        player=player,
        character=battle_char,
        is_in_team=is_in_team,
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
        rarity_colors=RARITY_COLORS
    )


@app.route('/stages')
@login_required
def stages():
    """副本页面"""
    player = current_user
    
    # 获取已通关关卡
    completed = [s.stage_id for s in player.completed_stages]
    
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
        
        # 随机选择角色
        characters = get_characters_by_rarity(rarity)
        if not characters:
            characters = ALL_CHARACTERS
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
        
        # 记录通关
        existing = PlayerCompletedStage.query.filter_by(
            player_id=player.id,
            stage_id=stage_id
        ).first()
        
        if not existing:
            completed = PlayerCompletedStage(
                player_id=player.id,
                stage_id=stage_id
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
        'rewards': stage['rewards'] if victory else None
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


# ==================== 初始化数据库 ====================

@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成！')


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
