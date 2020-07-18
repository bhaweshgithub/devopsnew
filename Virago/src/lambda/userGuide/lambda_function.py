import boto3
import secrets
import string
import os
from random import shuffle
from botocore.client import Config


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

def lambda_handler(event, context):
    sesSession = aws_session()
    sesClient = sesSession.client('ses', region_name = 'eu-west-1')
    global accountId
    accountId = str(event['accountId'])
    #accountEmail = event['accountemail']
    securityEmail = event['securityEmail']
    bucket_name = 'virago573123'
    key = 'Userguide-final.docx'
    document_url = get_presigned_url(bucket_name,key)
    login_information  = "Dear Team,\n As part of onboarding process,\n Please refer the documentation located at "+document_url+"\n Best regards,\n Your T-Managed AWS Team"
    response = sesClient.send_email(Source='service@taws.cloud',Destination={'ToAddresses': [securityEmail],},
    Message={'Subject': {
               'Data': 'Login information'},
           'Body': {
               'Text': {
                   'Data': login_information,
               }
           }
       })


def get_presigned_url(bucket,key):
    roleArn = 'arn:aws:iam::' + accountId +':role/TSI_Base_FullAccess'
    #print(roleArn)
    print("Role ARN : {}".format(roleArn))
    s3session = aws_session(role_arn=roleArn)
    s3 = s3session.client('s3')
    presignedUrl = s3.generate_presigned_url('put_object', Params={'Bucket':bucket,'Key':key}, ExpiresIn=432000, HttpMethod='GET')
    return presignedUrl
