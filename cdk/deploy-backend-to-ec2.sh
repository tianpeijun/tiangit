#!/bin/bash

# 后端代码部署到 EC2 脚本
# 使用方法：./deploy-backend-to-ec2.sh <EC2_PUBLIC_IP> <SSH_KEY_PATH>

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ "$#" -ne 2 ]; then
    echo "使用方法: $0 <EC2_PUBLIC_IP> <SSH_KEY_PATH>"
    echo "示例: $0 54.123.45.67 ~/.ssh/my-key.pem"
    exit 1
fi

EC2_IP=$1
SSH_KEY=$2

echo -e "${GREEN}开始部署后端代码到 EC2...${NC}"
echo -e "EC2 IP: ${YELLOW}${EC2_IP}${NC}"
echo -e "SSH Key: ${YELLOW}${SSH_KEY}${NC}"

# 检查 SSH 密钥文件是否存在
if [ ! -f "${SSH_KEY}" ]; then
    echo -e "${RED}错误：SSH 密钥文件不存在: ${SSH_KEY}${NC}"
    exit 1
fi

# 打包后端代码
echo -e "${YELLOW}打包后端代码...${NC}"
cd ..
tar -czf /tmp/awsome-shop-server.tar.gz \
    --exclude='server/__pycache__' \
    --exclude='server/logs/*' \
    --exclude='server/.DS_Store' \
    server/ \
    data/ \
    static/ \
    requirements.txt

# 上传到 EC2
echo -e "${YELLOW}上传代码到 EC2...${NC}"
scp -i ${SSH_KEY} -o StrictHostKeyChecking=no \
    /tmp/awsome-shop-server.tar.gz \
    ubuntu@${EC2_IP}:/tmp/

# 在 EC2 上部署
echo -e "${YELLOW}在 EC2 上部署代码...${NC}"
ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ubuntu@${EC2_IP} << 'ENDSSH'
set -e

# 解压代码
cd /opt/awsome-shop
sudo tar -xzf /tmp/awsome-shop-server.tar.gz
sudo chown -R ubuntu:ubuntu /opt/awsome-shop

# 安装 Python 依赖
cd /opt/awsome-shop/server
pip3 install -r ../requirements.txt

# 初始化数据库（如果不存在）
if [ ! -f "/opt/awsome-shop/data/awsome_shop.db" ]; then
    echo "初始化数据库..."
    python3 init_db.py
fi

# 重启服务
sudo systemctl restart awsome-shop

# 检查服务状态
sleep 3
sudo systemctl status awsome-shop --no-pager

echo "后端部署完成！"
ENDSSH

# 清理临时文件
rm /tmp/awsome-shop-server.tar.gz

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}后端部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "查看日志: ${YELLOW}ssh -i ${SSH_KEY} ubuntu@${EC2_IP} 'sudo journalctl -u awsome-shop -f'${NC}"
echo -e "测试 API: ${YELLOW}curl http://${EC2_IP}:8000/health${NC}"
