# ⚔️ 巅峰对决

> 一款以古今中外历史人物为背景的养成型回合制战斗游戏

## 📖 项目简介

《巅峰对决》是一款融合了角色收集、养成升级、副本挑战等核心玩法的回合制游戏。玩家可以召唤诸葛亮、关羽、花木兰、亚瑟王等历史名将，组建自己的队伍，挑战各种副本关卡。

### ✨ 核心功能

| 功能模块 | 说明 |
|---------|------|
| 🎭 **角色养成** | 升级、星魂（命座）、装备、符文、天赋 |
| ✨ **召唤系统** | 单抽、十连、保底机制、UP 池、首十连保底史诗 |
| ⚔️ **副本挑战** | 4 章 12 关、Boss 战、剧情对话、扫荡 |
| 📋 **任务中心** | 主线任务 16 条 + 每日任务 6 条 + 进度追踪 |
| 🎯 **队伍编辑** | 自由搭配 4 人队伍，策略战斗 |
| 🏪 **商会系统** | 金币/钻石购买资源、每日限购 |
| ⚔️ **竞技场** | 挑战机器人对手、积分排名、战斗记录 |
| 🎁 **新手福利** | 注册送资源、首十连保底、七日目标 |
| 📢 **公告系统** | 登录弹窗、公告列表、种子数据 |
| 🏆 **角色收集** | 14 位英雄（普通/稀有/史诗/传说） |
| 📚 **图鉴系统** | 角色图鉴 + 技能图鉴（筛选/预览） |
| 🔎 **预览界面** | 角色预览（不依赖拥有）+ 技能预览（结构化效果展示） |

---

## 📰 最近更新（自动生成）

<!-- AUTO-UPDATE-START -->
_最后生成时间：2026-03-19 12:02_

- `e4e92c5` (2026-03-18) feat: update battle and shop logic
- `f434058` (2026-03-18) feat: 升级解锁新技能时弹出技能更换提示
- `9fa9624` (2026-03-18) feat: 觉醒技能独立于4技能栏，每场战斗限用1次
- `f5b543d` (2026-03-18) refactor: 技能系统全面迁移到数据库存储
- `b996e8e` (2026-03-18) feat: 技能装备系统——17个技能中选择4个携带出战
- `90fb60c` (2026-03-18) feat: 元素技能池职业分支——同元素不同职业拥有不同技能
- `290e3b2` (2026-03-18) feat: 全新技能系统——品质成长 + 6元素共通技能 + 专属/觉醒/被动
- `b1764b7` (2026-03-18) fix: 修复回合制 bug——玩家可在同一回合多次行动
- `ed03bd4` (2026-03-18) feat: 战斗系统全面升级为 3D（Three.js Low-Poly 风格）
- `d5d37a2` (2026-03-18) feat: 所有玩家关联表添加 player_uid 字段，统一用 UID 作为数据统计唯一标识
- `d3c3251` (2026-03-18) fix: 修复经验养成系统 - 新手无法升级的死锁问题
- `add962b` (2026-03-18) merge: 合并远程副本体系重构与本地经验值升级系统
<!-- AUTO-UPDATE-END -->

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | Flask 3.0 |
| **ORM** | SQLAlchemy 3.1 |
| **数据库** | MySQL / SQLite |
| **前端模板** | Jinja2 |
| **样式** | CSS3 |
| **Python** | 3.8+（建议 3.11+） |

---

## 📦 安装部署

### 环境要求

- Python 3.8+（建议 3.11+）
- MySQL 8.0+ (可选，默认使用SQLite)

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/Chauncey0525/Mygame.git
cd Mygame

# 2. 创建虚拟环境
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows（PowerShell）
# .\venv\Scripts\Activate.ps1
# Windows（CMD）
# venv\Scripts\activate.bat

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务（推荐入口：run.py，默认端口 5000）
python run.py

