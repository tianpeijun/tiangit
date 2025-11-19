# AWSomeShop 实施任务列表

## 任务执行说明

本任务列表按照**企业级开发流程**组织，适合专业团队协作：

### 开发流程
```
1. 数据库设计 → 2. API 规范定义 → 3. 前后端并行开发 → 4. CDK 部署
```

### 团队角色
- **数据库工程师**：负责数据库设计和初始化
- **后端工程师**：负责所有后端 API 实现
- **前端工程师**：负责所有前端页面开发
- **DevOps 工程师**：负责 CDK 基础设施和部署

### 关键原则
- **API First**：前后端通过严格的 API 契约进行交互
- **并行开发**：API 定义完成后，前后端可以并行开发
- **Mock 数据**：前端可以使用 Mock 数据先行开发

## 任务列表

### Phase 1: 数据库设计和 API 规范

- [x] 1. 数据库：设计和初始化
  - 设计所有12个数据表结构（users, addresses, categories, products, product_images, product_categories, carts, orders, order_items, point_transactions, sessions, admin_logs）
  - 定义表字段、类型、约束、索引
  - 设计表关系和外键
  - 实现 database.py（SQLAlchemy Core 表定义）
  - 实现 init_db.py 数据库初始化脚本
  - 创建测试数据：1个管理员、20个员工、5个一级分类、20个二级分类、100个3C产品（含占位图）
  - 验证数据库完整性和性能
  - _需求: 16.1, 16.2, 9.1, 9.2, 12.1, 12.2, 数据初始化_
  - **负责人：数据库工程师**
  - **交付物：database.py, init_db.py, 数据库 schema 文档**

- [x] 2. API 规范：定义接口契约
  - 根据数据库 schema 定义所有 API 接口（60+ 个接口）
  - 定义请求/响应格式（JSON Schema）
  - 定义认证方式（Session-based）
  - 定义错误码和错误响应格式
  - 定义分页、排序、筛选参数规范
  - 创建 API 文档（OpenAPI/Swagger 格式）
  - 定义 API 接口清单：
    - 认证接口（4个）：登录、登出、获取当前用户、修改密码
    - 员工端产品接口（4个）：产品列表、产品详情、搜索、分类树
    - 员工端购物车接口（5个）：获取、添加、更新、删除、清空
    - 员工端订单接口（3个）：创建、列表、详情
    - 员工端积分接口（2个）：余额、明细
    - 员工端个人中心接口（3个）：个人信息、收货地址获取、收货地址更新
    - 管理端用户管理接口（7个）：列表、详情、创建、更新、删除、状态切换、重置密码
    - 管理端产品管理接口（8个）：列表、详情、创建、更新、删除、状态切换、上传图片、删除图片
    - 管理端分类管理接口（5个）：列表、详情、创建、更新、删除
    - 管理端积分管理接口（2个）：单个发放、批量发放
    - 管理端操作日志接口（2个）：列表、详情
    - 静态文件接口（3个）：图片访问、员工端首页、管理端首页
  - 前后端团队评审和确认 API 规范
  - _需求: 所有需求_
  - **负责人：后端工程师 + 前端工程师（联合定义）**
  - **依赖：任务 1**
  - **交付物：api-spec.yaml（OpenAPI 文档）**

### Phase 2: 后端开发（完整后端实现）

