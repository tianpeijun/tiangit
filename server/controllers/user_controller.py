"""
用户管理控制器
"""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional

from models.database import engine
from services.user_service import UserService
from services.admin_log_service import AdminLogService
from middleware.auth_middleware import require_admin
from utils.response import success_response

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    password: str
    real_name: str
    employee_id: str
    department: str
    position: Optional[str] = None
    role: Optional[str] = "employee"


class UpdateUserRequest(BaseModel):
    real_name: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    new_password: str


@router.get("")
async def list_users(
    request: Request,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    admin_info: dict = Depends(require_admin)
):
    """获取用户列表"""
    async with engine.begin() as conn:
        result = await UserService.list_users(conn, role, is_active, keyword, page, page_size)
    
    return success_response(result)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    admin_info: dict = Depends(require_admin)
):
    """获取用户详情"""
    async with engine.begin() as conn:
        user = await UserService.get_user(conn, user_id)
    
    return success_response(user)


@router.post("")
async def create_user(
    request: Request,
    user_data: CreateUserRequest,
    admin_info: dict = Depends(require_admin)
):
    """创建用户"""
    async with engine.begin() as conn:
        user_id = await UserService.create_user(conn, user_data.dict(), admin_info['user_id'])
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='CREATE',
            operation_module='USER',
            operation_desc=f"创建用户：{user_data.username}",
            data_after={'user_id': user_id, 'username': user_data.username},
            ip_address=request.client.host if request.client else None
        )
    
    return success_response({'user_id': user_id}, "用户创建成功")


@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: int,
    user_data: UpdateUserRequest,
    admin_info: dict = Depends(require_admin)
):
    """更新用户信息"""
    async with engine.begin() as conn:
        # 获取更新前的数据
        old_user = await UserService.get_user(conn, user_id)
        
        # 更新
        await UserService.update_user(conn, user_id, user_data.dict(exclude_unset=True))
        
        # 获取更新后的数据
        new_user = await UserService.get_user(conn, user_id)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='UPDATE',
            operation_module='USER',
            operation_desc=f"更新用户：{old_user['username']}",
            data_before=old_user,
            data_after=new_user,
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="用户更新成功")


@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: int,
    admin_info: dict = Depends(require_admin)
):
    """删除用户"""
    async with engine.begin() as conn:
        # 获取用户信息
        user = await UserService.get_user(conn, user_id)
        
        # 删除
        await UserService.delete_user(conn, user_id)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='DELETE',
            operation_module='USER',
            operation_desc=f"删除用户：{user['username']}",
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="用户删除成功")


@router.put("/{user_id}/status")
async def toggle_user_status(
    request: Request,
    user_id: int,
    is_active: bool,
    admin_info: dict = Depends(require_admin)
):
    """启用/禁用用户"""
    async with engine.begin() as conn:
        user = await UserService.get_user(conn, user_id)
        
        await UserService.toggle_user_status(conn, user_id, is_active)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='UPDATE',
            operation_module='USER',
            operation_desc=f"{'启用' if is_active else '禁用'}用户：{user['username']}",
            data_before={'is_active': user['is_active']},
            data_after={'is_active': is_active},
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message=f"用户{'启用' if is_active else '禁用'}成功")


@router.post("/{user_id}/reset-password")
async def reset_password(
    request: Request,
    user_id: int,
    password_data: ResetPasswordRequest,
    admin_info: dict = Depends(require_admin)
):
    """重置密码"""
    async with engine.begin() as conn:
        user = await UserService.get_user(conn, user_id)
        
        await UserService.reset_password(conn, user_id, password_data.new_password)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='RESET_PASSWORD',
            operation_module='USER',
            operation_desc=f"重置用户密码：{user['username']}",
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="密码重置成功")
