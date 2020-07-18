import boto3
import json
import os

def aws_session(role_arn=None, session_name='my_session'):
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

def lambda_handler(event, context):
    ROLE_ARN = 'arn:aws:iam::' + os.environ["secdevopsid"] +':role/TSI_Base_FullAccess'
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='lambdaexecution')
    print(event)
    arn = 'arn:aws:lambda:eu-central-1:'+ os.environ["secdevopsid"]+':function:pacbot-add-accounttomonitor'
    client = session_assumed.client('lambda')
    response = client.invoke(FunctionName=arn,
                             InvocationType='RequestResponse',
                             Payload=json.dumps(event))

    result = json.loads(response.get('Payload').read())
    return result