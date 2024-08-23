# marketplace-iam

This template creates an IAM policy (`deny-marketplace-changes-policy`) that denies changes to AWS Martketplace, including subscribing to Marketplace offerings. The template also creats a `shib-admin_no_market` IAM role that uses that policy to give the role full administrator access, excluding the AWS Marketplace.

See [IAM Resources for Limiting AWS Marketplace Access](https://confluence.cornell.edu/x/HrSCHw) in Cornell Confluence for more information.

**NOTE!** This role and policy are primary meant to dissuade AWS users from shooting themselves in the foot with respect to Marketplace changes. A knowledgeable user with `shib-admin_no_market` access can fairly easily circumvent the Marketplace restrictions built into that role.