# 5. 访问游戏
# 打开浏览器访问 http://localhost:5000
```

### 启动方式与端口说明

- **推荐**：`python run.py`（默认 `http://localhost:5000`）
- **也可以**：`python app.py`
  - 默认端口是 **5000**（可用环境变量覆盖：`PORT=xxxx python app.py`）

---

## 🧩 常见问题（FAQ）

### Windows 安装依赖时 `cryptography` 失败 / 提示需要 Rust

通常是 `pip` 过旧导致没装到预编译 wheel。按下面顺序执行即可：

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## 🐳 Docker 打包与运行

### 方式 A：Docker 直接运行

```bash
# 构建镜像
docker build -t mygame:latest .

# 运行（默认使用 SQLite，数据库文件在容器内 /app/instance/history_heroes.db）
docker run --rm -p 5000:5000 mygame:latest

# 访问
# http://localhost:5000
```

### 方式 B：docker compose（推荐）

```bash
# 启动（默认 SQLite，并把 ./instance 挂载到容器，保证数据持久化）
docker compose up --build

# 后台运行
docker compose up -d --build

# 停止
docker compose down
```

> 如果你要切到 MySQL：取消 `docker-compose.yml` 里 `db` 的注释，并在 `web.environment` 补齐 `MYSQL_HOST/MYSQL_USER/MYSQL_PASSWORD/MYSQL_DATABASE`，或直接设置 `DATABASE_URL`。

---

## 🤖 README 自动更新（提交前自动生成）

本仓库支持在 **每次提交前** 自动更新 README 的“最近更新（自动生成）”区块。

### 提交到 GitHub 前（必做）

- **必须保证 README 已更新**：每次准备提交/推送到 GitHub 前，都要确保“最近更新（自动生成）”区块是最新的（避免 README 与代码状态不一致）。
- **推荐做法**：安装并启用 `pre-commit`，让它在每次 `git commit` 前自动执行更新脚本。
- **兜底做法**：如果本机未启用 `pre-commit`，请在提交前手动运行更新命令（见下文）。

### 本地启用（推荐）

```bash
pip install pre-commit
pre-commit install
```

之后每次 `git commit` 前会自动运行：

```bash
python scripts/update_readme.py
```

### 手动更新

```bash
python scripts/update_readme.py
```

### 一键检查（可选）

```bash
# 运行所有 pre-commit hooks（不依赖 git commit）
pre-commit run -a
```

### MySQL 配置（可选）

创建 `.env` 文件：

```env
# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=history_heroes

# Flask 密钥
SECRET_KEY=your-secret-key
```

> 💡 不配置 MySQL 时，项目会自动使用 SQLite 数据库

---

## 📁 项目结构

```
Mygame/
├── app.py                 # Flask 主应用（路由 + API + 迁移）
├── run.py                 # 启动入口
├── config.py              # 配置文件
├── models.py              # SQLAlchemy 数据模型
├── game_data.py           # 游戏静态数据（角色/关卡/技能）
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 镜像
├── docker-compose.yml     # Docker Compose 编排
├── .env.example           # 环境变量示例
│
├── docs/                  # 项目文档
│   ├── 策划需求清单.md        # 需求总表（统一推进）
│   └── 美术资源清单.md        # 美术资源清单与规范
│
├── scripts/               # 工具脚本
│   └── update_readme.py       # README 自动更新（pre-commit）
│
├── templates/             # Jinja2 模板
│   ├── base.html              # 基础布局（导航栏/HUD/模态框）
│   ├── index.html             # 主城（城镇）
│   ├── login.html             # 登录
│   ├── register.html          # 注册
│   ├── characters.html        # 角色列表（军营）
│   ├── character_detail.html  # 角色详情
│   ├── summon.html            # 召唤（群英馆）
│   ├── stages.html            # 副本选择（演武场）
│   ├── battle.html            # 战斗界面
│   ├── inventory.html         # 仓库
│   ├── shop.html              # 商会
│   ├── research.html          # 研究所
│   └── arena.html             # 竞技场
│
├── static/                # 静态资源
│   ├── css/                   # 样式
│   ├── js/                    # 前端脚本（音频等）
│   ├── images/                # 图片资源
│   │   ├── avatars/           # 玩家头像
│   │   ├── backgrounds/       # 场景背景
│   │   ├── buildings/         # 建筑图标
│   │   ├── characters/        # 角色头像 & 立绘
│   │   ├── effects/           # 元素特效
│   │   ├── skills/            # 技能图标
│   │   └── ui/                # UI 素材
│   └── audio/                 # 音频资源
│       ├── bgm/               # 背景音乐
│       └── sfx/               # 音效
│
└── instance/              # 运行时数据（git 忽略）
    └── history_heroes.db      # SQLite 数据库
```

