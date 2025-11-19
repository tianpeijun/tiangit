"""
分类服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import List

from repositories.category_repository import CategoryRepository
from utils.response import ValidationException, NotFoundException


class CategoryService:
    """分类服务"""
    
    @staticmethod
    async def create_category(conn: AsyncConnection, category_data: dict) -> int:
        """创建分类"""
        # 如果是二级分类，验证父分类存在
        if category_data.get('parent_id'):
            parent = await CategoryRepository.get_category_by_id(conn, category_data['parent_id'])
            if not parent:
                raise ValidationException("父分类不存在")
            if parent['parent_id'] is not None:
                raise ValidationException("不支持三级分类")
        
        create_data = {
            'name': category_data['name'],
            'parent_id': category_data.get('parent_id'),
            'sort_order': category_data.get('sort_order', 0),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return await CategoryRepository.create_category(conn, create_data)
    
    @staticmethod
    async def update_category(conn: AsyncConnection, category_id: int, category_data: dict) -> bool:
        """更新分类"""
        category = await CategoryRepository.get_category_by_id(conn, category_id)
        if not category:
            raise NotFoundException("分类不存在")
        
        # 如果更新父分类，验证
        if 'parent_id' in category_data and category_data['parent_id']:
            parent = await CategoryRepository.get_category_by_id(conn, category_data['parent_id'])
            if not parent:
                raise ValidationException("父分类不存在")
            if parent['parent_id'] is not None:
                raise ValidationException("不支持三级分类")
            if category_data['parent_id'] == category_id:
                raise ValidationException("不能将分类设置为自己的子分类")
        
        update_data = {}
        allowed_fields = ['name', 'parent_id', 'sort_order']
        for field in allowed_fields:
            if field in category_data:
                update_data[field] = category_data[field]
        
        if not update_data:
            return True
        
        return await CategoryRepository.update_category(conn, category_id, update_data)
    
    @staticmethod
    async def delete_category(conn: AsyncConnection, category_id: int) -> bool:
        """删除分类"""
        category = await CategoryRepository.get_category_by_id(conn, category_id)
        if not category:
            raise NotFoundException("分类不存在")
        
        # 检查是否有子分类
        children = await CategoryRepository.get_children_categories(conn, category_id)
        if children:
            raise ValidationException("该分类下有子分类，无法删除")
        
        # 移除产品关联
        await CategoryRepository.remove_product_categories(conn, category_id)
        
        return await CategoryRepository.delete_category(conn, category_id)
    
    @staticmethod
    async def get_category(conn: AsyncConnection, category_id: int) -> dict:
        """获取分类详情"""
        category = await CategoryRepository.get_category_by_id(conn, category_id)
        if not category:
            raise NotFoundException("分类不存在")
        
        if category.get('created_at'):
            category['created_at'] = category['created_at'].isoformat()
        if category.get('updated_at'):
            category['updated_at'] = category['updated_at'].isoformat()
        
        return category
    
    @staticmethod
    async def list_categories(conn: AsyncConnection) -> List[dict]:
        """获取所有分类"""
        categories = await CategoryRepository.list_categories(conn)
        
        for cat in categories:
            if cat.get('created_at'):
                cat['created_at'] = cat['created_at'].isoformat()
            if cat.get('updated_at'):
                cat['updated_at'] = cat['updated_at'].isoformat()
        
        return categories
    
    @staticmethod
    async def get_category_tree(conn: AsyncConnection) -> List[dict]:
        """获取分类树"""
        tree = await CategoryRepository.get_category_tree(conn)
        
        def format_dates(cat):
            if cat.get('created_at'):
                cat['created_at'] = cat['created_at'].isoformat()
            if cat.get('updated_at'):
                cat['updated_at'] = cat['updated_at'].isoformat()
            for child in cat.get('children', []):
                format_dates(child)
        
        for cat in tree:
            format_dates(cat)
        
        return tree
