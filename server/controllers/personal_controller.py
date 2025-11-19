"""
个人中心控制器
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from models.database import engine
from repositories.address_repository import AddressRepository
from middleware.auth_middleware import require_employee
from utils.response import success_response

router = APIRouter()


class UpdateAddressRequest(BaseModel):
    address: str
    phone: str


@router.get("/api/personal/profile")
async def get_profile(user_info: dict = Depends(require_employee)):
    """获取个人信息"""
    from services.auth_service import AuthService
    from fastapi import Request
    
    # 这里直接返回user_info即可，因为已经包含了基本信息
    return success_response(user_info)


@router.get("/api/personal/address")
async def get_address(user_info: dict = Depends(require_employee)):
    """获取收货地址"""
    async with engine.begin() as conn:
        address = await AddressRepository.get_user_address(conn, user_info['user_id'])
    
    return success_response(address)


@router.put("/api/personal/address")
async def update_address(
    address_data: UpdateAddressRequest,
    user_info: dict = Depends(require_employee)
):
    """更新收货地址"""
    async with engine.begin() as conn:
        await AddressRepository.create_or_update_address(
            conn,
            user_info['user_id'],
            address_data.address,
            address_data.phone
        )
    
    return success_response(message="收货地址更新成功")