---

## 🗄️ 数据库设计

### 表结构

| 表名 | 说明 |
|------|------|
| `players` | 玩家信息（UID/头像/资源/保底计数） |
| `player_characters` | 玩家角色、等级、星魂等级（复用 stars）、魂力（重复角色获得） |
| `player_team` | 队伍配置 |
| `player_completed_stages` | 通关记录（含星级） |
| `player_daily_tasks` | 每日任务 |
| `player_favorite_characters` | 常用角色（5 槽位） |
| `summon_history` | 抽卡历史 |
| `announcements` | 公告（登录/主城展示） |
| `seven_day_goals` | 七日目标 |

### ER 图

```
┌─────────────┐       ┌──────────────────────┐
│   players   │───1:N─│   player_characters  │
│             │       │                      │
│ id          │       │ id                   │
│ name        │       │ player_id (FK)       │
│ gold        │       │ character_id         │
│ gems        │       │ level, stars, soul   │
│ energy      │       └──────────────────────┘
│ pity_count  │
└─────────────┘       ┌──────────────────────┐
        │             │     player_team      │
        └─────1:N─────│                      │
                      │ player_id (FK)       │
                      │ character_inst_id    │
                      └──────────────────────┘
```

---

## 🎮 游戏玩法

### 1. 召唤英雄

```
入口：底部导航 → 召唤

召唤方式：
├── 单抽：100 钻石
├── 十连：900 钻石（9折）
└── 召唤券：免费

保底机制：
├── 50 抽必出史诗
└── 100 抽必出传说

概率分布：
├── 普通：60%
├── 稀有：30%
├── 史诗：8%
└── 传说：2%
```

### 2. 角色养成

```
入口：底部导航 → 角色 → 选择角色

养成方式：
├── 升级：消耗经验书，提升等级
└── 星魂：重复抽取该角色获得“魂力”，每 1 魂力可提升 1 星魂（蓝卡以上生效，最多 5★）

属性计算：
基础属性 × 等级系数 ×（装备/符文/天赋）×（星魂 2★/4★ 属性加成）

星魂规则（类似原神命座）：
├── 1★ / 3★：强化技能（按角色定位自动生成，可被单角色覆盖）
├── 2★ / 4★：提升基础属性（每档 +5%，叠加）
└── 5★：大幅强化被动天赋（默认约 +75%）
```

### 3. 副本挑战

```
入口：底部导航 → 副本

章节结构：
├── 第一章：初入战场（3关）
├── 第二章：名将云集（3关）
└── 第三章：传说之战（3关）

难度分级：
├── 简单（绿色）
├── 普通（蓝色）
├── 困难（橙色）
└── 地狱（红色）

奖励内容：
├── 金币
├── 经验
└── 钻石（部分关卡）
```

### 4. 战斗系统

```
战斗流程：
1. 选择关卡 → 消耗体力
2. 我方角色 vs 敌方角色
3. 选择技能攻击
4. 敌人回合反击
5. 战斗结束 → 发放奖励

技能类型：
├── 物理攻击
├── 特殊攻击
└── 增益Buff
```

