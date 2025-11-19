"""
认证服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional
import re

from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from utils.password import hash_password, verify_password
from utils.response import AuthenticationException, ValidationException, PermissionException
from config.settings import settings


class AuthService:
    """认证服务"""
    
    @staticmethod
    async def login(conn: AsyncConnection, username: str, password: str) -> dict:
        """用户登录"""
        # 查询用户
        user = await UserRepository.get_user_by_username(conn, username)
        
        if not user:
            raise AuthenticationException("用户名或密码错误")
        
        # 验证密码
        if not verify_password(password, user['password_hash']):
            raise AuthenticationException("用户名或密码错误")
        
        # 检查账户状态
        if not user['is_active']:
            raise PermissionException("账户已被禁用")
        
        # 更新最后登录时间
        await UserRepository.update_last_login(conn, user['id'])
        
        # 创建 Session
        session_data = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
        session_id = await SessionRepository.create_session(conn, user['id'], session_data)
        
        # 返回用户信息和 Session ID
        return {
            'session_id': session_id,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'real_name': user['real_name'],
                'employee_id': user['employee_id'],
                'department': user['department'],
                'position': user['position'],
                'role': user['role'],
                'points': user['points']
            }
        }
    
    @staticmethod
    async def logout(conn: AsyncConnection, session_id: str) -> bool:
        """用户登出"""
        return await SessionRepository.delete_session(conn, session_id)
    
    @staticmethod
    async def verify_session(conn: AsyncConnection, session_id: str) -> Optional[dict]:
        """验证 Session"""
        session = await SessionRepository.get_session(conn, session_id)
        
        if not session:
            return None
        
        # 获取用户信息
        user = await UserRepository.get_user_by_id(conn, session['user_id'])
        
        if not user or not user['is_active']:
            # Session 有效但用户已被禁用，删除 Session
            await SessionRepository.delete_session(conn, session_id)
            return None
        
        return {
            'user_id': user['id'],
            'username': user['username'],
            'real_name': user['real_name'],
            'role': user['role'],
            'points': user['points']
        }
    
    @staticmethod
    async def get_current_user(conn: AsyncConnection, session_id: str) -> dict:
        """获取当前用户信息"""
        user_info = await AuthService.verify_session(conn, session_id)
        
        if not user_info:
            raise AuthenticationException("未登录或登录已过期")
        
        # 获取完整用户信息
        user = await UserRepository.get_user_by_id(conn, user_info['user_id'])
        
        return {
            'id': user['id'],
            'username': user['username'],
            'real_name': user['real_name'],
            'employee_id': user['employee_id'],
            'department': user['department'],
            'position': user['position'],
            'role': user['role'],
            'points': user['points'],
            'is_active': user['is_active'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'last_login_at': user['last_login_at'].isoformat() if user['last_login_at'] else None
        }
    
    @staticmethod
    async def change_password(
        conn: AsyncConnection,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """修改密码"""
        # 获取用户
        user = await UserRepository.get_user_by_id(conn, user_id)
        
        if not user:
            raise ValidationException("用户不存在")
        
        # 验证旧密码
        if not verify_password(old_password, user['password_hash']):
            raise ValidationException("当前密码错误")
        
        # 验证新密码格式
        AuthService.validate_password(new_password)
        
        # 更新密码
        new_password_hash = hash_password(new_password)
        return await UserRepository.update_password(conn, user_id, new_password_hash)
    
    @staticmethod
    def validate_password(password: str) -> None:
        """验证密码格式"""
        if len(password) < settings.PASSWORD_MIN_LENGTH or len(password) > settings.PASSWORD_MAX_LENGTH:
            raise ValidationException(
                f"密码长度必须为{settings.PASSWORD_MIN_LENGTH}-{settings.PASSWORD_MAX_LENGTH}位"
            )
        
        # 必须包含数字和字母
        if not re.search(r'[0-9]', password):
            raise ValidationException("密码必须包含数字")
        
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationException("密码必须包含字母")
    
    @staticmethod
    def require_role(user_info: dict, required_role: str) -> None:
        """检查用户角色"""
        if user_info['role'] != required_role:
            raise PermissionException("无权限访问")
    
    @staticmethod
    def require_admin(user_info: dict) -> None:
        """要求管理员权限"""
        AuthService.require_role(user_info, 'admin')
