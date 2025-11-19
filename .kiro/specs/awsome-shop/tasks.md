# AWSomeShop 实施任务列表

## 任务执行说明

本任务列表按照依赖关系和并行执行可能性进行了组织。标注了 **[并行组 X]** 的任务可以同时执行，以缩短整体交付时间。

## 任务列表

### Phase 1: 项目基础设施搭建

#### [并行组 A] 后端基础设施

- [ ] 1. 创建后端项目结构和数据库模型
  - 创建 server/ 目录结构（controllers/, services/, repositories/, models/, middleware/, utils/, config/）
  - 创建 requirements.txt 并定义依赖（FastAPI, SQLAlchemy, aiosqlite, bcrypt, Pillow, slowapi）
  - 实现 database.py 定义所有12个数据表结构
  - 实现 settings.py 配置文件
  - 创建 main.py 应用入口，配置 CORS 中间件
  - _需求: 16.1, 16.2_

- [ ] 2. 实现数据库初始化脚本
  - 创建 init_db.py 脚本
  - 实现创建管理员账户功能（1个管理员）
  - 实现创建员工账户功能（20个员工）
  - 实现创建产品分类功能（5个一级分类，20个二级分类）
  - _需求: 9.1, 9.2, 12.1, 12.2_

#### [并行组 B] 前端基础设施

- [ ] 3. 创建员工端 Vue 项目
  - 使用 Vue CLI 创建 front/personal/ 项目
  - 安装依赖（Element UI, Vuex 3, Vue Router, Axios）
  - 配置 webpack 构建输出到 front/static/personal/
  - 创建基础目录结构（views/, components/, store/, router/, api/, utils/, assets/）
  - _需求: 前端架构_

- [ ] 4. 创建管理端 Vue 项目
  - 使用 Vue CLI 创建 front/manage/ 项目
  - 安装依赖（Element UI, Vuex 3, Vue Router, Axios）
  - 配置 webpack 构建输出到 front/static/manage/
  - 创建基础目录结构（views/, components/, store/, router/, api/, utils/, assets/）
  - _需求: 前端架构_

- [ ] 5. 配置前端通用功能
  - 实现 Axios 请求拦截器（添加 Session ID 和 CSRF Token）
  - 实现 Axios 响应拦截器（统一错误处理）
  - 创建 API 请求封装模块
  - 配置 Vuex store 基础结构
  - 配置 Vue Router 基础路由
  - _需求: 安全性设计_


### Phase 2: 核心认证和用户模块

#### [并行组 C] 认证授权模块

- [ ] 6. 实现认证服务和中间件
  - 实现 utils/password.py（密码哈希和验证，使用 bcrypt）
  - 实现 repositories/session_repository.py（Session CRUD 操作）
  - 实现 repositories/user_repository.py（用户查询操作）
  - 实现 services/auth_service.py（登录、登出、Session 验证、密码修改）
  - 实现 middleware/auth_middleware.py（Session 验证中间件）
  - 实现 controllers/auth_controller.py（登录、登出、获取当前用户、修改密码接口）
  - _需求: 1.1, 1.2, 1.3, 1.4, 8.1, 8.2, 8.3, 8.4_

- [ ] 7. 实现用户管理模块
  - 实现 services/user_service.py（用户 CRUD、密码重置、状态切换）
  - 实现 controllers/user_controller.py（用户管理接口）
  - _需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.1, 10.2, 10.3_

#### [并行组 D] 前端认证页面

- [ ] 8. 实现员工端登录和个人中心
  - 创建员工端登录页面（views/Login.vue）
  - 创建员工端导航栏组件（components/Navbar.vue，显示积分余额）
  - 创建个人中心页面（views/Profile.vue，显示个人信息、积分余额、修改密码）
  - 创建收货地址管理页面（views/Address.vue）
  - 实现 Vuex 用户状态管理（store/modules/user.js）
  - 实现路由守卫（验证登录状态）
  - _需求: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4_

