# AWSomeShop 部署指南

本文档提供完整的部署步骤，从零开始将 AWSomeShop 部署到 AWS。

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户                                  │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             │ HTTP                       │ HTTP
             │                            │
┌────────────▼──────────┐    ┌───────────▼──────────────────┐
│  CloudFront (员工端)   │    │  CloudFront (管理端)          │
│  *.cloudfront.net     │    │  *.cloudfront.net            │
└────────────┬──────────┘    └───────────┬──────────────────┘
             │                            │
             │                            │
┌────────────▼──────────┐    ┌───────────▼──────────────────┐
│  S3 (员工端静态文件)   │    │  S3 (管理端静态文件)          │
└───────────────────────┘    └──────────────────────────────┘
             │                            │
             │ API 调用 (HTTP:8080)       │
             └────────────┬───────────────┘
                          │
                ┌─────────▼──────────┐
                │  Application       │
                │  Load Balancer     │
                │  (Port 8080)       │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │  EC2 Instance      │
                │  (t3.small)        │
                │  FastAPI (8000)    │
                │  ┌──────────────┐  │
                │  │ SQLite DB    │  │
                │  │ (EBS 20GB)   │  │
                │  └──────────────┘  │
                │  ┌──────────────┐  │
                │  │ 产品图片      │  │
                │  │ (本地存储)    │  │
                │  └──────────────┘  │
                └────────────────────┘
```

## 前置条件

### 1. 本地环境

- **操作系统**：macOS / Linux / Windows (WSL)
- **Node.js**：v20.x 或 v22.x
- **Python**：3.10+
- **AWS CLI**：2.x
- **AWS CDK**：2.x
- **Git**：2.x

### 2. AWS 账户

- 有效的 AWS 账户
- IAM 用户具有以下权限：
  - EC2 完全访问
  - VPC 完全访问
  - S3 完全访问
  - CloudFront 完全访问
  - ELB 完全访问
  - IAM 角色创建权限
  - CloudFormation 完全访问

### 3. SSH 密钥对

在 AWS EC2 控制台创建密钥对（us-east-1 region）：
1. 进入 EC2 控制台
2. 左侧菜单选择 "Key Pairs"
3. 点击 "Create key pair"
4. 名称：awsome-shop-key
5. 类型：RSA
6. 格式：.pem
7. 下载并保存到 ~/.ssh/awsome-shop-key.pem
8. 设置权限：`chmod 400 ~/.ssh/awsome-shop-key.pem`

## 部署步骤

### 步骤 1：配置 AWS 凭证

```bash
# 配置 AWS CLI
aws configure --profile global
# Access Key ID: 输入你的 Access Key
# Secret Access Key: 输入你的 Secret Key
# Default region: us-east-1
# Default output format: json

# 验证配置
aws sts get-caller-identity --profile global
```

### 步骤 2：安装依赖

```bash
# 安装 CDK
npm install -g aws-cdk

# 验证安装
cdk --version

# 安装项目依赖
cd cdk
npm install
```

### 步骤 3：Bootstrap CDK（首次部署）

```bash
cd cdk
export AWS_PROFILE=global

# 获取账户 ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $ACCOUNT_ID"

# Bootstrap
cdk bootstrap aws://${ACCOUNT_ID}/us-east-1
```

### 步骤 4：部署基础设施

```bash
# 方式 1：使用部署脚本（推荐）
./deploy.sh deploy

# 方式 2：手动部署
cdk deploy
```

部署大约需要 10-15 分钟。完成后会输出：
- ALB DNS 名称
- CloudFront 域名（员工端和管理端）
- EC2 实例 ID 和公网 IP
- S3 存储桶名称

**保存这些输出信息，后续步骤需要使用！**

### 步骤 5：部署后端代码到 EC2

#### 方式 1：使用部署脚本（推荐）

```bash
cd cdk
./deploy-backend-to-ec2.sh <EC2_PUBLIC_IP> ~/.ssh/awsome-shop-key.pem
```

#### 方式 2：手动部署

```bash
# SSH 到 EC2
ssh -i ~/.ssh/awsome-shop-key.pem ubuntu@<EC2_PUBLIC_IP>

# 在 EC2 上执行
cd /opt/awsome-shop

# 从 Git 克隆代码（推荐）
git clone https://github.com/your-repo/awsome-shop.git .

# 或者从本地上传（在本地执行）
# scp -i ~/.ssh/awsome-shop-key.pem -r ../server ubuntu@<EC2_PUBLIC_IP>:/opt/awsome-shop/

# 安装依赖
cd server
pip3 install -r requirements.txt

# 初始化数据库
python3 init_db.py

# 启动服务
sudo systemctl enable awsome-shop
sudo systemctl start awsome-shop

# 检查状态
sudo systemctl status awsome-shop

# 查看日志
sudo journalctl -u awsome-shop -f
```

#### 验证后端

```bash
# 测试健康检查
curl http://<EC2_PUBLIC_IP>:8000/health

# 测试通过 ALB
curl http://<ALB_DNS_NAME>:8080/health
```

### 步骤 6：配置前端环境变量

```bash
# 员工端
cd front/personal
cp .env.production.template .env.production

