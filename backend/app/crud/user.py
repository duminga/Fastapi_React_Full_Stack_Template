from typing import List, Optional
from app.models.user import User
from app.core.exceptions import NotFoundException, ServerException
from app.utils.log_server import logServer

logger = logServer().run()

async def get_user_by_id(user_id: int) -> Optional[User]:
    """
    根据ID获取用户
    @param: user_id 用户ID
    @return: Optional[User] 用户对象或None
    @exception: NotFoundException 用户不存在异常
    @exception: ServerException 服务器内部错误
    """
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")
        return user
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise ServerException(detail="获取用户信息失败")

async def get_all_users() -> List[User]:
    """
    获取所有用户列表
    @return: List[User] 用户列表
    @exception: ServerException 服务器内部错误
    """
    try:
        return await User.all()
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise ServerException(detail="获取用户列表失败")

async def activate_user(user_id: int) -> None:
    """
    激活用户
    @param: user_id 用户ID
    @exception: NotFoundException 用户不存在异常
    @exception: ServerException 服务器内部错误
    """
    try:
        user = await get_user_by_id(user_id)
        user.is_active = True
        await user.save()
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"激活用户失败: {str(e)}")
        raise ServerException(detail="激活用户失败")

async def deactivate_user(user_id: int) -> None:
    """
    禁用用户
    @param: user_id 用户ID
    @exception: NotFoundException 用户不存在异常
    @exception: ServerException 服务器内部错误
    """
    try:
        user = await get_user_by_id(user_id)
        user.is_active = False
        await user.save()
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"禁用用户失败: {str(e)}")
        raise ServerException(detail="禁用用户失败") 