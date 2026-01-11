"""
项目模型
"""
import uuid
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    ACTIVE = "active"         # 已发布
    FUNDING = "funding"       # 众筹中
    FUNDED = "funded"         # 众筹成功
    FAILED = "failed"         # 众筹失败
    COMPLETED = "completed"   # 已完成
    ARCHIVED = "archived"     # 已归档


class ProjectCategory(str, enum.Enum):
    TECH = "tech"             # 科技
    ART = "art"               # 艺术
    EDUCATION = "education"   # 教育
    HEALTH = "health"         # 健康
    SOCIAL = "social"         # 社会公益
    ENTERTAINMENT = "entertainment"  # 娱乐
    FINANCE = "finance"       # 金融
    OTHER = "other"           # 其他


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 基本信息
    title = Column(String(200), nullable=False)
    subtitle = Column(String(500), nullable=True)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(ProjectCategory), default=ProjectCategory.OTHER)

    # 媒体
    cover_image = Column(String(500), nullable=True)
    images = Column(Text, nullable=True)  # JSON 格式存储多张图片
    video_url = Column(String(500), nullable=True)

    # 需求
    required_skills = Column(Text, nullable=True)  # JSON 格式存储所需技能
    team_size = Column(Integer, default=1)

    # 状态
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

    # 关系
    owner = relationship("User", back_populates="projects")
    crowdfunding = relationship("Crowdfunding", back_populates="project", uselist=False)
    partnerships = relationship("Partnership", back_populates="project", lazy="dynamic")
