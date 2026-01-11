# 💡 IdeaHub - Claude Code 开发套件

IdeaHub 创意孵化平台的 Claude Code 开发配置包，包含 Skill、Agent 配置和完整开发文档。

## ✨ 特性

- 📦 **完整的 Skill 配置** - 包含数据库设计、API 端点、编码规范等参考文档
- 🤖 **Agent 配置** - CLAUDE.md 配置文件，定义项目上下文和工作流程
- 🚀 **初始化脚本** - 一键生成后端/前端项目骨架
- 📚 **详细文档** - 快速开始指南、开发任务清单

## 📂 目录结构

```
ideahub-claude-code/
├── CLAUDE.md                          # Agent 配置文件
├── README.md                          # 本文件
│
├── skills/
│   └── ideahub-fullstack/             # 全栈开发 Skill
│       ├── SKILL.md                   # Skill 主文件
│       ├── references/                # 参考文档
│       │   ├── database-schema.md     # 数据库设计
│       │   ├── api-endpoints.md       # API 端点
│       │   ├── project-structure.md   # 项目结构
│       │   └── coding-standards.md    # 编码规范
│       ├── scripts/                   # 初始化脚本
│       │   ├── init_backend.py        # 后端初始化
│       │   └── init_frontend.py       # 前端初始化
│       └── assets/                    # 静态资源
│
├── docs/
│   └── QUICKSTART.md                  # 快速开始指南
│
└── docker-compose.yml                 # Docker 配置
```

## 🚀 快速开始

### 1. 安装 Skill

将 Skill 文件夹复制到 Claude Code 的 skills 目录：

```bash
# macOS/Linux
cp -r skills/ideahub-fullstack ~/.claude/skills/

# 或者在 Claude Code 设置中添加 skill 路径
```

### 2. 初始化项目

```bash
# 初始化后端
python skills/ideahub-fullstack/scripts/init_backend.py ./backend/ideahub-api

# 初始化前端
python skills/ideahub-fullstack/scripts/init_frontend.py ./frontend/ideahub-web
```

### 3. 启动开发

```bash
# 后端
cd backend/ideahub-api
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend/ideahub-web
npm install
npm run dev
```

## 🔧 在 Claude Code 中使用

### 将 CLAUDE.md 放入项目根目录

```bash
cp CLAUDE.md your-project/
```

### 示例对话

```
👤 User: 帮我创建用户注册功能

🤖 Claude: 我来帮你创建用户注册功能，包括：
1. 用户模型 (app/models/user.py)
2. 注册 Schema (app/schemas/auth.py)
3. 注册 API (app/api/v1/endpoints/auth.py)
4. 注册页面 (src/pages/Auth/Register.tsx)
...
```

## 📋 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 数据库 | PostgreSQL + SQLAlchemy 2.0 |
| 缓存 | Redis |
| 认证 | JWT |
| 前端框架 | React 18 + TypeScript |
| 状态管理 | Zustand + React Query |
| 样式 | TailwindCSS |
| 构建工具 | Vite |

## 📖 文档

- [快速开始指南](docs/QUICKSTART.md)
- [数据库设计](skills/ideahub-fullstack/references/database-schema.md)
- [API 端点](skills/ideahub-fullstack/references/api-endpoints.md)
- [项目结构](skills/ideahub-fullstack/references/project-structure.md)
- [编码规范](skills/ideahub-fullstack/references/coding-standards.md)

## 🗺️ 开发路线图

### Phase 1 - MVP
- [x] 项目框架搭建
- [ ] 用户认证系统
- [ ] 项目 CRUD
- [ ] 基础页面

### Phase 2 - 社交
- [ ] 合伙人匹配
- [ ] 私信系统
- [ ] 通知系统

### Phase 3 - 众筹
- [ ] 众筹功能
- [ ] 支付集成
- [ ] 投资记录

## 📄 License

MIT License
