# iam-access-analyzer

This folder contains an AWS CloudFormation template that creates an IAM Role that IAM Access Analyzer can use to examine CloudTrail logs and generate IAM Policies based on actual usage.

## Contents

- [template.yaml](template.yaml) -- CloudFormation template that defines the the IAM Access Analyzer Role
- [deploy.sh](deploy.sh) -- Bash script to deploy the template

## Deploying the CloudFormation Template

### Option 1 - Manually

See [Creating a stack on the AWS CloudFormation console](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html) in the AWS CloudFormation documentation.

### Option 2 - With a Script

Setup the AWS CLI, and run the `deploy.sh` Bash script.

## Prerequisites for `deploy.sh` script

- AWS CLI
- `cfn-flip`: https://github.com/awslabs/aws-cfn-template-flip
- `jq`: https://stedolan.github.io/jq/
- `cfn-lint`: https://github.com/aws-cloudformation/cfn-python-lint