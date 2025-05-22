from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.core.deps import get_current_user, get_current_active_user
from app.core.exceptions import AuthenticationException, ServerException
from app.utils.log_server import logger

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """
    用户注册
    """
    try:
        user = await AuthService.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return UserResponse.from_orm(user)
    except ServerException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="注册失败")

@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录
    """
    try:
        access_token, expires_in = await AuthService.login(form_data.username, form_data.password)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in
        )
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="登录失败")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    用户登出
    """
    try:
        success = await AuthService.logout(token)
        if success:
            return {"message": "登出成功"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="登出失败")
    except Exception as e:
        logger.error(f"登出失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="登出失败")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    获取当前用户信息
    """
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    更新当前用户信息
    """
    try:
        # 更新用户信息
        current_user.email = user_data.email
        current_user.full_name = user_data.full_name
        if user_data.password:
            current_user.hashed_password = AuthService.get_password_hash(user_data.password)
        await current_user.save()
        return UserResponse.from_orm(current_user)
    except Exception as e:
        logger.error(f"更新用户信息失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新失败") 