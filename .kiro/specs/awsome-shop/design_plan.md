# AWSomeShop 设计规划文档

## 项目概述
基于已确认的需求文档，为 AWSomeShop 内部员工福利电商网站创建详细的技术设计方案。

## 设计步骤

### 1. 技术架构设计
- [ ] 1.1 整体架构决策
  - [Question] 前后端是否需要完全分离部署？还是可以将 Vue 前端构建后由 FastAPI 静态服务？
  - [Answer] 不需要，直接由FastAPI方式提供API服务，但是需要在生成的工程化代码框架层面分成front，server
  
  - [Question] API 设计风格偏好是什么？（RESTful API 还是 GraphQL？）
  - [Answer] RESTful API
  
  - [Question] 是否需要使用 API 网关或反向代理（如 Nginx）？
  - [Answer] 不需要直接在AWSomeShop工程里面提供API
  
  - [Question] 会话管理方式：使用 JWT Token 还是 Session Cookie？
  - [Answer] Session

- [ ] 1.2 前端架构
  - [Question] Vue 版本偏好？（Vue 2 还是 Vue 3？）
  - [Answer] Vue 3
  
  - [Question] 是否使用 UI 组件库？如果是，偏好哪个？（Element Plus、Ant Design Vue、Vuetify 等）
  - [Answer] Element
  
  - [Question] 状态管理方案：是否需要 Vuex/Pinia？
  - [Answer] Vuex
  
  - [Question] 路由管理：使用 Vue Router？
  - [Answer] Vue Router
  
  - [Question] 构建工具偏好：Vite 还是 Webpack？
  - [Answer] webpack

- [ ] 1.3 后端架构
  - [Question] FastAPI 项目结构偏好：分层架构（Controller-Service-Repository）还是其他模式？
  - [Answer] Controller-Service-Repository
  
  - [Question] ORM 选择：SQLAlchemy、Tortoise ORM 还是其他？
  - [Answer] 不需要ORM
  
  - [Question] 数据验证：使用 Pydantic 模型？
  - [Answer] 不需要
  
  - [Question] 异步处理：是否需要使用 async/await 异步编程？
  - [Answer] async/await 

### 2. 数据库设计
- [ ] 2.1 数据表设计
  - [Question] 用户表（users）需要哪些额外字段？（如：创建时间、更新时间、最后登录时间等）
  - [Answer] 创建时间、更新时间、最后登录时间、用户状态（在职/离职）
  
  - [Question] 产品表（products）是否需要软删除（标记删除而非物理删除）？
  - [Answer] 软删除
  
  - [Question] 产品分类表：一级分类和二级分类是否需要分成两个表，还是用一个表通过 parent_id 实现？
  - [Answer] 用一个表通过 parent_id
  
  - [Question] 产品与分类的多对多关系：是否需要中间表？
  - [Answer] 是多对多，需要中间表
  
  - [Question] 订单表（orders）是否需要记录收货地址快照（防止用户修改地址后历史订单信息丢失）？
  - [Answer] 需要
  
  - [Question] 积分明细表（point_transactions）是否需要区分交易类型（发放、消费、退回等）？
  - [Answer] 就只有消费和发放二种状态
  
  - [Question] 操作日志表（admin_logs）是否需要记录操作前后的数据快照？
  - [Answer] 需要

- [ ] 2.2 数据索引设计
  - [Question] 是否需要为常用查询字段创建索引？（如：用户名、产品名称、订单时间等）
  - [Answer] 需要
  
  - [Question] 是否需要考虑全文搜索索引？
  - [Answer] 不需要

- [ ] 2.3 数据完整性
  - [Question] 外键约束：是否在数据库层面强制外键约束？
  - [Answer] 需要外键约束
  
  - [Question] 数据库事务：积分扣除和订单创建是否需要在同一事务中？
  - [Answer] 需要

