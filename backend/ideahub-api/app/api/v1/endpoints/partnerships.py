"""
合伙人相关 API
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.schemas.partnership import (
    PartnershipApply, PartnershipResponse, PartnershipDetail, PartnershipList
)
from app.schemas.user import UserBrief
from app.services.partnership import PartnershipService
from app.models.user import User
from app.models.partnership import PartnershipStatus

router = APIRouter()


def partnership_to_detail(p) -> PartnershipDetail:
    """将合伙关系实体转换为详情响应"""
    user_brief = None
    if p.user:
        user_brief = UserBrief(
            id=p.user.id,
            nickname=p.user.nickname,
            avatar=p.user.avatar,
            role=p.user.role
        )

    return PartnershipDetail(
        id=p.id,
        project_id=p.project_id,
        user_id=p.user_id,
        role=p.role,
        position=p.position,
        responsibilities=p.responsibilities,
        equity_share=p.equity_share,
        application_message=p.application_message,
        status=p.status,
        created_at=p.created_at,
        user=user_brief
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "module": "partnerships"}


@router.post("", response_model=PartnershipDetail, status_code=status.HTTP_201_CREATED)
async def apply_partnership(
    data: PartnershipApply,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """申请成为合伙人"""
    service = PartnershipService(db)
    partnership = await service.apply(data, current_user)
    return partnership_to_detail(partnership)


@router.get("/my", response_model=PartnershipList)
async def get_my_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的申请列表"""
    service = PartnershipService(db)
    items, total = await service.get_my_applications(current_user.id, page, page_size)
    return PartnershipList(
        items=[partnership_to_detail(p) for p in items],
        total=total
    )


@router.get("/project/{project_id}", response_model=PartnershipList)
async def get_project_partnerships(
    project_id: UUID,
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取项目的合伙人/申请列表"""
    service = PartnershipService(db)
    ps_status = None
    if status_filter:
        try:
            ps_status = PartnershipStatus(status_filter)
        except ValueError:
            pass

    items, total = await service.get_project_partnerships(
        project_id, ps_status, page, page_size
    )
    return PartnershipList(
        items=[partnership_to_detail(p) for p in items],
        total=total
    )


@router.post("/{partnership_id}/approve", response_model=PartnershipDetail)
async def approve_partnership(
    partnership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """批准合伙人申请"""
    service = PartnershipService(db)
    partnership = await service.approve(partnership_id, current_user)
    return partnership_to_detail(partnership)


@router.post("/{partnership_id}/reject", response_model=PartnershipDetail)
async def reject_partnership(
    partnership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """拒绝合伙人申请"""
    service = PartnershipService(db)
    partnership = await service.reject(partnership_id, current_user)
    return partnership_to_detail(partnership)


@router.delete("/{partnership_id}")
async def cancel_application(
    partnership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消申请"""
    service = PartnershipService(db)
    await service.cancel(partnership_id, current_user)
    return {"message": "申请已取消"}


@router.post("/{partnership_id}/leave", response_model=PartnershipDetail)
async def leave_partnership(
    partnership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """退出合伙关系"""
    service = PartnershipService(db)
    partnership = await service.leave(partnership_id, current_user)
    return partnership_to_detail(partnership)
