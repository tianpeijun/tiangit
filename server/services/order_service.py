"""
订单服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional

from repositories.order_repository import OrderRepository
from repositories.cart_repository import CartRepository
from repositories.user_repository import UserRepository
from repositories.address_repository import AddressRepository
from repositories.point_repository import PointRepository
from utils.response import ValidationException, NotFoundException


class OrderService:
    """订单服务"""
    
    @staticmethod
    async def create_order_from_cart(
        conn: AsyncConnection,
        user_id: int,
        address: str,
        phone: str
    ) -> dict:
        """从购物车创建订单"""
        # 获取购物车
        cart_items = await CartRepository.get_user_cart(conn, user_id)
        if not cart_items:
            raise ValidationException("购物车为空")
        
        # 计算总积分
        total_points = sum(item['subtotal_points'] for item in cart_items)
        
        # 锁定用户记录并检查积分
        user = await UserRepository.lock_user_for_update(conn, user_id)
        if not user:
            raise NotFoundException("用户不存在")
        
        if user['points'] < total_points:
            raise ValidationException(f"积分不足，当前积分：{user['points']}，需要：{total_points}")
        
        # 扣除积分
        new_points = user['points'] - total_points
        await UserRepository.update_points(conn, user_id, new_points)
        
        # 创建订单
        order_no = OrderRepository.generate_order_no()
        order_data = {
            'order_no': order_no,
            'user_id': user_id,
            'total_points': total_points,
            'status': 'completed',
            'shipping_address': address,
            'shipping_phone': phone,
            'created_at': datetime.now()
        }
        order_id = await OrderRepository.create_order(conn, order_data)
        
        # 创建订单明细
        for item in cart_items:
            item_data = {
                'order_id': order_id,
                'product_id': item['product_id'],
                'product_name': item['product_name'],
                'quantity': item['quantity'],
                'points_per_item': item['points_required'],
                'subtotal_points': item['subtotal_points'],
                'created_at': datetime.now()
            }
            await OrderRepository.create_order_item(conn, item_data)
        
        # 创建积分交易记录
        transaction_data = {
            'user_id': user_id,
            'transaction_type': 'consume',
            'amount': -total_points,
            'balance_after': new_points,
            'order_id': order_id,
            'description': f'兑换订单：{order_no}',
            'created_at': datetime.now()
        }
        await PointRepository.create_transaction(conn, transaction_data)
        
        # 保存或更新收货地址
        await AddressRepository.create_or_update_address(conn, user_id, address, phone)
        
        # 清空购物车
        await CartRepository.clear_cart(conn, user_id)
        
        return {
            'order_id': order_id,
            'order_no': order_no,
            'total_points': total_points,
            'balance_after': new_points
        }
    
    @staticmethod
    async def get_order(conn: AsyncConnection, order_id: int, user_id: Optional[int] = None) -> dict:
        """获取订单详情"""
        order = await OrderRepository.get_order_by_id(conn, order_id)
        if not order:
            raise NotFoundException("订单不存在")
        
        # 如果指定了用户ID，验证订单归属
        if user_id is not None and order['user_id'] != user_id:
            raise ValidationException("无权访问该订单")
        
        # 获取订单明细
        items = await OrderRepository.get_order_items(conn, order_id)
        
        # 格式化日期
        if order.get('created_at'):
            order['created_at'] = order['created_at'].isoformat()
        
        for item in items:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
        
        order['items'] = items
        
        return order
    
    @staticmethod
    async def list_user_orders(
        conn: AsyncConnection,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取用户订单列表"""
        items, total = await OrderRepository.list_user_orders(conn, user_id, page, page_size)
        
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
