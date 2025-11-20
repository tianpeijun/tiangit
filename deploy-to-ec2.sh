#!/bin/bash

# 部署后端到 EC2 的脚本
# 使用 EC2 Instance Connect

set -e

EC2_IP="13.219.252.200"
INSTANCE_ID="i-070fa152cb90fbff8"
REGION="us-east-1"

echo "正在上传后端代码到 EC2..."

# 使用 scp 通过 EC2 Instance Connect
aws ec2-instance-connect send-ssh-public-key \
    --instance-id ${INSTANCE_ID} \
    --instance-os-user ec2-user \
    --ssh-public-key file://~/.ssh/id_rsa.pub \
    --availability-zone ${REGION}a \
    --region ${REGION} \
    --profile global

# 上传文件
scp -o "IdentitiesOnly=yes" \
    -o "StrictHostKeyChecking=no" \
    /tmp/awsome-shop-backend.tar.gz \
    ec2-user@${EC2_IP}:/tmp/

# 执行部署命令
ssh -o "IdentitiesOnly=yes" \
    -o "StrictHostKeyChecking=no" \
    ec2-user@${EC2_IP} << 'ENDSSH'
set -e

echo "解压代码..."
sudo mkdir -p /opt/awsome-shop
cd /opt/awsome-shop
sudo tar -xzf /tmp/awsome-shop-backend.tar.gz
sudo chown -R ec2-user:ec2-user /opt/awsome-shop

echo "创建目录..."
sudo mkdir -p /opt/awsome-shop/data
sudo mkdir -p /opt/awsome-shop/static/images
sudo chown -R ec2-user:ec2-user /opt/awsome-shop

echo "安装 Python 依赖..."
cd /opt/awsome-shop
pip3 install --user -r requirements.txt

echo "初始化数据库..."
cd /opt/awsome-shop/server
python3 init_db.py

echo "启动服务..."
sudo systemctl enable awsome-shop
sudo systemctl start awsome-shop

echo "检查服务状态..."
sleep 3
sudo systemctl status awsome-shop --no-pager

echo "部署完成！"
ENDSSH

echo "后端部署完成！"
echo "测试 API: curl http://${EC2_IP}:8000/health"
