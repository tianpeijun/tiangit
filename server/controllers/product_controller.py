"""
产品管理控制器
"""
from fastapi import APIRouter, Depends, Request, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List

from models.database import engine
from services.product_service import ProductService
from services.file_service import FileService
from services.admin_log_service import AdminLogService
from middleware.auth_middleware import require_admin, require_employee
from utils.response import success_response

router = APIRouter()


class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    points_required: int
    status: Optional[str] = "inactive"
    category_ids: Optional[List[int]] = []


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    points_required: Optional[int] = None
    status: Optional[str] = None
    category_ids: Optional[List[int]] = None


# 员工端接口
@router.get("/api/personal/products")
async def list_products_for_employee(
    category_ids: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_employee)
):
    """获取产品列表（员工端）"""
    # 解析分类ID
    category_id_list = None
    if category_ids:
        category_id_list = [int(id) for id in category_ids.split(',')]
    
    async with engine.begin() as conn:
        result = await ProductService.list_products(
            conn,
            status='active',
            category_ids=category_id_list,
            keyword=keyword,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
    
    return success_response(result)


@router.get("/api/personal/products/{product_id}")
async def get_product_for_employee(
    product_id: int,
    user_info: dict = Depends(require_employee)
):
    """获取产品详情（员工端）"""
    async with engine.begin() as conn:
        product = await ProductService.get_product(conn, product_id)
    
    return success_response(product)


# 管理端接口
@router.get("/api/manage/products")
async def list_products_for_admin(
    status: Optional[str] = None,
    category_ids: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    admin_info: dict = Depends(require_admin)
):
    """获取产品列表（管理端）"""
    category_id_list = None
    if category_ids:
        category_id_list = [int(id) for id in category_ids.split(',')]
    
    async with engine.begin() as conn:
        result = await ProductService.list_products(
            conn,
            status=status,
            category_ids=category_id_list,
            keyword=keyword,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
    
    return success_response(result)


@router.get("/api/manage/products/{product_id}")
async def get_product_for_admin(
    product_id: int,
    admin_info: dict = Depends(require_admin)
):
    """获取产品详情（管理端）"""
    async with engine.begin() as conn:
        product = await ProductService.get_product(conn, product_id)
    
    return success_response(product)


@router.post("/api/manage/products")
async def create_product(
    request: Request,
    product_data: CreateProductRequest,
    admin_info: dict = Depends(require_admin)
):
    """创建产品"""
    async with engine.begin() as conn:
        product_id = await ProductService.create_product(conn, product_data.dict())
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='CREATE',
            operation_module='PRODUCT',
            operation_desc=f"创建产品：{product_data.name}",
            data_after={'product_id': product_id, 'name': product_data.name},
            ip_address=request.client.host if request.client else None
        )
    
    return success_response({'product_id': product_id}, "产品创建成功")


@router.put("/api/manage/products/{product_id}")
async def update_product(
    request: Request,
    product_id: int,
    product_data: UpdateProductRequest,
    admin_info: dict = Depends(require_admin)
):
    """更新产品"""
    async with engine.begin() as conn:
        old_product = await ProductService.get_product(conn, product_id)
        
        await ProductService.update_product(conn, product_id, product_data.dict(exclude_unset=True))
        
        new_product = await ProductService.get_product(conn, product_id)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='UPDATE',
            operation_module='PRODUCT',
            operation_desc=f"更新产品：{old_product['name']}",
            data_before=old_product,
            data_after=new_product,
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="产品更新成功")


@router.delete("/api/manage/products/{product_id}")
async def delete_product(
    request: Request,
    product_id: int,
    admin_info: dict = Depends(require_admin)
):
    """删除产品"""
    async with engine.begin() as conn:
        product = await ProductService.get_product(conn, product_id)
        
        await ProductService.delete_product(conn, product_id)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='DELETE',
            operation_module='PRODUCT',
            operation_desc=f"删除产品：{product['name']}",
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="产品删除成功")


@router.put("/api/manage/products/{product_id}/status")
async def toggle_product_status(
    request: Request,
    product_id: int,
    status: str,
    admin_info: dict = Depends(require_admin)
):
    """上架/下架产品"""
    async with engine.begin() as conn:
        product = await ProductService.get_product(conn, product_id)
        
        await ProductService.toggle_product_status(conn, product_id, status)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='UPDATE',
            operation_module='PRODUCT',
            operation_desc=f"{'上架' if status == 'active' else '下架'}产品：{product['name']}",
            data_before={'status': product['status']},
            data_after={'status': status},
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message=f"产品{'上架' if status == 'active' else '下架'}成功")


@router.post("/api/manage/products/{product_id}/images")
async def upload_product_images(
    request: Request,
    product_id: int,
    files: List[UploadFile] = File(...),
    admin_info: dict = Depends(require_admin)
):
    """上传产品图片"""
    async with engine.begin() as conn:
        images = await FileService.upload_product_images(conn, product_id, files)
        
        # 记录操作日志
        product = await ProductService.get_product(conn, product_id)
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='UPDATE',
            operation_module='PRODUCT',
            operation_desc=f"上传产品图片：{product['name']}（{len(images)}张）",
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(images, "图片上传成功")


@router.delete("/api/manage/products/images/{image_id}")
async def delete_product_image(
    request: Request,
    image_id: int,
    admin_info: dict = Depends(require_admin)
):
    """删除产品图片"""
    async with engine.begin() as conn:
        await FileService.delete_product_image(conn, image_id)
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='DELETE',
            operation_module='PRODUCT',
            operation_desc=f"删除产品图片：{image_id}",
            ip_address=request.client.host if request.client else None
        )
    
    return success_response(message="图片删除成功")
