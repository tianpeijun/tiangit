# AWSomeShop CDK 部署指南

## 架构概述

本项目使用 AWS CDK 部署以下资源：

### 前端（CloudFront + S3）
- **员工端**：CloudFront 分发 + S3 存储桶
- **管理端**：CloudFront 分发 + S3 存储桶

### 后端（ALB + EC2）
- **EC2 实例**：t3.small，Ubuntu 22.04 LTS
- **Application Load Balancer**：监听端口 8080
- **EBS 卷**：20GB gp3，存储数据库和图片

### 网络
- **VPC**：2 个公有子网，跨 2 个可用区
- **安全组**：ALB（8080）、EC2（8000、22）

## 前置条件

1. **安装 AWS CLI**
   ```bash
   # macOS
   brew install awscli
   
   # 或下载安装包
   # https://aws.amazon.com/cli/
   ```

2. **配置 AWS 凭证**
   ```bash
   aws configure --profile global
   # 输入 Access Key ID
   # 输入 Secret Access Key
   # Region: us-east-1
   # Output format: json
   ```

3. **安装 Node.js 和 npm**
   ```bash
   # 需要 Node.js 20.x 或 22.x
   node --version
   npm --version
   ```

4. **安装 AWS CDK**
   ```bash
   npm install -g aws-cdk
   cdk --version
   ```

## 部署步骤

### 1. Bootstrap CDK（首次部署）

```bash
cd cdk
export AWS_PROFILE=global
cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

将 `ACCOUNT-ID` 替换为你的 AWS 账户 ID。

### 2. 合成 CloudFormation 模板

```bash
cdk synth
```

这会生成 CloudFormation 模板并显示在终端。

### 3. 部署堆栈

```bash
cdk deploy
```

部署过程大约需要 10-15 分钟。部署完成后，会输出以下信息：

- **ALBDnsName**：后端 API 地址（例如：http://awsome-alb-xxx.us-east-1.elb.amazonaws.com:8080）
- **PersonalCloudFrontURL**：员工端访问地址
- **ManageCloudFrontURL**：管理端访问地址
- **EC2InstanceId**：EC2 实例 ID
- **EC2PublicIP**：EC2 公网 IP
- **PersonalS3Bucket**：员工端 S3 存储桶名称
- **ManageS3Bucket**：管理端 S3 存储桶名称

### 4. 部署后端代码到 EC2

```bash
# SSH 到 EC2 实例
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# 上传后端代码
# 方式 1：使用 scp
scp -i your-key.pem -r ../server ubuntu@<EC2_PUBLIC_IP>:/opt/awsome-shop/

# 方式 2：使用 git（推荐）
cd /opt/awsome-shop
git clone <your-repo-url> server
cd server

# 安装 Python 依赖
pip3 install -r requirements.txt

# 初始化数据库
python3 init_db.py

# 启动服务
sudo systemctl enable awsome-shop
sudo systemctl start awsome-shop

# 检查服务状态
sudo systemctl status awsome-shop

# 查看日志
sudo journalctl -u awsome-shop -f
```

### 5. 配置前端环境变量

在部署前端之前，需要配置 API 地址。

**员工端（front/personal/.env.production）：**
```bash
VUE_APP_API_BASE_URL=http://<ALB_DNS_NAME>:8080
```

**管理端（front/manage/.env.production）：**
```bash
VUE_APP_API_BASE_URL=http://<ALB_DNS_NAME>:8080
```

将 `<ALB_DNS_NAME>` 替换为 CDK 输出的 ALB DNS 名称。

### 6. 修改前端代码以支持环境变量

**修改 front/personal/src/utils/request.js：**
```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})
```

**修改 front/manage/src/utils/request.js：**
```javascript
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000
})
```

### 7. 构建并部署前端

```bash
# 构建员工端
cd front/personal
npm run build

# 上传到 S3
aws s3 sync dist/ s3://<PERSONAL_S3_BUCKET>/ --profile global

