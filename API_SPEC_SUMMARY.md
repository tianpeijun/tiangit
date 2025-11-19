# AWSomeShop API 规范文档说明

## 概述

本文档是 AWSomeShop 员工福利电商平台的完整 API 规范，采用 OpenAPI 3.0.3 标准编写。

## 文档位置

- **主文档**: `api-spec.yaml`
- **格式**: OpenAPI 3.0.3 (Swagger)

## API 接口统计

### 总计：48 个接口

#### 1. 认证接口（4个）
- POST `/api/auth/login` - 用户登录
- POST `/api/auth/logout` - 用户登出
- GET `/api/auth/current-user` - 获取当前用户信息
- POST `/api/personal/password/change` - 员工修改密码

#### 2. 员工端-产品接口（4个）
- GET `/api/personal/products` - 获取产品列表（支持分页、排序、筛选）
- GET `/api/personal/products/{id}` - 获取产品详情
- GET `/api/personal/products/search` - 搜索产品
- GET `/api/personal/categories` - 获取分类树

#### 3. 员工端-购物车接口（5个）
- GET `/api/personal/cart` - 获取购物车
- POST `/api/personal/cart/add` - 添加到购物车
- PUT `/api/personal/cart/update` - 更新购物车商品数量
- DELETE `/api/personal/cart/remove/{product_id}` - 删除购物车商品
- DELETE `/api/personal/cart/clear` - 清空购物车

#### 4. 员工端-订单接口（3个）
- POST `/api/personal/orders/create` - 创建订单
- GET `/api/personal/orders` - 获取订单列表
- GET `/api/personal/orders/{id}` - 获取订单详情

#### 5. 员工端-积分接口（2个）
- GET `/api/personal/points/balance` - 获取积分余额
- GET `/api/personal/points/transactions` - 获取积分明细

#### 6. 员工端-个人中心接口（3个）
- GET `/api/personal/profile` - 获取个人信息
- GET `/api/personal/address` - 获取收货地址
- PUT `/api/personal/address` - 更新收货地址

#### 7. 管理端-用户管理接口（7个）
- GET `/api/manage/users` - 获取用户列表
- POST `/api/manage/users` - 创建用户
- GET `/api/manage/users/{id}` - 获取用户详情
- PUT `/api/manage/users/{id}` - 更新用户信息
- DELETE `/api/manage/users/{id}` - 删除用户
- PUT `/api/manage/users/{id}/status` - 启用/禁用用户
- POST `/api/manage/users/{id}/reset-password` - 重置密码

#### 8. 管理端-产品管理接口（8个）
- GET `/api/manage/products` - 获取产品列表
- POST `/api/manage/products` - 创建产品
- GET `/api/manage/products/{id}` - 获取产品详情
- PUT `/api/manage/products/{id}` - 更新产品
- DELETE `/api/manage/products/{id}` - 删除产品（软删除）
- PUT `/api/manage/products/{id}/status` - 上架/下架产品
- POST `/api/manage/products/{id}/images` - 上传产品图片
- DELETE `/api/manage/products/images/{image_id}` - 删除产品图片

#### 9. 管理端-分类管理接口（5个）
- GET `/api/manage/categories` - 获取分类列表
- POST `/api/manage/categories` - 创建分类
- GET `/api/manage/categories/{id}` - 获取分类详情
- PUT `/api/manage/categories/{id}` - 更新分类
- DELETE `/api/manage/categories/{id}` - 删除分类

#### 10. 管理端-积分管理接口（2个）
- POST `/api/manage/points/grant` - 单个发放积分
- POST `/api/manage/points/grant-batch` - 批量发放积分

#### 11. 管理端-操作日志接口（2个）
- GET `/api/manage/logs` - 获取操作日志列表
- GET `/api/manage/logs/{id}` - 获取日志详情

#### 12. 静态文件接口（3个）
- GET `/static/images/{path}` - 访问产品图片
- GET `/` - 员工端首页
- GET `/manage` - 管理端首页

## 核心特性

### 1. 认证方式
- **Session-based 认证**
- 登录成功后返回 Session ID
- 后续请求通过 `X-Session-ID` header 携带
- Session 过期时间：1小时

### 2. 统一响应格式

**成功响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

### 3. 分页格式

所有列表接口支持分页：

