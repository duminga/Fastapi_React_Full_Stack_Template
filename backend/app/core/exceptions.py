from fastapi import HTTPException, status
from typing import Optional, Any, Dict

class BaseAPIException(HTTPException):
    """
    基础API异常类
    """
    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.message = message
        self.detail = detail

class ValidationException(BaseAPIException):
    """
    参数验证异常
    """
    def __init__(
        self,
        message: str = "参数验证失败",
        detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            detail=detail
        )

class AuthenticationException(BaseAPIException):
    """
    认证异常
    """
    def __init__(
        self,
        message: str = "认证失败",
        detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class PermissionException(BaseAPIException):
    """
    权限异常
    """
    def __init__(
        self,
        message: str = "权限不足",
        detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            detail=detail
        )

class NotFoundException(BaseAPIException):
    """
    资源不存在异常
    """
    def __init__(
        self,
        message: str = "资源不存在",
        detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            detail=detail
        )

class ServerException(BaseAPIException):
    """
    服务器异常
    """
    def __init__(
        self,
        message: str = "服务器内部错误",
        detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            detail=detail
        ) 