from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserResponse
from app.schemas.response import ResponseModel
from app.models.user import User
from app.core.deps import LoginRequired, AdminRequired, check_permissions
from app.core.exceptions import NotFoundException, ServerException
from app.utils.log_server import logServer

logger = logServer().run()

router = APIRouter()

@router.get("/me", response_model=ResponseModel[UserResponse])
async def read_users_me(
    current_user: User = Depends(LoginRequired)
):
    """
    获取当前用户信息
    @param: current_user 当前用户对象
    @return: ResponseModel[UserResponse] 用户信息
    """
    return ResponseModel(data=current_user)

@router.get("/", response_model=ResponseModel[List[UserResponse]])
async def read_users(
    current_user: User = Depends(AdminRequired)
):
    """
    获取所有用户列表
    @param: current_user 当前用户对象
    @return: ResponseModel[List[UserResponse]] 用户列表
    """
    try:
        users = await User.all()
        return ResponseModel(data=users)
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise ServerException(detail="获取用户列表失败")

@router.get("/{user_id}", response_model=ResponseModel[UserResponse])
async def read_user(
    user_id: int,
    current_user: User = Depends(AdminRequired)
):
    """
    获取指定用户信息
    @param: user_id 用户ID
    @param: current_user 当前用户对象
    @return: ResponseModel[UserResponse] 用户信息
    @exception: NotFoundException 用户不存在异常
    """
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")
        return ResponseModel(data=user)
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise ServerException(detail="获取用户信息失败")

@router.put("/{user_id}/activate", response_model=ResponseModel)
async def activate_user(
    user_id: int,
    current_user: User = Depends(AdminRequired)
):
    """
    激活用户
    @param: user_id 用户ID
    @param: current_user 当前用户对象
    @return: ResponseModel 操作结果
    @exception: NotFoundException 用户不存在异常
    """
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")
        
        user.is_active = True
        await user.save()
        return ResponseModel(message="用户已激活")
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"激活用户失败: {str(e)}")
        raise ServerException(detail="激活用户失败")

@router.put("/{user_id}/deactivate", response_model=ResponseModel)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(AdminRequired)
):
    """
    禁用用户
    @param: user_id 用户ID
    @param: current_user 当前用户对象
    @return: ResponseModel 操作结果
    @exception: NotFoundException 用户不存在异常
    """
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise NotFoundException(detail="用户不存在")
        
        user.is_active = False
        await user.save()
        return ResponseModel(message="用户已禁用")
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"禁用用户失败: {str(e)}")
        raise ServerException(detail="禁用用户失败") 