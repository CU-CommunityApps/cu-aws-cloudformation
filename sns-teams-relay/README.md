# sns-teams-relay

CloudFormation template for creating a Lambda function to relay SNS messages to Microsoft Teams.

The Lambda attempts to provide decent formatting for these specific types of AWS notifications:
- SNS with plain `subject` and `message` fields
- `CodeBuild Build State Change`
- `CodeBuild Build Phase Change`
- `CodePipeline Pipeline Execution State Change`
- `CodePipeline Action Execution State Change`
- CodePipeline Manual Approval notifications
- CloudWatch Alarm notifications (Alarm, OK, Insufficient Data)

See [tf-module-sns-teams-relay](https://github.com/CU-CommunityApps/tf-module-sns-teams-relay) for a Terraform module to deploy similar functionality with Terraform.

## Contents

- [deploy.sh](deploy.sh) -- Bash script to deploy the template
- [invoke.sh](invoke.sh) -- Bash script to invoke the Lambda with example data
- [template.yaml](template.yaml) -- CloudFormation template
- [example-notifications](example-notifications/) -- Examples of SNS and message content

## Change Log

### v4.0.0
- Breaking changes! Switched to using Secrets Manager to retrieve Teams Webhook URLs.
- Remove `TeamsWebhookNormalURLParam`
- Remove `TeamsWebhookAlertURLParam`
- Simplified template and deployment script by using pre-zipped Lambda source.

### v3.0.0
- Breaking changes! Handle just a single SNS topic for each parameter, instead of a list. The template now creates SNS Subscriptions and Lambda Permissions for the SNS topics provided in the parameters. 
- replace `AlarmSNSTopicsNormal` parameter with `AlarmSNSTopicNormal`
- replace `AlarmSNSTopicsAlert` parameter with `AlarmSNSTopicAlert`
- add `GenericSNSTopicNormal` parameter
- add `GenericSNSTopicAlert` parameter
- add `AWS::SNS::Subscription` resources for each of the SNS topics in the parameters
- add `AWS::Lambda::Permission` resources for each of the SNS topics in the parameters

### v2.2.0
- minor change to generic SNS message display format to allow markdown-formatted message payloads to display better in Teams

### v2.1.1
- add support for handling CloudWatch alarms messages
- add `AlarmSNSTopicsNormal` parameter
- add `AlarmSNSTopicsAlert` parameter
- add `StrftimeFormatParam` parameter
- jumping to v2.1.1. instead of v2.1.0 to match corresponding version in https://github.com/CU-CommunityApps/tf-module-sns-teams-relay

### v2.0.0
- apply some Python style fixes
- add support for two different webhook URLs; one handles regular notifications, one handles more critical notifications
- add support for contextual colors, depending on notification type

### v1.0.0
- initial release

## Prerequisites for `deploy.sh` and `invoke.sh` script

- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and an active session with privileges to create/manage CloudFormation stacks and store data in an S3 bucket
- `cfn-flip`: https://github.com/awslabs/aws-cfn-template-flip
- `jq`: https://stedolan.github.io/jq/
- `cfn-lint`: https://github.com/aws-cloudformation/cfn-python-lint

## Deploy

1. Create new SNS topics (or find the ARNs of existing topics) that you want to use for these parameters:
  - AlarmSNSTopicNormal
  - AlarmSNSTopicAlert
  - GenericSNSTopicNormal
  - GenericSNSTopicAlert
2. Replace the default vaules for these parameters in `template.yaml`. You can also leave these parameters empty.
1. Create a secret in Secrets Manager to hold the Teams webhook URLs. This secret should contain a `alerts_channel` value and a `notifications_channel` value. 
1. Customize the following references to the secret in `template.yaml`. Change `/teams.microsoft.com/CHANGE_ME/webhooks` to whatever you named your secret. Find and update the following values:
  - `{{resolve:secretsmanager:/teams.microsoft.com/CHANGE_ME/webhooks:SecretString:alerts_channel}}`
  - `{{resolve:secretsmanager:/teams.microsoft.com/CHANGE_ME/webhooks:SecretString:notifications_channel}}`

1. Run `./deploy.sh`
1. To test the deployment, run `./invoke.sh` to send a test message to the Lambda function. This should trigger a new message to the target Teams channel (via the webhook).