### 3. 核心功能模块设计
- [ ] 3.1 认证授权模块
  - [Question] 密码存储：使用哪种哈希算法？（bcrypt、argon2、PBKDF2 等）
  - [Answer] bcrypt
  
  - [Question] Token 过期时间：访问令牌和刷新令牌的有效期分别是多久？
  - [Answer] 1个小时
  
  - [Question] 是否需要"记住我"功能？
  - [Answer] 不需要
  
  - [Question] 是否需要防止暴力破解的机制？（如：登录失败次数限制）
  - [Answer] 不需要

- [ ] 3.2 文件上传模块
  - [Question] 图片存储路径结构：按日期、按产品 ID 还是其他方式组织？
  - [Answer] 按日期+产品ID
  
  - [Question] 图片文件命名策略：使用原始文件名、UUID 还是其他方式？
  - [Answer] UUID，但是数据库中对于图片元数据命名需要保存原始文件名
  
  - [Question] 是否需要生成缩略图？
  - [Answer] 需要
  
  - [Question] 是否需要图片压缩或格式转换？
  - [Answer] 系统通过将上传的图片时候自动生成缩略图，不需要格式转换
  
  - [Question] 删除产品时，是否同时删除关联的图片文件？
  - [Answer] 需要删除关联的图片文件

- [ ] 3.3 积分系统模块
  - [Question] 积分是否支持小数？还是只支持整数？
  - [Answer] 不需要小数，本阶段只支持整数
  
  - [Question] 并发兑换时如何防止超扣积分？（乐观锁、悲观锁还是其他机制？）
  - [Answer] 前端需要防止重复点击，同时API接口层面需要防止重复提交，接口保证在一个事务里面，数据库采用悲观锁机制
  
  - [Question] 积分发放失败时的回滚策略是什么？
  - [Answer] 本阶段不需要考虑积分发放失败回滚策略

- [ ] 3.4 搜索和筛选模块
  - [Question] 产品搜索：是使用数据库 LIKE 查询还是需要更高级的搜索引擎？
  - [Answer] 直接使用LIKE，本阶段不需要高级搜索引擎
  
  - [Question] 分页方式：传统分页（页码+每页数量）还是游标分页？
  - [Answer] 传统分页
  
  - [Question] 每页显示多少条产品记录？
  - [Answer] 20条

### 4. 前端页面设计
- [ ] 4.1 页面结构
  - [Question] 员工端需要哪些页面？（如：登录页、产品列表页、产品详情页、个人中心、兑换历史等）
  - [Answer] 登录页、产品列表页、产品详情页、个人中心、兑换历史、购物车等
  
  - [Question] 管理端需要哪些页面？（如：登录页、仪表板、用户管理、产品管理、分类管理、积分管理、操作日志等）
  - [Answer] 如：登录页、仪表板、用户管理、产品管理、分类管理、积分管理、操作日志等
  
  - [Question] 员工端和管理端是否共用同一个前端项目？还是分开两个项目？
  - [Answer] 共用同一个前端都在front里面，但是需要在工程化框架分成到二个不同文件夹就行，管理端使用manage，用户端使用personal。

- [ ] 4.2 用户体验
  - [Question] 是否需要加载动画或骨架屏？
  - [Answer] 不需要
  
  - [Question] 错误提示方式：Toast 提示、Modal 弹窗还是其他方式？
  - [Answer] Toast 提示
  
  - [Question] 是否需要确认对话框？（如：删除产品、兑换产品等操作）
  - [Answer] 需要
  
  - [Question] 表单验证：前端验证还是前后端都验证？
  - [Answer] 前后端都需要验证

### 5. API 接口设计
- [ ] 5.1 接口规范
  - [Question] API 响应格式：是否统一使用标准格式？（如：`{code, message, data}`）
  - [Answer] {code, message, data}
  
  - [Question] HTTP 状态码使用策略：业务错误是否也返回 200 并在响应体中标识错误？
  - [Answer] 只有正确返回200，其他的错误信息定制各自的状态码，例如400、500等
  
  - [Question] 是否需要 API 版本控制？（如：/api/v1/）
  - [Answer] 本阶段不考虑API
  
  - [Question] 是否需要 API 文档？（Swagger/OpenAPI）
  - [Answer] Swagger

- [ ] 5.2 接口列表
  - [Question] 是否需要我列出所有需要的 API 接口清单？
  - [Answer] 需要

