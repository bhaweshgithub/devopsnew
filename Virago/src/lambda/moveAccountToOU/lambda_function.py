import boto3
import secrets
import datetime
import time
import json
from dateutil.tz import tzlocal

def moveAccountToOU(accountid,organizations,ouid):
    parentid = []
    parentresponse = organizations.list_parents(ChildId=accountid)
    for parent in parentresponse['Parents']:
        parentid.append(parent['Id'])
    while ('NextToken' in parentresponse):
        for parent in parentresponse['Parents']:
            parentid.append(parent['Id'])
    if (len(parentid) > 1):
        raise SystemExit("Multiple parent found, and we don't handle it") 
    #Moving from old parent to new parent if not the same :)
    if (parentid[0] != ouid):
        moveresponse = organizations.move_account(AccountId=accountid,SourceParentId=parentid[0],DestinationParentId=ouid)
        return(moveresponse)
    else:
        return("Not moved as old and new parent are the same")


def lambda_handler(event, context):
    print(event)
    if ('accountcreate' in event):
        accountId = event['accountcreate']['CreateAccountStatus']['AccountId']
    else:
        accountId = event['accountId']
    if 'customermasteraccountid' in event:
        stsclient = boto3.client('sts')
        accountRole='TSI_Base_FullAccess'
        roleArn = 'arn:aws:iam::' + event['customermasteraccountid'] + ':role/' + accountRole
        role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountcreation')
        organizations = boto3.client('organizations',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        print(role)
    else:
        organizations = boto3.client('organizations')
        print(organizations)
    OuMoveResponse = moveAccountToOU(accountId,organizations,event['ouid'])
    print(OuMoveResponse)
    return(OuMoveResponse)
