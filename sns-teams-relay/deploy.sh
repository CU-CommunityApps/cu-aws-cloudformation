#!/bin/bash
#
# Script to create/update CloudFormation stack from a template.
#
# Original Source:  https://github.com/CU-CommunityApps/cu-aws-cloudformation/template-template/deploys.sh
#
# Prerequisites:
#   - AWS CLI
#   - cfn-flip: https://github.com/awslabs/aws-cfn-template-flip
#   - jq: https://stedolan.github.io/jq/
#   - cfn-lint: https://github.com/aws-cloudformation/cfn-python-lint

ENV=${ENV:-dev}

TARGET_TEMPLATE=template.yaml

# Grab the version from the template metadata
TEMPLATE_VERSION=$(cfn-flip $TARGET_TEMPLATE | jq -r ".Metadata.Version")
STACK_NAME=$(cfn-flip $TARGET_TEMPLATE | jq -r ".Metadata.RecommendedStackName")
STACK_NAME=$(eval "echo $STACK_NAME")

echo "########## PROPERTIES ##########"
echo "Template: $TARGET_TEMPLATE"
echo "Deploying/Updating stack: $STACK_NAME"
echo "Deploying template version: $TEMPLATE_VERSION"

echo "########## LINT ##########"
cfn-lint $TARGET_TEMPLATE

echo "########## VALIDATE ##########"
set -e # Stop the script if it doesn't validate.
aws cloudformation validate-template --template-body file://$TARGET_TEMPLATE

# Uncomment other CAPABILITY values as needed
# CAPABILITIES=""
# CAPABILITIES="--capabilities CAPABILITY_IAM"
CAPABILITIES="--capabilities CAPABILITY_NAMED_IAM"

echo "########## DEPLOY ##########"
aws cloudformation deploy \
  --template-file $TARGET_TEMPLATE \
  --stack-name $STACK_NAME \
  $CAPABILITIES \
  --no-fail-on-empty-changeset \
  --parameter-overrides \
      VersionParam="$TEMPLATE_VERSION" \
      EnvironmentParam="$ENV"

aws cloudformation update-termination-protection \
  --enable-termination-protection \
  --stack-name $STACK_NAME

ARN=$(aws lambda get-function --function-name  sns-teams-relay-${ENV} --query Configuration.FunctionArn --output text)

echo "Lambda Function ARN: ${ARN}"
