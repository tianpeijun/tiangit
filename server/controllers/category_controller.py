"""
分类管理控制器
"""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional

from models.database import engine
from services.category_service import CategoryService
from services.admin_log_service import AdminLogService
from middleware.auth_middleware import require_admin, require_employee, get_current_user
from utils.response import success_response

router = APIRouter()
employee_router = APIRouter()


class CreateCategoryRequest(BaseModel):
    name: str
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


# 管理端接口
@router.get("")
async def list_categories(admin_info: dict = Depends(require_admin)):
    """获取所有分类（管理端）"""
    async with engine.begin() as conn:
        categories = await CategoryService.list_categories(conn)
    
    return success_response(categories)


@router.get("/tree")
async def get_category_tree(admin_info: dict = Depends(require_admin)):
    """获取分类树（管理端）"""
    async with engine.begin() as conn:
        tree = await CategoryService.get_category_tree(conn)
    
    return success_response(tree)


@router.get("/{category_id}")
async def get_category(category_id: int, admin_info: dict = Depends(require_admin)):
    """获取分类详情"""
    async with engine.begin() as conn:
        category = await CategoryService.get_category(conn, category_id)
    
    return success_response(category)


@router.post("")
async def create_category(
    request: Request,
    category_data: CreateCategoryRequest,
    admin_info: dict = Depends(require_admin)
):
    """创建分类"""
    async with engine.begin() as conn:
        category_id = await CategoryService.create_category(conn, category_data.dict())
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='CREATE',
            operation_module='CATEGORY',
            operation_desc=f"创建分类：{category_data.name}",
            data_after={'category_id': category_id, 'name': category_data.name},
            ip_address=request.client.host if request.client else None
        )
    
    return success_response({'category_id': category_id}, "分类创建成功")


@router.put("/{category_id}")
async def update_category(
    request: Request,
    category_id: int,
    category_data: UpdateCategoryRequest,
    admin_info: dict = Depends(require_admin)
):
    """更新分类"""
    async with engine.begin() as conn:
        old_category = await CategoryService.get_category(conn, category_id)
        
        await CategoryService.update_category(conn, category_id, category_data.dict(exclude_unset=True))
        
        new_category = await CategoryService.get_category(conn, category_id)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='UPDATE',
            operation_module='CATEGORY',
            operation_desc=f"更新分类：{old_category['name']}",
            data_before=old_category,
            data_after=new_category,
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="分类更新成功")


@router.delete("/{category_id}")
async def delete_category(
    request: Request,
    category_id: int,
    admin_info: dict = Depends(require_admin)
):
    """删除分类"""
    async with engine.begin() as conn:
        category = await CategoryService.get_category(conn, category_id)
        
        await CategoryService.delete_category(conn, category_id)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='DELETE',
            operation_module='CATEGORY',
            operation_desc=f"删除分类：{category['name']}",
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="分类删除成功")


# 员工端路由
@employee_router.get("")
async def list_categories_for_employee(user_info: dict = Depends(require_employee)):
    """获取所有分类（员工端）"""
    async with engine.begin() as conn:
        categories = await CategoryService.list_categories(conn)
    
    return success_response(categories)


@employee_router.get("/tree")
async def get_category_tree_for_employee(user_info: dict = Depends(require_employee)):
    """获取分类树（员工端）"""
    async with engine.begin() as conn:
        tree = await CategoryService.get_category_tree(conn)
    
    return success_response(tree)
