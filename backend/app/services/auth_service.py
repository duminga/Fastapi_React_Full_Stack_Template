from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status
from app.models.user import User
from app.core.config import settings
from app.core.blacklist import token_blacklist
from app.utils.log_server import logServer

logger = logServer().run()

class AuthService:
    """
    认证服务类
    """
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        @param: plain_password 明文密码
        @param: hashed_password 哈希密码
        @return: bool 验证结果
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        获取密码哈希值
        @param: password 明文密码
        @return: str 哈希密码
        """
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        @param: data 令牌数据
        @param: expires_delta 过期时间
        @return: str JWT令牌
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        创建刷新令牌
        @param: data 令牌数据
        @return: str JWT令牌
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def verify_token(token: str, token_type: str = "access") -> bool:
        """
        验证令牌
        @param: token JWT令牌
        @param: token_type 令牌类型
        @return: bool 是否有效
        """
        # 检查令牌是否在黑名单中
        if await token_blacklist.is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已失效",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 验证令牌
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 验证令牌类型
        if token_type == "refresh" and payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 检查用户是否存在
        user = await User.get_or_none(username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return True

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        认证用户
        @param: username 用户名
        @param: password 密码
        @return: Optional[User] 用户对象
        """
        user = await User.get_or_none(username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not AuthService.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user

    @staticmethod
    async def register_user(username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        注册新用户
        @param: username 用户名
        @param: email 邮箱
        @param: password 密码
        @param: full_name 全名
        @return: User 用户对象
        """
        # 检查用户名是否已存在
        if await User.filter(username=username).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if await User.filter(email=email).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

        # 创建新用户
        hashed_password = AuthService.get_password_hash(password)
        user = await User.create(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        return user

    @staticmethod
    async def login(username: str, password: str, remember: bool = False) -> Tuple[str, str, int]:
        """
        用户登录
        @param: username 用户名
        @param: password 密码
        @param: remember 是否记住登录
        @return: Tuple[str, str, int] (访问令牌, 刷新令牌, 过期时间)
        """
        user = await AuthService.authenticate_user(username, password)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已被禁用"
            )

        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
        access_token = AuthService.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        # 如果选择记住登录，创建刷新令牌
        refresh_token = ""
        if remember:
            refresh_token = AuthService.create_refresh_token(
                data={"sub": user.username}
            )
        
        return access_token, refresh_token, settings.ACCESS_TOKEN_EXPIRE_MINUTE * 60

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Tuple[str, str, int]:
        """
        刷新访问令牌
        @param: refresh_token 刷新令牌
        @return: Tuple[str, str, int] (访问令牌, 刷新令牌, 过期时间)
        """
        # 验证刷新令牌
        if not await AuthService.verify_token(refresh_token, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 解码刷新令牌
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )

        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
        access_token = AuthService.create_access_token(
            data={"sub": username},
            expires_delta=access_token_expires
        )

        # 创建新的刷新令牌
        new_refresh_token = AuthService.create_refresh_token(
            data={"sub": username}
        )

        return access_token, new_refresh_token, settings.ACCESS_TOKEN_EXPIRE_MINUTE * 60

    @staticmethod
    async def logout(token: str) -> bool:
        """
        用户登出
        @param: token JWT令牌
        @return: bool 是否成功
        """
        # 将令牌加入黑名单
        success = await token_blacklist.add_to_blacklist(token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="登出失败"
            )
        return True 