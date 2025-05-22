from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.services.auth_service import AuthService
from app.utils.log_server import logServer

logger = logServer().run()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    用户注册接口
    @param: user_data 用户注册数据
    @return: UserResponse 用户信息
    @exception: HTTPException 注册失败异常
    """
    try:
        user = await AuthService.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return user
    except Exception as e:
        logger.error(f"注册接口异常: {str(e)}")
        raise

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    @param: form_data 登录表单数据
    @return: Token JWT令牌信息
    @exception: HTTPException 登录失败异常
    """
    try:
        access_token, expires_in = await AuthService.login(
            username=form_data.username,
            password=form_data.password
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expires_in
        }
    except Exception as e:
        logger.error(f"登录接口异常: {str(e)}")
        raise

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    用户登出接口
    @param: token JWT令牌
    @return: dict 登出结果
    @exception: HTTPException 登出失败异常
    """
    try:
        # TODO: 实现令牌黑名单机制
        return {"message": "登出成功"}
    except Exception as e:
        logger.error(f"登出接口异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        ) 