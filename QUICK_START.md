# AWSomeShop 快速开始指南

## 5 分钟快速部署

### 前置条件
- AWS 账户
- AWS CLI 已配置（profile: global）
- Node.js 20.x 或 22.x
- SSH 密钥对（awsome-shop-key.pem）

### 步骤 1：Bootstrap CDK（首次）

```bash
cd cdk
export AWS_PROFILE=global
./deploy.sh bootstrap
```

### 步骤 2：部署基础设施

```bash
./deploy.sh deploy
```

等待 10-15 分钟，记录输出的：
- ALB DNS 名称
- CloudFront 域名（员工端和管理端）
- EC2 公网 IP

### 步骤 3：部署后端

```bash
./deploy-backend-to-ec2.sh <EC2_PUBLIC_IP> ~/.ssh/awsome-shop-key.pem
```

### 步骤 4：配置前端

```bash
# 员工端
cd ../front/personal
cp .env.production.template .env.production
# 编辑 .env.production，填入 ALB DNS 名称

# 管理端
cd ../manage
cp .env.production.template .env.production
# 编辑 .env.production，填入 ALB DNS 名称
```

### 步骤 5：部署前端

```bash
cd ../../cdk
./deploy.sh update-frontend
```

### 步骤 6：访问应用

- **员工端**：http://<PERSONAL_CLOUDFRONT_URL>
  - 账号：user1 / user123
  
- **管理端**：http://<MANAGE_CLOUDFRONT_URL>
  - 账号：admin / admin123

## 常用命令

```bash
# 查看后端日志
ssh -i ~/.ssh/awsome-shop-key.pem ec2-user@<EC2_IP>
sudo journalctl -u awsome-shop -f

# 更新后端
ssh -i ~/.ssh/awsome-shop-key.pem ec2-user@<EC2_IP>
cd /opt/awsome-shop/server
git pull
sudo systemctl restart awsome-shop

# 更新前端
cd cdk
./deploy.sh update-frontend

# 销毁资源
cd cdk
./deploy.sh destroy
```

## 故障排查

### 后端无法访问
```bash
# 检查服务状态
ssh -i ~/.ssh/awsome-shop-key.pem ec2-user@<EC2_IP>
sudo systemctl status awsome-shop

# 查看日志
sudo journalctl -u awsome-shop -n 50
```

### 前端无法调用 API
1. 检查 .env.production 配置
2. 检查浏览器控制台网络请求
3. 确认 ALB 健康检查通过

## 详细文档

- [完整部署指南](./DEPLOYMENT.md)
- [CDK 项目说明](./cdk/README.md)
- [任务完成总结](./TASK_6_CDK_COMPLETION_SUMMARY.md)
