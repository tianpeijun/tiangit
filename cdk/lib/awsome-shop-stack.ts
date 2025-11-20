import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as targets from 'aws-cdk-lib/aws-elasticloadbalancingv2-targets';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export class AwsomeShopStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ========================================
    // VPC 和网络配置
    // ========================================
    const vpc = new ec2.Vpc(this, 'AwsomeShopVPC', {
      maxAzs: 2,
      natGateways: 0, // 不使用 NAT Gateway 以节省成本
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
      ],
    });

    // ========================================
    // 安全组配置
    // ========================================
    
    // ALB 安全组
    const albSecurityGroup = new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
      vpc,
      description: 'Security group for ALB',
      allowAllOutbound: true,
    });
    albSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(8080),
      'Allow HTTP traffic on port 8080'
    );

    // EC2 安全组
    const ec2SecurityGroup = new ec2.SecurityGroup(this, 'EC2SecurityGroup', {
      vpc,
      description: 'Security group for EC2 instance',
      allowAllOutbound: true,
    });
    ec2SecurityGroup.addIngressRule(
      albSecurityGroup,
      ec2.Port.tcp(8000),
      'Allow traffic from ALB on port 8000'
    );
    ec2SecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(22),
      'Allow SSH access'
    );

    // ========================================
    // S3 存储桶（前端静态资源）
    // ========================================
    
    // 员工端 S3 存储桶（使用 OAC，不需要公共访问）
    const personalBucket = new s3.Bucket(this, 'PersonalBucket', {
      bucketName: `awsome-shop-personal-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // 管理端 S3 存储桶（使用 OAC，不需要公共访问）
    const manageBucket = new s3.Bucket(this, 'ManageBucket', {
      bucketName: `awsome-shop-manage-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // ========================================
    // CloudFront 分发（前端）
    // ========================================
    
    // 员工端 CloudFront 分发
    const personalDistribution = new cloudfront.Distribution(this, 'PersonalDistribution', {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(personalBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.ALLOW_ALL,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.seconds(0),
        },
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.seconds(0),
        },
      ],
    });

    // 管理端 CloudFront 分发
    const manageDistribution = new cloudfront.Distribution(this, 'ManageDistribution', {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(manageBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.ALLOW_ALL,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.seconds(0),
        },
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.seconds(0),
        },
      ],
    });

    // ========================================
    // IAM Role for EC2
    // ========================================
    const ec2Role = new iam.Role(this, 'EC2Role', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchAgentServerPolicy'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      ],
    });

    // 添加 S3 读取权限（用于部署）
    manageBucket.grantRead(ec2Role);

    // ========================================
    // EC2 实例（后端 API）
    // ========================================
    
    // User Data 脚本
    const userData = ec2.UserData.forLinux();
    userData.addCommands(
      '#!/bin/bash',
      'set -e',
      '',
      '# 更新系统',
      'dnf update -y',
      '',
      '# 安装依赖',
      'dnf install -y python3 python3-pip git',
      '',
      '# 创建应用目录',
      'mkdir -p /opt/awsome-shop',
      'mkdir -p /opt/awsome-shop/data',
      'mkdir -p /opt/awsome-shop/static/images',
      '',
      '# 设置权限',
      'chmod 755 /opt/awsome-shop',
      'chmod 755 /opt/awsome-shop/data',
      'chmod 755 /opt/awsome-shop/static',
      '',
      '# 注意：这里需要手动上传代码或从 Git 仓库克隆',
      '# 示例：git clone <your-repo-url> /opt/awsome-shop/server',
      '',
      '# 创建 systemd 服务文件',
      'cat > /etc/systemd/system/awsome-shop.service << EOF',
      '[Unit]',
      'Description=AWSomeShop Backend Service',
      'After=network.target',
      '',
      '[Service]',
      'Type=simple',
      'User=ec2-user',
      'WorkingDirectory=/opt/awsome-shop/server',
      'Environment="PATH=/usr/local/bin:/usr/bin:/bin"',
      'ExecStart=/usr/bin/python3 main.py',
      'Restart=always',
      'RestartSec=10',
      '',
      '[Install]',
      'WantedBy=multi-user.target',
      'EOF',
      '',
      '# 设置目录所有者',
      'chown -R ec2-user:ec2-user /opt/awsome-shop',
      '',
      '# 重新加载 systemd',
      'systemctl daemon-reload',
      '',
      '# 注意：需要手动启动服务',
      '# systemctl enable awsome-shop',
      '# systemctl start awsome-shop',
      '',
      'echo "EC2 instance setup completed"'
    );

    // EC2 实例
    const instance = new ec2.Instance(this, 'BackendInstance', {
      vpc,
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.SMALL),
      machineImage: ec2.MachineImage.latestAmazonLinux2023({
        cpuType: ec2.AmazonLinuxCpuType.X86_64,
      }),
      securityGroup: ec2SecurityGroup,
      role: ec2Role,
      userData: userData,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
      blockDevices: [
        {
          deviceName: '/dev/xvda',
          volume: ec2.BlockDeviceVolume.ebs(20, {
            volumeType: ec2.EbsDeviceVolumeType.GP3,
            deleteOnTermination: true,
          }),
        },
      ],
    });

    // ========================================
    // Application Load Balancer
    // ========================================
    const alb = new elbv2.ApplicationLoadBalancer(this, 'ALB', {
      vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup,
    });

    // 监听器（端口 8080）
    const listener = alb.addListener('Listener', {
      port: 8080,
      protocol: elbv2.ApplicationProtocol.HTTP,
    });

    // 目标组
    const targetGroup = new elbv2.ApplicationTargetGroup(this, 'TargetGroup', {
      vpc,
      port: 8000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targets: [new targets.InstanceTarget(instance)],
      healthCheck: {
        path: '/health',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 3,
      },
    });

    // 添加目标组到监听器
    listener.addTargetGroups('TargetGroup', {
      targetGroups: [targetGroup],
    });

    // ========================================
    // CloudWatch 日志
    // ========================================
    const logGroup = new logs.LogGroup(this, 'LogGroup', {
      logGroupName: '/aws/ec2/awsome-shop',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // ========================================
    // 输出信息
    // ========================================
    new cdk.CfnOutput(this, 'ALBDnsName', {
      value: `http://${alb.loadBalancerDnsName}:8080`,
      description: 'ALB DNS Name (Backend API URL)',
    });

    new cdk.CfnOutput(this, 'PersonalCloudFrontURL', {
      value: `http://${personalDistribution.distributionDomainName}`,
      description: 'CloudFront URL for Personal (Employee) Frontend',
    });

    new cdk.CfnOutput(this, 'ManageCloudFrontURL', {
      value: `http://${manageDistribution.distributionDomainName}`,
      description: 'CloudFront URL for Manage (Admin) Frontend',
    });

    new cdk.CfnOutput(this, 'EC2InstanceId', {
      value: instance.instanceId,
      description: 'EC2 Instance ID',
    });

    new cdk.CfnOutput(this, 'EC2PublicIP', {
      value: instance.instancePublicIp,
      description: 'EC2 Instance Public IP',
    });

    new cdk.CfnOutput(this, 'PersonalS3Bucket', {
      value: personalBucket.bucketName,
      description: 'S3 Bucket for Personal Frontend',
    });

    new cdk.CfnOutput(this, 'ManageS3Bucket', {
      value: manageBucket.bucketName,
      description: 'S3 Bucket for Manage Frontend',
    });
  }
}
