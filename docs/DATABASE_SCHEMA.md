# AWSomeShop 数据库设计文档

## 概述

本文档描述了 AWSomeShop 系统的数据库架构设计。系统使用 SQLite 数据库，包含 12 个核心表，支持用户管理、产品管理、订单处理、积分系统和操作审计等功能。

## 技术栈

- **数据库**: SQLite 3
- **ORM**: SQLAlchemy Core (非 ORM 模式)
- **异步驱动**: aiosqlite
- **数据库文件**: `data/awsome_shop.db`

## 数据库表结构

### 1. 用户表 (users)

存储系统用户信息，包括员工和管理员。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 (bcrypt) |
| real_name | VARCHAR(100) | NOT NULL | 真实姓名 |
| employee_id | VARCHAR(50) | UNIQUE, NOT NULL | 工号 |
| department | VARCHAR(100) | NOT NULL | 部门 |
| position | VARCHAR(100) | NULL | 职位 |
| role | VARCHAR(20) | NOT NULL | 角色 (employee/admin) |
| points | INTEGER | NOT NULL, DEFAULT 1000 | 积分余额 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 账户状态 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |
| last_login_at | DATETIME | NULL | 最后登录时间 |

**索引**:
- `idx_username` ON username
- `idx_employee_id` ON employee_id
- `idx_role` ON role

### 2. 收货地址表 (addresses)

存储用户的收货地址信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 地址ID |
| user_id | INTEGER | FOREIGN KEY(users.id), NOT NULL | 用户ID |
| address | VARCHAR(500) | NOT NULL | 收货地址 |
| phone | VARCHAR(20) | NOT NULL | 联系电话 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引**:
- `idx_user_id` ON user_id

### 3. 产品分类表 (categories)

存储产品分类信息，支持二级分类。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 分类ID |
| name | VARCHAR(100) | NOT NULL | 分类名称 |
| parent_id | INTEGER | FOREIGN KEY(categories.id), NULL | 父分类ID (NULL表示一级分类) |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 | 排序顺序 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引**:
- `idx_parent_id` ON parent_id

### 4. 产品表 (products)

存储产品基本信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 产品ID |
| name | VARCHAR(200) | NOT NULL | 产品名称 |
| description | TEXT | NULL | 产品描述 |
| points_required | INTEGER | NOT NULL | 所需积分 |
| status | VARCHAR(20) | NOT NULL | 状态 (active/inactive) |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | 软删除标记 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引**:
- `idx_name` ON name
- `idx_status` ON status
- `idx_is_deleted` ON is_deleted
- `idx_points_required` ON points_required

### 5. 产品图片表 (product_images)

存储产品图片的元数据。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 图片ID |
| product_id | INTEGER | FOREIGN KEY(products.id), NOT NULL | 产品ID |
| original_filename | VARCHAR(255) | NOT NULL | 原始文件名 |
| stored_filename | VARCHAR(255) | NOT NULL | 存储文件名 (UUID) |
| thumbnail_filename | VARCHAR(255) | NOT NULL | 缩略图文件名 |
| file_path | VARCHAR(500) | NOT NULL | 文件路径 |
| file_size | INTEGER | NOT NULL | 文件大小 (字节) |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 | 排序顺序 |
| created_at | DATETIME | NOT NULL | 创建时间 |

**索引**:
- `idx_product_id` ON product_id

### 6. 产品分类关联表 (product_categories)

多对多关系表，关联产品和分类。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 关联ID |
| product_id | INTEGER | FOREIGN KEY(products.id), NOT NULL | 产品ID |
| category_id | INTEGER | FOREIGN KEY(categories.id), NOT NULL | 分类ID |
| created_at | DATETIME | NOT NULL | 创建时间 |

**索引**:
- `idx_product_id` ON product_id
- `idx_category_id` ON category_id
- `unique_product_category` UNIQUE(product_id, category_id)

### 7. 购物车表 (carts)

存储用户购物车信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 购物车ID |
| user_id | INTEGER | FOREIGN KEY(users.id), NOT NULL | 用户ID |
| product_id | INTEGER | FOREIGN KEY(products.id), NOT NULL | 产品ID |
| quantity | INTEGER | NOT NULL, DEFAULT 1 | 数量 |
| created_at | DATETIME | NOT NULL | 添加时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引**:
- `idx_user_id` ON user_id
- `unique_user_product` UNIQUE(user_id, product_id)

