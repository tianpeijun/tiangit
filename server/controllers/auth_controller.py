"""
认证控制器
"""
from fastapi import APIRouter, Depends, Response, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.database import engine
from services.auth_service import AuthService
from middleware.auth_middleware import get_current_user
from utils.response import success_response
from config.settings import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/login")
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(request: Request, response: Response, login_data: LoginRequest):
    """用户登录"""
    async with engine.begin() as conn:
        result = await AuthService.login(conn, login_data.username, login_data.password)
    
    # 设置 Session Cookie
    response.set_cookie(
        key="session_id",
        value=result['session_id'],
        max_age=settings.SESSION_EXPIRE_SECONDS,
        httponly=True,
        samesite="lax"
    )
    
    return success_response(result, "登录成功")


@router.post("/logout")
async def logout(request: Request, response: Response, user_info: dict = Depends(get_current_user)):
    """用户登出"""
    session_id = request.cookies.get('session_id') or request.headers.get('X-Session-ID')
    
    if session_id:
        async with engine.begin() as conn:
            await AuthService.logout(conn, session_id)
    
    # 清除 Cookie
    response.delete_cookie("session_id")
    
    return success_response(message="登出成功")


@router.get("/current-user")
async def get_current_user_info(request: Request, user_info: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    session_id = request.cookies.get('session_id') or request.headers.get('X-Session-ID')
    
    async with engine.begin() as conn:
        user = await AuthService.get_current_user(conn, session_id)
    
    return success_response(user)


@router.post("/password/change")
async def change_password(
    password_data: ChangePasswordRequest,
    user_info: dict = Depends(get_current_user)
):
    """修改密码"""
    async with engine.begin() as conn:
        await AuthService.change_password(
            conn,
            user_info['user_id'],
            password_data.old_password,
            password_data.new_password
        )
    
    return success_response(message="密码修改成功")
