from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")

class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(..., min_length=6, description="密码")

class UserLogin(BaseModel):
    """
    用户登录模型
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """
    JWT Token响应模型
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int 