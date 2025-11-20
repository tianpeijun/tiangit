# Awsome Shop 项目总结

## 项目概述

Awsome Shop 是一个完整的电商系统，包含管理端和员工端两个前端应用，以及一个 FastAPI 后端服务。系统部署在 AWS 上，使用现代化的云原生架构。

## 技术栈

### 前端
- **框架**: Vue.js 2.x
- **UI 组件**: Element UI
- **状态管理**: Vuex
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **构建工具**: Vue CLI

### 后端
- **框架**: FastAPI (Python 3.9+)
- **数据库**: PostgreSQL (AWS RDS)
- **ORM**: 原生 SQL (使用 psycopg2)
- **认证**: JWT (JSON Web Tokens)
- **CORS**: FastAPI CORS Middleware

### 基础设施
- **IaC**: AWS CDK (TypeScript)
- **计算**: EC2 (后端)
- **存储**: S3 (前端静态文件)
- **CDN**: CloudFront
- **负载均衡**: Application Load Balancer (ALB)
- **数据库**: RDS PostgreSQL
- **网络**: VPC, Subnets, Security Groups

## 系统架构

```
┌─────────────┐         ┌──────────────┐
│  CloudFront │────────▶│  S3 Bucket   │
│  (管理端)    │         │  (管理端静态)  │
└─────────────┘         └──────────────┘

┌─────────────┐         ┌──────────────┐
│  CloudFront │────────▶│  S3 Bucket   │
│  (员工端)    │         │  (员工端静态)  │
└─────────────┘         └──────────────┘
       │
       │ API 请求
       ▼
┌─────────────┐         ┌──────────────┐
│     ALB     │────────▶│     EC2      │
│             │         │  (FastAPI)   │
└─────────────┘         └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   SQLlite    │
                        └──────────────┘
```

## 核心功能

### 管理端 (Manage)
- 用户管理
- 产品管理（CRUD）
- 订单管理
- 库存管理
- 数据统计和报表

### 员工端 (Personal)
- 产品浏览
- 购物车
- 订单创建和查看
- 个人信息管理
- 积分系统

### 后端 API
- RESTful API 设计
- JWT 认证和授权
- 角色权限控制
- 文件上传（产品图片）
- 数据验证和错误处理

## 部署流程

### 1. 基础设施部署
使用 AWS CDK 部署所有 AWS 资源：
- VPC 和网络配置
- RDS PostgreSQL 数据库
- EC2 实例
- ALB 负载均衡器
- S3 存储桶
- CloudFront 分发

### 2. 后端部署
使用 AWS Systems Manager Session Manager 部署后端代码到 EC2：
- 上传代码到 S3
- 通过 SSM 在 EC2 上执行部署脚本
- 安装依赖
- 配置 systemd 服务
- 启动 FastAPI 应用

### 3. 前端部署
构建前端应用并部署到 S3/CloudFront：
- 本地构建 Vue.js 应用
- 上传静态文件到 S3
- 清除 CloudFront 缓存

## 关键配置

### 环境变量

**后端 (server/config/settings.py)**:
- `DATABASE_URL`: SQL 连接字符串
- `SECRET_KEY`: JWT 签名密钥
- `UPLOAD_DIR`: 文件上传目录

**前端 (.env.production)**:
- `VUE_APP_API_BASE_URL`: 后端 API 地址 (ALB URL)

### CORS 配置
后端配置允许来自 CloudFront 的跨域请求：
```python
allow_origins=["*"]  # 生产环境应限制为具体域名
```

### 图片处理
- 产品图片存储在 EC2 的 `/opt/awsome-shop/static/images/` 目录
- 通过 ALB 提供静态文件服务
- 前端使用 `getImageUrl` 函数自动拼接完整 URL

## 数据库设计

主要表结构：
- `users`: 用户信息
- `products`: 产品信息
- `product_images`: 产品图片
- `orders`: 订单
- `order_items`: 订单明细
- `cart_items`: 购物车
- `addresses`: 收货地址
- `point_transactions`: 积分交易记录

详见 `docs/DATABASE_SCHEMA.md`

## API 设计

遵循 RESTful 设计原则：
- `GET /api/products/`: 获取产品列表
- `POST /api/products/`: 创建产品
- `PUT /api/products/{id}`: 更新产品
- `DELETE /api/products/{id}`: 删除产品
- `POST /api/auth/login`: 用户登录
- `POST /api/orders/`: 创建订单

完整 API 规格见 `docs/api-spec.yaml`

## 安全考虑

1. **认证**: 使用 JWT token 进行用户认证
2. **授权**: 基于角色的访问控制 (RBAC)
3. **密码**: 使用 bcrypt 加密存储
4. **HTTPS**: 生产环境应启用 HTTPS
5. **SQL 注入**: 使用参数化查询防止 SQL 注入
6. **XSS**: 前端对用户输入进行转义

## 性能优化

1. **CDN**: 使用 CloudFront 加速静态资源
2. **缓存**: 浏览器缓存和 CDN 缓存
3. **图片优化**: 生成缩略图减少加载时间
4. **数据库索引**: 在常用查询字段上建立索引
5. **连接池**: 数据库连接池管理

## 监控和日志

- **应用日志**: FastAPI 日志输出到 stdout
- **系统日志**: systemd journal
- **AWS 监控**: CloudWatch (待配置)
- **错误追踪**: 前端 console.error，后端异常日志

## 未来改进

1. **CI/CD**: 设置自动化部署流程
2. **测试**: 增加单元测试和集成测试覆盖率
3. **监控**: 配置 CloudWatch 告警
4. **备份**: 自动化数据库备份
5. **HTTPS**: 配置 SSL/TLS 证书
6. **性能**: 添加 Redis 缓存层
7. **搜索**: 集成 Elasticsearch 提升搜索性能
8. **支付**: 集成支付网关

## 维护指南

### 日常维护
- 定期检查应用日志
- 监控数据库性能
- 更新依赖包
- 备份数据库

### 故障排查
1. 检查 EC2 实例状态
2. 查看应用日志: `journalctl -u awsome-shop -f`
3. 检查数据库连接
4. 验证 ALB 健康检查
5. 清除 CloudFront 缓存

### 扩展
- **水平扩展**: 增加 EC2 实例，配置 Auto Scaling
- **垂直扩展**: 升级 EC2 实例类型
- **数据库**: 使用 RDS 读副本分离读写

## 联系方式

项目维护者: [Your Name]
文档更新日期: 2025-11-20
