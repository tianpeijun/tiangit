"""
积分控制器
"""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import List, Optional

from models.database import engine
from services.point_service import PointService
from services.admin_log_service import AdminLogService
from middleware.auth_middleware import require_employee, require_admin
from utils.response import success_response

router = APIRouter()


class GrantPointsRequest(BaseModel):
    user_ids: List[int]
    amount: int
    description: Optional[str] = None


# 员工端接口
@router.get("/api/personal/points/balance")
async def get_balance(user_info: dict = Depends(require_employee)):
    """获取积分余额"""
    async with engine.begin() as conn:
        balance = await PointService.get_user_balance(conn, user_info['user_id'])
    
    return success_response({'balance': balance})


@router.get("/api/personal/points/transactions")
async def get_user_transactions(
    transaction_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user_info: dict = Depends(require_employee)
):
    """获取积分明细"""
    async with engine.begin() as conn:
        result = await PointService.get_user_transactions(
            conn,
            user_info['user_id'],
            transaction_type,
            page,
            page_size
        )
    
    return success_response(result)


# 管理端接口
@router.post("/api/manage/points/grant")
async def grant_points(
    request: Request,
    grant_data: GrantPointsRequest,
    admin_info: dict = Depends(require_admin)
):
    """发放积分"""
    async with engine.begin() as conn:
        count = await PointService.grant_points(
            conn,
            grant_data.user_ids,
            grant_data.amount,
            admin_info['user_id'],
            grant_data.description
        )
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='GRANT_POINTS',
            operation_module='POINTS',
            operation_desc=f"发放积分：{grant_data.amount}分给{count}个用户",
            data_after={'user_ids': grant_data.user_ids, 'amount': grant_data.amount},
            ip_address=request.client.host if request.client else None
        )
    
    return success_response({'count': count}, f"成功发放积分给{count}个用户")


@router.post("/api/manage/points/grant-batch")
async def grant_points_batch(
    request: Request,
    amount: int,
    description: Optional[str] = None,
    admin_info: dict = Depends(require_admin)
):
    """批量发放积分（所有员工）"""
    from repositories.user_repository import UserRepository
    
    async with engine.begin() as conn:
        # 获取所有员工
        users, _ = await UserRepository.list_users(conn, role='employee', is_active=True, page=1, page_size=1000)
        user_ids = [user['id'] for user in users]
        
        count = await PointService.grant_points(
            conn,
            user_ids,
            amount,
            admin_info['user_id'],
            description or '批量发放积分'
        )
        
        # 记录操作日志
        await AdminLogService.log_operation(
            conn,
            admin_id=admin_info['user_id'],
            operation_type='GRANT_POINTS',
            operation_module='POINTS',
            operation_desc=f"批量发放积分：{amount}分给所有员工",
            data_after={'amount': amount, 'count': count},
            ip_address=request.client.host if request.client else None
        )
    
    return success_response({'count': count}, f"成功发放积分给{count}个员工")


@router.get("/api/manage/points/transactions")
async def get_all_transactions(
    transaction_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    admin_info: dict = Depends(require_admin)
):
    """获取所有积分交易记录"""
    async with engine.begin() as conn:
        result = await PointService.get_all_transactions(
            conn,
            transaction_type,
            page,
            page_size
        )
    
    return success_response(result)