---

## 🔌 API 接口

### 召唤

```http
POST /api/summon
Content-Type: application/json

{
  "type": "once"  // once | ten | ticket
}
```

### 升级角色

```http
POST /api/levelup
Content-Type: application/json

{
  "instance_id": 1,
  "exp": 100
}
```

### 星魂提升

```http
POST /api/starup
Content-Type: application/json

{
  "instance_id": 1
}
```

### 设置队伍

```http
POST /api/team
Content-Type: application/json

{
  "team": [1, 2, 3, 4]  // 角色实例ID数组
}
```

### 完成战斗

```http
POST /api/battle/complete
Content-Type: application/json

{
  "stage_id": "stage-1-1",
  "victory": true
}
```

### 领取每日任务

```http
POST /api/daily/claim
Content-Type: application/json

{
  "task_id": "daily-login"
}
```

---

## 👥 角色列表

| 角色 | 稀有度 | 元素 | 类型 | 历史背景 |
|------|--------|------|------|----------|
| 诸葛亮 | 传说 | 水 | 法师 | 三国蜀汉丞相 |
| 关羽 | 史诗 | 火 | 战士 | 三国蜀汉名将 |
| 花木兰 | 史诗 | 风 | 战士 | 北魏女英雄 |
| 亚瑟王 | 史诗 | 光 | 战士 | 不列颠传说之王 |
| 曹操 | 史诗 | 暗 | 战士 | 曹魏奠基者 |
| 宫本武藏 | 稀有 | 风 | 刺客 | 日本剑圣 |

---

## ⚙️ 配置说明

### config.py

```python
class Config:
    # 游戏配置
    MAX_TEAM_SIZE = 4        # 最大队伍人数
    MAX_ENERGY = 100         # 最大体力
    ENERGY_RECOVERY_RATE = 10 # 体力恢复速度（每小时）
    PITY_EPIC = 50           # 史诗保底
    PITY_LEGENDARY = 100     # 传说保底
```

### game_data.py

角色、技能、关卡等静态数据配置文件，可根据需要扩展：
- 添加新角色：在 `ALL_CHARACTERS` 列表中添加
- 添加新关卡：在 `CHAPTERS` 列表中添加

---

## 🚀 开发指南

### 添加新角色

编辑 `game_data.py`：

```python
ALL_CHARACTERS = [
    {
        'id': 'new-hero',
        'name': '新英雄',
        'title': '英雄称号',
        'era': '时代',
        'origin': '国家',
        'element': 'fire',
        'role_type': 'warrior',
        'rarity': 'epic',
        'stats': {...},
        'skills': [...]
    },
    # ...
]
```

### 添加新关卡

编辑 `game_data.py`：

```python
CHAPTERS = [
    {
        'id': 'chapter-4',
        'name': '新章节',
        'stages': [
            {
                'id': 'stage-4-1',
                'name': '新关卡',
                'enemy_ids': ['hero-id'],
                'enemy_levels': [20],
                # ...
            }
        ]
    }
]
```

---

## 📝 更新日志

### v2.1.0（当前版本）
- 玩家 UID（8 位自动生成）、可更换头像、常用角色 5 槽位
- 资源栏 HUD 优化（金币/钻石/体力）
- 公告系统 & 七日目标后端（模型 + API）
- 中世纪深色 UI 主题统一
- 战斗系统：自动战斗、倍速、属性克制、星级评价
- UP 池、扫荡、Toast 提示系统
- Docker / docker-compose 部署支持

### v2.0.0
- 重构为 Flask + SQLAlchemy 架构
- 支持 MySQL / SQLite 双数据库
- Jinja2 模板渲染、完整游戏功能

### v1.0.0
- Next.js + React 初始版本

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

> 详细需求规划见 [`docs/策划需求清单.md`](docs/策划需求清单.md)，美术资源规范见 [`docs/美术资源清单.md`](docs/美术资源清单.md)。
