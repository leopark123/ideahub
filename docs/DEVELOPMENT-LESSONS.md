# 开发经验教训

本文档记录开发过程中遇到的问题及其解决方案，避免重复犯错。

---

## 1. DateTime 时区不匹配问题

**日期**: 2026-01-10

**问题描述**:
创建众筹时报错 `can't subtract offset-naive and offset-aware datetimes`

**错误日志**:
```
sqlalchemy.exc.DBAPIError: can't subtract offset-naive and offset-aware datetimes
[parameters: (..., datetime.datetime(2026, 1, 11, 6, 39, tzinfo=TzInfo(0)), ...)]
```

**根本原因**:
1. 前端使用 `new Date().toISOString()` 发送日期时间，生成带 `Z` 后缀的 ISO 8601 格式（如 `2026-01-11T06:39:00.000Z`）
2. Pydantic 解析该字符串时会保留时区信息（`tzinfo=TzInfo(0)`）
3. PostgreSQL 数据库使用 `TIMESTAMP WITHOUT TIME ZONE` 类型，不接受带时区的 datetime
4. 代码中直接比较或存储带时区和不带时区的 datetime 导致错误

**解决方案**:
在 Service 层添加时区转换辅助方法：

```python
def _to_naive_utc(self, dt: datetime) -> datetime:
    """将日期时间转换为不带时区的UTC日期时间

    如果输入带时区信息，先转换为UTC再移除时区
    如果输入不带时区信息，假定已经是UTC
    """
    if dt.tzinfo is not None:
        # 先转换为UTC，再移除时区信息
        from datetime import timezone
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt.replace(tzinfo=None)
    return dt
```

**重要**：不能只用 `dt.replace(tzinfo=None)` 移除时区，必须先用 `astimezone(timezone.utc)` 转换为 UTC，否则时间值会错误。

**预防措施**:
1. **统一时区策略**: 项目应明确选择以下方案之一：
   - 方案A: 全部使用 UTC 不带时区（当前方案）
   - 方案B: 全部使用 `TIMESTAMP WITH TIME ZONE`

2. **Schema 层处理**: 可以在 Pydantic schema 中使用 validator 自动转换：
   ```python
   from pydantic import field_validator

   class CrowdfundingCreate(BaseModel):
       start_time: datetime

       @field_validator('start_time', 'end_time', mode='before')
       @classmethod
       def remove_timezone(cls, v):
           if isinstance(v, datetime) and v.tzinfo is not None:
               return v.replace(tzinfo=None)
           return v
   ```

3. **代码审查清单**: 涉及 datetime 字段时检查：
   - [ ] 前端发送的格式是什么？
   - [ ] 后端接收后的类型是否带时区？
   - [ ] 数据库字段类型是否匹配？
   - [ ] 比较操作的两个 datetime 类型是否一致？

---

## 2. SQLAlchemy 异步关系加载问题

**日期**: 2026-01-10

**问题描述**:
访问项目详情时显示"项目已被删除"，后端报 `MissingGreenlet` 错误

**错误日志**:
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called;
can't call await_only() here. Was IO attempted in an unexpected place?
```

**根本原因**:
1. SQLAlchemy 异步模式下，关系属性默认使用懒加载（lazy loading）
2. 在 `async` 上下文中访问未加载的关系属性会触发同步 IO，导致错误
3. 具体场景：`increment_view_count` 方法中修改并提交后，返回的 project 对象的关系属性（如 `owner`）未加载

**解决方案**:
在修改实体后重新加载完整数据：

```python
async def increment_view_count(self, project: Project) -> Project:
    project.view_count += 1
    await self.db.commit()
    # 重新加载以获取完整的关系数据
    return await self.get_by_id(project.id)
