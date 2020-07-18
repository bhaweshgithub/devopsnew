#This python script must be on the devsecops account
#It will check if the event coming from s3 events, also check the dynamodb table in master accont if the featureLevel is full
#it creates
#masteraccountid, and s3dpcmgmtrole must be added for environment variables

import json
import boto3
import logging
from io import BytesIO
from gzip import GzipFile
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import os
import re

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

def processS3Entry(entry,list_interesting_eventnames,accountconfiguration):
    account = entry['recipientAccountId']
    confidential_kms_key_arn = accountconfiguration['confidentialKMSKey']
    if (entry['userIdentity']['type'] == 'AssumedRole'):
        regexp = re.compile('(.*)TSI_Base(.*)',re.IGNORECASE)
        print(regexp.match(entry['userIdentity']['sessionContext']['sessionIssuer']['arn']))

        if((regexp.match(entry['userIdentity']['sessionContext']['sessionIssuer']['arn'])) is not None) :
            return 'bailing because of recursion danger'
    ROLE_ARN = 'arn:aws:iam::' + account +':role/' + os.environ['s3dpcmgmtrole']
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='my_lambda')
    client = session_assumed.client('s3')
    try:
        tags = client.get_bucket_tagging(
            Bucket=entry['requestParameters']['bucketName']
            )
    except ClientError as e:
        #print(e.response)
        if e.response['Error']['Code'] == 'NoSuchTagSet':
             tagsetExists=False
    else:
        tagsetExists=True
    if (tagsetExists):
        for tag in tags['TagSet']:
            #We have DPC tag
            if tag['Key'] == 'DPC':
                dpcexists=True
                dpc=tag['Value']
                #tag is internal
                if ((dpc.lower() == 'internal')):
                    try:
                        encryption = client.get_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName']
)
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                            encryption = "none"
                    else:
                        for serversideenc in encryption['ServerSideEncryptionConfiguration']['Rules']:
                            if ((serversideenc['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != 'AES256') or (serversideenc['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != 'aws:kms')):
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
                    if ((encryption=="none")):
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
                    result = client.get_bucket_acl(Bucket=entry['requestParameters']['bucketName'])
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            client.put_bucket_acl(ACL='private',Bucket=entry['requestParameters']['bucketName'])
                #tag is confidential
                elif ((dpc.lower() == 'confidential')):
                    try:
                        encryption = client.get_bucket_encryption(
    Bucket=event['detail']['requestParameters']['bucketName']
)
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                            encryption = "none"
                    else:
                        print(encryption)
                        for serversideenc in encryption['ServerSideEncryptionConfiguration']['Rules']:
                            if serversideenc['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != 'aws:kms':
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': confidential_kms_key_arn
                }
            },
        ]
    }
)
                    if ((encryption=="none")):
                                print("Here comes aes")
                                client.put_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': confidential_kms_key_arn
                }
            },
        ]
    }
)
                    result = client.get_bucket_acl(Bucket=entry['requestParameters']['bucketName'])
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            client.put_bucket_acl(ACL='private',Bucket=event['detail']['requestParameters']['bucketName'])
                #tag is open so can be public
                elif (dpc.lower() == 'public'):
                    result = client.get_bucket_acl(Bucket=entry['requestParameters']['bucketName'])
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            print("THIS IS FULLY OPEN!")
                elif (dpc == 'open'):
                    result = client.get_bucket_acl(Bucket=entry['requestParameters']['bucketName'])
                    try:
                            encryption = client.get_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName']
)
                    except ClientError as e:
                            #print(e.response)
                            print("No encryption found and it's okay")
                    else:
                            print("It's encrypted, leaving as is it")
                    for grants in result['Grants']:
                        if((grants['Grantee']['Type']=='Group') and (grants['Grantee']['URI']=='http://acs.amazonaws.com/groups/global/AllUsers')):
                            client.put_bucket_acl(ACL='private',Bucket=entry['requestParameters']['bucketName'])
                #dpc is not internal confidential or open
                else:
                    print("neither")
                    encryption = client.get_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName']
)
                    for rules in encryption['ServerSideEncryptionConfiguration']['Rules']:
                        if rules['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] != "AES256":
                            client.put_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)
                    client.put_bucket_acl(ACL='private',Bucket=entry['requestParameters']['bucketName'])
                    buckettags = client.get_bucket_tagging(Bucket=entry['requestParameters']['bucketName'])
                    for idx, tagitem in enumerate(buckettags['TagSet']):
                        if tagitem['Key'] == 'DPC':
                            buckettags['TagSet'][idx]['Value'] = 'Internal'
                    client.put_bucket_tagging(Bucket=entry['requestParameters']['bucketName'],
    Tagging={ 'TagSet' : buckettags['TagSet'] }
)
        if (not dpcexists):
            print("No DPC tagset adding private acl, and dpc tagset to the bucket")
            client.put_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)

            client.put_bucket_acl(ACL='private',Bucket=entry['requestParameters']['bucketName'])
            buckettags = client.get_bucket_tagging(Bucket=entry['requestParameters']['bucketName'])
            #print(buckettags)
            buckettags['TagSet'].append({
                'Key': 'DPC',
                'Value': 'Internal'
            })
            client.put_bucket_tagging(Bucket=entry['requestParameters']['bucketName'],
    Tagging= { 'TagSet' : buckettags['TagSet'] }
)
    else:
        print("No tagset adding one to the bucket")
        client.put_bucket_encryption(
    Bucket=entry['requestParameters']['bucketName'],
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            },
        ]
    }
)

        client.put_bucket_acl(ACL='private',Bucket=entry['requestParameters']['bucketName'])
        client.put_bucket_tagging(Bucket=entry['requestParameters']['bucketName'],
    Tagging={
        'TagSet': [
            {
                'Key': 'DPC',
                'Value': 'Internal'
            },
        ]
    }
)





def getAccountConfiguration(s3accountid):
    ROLE_ARN = 'arn:aws:iam::' + os.environ['masteraccountid'] + ':role/TSI_Base_DynamoDB_Read'
    print(ROLE_ARN)
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='dynamoquery')
    print(session_assumed)
    client = session_assumed.resource('dynamodb',region_name='eu-central-1')
    accounts_table = client.Table('accounts')
    result = accounts_table.query(KeyConditionExpression=Key('accountId').eq(s3accountid))
    print(result)
    return(result['Items'][0])

def lambda_handler(event, context):
    accountconfiguration = getAccountConfiguration(event['recipientAccountId'])
    if(accountconfiguration['featureLevel']=='full'):
        list_interesting_eventnames= ["DeleteBucketCors", "DeleteBucketTagging", "CreateBucket", "PutBucketAcl","PutBucketCors","PutBucketPolicy","PutBucketTagging", "PutBucketWebsite","DeleteBucketEncryption" ]
        processS3Entry(event,list_interesting_eventnames,accountconfiguration)
    else:
        print("Advanced features are disabled in dynamodb")


