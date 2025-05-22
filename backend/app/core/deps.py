from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from app.utils.log_server import logServer

logger = logServer().run()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户
    @param: token JWT令牌
    @return: User 当前用户对象
    @exception: HTTPException 认证失败异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 获取用户信息
    user = await User.get_or_none(username=username)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    @param: current_user 当前用户对象
    @return: User 当前活跃用户对象
    @exception: HTTPException 用户未激活异常
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user

def check_permissions(required_permissions: List[str]):
    """
    权限检查装饰器
    @param: required_permissions 所需权限列表
    @return: 权限检查函数
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """
        权限检查函数
        @param: current_user 当前用户对象
        @return: User 当前用户对象
        @exception: HTTPException 权限不足异常
        """
        # 获取用户所有权限
        user_permissions = set()
        for role in await current_user.roles.all():
            for permission in await role.permissions.all():
                user_permissions.add(permission.code)

        # 检查是否具有所需权限
        if not all(perm in user_permissions for perm in required_permissions):
            logger.warning(f"用户 {current_user.username} 权限不足")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return permission_checker

# 常用权限依赖
async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    获取管理员用户
    @param: current_user 当前用户对象
    @return: User 管理员用户对象
    @exception: HTTPException 非管理员异常
    """
    is_admin = False
    for role in await current_user.roles.all():
        if role.code == "admin":
            is_admin = True
            break
    
    if not is_admin:
        logger.warning(f"用户 {current_user.username} 尝试访问管理员接口")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

# 权限依赖快捷方式
LoginRequired = get_current_active_user
AdminRequired = get_admin_user 