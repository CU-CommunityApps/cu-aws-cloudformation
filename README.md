# cu-aws-cloudformation

This repo is a collection of standard, official templates used by the Cornell CIT Cloud DevOps Team.

- [baseline-nacl](baseline-nacl) creates a standard baseline network access control list for AWS VPCs
- [client-vpn](client-vpn) example deployment of Client VPN
- [iam-access-analyzer](iam-access-analyzer) creates an IAM Role that IAM Access Analyzer can use to examine CloudTrail logs and generate IAM Policies based on actual usage
- [ses](ses) creates IAM policy and user group for sending email using SES
- [shib-dba](shib-dba) creates an IAM Role that grants privileges for DBAs to function within AWS with RDS, EC2, etc.
- [shib-ec2emr](shib-ec2emr) creates an IAM Role that grants privileges that would be useful to data scientists.
- [shib-tagged](shib-tagged) creates an IAM role showing how to control access via tagging of resources
- [sns-teams-relay](sns-teams-relay) creates a Lambda function to relay SNS messages to Microsoft Teams
- [standard-vpc](standard-vpc) creates a Cornell Standard VPC
- [template-template](template-template) -- a standard starting point for new CloudFormation templates, including a helpful script
