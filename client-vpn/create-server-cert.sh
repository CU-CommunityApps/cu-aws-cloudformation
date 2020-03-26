#!/bin/bash
# Creates and uploads a self-signed server certificate for AWS Client VPN to use

git clone https://github.com/OpenVPN/easy-rsa.git /tmp/easy-rsa
cd /tmp/easy-rsa/easyrsa3
./easyrsa init-pki
./easyrsa build-ca nopass
./easyrsa build-server-full server nopass
aws acm import-certificate --certificate file://pki/issued/server.crt --private-key file://pki/private/server.key --certificate-chain file://pki/ca.crt --region us-east-1 --tags Key=Name,Value=demo-client-vpn-cert
