"""
订单控制器
"""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.database import engine
from services.order_service import OrderService
from repositories.address_repository import AddressRepository
from middleware.auth_middleware import require_employee
from utils.response import success_response
from config.settings import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class CreateOrderRequest(BaseModel):
    address: str
    phone: str


@router.post("/api/personal/orders/create")
@limiter.limit(settings.RATE_LIMIT_EXCHANGE)
async def create_order(
    request: Request,
    order_data: CreateOrderRequest,
    user_info: dict = Depends(require_employee)
):
    """创建订单（从购物车）"""
    async with engine.begin() as conn:
        result = await OrderService.create_order_from_cart(
            conn,
            user_info['user_id'],
            order_data.address,
            order_data.phone
        )
    
    return success_response(result, "兑换成功")


@router.get("/api/personal/orders")
async def list_user_orders(
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_employee)
):
    """获取用户订单列表"""
    async with engine.begin() as conn:
        result = await OrderService.list_user_orders(conn, user_info['user_id'], page, page_size)
    
    return success_response(result)


@router.get("/api/personal/orders/{order_id}")
async def get_order(
    order_id: int,
    user_info: dict = Depends(require_employee)
):
    """获取订单详情"""
    async with engine.begin() as conn:
        order = await OrderService.get_order(conn, order_id, user_info['user_id'])
    
    return success_response(order)
