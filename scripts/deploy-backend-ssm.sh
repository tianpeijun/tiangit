#!/bin/bash

# 使用 AWS Systems Manager Session Manager 部署后端到 EC2
# 不需要 SSH 密钥

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

INSTANCE_ID="i-070fa152cb90fbff8"
REGION="us-east-1"
PROFILE="global"

echo -e "${GREEN}开始部署后端代码到 EC2...${NC}"
echo -e "Instance ID: ${YELLOW}${INSTANCE_ID}${NC}"
echo -e "Region: ${YELLOW}${REGION}${NC}"

# 检查 AWS CLI 和 Session Manager 插件
if ! command -v aws &> /dev/null; then
    echo -e "${RED}错误：未安装 AWS CLI${NC}"
    exit 1
fi

# 打包后端代码
echo -e "${YELLOW}打包后端代码...${NC}"
tar -czf /tmp/awsome-shop-backend.tar.gz \
    --exclude='server/__pycache__' \
    --exclude='server/logs/*' \
    --exclude='server/.DS_Store' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='cdk/node_modules' \
    --exclude='cdk/cdk.out' \
    --exclude='front/*/node_modules' \
    server/ \
    data/ \
    static/ \
    requirements.txt

echo -e "${YELLOW}上传代码到 S3...${NC}"
S3_BUCKET="awsome-shop-manage-418295705866"
aws s3 cp /tmp/awsome-shop-backend.tar.gz s3://${S3_BUCKET}/deploy/ --profile ${PROFILE}

echo -e "${YELLOW}在 EC2 上部署代码...${NC}"

# 使用 SSM 执行部署命令
aws ssm send-command \
    --instance-ids ${INSTANCE_ID} \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "set -e",
        "echo \"下载代码包...\"",
        "aws s3 cp s3://'${S3_BUCKET}'/deploy/awsome-shop-backend.tar.gz /tmp/",
        "echo \"创建目录...\"",
        "sudo mkdir -p /opt/awsome-shop",
        "cd /opt/awsome-shop",
        "echo \"解压代码...\"",
        "sudo tar -xzf /tmp/awsome-shop-backend.tar.gz",
        "sudo chown -R ubuntu:ubuntu /opt/awsome-shop",
        "echo \"安装 Python 依赖...\"",
        "pip3 install -r requirements.txt --user",
        "echo \"初始化数据库...\"",
        "cd /opt/awsome-shop/server",
        "if [ ! -f \"/opt/awsome-shop/data/awsome_shop.db\" ]; then python3 init_db.py; fi",
        "echo \"创建 systemd 服务文件...\"",
        "sudo tee /etc/systemd/system/awsome-shop.service > /dev/null <<EOF
[Unit]
Description=AWSome Shop Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/awsome-shop/server
Environment=\"PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin\"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF",
        "echo \"重启服务...\"",
        "sudo systemctl daemon-reload",
        "sudo systemctl enable awsome-shop",
        "sudo systemctl restart awsome-shop",
        "sleep 5",
        "echo \"检查服务状态...\"",
        "sudo systemctl status awsome-shop --no-pager || true",
        "echo \"测试健康检查...\"",
        "curl -f http://localhost:8000/health || echo \"健康检查失败\"",
        "echo \"后端部署完成！\""
    ]' \
    --region ${REGION} \
    --profile ${PROFILE} \
    --output json > /tmp/ssm-command.json

COMMAND_ID=$(cat /tmp/ssm-command.json | grep -o '"CommandId": "[^"]*"' | cut -d'"' -f4)
echo -e "${YELLOW}命令 ID: ${COMMAND_ID}${NC}"
echo -e "${YELLOW}等待命令执行完成...${NC}"

# 等待命令完成
sleep 10

# 获取命令输出
echo -e "${YELLOW}获取执行结果...${NC}"
aws ssm get-command-invocation \
    --command-id ${COMMAND_ID} \
    --instance-id ${INSTANCE_ID} \
    --region ${REGION} \
    --profile ${PROFILE} \
    --output text \
    --query 'StandardOutputContent'

# 清理临时文件
rm /tmp/awsome-shop-backend.tar.gz
rm /tmp/ssm-command.json

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}后端部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "测试 API: ${YELLOW}curl http://13.219.252.200:8000/health${NC}"
echo -e "通过 ALB: ${YELLOW}curl http://Awsome-ALBAE-h0wHn3qk6cf1-60833011.us-east-1.elb.amazonaws.com:8080/health${NC}"
