import asyncio
import bcrypt
from tortoise import Tortoise
from app.core.config import settings
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.tortoise_config import TORTOISE_ORM

async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def create_initial_data():
    """创建初始数据"""
    # 创建超级管理员角色
    super_admin_role = await Role.create(
        name="超级管理员",
        code="super_admin",
        description="系统超级管理员，拥有所有权限"
    )

    # 创建基本权限
    permissions = [
        {
            "name": "用户管理",
            "code": "user_manage",
            "description": "用户的增删改查权限"
        },
        {
            "name": "角色管理",
            "code": "role_manage",
            "description": "角色的增删改查权限"
        },
        {
            "name": "权限管理",
            "code": "permission_manage",
            "description": "权限的增删改查权限"
        }
    ]

    for perm_data in permissions:
        permission = await Permission.create(**perm_data)
        await super_admin_role.permissions.add(permission)

    # 创建超级管理员用户
    password = settings.FIRST_SUPERUSER_PASSWORD.encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    
    super_admin = await User.create(
        email=settings.FIRST_SUPERUSER,
        password=hashed.decode('utf-8'),
        is_active=True,
        is_superuser=True
    )
    
    await super_admin.roles.add(super_admin_role)

async def init():
    """初始化数据库和创建初始数据"""
    await init_db()
    await create_initial_data()
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(init()) 