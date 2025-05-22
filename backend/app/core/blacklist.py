from datetime import datetime, timedelta
from typing import Optional
from app.utils.redis import RedisClient
from app.core.config import settings
from app.utils.log_server import logServer

logger = logServer().run()

class TokenBlacklist:
    """
    令牌黑名单管理类
    """
    def __init__(self):
        """
        初始化黑名单管理器
        """
        self.redis = RedisClient()
        self.prefix = "token_blacklist:"

    async def add_to_blacklist(self, token: str, expire_seconds: Optional[int] = None) -> bool:
        """
        将令牌添加到黑名单
        @param: token JWT令牌
        @param: expire_seconds 过期时间(秒)
        @return: bool 是否成功
        """
        try:
            key = f"{self.prefix}{token}"
            if expire_seconds is None:
                expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            
            success = await self.redis.set(key, "1", expire=expire_seconds)
            if success:
                logger.info(f"令牌已加入黑名单: {token[:10]}...")
            return success
        except Exception as e:
            logger.error(f"添加令牌到黑名单失败: {str(e)}")
            return False

    async def is_blacklisted(self, token: str) -> bool:
        """
        检查令牌是否在黑名单中
        @param: token JWT令牌
        @return: bool 是否在黑名单中
        """
        try:
            key = f"{self.prefix}{token}"
            return await self.redis.exists(key)
        except Exception as e:
            logger.error(f"检查令牌黑名单失败: {str(e)}")
            return False

    async def remove_from_blacklist(self, token: str) -> bool:
        """
        从黑名单中移除令牌
        @param: token JWT令牌
        @return: bool 是否成功
        """
        try:
            key = f"{self.prefix}{token}"
            success = await self.redis.delete(key)
            if success:
                logger.info(f"令牌已从黑名单移除: {token[:10]}...")
            return success
        except Exception as e:
            logger.error(f"从黑名单移除令牌失败: {str(e)}")
            return False

# 创建黑名单管理器实例
token_blacklist = TokenBlacklist() 