from typing import List
from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.schemas.response import ResponseModel
from app.models.user import User
from app.core.deps import LoginRequired, AdminRequired
from app.crud.user import get_user_by_id, get_all_users, activate_user, deactivate_user

router = APIRouter()

@router.get("/me", response_model=ResponseModel[UserResponse])
async def read_users_me(current_user: User = Depends(LoginRequired)):
    """
    获取当前用户信息
    @param: current_user 当前用户对象
    @return: ResponseModel[UserResponse] 用户信息
    """
    return ResponseModel(data=current_user)

@router.get("/", response_model=ResponseModel[List[UserResponse]])
async def read_users(current_user: User = Depends(AdminRequired)):
    """
    获取所有用户列表
    @param: current_user 当前用户对象
    @return: ResponseModel[List[UserResponse]] 用户列表
    """
    users = await get_all_users()
    return ResponseModel(data=users)

@router.get("/{user_id}", response_model=ResponseModel[UserResponse])
async def read_user(user_id: int,current_user: User = Depends(AdminRequired)):
    """
    获取指定用户信息
    @param: user_id 用户ID
    @param: current_user 当前用户对象
    @return: ResponseModel[UserResponse] 用户信息
    """
    user = await get_user_by_id(user_id)
    return ResponseModel(data=user)

@router.put("/{user_id}/activate", response_model=ResponseModel)
async def activate_user_endpoint(user_id: int,current_user: User = Depends(AdminRequired)):
    """
    激活用户
    @param: user_id 用户ID
    @param: current_user 当前用户对象
    @return: ResponseModel 操作结果
    """
    await activate_user(user_id)
    return ResponseModel(message="用户已激活")

@router.put("/{user_id}/deactivate", response_model=ResponseModel)
async def deactivate_user_endpoint(user_id: int,current_user: User = Depends(AdminRequired)):
    """
    禁用用户
    @param: user_id 用户ID
    @param: current_user 当前用户对象
    @return: ResponseModel 操作结果
    """
    await deactivate_user(user_id)
    return ResponseModel(message="用户已禁用") 