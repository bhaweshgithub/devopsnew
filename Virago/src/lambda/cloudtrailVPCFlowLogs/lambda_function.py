#This python script must be on the devsecops account
#It will check if the event coming from vpc events, also check the dynamodb table in master accont if the featureLevel is full
#it creates vpc flow log if we don't have one for this vpc
#masteraccountid, and s3_flowlogbucketname must be presented, alos flowlogmgmtrole

import json
import boto3
import logging
from io import BytesIO
from gzip import GzipFile
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import os

def aws_session(role_arn=None, session_name='my_session'):
    """
    If role_arn is given assumes a role and returns boto3 session
    otherwise return a regular session with the current IAM user/role
    """
    if role_arn:
        print("starting sts")
        client = boto3.client('sts')
        response = client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
        session = boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken'])
        return session
    else:
        return boto3.Session()

def getFlowLogsVPCId(flowlogid):
    ROLE_ARN = 'arn:aws:iam::' + os.environ['masteraccountid'] +':role/TSI_Base_DynamoDB_flowlog_RW'
    print(ROLE_ARN)
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='dynamoquery')
    print(session_assumed)
    client = session_assumed.resource('dynamodb',region_name='eu-central-1')
    accounts_table = client.Table('flowlogs')
    result = accounts_table.query(KeyConditionExpression=Key('FlowLogId').eq(flowlogid))
    print(result)
    if (len(result['Items']) > 0):
        print("Got {}".format(result['Items'][0]['VpcId']))
        return(result['Items'][0]['VpcId'])
    else:
        return("NULL")


def addFlowLogIdToDynamodB(accountid,vpcid,flowlogid):
    ROLE_ARN = 'arn:aws:iam::' + os.environ['masteraccountid'] +':role/TSI_Base_DynamoDB_flowlog_RW'
    print(ROLE_ARN)
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='dynamoquery')
    print(session_assumed)
    client = session_assumed.client('dynamodb',region_name='eu-central-1')
    accounts_table = client.put_item(TableName='flowlogs',
            Item={ 'FlowLogId' : {'S': flowlogid }, 'VpcId' : {'S': vpcid }, 'accountId' : {'S': accountid }  }
            )


def vpcCreationCheck(vpcid,region,accountid):
    loggingtag = ""
    print(vpcid)
    ROLE_ARN = 'arn:aws:iam::' + accountid +':role/' + os.environ['flowlogmgmtrole']
    print(ROLE_ARN)
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='vpccheck')
    print(session_assumed)
    client = session_assumed.client('ec2',region_name=region)
    print("Session assumed")
    vpcs = client.describe_vpcs( VpcIds = [vpcid])
    print(vpcs)
    for vpc in vpcs['Vpcs']:
        for vpctag in vpc['Tags']:
            if vpctag['Key'] == 'logging' :
                loggingtag = vpctag['Value']
    if(loggingtag==""):
        client.create_tags(Resources=[vpcid], Tags=[{'Key': 'logging', 'Value' : 'true'}])
        loggingtag='true'
    return(loggingtag)


def enforceFlowLog(vpcid,region,accountid):
    #we check if flow log is enabled for vpc if not create one
    #vpcid = vpcresponse['vpc']['vpcId']
    ROLE_ARN = 'arn:aws:iam::' + accountid +':role/' + os.environ['flowlogmgmtrole']
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='vpccheck')
    client = session_assumed.client('ec2',region_name=region)
    flowlogs = client.describe_flow_logs(Filters=[{'Name': 'resource-id','Values' : [vpcid]}])
    if(len(flowlogs['FlowLogs']) == 0):
        print("we need to create flowlog")
        response = client.create_flow_logs( ResourceIds=[vpcid],TrafficType='ALL', ResourceType='VPC',LogDestinationType='s3',LogDestination="arn:aws:s3:::" + os.environ['s3_flowlogbucketname'] )
        print(response)
        if (len(response['FlowLogIds']) > 0):
            addFlowLogIdToDynamodB(accountid,vpcid,response['FlowLogIds'][0])
        else:
            print("No flow log created")

    else:
        print("Flow logs already present for this vpc")

def deleteFlowLogEntry(flowlogid):
    #Here we need to delete the old entry of the flowlog
    print("Deleting flowlog entry for {}".format(flowlogid))
    ROLE_ARN = 'arn:aws:iam::' + os.environ['masteraccountid'] +':role/TSI_Base_DynamoDB_flowlog_RW'
    print(ROLE_ARN)
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='dynamoquery')
    print(session_assumed)
    client = session_assumed.client('dynamodb',region_name='eu-central-1')
    accounts_table = client.delete_item(TableName='flowlogs',
            Key={ 'FlowLogId' : {'S': flowlogid }}
            )
    print(accounts_table)


def eventDeletedFlowLog(flowlogid,region,accountid):
    #Flow log deleted, we need to check tagging, dynamodb for vpcid
    #also we need to check if the flowlog was our one
    vpcid = getFlowLogsVPCId(flowlogid)
    if vpcid=="NULL":
        print("No vpc found, not our flowlog")
    else:
        loggingtag = vpcCreationCheck(vpcid,region,accountid)
        if loggingtag=='true':
            print("Enforcing flow log")
            enforceFlowLog(vpcid,region,accountid)
            deleteFlowLogEntry(flowlogid)
        else:
            print("Logging disabled for this vpc")




def processVPCEntry(entry,list_interesting_eventnames):
    print(entry['eventSource'])
    if((entry['eventSource'] == 'ec2.amazonaws.com') and (entry['eventName'] in list_interesting_eventnames)):
        print("Found event")
        if((entry['eventName']=='CreateVpc') or ( entry['eventName']=='CreateDefaultVpc')):
            print("checking loggingtags")
            loggingtag = vpcCreationCheck(entry['responseElements']['vpc']['vpcId'],entry['awsRegion'],entry['recipientAccountId'])
            if loggingtag=='true':
                print("Enforcing flow log")
                enforceFlowLog(entry['responseElements']['vpc']['vpcId'],entry['awsRegion'],entry['recipientAccountId'])
            else:
                print("Logging disabled for this vpc by tag")
    elif((entry['eventSource'] == 'ec2.amazonaws.com') and ( entry['eventName'] == 'DeleteFlowLogs')):
        #Flow log deleted, we need to check if this was our flowlog
        eventDeletedFlowLog(entry['requestParameters']['flowLogId'][0],entry['awsRegion'],entry['recipientAccountId'])
    else:
        print("Event not found")


def checkFeatureLevel(vpcaccountid):
    ROLE_ARN = 'arn:aws:iam::' + os.environ['masteraccountid'] +':role/TSI_Base_DynamoDB_Read'
    print(ROLE_ARN)
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='dynamoquery')
    print(session_assumed)
    client = session_assumed.resource('dynamodb',region_name='eu-central-1')
    accounts_table = client.Table('accounts')
    result = accounts_table.query(KeyConditionExpression=Key('accountId').eq(vpcaccountid))
    print(result)
    print("Got {}".format(result['Items'][0]['featureLevel']))
    return(result['Items'][0]['featureLevel'])

def lambda_handler(event, context):
    if(checkFeatureLevel(event['recipientAccountId'])=='full'):
        list_interesting_eventnames= ["CreateDefaultVpc", "CreateVpc"]
        processVPCEntry(event,list_interesting_eventnames)
    else:
        print("Advanced features are disabled in dynamodb")

