"""
用户数据访问层
"""
from sqlalchemy import select, insert, update, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional, List

from models.database import users


class UserRepository:
    """用户仓储"""
    
    @staticmethod
    async def create_user(conn: AsyncConnection, user_data: dict) -> int:
        """创建用户"""
        result = await conn.execute(
            insert(users).values(**user_data)
        )
        return result.lastrowid
    
    @staticmethod
    async def get_user_by_id(conn: AsyncConnection, user_id: int) -> Optional[dict]:
        """根据ID获取用户"""
        result = await conn.execute(
            select(users).where(users.c.id == user_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def get_user_by_username(conn: AsyncConnection, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        result = await conn.execute(
            select(users).where(users.c.username == username)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def get_user_by_employee_id(conn: AsyncConnection, employee_id: str) -> Optional[dict]:
        """根据工号获取用户"""
        result = await conn.execute(
            select(users).where(users.c.employee_id == employee_id)
        )
        row = result.first()
        return dict(row._mapping) if row else None
    
    @staticmethod
    async def update_user(conn: AsyncConnection, user_id: int, user_data: dict) -> bool:
        """更新用户信息"""
        user_data['updated_at'] = datetime.now()
        result = await conn.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(**user_data)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_user(conn: AsyncConnection, user_id: int) -> bool:
        """删除用户"""
        result = await conn.execute(
            delete(users).where(users.c.id == user_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def update_password(conn: AsyncConnection, user_id: int, password_hash: str) -> bool:
        """更新密码"""
        result = await conn.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(password_hash=password_hash, updated_at=datetime.now())
        )
        return result.rowcount > 0
    
    @staticmethod
    async def update_last_login(conn: AsyncConnection, user_id: int) -> bool:
        """更新最后登录时间"""
        result = await conn.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(last_login_at=datetime.now())
        )
        return result.rowcount > 0
    
    @staticmethod
    async def update_points(conn: AsyncConnection, user_id: int, points: int) -> bool:
        """更新积分"""
        result = await conn.execute(
            update(users)
            .where(users.c.id == user_id)
            .values(points=points, updated_at=datetime.now())
        )
        return result.rowcount > 0
    
    @staticmethod
    async def get_user_points(conn: AsyncConnection, user_id: int) -> Optional[int]:
        """获取用户积分"""
        result = await conn.execute(
            select(users.c.points).where(users.c.id == user_id)
        )
        row = result.first()
        return row.points if row else None
    
    @staticmethod
    async def list_users(
        conn: AsyncConnection,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[dict], int]:
        """获取用户列表"""
        # 构建查询条件
        conditions = []
        if role:
            conditions.append(users.c.role == role)
        if is_active is not None:
            conditions.append(users.c.is_active == is_active)
        if keyword:
            conditions.append(
                or_(
                    users.c.username.like(f'%{keyword}%'),
                    users.c.real_name.like(f'%{keyword}%'),
                    users.c.employee_id.like(f'%{keyword}%')
                )
            )
        
        # 查询总数
        count_query = select(func.count()).select_from(users)
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await conn.execute(count_query)
        total = total_result.scalar()
        
        # 查询数据
        query = select(users)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(users.c.created_at.desc())
        query = query.limit(page_size).offset((page - 1) * page_size)
        
        result = await conn.execute(query)
        items = [dict(row._mapping) for row in result]
        
        return items, total
    
    @staticmethod
    async def lock_user_for_update(conn: AsyncConnection, user_id: int) -> Optional[dict]:
        """锁定用户记录（用于事务）"""
        result = await conn.execute(
            select(users).where(users.c.id == user_id).with_for_update()
        )
        row = result.first()
        return dict(row._mapping) if row else None
