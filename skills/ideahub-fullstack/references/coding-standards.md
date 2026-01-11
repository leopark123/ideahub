# IdeaHub 编码规范

## Python 后端规范

### 代码风格

- 遵循 PEP 8
- 使用 Black 格式化 (行宽 88)
- 使用 isort 排序导入
- 类型注解必须完整

### 命名规范

```python
# 模块/文件: snake_case
user_service.py

# 类: PascalCase
class UserService:
    pass

# 函数/方法: snake_case
def get_user_by_id():
    pass

# 变量: snake_case
user_count = 0

# 常量: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 私有: 前缀下划线
_internal_cache = {}
```

### 异步编程

```python
# ✅ 正确: 使用 async/await
async def get_user(user_id: UUID) -> User:
    return await db.execute(select(User).where(User.id == user_id))

# ❌ 错误: 在异步函数中使用同步代码
async def get_user(user_id: UUID) -> User:
    return db.query(User).filter(User.id == user_id).first()  # 阻塞!
```

### API 路由

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

router = APIRouter(prefix="/projects", tags=["项目"])

@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目列表
    
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，1-100
    - **category**: 可选，按分类筛选
    """
    service = ProjectService(db)
    return await service.list(page, page_size, category)
```

### Service 层

```python
class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProjectRepository(db)
    
    async def create(self, user_id: UUID, data: ProjectCreate) -> Project:
        # 业务逻辑验证
        if await self.repo.exists_by_title(data.title):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="项目名称已存在"
            )
        
        # 创建项目
        project = Project(
            user_id=user_id,
            **data.model_dump()
        )
        return await self.repo.create(project)
```

### Repository 层

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository[T]:
    def __init__(self, db: AsyncSession, model: type[T]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: UUID) -> T | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
```

### Schema 定义

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    nickname: str = Field(..., min_length=2, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    skills: Optional[List[str]] = None

class UserResponse(UserBase):
    id: UUID
    avatar: Optional[str]
    bio: Optional[str]
    role: str
    skills: List[str]
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

### 错误处理

```python
from fastapi import HTTPException, status

# 自定义异常
class BusinessException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

# 全局异常处理
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "code": exc.code
        }
    )

# 使用示例
raise BusinessException(
    code="PROJECT_NOT_FOUND",
    message="项目不存在",
    status_code=404
)
```

## TypeScript 前端规范

### 代码风格

- 使用 ESLint + Prettier
- 使用函数式组件
- 使用 TypeScript 严格模式

### 命名规范

```typescript
// 组件: PascalCase
const ProjectCard: React.FC<ProjectCardProps> = () => {}

// 文件名: PascalCase (组件) / camelCase (其他)
ProjectCard.tsx
useAuth.ts

// 变量/函数: camelCase
const projectCount = 0;
const handleSubmit = () => {};

// 常量: UPPER_SNAKE_CASE
const API_BASE_URL = '';

// 类型/接口: PascalCase
interface UserProfile {}
type ProjectStatus = 'draft' | 'published';

// 枚举: PascalCase
enum ProjectStage {
  Idea = 'idea',
  Building = 'building',
}
```

### 组件结构

```tsx
import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { Project } from '@/types';

interface ProjectCardProps {
  project: Project;
  onLike?: (id: string) => void;
  className?: string;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onLike,
  className = '',
}) => {
  // 1. Hooks
  const [isLiked, setIsLiked] = useState(false);
  
  // 2. Derived state
  const formattedDate = formatDate(project.createdAt);
  
  // 3. Effects
  useEffect(() => {
    // ...
  }, []);
  
  // 4. Event handlers
  const handleLike = useCallback(() => {
    setIsLiked(prev => !prev);
    onLike?.(project.id);
  }, [project.id, onLike]);
  
  // 5. Render
  return (
    <div className={`rounded-lg bg-white shadow ${className}`}>
      {/* ... */}
    </div>
  );
};
```

### API 请求

```typescript
// api/client.ts
import axios, { AxiosError } from 'axios';
import { useAuthStore } from '@/stores/authStore';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

// 请求拦截器
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
```

```typescript
// api/projects.ts
import { apiClient } from './client';
import type { Project, ProjectCreate, PaginatedResponse } from '@/types';

export const projectApi = {
  list: async (params?: ProjectListParams) => {
    const { data } = await apiClient.get<PaginatedResponse<Project>>(
      '/projects',
      { params }
    );
    return data;
  },

  get: async (id: string) => {
    const { data } = await apiClient.get<Project>(`/projects/${id}`);
    return data;
  },

  create: async (payload: ProjectCreate) => {
    const { data } = await apiClient.post<Project>('/projects', payload);
    return data;
  },
};
```

### 状态管理 (Zustand)

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      
      login: (token, user) => set({
        token,
        user,
        isAuthenticated: true,
      }),
      
      logout: () => set({
        token: null,
        user: null,
        isAuthenticated: false,
      }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
```

### React Query 使用

```typescript
// hooks/useProjects.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectApi } from '@/api/projects';

export const useProjects = (params?: ProjectListParams) => {
  return useQuery({
    queryKey: ['projects', params],
    queryFn: () => projectApi.list(params),
  });
};

export const useProject = (id: string) => {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => projectApi.get(id),
    enabled: !!id,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: projectApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};
```

### 类型定义

```typescript
// types/project.ts
export interface Project {
  id: string;
  title: string;
  slogan?: string;
  category: ProjectCategory;
  stage: ProjectStage;
  content?: string;
  tags: string[];
  coverImage?: string;
  viewCount: number;
  likeCount: number;
  owner: UserSummary;
  createdAt: string;
  updatedAt: string;
}

export type ProjectCategory = 
  | 'ai' 
  | 'app' 
  | 'game' 
  | 'health' 
  | 'education';

export type ProjectStage = 
  | 'idea' 
  | 'building' 
  | 'funding' 
  | 'launched';

export interface ProjectCreate {
  title: string;
  slogan?: string;
  category: ProjectCategory;
  stage: ProjectStage;
  content?: string;
  tags?: string[];
}

export interface ProjectListParams {
  page?: number;
  pageSize?: number;
  category?: ProjectCategory;
  stage?: ProjectStage;
  search?: string;
}
```

## Git 规范

### Commit Message

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

#### 示例

```
feat(project): 添加项目点赞功能

- 添加点赞 API 端点
- 添加前端点赞按钮组件
- 更新项目详情页

Closes #123
```

### 分支命名

```
main              # 主分支
develop           # 开发分支
feature/xxx       # 功能分支
fix/xxx           # 修复分支
release/v1.0.0    # 发布分支
```
