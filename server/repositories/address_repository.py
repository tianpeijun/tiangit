"""
收货地址数据访问层
"""
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional

from models.database import addresses


class AddressRepository:
    """收货地址仓储"""
    
    @staticmethod
    async def get_user_address(conn: AsyncConnection, user_id: int) -> Optional[dict]:
        """获取用户收货地址"""
        result = await conn.execute(
            select(addresses).where(addresses.c.user_id == user_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def create_or_update_address(
        conn: AsyncConnection,
        user_id: int,
        address: str,
        phone: str
    ) -> int:
        """创建或更新收货地址"""
        # 检查是否已存在
        existing = await AddressRepository.get_user_address(conn, user_id)
        
        if existing:
            # 更新
            await conn.execute(
                update(addresses)
                .where(addresses.c.user_id == user_id)
                .values(
                    address=address,
                    phone=phone,
                    updated_at=datetime.now()
                )
            )
            return existing['id']
        else:
            # 创建
            result = await conn.execute(
                insert(addresses).values(
                    user_id=user_id,
                    address=address,
                    phone=phone,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )
            return result.lastrowid