- [ ] 9. 实现管理端登录和用户管理页面
  - 创建管理端登录页面（views/Login.vue）
  - 创建管理端布局组件（components/Layout.vue，包含侧边栏导航）
  - 创建用户列表页面（views/UserList.vue，支持搜索、分页）
  - 创建用户编辑对话框（components/UserEditDialog.vue）
  - 创建用户创建对话框（components/UserCreateDialog.vue）
  - 实现 Vuex 用户状态管理（store/modules/user.js）
  - 实现路由守卫（验证管理员权限）
  - _需求: 1.1, 1.2, 1.3, 1.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.1, 10.2, 10.3_

### Phase 3: 产品和分类模块

#### [并行组 E] 产品后端服务

- [ ] 10. 实现产品分类管理模块
  - 实现 repositories/category_repository.py（分类 CRUD 操作）
  - 实现 services/category_service.py（分类业务逻辑）
  - 实现 controllers/category_controller.py（分类管理接口）
  - _需求: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 11. 实现文件上传服务
  - 实现 utils/image.py（图片验证、缩略图生成）
  - 实现 services/file_service.py（图片上传、删除、元数据管理）
  - 配置 FastAPI 静态文件服务（/static/images/）
  - _需求: 13.2, 13.3, 13.4_

- [ ] 12. 实现产品管理模块
  - 实现 repositories/product_repository.py（产品 CRUD、搜索、筛选）
  - 实现 services/product_service.py（产品业务逻辑、分类关联）
  - 实现 controllers/product_controller.py（产品管理接口、图片上传接口）
  - _需求: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 13.9_


- [ ] 13. 完善数据库初始化脚本 - 产品数据
  - 在 init_db.py 中实现创建100个3C产品功能
  - 实现产品图片生成功能（使用占位图服务）
  - 实现产品分类关联功能
  - 确保每个产品有1-3张图片和缩略图
  - _需求: 数据初始化_

#### [并行组 F] 产品前端页面

- [ ] 14. 实现员工端产品浏览功能
  - 创建产品列表页面（views/ProductList.vue，支持搜索、分类筛选、排序、分页）
  - 创建产品卡片组件（components/ProductCard.vue，显示图片、名称、积分）
  - 创建产品详情页面（views/ProductDetail.vue，显示完整信息和图片轮播）
  - 创建分类筛选组件（components/CategoryFilter.vue）
  - 创建搜索框组件（components/SearchBar.vue）
  - 实现 Vuex 产品状态管理（store/modules/product.js）
  - _需求: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3_

- [ ] 15. 实现管理端产品和分类管理页面
  - 创建分类管理页面（views/CategoryList.vue，树形结构展示）
  - 创建分类编辑对话框（components/CategoryEditDialog.vue）
  - 创建产品列表页面（views/ProductList.vue，支持搜索、筛选、分页）
  - 创建产品编辑页面（views/ProductEdit.vue，包含图片上传）
  - 创建图片上传组件（components/ImageUpload.vue，支持多图上传、预览、删除）
  - 实现 Vuex 产品和分类状态管理（store/modules/product.js, store/modules/category.js）
  - _需求: 12.1, 12.2, 12.3, 12.4, 12.5, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 13.9_

### Phase 4: 购物车和订单模块

#### [并行组 G] 购物车和订单后端

- [ ] 16. 实现购物车模块
  - 实现 repositories/cart_repository.py（购物车 CRUD 操作）
  - 实现 services/cart_service.py（购物车业务逻辑、数量限制）
  - 实现 controllers/cart_controller.py（购物车接口）
  - _需求: 购物车功能_

- [ ] 17. 实现积分服务
  - 实现 repositories/point_repository.py（积分交易记录操作）
  - 实现 services/point_service.py（积分发放、扣除、查询）
  - _需求: 5.1, 5.2, 5.3, 5.4, 11.1, 11.2, 11.3, 11.4_