- [ ] 3. 后端：完整后端 API 实现
  - **项目基础设施**
    - 创建 server/ 目录结构（controllers/, services/, repositories/, models/, middleware/, utils/, config/）
    - 创建 requirements.txt（FastAPI, SQLAlchemy, aiosqlite, bcrypt, Pillow, slowapi）
    - 实现 settings.py 配置文件
    - 创建 main.py 应用入口，配置 CORS 中间件
  - **工具和中间件**
    - 实现 utils/password.py（密码哈希和验证）
    - 实现 utils/image.py（图片验证、缩略图生成）
    - 实现 utils/response.py（统一响应格式）
    - 实现 middleware/auth_middleware.py（Session 验证）
    - 实现 middleware/csrf_middleware.py（CSRF 保护）
    - 实现 middleware/rate_limit_middleware.py（频率限制）
  - **Repository 层（数据访问）**
    - 实现 repositories/session_repository.py
    - 实现 repositories/user_repository.py
    - 实现 repositories/address_repository.py
    - 实现 repositories/category_repository.py
    - 实现 repositories/product_repository.py
    - 实现 repositories/cart_repository.py
    - 实现 repositories/order_repository.py
    - 实现 repositories/point_repository.py
    - 实现 repositories/admin_log_repository.py
  - **Service 层（业务逻辑）**
    - 实现 services/auth_service.py（登录、登出、Session 验证、密码修改）
    - 实现 services/user_service.py（用户 CRUD、密码重置、状态切换）
    - 实现 services/category_service.py（分类 CRUD）
    - 实现 services/file_service.py（图片上传、删除）
    - 实现 services/product_service.py（产品 CRUD、搜索、筛选、分类关联）
    - 实现 services/cart_service.py（购物车 CRUD、数量限制）
    - 实现 services/order_service.py（订单创建、查询、事务处理）
    - 实现 services/point_service.py（积分发放、扣除、查询）
    - 实现 services/admin_log_service.py（日志记录、查询）
  - **Controller 层（API 接口）**
    - 实现 controllers/auth_controller.py（4个接口）
    - 实现 controllers/user_controller.py（7个接口）
    - 实现 controllers/category_controller.py（5个接口）
    - 实现 controllers/product_controller.py（8个接口）
    - 实现 controllers/cart_controller.py（5个接口）
    - 实现 controllers/order_controller.py（3个接口）
    - 实现 controllers/point_controller.py（4个接口）
    - 实现 controllers/admin_log_controller.py（2个接口）
  - **错误处理和日志**
    - 实现全局异常处理器
    - 配置日志记录（日志轮转）
    - 实现 API 请求日志中间件
  - **静态文件服务**
    - 配置 FastAPI 静态文件服务（/static/images/）
    - 配置前端静态文件服务（/, /manage）
  - **API 测试**
    - 使用 Postman/curl 测试所有 API 接口
    - 验证请求/响应格式符合 API 规范
    - 验证错误处理和边界情况
  - _需求: 所有需求_
  - **负责人：后端工程师**
  - **依赖：任务 1, 2**
  - **交付物：完整的后端 API 服务**

### Phase 3: 前端开发（完整前端实现）

- [ ] 4. 前端：完整前端应用实现
  - **项目基础设施**
    - 使用 Vue CLI 创建 front/personal/ 和 front/manage/ 项目
    - 安装依赖（Element UI, Vuex 3, Vue Router, Axios）
    - 配置 webpack 构建输出到 front/static/
    - 创建基础目录结构（views/, components/, store/, router/, api/, utils/, assets/）
  - **通用功能**
    - 实现 Axios 请求拦截器（添加 Session ID、CSRF Token）
    - 实现 Axios 响应拦截器（统一错误处理）
    - 创建 API 请求封装模块（根据 API 规范）
    - 配置 Vuex store 基础结构
    - 配置 Vue Router 基础路由和路由守卫
    - 创建通用组件（分页、搜索框、图片上传、确认对话框）
  - **员工端应用（Personal）**
    - **认证和个人中心**
      - 登录页面（views/Login.vue）
      - 导航栏组件（components/Navbar.vue，显示积分余额）
      - 个人中心页面（views/Profile.vue，个人信息、修改密码）
      - 收货地址管理页面（views/Address.vue）
    - **产品浏览**
      - 产品列表页面（views/ProductList.vue，搜索、筛选、排序、分页）
      - 产品卡片组件（components/ProductCard.vue）
      - 产品详情页面（views/ProductDetail.vue，图片轮播）
      - 分类筛选组件（components/CategoryFilter.vue）
    - **购物车和订单**
      - 购物车页面（views/Cart.vue，商品列表、总积分、结算）
      - 购物车商品项组件（components/CartItem.vue）
      - 订单确认页面（views/OrderConfirm.vue，商品明细、收货信息）
      - 订单列表页面（views/OrderList.vue）
      - 订单详情页面（views/OrderDetail.vue）
    - **积分管理**
      - 积分明细页面（views/PointTransactions.vue）
    - **Vuex 状态管理**
      - store/modules/user.js
      - store/modules/product.js
      - store/modules/cart.js
      - store/modules/order.js
      - store/modules/point.js
  - **管理端应用（Manage）**
    - **认证和布局**
      - 登录页面（views/Login.vue）
      - 布局组件（components/Layout.vue，侧边栏导航）
    - **用户管理**
      - 用户列表页面（views/UserList.vue，搜索、分页）
      - 用户编辑对话框（components/UserEditDialog.vue）
      - 用户创建对话框（components/UserCreateDialog.vue）
    - **产品和分类管理**
      - 分类管理页面（views/CategoryList.vue，树形结构）
      - 分类编辑对话框（components/CategoryEditDialog.vue）
      - 产品列表页面（views/ProductList.vue，搜索、筛选、分页）
      - 产品编辑页面（views/ProductEdit.vue，图片上传）
      - 图片上传组件（components/ImageUpload.vue）
    - **积分管理**
      - 积分发放页面（views/PointGrant.vue，单个/批量）
      - 用户选择组件（components/UserSelector.vue）
    - **操作日志**
      - 操作日志列表页面（views/AdminLogList.vue，筛选、分页）
      - 日志详情对话框（components/LogDetailDialog.vue）
    - **Vuex 状态管理**
      - store/modules/user.js
      - store/modules/product.js
      - store/modules/category.js
      - store/modules/log.js
  - **样式和交互优化**
    - 统一主题样式
    - 添加加载状态指示器
    - 添加空状态提示
    - 优化表单验证
    - 添加操作确认对话框
  - **性能优化**
    - 实现路由懒加载
    - 优化图片懒加载
    - 优化打包体积
  - **前端测试**
    - 使用 Mock 数据测试所有页面
    - 集成后端 API 后进行联调测试
  - _需求: 所有需求_
  - **负责人：前端工程师**
  - **依赖：任务 2（可以先用 Mock 数据开发，后期集成真实 API）**
  - **交付物：完整的前端应用（员工端 + 管理端）**

