from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.models.user import User
from app.core.config import settings
from app.core.blacklist import token_blacklist
from app.core.exceptions import AuthenticationException, ServerException
from app.utils.log_server import logServer

logger = logServer().run()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        获取密码哈希值
        @param: password 明文密码
        @return: str 哈希密码
        """
        return pwd_context.hash(password)

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
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def verify_token(token: str) -> bool:
        """
        验证令牌
        @param: token JWT令牌
        @return: bool 是否有效
        @exception: AuthenticationException 认证失败异常
        """
        try:
            # 检查令牌是否在黑名单中
            if await token_blacklist.is_blacklisted(token):
                raise AuthenticationException(detail="令牌已失效")

            # 验证令牌
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                raise AuthenticationException(detail="无效的令牌")
            
            # 检查用户是否存在
            user = await User.get_or_none(username=username)
            if user is None:
                raise AuthenticationException(detail="用户不存在")
            
            return True
        except JWTError:
            raise AuthenticationException(detail="无效的令牌")
        except Exception as e:
            logger.error(f"验证令牌失败: {str(e)}")
            raise ServerException(detail="验证令牌失败")

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        认证用户
        @param: username 用户名
        @param: password 密码
        @return: Optional[User] 用户对象
        @exception: AuthenticationException 认证失败异常
        """
        try:
            user = await User.get_or_none(username=username)
            if not user:
                return None
            if not AuthService.verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}")
            raise ServerException(detail="认证失败")

    @staticmethod
    async def register_user(username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        注册新用户
        @param: username 用户名
        @param: email 邮箱
        @param: password 密码
        @param: full_name 全名
        @return: User 用户对象
        @exception: ServerException 注册失败异常
        """
        try:
            # 检查用户名是否已存在
            if await User.filter(username=username).exists():
                raise ServerException(detail="用户名已存在")
            
            # 检查邮箱是否已存在
            if await User.filter(email=email).exists():
                raise ServerException(detail="邮箱已被注册")

            # 创建新用户
            hashed_password = AuthService.get_password_hash(password)
            user = await User.create(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name
            )
            return user
        except ServerException:
            raise
        except Exception as e:
            logger.error(f"用户注册失败: {str(e)}")
            raise ServerException(detail="注册失败")

    @staticmethod
    async def login(username: str, password: str) -> Tuple[str, int]:
        """
        用户登录
        @param: username 用户名
        @param: password 密码
        @return: Tuple[str, int] (JWT令牌, 过期时间)
        @exception: AuthenticationException 登录失败异常
        """
        user = await AuthService.authenticate_user(username, password)
        if not user:
            raise AuthenticationException(detail="用户名或密码错误")
        
        if not user.is_active:
            raise ServerException(detail="用户已被禁用")

        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @staticmethod
    async def logout(token: str) -> bool:
        """
        用户登出
        @param: token JWT令牌
        @return: bool 是否成功
        @exception: ServerException 登出失败异常
        """
        try:
            # 将令牌加入黑名单
            success = await token_blacklist.add_to_blacklist(token)
            if not success:
                raise ServerException(detail="登出失败")
            return True
        except Exception as e:
            logger.error(f"用户登出失败: {str(e)}")
            raise ServerException(detail="登出失败") 