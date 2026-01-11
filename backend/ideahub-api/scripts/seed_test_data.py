"""
创建测试数据脚本
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.user import User
from app.models.project import Project, ProjectStatus, ProjectCategory
from app.models.crowdfunding import Crowdfunding, CrowdfundingStatus
from app.models.message import Message, MessageType
from app.models.investment import Investment, InvestmentStatus, PaymentMethod
import bcrypt


def hash_password(password: str) -> str:
    """简单的密码哈希函数"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def create_test_data():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 创建测试用户
        users = []
        user_data = [
            {"email": "alice@test.com", "nickname": "Alice", "bio": "全栈开发工程师，5年经验", "skills": '["Python", "React", "Node.js"]'},
            {"email": "bob@test.com", "nickname": "Bob", "bio": "产品经理，专注于用户体验设计", "skills": '["产品设计", "用户研究", "项目管理"]'},
            {"email": "charlie@test.com", "nickname": "Charlie", "bio": "UI/UX设计师，热爱创新", "skills": '["Figma", "Sketch", "用户体验"]'},
            {"email": "david@test.com", "nickname": "David", "bio": "市场营销专家，擅长增长黑客", "skills": '["市场营销", "数据分析", "内容运营"]'},
            {"email": "eve@test.com", "nickname": "Eve", "bio": "数据分析师，Python爱好者", "skills": '["Python", "数据分析", "机器学习"]'},
        ]

        for data in user_data:
            user = User(
                id=uuid4(),
                email=data["email"],
                nickname=data["nickname"],
                bio=data["bio"],
                hashed_password=hash_password("test123"),
                is_active=True,
                is_verified=True,
                skills=data["skills"],
            )
            db.add(user)
            users.append(user)

        await db.commit()
        print(f"✓ 创建了 {len(users)} 个测试用户")

        # 创建测试项目
        projects = []
        project_data = [
            {
                "title": "智能家居控制系统",
                "subtitle": "让你的家更智能",
                "description": "基于物联网技术的智能家居控制系统，支持语音控制、远程操控、自动化场景等功能。我们正在寻找有经验的嵌入式开发工程师和移动端开发者加入团队。",
                "category": ProjectCategory.TECH,
                "required_skills": '["IoT", "嵌入式开发", "React Native"]',
                "team_size": 5,
                "owner_idx": 0,
            },
            {
                "title": "在线艺术教育平台",
                "subtitle": "让艺术触手可及",
                "description": "为艺术爱好者提供专业的在线课程，包括绘画、音乐、摄影等领域。平台支持实时互动教学和作品分享社区。",
                "category": ProjectCategory.EDUCATION,
                "required_skills": '["视频处理", "直播技术", "社区运营"]',
                "team_size": 4,
                "owner_idx": 1,
            },
            {
                "title": "健康饮食管理App",
                "subtitle": "科学饮食，健康生活",
                "description": "通过AI算法分析用户的饮食习惯，提供个性化的营养建议和食谱推荐。支持食物识别、营养成分查询等功能。",
                "category": ProjectCategory.HEALTH,
                "required_skills": '["机器学习", "iOS开发", "营养学"]',
                "team_size": 3,
                "owner_idx": 2,
            },
            {
                "title": "社区公益互助平台",
                "subtitle": "邻里互助，温暖社区",
                "description": "连接社区居民，提供互助服务发布、志愿者招募、物品共享等功能，打造温暖有爱的社区氛围。",
                "category": ProjectCategory.SOCIAL,
                "required_skills": '["小程序开发", "地图API", "社区运营"]',
                "team_size": 4,
                "owner_idx": 3,
            },
            {
                "title": "独立音乐人推广平台",
                "subtitle": "让好音乐被更多人听到",
                "description": "为独立音乐人提供作品展示、粉丝互动、演出信息发布等服务，帮助优秀的独立音乐人获得更多曝光机会。",
                "category": ProjectCategory.ENTERTAINMENT,
                "required_skills": '["音频处理", "推荐算法", "社交功能"]',
                "team_size": 5,
                "owner_idx": 4,
            },
            {
                "title": "个人理财助手",
                "subtitle": "轻松管理你的财务",
                "description": "帮助用户记录收支、分析消费习惯、制定理财计划。支持银行账单导入、智能分类、可视化报表等功能。",
                "category": ProjectCategory.FINANCE,
                "required_skills": '["数据可视化", "金融知识", "安全开发"]',
                "team_size": 3,
                "owner_idx": 0,
            },
        ]

        for data in project_data:
            project = Project(
                id=uuid4(),
                owner_id=users[data["owner_idx"]].id,
                title=data["title"],
                subtitle=data["subtitle"],
                description=data["description"],
                category=data["category"],
                required_skills=data["required_skills"],
                team_size=data["team_size"],
                status=ProjectStatus.ACTIVE,
                view_count=50 + hash(data["title"]) % 200,
                like_count=10 + hash(data["title"]) % 50,
            )
            db.add(project)
            projects.append(project)

        await db.commit()
        print(f"✓ 创建了 {len(projects)} 个测试项目")

        # 为部分项目创建众筹
        crowdfundings = []
        cf_data = [
            {"project_idx": 0, "target": 50000, "current": 32000, "investors": 45},
            {"project_idx": 2, "target": 30000, "current": 18500, "investors": 28},
            {"project_idx": 4, "target": 80000, "current": 45000, "investors": 62},
        ]

        for data in cf_data:
            cf = Crowdfunding(
                id=uuid4(),
                project_id=projects[data["project_idx"]].id,
                target_amount=Decimal(data["target"]),
                current_amount=Decimal(data["current"]),
                min_investment=Decimal(100),
                max_investment=Decimal(10000),
                investor_count=data["investors"],
                status=CrowdfundingStatus.ACTIVE,
                start_time=datetime.utcnow() - timedelta(days=10),
                end_time=datetime.utcnow() + timedelta(days=20),
            )
            db.add(cf)
            crowdfundings.append(cf)

            # 更新项目状态为众筹中
            projects[data["project_idx"]].status = ProjectStatus.FUNDING

        await db.commit()
        print(f"✓ 创建了 {len(crowdfundings)} 个众筹活动")

        # 创建一些消息
        messages = [
            {"sender_idx": 1, "receiver_idx": 0, "content": "你好，我对你的智能家居项目很感兴趣，能详细介绍一下吗？"},
            {"sender_idx": 0, "receiver_idx": 1, "content": "当然可以！我们计划开发一套完整的智能家居解决方案..."},
            {"sender_idx": 2, "receiver_idx": 0, "content": "Alice，我是UI设计师，想申请加入你的团队"},
            {"sender_idx": 3, "receiver_idx": 1, "content": "Bob，你的艺术教育平台什么时候上线？"},
            {"sender_idx": 4, "receiver_idx": 2, "content": "健康饮食App的AI模型是自研的吗？"},
        ]

        for data in messages:
            msg = Message(
                id=uuid4(),
                sender_id=users[data["sender_idx"]].id,
                receiver_id=users[data["receiver_idx"]].id,
                content=data["content"],
                message_type=MessageType.TEXT,
                is_read=False,
            )
            db.add(msg)

        await db.commit()
        print(f"✓ 创建了 {len(messages)} 条测试消息")

        # 创建一些投资记录
        investments = []
        for i, cf in enumerate(crowdfundings):
            for j in range(3):
                investor_idx = (i + j + 1) % len(users)
                inv = Investment(
                    id=uuid4(),
                    investor_id=users[investor_idx].id,
                    crowdfunding_id=cf.id,
                    amount=Decimal(500 + j * 200),
                    payment_method=PaymentMethod.ALIPAY,
                    status=InvestmentStatus.CONFIRMED,
                    transaction_id=f"TXN_{uuid4().hex[:12]}",
                )
                db.add(inv)
                investments.append(inv)

        await db.commit()
        print(f"✓ 创建了 {len(investments)} 条投资记录")

        print("\n" + "="*50)
        print("测试数据创建完成！")
        print("="*50)
        print("\n测试账号（密码都是 test123）：")
        for user in users:
            print(f"  - {user.email}")
        print()


if __name__ == "__main__":
    asyncio.run(create_test_data())
