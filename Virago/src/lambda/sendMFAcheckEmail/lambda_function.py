import boto3
import secrets
import string
import os
from random import shuffle
email = boto3.client('ses',region_name="eu-west-1")
accountId = ""


def lambda_handler(event, context):
    accountId = str(event['accountId'])
    logininformation  = """Dear Team,

As part of onboarding process, please enable MFA for root access.

Account ID: {}
Root Email Address : {}
Account name : {}

Best regards,
Your T-Managed AWS Team""".format(event['accountId'],event['accountemail'],event['description'])
    response = email.send_email(
        Source='service@taws.cloud',
        Destination={
            'ToAddresses': [
                os.environ['mfateamemail'] ],
            },
        Message={
            'Subject': {
                'Data': 'Login information'
            },
            'Body': {
                'Text': {
                    'Data': logininformation,
                }
            }
        })
    

    
    

