"""
AWSomeShop Infrastructure Stack

This stack provisions:
- VPC with public and private subnets across 2 AZs
- Application Load Balancer (ALB)
- EC2 Auto Scaling Group
- Security Groups
- IAM Roles
- EBS Volumes for persistent storage

Following AWS Well-Architected Framework principles.
"""

from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    Tags,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
)
from constructs import Construct


class AwsomeShopStack(Stack):
    """Main infrastructure stack for AWSomeShop"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ========================================
        # 1. VPC - Network Foundation
        # ========================================
        # Creates a VPC with public and private subnets across 2 AZs
        # Public subnets: For ALB (internet-facing)
        # Private subnets: For EC2 instances (more secure)
        
        vpc = ec2.Vpc(
            self,
            "AwsomeShopVPC",
            vpc_name="awsome-shop-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,  # Use 2 Availability Zones for high availability
            nat_gateways=2,  # One NAT gateway per AZ for redundancy
            subnet_configuration=[
                # Public subnets for ALB
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,  # 10.0.0.0/24, 10.0.1.0/24
                ),
                # Private subnets for EC2 instances
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,  # 10.0.2.0/24, 10.0.3.0/24
                ),
            ],
        )
        
        # Add resource-specific tags to VPC
        Tags.of(vpc).add("Name", "awsome-shop-vpc")
        Tags.of(vpc).add("Component", "networking")

        # ========================================
        # 2. Security Groups
        # ========================================
        
        # ALB Security Group - Allows HTTP traffic from internet
        alb_security_group = ec2.SecurityGroup(
            self,
            "ALBSecurityGroup",
            vpc=vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=True,
        )
        
        # Allow HTTP traffic from anywhere
        alb_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic from internet",
        )
        
        # Add tags to ALB security group
        Tags.of(alb_security_group).add("Name", "awsome-shop-alb-sg")
        Tags.of(alb_security_group).add("Component", "load-balancer")

        # EC2 Security Group - Only allows traffic from ALB
        ec2_security_group = ec2.SecurityGroup(
            self,
            "EC2SecurityGroup",
            vpc=vpc,
            description="Security group for EC2 instances",
            allow_all_outbound=True,
        )
        
        # Allow traffic from ALB only
        ec2_security_group.add_ingress_rule(
            peer=alb_security_group,
            connection=ec2.Port.tcp(8000),  # Python app typically runs on 8000
            description="Allow traffic from ALB",
        )
        
        # Add tags to EC2 security group
        Tags.of(ec2_security_group).add("Name", "awsome-shop-ec2-sg")
        Tags.of(ec2_security_group).add("Component", "compute")
        
        # Allow SSH for management (optional - remove in production)
        # Uncomment if you need SSH access
        # ec2_security_group.add_ingress_rule(
        #     peer=ec2.Peer.any_ipv4(),
        #     connection=ec2.Port.tcp(22),
        #     description="Allow SSH access",
        # )

        # ========================================
        # 3. IAM Role for EC2 Instances
        # ========================================
        
        # Create IAM role with necessary permissions
        ec2_role = iam.Role(
            self,
            "EC2InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="IAM role for AWSomeShop EC2 instances",
            managed_policies=[
                # Allows SSM Session Manager access (secure alternative to SSH)
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
                # Allows CloudWatch logging
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchAgentServerPolicy"
                ),
            ],
        )
        
        # Add tags to IAM role
        Tags.of(ec2_role).add("Name", "awsome-shop-ec2-role")
        Tags.of(ec2_role).add("Component", "iam")

        # ========================================
        # 4. EC2 Launch Template
        # ========================================
        
        # User data script - runs on instance launch
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "# Update system packages",
            "yum update -y",
            "",
            "# Install Python 3 and pip",
            "yum install -y python3 python3-pip",
            "",
            "# Install Git",
            "yum install -y git",
            "",
            "# Create application directory",
            "mkdir -p /opt/awsome-shop",
            "",
            "# Mount EBS volume for database (if attached)",
            "# You'll need to format and mount the EBS volume",
            "# Example:",
            "# mkfs -t ext4 /dev/xvdf",
            "# mkdir -p /data",
            "# mount /dev/xvdf /data",
            "# echo '/dev/xvdf /data ext4 defaults,nofail 0 2' >> /etc/fstab",
            "",
            "# Install CloudWatch agent for monitoring",
            "wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm",
            "rpm -U ./amazon-cloudwatch-agent.rpm",
            "",
            "# TODO: Add commands to clone and start your application",
            "# cd /opt/awsome-shop",
            "# git clone <your-repo-url> .",
            "# pip3 install -r requirements.txt",
            "# python3 app.py",
        )

        # Choose Amazon Linux 2023 AMI
        machine_image = ec2.MachineImage.latest_amazon_linux2023(
            cpu_type=ec2.AmazonLinuxCpuType.X86_64,
        )

        # ========================================
        # 5. Application Load Balancer
        # ========================================
        
        alb = elbv2.ApplicationLoadBalancer(
            self,
            "AwsomeShopALB",
            vpc=vpc,
            internet_facing=True,  # Accessible from internet
            load_balancer_name="awsome-shop-alb",
            security_group=alb_security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        
        # Add tags to ALB
        Tags.of(alb).add("Name", "awsome-shop-alb")
        Tags.of(alb).add("Component", "load-balancer")

        # Create target group for EC2 instances
        target_group = elbv2.ApplicationTargetGroup(
            self,
            "AwsomeShopTargetGroup",
            vpc=vpc,
            port=8000,  # Python app port
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(
                enabled=True,
                path="/",  # Health check endpoint
                protocol=elbv2.Protocol.HTTP,
                port="8000",
                healthy_threshold_count=2,
                unhealthy_threshold_count=3,
                timeout=Duration.seconds(5),
                interval=Duration.seconds(30),
            ),
            deregistration_delay=Duration.seconds(30),
        )
        
        # Add tags to target group
        Tags.of(target_group).add("Name", "awsome-shop-tg")
        Tags.of(target_group).add("Component", "load-balancer")

        # Add listener to ALB
        listener = alb.add_listener(
            "HTTPListener",
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_target_groups=[target_group],
        )

        # ========================================
        # 6. Auto Scaling Group with EC2 Instances
        # ========================================
        
        asg = autoscaling.AutoScalingGroup(
            self,
            "AwsomeShopASG",
            vpc=vpc,
            instance_type=ec2.InstanceType("t3.small"),  # 2 vCPU, 2 GB RAM
            machine_image=machine_image,
            security_group=ec2_security_group,
            role=ec2_role,
            user_data=user_data,
            min_capacity=2,  # Minimum 2 instances for high availability
            max_capacity=4,  # Maximum 4 instances for scaling
            desired_capacity=2,  # Start with 2 instances
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            health_check=autoscaling.HealthCheck.elb(
                grace=Duration.seconds(300)  # Wait 5 minutes before health checks
            ),
            # Add EBS volume for database storage
            block_devices=[
                autoscaling.BlockDevice(
                    device_name="/dev/xvda",  # Root volume
                    volume=autoscaling.BlockDeviceVolume.ebs(
                        volume_size=20,  # 20 GB
                        volume_type=autoscaling.EbsDeviceVolumeType.GP3,
                        delete_on_termination=True,
                        encrypted=True,  # Encrypt at rest
                    ),
                ),
                autoscaling.BlockDevice(
                    device_name="/dev/xvdf",  # Data volume for SQLite
                    volume=autoscaling.BlockDeviceVolume.ebs(
                        volume_size=50,  # 50 GB for database
                        volume_type=autoscaling.EbsDeviceVolumeType.GP3,
                        delete_on_termination=False,  # Preserve data
                        encrypted=True,  # Encrypt at rest
                    ),
                ),
            ],
        )
        
        # Add tags to Auto Scaling Group (will propagate to EC2 instances)
        Tags.of(asg).add("Name", "awsome-shop-asg")
        Tags.of(asg).add("Component", "compute")
        Tags.of(asg).add("Application", "awsome-shop")

        # Attach Auto Scaling Group to Target Group
        asg.attach_to_application_target_group(target_group)

        # ========================================
        # 7. Auto Scaling Policies
        # ========================================
        
        # Scale up when CPU > 70%
        asg.scale_on_cpu_utilization(
            "ScaleUpPolicy",
            target_utilization_percent=70,
            cooldown=Duration.seconds(300),
        )

        # ========================================
        # 8. Outputs
        # ========================================
        
        # Output the ALB DNS name
        CfnOutput(
            self,
            "LoadBalancerDNS",
            value=alb.load_balancer_dns_name,
            description="Application Load Balancer DNS name",
            export_name="AwsomeShopALBDNS",
        )

        # Output the VPC ID
        CfnOutput(
            self,
            "VPCId",
            value=vpc.vpc_id,
            description="VPC ID",
            export_name="AwsomeShopVPCId",
        )

        # Output the Auto Scaling Group name
        CfnOutput(
            self,
            "AutoScalingGroupName",
            value=asg.auto_scaling_group_name,
            description="Auto Scaling Group name",
            export_name="AwsomeShopASGName",
        )
