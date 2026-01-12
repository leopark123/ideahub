"""
众筹相关 API
"""

from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.schemas.crowdfunding import (
    CrowdfundingCreate,
    CrowdfundingUpdate,
    CrowdfundingResponse,
    CrowdfundingDetail,
    CrowdfundingStats,
    CrowdfundingList,
)
from app.services.crowdfunding import CrowdfundingService
from app.models.user import User
from app.models.crowdfunding import CrowdfundingStatus
from app.repositories.crowdfunding import CrowdfundingRepository

router = APIRouter()


def crowdfunding_to_response(cf) -> CrowdfundingResponse:
    """将众筹实体转换为响应模型，包含项目标题和描述"""
    return CrowdfundingResponse(
        id=cf.id,
        project_id=cf.project_id,
        target_amount=cf.target_amount,
        current_amount=cf.current_amount,
        min_investment=cf.min_investment,
        max_investment=cf.max_investment,
        start_time=cf.start_time,
        end_time=cf.end_time,
        status=cf.status,
        investor_count=int(cf.investor_count) if cf.investor_count else 0,
        reward_tiers=cf.reward_tiers,
        created_at=cf.created_at,
        updated_at=cf.updated_at,
        title=cf.project.title if cf.project else None,
        description=cf.project.description if cf.project else None,
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "crowdfunding"}


@router.get("", response_model=CrowdfundingList)
async def list_crowdfundings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取众筹列表"""
    repo = CrowdfundingRepository(db)
    cf_status = None
    if status:
        try:
            cf_status = CrowdfundingStatus(status)
        except ValueError:
            pass
    items, total = await repo.list_crowdfundings(page, page_size, cf_status)
    return CrowdfundingList(
        items=[crowdfunding_to_response(cf) for cf in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/active", response_model=List[CrowdfundingResponse])
async def list_active_crowdfundings(db: AsyncSession = Depends(get_db)):
    """获取进行中的众筹列表"""
    service = CrowdfundingService(db)
    items = await service.list_active()
    return [crowdfunding_to_response(cf) for cf in items]


@router.post(
    "", response_model=CrowdfundingResponse, status_code=status.HTTP_201_CREATED
)
async def create_crowdfunding(
    data: CrowdfundingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建众筹活动"""
    service = CrowdfundingService(db)
    cf = await service.create_crowdfunding(data, current_user)
    # 重新加载以获取关联数据
    repo = CrowdfundingRepository(db)
    cf = await repo.get_by_id(cf.id)
    return crowdfunding_to_response(cf)


@router.get("/{crowdfunding_id}", response_model=CrowdfundingResponse)
async def get_crowdfunding(crowdfunding_id: UUID, db: AsyncSession = Depends(get_db)):
    """获取众筹详情"""
    service = CrowdfundingService(db)
    cf = await service.get_crowdfunding(crowdfunding_id)
    return crowdfunding_to_response(cf)


@router.get("/{crowdfunding_id}/stats", response_model=CrowdfundingStats)
async def get_crowdfunding_stats(
    crowdfunding_id: UUID, db: AsyncSession = Depends(get_db)
):
    """获取众筹统计"""
    service = CrowdfundingService(db)
    crowdfunding = await service.get_crowdfunding(crowdfunding_id)
    return service.get_stats(crowdfunding)


@router.get("/project/{project_id}", response_model=CrowdfundingResponse)
async def get_crowdfunding_by_project(
    project_id: UUID, db: AsyncSession = Depends(get_db)
):
    """根据项目获取众筹信息"""
    service = CrowdfundingService(db)
    cf = await service.get_by_project(project_id)
    return crowdfunding_to_response(cf)


@router.put("/{crowdfunding_id}", response_model=CrowdfundingResponse)
async def update_crowdfunding(
    crowdfunding_id: UUID,
    data: CrowdfundingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新众筹信息"""
    service = CrowdfundingService(db)
    cf = await service.update_crowdfunding(crowdfunding_id, data, current_user)
    repo = CrowdfundingRepository(db)
    cf = await repo.get_by_id(cf.id)
    return crowdfunding_to_response(cf)


@router.post("/{crowdfunding_id}/start", response_model=CrowdfundingResponse)
async def start_crowdfunding(
    crowdfunding_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """启动众筹"""
    service = CrowdfundingService(db)
    cf = await service.start_crowdfunding(crowdfunding_id, current_user)
    repo = CrowdfundingRepository(db)
    cf = await repo.get_by_id(cf.id)
    return crowdfunding_to_response(cf)
