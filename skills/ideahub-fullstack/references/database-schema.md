# IdeaHub 数据库设计

## ER 关系图

```
users 1──┬──N projects
         │
         ├──N partnerships
         │
         ├──N investments
         │
         └──N messages (sender/receiver)

projects 1──1 crowdfundings
         │
         └──N partnerships

crowdfundings 1──N investments
```

## 表结构定义

### users (用户表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 用户ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱 |
| phone | VARCHAR(20) | UNIQUE | 手机号 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| nickname | VARCHAR(50) | NOT NULL | 昵称 |
| avatar | VARCHAR(500) | | 头像URL |
| bio | TEXT | | 个人简介 |
| role | ENUM | DEFAULT 'user' | user/creator/investor/admin |
| skills | JSONB | DEFAULT '[]' | 技能标签 |
| social_links | JSONB | DEFAULT '{}' | 社交链接 |
| is_verified | BOOLEAN | DEFAULT false | 实名认证 |
| is_active | BOOLEAN | DEFAULT true | 账号状态 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | ON UPDATE | 更新时间 |

### projects (项目表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 项目ID |
| user_id | UUID | FK → users.id | 创建者 |
| title | VARCHAR(100) | NOT NULL | 项目名称 |
| slogan | VARCHAR(200) | | 一句话介绍 |
| cover_image | VARCHAR(500) | | 封面图URL |
| category | VARCHAR(50) | NOT NULL | 分类 |
| stage | ENUM | NOT NULL | idea/building/funding/launched |
| content | TEXT | | 详情(Markdown) |
| tags | JSONB | DEFAULT '[]' | 标签 |
| needs | JSONB | DEFAULT '{}' | 需求 |
| team_size | INTEGER | DEFAULT 1 | 团队人数 |
| view_count | INTEGER | DEFAULT 0 | 浏览数 |
| like_count | INTEGER | DEFAULT 0 | 点赞数 |
| status | ENUM | DEFAULT 'draft' | draft/pending/published/closed |
| is_hot | BOOLEAN | DEFAULT false | 是否热门 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | ON UPDATE | 更新时间 |

### crowdfundings (众筹表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 众筹ID |
| project_id | UUID | FK → projects.id, UNIQUE | 关联项目 |
| goal_amount | DECIMAL(12,2) | NOT NULL | 目标金额 |
| raised_amount | DECIMAL(12,2) | DEFAULT 0 | 已筹金额 |
| min_investment | DECIMAL(10,2) | DEFAULT 100 | 最低投资额 |
| equity_offered | DECIMAL(5,2) | | 出让股权% |
| investor_count | INTEGER | DEFAULT 0 | 投资人数 |
| start_date | TIMESTAMP | NOT NULL | 开始时间 |
| end_date | TIMESTAMP | NOT NULL | 结束时间 |
| status | ENUM | DEFAULT 'pending' | pending/active/success/failed/cancelled |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | ON UPDATE | 更新时间 |

### investments (投资记录表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 投资ID |
| user_id | UUID | FK → users.id | 投资人 |
| crowdfunding_id | UUID | FK → crowdfundings.id | 众筹项目 |
| order_no | VARCHAR(50) | UNIQUE, NOT NULL | 订单号 |
| amount | DECIMAL(12,2) | NOT NULL | 投资金额 |
| equity_share | DECIMAL(5,4) | | 获得股权比例 |
| payment_method | VARCHAR(20) | | alipay/wechat/bank |
| payment_status | ENUM | DEFAULT 'pending' | pending/paid/refunded |
| transaction_id | VARCHAR(100) | | 第三方交易号 |
| paid_at | TIMESTAMP | | 支付时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### partnerships (合伙关系表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 记录ID |
| project_id | UUID | FK → projects.id | 项目 |
| user_id | UUID | FK → users.id | 成员 |
| role | VARCHAR(50) | NOT NULL | founder/co-founder/tech/product/operation |
| title | VARCHAR(100) | | 职位名称 |
| equity | DECIMAL(5,2) | | 股权比例% |
| salary | VARCHAR(50) | | 薪资范围 |
| status | ENUM | DEFAULT 'pending' | pending/approved/rejected/left |
| apply_message | TEXT | | 申请留言 |
| joined_at | TIMESTAMP | | 加入时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | ON UPDATE | 更新时间 |

### messages (消息表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 消息ID |
| sender_id | UUID | FK → users.id | 发送者 |
| receiver_id | UUID | FK → users.id | 接收者 |
| content | TEXT | NOT NULL | 消息内容 |
| message_type | ENUM | DEFAULT 'text' | text/image/file |
| is_read | BOOLEAN | DEFAULT false | 是否已读 |
| read_at | TIMESTAMP | | 阅读时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 发送时间 |

### notifications (通知表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 通知ID |
| user_id | UUID | FK → users.id | 用户 |
| type | VARCHAR(50) | NOT NULL | 通知类型 |
| title | VARCHAR(200) | NOT NULL | 标题 |
| content | TEXT | | 内容 |
| data | JSONB | | 附加数据 |
| is_read | BOOLEAN | DEFAULT false | 是否已读 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### project_likes (项目点赞表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 记录ID |
| user_id | UUID | FK → users.id | 用户 |
| project_id | UUID | FK → projects.id | 项目 |
| created_at | TIMESTAMP | DEFAULT NOW() | 点赞时间 |
| | | UNIQUE(user_id, project_id) | 联合唯一 |

### project_favorites (项目收藏表)

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | UUID | PK | 记录ID |
| user_id | UUID | FK → users.id | 用户 |
| project_id | UUID | FK → projects.id | 项目 |
| created_at | TIMESTAMP | DEFAULT NOW() | 收藏时间 |
| | | UNIQUE(user_id, project_id) | 联合唯一 |

## 索引设计

```sql
-- users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- projects
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_category ON projects(category);
CREATE INDEX idx_projects_stage ON projects(stage);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- crowdfundings
CREATE INDEX idx_crowdfundings_status ON crowdfundings(status);
CREATE INDEX idx_crowdfundings_end_date ON crowdfundings(end_date);

-- investments
CREATE INDEX idx_investments_user_id ON investments(user_id);
CREATE INDEX idx_investments_crowdfunding_id ON investments(crowdfunding_id);
CREATE INDEX idx_investments_order_no ON investments(order_no);

-- partnerships
CREATE INDEX idx_partnerships_project_id ON partnerships(project_id);
CREATE INDEX idx_partnerships_user_id ON partnerships(user_id);
CREATE INDEX idx_partnerships_status ON partnerships(status);

-- messages
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_receiver_id ON messages(receiver_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- notifications
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
```

## ENUM 类型定义

```sql
CREATE TYPE user_role AS ENUM ('user', 'creator', 'investor', 'admin');
CREATE TYPE project_stage AS ENUM ('idea', 'building', 'funding', 'launched');
CREATE TYPE project_status AS ENUM ('draft', 'pending', 'published', 'closed');
CREATE TYPE crowdfunding_status AS ENUM ('pending', 'active', 'success', 'failed', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'refunded');
CREATE TYPE partnership_status AS ENUM ('pending', 'approved', 'rejected', 'left');
CREATE TYPE message_type AS ENUM ('text', 'image', 'file');
```