### 6. 安全性设计
- [ ] 6.1 安全措施
  - [Question] CORS 策略：允许哪些域名访问 API？
  - [Answer] 不限制CORS
  
  - [Question] 是否需要 CSRF 保护？
  - [Answer] 需要CSRF
  
  - [Question] 是否需要请求频率限制（Rate Limiting）？
  - [Answer] 需要多请求接口进行频率限制
  
  - [Question] 敏感信息（如密码）在日志中如何处理？
  - [Answer] 本阶段不需要处理
  
  - [Question] SQL 注入防护：ORM 是否足够？还是需要额外的输入验证？
  - [Answer] 足够了

### 7. 错误处理和日志
- [ ] 7.1 错误处理
  - [Question] 后端错误处理策略：全局异常处理器？
  - [Answer] 需要
  
  - [Question] 前端错误处理：是否需要全局错误拦截器？
  - [Answer] 需要一个错误提示页面

- [ ] 7.2 日志记录
  - [Question] 应用日志级别：DEBUG、INFO、WARNING、ERROR？
  - [Answer] DEBUG、INFO、WARNING、ERROR
  
  - [Question] 日志存储位置：文件、数据库还是日志服务？
  - [Answer] 文件
  
  - [Question] 是否需要记录 API 请求日志？
  - [Answer] 需要

### 8. 部署和环境配置
- [ ] 8.1 部署方式
  - [Question] 部署到 AWS 的哪个服务？（EC2、ECS、Lambda、Elastic Beanstalk 等）
  - [Answer] EC2
  
  - [Question] 是否使用 Docker 容器化部署？
  - [Answer] 不需要docker容器化部署
  
  - [Question] 数据库文件存储位置：本地磁盘还是 AWS EBS？
  - [Answer]  AWS EBS
  
  - [Question] 产品图片存储：本地磁盘、AWS S3 还是 EFS？
  - [Answer]  AWS EBS

- [ ] 8.2 环境配置
  - [Question] 是否需要区分开发、测试、生产环境？
  - [Answer] 不需要
  
  - [Question] 配置文件管理方式：环境变量、配置文件还是 AWS Systems Manager？
  - [Answer] 配置文件

### 9. 测试策略
- [ ] 9.1 测试类型
  - [Question] 是否需要单元测试？测试覆盖率目标是多少？
  - [Answer] 不需要
  
  - [Question] 是否需要集成测试？
  - [Answer] 不需要
  
  - [Question] 是否需要端到端测试？
  - [Answer] 不需要
  
  - [Question] 是否需要性能测试？
  - [Answer] 不需要

### 10. 编写正式设计文档
- [ ] 10.1 整理设计文档
  - 基于以上澄清的信息，编写完整的设计文档
  - 包含：架构图、数据模型、组件设计、接口设计、错误处理、测试策略等

---

## 追加澄清问题

基于您的回答，我发现以下几个方面需要进一步明确：

### 11. 前端架构补充
- [ ] 11.1 UI 组件库版本
  - [Question] 您提到使用 Element，请确认是 Element Plus（Vue 3 版本）还是 Element UI（Vue 2 版本）？
  - [Answer] Element UI（Vue 2 版本）
  
- [ ] 11.2 购物车功能
  - [Question] 您提到员工端需要"购物车"页面，但需求文档中没有提到购物车功能。请确认：购物车是否允许一次兑换多个产品？
  - [Answer] 购物车允许一次兑换多个产品
  
  - [Question] 如果支持购物车，购物车数据是存储在前端（localStorage）还是后端数据库？
  - [Answer] 后端数据库
  
  - [Question] 购物车中的产品是否有数量概念？（即同一产品可以兑换多个）
  - [Answer] 可以兑换多个

### 12. 后端架构补充
- [ ] 12.1 数据库操作
  - [Question - Updated] 您提到"不需要 ORM"，请确认是使用原生 SQL 查询还是使用 SQLAlchemy Core（非 ORM 模式）？
  - [Answer] 使用 SQLAlchemy Core
  
  - [Question] 如果使用原生 SQL，是否需要数据库连接池管理？
  - [Answer] 需要数据库连接池管理

