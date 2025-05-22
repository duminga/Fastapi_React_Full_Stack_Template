import os
from dotenv import load_dotenv
from pathlib import Path


# 加载 .env 文件
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

class Settings:
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    TORTOISE_ORM_DATABASE_URL: str = os.getenv("TORTOISE_ORM_DATABASE_URL")

    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # JWT 配置
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTE: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # 应用配置
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI Full Stack Template")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    BACKEND_CORS_ORIGINS: list = eval(os.getenv("BACKEND_CORS_ORIGINS", "[]"))

    # 初始管理员信息
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD")

settings = Settings()