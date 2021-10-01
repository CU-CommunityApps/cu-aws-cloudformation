# sns-teams-relay

CloudFormation template for creating a Lambda function to relay SNS messages to Microsoft Teams.

The Lambda attempts to provide decent formatting for these specific types of AWS notifications:
- SNS with plain `subject` and `message` fields
- `CodeBuild Build State Change`
- `CodeBuild Build Phase Change`
- `CodePipeline Pipeline Execution State Change`
- `CodePipeline Action Execution State Change`
- CodePipeline Manual Approval notifications

See [tf-module-sns-teams-relay](https://github.com/CU-CommunityApps/tf-module-sns-teams-relay) for a Terraform module to deploy similar functionality with Terraform.

## Contents

- [deploy.sh](deploy.sh) -- Bash script to deploy the template
- [invoke.sh](invoke.sh) -- Bash script to invoke the Lambda with example data
- [template.yaml](template.yaml) -- CloudFormation template
- [example-notifications](example-notifications/) -- Examples of SNS and message content

## Prerequisites for `deploy.sh` and `invoke.sh` script

- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and an active session with priviledges to create/manage CloudFormation stacks and store data in an S3 bucket
- `cfn-flip`: https://github.com/awslabs/aws-cfn-template-flip
- `jq`: https://stedolan.github.io/jq/
- `cfn-lint`: https://github.com/aws-cloudformation/cfn-python-lint

## Deploy

1. Customize the following variables in [deploy.sh](deploy.sh):
  - `WEBHOOK_URL`: The URL for your Teams webhook
  - `S3_BUCKET`: Any S3 bucket that you have write priviledges to. Used as temporary storage during the `aws cloudformation package` and `aws cloudformation deploy` processes.
2. Run `./deploy.sh`
3. To test the deployment, run `./invoke.sh` to send a test message to the Lambda function. This should trigger a new message to the target Teams channel (via the webhook).

## Configure Messaging
1. Create a new (or choose an existing) SNS topic to which messages for Teams will be sent. See [Creating an Amazon SNS topic](https://docs.aws.amazon.com/sns/latest/dg/sns-create-topic.html).
2. Create a subscription to that SNS topic with the Lambda Function ARN as the target. See [How do I subscribe a Lambda function to an Amazon SNS topic in the same account?](https://aws.amazon.com/premiumsupport/knowledge-center/lambda-subscribe-sns-topic-same-account/).
3. (Optional) Send a test message to the SNS topic. See [Amazon SNS message publishing](https://docs.aws.amazon.com/sns/latest/dg/sns-publishing.html).
