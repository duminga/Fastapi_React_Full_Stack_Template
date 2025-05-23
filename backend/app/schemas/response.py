from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应模型
    """
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    def dict(self, *args, **kwargs):
        """
        兼容新旧版本的 Pydantic
        """
        try:
            return super().model_dump(*args, **kwargs)
        except AttributeError:
            return super().dict(*args, **kwargs)

class ErrorResponse(BaseModel):
    """
    错误响应模型
    """
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="错误详情")

    def dict(self, *args, **kwargs):
        """
        兼容新旧版本的 Pydantic
        """
        try:
            return super().model_dump(*args, **kwargs)
        except AttributeError:
            return super().dict(*args, **kwargs)

    def model_dump(self, *args, **kwargs):
        """
        兼容 Pydantic v2
        """
        return self.dict(*args, **kwargs)

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "请求参数错误",
                "detail": "用户名不能为空"
            }
        } 