- [ ] 18. 实现订单模块
  - 实现 repositories/order_repository.py（订单 CRUD 操作）
  - 实现 repositories/address_repository.py（收货地址操作）
  - 实现 services/order_service.py（订单创建、查询，包含事务和悲观锁）
  - 实现 controllers/order_controller.py（订单接口）
  - 实现 controllers/point_controller.py（积分查询和发放接口）
  - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 7.4, 11.1, 11.2, 11.3, 11.4_

#### [并行组 H] 购物车和订单前端

- [ ] 19. 实现员工端购物车功能
  - 创建购物车页面（views/Cart.vue，显示商品列表、总积分、结算按钮）
  - 创建购物车商品项组件（components/CartItem.vue，支持修改数量、删除）
  - 在产品详情页添加"加入购物车"按钮
  - 在导航栏添加购物车图标和数量徽章
  - 实现 Vuex 购物车状态管理（store/modules/cart.js）
  - _需求: 购物车功能_

- [ ] 20. 实现员工端订单和积分功能
  - 创建订单确认页面（views/OrderConfirm.vue，显示商品明细、收货信息、总积分）
  - 创建订单列表页面（views/OrderList.vue，显示历史订单）
  - 创建订单详情页面（views/OrderDetail.vue，显示订单完整信息）
  - 创建积分明细页面（views/PointTransactions.vue，显示积分变动记录）
  - 实现 Vuex 订单和积分状态管理（store/modules/order.js, store/modules/point.js）
  - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3_


- [ ] 21. 实现管理端积分管理页面
  - 创建积分发放页面（views/PointGrant.vue，支持单个和批量发放）
  - 创建用户选择组件（components/UserSelector.vue，支持搜索和多选）
  - 在用户列表页面添加"发放积分"快捷操作
  - _需求: 11.1, 11.2, 11.3, 11.4_

### Phase 5: 安全和日志模块

#### [并行组 I] 安全中间件

- [ ] 22. 实现安全中间件
  - 实现 middleware/csrf_middleware.py（CSRF 保护）
  - 实现 middleware/rate_limit_middleware.py（请求频率限制）
  - 在 main.py 中注册中间件
  - 配置频率限制规则（登录、兑换、搜索接口）
  - _需求: 安全性设计_

- [ ] 23. 实现操作日志模块
  - 实现 repositories/admin_log_repository.py（日志 CRUD 操作）
  - 实现 services/admin_log_service.py（日志记录、查询）
  - 创建日志记录装饰器（自动记录管理员操作）
  - 在所有管理员操作中集成日志记录
  - 实现 controllers/admin_log_controller.py（日志查询接口）
  - _需求: 14.1, 14.2, 14.3, 14.4, 14.5_

#### [并行组 J] 日志前端页面

- [ ] 24. 实现管理端操作日志页面
  - 创建操作日志列表页面（views/AdminLogList.vue，支持筛选、分页）
  - 创建日志详情对话框（components/LogDetailDialog.vue，显示数据快照）
  - 实现 Vuex 日志状态管理（store/modules/log.js）
  - _需求: 14.1, 14.2, 14.3, 14.4, 14.5_

### Phase 6: 集成和优化

- [ ] 25. 前端样式和交互优化
  - 统一两个应用的主题样式
  - 添加加载状态指示器
  - 添加空状态提示
  - 优化表单验证提示
  - 添加操作确认对话框
  - 优化移动端响应式布局（可选）
  - _需求: 用户体验_

- [ ] 26. 错误处理和日志完善
  - 完善全局异常处理器
  - 配置日志轮转
  - 添加 API 请求日志中间件
  - 完善前端错误提示
  - 创建错误页面（404, 500, 403）
  - _需求: 错误处理_

- [ ] 27. 性能优化
  - 添加数据库查询索引
  - 实现前端路由懒加载
  - 优化图片加载（懒加载）
  - 添加 API 响应缓存（可选）
  - _需求: 15.1, 15.2, 15.3_

### Phase 7: 测试和部署准备

