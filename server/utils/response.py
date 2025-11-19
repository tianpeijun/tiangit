"""
统一响应格式工具
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def error_response(code: int, message: str, data: Any = None) -> JSONResponse:
    """错误响应"""
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )


def paginated_response(items: list, total: int, page: int, page_size: int) -> dict:
    """分页响应"""
    total_pages = (total + page_size - 1) // page_size
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


class BusinessException(Exception):
    """业务异常"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class AuthenticationException(BusinessException):
    """认证异常"""
    def __init__(self, message: str = "未认证"):
        super().__init__(401, message)


class PermissionException(BusinessException):
    """权限异常"""
    def __init__(self, message: str = "无权限"):
        super().__init__(403, message)


class NotFoundException(BusinessException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(404, message)


class ValidationException(BusinessException):
    """验证异常"""
    def __init__(self, message: str):
        super().__init__(400, message)
