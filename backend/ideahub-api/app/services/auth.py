"""
认证服务
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token
from app.repositories.user import UserRepository
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: UserRegister) -> User:
        # 检查邮箱是否已存在
        if await self.user_repo.exists_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )

        # 创建用户
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            nickname=data.nickname or data.email.split("@")[0]
        )

        return await self.user_repo.create(user)

    async def login(self, data: UserLogin) -> Token:
        # 查找用户
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )

        # 验证密码
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )

        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已被禁用"
            )

        # 生成 token
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_token(self, user_id: str) -> Token:
        """
        刷新 Token

        安全措施:
        - 验证用户是否存在
        - 验证用户是否仍然活跃
        - 防止已禁用/删除用户继续获取新 token
        """
        from uuid import UUID

        # 验证用户是否存在且活跃
        try:
            user = await self.user_repo.get_by_id(UUID(user_id))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户标识"
            )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用"
            )

        # 生成新 token
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
