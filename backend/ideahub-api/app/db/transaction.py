"""
事务管理工具

提供显式事务控制，确保多个数据库操作的原子性。

使用示例:
    async with TransactionManager(db) as tx:
        await repo1.create(entity1)
        await repo2.update(entity2)
        # 自动提交或回滚
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


class TransactionManager:
    """
    事务管理器 - 确保操作原子性
    
    用法:
        async with TransactionManager(db) as tx:
            # 所有数据库操作在同一事务中
            await tx.session.execute(...)
            # 成功则自动提交，异常则自动回滚
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._savepoint = None
    
    async def __aenter__(self):
        # 创建保存点，支持嵌套事务
        self._savepoint = await self.session.begin_nested()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 有异常，回滚到保存点
            await self._savepoint.rollback()
            return False  # 重新抛出异常
        else:
            # 无异常，提交保存点
            await self._savepoint.commit()
            return True
    
    async def commit(self):
        """手动提交事务"""
        await self.session.commit()
    
    async def rollback(self):
        """手动回滚事务"""
        await self.session.rollback()


@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    事务上下文管理器 - 函数式风格
    
    用法:
        async with transaction(db) as session:
            session.add(entity)
            # 自动提交或回滚
    """
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


class UnitOfWork:
    """
    工作单元模式 - 管理一组相关的数据库操作
    
    用法:
        async with UnitOfWork(db) as uow:
            investment = Investment(...)
            uow.session.add(investment)
            crowdfunding.current_amount += amount
            uow.session.add(crowdfunding)
            await uow.commit()
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
            return False
        
        # 如果没有显式提交，自动回滚（避免意外提交）
        if not self._committed:
            await self.rollback()
    
    async def commit(self):
        """提交所有更改"""
        await self.session.commit()
        self._committed = True
    
    async def rollback(self):
        """回滚所有更改"""
        await self.session.rollback()
    
    def add(self, entity):
        """添加实体到会话"""
        self.session.add(entity)
    
    def add_all(self, entities):
        """添加多个实体到会话"""
        self.session.add_all(entities)
