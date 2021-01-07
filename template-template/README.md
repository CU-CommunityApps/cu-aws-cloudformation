# CloudFormation Template Template

A template for CloudFormation templates and a "smart" script to deploy it.

## Contents

- [template.yaml](template.yaml) -- a template to use as a starting point for new CloudFormation templates.
- [deploy.sh](deploy.sh) -- Bash script to deploy the template

## Prerequisites for `deploy.sh` script

- AWS CLI
- `cfn-flip`: https://github.com/awslabs/aws-cfn-template-flip
- `jq`: https://stedolan.github.io/jq/
- `cfn-lint`: https://github.com/aws-cloudformation/cfn-python-lint