**请求参数：**
- `page`: 页码（从1开始，默认1）
- `page_size`: 每页数量（默认20，最大100）

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 4. 错误码规范

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或会话已过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### 5. 频率限制

以下接口有频率限制：
- 登录接口：10次/秒
- 兑换接口：10次/秒
- 搜索接口：10次/秒

### 6. 数据验证规则

**密码规则：**
- 长度：6-8位
- 必须包含数字和字母

**图片上传规则：**
- 支持格式：PNG、JPG
- 单个文件大小：最大10MB
- 每个产品最多：3张图片

**购物车规则：**
- 总商品数量上限：100个

## 数据模型

### 核心实体

1. **User（用户）**
   - 包含基本信息、角色、积分余额、账户状态

2. **Product（产品）**
   - 包含名称、描述、所需积分、状态、图片

3. **Category（分类）**
   - 支持二级分类（一级分类和二级分类）

4. **Order（订单）**
   - 包含订单号、总积分、收货信息、订单明细

5. **CartItem（购物车项）**
   - 包含产品信息、数量、小计积分

6. **PointTransaction（积分交易）**
   - 记录积分发放和消费历史

7. **AdminLog（操作日志）**
   - 记录管理员操作，包含数据快照

## 使用指南

### 1. 查看 API 文档

使用 Swagger UI 或其他 OpenAPI 工具查看：

```bash
# 使用 Swagger Editor（在线）
# 访问 https://editor.swagger.io/
# 将 api-spec.yaml 内容粘贴进去

# 或使用本地工具
npm install -g swagger-ui-watcher
swagger-ui-watcher api-spec.yaml
```

### 2. 生成客户端代码

使用 OpenAPI Generator 生成客户端代码：

```bash
# 安装 OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# 生成 JavaScript/TypeScript 客户端
openapi-generator-cli generate \
  -i api-spec.yaml \
  -g typescript-axios \
  -o ./client

# 生成 Python 客户端
openapi-generator-cli generate \
  -i api-spec.yaml \
  -g python \
  -o ./client-python
```

### 3. API 测试

使用 Postman 导入：
1. 打开 Postman
2. 点击 Import
3. 选择 api-spec.yaml 文件
4. 自动生成所有接口的测试集合

## 前后端协作流程

### 1. API First 开发流程

```
1. 数据库设计完成
   ↓
2. 前后端联合定义 API 规范（本文档）
   ↓
3. 前后端评审确认 API 规范
   ↓
4. 后端按照规范实现接口
   ↓
5. 前端使用 Mock 数据先行开发
   ↓
6. 集成测试和联调
```

### 2. Mock 数据开发

前端可以使用以下工具进行 Mock 开发：

**方案1：使用 json-server**
```bash
npm install -g json-server
json-server --watch mock-db.json --port 3000
```

**方案2：使用 Mockoon**
- 下载 Mockoon 应用
- 导入 api-spec.yaml
- 自动生成 Mock 服务器

**方案3：使用 Axios Mock Adapter**
```javascript
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'

const mock = new MockAdapter(axios)

mock.onGet('/api/personal/products').reply(200, {
  code: 200,
  message: 'success',
  data: {
    items: [...],
    total: 100,
    page: 1,
    page_size: 20,
    total_pages: 5
  }
})
```

## 注意事项

### 1. 安全性
- 所有需要认证的接口都必须携带 Session ID
- 管理端接口需要验证管理员角色
- 敏感操作（删除、重置密码）需要二次确认

### 2. 性能优化
- 列表接口支持分页，避免一次性加载大量数据
- 图片使用缩略图，提高加载速度
- 搜索接口有频率限制，防止滥用

### 3. 错误处理
- 前端需要统一处理 401 错误（跳转登录页）
- 前端需要统一处理 403 错误（显示无权限提示）
- 前端需要统一处理 429 错误（显示频率限制提示）

### 4. 数据一致性
- 订单创建使用事务，确保积分扣除和订单生成的原子性
- 购物车结算后自动清空
- 删除分类时自动移除产品关联

## 下一步

1. ✅ API 规范定义完成
2. ⏭️ 后端工程师按照规范实现接口
3. ⏭️ 前端工程师使用 Mock 数据开发界面
4. ⏭️ 集成测试和联调

## 联系方式

如有疑问，请联系：
- 后端负责人：[后端工程师]
- 前端负责人：[前端工程师]
- 项目经理：[项目经理]
