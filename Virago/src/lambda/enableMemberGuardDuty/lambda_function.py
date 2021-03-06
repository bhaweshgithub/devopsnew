import json
import boto3
import os

regionlist = []

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
    print(event)
    regionlist.clear()
    ROLE_ARN = 'arn:aws:iam::' + event['accountId'] +':role/TSI_Base_FullAccess'
    session_assumed = aws_session(role_arn=ROLE_ARN, session_name='guardDuty')
    ec2client = session_assumed.client('ec2')
    ec2regionlist = ec2client.describe_regions()['Regions']
    for region in ec2regionlist:
    
      if region['RegionName'] != 'eu-north-1':
        guardDutyClient = session_assumed.client(service_name = 'guardduty',region_name = region['RegionName'])
        detector = guardDutyClient.list_detectors()
        if len(detector['DetectorIds']) > 0:
          detector_id = detector['DetectorIds'][0]
          print('Detector exists in Region ' + region['RegionName'] + ' Detector Id: ' + detector_id)
        else :
          print('Creating Detector in ' + region['RegionName'] + ' ...')
          detectorResp = guardDutyClient.create_detector(Enable=True)
          detector_id = detectorResp['DetectorId']
          
        for invitation_details in guardDutyClient.list_invitations()['Invitations']:
          guardDutyClient.accept_invitation(DetectorId=detector_id,InvitationId=invitation_details['InvitationId'],MasterId=invitation_details['AccountId'])
          print('Accepted Invitation: ' + invitation_details['InvitationId'])
