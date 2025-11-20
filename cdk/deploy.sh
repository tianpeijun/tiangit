#!/bin/bash

# AWSomeShop 部署脚本
# 使用方法：./deploy.sh [bootstrap|deploy|destroy|update-frontend]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 AWS Profile
export AWS_PROFILE=global

echo -e "${GREEN}使用 AWS Profile: ${AWS_PROFILE}${NC}"
echo -e "${GREEN}部署 Region: us-east-1${NC}"

# 获取 AWS 账户 ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile ${AWS_PROFILE})
echo -e "${GREEN}AWS 账户 ID: ${ACCOUNT_ID}${NC}"

case "$1" in
  bootstrap)
    echo -e "${YELLOW}开始 Bootstrap CDK...${NC}"
    cdk bootstrap aws://${ACCOUNT_ID}/us-east-1
    echo -e "${GREEN}Bootstrap 完成！${NC}"
    ;;
    
  deploy)
    echo -e "${YELLOW}开始部署 CDK 堆栈...${NC}"
    cdk deploy --require-approval never
    echo -e "${GREEN}CDK 堆栈部署完成！${NC}"
    
    echo -e "${YELLOW}获取输出信息...${NC}"
    ALB_DNS=$(aws cloudformation describe-stacks \
      --stack-name AwsomeShopStack \
      --query 'Stacks[0].Outputs[?OutputKey==`ALBDnsName`].OutputValue' \
      --output text \
      --region us-east-1 \
      --profile ${AWS_PROFILE})
    
    PERSONAL_CF=$(aws cloudformation describe-stacks \
      --stack-name AwsomeShopStack \
      --query 'Stacks[0].Outputs[?OutputKey==`PersonalCloudFrontURL`].OutputValue' \
      --output text \
      --region us-east-1 \
      --profile ${AWS_PROFILE})
    
    MANAGE_CF=$(aws cloudformation describe-stacks \
      --stack-name AwsomeShopStack \
      --query 'Stacks[0].Outputs[?OutputKey==`ManageCloudFrontURL`].OutputValue' \
      --output text \
      --region us-east-1 \
      --profile ${AWS_PROFILE})
    
    EC2_IP=$(aws cloudformation describe-stacks \
      --stack-name AwsomeShopStack \
      --query 'Stacks[0].Outputs[?OutputKey==`EC2PublicIP`].OutputValue' \
      --output text \
      --region us-east-1 \
      --profile ${AWS_PROFILE})
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}部署信息：${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "ALB DNS (后端 API): ${YELLOW}${ALB_DNS}${NC}"
    echo -e "员工端 URL: ${YELLOW}${PERSONAL_CF}${NC}"
    echo -e "管理端 URL: ${YELLOW}${MANAGE_CF}${NC}"
    echo -e "EC2 公网 IP: ${YELLOW}${EC2_IP}${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    echo -e "${YELLOW}下一步：${NC}"
    echo -e "1. SSH 到 EC2 并部署后端代码"
    echo -e "   ssh -i your-key.pem ubuntu@${EC2_IP}"
    echo -e "2. 配置前端环境变量（.env.production）"
    echo -e "   VUE_APP_API_BASE_URL=${ALB_DNS}"
    echo -e "3. 构建并部署前端"
    echo -e "   ./deploy.sh update-frontend"
    ;;
    
  destroy)
    echo -e "${RED}警告：即将销毁所有资源！${NC}"
    read -p "确认销毁？(yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
      echo -e "${YELLOW}开始销毁 CDK 堆栈...${NC}"
      cdk destroy --force
      echo -e "${GREEN}CDK 堆栈已销毁！${NC}"
    else
      echo -e "${YELLOW}取消销毁操作${NC}"
    fi
    ;;
    
  update-frontend)
    echo -e "${YELLOW}开始更新前端...${NC}"
    
    # 获取 S3 存储桶名称
    PERSONAL_BUCKET=$(aws cloudformation describe-stacks \
      --stack-name AwsomeShopStack \
      --query 'Stacks[0].Outputs[?OutputKey==`PersonalS3Bucket`].OutputValue' \
      --output text \
      --region us-east-1 \
      --profile ${AWS_PROFILE})
    
    MANAGE_BUCKET=$(aws cloudformation describe-stacks \
      --stack-name AwsomeShopStack \
      --query 'Stacks[0].Outputs[?OutputKey==`ManageS3Bucket`].OutputValue' \
      --output text \
      --region us-east-1 \
      --profile ${AWS_PROFILE})
    
    # 构建员工端
    echo -e "${YELLOW}构建员工端...${NC}"
    cd ../front/personal
    npm run build
    
    # 上传到 S3
    echo -e "${YELLOW}上传员工端到 S3...${NC}"
    aws s3 sync dist/ s3://${PERSONAL_BUCKET}/ --delete --profile ${AWS_PROFILE}
    
    # 构建管理端
    echo -e "${YELLOW}构建管理端...${NC}"
    cd ../manage
    npm run build
    
    # 上传到 S3
    echo -e "${YELLOW}上传管理端到 S3...${NC}"
    aws s3 sync dist/ s3://${MANAGE_BUCKET}/ --delete --profile ${AWS_PROFILE}
    
    echo -e "${GREEN}前端更新完成！${NC}"
    echo -e "${YELLOW}注意：CloudFront 缓存可能需要几分钟才能更新${NC}"
    ;;
    
  *)
    echo "使用方法: $0 {bootstrap|deploy|destroy|update-frontend}"
    echo ""
    echo "命令说明："
    echo "  bootstrap        - 首次部署前初始化 CDK"
    echo "  deploy           - 部署 CDK 堆栈"
    echo "  destroy          - 销毁 CDK 堆栈"
    echo "  update-frontend  - 更新前端代码"
    exit 1
    ;;
esac
