"""
购物车服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List

from repositories.cart_repository import CartRepository
from repositories.product_repository import ProductRepository
from utils.response import ValidationException, NotFoundException
from config.settings import settings


class CartService:
    """购物车服务"""
    
    @staticmethod
    async def add_to_cart(conn: AsyncConnection, user_id: int, product_id: int, quantity: int = 1) -> dict:
        """添加到购物车"""
        if quantity <= 0:
            raise ValidationException("数量必须大于0")
        
        # 检查产品是否存在且已上架
        product = await ProductRepository.get_product_by_id(conn, product_id)
        if not product:
            raise NotFoundException("产品不存在")
        if product['status'] != 'active':
            raise ValidationException("产品未上架")
        
        # 检查购物车总数量
        current_total = await CartRepository.get_cart_total_quantity(conn, user_id)
        if current_total + quantity > settings.MAX_CART_ITEMS:
            raise ValidationException(f"购物车商品数量不能超过{settings.MAX_CART_ITEMS}个")
        
        # 添加到购物车
        cart_id = await CartRepository.add_to_cart(conn, user_id, product_id, quantity)
        
        return {'cart_id': cart_id, 'message': '添加成功'}
    
    @staticmethod
    async def update_cart_item(conn: AsyncConnection, user_id: int, product_id: int, quantity: int) -> bool:
        """更新购物车商品数量"""
        if quantity <= 0:
            raise ValidationException("数量必须大于0")
        
        # 检查购物车项是否存在
        cart_item = await CartRepository.get_cart_item(conn, user_id, product_id)
        if not cart_item:
            raise NotFoundException("购物车中没有该商品")
        
        # 检查购物车总数量
        current_total = await CartRepository.get_cart_total_quantity(conn, user_id)
        quantity_diff = quantity - cart_item['quantity']
        if current_total + quantity_diff > settings.MAX_CART_ITEMS:
            raise ValidationException(f"购物车商品数量不能超过{settings.MAX_CART_ITEMS}个")
        
        return await CartRepository.update_cart_item(conn, user_id, product_id, quantity)
    
    @staticmethod
    async def remove_from_cart(conn: AsyncConnection, user_id: int, product_id: int) -> bool:
        """从购物车移除"""
        cart_item = await CartRepository.get_cart_item(conn, user_id, product_id)
        if not cart_item:
            raise NotFoundException("购物车中没有该商品")
        
        return await CartRepository.remove_from_cart(conn, user_id, product_id)
    
    @staticmethod
    async def clear_cart(conn: AsyncConnection, user_id: int) -> int:
        """清空购物车"""
        return await CartRepository.clear_cart(conn, user_id)
    
    @staticmethod
    async def get_cart(conn: AsyncConnection, user_id: int) -> dict:
        """获取购物车"""
        items = await CartRepository.get_user_cart(conn, user_id)
        
        # 计算总计
        total_quantity = sum(item['quantity'] for item in items)
        total_points = sum(item['subtotal_points'] for item in items)
        
        return {
            'items': items,
            'total_quantity': total_quantity,
            'total_points': total_points
        }
