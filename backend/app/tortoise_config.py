from app.core.config import settings
from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": settings.TORTOISE_ORM_DATABASE_URL
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.role",
                "app.models.permission",
                "aerich.models"
            ],
            "default_connection": "default",
        }
    }
}

async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(config=TORTOISE_ORM)
    # 创建数据库表
    await Tortoise.generate_schemas()

async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections() 