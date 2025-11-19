"""
积分数据访问层
"""
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import List, Optional

from models.database import point_transactions


class PointRepository:
    """积分仓储"""
    
    @staticmethod
    async def create_transaction(conn: AsyncConnection, transaction_data: dict) -> int:
        """创建积分交易记录"""
        result = await conn.execute(
            insert(point_transactions).values(**transaction_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def get_user_transactions(
        conn: AsyncConnection,
        user_id: int,
        transaction_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[dict], int]:
        """获取用户积分交易记录"""
        # 构建查询条件
        conditions = [point_transactions.c.user_id == user_id]
        if transaction_type:
            conditions.append(point_transactions.c.transaction_type == transaction_type)
        
        # 查询总数
        count_result = await conn.execute(
            select(func.count())
            .select_from(point_transactions)
            .where(*conditions)
        )
        total = count_result.scalar()
        
        # 查询数据
        result = await conn.execute(
            select(point_transactions)
            .where(*conditions)
            .order_by(point_transactions.c.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        items = [dict(row._mapping) for row in result]
        
        return items, total
    
    @staticmethod
    async def get_all_transactions(
        conn: AsyncConnection,
        transaction_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[dict], int]:
        """获取所有积分交易记录（管理员）"""
        # 构建查询条件
        conditions = []
        if transaction_type:
            conditions.append(point_transactions.c.transaction_type == transaction_type)
        
        # 查询总数
        count_query = select(func.count()).select_from(point_transactions)
        if conditions:
            count_query = count_query.where(*conditions)
        count_result = await conn.execute(count_query)
        total = count_result.scalar()
        
        # 查询数据
        query = select(point_transactions)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(point_transactions.c.created_at.desc())
        query = query.limit(page_size).offset((page - 1) * page_size)
        
        result = await conn.execute(query)
        items = [dict(row._mapping) for row in result]
        
        return items, total
