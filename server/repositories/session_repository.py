"""
Session 数据访问层
"""
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime, timedelta
from typing import Optional
import uuid
import json

from models.database import sessions
from config.settings import settings


class SessionRepository:
    """Session 仓储"""
    
    @staticmethod
    async def create_session(conn: AsyncConnection, user_id: int, data: dict = None) -> str:
        """创建 Session"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(seconds=settings.SESSION_EXPIRE_SECONDS)
        
        await conn.execute(
            insert(sessions).values(
                session_id=session_id,
                user_id=user_id,
                data=json.dumps(data) if data else None,
                created_at=datetime.now(),
                expires_at=expires_at
            )
        )
        
        return session_id
    
    @staticmethod
    async def get_session(conn: AsyncConnection, session_id: str) -> Optional[dict]:
        """获取 Session"""
        result = await conn.execute(
            select(sessions).where(
                sessions.c.session_id == session_id,
                sessions.c.expires_at > datetime.now()
            )
        )
        row = result.first()
        
        if row:
            return {
                'id': row.id,
                'session_id': row.session_id,
                'user_id': row.user_id,
                'data': json.loads(row.data) if row.data else None,
                'created_at': row.created_at,
                'expires_at': row.expires_at
            }
        return None
    
    @staticmethod
    async def delete_session(conn: AsyncConnection, session_id: str) -> bool:
        """删除 Session"""
        result = await conn.execute(
            delete(sessions).where(sessions.c.session_id == session_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_user_sessions(conn: AsyncConnection, user_id: int) -> int:
        """删除用户的所有 Session"""
        result = await conn.execute(
            delete(sessions).where(sessions.c.user_id == user_id)
        )
        return result.rowcount
    
    @staticmethod
    async def cleanup_expired_sessions(conn: AsyncConnection) -> int:
        """清理过期的 Session"""
        result = await conn.execute(
            delete(sessions).where(sessions.c.expires_at <= datetime.now())
        )
        return result.rowcount
    
    @staticmethod
    async def update_session_data(conn: AsyncConnection, session_id: str, data: dict) -> bool:
        """更新 Session 数据"""
        result = await conn.execute(
            update(sessions)
            .where(sessions.c.session_id == session_id)
            .values(data=json.dumps(data))
        )
        return result.rowcount > 0
