"""
分类数据访问层
"""
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional, List

from models.database import categories, product_categories


class CategoryRepository:
    """分类仓储"""
    
    @staticmethod
    async def create_category(conn: AsyncConnection, category_data: dict) -> int:
        """创建分类"""
        result = await conn.execute(
            insert(categories).values(**category_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def get_category_by_id(conn: AsyncConnection, category_id: int) -> Optional[dict]:
        """根据ID获取分类"""
        result = await conn.execute(
            select(categories).where(categories.c.id == category_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def update_category(conn: AsyncConnection, category_id: int, category_data: dict) -> bool:
        """更新分类"""
        category_data['updated_at'] = datetime.now()
        result = await conn.execute(
            update(categories)
            .where(categories.c.id == category_id)
            .values(**category_data)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_category(conn: AsyncConnection, category_id: int) -> bool:
        """删除分类"""
        result = await conn.execute(
            delete(categories).where(categories.c.id == category_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def list_categories(conn: AsyncConnection) -> List[dict]:
        """获取所有分类"""
        result = await conn.execute(
            select(categories).order_by(categories.c.sort_order)
        )
        return [dict(row._mapping) for row in result]
    
    @staticmethod
    async def get_category_tree(conn: AsyncConnection) -> List[dict]:
        """获取分类树"""
        # 获取所有分类
        all_categories = await CategoryRepository.list_categories(conn)
        
        # 构建树形结构
        category_map = {cat['id']: {**cat, 'children': []} for cat in all_categories}
        tree = []
        
        for cat in all_categories:
            if cat['parent_id'] is None:
                tree.append(category_map[cat['id']])
            else:
                if cat['parent_id'] in category_map:
                    category_map[cat['parent_id']]['children'].append(category_map[cat['id']])
        
        return tree
    
    @staticmethod
    async def get_children_categories(conn: AsyncConnection, parent_id: int) -> List[dict]:
        """获取子分类"""
        result = await conn.execute(
            select(categories)
            .where(categories.c.parent_id == parent_id)
            .order_by(categories.c.sort_order)
        )
        return [dict(row._mapping) for row in result]
    
    @staticmethod
    async def remove_product_categories(conn: AsyncConnection, category_id: int) -> int:
        """移除分类下的所有产品关联"""
        result = await conn.execute(
            delete(product_categories).where(product_categories.c.category_id == category_id)
        )
        return result.rowcount
