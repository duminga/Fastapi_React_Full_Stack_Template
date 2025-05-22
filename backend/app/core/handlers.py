from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.core.exceptions import BaseAPIException
from app.schemas.response import ErrorResponse
from app.utils.log_server import logServer

logger = logServer().run()

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    参数验证异常处理器
    @param: request 请求对象
    @param: exc 异常对象
    @return: JSONResponse 错误响应
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    error_response = ErrorResponse(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="参数验证失败",
        detail=str(errors)
    )
    
    logger.warning(f"参数验证失败: {str(errors)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )

async def api_exception_handler(request: Request, exc: BaseAPIException):
    """
    API异常处理器
    @param: request 请求对象
    @param: exc 异常对象
    @return: JSONResponse 错误响应
    """
    error_response = ErrorResponse(
        code=exc.status_code,
        message=exc.message,
        detail=exc.detail
    )
    
    logger.error(f"API异常: {exc.message}, 详情: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=exc.headers
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP异常处理器
    @param: request 请求对象
    @param: exc 异常对象
    @return: JSONResponse 错误响应
    """
    error_response = ErrorResponse(
        code=exc.status_code,
        message=str(exc.detail),
        detail=None
    )
    
    logger.error(f"HTTP异常: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
        headers=exc.headers
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    @param: request 请求对象
    @param: exc 异常对象
    @return: JSONResponse 错误响应
    """
    error_response = ErrorResponse(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="服务器内部错误",
        detail=str(exc)
    )
    
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    ) 