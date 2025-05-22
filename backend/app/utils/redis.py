from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings
from app.utils.log_server import logServer

logger = logServer().run()

class RedisClient:
    """
    Redis客户端工具类
    """
    _instance = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        """
        单例模式
        @return: RedisClient Redis客户端实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init(self):
        """
        初始化Redis连接
        @return: None
        @exception: Exception Redis连接异常
        """
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            await self._client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise

    async def close(self):
        """
        关闭Redis连接
        @return: None
        """
        if self._client:
            await self._client.close()
            logger.info("Redis连接已关闭")

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值对
        @param: key 键
        @param: value 值
        @param: expire 过期时间(秒)
        @return: bool 是否成功
        """
        try:
            await self._client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis设置键值对失败: {str(e)}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """
        获取键值
        @param: key 键
        @return: Optional[str] 值
        """
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.error(f"Redis获取键值失败: {str(e)}")
            return None

    async def delete(self, key: str) -> bool:
        """
        删除键
        @param: key 键
        @return: bool 是否成功
        """
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis删除键失败: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """
        检查键是否存在
        @param: key 键
        @return: bool 是否存在
        """
        try:
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis检查键失败: {str(e)}")
            return False 