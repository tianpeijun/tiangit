#!/bin/bash

# 通过 S3 和 User Data 部署后端的替代方案

set -e

INSTANCE_ID="i-070fa152cb90fbff8"
REGION="us-east-1"
PROFILE="global"
S3_BUCKET="awsome-shop-manage-418295705866"

echo "=== 使用 SSM Run Command 部署后端 ==="

# 创建部署脚本
cat > /tmp/deploy-script.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "=== 开始部署 ==="

# 下载代码
echo "下载代码包..."
sudo -u ubuntu aws s3 cp s3://awsome-shop-manage-418295705866/deploy/awsome-shop-backend.tar.gz /tmp/ --region us-east-1

# 创建目录
echo "创建目录..."
sudo mkdir -p /opt/awsome-shop
cd /opt/awsome-shop

# 解压
echo "解压代码..."
sudo tar -xzf /tmp/awsome-shop-backend.tar.gz
sudo chown -R ubuntu:ubuntu /opt/awsome-shop

# 安装依赖
echo "安装依赖..."
sudo -u ubuntu pip3 install -r /opt/awsome-shop/requirements.txt --user

# 初始化数据库
echo "初始化数据库..."
cd /opt/awsome-shop/server
if [ ! -f "/opt/awsome-shop/data/awsome_shop.db" ]; then
    sudo -u ubuntu python3 init_db.py
fi

# 创建服务
echo "创建 systemd 服务..."
cat > /tmp/awsome-shop.service << 'EOF'
[Unit]
Description=AWSome Shop Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/awsome-shop/server
Environment="PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/awsome-shop.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable awsome-shop
sudo systemctl restart awsome-shop

sleep 5
sudo systemctl status awsome-shop --no-pager

echo "测试健康检查..."
curl -f http://localhost:8000/health

echo "=== 部署完成 ==="
DEPLOY_SCRIPT

# 上传脚本到 S3
echo "上传部署脚本到 S3..."
aws s3 cp /tmp/deploy-script.sh s3://${S3_BUCKET}/deploy/ --profile ${PROFILE}

# 使用 SSM 执行
echo "执行部署脚本..."
aws ssm send-command \
    --instance-ids ${INSTANCE_ID} \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "aws s3 cp s3://'${S3_BUCKET}'/deploy/deploy-script.sh /tmp/",
        "chmod +x /tmp/deploy-script.sh",
        "/tmp/deploy-script.sh"
    ]' \
    --region ${REGION} \
    --profile ${PROFILE} \
    --output json

echo "命令已发送，请等待执行完成..."
