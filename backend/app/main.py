from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging as py_logging
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.handlers import (
    validation_exception_handler,
    api_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.core.exceptions import BaseAPIException
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException
from app.middlewares.rbac_middleware import RBACMiddleware
from app.utils.log_server import logServer
from app.tortoise_config import init_db, close_db
from app.utils.redis import RedisClient

logger = logServer().run()

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(BaseAPIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册RBAC中间件
app.add_middleware(RBACMiddleware)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# 替换 uvicorn 的 handler，让uvicorn日志也走自定义日志组件
uvicorn_logger = py_logging.getLogger("uvicorn")
uvicorn_access_logger = py_logging.getLogger("uvicorn.access")
uvicorn_logger.handlers = []
uvicorn_access_logger.handlers = []
for handler in logger.handlers:
    uvicorn_logger.addHandler(handler)
    uvicorn_access_logger.addHandler(handler)

@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    """
    # 初始化数据库连接
    await init_db()
    
    # 初始化Redis连接
    redis_client = RedisClient()
    await redis_client.init()
    
    # 输出数据库配置
    logger.debug(f"数据库配置:{settings.DATABASE_URL}")
    logger.debug(f"Tortoise ORM URL:{settings.TORTOISE_ORM_DATABASE_URL}")
    
    # 输出Redis配置
    logger.debug(f"Redis配置:{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    logger.debug(f"访问令牌过期时间: {settings.ACCESS_TOKEN_EXPIRE_MINUTE}分钟,刷新令牌过期时间: {settings.REFRESH_TOKEN_EXPIRE_DAYS}天")
    
    # 输出CORS配置
    logger.debug(f"CORS允许的源: {settings.BACKEND_CORS_ORIGINS}")
    
    logger.info("应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件
    """
    # 关闭数据库连接
    await close_db()
    
    # 关闭Redis连接
    redis_client = RedisClient()
    await redis_client.close()
    
    logger.info("应用关闭完成")
