from tortoise import fields, models
from app.models.base import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    """
    用户模型
    """
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    email = fields.CharField(max_length=255, unique=True, description="邮箱")
    hashed_password = fields.CharField(max_length=255, description="密码哈希")
    full_name = fields.CharField(max_length=255, null=True, description="全名")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_superuser = fields.BooleanField(default=False, description="是否超级管理员")
    roles = fields.ManyToManyField(
        'models.Role',
        related_name='user_roles',  # 修改这里
        description="关联角色"
    )

    class Meta:
        table = "users"
        table_description = "用户表"

    def __str__(self):
        return self.username

    @property
    async def permissions(self):
        """
        获取用户所有权限
        @return: List[Permission] 权限列表
        """
        permissions = set()
        roles = await self.roles.all().prefetch_related('permissions')
        for role in roles:
            role_permissions = await role.permissions.all()
            permissions.update(role_permissions)
        return list(permissions)

# Pydantic 模型定义
class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 用于API响应
User_Pydantic = UserInDB
# 用于创建用户
UserIn_Pydantic = UserCreate 