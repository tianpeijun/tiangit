"""
产品数据访问层
"""
from sqlalchemy import select, insert, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional, List

from models.database import products, product_images, product_categories


class ProductRepository:
    """产品仓储"""
    
    @staticmethod
    async def create_product(conn: AsyncConnection, product_data: dict) -> int:
        """创建产品"""
        result = await conn.execute(
            insert(products).values(**product_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def get_product_by_id(conn: AsyncConnection, product_id: int, include_deleted: bool = False) -> Optional[dict]:
        """根据ID获取产品"""
        query = select(products).where(products.c.id == product_id)
        if not include_deleted:
            query = query.where(products.c.is_deleted == False)
        
        result = await conn.execute(query)
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def update_product(conn: AsyncConnection, product_id: int, product_data: dict) -> bool:
        """更新产品"""
        product_data['updated_at'] = datetime.now()
        result = await conn.execute(
            update(products)
            .where(products.c.id == product_id)
            .values(**product_data)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_product(conn: AsyncConnection, product_id: int) -> bool:
        """软删除产品"""
        result = await conn.execute(
            update(products)
            .where(products.c.id == product_id)
            .values(is_deleted=True, updated_at=datetime.now())
        )
        return result.rowcount > 0
    
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
        include_deleted: bool = False
    ) -> tuple[List[dict], int]:
        """获取产品列表"""
        # 构建查询条件
        conditions = [products.c.is_deleted == False] if not include_deleted else []
        
        if status:
            conditions.append(products.c.status == status)
        if keyword:
            conditions.append(products.c.name.like(f'%{keyword}%'))
        
        # 如果有分类筛选，需要 JOIN
        if category_ids:
            # 查询总数
            count_query = (
                select(func.count(func.distinct(products.c.id)))
                .select_from(products.join(product_categories))
                .where(
                    and_(
                        *conditions,
                        product_categories.c.category_id.in_(category_ids)
                    )
                )
            )
            total_result = await conn.execute(count_query)
            total = total_result.scalar()
            
            # 查询数据
            query = (
                select(products)
                .join(product_categories)
                .where(
                    and_(
                        *conditions,
                        product_categories.c.category_id.in_(category_ids)
                    )
                )
                .distinct()
            )
        else:
            # 查询总数
            count_query = select(func.count()).select_from(products)
            if conditions:
                count_query = count_query.where(*conditions)
            total_result = await conn.execute(count_query)
            total = total_result.scalar()
            
            # 查询数据
            query = select(products)
            if conditions:
                query = query.where(*conditions)
        
        # 排序
        if sort_by == 'points':
            order_col = products.c.points_required
        else:
            order_col = products.c.created_at
        
        if sort_order == 'asc':
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())
        
        # 分页
        query = query.limit(page_size).offset((page - 1) * page_size)
        
        result = await conn.execute(query)
        items = [dict(row._mapping) for row in result]
        
        return items, total
    
    @staticmethod
    async def add_product_image(conn: AsyncConnection, image_data: dict) -> int:
        """添加产品图片"""
        result = await conn.execute(
            insert(product_images).values(**image_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def get_product_images(conn: AsyncConnection, product_id: int) -> List[dict]:
        """获取产品图片"""
        result = await conn.execute(
            select(product_images)
            .where(product_images.c.product_id == product_id)
            .order_by(product_images.c.sort_order)
        )
        return [dict(row._mapping) for row in result]
    
    @staticmethod
    async def get_image_by_id(conn: AsyncConnection, image_id: int) -> Optional[dict]:
        """根据ID获取图片"""
        result = await conn.execute(
            select(product_images).where(product_images.c.id == image_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def delete_product_image(conn: AsyncConnection, image_id: int) -> bool:
        """删除产品图片"""
        result = await conn.execute(
            delete(product_images).where(product_images.c.id == image_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_product_images(conn: AsyncConnection, product_id: int) -> int:
        """删除产品的所有图片"""
        result = await conn.execute(
            delete(product_images).where(product_images.c.product_id == product_id)
        )
        return result.rowcount
    
    @staticmethod
    async def count_product_images(conn: AsyncConnection, product_id: int) -> int:
        """统计产品图片数量"""
        result = await conn.execute(
            select(func.count())
            .select_from(product_images)
            .where(product_images.c.product_id == product_id)
        )
        return result.scalar()
    
    @staticmethod
    async def add_product_category(conn: AsyncConnection, product_id: int, category_id: int) -> int:
        """添加产品分类关联"""
        result = await conn.execute(
            insert(product_categories).values(
                product_id=product_id,
                category_id=category_id,
                created_at=datetime.now()
            )
        )
        return result.lastrowid
    
    @staticmethod
    async def remove_product_category(conn: AsyncConnection, product_id: int, category_id: int) -> bool:
        """移除产品分类关联"""
        result = await conn.execute(
            delete(product_categories).where(
                and_(
                    product_categories.c.product_id == product_id,
                    product_categories.c.category_id == category_id
                )
            )
        )
        return result.rowcount > 0
    
    @staticmethod
    async def remove_all_product_categories(conn: AsyncConnection, product_id: int) -> int:
        """移除产品的所有分类关联"""
        result = await conn.execute(
            delete(product_categories).where(product_categories.c.product_id == product_id)
        )
        return result.rowcount
    
    @staticmethod
    async def get_product_categories(conn: AsyncConnection, product_id: int) -> List[int]:
        """获取产品的分类ID列表"""
        result = await conn.execute(
            select(product_categories.c.category_id)
            .where(product_categories.c.product_id == product_id)
        )
        return [row.category_id for row in result]
