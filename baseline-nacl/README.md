# baseline-nacl

This is an AWS CloudFormation template to create a somewhat reasonable Network ACL for a VPC. However, we recommend reviewing the ingress and egress rules to make it as strict as possible for your own needs.

Once the Network ACL is created, you must associate it with target subnets.

See [Baseline AWS Network ACL](https://confluence.cornell.edu/x/rFL_Ew).

Note! The NACL created by this template can support a VPC with CIDR block(s) in the `100.64.0.0/10` range. If this is your situation, you will need to request a NACL rule quota increase since the number of outbound rules is greater than the default 20 rule quota before using this template. See https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-nacls.