### Phase 4: 集成测试

- [ ] 5. 集成测试：前后端联调和功能验证
  - **环境准备**
    - 执行数据库初始化脚本
    - 启动后端服务
    - 构建并部署前端应用
  - **功能测试**
    - 测试员工端完整流程：登录 → 浏览产品 → 搜索筛选 → 加入购物车 → 兑换 → 查看订单 → 查看积分明细
    - 测试管理端完整流程：登录 → 创建用户 → 创建分类 → 创建产品 → 上传图片 → 发放积分 → 查看日志
    - 测试权限验证：员工无法访问管理端，管理员可以访问所有功能
  - **边界测试**
    - 测试积分不足时无法兑换
    - 测试购物车数量上限（100个）
    - 测试图片上传限制（格式、大小、数量）
    - 测试密码策略（6-8位，数字+字母）
  - **安全测试**
    - 测试 CSRF 保护
    - 测试请求频率限制（登录、兑换、搜索）
    - 测试 Session 过期和自动登出
  - **性能测试**
    - 测试页面加载时间（< 3秒）
    - 测试并发用户（50个并发）
    - 测试数据库查询性能
  - **数据完整性测试**
    - 验证订单创建的事务完整性
    - 验证积分扣除和余额更新的一致性
    - 验证操作日志记录的完整性
  - **浏览器兼容性测试**
    - Chrome、Firefox、Safari、Edge
  - _需求: 所有需求_
  - **负责人：全体团队（前端、后端、数据库工程师）**
  - **依赖：任务 3, 4**
  - **交付物：测试报告**

### Phase 5: CDK 部署

- [ ] 6. CDK：基础设施即代码
  - **CDK 项目初始化**
    - 创建 cdk/ 目录
    - 初始化 CDK 项目（TypeScript）
    - 配置 CDK 依赖
  - **VPC 和网络**
    - 定义 VPC（公有子网、私有子网）
    - 配置安全组（HTTP/HTTPS、SSH）
    - 配置 NAT Gateway（可选）
  - **EC2 实例**
    - 定义 EC2 实例（t3.small）
    - 配置 Ubuntu 22.04 LTS AMI
    - 配置 User Data 脚本（安装依赖、部署应用）
    - 配置 IAM Role 和 Instance Profile
  - **EBS 卷**
    - 创建 EBS 卷（20GB，gp3）
    - 配置自动挂载到 /mnt/data
    - 配置数据库和图片存储路径
  - **应用部署**
    - 配置 systemd 服务文件
    - 配置 Nginx 反向代理（可选）
    - 配置 SSL 证书（可选）
  - **监控和日志**
    - 配置 CloudWatch 日志
    - 配置 CloudWatch 指标
    - 配置告警（CPU、内存、磁盘）
  - **备份策略**
    - 配置 EBS 快照策略
    - 配置数据库备份
  - **CDK 部署**
    - 执行 cdk synth 生成 CloudFormation 模板
    - 执行 cdk deploy 部署到 AWS
    - 验证部署成功
  - _需求: 部署方案_
  - **负责人：DevOps 工程师**
  - **依赖：任务 5**
  - **交付物：CDK 代码、CloudFormation 模板、部署文档**

