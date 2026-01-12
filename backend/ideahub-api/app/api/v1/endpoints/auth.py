"""
认证相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.user import Token, UserLogin, UserRegister, UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "auth"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    service = AuthService(db)
    user = await service.register(data)
    return user


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    service = AuthService(db)
    return await service.login(data)


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """用户登录 (OAuth2 表单格式)"""
    service = AuthService(db)
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await service.login(login_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """刷新 Token"""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
        )

    user_id = payload.get("sub")
    service = AuthService(db)
    return await service.refresh_token(user_id)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # TODO: 可以在这里将 token 加入黑名单（使用 Redis）
    return {"message": "登出成功"}
