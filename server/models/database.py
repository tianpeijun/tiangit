"""
数据库表定义 - SQLAlchemy Core
"""
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Text, Boolean, 
    DateTime, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.asyncio import create_async_engine
from datetime import datetime
import os

# 数据库连接配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///data/awsome_shop.db"
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# 元数据对象
metadata = MetaData()

# 1. 用户表（users）
users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(50), unique=True, nullable=False),
    Column('password_hash', String(255), nullable=False),
    Column('real_name', String(100), nullable=False),
    Column('employee_id', String(50), unique=True, nullable=False),
    Column('department', String(100), nullable=False),
    Column('position', String(100), nullable=True),
    Column('role', String(20), nullable=False),  # employee/admin
    Column('points', Integer, nullable=False, default=1000),
    Column('is_active', Boolean, nullable=False, default=True),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    Column('updated_at', DateTime, nullable=False, default=datetime.now, onupdate=datetime.now),
    Column('last_login_at', DateTime, nullable=True),
    
    Index('idx_username', 'username'),
    Index('idx_employee_id', 'employee_id'),
    Index('idx_role', 'role'),
)

# 2. 收货地址表（addresses）
addresses = Table(
    'addresses',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('address', String(500), nullable=False),
    Column('phone', String(20), nullable=False),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    Column('updated_at', DateTime, nullable=False, default=datetime.now, onupdate=datetime.now),
    
    Index('idx_addresses_user_id', 'user_id'),
)

# 3. 产品分类表（categories）
categories = Table(
    'categories',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(100), nullable=False),
    Column('parent_id', Integer, ForeignKey('categories.id'), nullable=True),
    Column('sort_order', Integer, nullable=False, default=0),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    Column('updated_at', DateTime, nullable=False, default=datetime.now, onupdate=datetime.now),
    
    Index('idx_parent_id', 'parent_id'),
)

# 4. 产品表（products）
products = Table(
    'products',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(200), nullable=False),
    Column('description', Text, nullable=True),
    Column('points_required', Integer, nullable=False),
    Column('status', String(20), nullable=False),  # active/inactive
    Column('is_deleted', Boolean, nullable=False, default=False),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    Column('updated_at', DateTime, nullable=False, default=datetime.now, onupdate=datetime.now),
    
    Index('idx_name', 'name'),
    Index('idx_status', 'status'),
    Index('idx_is_deleted', 'is_deleted'),
    Index('idx_points_required', 'points_required'),
)

# 5. 产品图片表（product_images）
product_images = Table(
    'product_images',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
    Column('original_filename', String(255), nullable=False),
    Column('stored_filename', String(255), nullable=False),
    Column('thumbnail_filename', String(255), nullable=False),
    Column('file_path', String(500), nullable=False),
    Column('file_size', Integer, nullable=False),
    Column('sort_order', Integer, nullable=False, default=0),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    
    Index('idx_product_images_product_id', 'product_id'),
)

# 6. 产品分类关联表（product_categories）
product_categories = Table(
    'product_categories',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
    Column('category_id', Integer, ForeignKey('categories.id'), nullable=False),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    
    Index('idx_product_categories_product_id', 'product_id'),
    Index('idx_product_categories_category_id', 'category_id'),
    UniqueConstraint('product_id', 'category_id', name='unique_product_category'),
)

# 7. 购物车表（carts）
carts = Table(
    'carts',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
    Column('quantity', Integer, nullable=False, default=1),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    Column('updated_at', DateTime, nullable=False, default=datetime.now, onupdate=datetime.now),
    
    Index('idx_carts_user_id', 'user_id'),
    UniqueConstraint('user_id', 'product_id', name='unique_user_product'),
    CheckConstraint('quantity > 0', name='check_quantity_positive'),
)

# 8. 订单表（orders）
orders = Table(
    'orders',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('order_no', String(50), unique=True, nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('total_points', Integer, nullable=False),
    Column('status', String(20), nullable=False),  # completed
    Column('shipping_address', String(500), nullable=False),
    Column('shipping_phone', String(20), nullable=False),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    
    Index('idx_orders_order_no', 'order_no'),
    Index('idx_orders_user_id', 'user_id'),
    Index('idx_orders_created_at', 'created_at'),
)

# 9. 订单明细表（order_items）
order_items = Table(
    'order_items',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('order_id', Integer, ForeignKey('orders.id'), nullable=False),
    Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
    Column('product_name', String(200), nullable=False),
    Column('quantity', Integer, nullable=False),
    Column('points_per_item', Integer, nullable=False),
    Column('subtotal_points', Integer, nullable=False),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    
    Index('idx_order_items_order_id', 'order_id'),
    Index('idx_order_items_product_id', 'product_id'),
)

# 10. 积分交易表（point_transactions）
point_transactions = Table(
    'point_transactions',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('transaction_type', String(20), nullable=False),  # grant/consume
    Column('amount', Integer, nullable=False),
    Column('balance_after', Integer, nullable=False),
    Column('order_id', Integer, ForeignKey('orders.id'), nullable=True),
    Column('admin_id', Integer, ForeignKey('users.id'), nullable=True),
    Column('description', String(500), nullable=True),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    
    Index('idx_point_transactions_user_id', 'user_id'),
    Index('idx_point_transactions_transaction_type', 'transaction_type'),
    Index('idx_point_transactions_created_at', 'created_at'),
)

# 11. Session 表（sessions）
sessions = Table(
    'sessions',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('session_id', String(255), unique=True, nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('data', Text, nullable=True),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    Column('expires_at', DateTime, nullable=False),
    
    Index('idx_sessions_session_id', 'session_id'),
    Index('idx_sessions_user_id', 'user_id'),
    Index('idx_sessions_expires_at', 'expires_at'),
)

# 12. 操作日志表（admin_logs）
admin_logs = Table(
    'admin_logs',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('admin_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('operation_type', String(50), nullable=False),
    Column('operation_module', String(50), nullable=False),
    Column('operation_desc', String(500), nullable=False),
    Column('data_before', Text, nullable=True),
    Column('data_after', Text, nullable=True),
    Column('ip_address', String(50), nullable=True),
    Column('created_at', DateTime, nullable=False, default=datetime.now),
    
    Index('idx_admin_logs_admin_id', 'admin_id'),
    Index('idx_admin_logs_operation_type', 'operation_type'),
    Index('idx_admin_logs_created_at', 'created_at'),
)
