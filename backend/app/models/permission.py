from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.base import BaseModel

class Permission(BaseModel):
    """
    权限模型
    实现权限的基本信息
    用于RBAC权限控制中的权限管理
    """
    id = fields.IntField(pk=True, description="权限ID")
    name = fields.CharField(max_length=50, description="权限名称")
    code = fields.CharField(max_length=50, unique=True, description="权限编码，用于权限判断")
    description = fields.TextField(null=True, description="权限描述")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    roles = fields.ManyToManyField(
        'models.Role',
        related_name='permission_roles',  # 修改这里
        description="关联角色"
    )
    class Meta:
        table = "permissions"
        table_description = "权限表"

    def __str__(self):
        return f"{self.name}"

# 创建Pydantic模型，用于API请求和响应
Permission_Pydantic = pydantic_model_creator(Permission, name="Permission")
PermissionIn_Pydantic = pydantic_model_creator(
    Permission, 
    name="PermissionIn", 
    exclude_readonly=True,
    exclude=("created_at", "updated_at")
) 