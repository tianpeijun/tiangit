"""
积分服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import List, Optional

from repositories.point_repository import PointRepository
from repositories.user_repository import UserRepository
from utils.response import ValidationException, NotFoundException


class PointService:
    """积分服务"""
    
    @staticmethod
    async def grant_points(
        conn: AsyncConnection,
        user_ids: List[int],
        amount: int,
        admin_id: int,
        description: Optional[str] = None
    ) -> int:
        """发放积分"""
        if amount <= 0:
            raise ValidationException("发放积分必须大于0")
        
        granted_count = 0
        
        for user_id in user_ids:
            # 获取用户
            user = await UserRepository.get_user_by_id(conn, user_id)
            if not user:
                continue
            
            # 更新积分
            new_points = user['points'] + amount
            await UserRepository.update_points(conn, user_id, new_points)
            
            # 创建积分交易记录
            transaction_data = {
                'user_id': user_id,
                'transaction_type': 'grant',
                'amount': amount,
                'balance_after': new_points,
                'admin_id': admin_id,
                'description': description or '管理员发放积分',
                'created_at': datetime.now()
            }
            await PointRepository.create_transaction(conn, transaction_data)
            
            granted_count += 1
        
        return granted_count
    
    @staticmethod
    async def get_user_balance(conn: AsyncConnection, user_id: int) -> int:
        """获取用户积分余额"""
        points = await UserRepository.get_user_points(conn, user_id)
        if points is None:
            raise NotFoundException("用户不存在")
        return points
    
    @staticmethod
    async def get_user_transactions(
        conn: AsyncConnection,
        user_id: int,
        transaction_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取用户积分明细"""
        items, total = await PointRepository.get_user_transactions(
            conn, user_id, transaction_type, page, page_size
        )
        
        # 格式化日期
        for item in items:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    @staticmethod
    async def get_all_transactions(
        conn: AsyncConnection,
        transaction_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取所有积分交易记录（管理员）"""
        items, total = await PointRepository.get_all_transactions(
            conn, transaction_type, page, page_size
        )
        
        # 格式化日期
        for item in items:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
