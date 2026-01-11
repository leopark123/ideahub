# IdeaHub 项目结构

## 整体结构

```
ideahub/
├── backend/                 # 后端项目
│   └── ideahub-api/
├── frontend/                # 前端项目
│   └── ideahub-web/
├── docker/                  # Docker配置
├── docs/                    # 文档
├── docker-compose.yml
├── Makefile
└── README.md
```

## 后端结构 (FastAPI)

```
ideahub-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置管理
│   │
│   ├── api/                       # API 路由
│   │   ├── __init__.py
│   │   ├── deps.py                # 依赖注入
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # 路由汇总
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── projects.py
│   │           ├── crowdfunding.py
│   │           ├── partnerships.py
│   │           ├── messages.py
│   │           ├── notifications.py
│   │           └── upload.py
│   │
│   ├── core/                      # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py              # 配置类
│   │   ├── security.py            # 安全相关(JWT,密码)
│   │   ├── deps.py                # 全局依赖
│   │   └── exceptions.py          # 自定义异常
│   │
│   ├── db/                        # 数据库
│   │   ├── __init__.py
│   │   ├── base.py                # Base 模型
│   │   ├── session.py             # 数据库会话
│   │   └── init_db.py             # 初始化数据
│   │
│   ├── models/                    # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── crowdfunding.py
│   │   ├── investment.py
│   │   ├── partnership.py
│   │   ├── message.py
│   │   └── notification.py
│   │
│   ├── schemas/                   # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── crowdfunding.py
│   │   ├── investment.py
│   │   ├── partnership.py
│   │   ├── message.py
│   │   ├── notification.py
│   │   ├── auth.py
│   │   └── common.py              # 通用Schema
│   │
│   ├── services/                  # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── crowdfunding.py
│   │   ├── partnership.py
│   │   ├── message.py
│   │   ├── notification.py
│   │   ├── payment.py
│   │   └── upload.py
│   │
│   ├── repositories/              # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py                # 基础Repository
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── crowdfunding.py
│   │   ├── investment.py
│   │   ├── partnership.py
│   │   └── message.py
│   │
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── pagination.py
│       ├── validators.py
│       └── helpers.py
│
├── migrations/                    # Alembic 迁移
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── tests/                         # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_projects.py
│   └── ...
│
├── scripts/                       # 脚本
│   ├── init_db.py
│   └── seed_data.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## 前端结构 (React + TypeScript)

```
ideahub-web/
├── public/
│   ├── favicon.ico
│   └── robots.txt
│
├── src/
│   ├── main.tsx                   # 入口文件
│   ├── App.tsx                    # 根组件
│   ├── vite-env.d.ts
│   │
│   ├── api/                       # API 请求
│   │   ├── client.ts              # Axios 实例
│   │   ├── auth.ts
│   │   ├── users.ts
│   │   ├── projects.ts
│   │   ├── crowdfunding.ts
│   │   ├── messages.ts
│   │   └── upload.ts
│   │
│   ├── components/                # 组件
│   │   ├── ui/                    # 基础UI组件
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Avatar.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Dropdown.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/                # 布局组件
│   │   │   ├── Navbar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── PageContainer.tsx
│   │   │
│   │   ├── project/               # 项目相关组件
│   │   │   ├── ProjectCard.tsx
│   │   │   ├── ProjectList.tsx
│   │   │   ├── ProjectForm.tsx
│   │   │   ├── ProjectDetail.tsx
│   │   │   └── ProjectFilters.tsx
│   │   │
│   │   ├── crowdfunding/          # 众筹相关组件
│   │   │   ├── CrowdfundingCard.tsx
│   │   │   ├── CrowdfundingProgress.tsx
│   │   │   ├── InvestModal.tsx
│   │   │   └── InvestorList.tsx
│   │   │
│   │   ├── user/                  # 用户相关组件
│   │   │   ├── UserCard.tsx
│   │   │   ├── UserAvatar.tsx
│   │   │   ├── ProfileForm.tsx
│   │   │   └── SkillTags.tsx
│   │   │
│   │   └── common/                # 通用组件
│   │       ├── Loading.tsx
│   │       ├── Error.tsx
│   │       ├── Empty.tsx
│   │       ├── Pagination.tsx
│   │       ├── SearchBar.tsx
│   │       └── ProtectedRoute.tsx
│   │
│   ├── pages/                     # 页面
│   │   ├── Home.tsx
│   │   ├── ProjectDetail.tsx
│   │   ├── ProjectCreate.tsx
│   │   ├── Partners.tsx
│   │   ├── Crowdfunding.tsx
│   │   ├── Search.tsx
│   │   ├── Profile.tsx
│   │   ├── Settings.tsx
│   │   ├── Messages.tsx
│   │   ├── Auth/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── ForgotPassword.tsx
│   │   └── NotFound.tsx
│   │
│   ├── hooks/                     # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useUser.ts
│   │   ├── useProjects.ts
│   │   ├── useWebSocket.ts
│   │   ├── useInfiniteScroll.ts
│   │   └── useDebounce.ts
│   │
│   ├── stores/                    # Zustand 状态管理
│   │   ├── authStore.ts
│   │   ├── userStore.ts
│   │   └── uiStore.ts
│   │
│   ├── types/                     # TypeScript 类型
│   │   ├── user.ts
│   │   ├── project.ts
│   │   ├── crowdfunding.ts
│   │   ├── message.ts
│   │   ├── api.ts
│   │   └── index.ts
│   │
│   ├── utils/                     # 工具函数
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   ├── storage.ts
│   │   └── constants.ts
│   │
│   ├── styles/                    # 样式
│   │   ├── globals.css
│   │   └── tailwind.css
│   │
│   └── router/                    # 路由配置
│       └── index.tsx
│
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── eslint.config.js
```

## Docker 配置

```
docker/
├── backend/
│   └── Dockerfile
├── frontend/
│   └── Dockerfile
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
└── postgres/
    └── init.sql
```

## 配置文件示例

### docker-compose.yml

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ideahub
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ideahub
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend/ideahub-api
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://ideahub:password@db:5432/ideahub
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend/ideahub-web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

### Makefile

```makefile
.PHONY: dev build test clean

dev:
	docker-compose up -d

build:
	docker-compose build

test:
	cd backend/ideahub-api && pytest
	cd frontend/ideahub-web && npm test

clean:
	docker-compose down -v

migrate:
	cd backend/ideahub-api && alembic upgrade head

seed:
	cd backend/ideahub-api && python scripts/seed_data.py
```
