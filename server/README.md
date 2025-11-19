# AWSomeShop 后端服务

## 概述

AWSomeShop 后端服务基于 FastAPI 和 SQLAlchemy Core 构建，提供员工福利电商平台的所有 API 接口。

## 技术栈

- **Python**: 3.8+
- **Web 框架**: FastAPI 0.109.0
- **数据库**: SQLite 3
- **ORM**: SQLAlchemy Core 2.0.25 (非 ORM 模式)
- **异步驱动**: aiosqlite 0.19.0
- **密码哈希**: bcrypt 4.1.2
- **图片处理**: Pillow 10.2.0
- **频率限制**: slowapi 0.1.9

## 项目结构

```
server/
├── models/
│   └── database.py          # 数据库表定义
├── utils/
│   └── password.py          # 密码工具函数
├── init_db.py               # 数据库初始化脚本
├── verify_db.py             # 数据库验证脚本
└── README.md                # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python server/init_db.py
```

这将创建:
- 12 个数据库表
- 1 个管理员账户
- 20 个测试员工账户
- 5 个一级产品分类
- 22 个二级产品分类
- 100 个 3C 电子产品
- 200 张产品图片 (每个产品 1-3 张)

### 3. 验证数据库

```bash
python server/verify_db.py
```

## 默认账户

### 管理员账户
- **用户名**: `admin`
- **密码**: `admin123`
- **工号**: `ADMIN001`
- **初始积分**: 0

### 测试员工账户
- **用户名**: `employee001` - `employee020`
- **密码**: `test123`
- **工号**: `EMP0001` - `EMP0020`
- **初始积分**: 1000

## 数据库设计

### 核心表 (12个)

1. **users** - 用户表 (员工和管理员)
2. **addresses** - 收货地址表
3. **categories** - 产品分类表 (支持二级分类)
4. **products** - 产品表
5. **product_images** - 产品图片表
6. **product_categories** - 产品分类关联表
7. **carts** - 购物车表
8. **orders** - 订单表
9. **order_items** - 订单明细表
10. **point_transactions** - 积分交易表
11. **sessions** - Session 表
12. **admin_logs** - 操作日志表

详细的数据库设计文档请参考: [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md)

### 数据库关系

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

### 产品分类体系

**一级分类 (5个)**:
1. 手机通讯
2. 电脑办公
3. 数码配件
4. 智能设备
5. 影音娱乐

**二级分类 (22个)**:
- 手机通讯: 智能手机、功能手机、手机配件、运营商
- 电脑办公: 笔记本电脑、台式机、平板电脑、显示器、键鼠
- 数码配件: 移动电源、数据线、充电器、保护壳、耳机
- 智能设备: 智能手表、智能手环、智能音箱、智能家居
- 影音娱乐: 耳机音箱、相机摄像、游戏设备、影音配件

### 测试产品 (100个)

产品分布:
- 手机通讯类: 20个产品
- 电脑办公类: 25个产品
- 数码配件类: 30个产品
- 智能设备类: 15个产品
- 影音娱乐类: 10个产品

积分范围:
- 低价位: 0-500 积分 (数据线、充电器、保护壳等)
- 中价位: 500-3000 积分 (移动电源、耳机、智能手环等)
- 高价位: 3000-30000 积分 (手机、电脑、平板、智能手表等)

### 产品图片

- 每个产品: 1-3 张图片
- 原图尺寸: 800x800
- 缩略图尺寸: 320x320
- 存储路径: `static/images/{YYYYMMDD}/init/{product_id}/`
- 文件命名: `{uuid}.jpg` (原图), `{uuid}_thumb.jpg` (缩略图)

## 密码策略

- **长度**: 6-8 位
- **要求**: 必须包含数字和字母
- **哈希算法**: bcrypt (cost factor: 12)

## 数据库文件位置

- **开发环境**: `data/awsome_shop.db`
- **生产环境**: `/mnt/data/awsome_shop.db` (AWS EBS)

## 图片存储位置

- **开发环境**: `static/images/`
- **生产环境**: `/mnt/data/images/`

## 常用命令

### 查看数据库表

```bash
sqlite3 data/awsome_shop.db ".tables"
```

### 查看用户数据

```bash
sqlite3 data/awsome_shop.db "SELECT username, role, points FROM users LIMIT 10;"
```

### 查看产品数据

```bash
sqlite3 data/awsome_shop.db "SELECT name, points_required, status FROM products LIMIT 10;"
```

### 查看分类数据

```bash
sqlite3 data/awsome_shop.db "SELECT name, parent_id FROM categories;"
```

### 检查外键完整性

```bash
sqlite3 data/awsome_shop.db "PRAGMA foreign_key_check;"
```

### 查看数据库大小

```bash
ls -lh data/awsome_shop.db
```

## 数据验证

运行验证脚本检查数据完整性:

```bash
python server/verify_db.py
```

验证内容包括:
- ✓ 用户数量 (1 管理员 + 20 员工)
- ✓ 分类数量 (5 一级 + 22 二级)
- ✓ 产品数量 (100 个)
- ✓ 图片数量 (200 张)
- ✓ 产品分类关联 (100 个)
- ✓ 积分总额 (20000)
- ✓ 数据完整性 (所有产品都有图片和分类)

## 重新初始化数据库

如果需要重新初始化数据库:

```bash
# 删除现有数据库
rm -f data/awsome_shop.db

# 删除现有图片
rm -rf static/images/*

# 重新初始化
python server/init_db.py
```

## 性能优化

### 索引策略

所有外键字段和常用查询字段都创建了索引:
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

## 备份和恢复

### 备份数据库

```bash
# 备份数据库文件
cp data/awsome_shop.db data/awsome_shop_backup_$(date +%Y%m%d).db

# 备份图片文件
tar -czf images_backup_$(date +%Y%m%d).tar.gz static/images/
```

### 恢复数据库

```bash
# 恢复数据库文件
cp data/awsome_shop_backup_YYYYMMDD.db data/awsome_shop.db

# 恢复图片文件
tar -xzf images_backup_YYYYMMDD.tar.gz
```

## 故障排查

### 数据库文件无法打开

```bash
# 检查文件权限
ls -l data/awsome_shop.db

# 检查目录是否存在
mkdir -p data
```

### 图片无法显示

```bash
# 检查图片目录
ls -la static/images/

# 检查图片文件
ls -la static/images/20251119/init/1/
```

### 外键约束错误

```bash
# 检查外键完整性
sqlite3 data/awsome_shop.db "PRAGMA foreign_key_check;"
```

## 安全注意事项

1. **密码存储**: 使用 bcrypt 哈希，不存储明文密码
2. **SQL 注入**: 使用 SQLAlchemy 参数化查询
3. **数据库权限**: 生产环境数据库文件权限设置为 600
4. **敏感数据**: 操作日志中的敏感数据需要脱敏

## 下一步

完成数据库初始化后，可以继续:
1. 实现 API 接口 (Task 2)
2. 开发前端应用 (Task 3)
3. 集成测试 (Task 4)
4. 部署到 AWS (Task 5)

## 参考文档

- [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md) - 详细的数据库设计文档
- [requirements.md](../.kiro/specs/awsome-shop/requirements.md) - 需求文档
- [design.md](../.kiro/specs/awsome-shop/design.md) - 设计文档
- [tasks.md](../.kiro/specs/awsome-shop/tasks.md) - 任务列表
