# IdeaHub API 端点

Base URL: `/api/v1`

## 认证 (Auth)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| POST | `/auth/register` | 用户注册 | ❌ |
| POST | `/auth/login` | 用户登录 | ❌ |
| POST | `/auth/refresh` | 刷新Token | ✅ |
| POST | `/auth/logout` | 退出登录 | ✅ |
| POST | `/auth/forgot-password` | 忘记密码 | ❌ |
| POST | `/auth/reset-password` | 重置密码 | ❌ |
| POST | `/auth/oauth/{provider}` | 第三方登录 | ❌ |
| GET | `/auth/me` | 获取当前用户 | ✅ |

### 请求/响应示例

#### POST /auth/register
```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "nickname": "张三",
  "role": "creator"
}

// Response 201
{
  "id": "uuid",
  "email": "user@example.com",
  "nickname": "张三",
  "role": "creator",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### POST /auth/login
```json
// Request (form-data)
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

## 用户 (Users)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| GET | `/users` | 用户列表(人才库) | ❌ |
| GET | `/users/{id}` | 用户详情 | ❌ |
| PUT | `/users/me` | 更新个人信息 | ✅ |
| PUT | `/users/me/password` | 修改密码 | ✅ |
| POST | `/users/me/avatar` | 上传头像 | ✅ |
| GET | `/users/me/projects` | 我的项目 | ✅ |
| GET | `/users/me/investments` | 我的投资 | ✅ |
| GET | `/users/me/favorites` | 我的收藏 | ✅ |

### 查询参数

```
GET /users?skills=Python,React&role=creator&page=1&page_size=20
```

## 项目 (Projects)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| GET | `/projects` | 项目列表 | ❌ |
| GET | `/projects/hot` | 热门项目 | ❌ |
| GET | `/projects/{id}` | 项目详情 | ❌ |
| POST | `/projects` | 创建项目 | ✅ |
| PUT | `/projects/{id}` | 更新项目 | ✅ |
| DELETE | `/projects/{id}` | 删除项目 | ✅ |
| POST | `/projects/{id}/like` | 点赞/取消 | ✅ |
| POST | `/projects/{id}/favorite` | 收藏/取消 | ✅ |
| GET | `/projects/{id}/team` | 获取团队 | ❌ |
| POST | `/projects/{id}/apply` | 申请加入 | ✅ |
| GET | `/projects/{id}/applications` | 申请列表(项目方) | ✅ |
| PUT | `/projects/{id}/applications/{app_id}` | 处理申请 | ✅ |

### 查询参数

```
GET /projects?category=ai&stage=funding&search=机器人&sort_by=created_at&page=1&page_size=20
```

### 请求/响应示例

#### POST /projects
```json
// Request
{
  "title": "AI智能助手",
  "slogan": "让AI更懂你",
  "category": "ai",
  "stage": "idea",
  "content": "## 项目介绍\n...",
  "tags": ["AI", "ChatGPT", "效率工具"],
  "needs": {
    "partner": ["tech", "product"],
    "funding": true
  }
}

// Response 201
{
  "id": "uuid",
  "title": "AI智能助手",
  "slogan": "让AI更懂你",
  "category": "ai",
  "stage": "idea",
  "status": "draft",
  "owner": {
    "id": "uuid",
    "nickname": "张三",
    "avatar": "..."
  },
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### POST /projects/{id}/apply
```json
// Request
{
  "role": "tech",
  "message": "我有5年Python开发经验，对AI很感兴趣..."
}

// Response 201
{
  "id": "uuid",
  "project_id": "uuid",
  "user_id": "uuid",
  "role": "tech",
  "status": "pending",
  "apply_message": "...",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## 众筹 (Crowdfunding)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| GET | `/crowdfunding` | 众筹列表 | ❌ |
| GET | `/crowdfunding/{id}` | 众筹详情 | ❌ |
| POST | `/crowdfunding` | 发起众筹 | ✅ |
| PUT | `/crowdfunding/{id}` | 更新众筹 | ✅ |
| POST | `/crowdfunding/{id}/invest` | 投资 | ✅ |
| GET | `/crowdfunding/{id}/investors` | 投资人列表 | ❌ |
| POST | `/crowdfunding/{id}/cancel` | 取消众筹 | ✅ |

### 请求/响应示例

#### POST /crowdfunding
```json
// Request
{
  "project_id": "uuid",
  "goal_amount": 1000000,
  "min_investment": 1000,
  "equity_offered": 10,
  "end_date": "2025-03-01T00:00:00Z"
}

// Response 201
{
  "id": "uuid",
  "project_id": "uuid",
  "goal_amount": 1000000,
  "raised_amount": 0,
  "equity_offered": 10,
  "investor_count": 0,
  "status": "pending",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-03-01T00:00:00Z"
}
```

#### POST /crowdfunding/{id}/invest
```json
// Request
{
  "amount": 10000,
  "payment_method": "alipay"
}

// Response 201
{
  "investment_id": "uuid",
  "order_no": "IH20250101000001",
  "amount": 10000,
  "payment_url": "https://openapi.alipay.com/..."
}
```

## 支付 (Payment)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| POST | `/payment/callback/alipay` | 支付宝回调 | ❌ |
| POST | `/payment/callback/wechat` | 微信回调 | ❌ |
| GET | `/payment/{order_no}/status` | 查询支付状态 | ✅ |
| POST | `/payment/{order_no}/refund` | 申请退款 | ✅ |

## 消息 (Messages)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| GET | `/messages/conversations` | 会话列表 | ✅ |
| GET | `/messages/{user_id}` | 消息记录 | ✅ |
| POST | `/messages` | 发送消息 | ✅ |
| PUT | `/messages/{id}/read` | 标记已读 | ✅ |
| GET | `/messages/unread-count` | 未读数量 | ✅ |

### WebSocket

```
WS /ws/messages?token={access_token}

// 接收消息
{
  "type": "message",
  "data": {
    "id": "uuid",
    "sender_id": "uuid",
    "content": "Hello",
    "created_at": "2025-01-01T00:00:00Z"
  }
}

// 发送消息
{
  "type": "send",
  "receiver_id": "uuid",
  "content": "Hi there"
}
```

## 通知 (Notifications)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| GET | `/notifications` | 通知列表 | ✅ |
| PUT | `/notifications/read-all` | 全部已读 | ✅ |
| PUT | `/notifications/{id}/read` | 标记已读 | ✅ |
| DELETE | `/notifications/{id}` | 删除通知 | ✅ |

## 上传 (Upload)

| Method | Path | 描述 | 认证 |
|--------|------|------|------|
| POST | `/upload/image` | 上传图片 | ✅ |
| POST | `/upload/file` | 上传文件 | ✅ |

## 通用响应格式

### 成功响应 (2xx)

```json
{
  "id": "...",
  "...": "..."
}
```

### 列表响应

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### 错误响应 (4xx/5xx)

```json
{
  "detail": "错误描述",
  "code": "ERROR_CODE",
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ]
}
```

## HTTP 状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功(无内容) |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 500 | 服务器错误 |