**约束**:
- `check_quantity_positive`: quantity > 0
- 每个用户购物车总商品数量 ≤ 100

### 8. 订单表 (orders)

存储订单主表信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 订单ID |
| order_no | VARCHAR(50) | UNIQUE, NOT NULL | 订单号 |
| user_id | INTEGER | FOREIGN KEY(users.id), NOT NULL | 用户ID |
| total_points | INTEGER | NOT NULL | 总消耗积分 |
| status | VARCHAR(20) | NOT NULL | 订单状态 (completed) |
| shipping_address | VARCHAR(500) | NOT NULL | 收货地址快照 |
| shipping_phone | VARCHAR(20) | NOT NULL | 联系电话快照 |
| created_at | DATETIME | NOT NULL | 创建时间 |

**索引**:
- `idx_order_no` ON order_no
- `idx_user_id` ON user_id
- `idx_created_at` ON created_at

### 9. 订单明细表 (order_items)

存储订单商品明细。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 明细ID |
| order_id | INTEGER | FOREIGN KEY(orders.id), NOT NULL | 订单ID |
| product_id | INTEGER | FOREIGN KEY(products.id), NOT NULL | 产品ID |
| product_name | VARCHAR(200) | NOT NULL | 产品名称快照 |
| quantity | INTEGER | NOT NULL | 数量 |
| points_per_item | INTEGER | NOT NULL | 单价积分 |
| subtotal_points | INTEGER | NOT NULL | 小计积分 |
| created_at | DATETIME | NOT NULL | 创建时间 |

**索引**:
- `idx_order_id` ON order_id
- `idx_product_id` ON product_id

### 10. 积分交易表 (point_transactions)

记录所有积分变动历史。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 交易ID |
| user_id | INTEGER | FOREIGN KEY(users.id), NOT NULL | 用户ID |
| transaction_type | VARCHAR(20) | NOT NULL | 交易类型 (grant/consume) |
| amount | INTEGER | NOT NULL | 积分数量 |
| balance_after | INTEGER | NOT NULL | 交易后余额 |
| order_id | INTEGER | FOREIGN KEY(orders.id), NULL | 关联订单ID (消费时) |
| admin_id | INTEGER | FOREIGN KEY(users.id), NULL | 操作管理员ID (发放时) |
| description | VARCHAR(500) | NULL | 描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |

**索引**:
- `idx_user_id` ON user_id
- `idx_transaction_type` ON transaction_type
- `idx_created_at` ON created_at

### 11. Session 表 (sessions)

存储用户会话信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Session ID |
| session_id | VARCHAR(255) | UNIQUE, NOT NULL | Session 标识 (UUID) |
| user_id | INTEGER | FOREIGN KEY(users.id), NOT NULL | 用户ID |
| data | TEXT | NULL | Session 数据 (JSON) |
| created_at | DATETIME | NOT NULL | 创建时间 |
| expires_at | DATETIME | NOT NULL | 过期时间 |

**索引**:
- `idx_session_id` ON session_id
- `idx_user_id` ON user_id
- `idx_expires_at` ON expires_at

### 12. 操作日志表 (admin_logs)

记录管理员操作日志。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 日志ID |
| admin_id | INTEGER | FOREIGN KEY(users.id), NOT NULL | 管理员ID |
| operation_type | VARCHAR(50) | NOT NULL | 操作类型 |
| operation_module | VARCHAR(50) | NOT NULL | 操作模块 |
| operation_desc | VARCHAR(500) | NOT NULL | 操作描述 |
| data_before | TEXT | NULL | 操作前数据快照 (JSON) |
| data_after | TEXT | NULL | 操作后数据快照 (JSON) |
| ip_address | VARCHAR(50) | NULL | IP 地址 |
| created_at | DATETIME | NOT NULL | 操作时间 |

**索引**:
- `idx_admin_id` ON admin_id
- `idx_operation_type` ON operation_type
- `idx_created_at` ON created_at

## 数据库关系图

```
users (1) ─────── (N) addresses
  │
  ├─── (N) carts ─────── (1) products
  │
  ├─── (N) orders
  │         │
  │         └─── (N) order_items ─────── (1) products
  │
  ├─── (N) point_transactions
  │
  └─── (N) sessions

products (1) ─────── (N) product_images
  │
  └─── (N) product_categories ─────── (1) categories
                                            │
                                            └─── (N) categories (self-reference)

users (admin) (1) ─────── (N) admin_logs
```

## 初始化数据

### 默认账户

