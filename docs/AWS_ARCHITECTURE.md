# AWS 架构设计文档

## 概述

本文档详细描述了 Awsome Shop 电商系统的 AWS 架构设计。该架构采用现代化的云原生设计原则，利用 AWS 服务构建了一个高可用、可扩展的电商系统。

## 架构图

![AWS 架构图](AWS_ARCHITECTURE.html)

*注：打开 `AWS_ARCHITECTURE.html` 文件查看交互式架构图*

## 架构组件详解

### 1. 网络层 (Network Layer)

#### VPC (Virtual Private Cloud)
- **配置**: 2 个可用区 (Availability Zones)，每个 AZ 包含一个公有子网
- **目的**: 提供隔离的网络环境，确保资源安全
- **特点**: 
  - 不使用 NAT Gateway 以降低成本
  - 仅使用公有子网，简化网络配置

#### Internet Gateway
- **作用**: 允许 VPC 内的资源与互联网通信
- **连接**: 连接到 VPC，为公有子网提供互联网访问能力

### 2. 前端架构 (Frontend Architecture)

#### CloudFront 分发
- **数量**: 2 个独立的分发
  - 管理员端 (Admin) CloudFront
  - 员工端 (Employee) CloudFront
- **特性**:
  - 全球内容分发网络 (CDN)
  - 静态资源加速
  - 自定义错误响应 (404/403 重定向到 index.html)
  - 使用 Origin Access Control (OAC) 安全访问 S3

#### S3 存储桶
- **数量**: 2 个存储桶
  - 管理员端静态资源存储桶
  - 员工端静态资源存储桶
- **安全**: 
  - 不允许公共访问
  - 仅通过 CloudFront OAC 访问
  - 自动删除策略 (便于开发测试)

### 3. 后端架构 (Backend Architecture)

#### Application Load Balancer (ALB)
- **配置**: 
  - 面向互联网的负载均衡器
  - 监听端口 8080 (HTTP)
  - 健康检查路径 `/health`
- **作用**:
  - 分发流量到后端 EC2 实例
  - 提供高可用性
  - SSL 终止 (可扩展支持 HTTPS)

#### EC2 实例
- **实例类型**: t3.small (2 vCPU, 2 GiB 内存)
- **AMI**: Amazon Linux 2023
- **存储**: 20GB gp3 EBS 卷
- **配置**:
  - 预安装 Python 3 和 Git
  - 自动创建应用目录结构
  - 预配置 systemd 服务文件
  - 安全组限制访问

#### 安全组 (Security Groups)
- **ALB 安全组**:
  - 允许来自互联网的 8080 端口访问
- **EC2 安全组**:
  - 仅允许来自 ALB 的 8000 端口访问
  - 允许 SSH 访问 (22 端口) 用于管理

### 4. 安全与权限 (Security & Permissions)

#### IAM Role
- **关联**: 附加到 EC2 实例
- **权限**:
  - CloudWatch Agent Server Policy (日志收集)
  - Amazon SSM Managed Instance Core (远程管理)
  - S3 读取权限 (用于部署)

#### 安全最佳实践
- 零信任网络模型
- 最小权限原则
- 端到端加密 (可扩展)
- 定期安全评估

### 5. 监控与日志 (Monitoring & Logging)

#### CloudWatch Logs
- **用途**: 收集 EC2 实例应用日志
- **保留**: 一周自动删除
- **配置**: 通过 CloudWatch Agent 收集

## 数据流分析 (Data Flow Analysis)

### 前端请求流程
1. 用户访问 CloudFront URL
2. CloudFront 检查边缘节点缓存
3. 缓存未命中时，从 S3 获取静态资源
4. S3 通过 OAC 验证请求合法性

### 后端 API 请求流程
1. 用户通过 CloudFront 发起 API 请求
2. 请求路由到 ALB
3. ALB 根据健康检查结果分发到可用的 EC2 实例
4. EC2 实例处理请求并返回响应
5. 响应通过 ALB 返回给用户

### 部署流程
1. 前端构建产物上传到对应 S3 存储桶
2. CloudFront 缓存失效，获取最新资源
3. 后端代码通过 SSM 部署到 EC2 实例
4. 重启服务应用新代码

## 高可用性设计 (High Availability Design)

### 多可用区部署
- VPC 跨 2 个可用区
- EC2 实例可在多个 AZ 部署
- ALB 自动跨 AZ 分发流量

### 负载均衡
- ALB 提供应用层负载均衡
- 健康检查自动剔除故障实例
- 自动故障转移

### 数据持久化
- 使用 RDS PostgreSQL (通过 CDK 部署)
- 自动备份和快照
- 多 AZ 部署选项

## 成本优化策略 (Cost Optimization Strategies)

### 资源选择
- 使用 t3.small 实例平衡性能与成本
- 不使用 NAT Gateway 降低网络费用
- 使用 S3 标准存储降低成本

### 自动化管理
- 自动删除策略避免资源浪费
- CloudWatch 日志自动过期
- 按需扩缩容能力

## 扩展性考虑 (Scalability Considerations)

### 水平扩展
- 可增加 EC2 实例数量
- ALB 自动支持多实例负载均衡
- S3 和 CloudFront 天然支持高并发

### 垂直扩展
- 可升级 EC2 实例类型
- 可调整 EBS 卷大小
- 可增加 RDS 实例规格

### 微服务架构
- 当前为单体应用，可拆分为微服务
- 使用 ECS/EKS 容器化部署
- API Gateway 替代 ALB

## 安全加固建议 (Security Hardening Recommendations)

### 网络安全
1. 添加私有子网和 NAT Gateway
2. 使用 AWS WAF 保护 ALB
3. 配置 VPC Flow Logs 监控网络流量

### 访问控制
1. 启用多因素认证 (MFA)
2. 使用 AWS Secrets Manager 管理敏感信息
3. 实施最小权限 IAM 策略

### 数据保护
1. 启用 S3 服务端加密
2. 使用 SSL/TLS 加密传输数据
3. 定期轮换密钥和证书

## 监控告警建议 (Monitoring & Alerting Recommendations)

### 关键指标
1. EC2 CPU 和内存使用率
2. ALB 请求延迟和错误率
3. S3 存储使用情况
4. CloudFront 缓存命中率

### 告警设置
1. 高 CPU 使用率告警
2. 健康检查失败告警
3. 高错误率告警
4. 存储空间不足告警

## 灾难恢复计划 (Disaster Recovery Plan)

### 备份策略
1. RDS 自动备份
2. S3 版本控制
3. 定期快照

### 恢复流程
1. 从 RDS 快照恢复数据库
2. 重新部署应用到 EC2
3. 从 S3 恢复静态资源
4. 更新 DNS 指向新环境

## 未来改进建议 (Future Improvement Suggestions)

### 性能优化
1. 添加 Redis 缓存层
2. 使用 ElastiCache 提升数据库性能
3. 实施更精细的 CDN 缓存策略

### 架构演进
1. 迁移到容器化部署 (ECS/EKS)
2. 使用 API Gateway 替代 ALB
3. 实施微服务架构

### 运维自动化
1. 配置 CI/CD 流水线
2. 实施蓝绿部署
3. 自动化扩缩容

## 总结

该 AWS 架构为 Awsome Shop 电商系统提供了稳定、安全、可扩展的云基础设施。通过合理利用 AWS 服务，实现了前后端分离、高可用性和成本效益的最佳平衡。随着业务发展，可以按需扩展和优化架构组件。