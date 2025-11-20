#!/usr/bin/env python3
"""
AWSomeShop CDK Application Entry Point

This is the main entry point for the CDK application.
It creates and synthesizes the CloudFormation stack.
"""

import aws_cdk as cdk
from awsome_shop.awsome_shop_stack import AwsomeShopStack


app = cdk.App()

# Create the main infrastructure stack
stack = AwsomeShopStack(
    app,
    "AwsomeShopStack",
    description="AWSomeShop Employee Benefits Platform Infrastructure",
    
    # Uncomment to specify account and region
    # env=cdk.Environment(
    #     account='123456789012',
    #     region='us-east-1'
    # ),
)

# ========================================
# MANDATORY TAGS - Apply to ALL resources
# ========================================
# These tags will be automatically applied to every resource in the stack
# Similar to Terraform's default_tags
cdk.Tags.of(stack).add("owner", "group4")
cdk.Tags.of(stack).add("team", "sz24-tm4")
cdk.Tags.of(stack).add("project", "aidlc")
cdk.Tags.of(stack).add("Environment", "dev")

app.synth()
