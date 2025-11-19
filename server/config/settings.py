"""
应用配置文件
"""
import os
from pathlib import Path

class Settings:
    # 项目路径
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # 数据库配置
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///data/awsome_shop.db"
    )
    
    # 文件存储配置
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "static/images"))
    STATIC_URL = "/static/images"
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    TOTAL_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
    THUMBNAIL_SIZE = (320, 320)
    
    # Session 配置
    SESSION_SECRET_KEY = os.getenv(
        "SESSION_SECRET_KEY",
        "awsome-shop-secret-key-change-in-production"
    )
    SESSION_EXPIRE_SECONDS = 3600  # 1小时
    
    # CSRF 配置
    CSRF_SECRET_KEY = os.getenv(
        "CSRF_SECRET_KEY",
        "awsome-shop-csrf-key-change-in-production"
    )
    
    # 密码配置
    PASSWORD_MIN_LENGTH = 6
    PASSWORD_MAX_LENGTH = 8
    BCRYPT_ROUNDS = 12
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 购物车配置
    MAX_CART_ITEMS = 100
    
    # 频率限制配置
    RATE_LIMIT_LOGIN = "10/second"
    RATE_LIMIT_EXCHANGE = "10/second"
    RATE_LIMIT_SEARCH = "10/second"
    
    # 日志配置
    LOG_DIR = BASE_DIR / "logs"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # 应用配置
    APP_NAME = "AWSomeShop"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS 配置
    CORS_ORIGINS = [
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
    ]

settings = Settings()
