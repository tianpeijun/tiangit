# Tagging Strategy for AWSomeShop

## Overview

All resources in the AWSomeShop infrastructure are tagged with mandatory tags for cost tracking, ownership, and resource management.

## Mandatory Tags (Applied to ALL Resources)

These tags are automatically applied to every resource in the stack using `Tags.of(self)`:

```python
owner       = "dexter"
team        = "sz24-tm4"
project     = "aidlc"
Environment = "dev"
```

This is equivalent to Terraform's `default_tags` functionality.

## How It Works

In the main application file (`app.py`), we apply tags to the stack after creation:

```python
stack = AwsomeShopStack(app, "AwsomeShopStack", ...)

# Apply mandatory tags to all resources
cdk.Tags.of(stack).add("owner", "dexter")
cdk.Tags.of(stack).add("team", "sz24-tm4")
cdk.Tags.of(stack).add("project", "aidlc")
cdk.Tags.of(stack).add("Environment", "dev")
```

These tags propagate to ALL resources created within the stack, including:
- VPC and subnets
- EC2 instances
- Auto Scaling Groups
- Load Balancers
- Security Groups
- EBS volumes
- IAM roles
- NAT Gateways
- Internet Gateways

## Additional Resource-Specific Tags

Beyond the mandatory tags, specific resources have additional tags for identification:

### VPC
- `Name`: awsome-shop-vpc
- `Component`: networking

### Security Groups
- ALB SG: `Name`: awsome-shop-alb-sg, `Component`: load-balancer
- EC2 SG: `Name`: awsome-shop-ec2-sg, `Component`: compute

### Load Balancer
- `Name`: awsome-shop-alb
- `Component`: load-balancer

### Target Group
- `Name`: awsome-shop-tg
- `Component`: load-balancer

### Auto Scaling Group / EC2 Instances
- `Name`: awsome-shop-asg
- `Component`: compute
- `Application`: awsome-shop

### IAM Role
- `Name`: awsome-shop-ec2-role
- `Component`: iam

## Verifying Tags After Deployment

### View all resources with tags
```bash
# List EC2 instances with tags
aws ec2 describe-instances \
  --filters "Name=tag:project,Values=aidlc" \
  --query 'Reservations[*].Instances[*].[InstanceId,Tags]' \
  --output table

# List all resources by tag
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=project,Values=aidlc \
  --query 'ResourceTagMappingList[*].[ResourceARN]' \
  --output table
```

### Cost allocation by tags
```bash
# View costs by owner
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=TAG,Key=owner

# View costs by team
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=TAG,Key=team
```

## Modifying Tags

### Change mandatory tags for different environments

Edit `cloudformation/app.py`:

```python
# For production environment
cdk.Tags.of(stack).add("Environment", "prod")

# For staging environment
cdk.Tags.of(stack).add("Environment", "staging")
```

### Add new mandatory tags

Simply add more `cdk.Tags.of(stack).add()` calls in `app.py`:

```python
cdk.Tags.of(stack).add("cost-center", "engineering")
cdk.Tags.of(stack).add("compliance", "required")
```

### Create multiple stacks with different tags

You can create separate stacks for different environments:

```python
# Development stack
dev_stack = AwsomeShopStack(app, "AwsomeShopDev", ...)
cdk.Tags.of(dev_stack).add("Environment", "dev")
cdk.Tags.of(dev_stack).add("owner", "dexter")

# Production stack
prod_stack = AwsomeShopStack(app, "AwsomeShopProd", ...)
cdk.Tags.of(prod_stack).add("Environment", "prod")
cdk.Tags.of(prod_stack).add("owner", "dexter")
```

## Best Practices

✅ **Always include**: owner, team, project, Environment
✅ **Use consistent casing**: We use lowercase for most tags, PascalCase for Environment
✅ **Cost allocation**: Enable these tags in AWS Cost Explorer for cost tracking
✅ **Automation**: Tags are applied automatically via CDK - no manual tagging needed
✅ **Propagation**: Tags on Auto Scaling Groups automatically propagate to EC2 instances

## Tag Compliance

To ensure all resources are properly tagged, you can use AWS Config rules:

```bash
# Check for required tags
aws configservice put-config-rule --config-rule file://required-tags-rule.json
```

Example rule (save as `required-tags-rule.json`):
```json
{
  "ConfigRuleName": "required-tags",
  "Description": "Checks that resources have required tags",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "REQUIRED_TAGS"
  },
  "InputParameters": "{\"tag1Key\":\"owner\",\"tag2Key\":\"team\",\"tag3Key\":\"project\",\"tag4Key\":\"Environment\"}"
}
```

## Troubleshooting

### Tags not appearing on resources

1. **Redeploy the stack**: `cdk deploy`
2. **Check CloudFormation**: Tags should appear in the CloudFormation template
3. **Verify in console**: Check AWS Console for the specific resource

### Some resources missing tags

- Some AWS resources don't support tags (e.g., some networking components)
- Check AWS documentation for tag support per service
- CDK will silently skip tagging for unsupported resources

### Tags not showing in Cost Explorer

1. Enable cost allocation tags in AWS Billing Console
2. Go to: Billing → Cost Allocation Tags
3. Activate: owner, team, project, Environment
4. Wait 24 hours for data to populate
