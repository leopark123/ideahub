"""
合伙人服务
"""
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partnership import Partnership, PartnershipStatus
from app.models.user import User
from app.schemas.partnership import PartnershipApply, PartnershipUpdate
from app.repositories.partnership import PartnershipRepository
from app.repositories.project import ProjectRepository


class PartnershipService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PartnershipRepository(db)
        self.project_repo = ProjectRepository(db)

    async def apply(
        self,
        data: PartnershipApply,
        current_user: User
    ) -> Partnership:
        # 检查项目是否存在
        project = await self.project_repo.get_by_id(data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )

        # 不能申请自己的项目
        if project.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能申请加入自己的项目"
            )

        # 检查是否已申请
        existing = await self.repo.get_by_user_and_project(
            current_user.id, data.project_id
        )
        if existing:
            if existing.status == PartnershipStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="您已提交过申请，请等待审核"
                )
            elif existing.status == PartnershipStatus.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="您已是该项目的合伙人"
                )
            elif existing.status == PartnershipStatus.REJECTED:
                # 允许重新申请，更新状态
                existing.status = PartnershipStatus.PENDING
                existing.role = data.role
                existing.position = data.position
                existing.application_message = data.application_message
                return await self.repo.update(existing)

        partnership = Partnership(
            project_id=data.project_id,
            user_id=current_user.id,
            role=data.role,
            position=data.position,
            application_message=data.application_message,
            status=PartnershipStatus.PENDING
        )

        return await self.repo.create(partnership)

    async def approve(
        self,
        partnership_id: UUID,
        current_user: User
    ) -> Partnership:
        partnership = await self.repo.get_by_id(partnership_id)
        if not partnership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请不存在"
            )

        # 检查权限：只有项目创建者可以审批
        project = await self.project_repo.get_by_id(partnership.project_id)
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限审批此申请"
            )

        if partnership.status != PartnershipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该申请已处理"
            )

        partnership.status = PartnershipStatus.APPROVED
        return await self.repo.update(partnership)

    async def reject(
        self,
        partnership_id: UUID,
        current_user: User
    ) -> Partnership:
        partnership = await self.repo.get_by_id(partnership_id)
        if not partnership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请不存在"
            )

        # 检查权限
        project = await self.project_repo.get_by_id(partnership.project_id)
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限审批此申请"
            )

        if partnership.status != PartnershipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该申请已处理"
            )

        partnership.status = PartnershipStatus.REJECTED
        return await self.repo.update(partnership)

    async def cancel(
        self,
        partnership_id: UUID,
        current_user: User
    ) -> None:
        partnership = await self.repo.get_by_id(partnership_id)
        if not partnership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请不存在"
            )

        # 只有申请人可以取消
        if partnership.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限取消此申请"
            )

        if partnership.status != PartnershipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能取消待审核的申请"
            )

        await self.db.delete(partnership)
        await self.db.commit()

    async def leave(
        self,
        partnership_id: UUID,
        current_user: User
    ) -> Partnership:
        partnership = await self.repo.get_by_id(partnership_id)
        if not partnership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="合伙关系不存在"
            )

        if partnership.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限操作"
            )

        if partnership.status != PartnershipStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您不是该项目的合伙人"
            )

        partnership.status = PartnershipStatus.LEFT
        return await self.repo.update(partnership)

    async def get_project_partnerships(
        self,
        project_id: UUID,
        status_filter: PartnershipStatus = None,
        page: int = 1,
        page_size: int = 20
    ):
        return await self.repo.get_by_project(project_id, status_filter, page, page_size)

    async def get_my_applications(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20
    ):
        return await self.repo.get_by_user(user_id, None, page, page_size)
