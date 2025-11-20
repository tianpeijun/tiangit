# Awsome Shop - 电商系统

一个基于 Vue.js + FastAPI + SQLite的全栈电商系统，部署在 AWS 上。

## 系统架构

- **前端**: Vue.js (管理端 + 员工端)
- **后端**: FastAPI (Python)
- **数据库**: SQLite
- **基础设施**: AWS CDK
- **部署**: EC2 (后端) + S3/CloudFront (前端)

## 项目结构

```
.
├── cdk/                    # AWS CDK 基础设施代码
├── server/                 # FastAPI 后端
├── front/
│   ├── manage/            # 管理端前端
│   └── personal/          # 员工端前端
├── data/                  # 数据库初始化脚本
├── static/                # 静态资源（图片等）
├── docs/                  # 文档
│   ├── DATABASE_SCHEMA.md # 数据库 schema
│   ├── DEPLOYMENT.md      # 部署指南
│   └── api-spec.yaml      # API 规格 (OpenAPI 3.0)
├── scripts/               # 部署和测试脚本
│   ├── deploy-backend-ssm.sh  # 后端部署脚本
│   ├── deploy-via-s3.sh       # 前端部署脚本
│   └── integration_test.py    # 集成测试
└── .kiro/specs/           # 功能规格文档
```

## 快速开始

### 1. 部署基础设施

```bash
cd cdk
npm install
cdk deploy
```

### 2. 部署后端到 EC2

```bash
bash scripts/deploy-backend-ssm.sh
```

### 3. 部署前端到 S3/CloudFront

```bash
# 管理端
cd front/manage
npm run build
aws s3 sync ../static/manage s3://awsome-shop-manage-418295705866/ --delete

# 员工端
cd front/personal
npm run build
aws s3 sync ../static/personal s3://awsome-shop-personal-418295705866/ --delete
```

### 4. 清除 CloudFront 缓存

```bash
# 获取 Distribution ID
aws cloudfront list-distributions --query "DistributionList.Items[].{Id:Id,DomainName:DomainName}"

# 清除缓存
aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*"
```

## 访问地址

- **管理端**: https://d3xxxxxxxxxx.cloudfront.net
- **员工端**: https://d2xxxxxxxxxx.cloudfront.net
- **后端 API**: http://Awsome-ALBAE-xxxxxxxx.us-east-1.elb.amazonaws.com:8080

## 文档

- **数据库 Schema**: `docs/DATABASE_SCHEMA.md`
- **API 规格**: `docs/api-spec.yaml` (OpenAPI 3.0)
- **部署指南**: `docs/DEPLOYMENT.md`

## 开发

### 本地运行后端

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 本地运行前端

```bash
# 管理端
cd front/manage
npm install
npm run serve

# 员工端
cd front/personal
npm install
npm run serve
```

## 部署脚本

- `scripts/deploy-backend-ssm.sh` - 使用 AWS SSM 部署后端到 EC2
- `scripts/deploy-via-s3.sh` - 部署前端到 S3/CloudFront
- `scripts/integration_test.py` - 集成测试脚本
- `cdk/deploy.sh` - 部署 CDK 基础设施

## 配置文件

- `server/config/settings.py` - 后端配置
- `front/manage/.env.production` - 管理端生产环境配置
- `front/personal/.env.production` - 员工端生产环境配置

## License

MIT
