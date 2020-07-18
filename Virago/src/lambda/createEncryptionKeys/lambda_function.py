import boto3
import json

regionlist = []

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
    
def createEncryptionKey(client,aliasname,description,tags):
    keyresponse = client.create_key(
        Description=description,
        KeyUsage='ENCRYPT_DECRYPT',
        Origin='AWS_KMS',
        BypassPolicyLockoutSafetyCheck=False,
        Tags=tags
        )
    try:
        aliasintresponse = client.create_alias(
        AliasName=aliasname,
        TargetKeyId=keyresponse['KeyMetadata']['Arn']
        )
    except:
            print("{} already have {} key with this alias".format(region,description))
def lambda_handler(event, context):
    enabledregions = event['enabledregions'].split(",")
    if 'accountId' in event:
        accountId = str(event['accountId'])
    else:
        raise ValueError("No accountID provided")
    
    
    ROLE_ARN = 'arn:aws:iam::' + accountId +':role/TSI_Base_FullAccess'
    
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='kmskey')
    for region in enabledregions: 
        client = session_assumed.client('kms',region_name=region)
        aliaslistresponse = client.list_aliases()
        aliases = []
        for alias in aliaslistresponse['Aliases']:
            aliases.append(alias['AliasName'])
        if ('alias/TSI_Base_InternalS3Key' not in aliases):
            print("Creating internal s3 key")
            description = 'Internal Key'
            tags = [{
                'TagKey': 'TSI_KEY',
                'TagValue': 'Internal'
            }]
            createEncryptionKey(client,'alias/TSI_Base_InternalS3Key',description,tags)
        else:
            print("Key found with internal alias in region {}".format(region))
        if ('alias/TSI_Base_ConfidentialS3Key' not in aliases):
            print("Creating confidential s3 key")
            description = 'Confidential Key'
            tags = [{
                'TagKey': 'TSI_KEY',
                'TagValue': 'Confidential'
            }]
            createEncryptionKey(client,'alias/TSI_Base_ConfidentialS3Key',description,tags)
        else:
            print("Key found with confidential alias in region {}".format(region))
