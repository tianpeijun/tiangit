# 完成 AWSomeShop 部署

## 当前状态

✅ AWS 基础设施已部署完成
⏳ 后端代码需要部署到 EC2
⏳ 前端需要构建并上传到 S3

## 快速完成部署（3 个步骤）

### 步骤 1：部署后端到 EC2

#### 选项 A：使用 AWS Console（最简单）

1. 打开 AWS Console：https://console.aws.amazon.com/ec2/
2. 进入 EC2 > Instances
3. 选择实例 `i-070fa152cb90fbff8`
4. 点击 "Connect" > "EC2 Instance Connect" > "Connect"
5. 在浏览器终端中执行：

```bash
# 安装依赖
sudo dnf install -y git python3-pip

# 克隆代码（替换为你的仓库地址）
cd /opt/awsome-shop
sudo git clone https://github.com/tianpeijun/tiangit.git .
sudo chown -R ec2-user:ec2-user /opt/awsome-shop

# 安装 Python 依赖
pip3 install --user -r requirements.txt

# 初始化数据库
cd server
python3 init_db.py

# 启动服务
sudo systemctl enable awsome-shop
sudo systemctl start awsome-shop

# 检查状态
sudo systemctl status awsome-shop
```

#### 选项 B：使用本地终端

```bash
# 如果你有 SSH 密钥
ssh -i ~/.ssh/your-key.pem ec2-user@13.219.252.200

# 然后执行上面的命令
```

### 步骤 2：配置并部署前端

#### 2.1 配置环境变量

```bash
# 员工端
cat > front/personal/.env.production << EOF
VUE_APP_API_BASE_URL=http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080
EOF

# 管理端
cat > front/manage/.env.production << EOF
VUE_APP_API_BASE_URL=http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080
EOF
```

#### 2.2 修改前端代码（如果还没改）

确保 `front/personal/src/utils/request.js` 和 `front/manage/src/utils/request.js` 中：

```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})
```

#### 2.3 构建并部署

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

### 步骤 3：验证部署

#### 3.1 测试后端 API

```bash
# 测试健康检查
curl http://13.219.252.200:8000/health

# 通过 ALB 测试
curl http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080/health

# 应该返回：{"status":"ok","version":"1.0.0"}
```

#### 3.2 访问前端应用

**员工端：**
- URL: http://d2w3kt9fvl0sk8.cloudfront.net
- 账号：user1 / user123

**管理端：**
- URL: http://d1vrkuin69xwe2.cloudfront.net
- 账号：admin / admin123

#### 3.3 测试完整流程

1. **员工端测试**：
   - 登录
   - 浏览产品
   - 加入购物车
   - 兑换产品
   - 查看订单

2. **管理端测试**：
   - 登录
   - 创建产品
   - 上传图片
   - 发放积分
   - 查看日志

## 常见问题

### Q1: 后端服务无法启动

```bash
# 查看日志
sudo journalctl -u awsome-shop -n 50

# 检查端口
sudo netstat -tlnp | grep 8000

# 手动启动测试
cd /opt/awsome-shop/server
python3 main.py
```

### Q2: ALB 健康检查失败

1. 检查 EC2 实例状态
2. 检查安全组规则
3. 确认后端服务在 8000 端口运行
4. 测试 /health 端点

### Q3: 前端无法调用 API

1. 检查 .env.production 配置
2. 检查浏览器控制台网络请求
3. 确认 ALB 和 EC2 正常运行
4. 检查 CORS 配置

### Q4: CloudFront 显示 403 错误

1. 检查 S3 存储桶是否有文件
2. 等待 CloudFront 缓存更新（可能需要几分钟）
3. 清除 CloudFront 缓存：
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id <DISTRIBUTION_ID> \
     --paths "/*" \
     --profile global
   ```

## 一键部署脚本

如果你想自动化整个过程，可以使用这个脚本：

```bash
#!/bin/bash
set -e

echo "=== 部署前端 ==="

# 配置环境变量
ALB_DNS="Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com"

# 员工端
cd front/personal
echo "VUE_APP_API_BASE_URL=http://${ALB_DNS}:8080" > .env.production
npm install
npm run build
aws s3 sync dist/ s3://awsome-shop-personal-418295705866/ --delete --profile global

# 管理端
cd ../manage
echo "VUE_APP_API_BASE_URL=http://${ALB_DNS}:8080" > .env.production
npm install
npm run build
aws s3 sync dist/ s3://awsome-shop-manage-418295705866/ --delete --profile global

echo "=== 部署完成 ==="
echo "员工端: http://d2w3kt9fvl0sk8.cloudfront.net"
echo "管理端: http://d1vrkuin69xwe2.cloudfront.net"
```

## 监控和维护

### 查看日志

```bash
# 后端日志
ssh ec2-user@13.219.252.200
sudo journalctl -u awsome-shop -f

# CloudWatch 日志
aws logs tail /aws/ec2/awsome-shop --follow --profile global
```

### 更新代码

```bash
# 后端更新
ssh ec2-user@13.219.252.200
cd /opt/awsome-shop
git pull
sudo systemctl restart awsome-shop

# 前端更新
# 重新构建并上传到 S3
```

### 备份数据

```bash
# 备份数据库
ssh ec2-user@13.219.252.200
sudo cp /opt/awsome-shop/data/awsome_shop.db /opt/awsome-shop/data/backup_$(date +%Y%m%d).db

# 下载到本地
scp ec2-user@13.219.252.200:/opt/awsome-shop/data/awsome_shop.db ./backup/
```

## 成功标志

当你看到以下情况时，说明部署成功：

✅ 后端 API 返回健康检查：`{"status":"ok"}`
✅ ALB 目标组健康检查通过
✅ 员工端可以正常登录和浏览产品
✅ 管理端可以正常管理产品和用户
✅ 前后端可以正常通信

## 需要帮助？

查看详细文档：
- [部署状态](./DEPLOYMENT_STATUS.md)
- [完整部署指南](./DEPLOYMENT.md)
- [故障排查](./cdk/README.md#故障排查)
