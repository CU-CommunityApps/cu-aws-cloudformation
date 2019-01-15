# baseline-nacl

This is an AWS CloudFormation template to create a somewhat reasonable Network ACL for a VPC. However, we recommend reviewing the ingress and egress rules to make it as strict as possible for your own needs.

Once the Network ACL is created, you must associate it with target subnets.
