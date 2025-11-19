"""
订单数据访问层
"""
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import List, Optional
import uuid

from models.database import orders, order_items, products


class OrderRepository:
    """订单仓储"""
    
    @staticmethod
    def generate_order_no() -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = str(uuid.uuid4())[:8].upper()
        return f"ORD{timestamp}{random_str}"
    
    @staticmethod
    async def create_order(conn: AsyncConnection, order_data: dict) -> int:
        """创建订单"""
        result = await conn.execute(
            insert(orders).values(**order_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def create_order_item(conn: AsyncConnection, item_data: dict) -> int:
        """创建订单明细"""
        result = await conn.execute(
            insert(order_items).values(**item_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def get_order_by_id(conn: AsyncConnection, order_id: int) -> Optional[dict]:
        """根据ID获取订单"""
        result = await conn.execute(
            select(orders).where(orders.c.id == order_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def get_order_by_no(conn: AsyncConnection, order_no: str) -> Optional[dict]:
        """根据订单号获取订单"""
        result = await conn.execute(
            select(orders).where(orders.c.order_no == order_no)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def get_order_items(conn: AsyncConnection, order_id: int) -> List[dict]:
        """获取订单明细"""
        result = await conn.execute(
            select(order_items)
            .where(order_items.c.order_id == order_id)
            .order_by(order_items.c.id)
        )
        return [dict(row._mapping) for row in result]
    
    @staticmethod
    async def list_user_orders(
        conn: AsyncConnection,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[dict], int]:
        """获取用户订单列表"""
        # 查询总数
        count_result = await conn.execute(
            select(func.count())
            .select_from(orders)
            .where(orders.c.user_id == user_id)
        )
        total = count_result.scalar()
        
        # 查询数据
        result = await conn.execute(
            select(orders)
            .where(orders.c.user_id == user_id)
            .order_by(orders.c.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        items = [dict(row._mapping) for row in result]
        
        return items, total
    
    @staticmethod
    async def list_all_orders(
        conn: AsyncConnection,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[dict], int]:
        """获取所有订单列表（管理员）"""
        # 查询总数
        count_result = await conn.execute(
            select(func.count()).select_from(orders)
        )
        total = count_result.scalar()
        
        # 查询数据
        result = await conn.execute(
            select(orders)
            .order_by(orders.c.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        items = [dict(row._mapping) for row in result]
        
        return items, total