```

`get_by_id` 方法使用 `selectinload` 预加载所有需要的关系。

**预防措施**:
1. **查询时预加载**: 使用 `selectinload` 或 `joinedload` 预加载关系
   ```python
   query = select(Project).options(
       selectinload(Project.owner),
       selectinload(Project.crowdfunding)
   )
   ```

2. **修改后重新查询**: 任何修改实体的操作后，如果需要返回完整数据，应重新查询

3. **代码审查清单**: 涉及 SQLAlchemy 异步操作时检查：
   - [ ] 是否需要访问关系属性？
   - [ ] 查询时是否使用了 `selectinload`？
   - [ ] 修改后返回的对象是否包含所需的关系数据？

---

## 3. Repository 层 create/update 后必须重新加载

**日期**: 2026-01-10

**问题描述**:
在 Repository 的 `create` 和 `update` 方法中使用 `await self.db.refresh(entity)` 后，关系属性仍然未加载，导致后续访问关系时出错。

**错误示例**:
```python
async def create(self, crowdfunding: Crowdfunding) -> Crowdfunding:
    self.db.add(crowdfunding)
    await self.db.commit()
    await self.db.refresh(crowdfunding)  # ❌ 不会加载关系
    return crowdfunding
```

**根本原因**:
`db.refresh()` 只刷新实体的标量属性，不会加载关系属性。在异步模式下，后续访问 `crowdfunding.project` 等关系会失败。

**解决方案**:
使用 `get_by_id` 重新查询，该方法已配置 `selectinload` 预加载关系：

```python
async def create(self, crowdfunding: Crowdfunding) -> Crowdfunding:
    self.db.add(crowdfunding)
    await self.db.commit()
    # 重新加载以获取完整的关系数据
    return await self.get_by_id(crowdfunding.id)
```

**代码审查清单**:
- [ ] Repository 的 `create` 方法是否重新加载实体？
- [ ] Repository 的 `update` 方法是否重新加载实体？
- [ ] 返回的实体是否会被访问关系属性？

---

## 4. 前端代码质量问题

**日期**: 2026-01-10

**问题描述**:
代码审查时发现多个前端代码质量问题。

### 4.1 调试代码未清理

**问题**: 生产代码中包含 `console.log()` 调试语句

**解决方案**: 提交前删除所有 `console.log()`，仅保留 `console.error()` 用于错误日志

### 4.2 TypeScript 类型不安全

**问题**: 使用 `unknown[]` 或 `as` 强制类型转换

**错误示例**:
```typescript
getMyProjects: async (): Promise<{ items: unknown[]; total: number }> => {
```

**解决方案**: 定义具体类型并正确使用泛型
```typescript
getMyProjects: async (): Promise<{ items: Project[]; total: number }> => {
  const response = await apiClient.get<{ items: Project[]; total: number }>('/users/me/projects');
  return response.data;
}
```

### 4.3 错误类型处理

**问题**: 使用 `as` 强制转换错误类型不安全

**解决方案**: 创建统一的错误处理工具函数
```typescript
// utils/errorHandler.ts
export function getApiErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response?: { data?: { detail?: string } } }).response;
    return response?.data?.detail || '操作失败，请稍后再试';
  }
  return '网络错误，请检查连接';
}
```

**代码审查清单**:
- [ ] 是否有未删除的 `console.log()`？
- [ ] API 返回类型是否使用了具体类型而非 `unknown`？
- [ ] 错误处理是否完整且类型安全？

---

## 通用开发原则

### 前后端数据交互
1. 明确数据类型和格式（特别是日期、数字、枚举）
2. 后端不应假设前端发送的数据格式，应进行验证和转换
3. 错误信息应该清晰明确，便于调试

### SQLAlchemy 异步最佳实践
1. 永远使用 eager loading（预加载）而非 lazy loading
2. 在 repository 层统一处理关系加载
3. 修改操作后如需返回完整对象，重新查询

### 调试技巧
1. 查看 Docker 日志: `docker-compose logs --tail=100 backend`
2. 检查具体错误信息中的参数类型
3. 在不确定时打印变量类型: `print(type(variable), variable)`
