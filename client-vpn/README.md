# client-vpn

Example deployment of AWS Client VPN

## AWS Client VPN with Directory Authentication

### Prerequisites

#### AWS Directory 

This example uses directory-based authentication, so you will need some form of an [AWS Directory](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/what_is.html) in the same VPC where you are deploying the Client VPC Endpoint. This can be an [AD Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_ad_connector.html) linked to the main Cornell Active Directory.

#### AWS Direct Connect

If you want this example to provide functional access to public networks on the Cornell campus or to private networks on the Cornell campus, the VPC to which you are deploying this should be a [Cornell Standard VPC](https://blogs.cornell.edu/cloudification/2017/05/09/the-cornell-standard-aws-vpc-2-0/) with Direct Connect enabled, and with ["hybrid"](https://confluence.cornell.edu/display/CLOUD/AWS+Direct+Connect+Routing+Diagrams#AWSDirectConnectRoutingDiagrams-HybridRouting) or ["all-campus"](https://confluence.cornell.edu/display/CLOUD/AWS+Direct+Connect+Routing+Diagrams#AWSDirectConnectRoutingDiagrams-%22AllCampus%22Routing) routing configured for it. 

#### Linux or Linux-like Command Line 

The script(s) here require `git` and `bash`.

#### AWS CLI

The AWS CLI is used to import a server certificate into AWS Certificate Manager. If you don't have the AWS CLI installed and credentials configured, you can import using the AWS web console instead.

### Deploying AWS Client VPN with Directory Authentication

#### 1. Server Certificate

Client VPN requires you to provide a server certificate for it to use.

1. Ensure your AWS CLI credentials are configured and valid.
1. In a shell, execute `./create-server-cert.sh`. There is one point in this script where your input is required. You can just hit \<enter\> to continue with the default.
1. When the script completes, it will output a `CertificateArn`. You will need this value for the CloudFormation template.

If this script does not work for you, you can follow the directions for creating a server certificate in the [Mutual Authentication](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/authentication-authorization.html#mutual) section of the ["Client Authentication and Authorization" page in the AWS Client VPN documentation](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/authentication-authorization.html).

#### 2. Collect Required Parameter Values

Gather the following information for use by the CloudFormation template in the next step.
  
`VPCParam` - The ID of the VPC into which the Client VPN endpoint will be deployed. Ideally, this is a Cornell Standard VPC with Direct Connect configured.
    
`VPCSubnetParam` - The ID of a subnet in the VPC to which the Client VPN endpoint will be deployed (i.e., in `VPCParam`). If deploying to a Cornell Standard VPC, use a private subnet for this parameter.

`PeeredVPCCIDRParam` - This is optional. If you provide the CIDR block of a VPC peered to `VPCParam`, then the Client VPN will be configured to give Client VPN clients access to that VPC.

`DirectoryIdParam` - The ID of the AWS Directory to use for authentication. Format is d-XXXXXXXXXX. This directory should deployed in `VPCParam`.

`DirectorySecurityGroupParam` - The ID of the security group assigned to the directory (`DirectoryIdParam`) you are using. This security group needs to be added to the Client VPN endpoint deployment so the VPN endpoint can access the directory. This is hard to find in the AWS web console. Use this CLI command to find it: `aws ds describe-directories`.

`ServerCertificateParam` - The ARN of a server certificate stored in AWS Certificate Manager. This value is the `CertificateArn` from the previous step.

`ClientVPNCIDRParam` - This is the CIDR block assigned to clients connected to the Client VPN. This parameter defaults to 172.32.0.0/22. You shouldn't have to change it UNLESS the CIDR block of your `VPCParam` overlaps with 172.32.0.0/22.

`RoutingTypeParam` - This paremter defines which routes are included in your Client VPN. This determines what networks clients connected to the Client VPN can access.

- `none` - no routing is configured; VPN clients will only be able to access the `VPCParam` VPC and the peered VPC (if you have provided a value for `ClientVPNCIDRParam`)
- `campus-public` - configures routing for clients to reach public IP addresses on campus (via Direct Connect)
- `campus-private` - configures routing for clients to reach the entirety of te Cornell private network (10.0.0.0/8) via Direct Connect, except for private network space in AWS.

#### 3. CloudFormation Template

Use the AWS web console or CLI, create a new CloudFormation stack using the `client-vpn-with-directory.yml` template. You will need to provide the parameter values you determined above.

The stack will take several minutes to create.


#### 4. Connect to the Client VPN as a Client

The following procedure is valid only when connecting from a network location not in the Cornell private or public IP address space.

1. Be sure your client workstation is not connected to any other VPN.
2. Navigate to the [Client VPN web console](https://console.aws.amazon.com/vpc/home?region=us-east-1#ClientVPNEndpoints:sort=clientVpnEndpointId)
3. Select the `demo-client-vpn`.
4. Click on `Download Client Configuraion`. Be sure to note where the `.ovpn` file is saved.
5. Now, navigate to https://aws.amazon.com/vpn/client-vpn-download/.
6. Download and install a Client VPN client appropriate to your system type.
7. Follow these instructions for using the AWS Client VPN Client: https://docs.aws.amazon.com/vpn/latest/clientvpn-user/connect-aws-client-vpn-connect.html
8. When you connect, you will be asked for a username and credentials known to the directory you used in the Client VPN deployment.

## Notes

### Cornell VPN

AWS Client VPN is NOT a direct replacement for [Cornell VPN](https://it.cornell.edu/cuvpn). The configuration options and limitations of Client VPN are limited and it is nearly impossible to duplicate all the configuration of Cornell VPN in AWS Client VPN. However, there may be specific use cases where an AWS Client VPN deployment may fill needs better than Cornell VPN.

### Split Tunneling 
This example deployment uses a split tunnel so that only traffic targeted to the local VPC, Cornell campus public IPs, or Cornell private networks flows through the VPN from the client. Traffic for other IPs do not use the Client VPN. See [Split-Tunnel on AWS Client VPN Endpoints](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/split-tunnel-vpn.html).

### Access Restrictions

This example deployment configures very broad network access for VPN clients. However, the Client VPN can support restrictive network access models, and also models that authorize specific access depending on directory group memebership. See https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/scenario.html and https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-rules.html.

### Mutual Authentication

Client VPNs can be configured to use certificate-based authentication, thus dispensing with the need for a directoy. However, certificate-based authentication requires careful certificate management and secure distribution, so it can be hard to implement logistically, depending on number of types of users.

### Route Limits

Each Client VPN can have only 10 routes and those routes cannot specify overlapping CIDR blocks. 

Since the CIDR block of the VPCs to which the Client VPN is associated are automatically added to the VPN routes, you cannot add a route for a large CIDR block that includes the VPC CIDR block. E.g., if we have associated the VPN with a VPC having CIDR block 10.92.76.0/22, then we CANNOT add a single route for 10.0.0.0/8 if we want to route to all other addresses in 10.0.0.0/8. Instead we need to break 10.0.0.0/8 into sub-blocks that represents 10.0.0.0/8 with 10.92.76.0/22 removed. This is why the example deployment here does not offer to route both private Cornell network space and public Cornell campus IPs at the same time. We run into the route limit.