import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#move it to environ variable
#SNS_TOPIC_ARN = 'arn:aws:sns:eu-central-1:808065542248:tsi_send_mail_sdm_cloudchkr'


def send_mail_to_sdm(event):
    #Create Subscription
    sesSession = aws_session()
    sesClient = sesSession.client('ses', region_name = 'eu-west-1')
    accountMail = event['accountemail']
    accountId = event['accountId']
    email = event['email']
    description = event['description']
    dbresopnse = get_table_metadata('accounts',accountId)
    #logger.info(json.dumps(securityEmail))
    securityEmail = dbresopnse['Item']['securityEmail']['S']
    #ToAddress = aws-servicemanagement@t-systems.com
    message  = """Dear Team,
    
    As part of onboarding process, please enable cloudchckr integration for below account.
    
    Account ID: {}
    Root Email Address : {}
    Account name : {}
    Security Email: {}
	
    
    Best regards,
    Your T-Managed AWS Team""".format(accountId,accountMail,description,securityEmail)
    response = sesClient.send_email(
        Source='service@taws.cloud',
        Destination={
            'ToAddresses': [
                'd.verma@t-systems.com'],
            },
        Message={
            'Subject': {
                'Data': 'CloudCheckr Integration required!!!'
            },
            'Body': {
                'Text': {
                    'Data': message,
                }
            }
        })
    
    return securityEmail


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

def get_table_metadata(table_name,keyVal):
  # The boto3 dynamoDB resource
  Key = { 'accountId': {'S': keyVal}}
  client = boto3.client('dynamodb', region_name = 'eu-central-1')
  response = client.get_item( TableName=table_name, Key=Key)
  return response


def lambda_handler(event, context):
    '''This lambda function send email to FMB when baseline provisioning is done'''
    response = send_mail_to_sdm(event)
    return response