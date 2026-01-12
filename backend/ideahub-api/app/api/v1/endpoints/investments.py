"""
投资相关 API
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.investment import InvestmentCreate, InvestmentList, InvestmentResponse
from app.services.investment import InvestmentService

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "investments"}


@router.post("", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
async def create_investment(
    data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建投资"""
    service = InvestmentService(db)
    return await service.create_investment(data, current_user)


@router.get("/my", response_model=InvestmentList)
async def get_my_investments(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取我的投资列表"""
    service = InvestmentService(db)
    items, total = await service.get_user_investments(current_user.id, page, page_size)
    return InvestmentList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{investment_id}", response_model=InvestmentResponse)
async def get_investment(
    investment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取投资详情"""
    service = InvestmentService(db)
    return await service.get_investment(investment_id)


@router.post("/{investment_id}/confirm", response_model=InvestmentResponse)
async def confirm_investment(
    investment_id: UUID, transaction_id: str, db: AsyncSession = Depends(get_db)
):
    """确认投资支付（模拟支付回调）"""
    service = InvestmentService(db)
    return await service.confirm_investment(investment_id, transaction_id)
