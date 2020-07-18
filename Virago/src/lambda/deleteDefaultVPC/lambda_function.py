#!/usr/bin/env python3

import boto3
import json
import os
import time

def aws_session(role_arn=None, session_name='my_session'):
    """
    If role_arn is given assumes a role and returns boto3 session
    otherwise return a regular session with the current IAM user/role
    """
    if role_arn:
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])
        return session
    else:
        return boto3.Session()


def lambda_handler(event,context):
    accountId = ""
    if 'accountId' in event:
        accountId=event['accountId']
    else:
        raise ValueError("No accountID provided")
    regionlist = []
    ec2regionlist=[]
    regionlist = []
    print("Current account: " + accountId)
    ROLE_ARN = 'arn:aws:iam::' + accountId +':role/TSI_Base_FullAccess'
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='s3dpcLambda')
    ec2client = session_assumed.client('ec2')
    ec2regionlist = ec2client.describe_regions()['Regions']
    for region in ec2regionlist:
        regionlist.append(region['RegionName'])
    for region in regionlist:
        print(region)
        client = session_assumed.client('ec2',region_name=region)
        response = client.describe_vpcs()
        #print(json.dumps(response))
        for vpc in response['Vpcs']:
            attachedsubnets = []
            attachedigws = []
            attachedrts = []
            attachedsgs = []
            if(vpc['IsDefault']):
                print("Default VPC found in {} with name {}".format(region,vpc['VpcId']))
                subnets = client.describe_subnets(Filters=[{'Name' : 'vpc-id','Values' : [ vpc['VpcId'] ] }])
                for subnet in subnets['Subnets']:
                    if subnet['VpcId'] == vpc['VpcId']:
                        attachedsubnets.append(subnet['SubnetId'])
                print("attached subnets")
                print(attachedsubnets)
                igws = client.describe_internet_gateways(Filters=[{'Name' : 'attachment.vpc-id','Values' : [ vpc['VpcId'] ] }])
                for igw in igws['InternetGateways']:
                    for attachment in igw['Attachments']:
                        if attachment['VpcId'] == vpc['VpcId']:
                            attachedigws.append(igw['InternetGatewayId'])
                print("attached internetgateways")
                print(attachedigws)
                rts = client.describe_route_tables(Filters=[{'Name' : 'vpc-id','Values' : [ vpc['VpcId'] ] }])
                for rt in rts['RouteTables']:
                    if rt['VpcId']==vpc['VpcId']:
                        for association in rt['Associations']:
                            attachedrts.append({'rtid' : association['RouteTableId'], 'associationid' : association['RouteTableAssociationId']})
                print("Route tables")
                print(attachedrts)
                sgs = client.describe_security_groups(Filters=[{'Name' : 'vpc-id','Values' : [ vpc['VpcId'] ] }])
                for sg in sgs['SecurityGroups']:
                    if sg['VpcId'] ==vpc['VpcId']:
                        attachedsgs.append(sg['GroupId'])
                #for sg in attachedsgs:
                #    print(sg)
                #    print(client.delete_security_group(GroupId=sg, DryRun=False))
                for igw in attachedigws:
                    print(client.detach_internet_gateway(DryRun=False,InternetGatewayId=igw,VpcId=vpc['VpcId']))
                    print(client.delete_internet_gateway( DryRun=False,InternetGatewayId=igw))
                for subnet in attachedsubnets:
                    print(client.delete_subnet(DryRun=False,SubnetId=subnet))
                #for attachedrt in attachedrts:
                #    print(client.disassociate_route_table( AssociationId=attachedrt['associationid']))
                #    print(client.delete_route_table(DryRun=False,RouteTableId=attachedrt['rtid']))
                print(client.delete_vpc(DryRun=False,VpcId=vpc['VpcId']))
