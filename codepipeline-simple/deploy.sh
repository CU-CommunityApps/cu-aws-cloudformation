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

TARGET_TEMPLATE=template.yml

if [[ -z "$ENV" ]]; then
  echo 'ENV environment variable is not set. Please set to "dev" or "test" or "prod".'
  exit 1
fi

# Grab the version from the template metadata
TEMPLATE_VERSION=$(cfn-flip $TARGET_TEMPLATE | jq -r ".Metadata.Version")
STACK_NAME=$(cfn-flip $TARGET_TEMPLATE | jq -r ".Metadata.RecommendedStackName")
STACK_NAME=$(eval "echo $STACK_NAME")

echo "########## PROPERTIES ##########"
echo "Template: $TARGET_TEMPLATE"
echo "Depoying/Updating stack: $STACK_NAME"
echo "Deploying template version: $TEMPLATE_VERSION"

echo "########## LINT ##########"
cfn-lint $TARGET_TEMPLATE

echo "########## VALDIATE ##########"
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
  --no-fail-on-empty-changeset \
  $CAPABILITIES \
  --parameter-overrides \
      VersionParam="$TEMPLATE_VERSION" \
      EnvironmentParam="$ENV"

aws cloudformation update-termination-protection \
  --enable-termination-protection \
  --stack-name $STACK_NAME
