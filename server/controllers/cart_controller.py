"""
购物车控制器
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from models.database import engine
from services.cart_service import CartService
from middleware.auth_middleware import require_employee
from utils.response import success_response

router = APIRouter()


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1


class UpdateCartRequest(BaseModel):
    product_id: int
    quantity: int


@router.get("")
async def get_cart(user_info: dict = Depends(require_employee)):
    """获取购物车"""
    async with engine.begin() as conn:
        cart = await CartService.get_cart(conn, user_info['user_id'])
    
    return success_response(cart)


@router.post("/add")
async def add_to_cart(
    cart_data: AddToCartRequest,
    user_info: dict = Depends(require_employee)
):
    """添加到购物车"""
    async with engine.begin() as conn:
        result = await CartService.add_to_cart(
            conn,
            user_info['user_id'],
            cart_data.product_id,
            cart_data.quantity
        )
    
    return success_response(result)


@router.put("/update")
async def update_cart_item(
    cart_data: UpdateCartRequest,
    user_info: dict = Depends(require_employee)
):
    """更新购物车商品数量"""
    async with engine.begin() as conn:
        await CartService.update_cart_item(
            conn,
            user_info['user_id'],
            cart_data.product_id,
            cart_data.quantity
        )
    
    return success_response(message="更新成功")


@router.delete("/remove/{product_id}")
async def remove_from_cart(
    product_id: int,
    user_info: dict = Depends(require_employee)
):
    """从购物车移除"""
    async with engine.begin() as conn:
        await CartService.remove_from_cart(conn, user_info['user_id'], product_id)
    
    return success_response(message="移除成功")


@router.delete("/clear")
async def clear_cart(user_info: dict = Depends(require_employee)):
    """清空购物车"""
    async with engine.begin() as conn:
        count = await CartService.clear_cart(conn, user_info['user_id'])
    
    return success_response({'count': count}, "购物车已清空")
