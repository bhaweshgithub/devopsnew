import json
import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    accountId = str(event['accountId'])
    description = str(event['description'])
    entry = {'accountNr' : accountId, 'description' : description, 'readonlyRole' : 'TSI_Base_ReadOnlySwitchRole', 'writeRole' : 'TSI_Base_FullAccess'}
    try:
        accountids = json.loads(s3.get_object(
        Bucket=os.environ['provbucketname'],
        Key='accounts.json')['Body'].read())
    except:
        print("File couldn't be opened, assuming new file")
        accountids = []
        accountids.append(entry)
        s3.put_object(
            Bucket=os.environ['provbucketname'],
            Key='accounts.json',
            Body=json.dumps(accountids),
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=os.environ['kmskeyid'],
            ACL='private')
    else:
        accountids.append(entry)
        s3.put_object(
            Bucket=os.environ['provbucketname'],
            Key='accounts.json',
            Body=json.dumps(accountids),
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=os.environ['kmskeyid'],
            ACL='private')
    return 0

