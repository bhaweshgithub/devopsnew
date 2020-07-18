import boto3
import json
import os

def lambda_handler(event,context):
    accountId = str(event['accountId'])
    counter = 0
    if 'mfaresponse' in event:
        counter = event['mfaresponse']['counter']+1
    #accountId = "144415869861"
    print("{} attempt".format(counter))
    stsclient = boto3.client('sts')
    accountRole='TSI_Base_FullAccess'
    roleArn = 'arn:aws:iam::' + accountId + ':role/' + accountRole
    role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountprovision')
    iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    iamresponse = iamclient.get_account_summary()
    return({'counter' : counter, 'iamresponse' : iamresponse})
