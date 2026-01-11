"""
项目相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.project import ProjectStatus, ProjectCategory
from app.schemas.user import UserBrief


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=500)
    description: str = Field(..., min_length=10)
    category: ProjectCategory = ProjectCategory.OTHER


class ProjectCreate(ProjectBase):
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None
    required_skills: Optional[List[str]] = None
    team_size: int = Field(default=1, ge=1)


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    category: Optional[ProjectCategory] = None
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None
    required_skills: Optional[List[str]] = None
    team_size: Optional[int] = Field(None, ge=1)
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    id: UUID
    owner_id: UUID
    cover_image: Optional[str] = None
    images: Optional[str] = None
    video_url: Optional[str] = None
    required_skills: Optional[str] = None
    team_size: int
    status: ProjectStatus
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetail(ProjectResponse):
    owner: UserBrief


class ProjectList(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int


class ProjectFilter(BaseModel):
    category: Optional[ProjectCategory] = None
    status: Optional[ProjectStatus] = None
    keyword: Optional[str] = None
    owner_id: Optional[UUID] = None