### Phase 6: 文档和交付

- [ ] 7. 文档：项目文档和操作手册
  - **技术文档**
    - README.md（项目说明、技术栈、目录结构）
    - 数据库设计文档（ER 图、表结构说明）
    - API 文档（OpenAPI/Swagger）
    - 架构设计文档（C4 模型图）
  - **部署文档**
    - 本地开发环境搭建指南
    - 生产环境部署指南
    - CDK 部署指南
    - 故障排查指南
  - **操作手册**
    - 管理员操作手册（用户管理、产品管理、积分发放）
    - 员工使用手册（产品浏览、兑换流程）
    - 系统维护手册（备份、恢复、监控）
  - **测试文档**
    - 测试用例文档
    - 测试报告
    - 性能测试报告
  - _需求: 文档需求_
  - **负责人：全体团队**
  - **依赖：任务 6**
  - **交付物：完整的项目文档**

- [ ] 8. 最终验收：生产环境验证
  - 在生产环境执行完整的功能测试
  - 验证系统可用性达到 95%
  - 验证数据持久化正确
  - 验证安全措施生效
  - 验证监控和告警正常
  - 验证备份策略有效
  - 交付项目给客户
  - _需求: 17.1_
  - **负责人：全体团队**
  - **依赖：任务 7**
  - **交付物：生产环境验收报告**

## 团队分工

### 4 人团队（推荐）
- **数据库工程师**：任务 1
- **后端工程师**：任务 2（联合定义 API）, 3
- **前端工程师**：任务 2（联合定义 API）, 4
- **DevOps 工程师**：任务 6

**协作任务**：
- 任务 5（集成测试）：全体参与
- 任务 7（文档）：全体参与
- 任务 8（验收）：全体参与

### 3 人团队
- **后端工程师**：任务 1, 2, 3
- **前端工程师**：任务 2, 4
- **DevOps 工程师**：任务 5, 6, 7, 8

### 2 人团队
- **全栈工程师 A**：任务 1, 2, 3, 6
- **全栈工程师 B**：任务 2, 4, 5, 7, 8

## 执行时间估算

### Day 1（8小时）
- **数据库工程师**：任务 1（数据库设计和初始化）- 8小时
- **后端 + 前端工程师**：任务 2（API 规范定义）- 4小时
- **前端工程师**：开始任务 4（使用 Mock 数据）- 4小时

### Day 2-3（16小时）
- **后端工程师**：任务 3（完整后端实现）- 16小时
- **前端工程师**：任务 4（完整前端实现）- 16小时
- **并行开发**：前后端同时进行

### Day 4（8小时）
- **全体团队**：任务 5（集成测试）- 4小时
- **DevOps 工程师**：任务 6（CDK 部署）- 4小时

### Day 5（缓冲，如需要）
- **全体团队**：任务 7（文档）- 4小时
- **全体团队**：任务 8（最终验收）- 4小时

## 关键依赖路径

```
任务 1（数据库）→ 任务 2（API 规范）→ 任务 3（后端）→ 任务 5（测试）→ 任务 6（CDK）→ 任务 8（验收）
                                    ↘ 任务 4（前端）↗
```

## API First 开发流程

### 1. API 规范定义阶段
- 数据库工程师完成 schema 设计
- 后端和前端工程师联合定义 API 规范
- 使用 OpenAPI/Swagger 格式文档化
- 前后端团队评审和确认

### 2. 并行开发阶段
- **后端**：严格按照 API 规范实现接口
- **前端**：使用 Mock 数据先行开发，后期切换到真实 API
- **Mock 工具**：可以使用 Mock Server（如 json-server, Mockoon）

### 3. 集成测试阶段
- 前端切换到真实 API
- 验证请求/响应格式符合规范
- 修复集成问题

## 质量检查点

- **检查点 1**：任务 1 完成后，数据库 schema 评审
- **检查点 2**：任务 2 完成后，API 规范评审（前后端确认）
- **检查点 3**：任务 3 完成后，后端 API 测试（Postman/curl）
- **检查点 4**：任务 4 完成后，前端功能测试（Mock 数据）
- **检查点 5**：任务 5 完成后，集成测试通过
- **检查点 6**：任务 8 完成后，生产环境验收通过

---

**总计**：8 个主要任务，预计 4-5 天完成
**开发模式**：API First，前后端严格按照 API 契约并行开发
**部署方式**：CDK 基础设施即代码，自动化部署到 AWS
