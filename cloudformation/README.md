# AWSomeShop CloudFormation Infrastructure

This directory contains AWS CDK (Cloud Development Kit) code written in Python to provision the infrastructure for AWSomeShop.

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions
2. **AWS CLI**: Install and configure AWS CLI
   ```bash
   # Install AWS CLI (macOS)
   brew install awscli
   
   # Configure with your credentials
   aws configure
   # Enter: AWS Access Key ID, Secret Access Key, Default region (e.g., us-east-1), Output format (json)
   ```

3. **Python 3.8+**: Ensure Python is installed
   ```bash
   python3 --version
   ```

4. **Node.js**: Required for AWS CDK
   ```bash
   # Install Node.js (macOS)
   brew install node
   ```

5. **AWS CDK**: Install the CDK CLI
   ```bash
   npm install -g aws-cdk
   cdk --version
   ```

## Project Structure

```
cloudformation/
├── README.md           # This file
├── app.py             # CDK app entry point
├── requirements.txt   # Python dependencies
├── cdk.json          # CDK configuration
└── awsome_shop/      # CDK stack code
    ├── __init__.py
    └── awsome_shop_stack.py
```

## Initial Setup

### Step 1: Install Python Dependencies

```bash
cd cloudformation
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### Step 2: Bootstrap CDK (First Time Only)

This creates necessary resources in your AWS account for CDK deployments:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION

# Example:
# cdk bootstrap aws://123456789012/us-east-1
```

To find your account ID:
```bash
aws sts get-caller-identity --query Account --output text
```

## Deployment Commands

### Synthesize CloudFormation Template

This generates the CloudFormation template without deploying:

```bash
cdk synth
```

### View Changes (Diff)

See what will change before deploying:

```bash
cdk diff
```

### Deploy Infrastructure

Deploy the stack to AWS:

```bash
cdk deploy
```

You'll be prompted to approve security-related changes. Type 'y' to proceed.

### Destroy Infrastructure

Remove all resources (careful - this deletes everything!):

```bash
cdk destroy
```

## What Gets Provisioned

### 1. VPC (Virtual Private Cloud)
- CIDR: 10.0.0.0/16
- 2 Availability Zones for high availability
- Public subnets (for ALB)
- Private subnets (for EC2 instances)
- NAT Gateways for private subnet internet access
- Internet Gateway for public access

### 2. Application Load Balancer (ALB)
- Internet-facing
- Listens on port 80 (HTTP)
- Health checks configured
- Distributes traffic to EC2 instances

### 3. EC2 Instances
- Instance type: t3.small (adjustable)
- Auto Scaling Group (min: 2, max: 4)
- Automatically registered with ALB
- Security group allowing traffic from ALB
- EBS volumes for persistent storage
- User data script for application setup

### 4. Security Groups
- ALB Security Group: Allows HTTP (80) from internet
- EC2 Security Group: Allows traffic from ALB only
- Database access restricted to application tier

### 5. IAM Roles
- EC2 instance role with necessary permissions
- SSM access for secure instance management

## Configuration

### Customizing the Stack

Edit `awsome_shop/awsome_shop_stack.py` to modify:

- **Instance Type**: Change `instance_type` parameter
- **Capacity**: Adjust `min_capacity` and `max_capacity` in Auto Scaling Group
- **Region**: Modify in `cdk.json` or use `--region` flag
- **VPC CIDR**: Change `cidr` in VPC configuration

### Environment Variables

You can set environment-specific configurations:

```bash
export AWS_REGION=us-east-1
export ENVIRONMENT=production
cdk deploy
```

## Outputs

After deployment, CDK will output:

- **LoadBalancerDNS**: The URL to access your application
- **VPCId**: The VPC identifier
- **InstanceIds**: EC2 instance identifiers

Example:
```
Outputs:
AwsomeShopStack.LoadBalancerDNS = awsome-alb-123456789.us-east-1.elb.amazonaws.com
AwsomeShopStack.VPCId = vpc-0123456789abcdef0
```

Access your application at: `http://<LoadBalancerDNS>`

## Troubleshooting

### Issue: "CDK command not found"
```bash
npm install -g aws-cdk
```

### Issue: "Unable to resolve AWS account"
```bash
aws configure
# Verify with:
aws sts get-caller-identity
```

### Issue: "Stack already exists"
```bash
# Update existing stack
cdk deploy

# Or delete and recreate
cdk destroy
cdk deploy
```

### Issue: Deployment fails
```bash
# Check CloudFormation console for detailed error
# Or view events:
aws cloudformation describe-stack-events --stack-name AwsomeShopStack
```

## Monitoring

### View Stack Status
```bash
aws cloudformation describe-stacks --stack-name AwsomeShopStack
```

### View EC2 Instances
```bash
aws ec2 describe-instances --filters "Name=tag:aws:cloudformation:stack-name,Values=AwsomeShopStack"
```

### View Load Balancer
```bash
aws elbv2 describe-load-balancers
```

## Cost Estimation

Approximate monthly costs (us-east-1):
- 2x t3.small EC2 instances: ~$30
- Application Load Balancer: ~$20
- NAT Gateway (2 AZs): ~$65
- EBS volumes: ~$10
- Data transfer: Variable

**Total: ~$125-150/month**

Use AWS Cost Explorer for accurate tracking.

## Best Practices Applied

✅ Multi-AZ deployment for high availability
✅ Private subnets for EC2 instances
✅ Security groups with least privilege
✅ Auto Scaling for elasticity
✅ Health checks for reliability
✅ IAM roles instead of access keys
✅ Infrastructure as Code for repeatability

## Next Steps

1. Deploy the infrastructure: `cdk deploy`
2. Note the LoadBalancerDNS output
3. SSH into EC2 instances to deploy application code
4. Configure application to use EBS-mounted SQLite database
5. Set up CloudWatch alarms for monitoring
6. Configure Route53 for custom domain (optional)

## Support

For CDK documentation: https://docs.aws.amazon.com/cdk/
For CloudFormation: https://docs.aws.amazon.com/cloudformation/
