"""
操作日志控制器
"""
from fastapi import APIRouter, Depends
from typing import Optional
from datetime import datetime

from models.database import engine
from services.admin_log_service import AdminLogService
from middleware.auth_middleware import require_admin
from utils.response import success_response

router = APIRouter()


@router.get("")
async def list_logs(
    admin_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    operation_module: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    admin_info: dict = Depends(require_admin)
):
    """获取操作日志列表"""
    # 解析日期
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    async with engine.begin() as conn:
        result = await AdminLogService.list_logs(
            conn,
            admin_id,
            operation_type,
            operation_module,
            start_dt,
            end_dt,
            page,
            page_size
        )
    
    return success_response(result)


@router.get("/{log_id}")
async def get_log(
    log_id: int,
    admin_info: dict = Depends(require_admin)
):
    """获取日志详情"""
    async with engine.begin() as conn:
        log = await AdminLogService.get_log(conn, log_id)
    
    return success_response(log)
