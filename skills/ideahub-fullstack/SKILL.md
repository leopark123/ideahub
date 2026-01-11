---
name: ideahub-fullstack
description: IdeaHub创意孵化平台全栈开发技能包。包含FastAPI后端、React前端、PostgreSQL数据库的完整开发指南。使用场景：(1) 开发用户认证系统, (2) 创建项目/众筹/合伙人相关API, (3) 构建React前端页面, (4) 数据库迁移和模型定义, (5) 支付系统集成, (6) WebSocket实时消息。技术栈：Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, React 18, TypeScript, TailwindCSS。
---

# IdeaHub 全栈开发技能包

用于开发 IdeaHub 创意孵化平台的完整技能包。

## 项目概述

IdeaHub 是一个连接创意、人才和资本的创业服务平台，核心功能包括：
- 项目发布与展示
- 智能合伙人匹配
- 众筹融资
- 实时消息系统

## 技术栈

### 后端
- Python 3.11+
- FastAPI (异步Web框架)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL (数据库)
- Redis (缓存/Session)
- Alembic (数据库迁移)
- Pydantic (数据验证)
- python-jose (JWT认证)

### 前端
- React 18
- TypeScript
- Vite (构建工具)
- TailwindCSS (样式)
- React Query (数据获取)
- Zustand (状态管理)
- React Router v6 (路由)

## 项目结构

参考 `references/project-structure.md` 获取完整目录结构。

## 开发指南

### 后端开发

#### 1. 创建新的 API 路由

```python
# api/v1/endpoints/{resource}.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.schemas.{resource} import {Resource}Create, {Resource}Response
from app.services.{resource} import {Resource}Service

router = APIRouter()

@router.post("", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    data: {Resource}Create,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = {Resource}Service(db)
    return await service.create(current_user.id, data)
```

#### 2. 创建数据模型

```python
# models/{resource}.py
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid

class {Resource}(Base):
    __tablename__ = "{resources}"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # ... 其他字段
    
    # Relationships
    owner = relationship("User", back_populates="{resources}")
```

#### 3. 创建 Pydantic Schema

```python
# schemas/{resource}.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class {Resource}Base(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    # ... 其他字段

class {Resource}Create({Resource}Base):
    pass

class {Resource}Response({Resource}Base):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 前端开发

#### 1. 创建页面组件

```tsx
// pages/{Resource}Page.tsx
import { useQuery } from '@tanstack/react-query';
import { fetch{Resources} } from '@/api/{resource}';

export default function {Resource}Page() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['{resources}'],
    queryFn: fetch{Resources}
  });

  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 页面内容 */}
    </div>
  );
}
```

#### 2. API 请求封装

```typescript
// api/{resource}.ts
import { apiClient } from './client';
import type { {Resource}, {Resource}Create } from '@/types/{resource}';

export const fetch{Resources} = async (params?: {Resource}Params) => {
  const { data } = await apiClient.get<{Resource}[]>('/{resources}', { params });
  return data;
};

export const create{Resource} = async (payload: {Resource}Create) => {
  const { data } = await apiClient.post<{Resource}>('/{resources}', payload);
  return data;
};
```

## 数据库模型

参考 `references/database-schema.md` 获取完整数据库设计。

核心表：
- `users` - 用户表
- `projects` - 项目表
- `crowdfundings` - 众筹表
- `investments` - 投资记录表
- `partnerships` - 合伙关系表
- `messages` - 消息表

## API 端点

参考 `references/api-endpoints.md` 获取完整API列表。

主要模块：
- `/api/v1/auth/*` - 认证
- `/api/v1/users/*` - 用户
- `/api/v1/projects/*` - 项目
- `/api/v1/crowdfunding/*` - 众筹
- `/api/v1/messages/*` - 消息

## 常用命令

### 后端

```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload --port 8000

# 数据库迁移
alembic revision --autogenerate -m "description"
alembic upgrade head

# 运行测试
pytest tests/ -v
```

### 前端

```bash
# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build

# 类型检查
npm run typecheck
```

## 环境变量

### 后端 (.env)

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ideahub
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 前端 (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## 编码规范

1. 后端使用 async/await 异步编程
2. 所有 API 响应使用 Pydantic 模型
3. 前端组件使用函数式组件 + Hooks
4. 使用 TypeScript 严格模式
5. 遵循 RESTful API 设计规范

## 错误处理

后端统一错误响应格式：

```json
{
  "detail": "错误描述",
  "code": "ERROR_CODE",
  "errors": []
}
```

## 参考文档

- `references/database-schema.md` - 数据库设计
- `references/api-endpoints.md` - API 端点列表
- `references/project-structure.md` - 项目结构
- `references/coding-standards.md` - 编码规范
