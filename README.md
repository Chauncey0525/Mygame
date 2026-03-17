# ⚔️ 巅峰对决

> 一款以古今中外历史人物为背景的养成型回合制战斗游戏

## 📖 项目简介

《巅峰对决》是一款融合了角色收集、养成升级、副本挑战等核心玩法的回合制游戏。玩家可以召唤诸葛亮、关羽、花木兰、亚瑟王等历史名将，组建自己的队伍，挑战各种副本关卡。

### ✨ 核心功能

| 功能模块 | 说明 |
|---------|------|
| 🎭 **角色养成** | 升级、突破、星级提升，打造最强角色 |
| ✨ **召唤系统** | 单抽、十连、保底机制，收集传奇英雄 |
| ⚔️ **副本挑战** | 多章节关卡，不同难度，丰富奖励 |
| 📋 **每日任务** | 完成任务获取资源，每日签到奖励 |
| 🎯 **队伍编辑** | 自由搭配4人队伍，策略战斗 |

---

## 📰 最近更新（自动生成）

<!-- AUTO-UPDATE-START -->
_最后生成时间：2026-03-17 18:57_

- `244d0c8` (2026-03-17) chore: unify port 5000, add docker and auto README updates
- `9e7d6c5` (2026-03-17) feat: 属性系统重构与角色头像图片
- `4067d3a` (2026-03-17) feat: 属性系统重构与角色头像图片
- `dc6ba84` (2026-03-17) chore: 提交本地 sqlite 数据库
- `1f268b2` (2026-03-17) feat: 手机号验证码注册与密码规则校验
- `be073e5` (2026-03-17) fix: 统一所有用户密码为123456，便于登录测试
- `a53c3a7` (2026-03-17) chore: 提供浏览器缓存清除说明
- `5b2a375` (2026-03-17) fix: 修复登录问题并添加记住我功能
- `1d0117f` (2026-03-17) fix: 修复登录状态无法保持的问题
- `ca8a125` (2026-03-17) fix: 修复数据库路径配置，确保使用 instance 目录
- `61233ca` (2026-03-17) fix: 修复数据库路径配置，确保使用 instance 目录
- `901e188` (2026-03-17) feat: 添加用户账号注册登录系统
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
├── app.py                 # Flask 主应用
├── run.py                 # 启动入口
├── config.py              # 配置文件
├── models.py              # 数据库模型
├── game_data.py           # 游戏静态数据
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量示例
│
├── templates/             # Jinja2 模板
│   ├── base.html              # 基础布局
│   ├── index.html             # 首页
│   ├── characters.html        # 角色列表
│   ├── character_detail.html  # 角色详情
│   ├── summon.html            # 召唤页面
│   ├── stages.html            # 副本选择
│   └── battle.html            # 战斗界面
│
├── static/                # 静态资源
│   ├── css/
│   │   └── style.css          # 样式文件
│   └── images/
│       └── characters/        # 角色图片
│
└── instance/              # 实例数据
    └── history_heroes.db       # SQLite 数据库
```

---

## 🗄️ 数据库设计

### 表结构

| 表名 | 说明 |
|------|------|
| `players` | 玩家信息、资源、保底计数 |
| `player_characters` | 玩家角色、等级、星级、突破 |
| `player_team` | 队伍配置 |
| `player_completed_stages` | 通关记录 |
| `player_daily_tasks` | 每日任务 |
| `summon_history` | 抽卡历史 |

### ER 图

```
┌─────────────┐       ┌──────────────────────┐
│   players   │───1:N─│   player_characters  │
│             │       │                      │
│ id          │       │ id                   │
│ name        │       │ player_id (FK)       │
│ gold        │       │ character_id         │
│ gems        │       │ level, stars, break  │
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
└── 突破：消耗金币，提升属性上限

属性计算：
基础属性 × 等级系数 × 星级系数 × 突破系数
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

### 突破角色

```http
POST /api/breakthrough
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

### v2.0.1（未发布）
- ❔ 召唤页“概率说明”收起到问号提示中，页面更清爽

### v2.0.0 (当前版本)
- 🔄 重构为 Flask + MySQL 架构
- 🎨 使用 Jinja2 模板渲染
- 🗄️ 支持 MySQL / SQLite 双数据库
- 🎮 完整的游戏功能实现

### v1.0.0
- ✨ Next.js + React 初始版本
- 🎭 角色养成系统
- ⚔️ 回合制战斗系统

---

## 🧠 后续更新 Brainstorm（可选 Roadmap）

下面是一些“按收益优先”的可迭代方向，后续可以逐步挑选落地（不要求一次做完）。

### 玩法与数值
- **更完整的抽卡机制**：UP卡池/限定池、概率展示与历史统计、保底继承规则与可视化
- **战斗策略深化**：速度轴/行动条、属性克制更明确、技能冷却/能量系统、异常状态（中毒/眩晕/护盾等）
- **养成深度**：装备/符文、天赋树、羁绊加成、同名升星材料与分解回收
- **平衡与可调参**：把关键倍率/掉落/关卡难度集中配置，支持热更新或管理后台调参

### 内容扩展
- **更多章节/关卡**：分支路线、精英/首领关、事件关、每周轮换挑战
- **角色内容**：新角色、新技能组合、角色语音/立绘、角色背景故事页面完善
- **日常与活动**：周常任务、签到/月卡、活动副本与兑换商店

### UI/UX
- **移动端体验**：tooltip 改为“点击展开/再次点击收起”、按钮更大、底部导航更顺手
- **统一组件风格**：卡片/弹窗/提示（toast）/表单校验统一；加载态/空状态更友好
- **可访问性**：键盘可操作、focus 样式、对比度优化、ARIA 标注

### 工程化与质量
- **测试体系**：核心逻辑单元测试（数值/掉落/战斗结算）、接口测试（Flask test client）
- **日志与监控**：关键行为埋点（召唤/战斗/资源变动）、错误日志与慢请求定位
- **CI/CD**：GitHub Actions 跑 lint/test；打包发布（Docker）与一键部署
- **代码结构演进**：按模块拆分 `app.py`（blueprints/services/repositories），减少单文件复杂度

### 安全与账号体系
- **鉴权与安全加固**：CSRF、防暴力登录、密码策略、敏感配置与密钥管理
- **数据一致性**：关键写操作事务化、并发安全（资源扣减/抽卡写入）

> 如果你想把它变成真正的 Roadmap，我也可以把上面内容拆成里程碑（M1/M2/M3）并附上更具体的交付清单与验收标准。

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！