- [ ] 12.2 Session 管理
  - [Question] Session 存储方式：内存、Redis 还是数据库？
  - [Answer] 数据库
  
  - [Question] Session 过期时间是多久？
  - [Answer] 1个小时
  
  - [Question] 用户登出时是否需要清除 Session？
  - [Answer] 需要清除session

### 13. 数据库表设计补充
- [ ] 13.1 用户表字段
  - [Question] 用户状态字段：是使用布尔值（is_active）还是枚举值（在职/离职/其他）？
  - [Answer] 布尔值
  
  - [Question] 收货地址和电话是存储在用户表中，还是单独的地址表？
  - [Answer] 单独表

- [ ] 13.2 产品图片存储
  - [Question] 产品图片元数据（原始文件名、UUID、缩略图路径等）是存储在产品表中，还是单独的图片表？
  - [Answer] 单独表
  
  - [Question] 缩略图尺寸规格是多少？（如：200x200）
  - [Answer] 320*320

- [ ] 13.3 操作日志数据快照
  - [Question] 操作前后的数据快照是以 JSON 格式存储，还是其他格式？
  - [Answer] json
  
  - [Question] 对于删除操作，是否只记录删除前的数据快照？
  - [Answer] 不需要

### 14. API 接口补充
- [ ] 14.1 静态文件服务
  - [Question] FastAPI 如何提供 Vue 构建后的静态文件？是通过 StaticFiles 中间件还是其他方式？
  - [Answer] 创建静态文件目录，将Vue项目dist目录下所有构建生成的文件复制到新创建的static文件夹内，运行FastAPI应用， 在浏览器中访问前端页面。不需要其他方式
  
  - [Question] 产品图片访问路径格式是什么？（如：/static/images/{date}/{product_id}/{filename}）
  - [Answer] 确认

- [ ] 14.2 文件上传
  - [Question] 文件上传接口是否需要支持多文件同时上传？
  - [Answer] 需要
  
  - [Question] 文件上传大小限制除了单个文件 10MB，是否需要限制总上传大小？
  - [Answer] 总上传大小限定为500MB

### 15. 安全性补充
- [ ] 15.1 CSRF 保护
  - [Question] CSRF Token 的生成和验证机制：使用 FastAPI 的内置支持还是自定义实现？
  - [Answer] 使用 FastAPI 的内置支持还是自定义实现
  
- [ ] 15.2 请求频率限制
  - [Question] 哪些接口需要频率限制？（如：登录、兑换、搜索等）
  - [Answer] 登录、兑换、搜索
  
  - [Question] 频率限制的阈值是多少？（如：每分钟 10 次）
  - [Answer] 每秒钟10次

### 16. 项目结构补充
- [ ] 16.1 目录结构
  - [Question] 项目根目录结构是否按以下方式组织？
    ```
    AWSomeShop/
    ├── front/           # 前端代码
    │   ├── manage/      # 管理端
    │   └── personal/    # 员工端
    └── server/          # 后端代码
        ├── controllers/
        ├── services/
        └── repositories/
    ```
  - [Answer]  确认
  
  - [Question] 前端构建输出目录放在哪里？（如：server/static/）
  - [Answer] front/static/

### 17. 数据初始化
- [ ] 17.1 初始数据
  - [Question] 系统是否需要初始化脚本？（如：创建默认管理员账户、初始化产品分类等）
  - [Answer] 需要
  
  - [Question] 如果需要，默认管理员的用户名和密码是什么？
  - [Answer] admin/admin123456

---

## 再次澄清问题

基于您的最新回答，我发现以下几个关键问题需要再次确认：

### 18. 技术栈冲突确认
- [ ] 18.1 Vue 版本与 UI 库匹配
  - [Question - IMPORTANT] 您在第 1.2 节选择了 Vue 3，但在第 11.1 节选择了 Element UI（Vue 2 版本）。这两者不兼容。请确认：
    - 选项 A：使用 Vue 3 + Element Plus
    - 选项 B：使用 Vue 2 + Element UI
  - [Answer] 选项 B：使用 Vue 2 + Element UI
  
