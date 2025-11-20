"""
购物车数据访问层
"""
from sqlalchemy import select, insert, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import List, Optional

from models.database import carts, products


class CartRepository:
    """购物车仓储"""
    
    @staticmethod
    async def add_to_cart(conn: AsyncConnection, user_id: int, product_id: int, quantity: int) -> int:
        """添加到购物车"""
        # 检查是否已存在
        existing = await CartRepository.get_cart_item(conn, user_id, product_id)
        
        if existing:
            # 更新数量
            new_quantity = existing['quantity'] + quantity
            await conn.execute(
                update(carts)
                .where(and_(carts.c.user_id == user_id, carts.c.product_id == product_id))
                .values(quantity=new_quantity, updated_at=datetime.now())
            )
            return existing['id']
        else:
            # 新增
            result = await conn.execute(
                insert(carts).values(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )
            return result.lastrowid
    
    @staticmethod
    async def get_cart_item(conn: AsyncConnection, user_id: int, product_id: int) -> Optional[dict]:
        """获取购物车项"""
        result = await conn.execute(
            select(carts).where(
                and_(carts.c.user_id == user_id, carts.c.product_id == product_id)
            )
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def update_cart_item(conn: AsyncConnection, user_id: int, product_id: int, quantity: int) -> bool:
        """更新购物车项数量"""
        result = await conn.execute(
            update(carts)
            .where(and_(carts.c.user_id == user_id, carts.c.product_id == product_id))
            .values(quantity=quantity, updated_at=datetime.now())
        )
        return result.rowcount > 0
    
    @staticmethod
    async def remove_from_cart(conn: AsyncConnection, user_id: int, product_id: int) -> bool:
        """从购物车移除"""
        result = await conn.execute(
            delete(carts).where(
                and_(carts.c.user_id == user_id, carts.c.product_id == product_id)
            )
        )
        return result.rowcount > 0
    
    @staticmethod
    async def clear_cart(conn: AsyncConnection, user_id: int) -> int:
        """清空购物车"""
        result = await conn.execute(
            delete(carts).where(carts.c.user_id == user_id)
        )
        return result.rowcount
    
    @staticmethod
    async def get_user_cart(conn: AsyncConnection, user_id: int) -> List[dict]:
        """获取用户购物车"""
        from server.repositories.product_repository import ProductRepository
        from server.config.settings import settings
        
        result = await conn.execute(
            select(carts, products)
            .join(products, carts.c.product_id == products.c.id)
            .where(
                and_(
                    carts.c.user_id == user_id,
                    products.c.status == 'active',
                    products.c.is_deleted == False
                )
            )
            .order_by(carts.c.created_at.desc())
        )
        
        items = []
        for row in result:
            # 获取产品的第一张图片作为缩略图
            images = await ProductRepository.get_product_images(conn, row.product_id)
            thumbnail_url = None
            if images:
                first_img = images[0]
                thumbnail_url = f"{settings.STATIC_URL}/{first_img['file_path'].replace('static/images/', '')}/{first_img['thumbnail_filename']}"
            
            items.append({
                'cart_id': row.id,
                'product_id': row.product_id,
                'quantity': row.quantity,
                'product_name': row.name,
                'product_description': row.description,
                'product_thumbnail': thumbnail_url,
                'points_required': row.points_required,
                'subtotal_points': row.quantity * row.points_required
            })
        
        return items
    
    @staticmethod
    async def get_cart_total_quantity(conn: AsyncConnection, user_id: int) -> int:
        """获取购物车总数量"""
        result = await conn.execute(
            select(func.sum(carts.c.quantity))
            .where(carts.c.user_id == user_id)
        )
        total = result.scalar()
        return total if total else 0
    
    @staticmethod
    async def get_cart_total_points(conn: AsyncConnection, user_id: int) -> int:
        """获取购物车总积分"""
        result = await conn.execute(
            select(func.sum(carts.c.quantity * products.c.points_required))
            .select_from(carts.join(products))
            .where(carts.c.user_id == user_id)
        )
        total = result.scalar()
        return total if total else 0
