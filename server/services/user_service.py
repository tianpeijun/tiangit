"""
用户服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional, List

from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from utils.password import hash_password
from utils.response import ValidationException, NotFoundException
from config.settings import settings


class UserService:
    """用户服务"""
    
    @staticmethod
    async def create_user(conn: AsyncConnection, user_data: dict, admin_id: int) -> int:
        """创建用户"""
        # 验证用户名唯一性
        existing_user = await UserRepository.get_user_by_username(conn, user_data['username'])
        if existing_user:
            raise ValidationException("用户名已存在")
        
        # 验证工号唯一性
        existing_employee = await UserRepository.get_user_by_employee_id(conn, user_data['employee_id'])
        if existing_employee:
            raise ValidationException("工号已存在")
        
        # 验证密码格式
        AuthService.validate_password(user_data['password'])
        
        # 准备数据
        create_data = {
            'username': user_data['username'],
            'password_hash': hash_password(user_data['password']),
            'real_name': user_data['real_name'],
            'employee_id': user_data['employee_id'],
            'department': user_data['department'],
            'position': user_data.get('position'),
            'role': user_data.get('role', 'employee'),
            'points': 1000,  # 新用户初始积分
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return await UserRepository.create_user(conn, create_data)
    
    @staticmethod
    async def update_user(conn: AsyncConnection, user_id: int, user_data: dict) -> bool:
        """更新用户信息"""
        # 检查用户是否存在
        user = await UserRepository.get_user_by_id(conn, user_id)
        if not user:
            raise NotFoundException("用户不存在")
        
        # 如果更新工号，检查唯一性
        if 'employee_id' in user_data and user_data['employee_id'] != user['employee_id']:
            existing = await UserRepository.get_user_by_employee_id(conn, user_data['employee_id'])
            if existing:
                raise ValidationException("工号已存在")
        
        # 准备更新数据
        update_data = {}
        allowed_fields = ['real_name', 'employee_id', 'department', 'position', 'is_active']
        for field in allowed_fields:
            if field in user_data:
                update_data[field] = user_data[field]
        
        if not update_data:
            return True
        
        return await UserRepository.update_user(conn, user_id, update_data)
    
    @staticmethod
    async def delete_user(conn: AsyncConnection, user_id: int) -> bool:
        """删除用户"""
        user = await UserRepository.get_user_by_id(conn, user_id)
        if not user:
            raise NotFoundException("用户不存在")
        
        return await UserRepository.delete_user(conn, user_id)
    
    @staticmethod
    async def toggle_user_status(conn: AsyncConnection, user_id: int, is_active: bool) -> bool:
        """启用/禁用用户"""
        user = await UserRepository.get_user_by_id(conn, user_id)
        if not user:
            raise NotFoundException("用户不存在")
        
        return await UserRepository.update_user(conn, user_id, {'is_active': is_active})
    
    @staticmethod
    async def reset_password(conn: AsyncConnection, user_id: int, new_password: str) -> bool:
        """重置密码（管理员操作）"""
        user = await UserRepository.get_user_by_id(conn, user_id)
        if not user:
            raise NotFoundException("用户不存在")
        
        # 验证密码格式
        AuthService.validate_password(new_password)
        
        # 更新密码
        new_password_hash = hash_password(new_password)
        return await UserRepository.update_password(conn, user_id, new_password_hash)
    
    @staticmethod
    async def get_user(conn: AsyncConnection, user_id: int) -> dict:
        """获取用户详情"""
        user = await UserRepository.get_user_by_id(conn, user_id)
        if not user:
            raise NotFoundException("用户不存在")
        
        # 移除敏感信息
        user.pop('password_hash', None)
        
        # 格式化日期
        if user.get('created_at'):
            user['created_at'] = user['created_at'].isoformat()
        if user.get('updated_at'):
            user['updated_at'] = user['updated_at'].isoformat()
        if user.get('last_login_at'):
            user['last_login_at'] = user['last_login_at'].isoformat()
        
        return user
    
    @staticmethod
    async def list_users(
        conn: AsyncConnection,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取用户列表"""
        items, total = await UserRepository.list_users(
            conn, role, is_active, keyword, page, page_size
        )
        
        # 移除敏感信息并格式化日期
        for item in items:
            item.pop('password_hash', None)
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].isoformat()
            if item.get('last_login_at'):
                item['last_login_at'] = item['last_login_at'].isoformat()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
