"""
操作日志数据访问层
"""
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import List, Optional

from models.database import admin_logs


class AdminLogRepository:
    """操作日志仓储"""
    
    @staticmethod
    async def create_log(conn: AsyncConnection, log_data: dict) -> int:
        """创建操作日志"""
        result = await conn.execute(
            insert(admin_logs).values(**log_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def get_log_by_id(conn: AsyncConnection, log_id: int) -> Optional[dict]:
        """根据ID获取日志"""
        result = await conn.execute(
            select(admin_logs).where(admin_logs.c.id == log_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def list_logs(
        conn: AsyncConnection,
        admin_id: Optional[int] = None,
        operation_type: Optional[str] = None,
        operation_module: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[dict], int]:
        """获取操作日志列表"""
        # 构建查询条件
        conditions = []
        if admin_id:
            conditions.append(admin_logs.c.admin_id == admin_id)
        if operation_type:
            conditions.append(admin_logs.c.operation_type == operation_type)
        if operation_module:
            conditions.append(admin_logs.c.operation_module == operation_module)
        if start_date:
            conditions.append(admin_logs.c.created_at >= start_date)
        if end_date:
            conditions.append(admin_logs.c.created_at <= end_date)
        
        # 查询总数
        count_query = select(func.count()).select_from(admin_logs)
        if conditions:
            count_query = count_query.where(*conditions)
        count_result = await conn.execute(count_query)
        total = count_result.scalar()
        
        # 查询数据
        query = select(admin_logs)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(admin_logs.c.created_at.desc())
        query = query.limit(page_size).offset((page - 1) * page_size)
        
        result = await conn.execute(query)
        items = [dict(row._mapping) for row in result]
        
        return items, total
