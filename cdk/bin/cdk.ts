#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { AwsomeShopStack } from '../lib/awsome-shop-stack';

const app = new cdk.App();

// 使用本地 AWS CLI 配置的账户和 us-east-1 region
new AwsomeShopStack(app, 'AwsomeShopStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: 'us-east-1' 
  },
  description: 'AWSomeShop - Employee Benefits E-commerce Platform',
});