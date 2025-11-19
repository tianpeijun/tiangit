"""
操作日志服务层
"""
from sqlalchemy.ext.asyncio import AsyncConnection
from datetime import datetime
from typing import Optional
import json

from repositories.admin_log_repository import AdminLogRepository
from utils.response import NotFoundException


class AdminLogService:
    """操作日志服务"""
    
    @staticmethod
    async def log_operation(
        conn: AsyncConnection,
        admin_id: int,
        operation_type: str,
        operation_module: str,
        operation_desc: str,
        data_before: Optional[dict] = None,
        data_after: Optional[dict] = None,
        ip_address: Optional[str] = None
    ) -> int:
        """记录操作日志"""
        log_data = {
            'admin_id': admin_id,
            'operation_type': operation_type,
            'operation_module': operation_module,
            'operation_desc': operation_desc,
            'data_before': json.dumps(data_before, ensure_ascii=False) if data_before else None,
            'data_after': json.dumps(data_after, ensure_ascii=False) if data_after else None,
            'ip_address': ip_address,
            'created_at': datetime.now()
        }
        
        return await AdminLogRepository.create_log(conn, log_data)
    
    @staticmethod
    async def get_log(conn: AsyncConnection, log_id: int) -> dict:
        """获取日志详情"""
        log = await AdminLogRepository.get_log_by_id(conn, log_id)
        if not log:
            raise NotFoundException("日志不存在")
        
        # 格式化日期
        if log.get('created_at'):
            log['created_at'] = log['created_at'].isoformat()
        
        # 解析JSON数据
        if log.get('data_before'):
            try:
                log['data_before'] = json.loads(log['data_before'])
            except:
                pass
        
        if log.get('data_after'):
            try:
                log['data_after'] = json.loads(log['data_after'])
            except:
                pass
        
        return log
    
    @staticmethod
    async def list_logs(
        conn: AsyncConnection,
        admin_id: Optional[int] = None,
        operation_type: Optional[str] = None,
        operation_module: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取操作日志列表"""
        items, total = await AdminLogRepository.list_logs(
            conn, admin_id, operation_type, operation_module,
            start_date, end_date, page, page_size
        )
        
        # 格式化日期
        for item in items:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            
            # 不在列表中返回详细数据快照，只返回是否有数据
            if item.get('data_before'):
                item['has_data_before'] = True
                item.pop('data_before')
            else:
                item['has_data_before'] = False
            
            if item.get('data_after'):
                item['has_data_after'] = True
                item.pop('data_after')
            else:
                item['has_data_after'] = False
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