# 编辑 .env.production
# VUE_APP_API_BASE_URL=http://<ALB_DNS_NAME>:8080

# 管理端
cd ../manage
cp .env.production.template .env.production

# 编辑 .env.production
# VUE_APP_API_BASE_URL=http://<ALB_DNS_NAME>:8080
```

### 步骤 7：修改前端代码支持环境变量

**front/personal/src/utils/request.js：**
```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})
```

**front/manage/src/utils/request.js：**
```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})
```

### 步骤 8：构建并部署前端

#### 方式 1：使用部署脚本（推荐）

```bash
cd cdk
./deploy.sh update-frontend
```

#### 方式 2：手动部署

```bash
# 员工端
cd front/personal
npm install
npm run build

# 上传到 S3
aws s3 sync dist/ s3://<PERSONAL_S3_BUCKET>/ --delete --profile global

# 管理端
cd ../manage
npm install
npm run build

# 上传到 S3
aws s3 sync dist/ s3://<MANAGE_S3_BUCKET>/ --delete --profile global
```

### 步骤 9：验证部署

1. **验证后端 API**
   ```bash
   curl http://<ALB_DNS_NAME>:8080/health
   # 应该返回：{"status":"ok","version":"1.0.0"}
   ```

2. **访问员工端**
   - 打开浏览器访问：`http://<PERSONAL_CLOUDFRONT_URL>`
   - 使用测试账号登录：user1 / user123

3. **访问管理端**
   - 打开浏览器访问：`http://<MANAGE_CLOUDFRONT_URL>`
   - 使用管理员账号登录：admin / admin123

4. **测试完整流程**
   - 员工端：浏览产品 → 加入购物车 → 兑换
   - 管理端：创建产品 → 上传图片 → 发放积分

## 更新部署

### 更新后端

```bash
# SSH 到 EC2
ssh -i ~/.ssh/awsome-shop-key.pem ubuntu@<EC2_PUBLIC_IP>

# 拉取最新代码
cd /opt/awsome-shop
git pull

# 重启服务
sudo systemctl restart awsome-shop

# 查看日志
sudo journalctl -u awsome-shop -f
```

### 更新前端

```bash
cd cdk
./deploy.sh update-frontend
```

## 监控和维护

### 查看日志

```bash
# 后端日志
ssh -i ~/.ssh/awsome-shop-key.pem ubuntu@<EC2_PUBLIC_IP>
sudo journalctl -u awsome-shop -f

# CloudWatch 日志
aws logs tail /aws/ec2/awsome-shop --follow --profile global
```

### 监控指标

在 AWS Console 中查看：
- EC2 > Instances > Monitoring（CPU、网络、磁盘）
- EC2 > Load Balancers > Monitoring（请求数、延迟）
- CloudFront > Distributions > Monitoring（请求数、错误率）

### 备份数据

```bash
# 手动备份数据库
ssh -i ~/.ssh/awsome-shop-key.pem ubuntu@<EC2_PUBLIC_IP>
sudo cp /opt/awsome-shop/data/awsome_shop.db /opt/awsome-shop/data/awsome_shop.db.backup

# 下载到本地
scp -i ~/.ssh/awsome-shop-key.pem \
  ubuntu@<EC2_PUBLIC_IP>:/opt/awsome-shop/data/awsome_shop.db \
  ./backup/awsome_shop_$(date +%Y%m%d).db
```

## 故障排查

### 后端服务无法启动

```bash
# 检查服务状态
sudo systemctl status awsome-shop

# 查看详细日志
sudo journalctl -u awsome-shop -n 100 --no-pager

# 检查端口占用
sudo netstat -tlnp | grep 8000

# 手动启动测试
cd /opt/awsome-shop/server
python3 main.py
```

### ALB 健康检查失败

1. 检查 EC2 实例状态
2. 检查安全组规则
3. 检查后端服务是否运行
4. 测试 /health 端点

### 前端无法访问

1. 检查 S3 存储桶内容
2. 检查 CloudFront 分发状态
3. 清除浏览器缓存
4. 检查浏览器控制台错误

### 前端无法调用 API

1. 检查 .env.production 配置
2. 检查浏览器网络请求
3. 检查 CORS 配置
4. 检查 ALB 和 EC2 状态

## 销毁资源

```bash
cd cdk
./deploy.sh destroy

# 或手动销毁
cdk destroy
```

**警告**：销毁前请确保已备份重要数据！

## 成本估算

- EC2 t3.small：约 $15/月
- EBS 20GB：约 $2/月
- ALB：约 $16/月
- CloudFront：按流量计费
- S3：按存储计费

**总计**：约 $35-50/月（不含流量费用）

## 安全建议

1. 定期更新系统和依赖
2. 使用强密码
3. 限制 SSH 访问 IP
4. 启用 CloudWatch 告警
5. 定期备份数据
6. 审查 IAM 权限

## 支持

如有问题，请查看：
- [CDK 文档](https://docs.aws.amazon.com/cdk/)
- [项目 README](./README.md)
- [GitHub Issues](https://github.com/your-repo/issues)