- [ ] 28. 系统集成测试
  - 执行数据库初始化脚本，验证数据正确性
  - 测试员工端完整流程（登录 → 浏览产品 → 加入购物车 → 兑换 → 查看订单）
  - 测试管理端完整流程（登录 → 创建用户 → 创建产品 → 发放积分 → 查看日志）
  - 测试边界情况（积分不足、购物车上限、图片上传限制）
  - 测试安全功能（CSRF 保护、频率限制、权限验证）
  - _需求: 所有需求_

- [ ] 29. 部署配置和文档
  - 创建生产环境配置文件（settings.py 环境变量）
  - 创建 systemd 服务文件
  - 编写部署脚本（deploy.sh）
  - 编写 README.md（项目说明、安装步骤、运行方法）
  - 编写操作手册（管理员使用指南）
  - 配置 EBS 挂载脚本
  - _需求: 部署方案_

- [ ] 30. 最终验收检查
  - 验证所有 API 接口正常工作
  - 验证所有页面功能正常
  - 验证数据持久化正确
  - 验证日志记录完整
  - 验证安全措施生效
  - 进行性能测试（50 并发用户）
  - _需求: 15.1, 15.2, 15.3, 16.1, 16.2, 16.3, 17.1_

## 并行执行时间估算

### Day 1（8小时）

**上午（4小时）**
- **并行组 A + B**：任务 1-5（项目基础设施）- 预计 3 小时
- **并行组 C + D**：任务 6-9（认证和用户模块）- 预计 1 小时开始

**下午（4小时）**
- **并行组 C + D**：任务 6-9 继续 - 预计 3 小时
- **并行组 E**：任务 10-13（产品后端）- 预计 1 小时开始

### Day 2（8小时）

**上午（4小时）**
- **并行组 E + F**：任务 10-15（产品模块）- 预计 3 小时
- **并行组 G + H**：任务 16-21（购物车和订单）- 预计 1 小时开始

**下午（4小时）**
- **并行组 G + H**：任务 16-21 继续 - 预计 2 小时
- **并行组 I + J**：任务 22-24（安全和日志）- 预计 1.5 小时
- **顺序执行**：任务 25-30（集成、测试、部署）- 预计 0.5 小时开始

### Day 3（缓冲时间，如需要）

**全天（8小时）**
- **顺序执行**：任务 25-30 继续（优化、测试、部署）- 预计 4-6 小时

## 关键依赖路径

```
任务 1 → 任务 2 → 任务 13 → 任务 28 → 任务 29 → 任务 30
任务 1 → 任务 6 → 任务 7 → 任务 23 → 任务 28
任务 1 → 任务 10 → 任务 12 → 任务 18 → 任务 28
任务 3,4,5 → 任务 8,9 → 任务 14,15 → 任务 19,20,21 → 任务 28
```

## 资源分配建议

**2 人团队**
- **开发者 A（后端）**：任务 1, 2, 6, 7, 10, 11, 12, 13, 16, 17, 18, 22, 23
- **开发者 B（前端）**：任务 3, 4, 5, 8, 9, 14, 15, 19, 20, 21, 24, 25

**3 人团队**
- **开发者 A（后端核心）**：任务 1, 2, 6, 7, 22, 23, 26, 27
- **开发者 B（后端业务）**：任务 10, 11, 12, 13, 16, 17, 18
- **开发者 C（前端）**：任务 3, 4, 5, 8, 9, 14, 15, 19, 20, 21, 24, 25

**单人团队**
- 按照任务顺序执行，预计需要 3-4 天完成

## 质量检查点

- **检查点 1**：Phase 2 完成后，验证认证和用户管理功能可用
- **检查点 2**：Phase 3 完成后，验证产品浏览和管理功能可用
- **检查点 3**：Phase 4 完成后，验证完整的兑换流程可用
- **检查点 4**：Phase 7 完成后，验证系统整体稳定性和性能

---

**总计**：30 个主要任务，预计 2-3 天完成
**并行效率**：通过合理分组，可实现约 50-60% 的并行开发效率
