import boto3
import secrets
import datetime
import time
import json
from dateutil.tz import tzlocal

def createRealAccountViragoMaster(accountname, accountemail,organizations,viragomaster):
    print("Now creating the account")
    if(viragomaster==True):
        createresponse = organizations.create_account(
            Email=accountemail,
            AccountName=accountname,
            RoleName='TSI_Base_FullAccess',
            IamUserAccessToBilling='DENY'
        )
    else:
         createresponse = organizations.create_account(
            Email=accountemail,
            AccountName=accountname,
            IamUserAccessToBilling='DENY'
        )
    response = {}
    response['CreateAccountStatus']={}
    response['CreateAccountStatus']['State']=createresponse['CreateAccountStatus']['State']
    response['CreateAccountStatus']['Id']=createresponse['CreateAccountStatus']['Id']
    response['CreateAccountStatus']['AccountName']=createresponse['CreateAccountStatus']['AccountName']
    if(createresponse['CreateAccountStatus']['State']=='SUCCEEDED'):
        response['CreateAccountStatus']['AccountId']=createresponse['CreateAccountStatus']['AccountId']
    if(createresponse['CreateAccountStatus']['State']=='FAILED'):
        if(createresponse['CreateAccountStatus']['FailureReason']=='CONCURRENT_ACCOUNT_MODIFICATION'):
            createresponse['CreateAccountStatus']['FailureReason']='INTERNAL_FAILURE'
    return(response)

def lambda_handler(event, context):
    print(event)
    if 'customermasteraccountid' in event:
        viragomaster=False
        stsclient = boto3.client('sts')
        accountRole='TSI_Base_FullAccess'
        roleArn = 'arn:aws:iam::' + event['customermasteraccountid'] + ':role/' + accountRole
        role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountcreation')
        organizations = boto3.client('organizations',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        print(role)
    else:
        viragomaster=True
        organizations = boto3.client('organizations')
        print(organizations)
    accountResponse = createRealAccountViragoMaster(event['accountname'],event['accountemail'],organizations,viragomaster)
    return(accountResponse)