**管理员账户**:
- 用户名: `admin`
- 密码: `admin123`
- 工号: `ADMIN001`
- 部门: 技术部
- 初始积分: 0

**测试员工账户** (20个):
- 用户名: `employee001` - `employee020`
- 密码: `test123`
- 工号: `EMP0001` - `EMP0020`
- 部门: 技术部、市场部、销售部、人力资源部、财务部 (轮流分配)
- 初始积分: 1000

### 产品分类

**一级分类** (5个):
1. 手机通讯
2. 电脑办公
3. 数码配件
4. 智能设备
5. 影音娱乐

**二级分类** (20个):
- 手机通讯: 智能手机、功能手机、手机配件、运营商
- 电脑办公: 笔记本电脑、台式机、平板电脑、显示器、键鼠
- 数码配件: 移动电源、数据线、充电器、保护壳、耳机
- 智能设备: 智能手表、智能手环、智能音箱、智能家居
- 影音娱乐: 耳机音箱、相机摄像、游戏设备、影音配件

### 测试产品

系统初始化时会创建 100 个 3C 电子产品，分布如下:
- 手机通讯类: 20个产品
- 电脑办公类: 25个产品
- 数码配件类: 30个产品
- 智能设备类: 15个产品
- 影音娱乐类: 10个产品

每个产品包含:
- 产品名称、描述、所需积分
- 1-3 张产品图片 (原图 800x800, 缩略图 320x320)
- 关联的产品分类

## 使用说明

### 初始化数据库

```bash
# 安装依赖
pip install -r requirements.txt

# 运行初始化脚本
python server/init_db.py
```

### 数据库文件位置

- 开发环境: `data/awsome_shop.db`
- 生产环境: `/mnt/data/awsome_shop.db` (AWS EBS)

### 图片存储

- 开发环境: `static/images/`
- 生产环境: `/mnt/data/images/`

图片目录结构:
```
static/images/
└── YYYYMMDD/
    └── init/
        └── {product_id}/
            ├── {uuid}.jpg (原图)
            └── {uuid}_thumb.jpg (缩略图)
```

## 性能优化

### 索引策略

所有外键字段都创建了索引，以优化关联查询性能:
- 用户相关: username, employee_id, role
- 产品相关: name, status, is_deleted, points_required
- 订单相关: order_no, user_id, created_at
- 积分相关: user_id, transaction_type, created_at
- Session相关: session_id, user_id, expires_at

### 查询优化建议

1. **产品列表查询**: 使用 status 和 is_deleted 索引过滤
2. **订单历史查询**: 使用 user_id 和 created_at 复合索引
3. **积分明细查询**: 使用 user_id 和 created_at 复合索引
4. **Session 清理**: 使用 expires_at 索引定期清理过期会话

## 数据完整性

### 外键约束

所有表间关系都使用外键约束，确保数据完整性:
- 级联删除: 不使用 (保留历史数据)
- 引用完整性: 所有外键都必须引用有效记录

### 业务约束

1. **购物车**: 数量必须 > 0
2. **用户**: 用户名和工号必须唯一
3. **产品分类**: 产品和分类的关联必须唯一
4. **订单**: 订单号必须唯一

### 软删除

产品表使用软删除机制 (is_deleted 字段)，保留历史订单中的产品引用。

## 备份策略

### 开发环境

```bash
# 备份数据库
cp data/awsome_shop.db data/awsome_shop_backup_$(date +%Y%m%d).db

# 备份图片
tar -czf images_backup_$(date +%Y%m%d).tar.gz static/images/
```

### 生产环境

使用 AWS EBS 快照功能进行自动备份:
- 每日快照
- 保留 7 天
- 跨可用区复制

## 维护任务

### 定期清理

1. **过期 Session**: 每小时清理一次
```sql
DELETE FROM sessions WHERE expires_at < datetime('now');
```

2. **操作日志归档**: 每月归档一次 (保留最近 3 个月)

### 性能监控

监控以下指标:
- 数据库文件大小
- 查询响应时间
- 索引使用率
- 锁等待时间

## 安全考虑

1. **密码存储**: 使用 bcrypt 哈希 (cost factor: 12)
2. **SQL 注入**: 使用 SQLAlchemy 参数化查询
3. **数据快照**: 操作日志中的敏感数据需要脱敏
4. **访问控制**: 数据库文件权限设置为 600

## 版本历史

- v1.0.0 (2024-01-01): 初始版本，包含 12 个核心表
