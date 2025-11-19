"""
认证中间件
"""
from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection

from models.database import engine
from services.auth_service import AuthService


async def get_current_user(request: Request) -> dict:
    """获取当前用户（依赖注入）"""
    # 从 Cookie 或 Header 中获取 Session ID
    session_id = request.cookies.get('session_id') or request.headers.get('X-Session-ID')
    
    if not session_id:
        raise HTTPException(status_code=401, detail="未登录")
    
    # 验证 Session
    async with engine.begin() as conn:
        user_info = await AuthService.verify_session(conn, session_id)
    
    if not user_info:
        raise HTTPException(status_code=401, detail="登录已过期")
    
    return user_info


async def require_admin(request: Request) -> dict:
    """要求管理员权限（依赖注入）"""
    user_info = await get_current_user(request)
    
    if user_info['role'] != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return user_info


async def require_employee(request: Request) -> dict:
    """要求员工权限（依赖注入）"""
    user_info = await get_current_user(request)
    
    if user_info['role'] not in ['employee', 'admin']:
        raise HTTPException(status_code=403, detail="需要员工权限")
    
    return user_info
