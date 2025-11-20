# AWSomeShop 部署状态

## 部署时间
2025-11-20 10:00 AM

## ✅ 已完成的部署

### 1. AWS 基础设施（CDK）- 已完成 ✅

所有 AWS 资源已成功部署到 us-east-1 region：

#### 网络资源
- ✅ VPC（2 个公有子网，跨 2 个可用区）
- ✅ Internet Gateway
- ✅ 安全组（ALB 和 EC2）

#### 前端资源
- ✅ S3 存储桶（员工端）: `awsome-shop-personal-418295705866`
- ✅ S3 存储桶（管理端）: `awsome-shop-manage-418295705866`
- ✅ CloudFront 分发（员工端）: `d2w3kt9fvl0sk8.cloudfront.net`
- ✅ CloudFront 分发（管理端）: `d1vrkuin69xwe2.cloudfront.net`

#### 后端资源
- ✅ EC2 实例: `i-070fa152cb90fbff8`
- ✅ EC2 公网 IP: `13.219.252.200`
- ✅ Application Load Balancer
- ✅ ALB DNS: `Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com`
- ✅ 目标组和健康检查配置

#### 监控资源
- ✅ CloudWatch 日志组: `/aws/ec2/awsome-shop`

## ⏳ 待完成的部署

### 2. 后端代码部署 - 待完成 ⏳

需要将后端代码部署到 EC2 实例。

#### 方式 1：使用 Git（推荐）

```bash
# 1. 将代码推送到 Git 仓库（如 GitHub）
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. SSH 到 EC2（使用 EC2 Instance Connect）
# 在 AWS Console 中：EC2 > Instances > Connect > EC2 Instance Connect

# 3. 在 EC2 上执行
sudo dnf install -y git python3 python3-pip
cd /opt/awsome-shop
git clone https://github.com/your-repo/awsome-shop.git .

# 4. 安装依赖
pip3 install --user -r requirements.txt

# 5. 初始化数据库
cd server
python3 init_db.py

# 6. 启动服务
sudo systemctl enable awsome-shop
sudo systemctl start awsome-shop
sudo systemctl status awsome-shop
```

#### 方式 2：手动上传文件

```bash
# 1. 打包代码
tar -czf awsome-shop-backend.tar.gz server/ requirements.txt

# 2. 上传到 S3
aws s3 cp awsome-shop-backend.tar.gz s3://awsome-shop-manage-418295705866/deploy/ --profile global

# 3. 在 EC2 上下载（需要先给 EC2 IAM 角色添加 S3 权限）
# 或者使用 SCP 直接上传
```

#### 方式 3：使用 AWS Systems Manager Session Manager

```bash
# 在 AWS Console 中：
# Systems Manager > Session Manager > Start session
# 选择实例 i-070fa152cb90fbff8

# 然后执行部署命令
```

### 3. 前端部署 - 待完成 ⏳

#### 步骤 1：配置环境变量

**员工端（front/personal/.env.production）：**
```bash
VUE_APP_API_BASE_URL=http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080
```

**管理端（front/manage/.env.production）：**
```bash
VUE_APP_API_BASE_URL=http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080
```

#### 步骤 2：修改前端代码

确保 `front/personal/src/utils/request.js` 和 `front/manage/src/utils/request.js` 使用环境变量：

```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})
```

#### 步骤 3：构建并部署

```bash
# 员工端
cd front/personal
npm install
npm run build
aws s3 sync dist/ s3://awsome-shop-personal-418295705866/ --delete --profile global

# 管理端
cd ../manage
npm install
npm run build
aws s3 sync dist/ s3://awsome-shop-manage-418295705866/ --delete --profile global
```

## 📋 部署信息汇总

### 访问地址

| 服务 | URL | 状态 |
|------|-----|------|
| 后端 API (直接) | http://13.219.252.200:8000 | ⏳ 待部署 |
| 后端 API (ALB) | http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080 | ⏳ 待部署 |
| 员工端前端 | http://d2w3kt9fvl0sk8.cloudfront.net | ⏳ 待部署 |
| 管理端前端 | http://d1vrkuin69xwe2.cloudfront.net | ⏳ 待部署 |

### 测试账号

**员工账号：**
- 用户名：user1
- 密码：user123

**管理员账号：**
- 用户名：admin
- 密码：admin123

### AWS 资源

| 资源类型 | 资源 ID/名称 | Region |
|---------|-------------|--------|
| VPC | vpc-xxx | us-east-1 |
| EC2 Instance | i-070fa152cb90fbff8 | us-east-1 |
| ALB | Awsome-ALBAE-h0wHn3qk6cf1 | us-east-1 |
| S3 Bucket (员工端) | awsome-shop-personal-418295705866 | us-east-1 |
| S3 Bucket (管理端) | awsome-shop-manage-418295705866 | us-east-1 |
| CloudFront (员工端) | d2w3kt9fvl0sk8.cloudfront.net | Global |
| CloudFront (管理端) | d1vrkuin69xwe2.cloudfront.net | Global |

## 🔧 故障排查

### 检查后端服务状态

```bash
# 使用 EC2 Instance Connect 连接到 EC2
# 然后执行：
sudo systemctl status awsome-shop
sudo journalctl -u awsome-shop -f
```

### 检查 ALB 健康检查

```bash
# 在 AWS Console 中：
# EC2 > Load Balancers > Target Groups > Targets
# 查看健康检查状态
```

### 测试后端 API

```bash
# 直接访问 EC2
curl http://13.219.252.200:8000/health

# 通过 ALB 访问
curl http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080/health
```

### 检查前端部署

```bash
# 检查 S3 存储桶内容
aws s3 ls s3://awsome-shop-personal-418295705866/ --profile global
aws s3 ls s3://awsome-shop-manage-418295705866/ --profile global

# 访问 CloudFront URL
curl http://d2w3kt9fvl0sk8.cloudfront.net
curl http://d1vrkuin69xwe2.cloudfront.net
```

## 📝 下一步操作

1. **部署后端代码**
   - 使用 EC2 Instance Connect 连接到 EC2
   - 克隆代码仓库或上传代码
   - 安装依赖并启动服务

2. **配置前端环境变量**
   - 创建 .env.production 文件
   - 填入 ALB DNS 名称

3. **构建并部署前端**
   - 构建员工端和管理端
   - 上传到对应的 S3 存储桶

4. **验证部署**
   - 测试后端 API
   - 访问前端应用
   - 测试完整流程

## 💰 成本估算

- EC2 t3.small: ~$15/月
- EBS 20GB: ~$2/月
- ALB: ~$16/月
- CloudFront: 按流量计费
- S3: 按存储计费

**预计总成本**: $35-50/月（不含流量费用）

## 🗑️ 清理资源

如果需要删除所有资源：

```bash
cd cdk
export AWS_PROFILE=global
cdk destroy
```

**警告**：这将删除所有资源，包括数据库和图片！

## 📚 相关文档

- [完整部署指南](./DEPLOYMENT.md)
- [CDK 项目说明](./cdk/README.md)
- [快速开始指南](./QUICK_START.md)
- [任务完成总结](./TASK_6_CDK_COMPLETION_SUMMARY.md)
