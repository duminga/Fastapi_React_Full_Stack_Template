from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.base import BaseModel

class Role(BaseModel):
    """
    角色模型
    实现角色的基本信息和权限关联
    用于RBAC权限控制中的角色管理
    """
    id = fields.IntField(pk=True, description="角色ID")
    name = fields.CharField(max_length=50, description="角色名称")
    code = fields.CharField(max_length=50, unique=True, description="角色编码，用于权限判断")
    description = fields.TextField(null=True, description="角色描述")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    users = fields.ManyToManyField(
        'models.User',
        related_name='role_users',  # 修改这里
        description="关联用户"
    )
    permissions = fields.ManyToManyField(
        'models.Permission',
        related_name='role_permissions',  # 修改这里
        description="关联权限"
    )

    class Meta:
        table = "roles"
        table_description = "角色表"

    def __str__(self):
        return self.name

# 创建Pydantic模型，用于API请求和响应
Role_Pydantic = pydantic_model_creator(Role, name="Role")
RoleIn_Pydantic = pydantic_model_creator(
    Role, 
    name="RoleIn", 
    exclude_readonly=True,
    exclude=("created_at", "updated_at")
) 