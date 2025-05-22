from typing import List, Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.exceptions import AuthenticationException, PermissionException
from app.utils.log_server import logServer

logger = logServer().run()

class RBACMiddleware(BaseHTTPMiddleware):
    """
    RBAC权限校验中间件
    """
    def __init__(self, app: Callable, required_permissions: Optional[List[str]] = None):
        """
        初始化中间件
        @param: app ASGI应用
        @param: required_permissions 所需权限列表
        """
        super().__init__(app)
        self.required_permissions = required_permissions or []

    async def dispatch(self, request: Request, call_next):
        """
        中间件处理函数
        @param: request 请求对象
        @param: call_next 下一个处理函数
        @return: Response 响应对象
        @exception: AuthenticationException 认证失败异常
        @exception: PermissionDeniedException 权限不足异常
        """
        try:
            # 获取当前用户
            user = request.state.user
            if not user:
                raise AuthenticationException(detail="未认证")

            # 如果用户是超级管理员，直接放行
            if user.is_superuser:
                return await call_next(request)

            # 获取用户角色
            roles = await Role.filter(users__id=user.id).prefetch_related('permissions')
            if not roles:
                raise PermissionException(detail="用户没有分配角色")

            # 获取用户所有权限
            user_permissions = set()
            for role in roles:
                permissions = await role.permissions.all()
                user_permissions.update(p.code for p in permissions)

            # 检查是否有所需权限
            if self.required_permissions:
                if not any(perm in user_permissions for perm in self.required_permissions):
                    raise PermissionException(detail="权限不足")

            # 继续处理请求
            return await call_next(request)

        except AuthenticationException as e:
            logger.warning(f"认证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        except PermissionException as e:
            logger.warning(f"权限不足: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"RBAC中间件处理失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部错误"
            )

def require_permissions(*permissions: str):
    """
    权限检查装饰器
    @param: permissions 所需权限列表
    @return: RBACMiddleware RBAC中间件
    """
    return lambda app: RBACMiddleware(app, required_permissions=list(permissions)) 