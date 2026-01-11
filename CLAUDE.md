# CLAUDE.md - IdeaHub 项目 Agent 配置

这是 IdeaHub 项目的 Claude Code Agent 配置文件。

## 项目概述

IdeaHub 是一个创意孵化平台，包含以下核心功能：
- 项目发布与展示
- 智能合伙人匹配
- 众筹融资
- 实时消息系统

## 技术栈

### 后端
- Python 3.11+ / FastAPI
- PostgreSQL + SQLAlchemy 2.0
- Redis
- JWT 认证

### 前端
- React 18 + TypeScript
- Vite / TailwindCSS
- React Query + Zustand

## 项目结构

```
ideahub/
├── backend/ideahub-api/     # FastAPI 后端
├── frontend/ideahub-web/    # React 前端
├── docker/                   # Docker 配置
└── docs/                     # 文档
```

## 开发命令

### 后端
```bash
cd backend/ideahub-api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端
```bash
cd frontend/ideahub-web
npm install
npm run dev
```

### 数据库迁移
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 编码规范

### Python
- 使用 async/await 异步编程
- 类型注解必须完整
- 遵循 PEP 8，使用 Black 格式化
- 所有 API 使用 Pydantic 模型

### TypeScript
- 使用函数式组件 + Hooks
- 严格模式，禁止 any
- 组件使用 PascalCase 命名

## Agent 工作流程

### 创建新的 API 功能

1. **定义数据模型** (`app/models/`)
```python
# app/models/example.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin
import uuid

class Example(Base, TimestampMixin):
    __tablename__ = "examples"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
```

2. **定义 Schema** (`app/schemas/`)
```python
# app/schemas/example.py
from pydantic import BaseModel, Field
from uuid import UUID

class ExampleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class ExampleResponse(BaseModel):
    id: UUID
    name: str
    class Config:
        from_attributes = True
```

3. **创建 Service** (`app/services/`)
```python
# app/services/example.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.example import Example
from app.schemas.example import ExampleCreate

class ExampleService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: ExampleCreate) -> Example:
        obj = Example(**data.model_dump())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
```

4. **创建 API 端点** (`app/api/v1/endpoints/`)
```python
# app/api/v1/endpoints/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.schemas.example import ExampleCreate, ExampleResponse
from app.services.example import ExampleService

router = APIRouter()

@router.post("", response_model=ExampleResponse)
async def create_example(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ExampleService(db)
    return await service.create(data)
```

5. **注册路由** (`app/api/v1/router.py`)
```python
from app.api.v1.endpoints import example
api_router.include_router(example.router, prefix="/examples", tags=["示例"])
```

### 创建前端页面

1. **定义类型** (`src/types/`)
```typescript
// src/types/example.ts
export interface Example {
  id: string;
  name: string;
  createdAt: string;
}
```

2. **创建 API 函数** (`src/api/`)
```typescript
// src/api/example.ts
import { apiClient } from './client';
import type { Example } from '@/types/example';

export const exampleApi = {
  list: async () => {
    const { data } = await apiClient.get<Example[]>('/examples');
    return data;
  },
  create: async (payload: { name: string }) => {
    const { data } = await apiClient.post<Example>('/examples', payload);
    return data;
  },
};
```

3. **创建 Hook** (`src/hooks/`)
```typescript
// src/hooks/useExamples.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { exampleApi } from '@/api/example';

export const useExamples = () => {
  return useQuery({
    queryKey: ['examples'],
    queryFn: exampleApi.list,
  });
};

export const useCreateExample = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: exampleApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['examples'] });
    },
  });
};
```

4. **创建页面组件** (`src/pages/`)
```tsx
// src/pages/Examples.tsx
import { useExamples, useCreateExample } from '@/hooks/useExamples';

export default function Examples() {
  const { data, isLoading } = useExamples();
  const createMutation = useCreateExample();

  if (isLoading) return <div>加载中...</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">示例列表</h1>
      <ul>
        {data?.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

## 常见任务快速参考

| 任务 | 命令/位置 |
|------|----------|
| 添加新表 | `app/models/` → `alembic revision --autogenerate` |
| 添加 API | `app/api/v1/endpoints/` → 注册到 router.py |
| 添加页面 | `src/pages/` → 添加路由到 App.tsx |
| 添加组件 | `src/components/` |
| 添加类型 | `src/types/` |
| 运行测试 | `pytest tests/ -v` |
| 格式化代码 | `black .` / `npm run lint` |

## 环境变量

### 后端 (.env)
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ideahub
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

### 前端 (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 数据库表

核心表: `users`, `projects`, `crowdfundings`, `investments`, `partnerships`, `messages`

详细字段参考: `docs/database-schema.md`

## API 端点

主要模块:
- `/api/v1/auth/*` - 认证
- `/api/v1/users/*` - 用户
- `/api/v1/projects/*` - 项目
- `/api/v1/crowdfunding/*` - 众筹
- `/api/v1/messages/*` - 消息

详细接口参考: `docs/api-endpoints.md`
