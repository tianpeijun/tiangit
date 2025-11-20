# Quick Start Guide - AWSomeShop Infrastructure

This is a simplified guide to get you started quickly. For detailed information, see [README.md](README.md).

## Prerequisites Checklist

- [ ] AWS Account with admin access
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Python 3.8+ installed
- [ ] Node.js installed (for CDK)
- [ ] AWS CDK CLI installed (`npm install -g aws-cdk`)

## 5-Minute Deployment

### 1. Install Dependencies

```bash
cd cloudformation

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Bootstrap CDK (First Time Only)

```bash
# Get your AWS account ID
aws sts get-caller-identity

# Bootstrap (replace with your account ID and region)
cdk bootstrap aws://123456789012/us-east-1
```

### 3. Preview Changes

```bash
# See what will be created
cdk synth

# Or view as a diff
cdk diff
```

### 4. Deploy

```bash
cdk deploy
```

Type `y` when prompted to approve security changes.

⏱️ Deployment takes about 5-10 minutes.

### 5. Get Your Application URL

After deployment completes, look for the output:

```
Outputs:
AwsomeShopStack.LoadBalancerDNS = awsome-shop-alb-xxxxx.us-east-1.elb.amazonaws.com
```

Your application will be accessible at: `http://<LoadBalancerDNS>`

## What You Get

✅ VPC with public and private subnets (2 AZs)
✅ Application Load Balancer (internet-facing)
✅ 2 EC2 instances (t3.small) in Auto Scaling Group
✅ Security groups configured
✅ EBS volumes for persistent storage
✅ IAM roles for secure access

## Next Steps

1. **Deploy Your Application**
   - SSH or use SSM Session Manager to access EC2 instances
   - Clone your application code
   - Install dependencies
   - Start your Python backend and Vue.js frontend

2. **Configure Database**
   - Mount the EBS data volume (`/dev/xvdf`)
   - Set up SQLite database on the mounted volume

3. **Update Health Check**
   - Modify the health check path in `awsome_shop_stack.py` if needed
   - Default is `/` on port 8000

4. **Set Up Monitoring**
   - CloudWatch metrics are automatically collected
   - Set up alarms for CPU, memory, and health checks

## Common Commands

```bash
# View stack status
aws cloudformation describe-stacks --stack-name AwsomeShopStack

# List EC2 instances
aws ec2 describe-instances --filters "Name=tag:aws:cloudformation:stack-name,Values=AwsomeShopStack"

# Connect to instance via SSM (no SSH key needed)
aws ssm start-session --target <instance-id>

# Update stack after code changes
cdk deploy

# Destroy everything
cdk destroy
```

## Troubleshooting

**Issue**: CDK command not found
```bash
npm install -g aws-cdk
```

**Issue**: AWS credentials not configured
```bash
aws configure
```

**Issue**: Deployment fails
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name AwsomeShopStack --max-items 10
```

## Cost Estimate

Approximate monthly cost: **$125-150**
- 2x t3.small EC2: ~$30
- ALB: ~$20
- NAT Gateways: ~$65
- EBS: ~$10
- Data transfer: Variable

## Need Help?

- Full documentation: [README.md](README.md)
- AWS CDK docs: https://docs.aws.amazon.com/cdk/
- CloudFormation docs: https://docs.aws.amazon.com/cloudformation/
