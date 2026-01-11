# IdeaHub 快速开始指南

## 🚀 5分钟快速启动

### 方式一：使用初始化脚本（推荐）

```bash
# 1. 克隆或下载本配置包
cd ideahub-claude-code

# 2. 初始化后端项目
python skills/ideahub-fullstack/scripts/init_backend.py backend/ideahub-api

# 3. 初始化前端项目
python skills/ideahub-fullstack/scripts/init_frontend.py frontend/ideahub-web

# 4. 启动后端
cd backend/ideahub-api
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# 5. 启动前端（新终端）
cd frontend/ideahub-web
npm install
cp .env.example .env
npm run dev
```

### 方式二：使用 Docker

```bash
# 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 📂 项目结构

```
ideahub/
├── backend/
│   └── ideahub-api/        # FastAPI 后端 (localhost:8000)
├── frontend/
│   └── ideahub-web/        # React 前端 (localhost:3000)
├── docs/                    # 项目文档
├── CLAUDE.md               # Claude Code Agent 配置
└── docker-compose.yml
```

## 🔧 在 Claude Code 中使用

### 安装 Skill

将 `skills/ideahub-fullstack` 文件夹添加到你的 Claude Code skills 目录：

```bash
cp -r skills/ideahub-fullstack ~/.claude/skills/
```

### 常用指令示例

```
# 创建新的 API 端点
"帮我创建一个评论功能的 API，包括发表评论、获取评论列表、删除评论"

# 创建前端页面
"帮我创建项目详情页面，显示项目信息、团队成员、众筹进度"

# 添加新功能
"给项目添加收藏功能，用户可以收藏感兴趣的项目"

# 修复问题
"登录接口返回 401 错误，帮我排查问题"

# 数据库变更
"给用户表添加手机号验证字段"
```

## 📋 开发任务清单

### Phase 1 - MVP (4-6周)

- [ ] 用户系统
  - [ ] 注册/登录 API
  - [ ] JWT 认证
  - [ ] 个人信息管理
  - [ ] 头像上传

- [ ] 项目系统
  - [ ] 项目 CRUD API
  - [ ] 项目列表页面
  - [ ] 项目详情页面
  - [ ] 发布项目页面
  - [ ] 分类筛选

- [ ] 基础功能
  - [ ] 搜索功能
  - [ ] 点赞/收藏
  - [ ] 分页加载

### Phase 2 - 社交 (3-4周)

- [ ] 合伙人系统
  - [ ] 人才库页面
  - [ ] 技能匹配
  - [ ] 申请加入项目

- [ ] 消息系统
  - [ ] 私信功能
  - [ ] 通知系统
  - [ ] WebSocket 实时消息

### Phase 3 - 众筹 (4-6周)

- [ ] 众筹系统
  - [ ] 发起众筹
  - [ ] 众筹详情
  - [ ] 投资功能
  - [ ] 支付集成
  - [ ] 投资记录

## 🔗 有用链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)
- [TailwindCSS 文档](https://tailwindcss.com/docs)
- [React Query 文档](https://tanstack.com/query/latest)
- [Zustand 文档](https://github.com/pmndrs/zustand)

## ❓ 常见问题

### Q: 数据库连接失败？
确保 PostgreSQL 已启动，检查 `.env` 中的 `DATABASE_URL` 配置。

### Q: 前端请求 API 跨域？
Vite 已配置代理，确保 `vite.config.ts` 中的 proxy 指向正确的后端地址。

### Q: 如何添加新的数据库表？
1. 在 `app/models/` 创建模型
2. 运行 `alembic revision --autogenerate -m "add xxx table"`
3. 运行 `alembic upgrade head`

### Q: 如何部署？
参考 `docs/deployment.md` 部署指南（待补充）。