# 使 CloudFront 缓存失效
aws cloudfront create-invalidation \
  --distribution-id <PERSONAL_DISTRIBUTION_ID> \
  --paths "/*" \
  --profile global

# 构建管理端
cd ../manage
npm run build

# 上传到 S3
aws s3 sync dist/ s3://<MANAGE_S3_BUCKET>/ --profile global

# 使 CloudFront 缓存失效
aws cloudfront create-invalidation \
  --distribution-id <MANAGE_DISTRIBUTION_ID> \
  --paths "/*" \
  --profile global
```

### 8. 验证部署

1. **验证后端 API**
   ```bash
   curl http://<ALB_DNS_NAME>:8080/health
   ```

2. **访问员工端**
   打开浏览器访问：`http://<PERSONAL_CLOUDFRONT_URL>`

3. **访问管理端**
   打开浏览器访问：`http://<MANAGE_CLOUDFRONT_URL>`

## 更新部署

### 更新后端代码

```bash
# SSH 到 EC2
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# 拉取最新代码
cd /opt/awsome-shop/server
git pull

# 重启服务
sudo systemctl restart awsome-shop
```

### 更新前端代码

```bash
# 重新构建
cd front/personal
npm run build
aws s3 sync dist/ s3://<PERSONAL_S3_BUCKET>/ --profile global
aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*" --profile global

# 同样操作管理端
cd ../manage
npm run build
aws s3 sync dist/ s3://<MANAGE_S3_BUCKET>/ --profile global
aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*" --profile global
```

## 销毁资源

```bash
cd cdk
export AWS_PROFILE=global
cdk destroy
```

**注意**：销毁前请确保已备份重要数据。

## 监控和日志

### CloudWatch 日志

```bash
# 查看 EC2 日志
aws logs tail /aws/ec2/awsome-shop --follow --profile global
```

### ALB 健康检查

```bash
# 在 AWS Console 中查看
# EC2 > Load Balancers > Target Groups > Targets
```

### EC2 实例监控

```bash
# 在 AWS Console 中查看
# EC2 > Instances > Monitoring
```

## 故障排查

### 后端服务无法启动

```bash
# 检查服务状态
sudo systemctl status awsome-shop

# 查看日志
sudo journalctl -u awsome-shop -n 100

# 检查端口占用
sudo netstat -tlnp | grep 8000
```

### ALB 健康检查失败

1. 检查 EC2 安全组是否允许 ALB 访问 8000 端口
2. 检查后端服务是否正常运行
3. 检查 /health 端点是否可访问

### 前端无法访问

1. 检查 S3 存储桶是否有文件
2. 检查 CloudFront 分发状态
3. 检查浏览器控制台错误

### 前端无法调用 API

1. 检查 .env.production 文件是否正确配置
2. 检查前端代码是否正确读取环境变量
3. 检查浏览器控制台网络请求
4. 检查 CORS 配置

## 成本估算

- **EC2 t3.small**：约 $0.0208/小时 = $15/月
- **EBS 20GB gp3**：约 $1.6/月
- **ALB**：约 $16/月
- **CloudFront**：按流量计费，约 $0.085/GB
- **S3**：按存储和请求计费，约 $0.023/GB

**总计**：约 $35-50/月（不含流量费用）

## 安全建议

1. **使用 SSH 密钥对**：不要使用密码登录 EC2
2. **限制 SSH 访问**：只允许特定 IP 访问 22 端口
3. **定期更新系统**：`sudo apt-get update && sudo apt-get upgrade`
4. **启用 CloudWatch 告警**：监控 CPU、内存、磁盘使用率
5. **定期备份数据**：使用 EBS 快照备份数据库

## 支持

如有问题，请查看：
- [AWS CDK 文档](https://docs.aws.amazon.com/cdk/)
- [AWS CloudFormation 文档](https://docs.aws.amazon.com/cloudformation/)
- [项目 GitHub Issues](https://github.com/your-repo/issues)
