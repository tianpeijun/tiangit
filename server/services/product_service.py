"""
产品服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional, List

from repositories.product_repository import ProductRepository
from repositories.category_repository import CategoryRepository
from utils.response import ValidationException, NotFoundException
from config.settings import settings


class ProductService:
    """产品服务"""
    
    @staticmethod
    async def create_product(conn: AsyncConnection, product_data: dict) -> int:
        """创建产品"""
        create_data = {
            'name': product_data['name'],
            'description': product_data.get('description'),
            'points_required': product_data['points_required'],
            'status': product_data.get('status', 'inactive'),
            'is_deleted': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        product_id = await ProductRepository.create_product(conn, create_data)
        
        # 关联分类
        if 'category_ids' in product_data and product_data['category_ids']:
            for category_id in product_data['category_ids']:
                await ProductRepository.add_product_category(conn, product_id, category_id)
        
        return product_id
    
    @staticmethod
    async def update_product(conn: AsyncConnection, product_id: int, product_data: dict) -> bool:
        """更新产品"""
        product = await ProductRepository.get_product_by_id(conn, product_id, include_deleted=True)
        if not product:
            raise NotFoundException("产品不存在")
        
        update_data = {}
        allowed_fields = ['name', 'description', 'points_required', 'status']
        for field in allowed_fields:
            if field in product_data:
                update_data[field] = product_data[field]
        
        if update_data:
            await ProductRepository.update_product(conn, product_id, update_data)
        
        # 更新分类关联
        if 'category_ids' in product_data:
            # 移除所有现有关联
            await ProductRepository.remove_all_product_categories(conn, product_id)
            # 添加新关联
            for category_id in product_data['category_ids']:
                await ProductRepository.add_product_category(conn, product_id, category_id)
        
        return True
    
    @staticmethod
    async def delete_product(conn: AsyncConnection, product_id: int) -> bool:
        """删除产品（软删除）"""
        product = await ProductRepository.get_product_by_id(conn, product_id)
        if not product:
            raise NotFoundException("产品不存在")
        
        return await ProductRepository.delete_product(conn, product_id)
    
    @staticmethod
    async def toggle_product_status(conn: AsyncConnection, product_id: int, status: str) -> bool:
        """上架/下架产品"""
        if status not in ['active', 'inactive']:
            raise ValidationException("无效的状态值")
        
        product = await ProductRepository.get_product_by_id(conn, product_id)
        if not product:
            raise NotFoundException("产品不存在")
        
        return await ProductRepository.update_product(conn, product_id, {'status': status})
    
    @staticmethod
    async def get_product(conn: AsyncConnection, product_id: int, include_images: bool = True) -> dict:
        """获取产品详情"""
        product = await ProductRepository.get_product_by_id(conn, product_id)
        if not product:
            raise NotFoundException("产品不存在")
        
        # 格式化日期
        if product.get('created_at'):
            product['created_at'] = product['created_at'].isoformat()
        if product.get('updated_at'):
            product['updated_at'] = product['updated_at'].isoformat()
        
        # 获取图片
        if include_images:
            images = await ProductRepository.get_product_images(conn, product_id)
            product['images'] = []
            for img in images:
                product['images'].append({
                    'id': img['id'],
                    'url': f"{settings.STATIC_URL}/{img['file_path'].replace('static/images/', '')}/{img['stored_filename']}",
                    'thumbnail_url': f"{settings.STATIC_URL}/{img['file_path'].replace('static/images/', '')}/{img['thumbnail_filename']}",
                    'sort_order': img['sort_order']
                })
        
        # 获取分类
        category_ids = await ProductRepository.get_product_categories(conn, product_id)
        product['category_ids'] = category_ids
        
        return product
    
    @staticmethod
    async def list_products(
        conn: AsyncConnection,
        status: Optional[str] = None,
        category_ids: Optional[List[int]] = None,
        keyword: Optional[str] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc',
        page: int = 1,
        page_size: int = 20,
        include_images: bool = True
    ) -> dict:
        """获取产品列表"""
        items, total = await ProductRepository.list_products(
            conn, status, category_ids, keyword, sort_by, sort_order, page, page_size
        )
        
        # 格式化数据
        for item in items:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].isoformat()
            
            # 获取图片
            if include_images:
                images = await ProductRepository.get_product_images(conn, item['id'])
                item['images'] = []
                for img in images:
                    item['images'].append({
                        'id': img['id'],
                        'url': f"{settings.STATIC_URL}/{img['file_path'].replace('static/images/', '')}/{img['stored_filename']}",
                        'thumbnail_url': f"{settings.STATIC_URL}/{img['file_path'].replace('static/images/', '')}/{img['thumbnail_filename']}",
                        'sort_order': img['sort_order']
                    })
            
            # 获取分类
            category_ids_list = await ProductRepository.get_product_categories(conn, item['id'])
            item['category_ids'] = category_ids_list
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