- [ ] 18.2 Vuex 版本确认
  - [Question] 如果使用 Vue 3，Vuex 需要使用 Vuex 4；如果使用 Vue 2，则使用 Vuex 3。请确认您的选择与 Vue 版本匹配。
  - [Answer] Vuex 3

### 19. 购物车功能需求补充
由于购物车是新增功能，需要补充到需求文档中：

- [ ] 19.1 购物车基本功能
  - [Question] 购物车需要支持哪些操作？（添加产品、修改数量、删除产品、清空购物车等）
  - [Answer] 添加产品、修改数量、删除产品、清空购物车等
  
  - [Question] 购物车中的产品数量是否有上限？
  - [Answer] 最多100个
  
  - [Question] 购物车是否有有效期？（如：7天后自动清空）
  - [Answer] 没有有效期设置
  
- [ ] 19.2 购物车结算
  - [Question] 从购物车结算时，如果积分不足以兑换所有产品，如何处理？（全部失败、部分成功、提示用户选择等）
  - [Answer] 直接提示用户选择符合积分兑换的产品
  
  - [Question] 购物车结算时，是生成一个订单还是多个订单？
  - [Answer] 一个订单就行，不需要拆分合并订单
  
  - [Question] 购物车结算时的收货地址：是所有产品使用同一个地址，还是可以分别指定？
  - [Answer] 同一个

### 20. 数据库表补充
- [ ] 20.1 购物车表设计
  - [Question] 购物车表需要哪些字段？（如：用户ID、产品ID、数量、添加时间等）
  - [Answer] 用户ID、产品ID、数量、添加时间等
  
  - [Question] 用户是否可以将同一产品多次添加到购物车？还是自动合并数量？
  - [Answer] 

- [ ] 20.2 订单表补充
  - [Question] 如果购物车一次兑换多个产品，订单表是否需要订单明细表（order_items）来记录每个产品？
  - [Answer] 
  
  - [Question] 订单表是否需要记录总消耗积分？
  - [Answer] 

### 21. Session 表设计
- [ ] 21.1 Session 存储
  - [Question] Session 存储在数据库中，需要创建 sessions 表。该表需要哪些字段？（如：session_id、user_id、data、created_at、expires_at等）
  - [Answer] 
  
  - [Question] 是否需要定期清理过期的 Session 记录？
  - [Answer] 

### 22. 操作日志补充
- [ ] 22.1 删除操作日志
  - [Question - Updated] 您在 13.3 节回答"不需要"记录删除操作的数据快照。请确认：
    - 删除操作是否完全不记录日志？
    - 还是记录日志但不记录数据快照？
  - [Answer] 
  
### 23. CSRF 实现确认
- [ ] 23.1 CSRF 选择
  - [Question - Updated] 您在 15.1 节回答"使用 FastAPI 的内置支持还是自定义实现"，这似乎是问题而非答案。请明确选择：
    - 选项 A：使用 FastAPI 内置的 CSRF 保护
    - 选项 B：自定义实现 CSRF 保护
    - 选项 C：不实现 CSRF 保护（因为前后端不分离，风险较低）
  - [Answer] 

### 24. 前端构建输出位置确认
- [ ] 24.1 静态文件位置
  - [Question - Updated] 您在 16.1 节回答前端构建输出在 "front/static/"，但通常 FastAPI 需要从 server 目录访问静态文件。请确认：
    - 选项 A：构建输出到 front/dist/，然后复制到 server/static/
    - 选项 B：直接构建输出到 server/static/
    - 选项 C：构建输出到 front/static/，FastAPI 配置访问 ../front/static/
  - [Answer] 

## 当前状态
等待您回答再次澄清的问题。这些问题对于技术选型和架构设计至关重要。

## 说明
- 请特别注意第 18.1 节的 Vue 版本与 UI 库匹配问题，这是技术栈的基础
- 购物车功能是新增需求，需要详细确认
- 请逐步回答上述问题
- 如果有任何疑问，请告诉我
