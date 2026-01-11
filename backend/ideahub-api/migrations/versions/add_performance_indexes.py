"""Add performance indexes for foreign keys

Revision ID: add_perf_indexes
Revises: 650cb94b2f2a
Create Date: 2026-01-11

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'add_perf_indexes'
down_revision: Union[str, None] = '650cb94b2f2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    添加性能索引
    
    索引策略:
    1. 所有外键字段都需要索引 (加速 JOIN 和 WHERE 查询)
    2. 常用查询条件组合使用复合索引
    3. 时间排序字段添加索引
    """
    
    # ========== projects 表 ==========
    # 外键索引: owner_id 用于查询用户的项目
    op.create_index('ix_projects_owner_id', 'projects', ['owner_id'])
    # 复合索引: 按状态筛选 + 时间排序
    op.create_index('ix_projects_status_created', 'projects', ['status', 'created_at'])
    # 分类筛选索引
    op.create_index('ix_projects_category', 'projects', ['category'])
    
    # ========== messages 表 ==========
    # 外键索引
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'])
    op.create_index('ix_messages_receiver_id', 'messages', ['receiver_id'])
    op.create_index('ix_messages_project_id', 'messages', ['project_id'])
    # 复合索引: 查询会话消息 (双向)
    op.create_index(
        'ix_messages_conversation', 
        'messages', 
        ['sender_id', 'receiver_id', 'created_at']
    )
    # 复合索引: 未读消息查询
    op.create_index(
        'ix_messages_unread', 
        'messages', 
        ['receiver_id', 'is_read', 'sender_id']
    )
    
    # ========== partnerships 表 ==========
    # 外键索引
    op.create_index('ix_partnerships_project_id', 'partnerships', ['project_id'])
    op.create_index('ix_partnerships_user_id', 'partnerships', ['user_id'])
    # 复合索引: 按项目和状态查询
    op.create_index(
        'ix_partnerships_project_status', 
        'partnerships', 
        ['project_id', 'status']
    )
    # 复合索引: 用户的申请列表
    op.create_index(
        'ix_partnerships_user_status', 
        'partnerships', 
        ['user_id', 'status', 'created_at']
    )
    
    # ========== investments 表 ==========
    # 外键索引
    op.create_index('ix_investments_investor_id', 'investments', ['investor_id'])
    op.create_index('ix_investments_crowdfunding_id', 'investments', ['crowdfunding_id'])
    # 复合索引: 众筹的投资记录 + 状态筛选
    op.create_index(
        'ix_investments_cf_status', 
        'investments', 
        ['crowdfunding_id', 'status']
    )
    # 复合索引: 用户的投资记录
    op.create_index(
        'ix_investments_investor_created', 
        'investments', 
        ['investor_id', 'created_at']
    )
    
    # ========== crowdfundings 表 ==========
    # 状态和时间索引 (project_id 已有 UNIQUE 约束)
    op.create_index('ix_crowdfundings_status', 'crowdfundings', ['status'])
    op.create_index('ix_crowdfundings_end_time', 'crowdfundings', ['end_time'])


def downgrade() -> None:
    """移除所有性能索引"""
    # crowdfundings
    op.drop_index('ix_crowdfundings_end_time', table_name='crowdfundings')
    op.drop_index('ix_crowdfundings_status', table_name='crowdfundings')
    
    # investments
    op.drop_index('ix_investments_investor_created', table_name='investments')
    op.drop_index('ix_investments_cf_status', table_name='investments')
    op.drop_index('ix_investments_crowdfunding_id', table_name='investments')
    op.drop_index('ix_investments_investor_id', table_name='investments')
    
    # partnerships
    op.drop_index('ix_partnerships_user_status', table_name='partnerships')
    op.drop_index('ix_partnerships_project_status', table_name='partnerships')
    op.drop_index('ix_partnerships_user_id', table_name='partnerships')
    op.drop_index('ix_partnerships_project_id', table_name='partnerships')
    
    # messages
    op.drop_index('ix_messages_unread', table_name='messages')
    op.drop_index('ix_messages_conversation', table_name='messages')
    op.drop_index('ix_messages_project_id', table_name='messages')
    op.drop_index('ix_messages_receiver_id', table_name='messages')
    op.drop_index('ix_messages_sender_id', table_name='messages')
    
    # projects
    op.drop_index('ix_projects_category', table_name='projects')
    op.drop_index('ix_projects_status_created', table_name='projects')
    op.drop_index('ix_projects_owner_id', table_name='projects')
