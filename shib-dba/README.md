# shib-dba

The [shib-dba-role-with-assume-role.yaml] CloudFormation template creates a shib-dba IAM role in an AWS account that also gives access to the Cornell CIT DBA team to use that role programmatically, via cross account permissions.

The [instance-profile.yaml] CloudFormation template was used by the Cornell CIT DBA team to setup the role they use to assume the shib-dba roles in other accounts.

The [assume-role.sh] script is an example script that would be used by the Cornell CIT DBA team to exercise those cross-account privileges.


