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
    def __init__(self, app, required_permissions: Optional[List[str]] = None):
        """
        初始化中间件
        @param: app ASGI应用
        @param: required_permissions 所需权限列表
        """
        super().__init__(app)
        self.required_permissions = required_permissions or []

    async def dispatch(self, request: Request, call_next: Callable):
        """
        中间件处理函数
        @param: request 请求对象
        @param: call_next 下一个处理函数
        @return: Response 响应对象
        @exception: AuthenticationException 认证失败异常
        @exception: PermissionDeniedException 权限不足异常
        """
        try:
            # 检查是否是认证相关的路径
            if request.url.path.startswith("/api/v1/auth"):
                return await call_next(request)

            # 获取用户信息
            user = getattr(request.state, "user", None)
            if not user:
                # 如果没有用户信息，直接放行，让后续的权限检查处理
                return await call_next(request)

            # 检查用户权限
            if not user.is_active:
                raise AuthenticationException(detail="用户已被禁用")

            # 如果是超级用户，直接放行
            if user.is_superuser:
                return await call_next(request)

            # 获取用户角色和权限
            roles = await user.roles.all()
            permissions = set()
            for role in roles:
                role_permissions = await role.permissions.all()
                permissions.update(p.code for p in role_permissions)

            # 将权限信息添加到请求状态中
            request.state.permissions = permissions

            # 检查是否有所需权限
            if self.required_permissions:
                if not any(perm in permissions for perm in self.required_permissions):
                    raise PermissionException(detail="权限不足")

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
                detail="权限检查失败"
            )

def require_permissions(*permissions: str):
    """
    权限检查装饰器
    @param: permissions 所需权限列表
    @return: RBACMiddleware RBAC中间件
    """
    return lambda app: RBACMiddleware(app, required_permissions=list(permissions)) 