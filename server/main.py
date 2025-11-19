"""
FastAPI 应用入口
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time

from config.settings import settings
from utils.response import BusinessException, error_response
from controllers import (
    auth_controller,
    user_controller,
    category_controller,
    product_controller,
    cart_controller,
    order_controller,
    point_controller,
    admin_log_controller,
    personal_controller
)

# 创建日志目录
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            settings.LOG_DIR / 'app.log',
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置频率限制
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有 API 请求"""
    start_time = time.time()
    
    # 记录请求
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # 记录响应
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        raise


# 全局异常处理
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理"""
    logger.warning(f"Business exception: {exc.message}")
    return error_response(exc.code, exc.message)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return error_response(500, "服务器内部错误")


# 注册路由
app.include_router(auth_controller.router, prefix="/api/auth", tags=["认证"])
app.include_router(user_controller.router, prefix="/api/manage/users", tags=["用户管理"])
app.include_router(category_controller.router, prefix="/api/manage/categories", tags=["分类管理"])
app.include_router(category_controller.employee_router, prefix="/api/personal/categories", tags=["分类（员工端）"])
app.include_router(product_controller.router, tags=["产品管理"])
app.include_router(cart_controller.router, prefix="/api/personal/cart", tags=["购物车"])
app.include_router(order_controller.router, tags=["订单管理"])
app.include_router(point_controller.router, tags=["积分管理"])
app.include_router(admin_log_controller.router, prefix="/api/manage/logs", tags=["操作日志"])
app.include_router(personal_controller.router, tags=["个人中心"])

# 挂载静态文件
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": settings.APP_VERSION}


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "AWSomeShop API is running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
