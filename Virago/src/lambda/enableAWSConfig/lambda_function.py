import boto3
import json
import os

sts = boto3.client('sts')
# List of all regions supported by AWS config
allRegions = [ "us-east-2", "us-east-1", "us-west-1", "us-west-2", "ap-south-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1", "sa-east-1", "us-gov-east-1", "us-gov-west-1"]

def lambda_handler(event,context):
    print("Event: {}".format(event))
    #newregions = event['newregions']
    newregions = []
    accountId = str(event['accountId'])

    for r in event['newImage']['enabledregions']['L']:
        newregions.append(r['S'])

    print("newregions : {}".format(newregions))

    roleArn = 'arn:aws:iam::' + accountId + ':role/TSI_Base_FullAccess' 
    print("Role ARN : {}".format(roleArn))
    try:
        role = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
    except Exception as e:
        print("Assume Role failed with exception : {}".format(type(e)))
        traceback.print_exc()

    awsconfigenabled = event['newImage']['awsconfigenabled']['S']
    configRole ="arn:aws:iam::" + accountId + ":role/" + os.environ['aws_config_role']
    configBucket = os.environ['awsconfigBucket']
    configName = os.environ['awsconfigname']
    dcName = os.environ['awsconfigdeliverychannel']
    bucketKey = accountId

    print("awsconfigenabled: {}".format(awsconfigenabled))


    for region in allRegions:
        if region in newregions and awsconfigenabled == 'true':
            response=enableAWSconfig(role,region,configName, dcName,configRole,configBucket, bucketKey)
        else:
            response=disableAWSconfig(role,region, configName, dcName)

    

def enableAWSconfig(role,region, configName, dcName, configRole, configBucket, bucketKey):
    print("Enabling config in region {}".format(region))
    try:
        client = boto3.client('config',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        
        if check_recorder_exists(role, region, configName) is False:
            # put config recording
            client.put_configuration_recorder( ConfigurationRecorder={ 'name': configName, 'roleARN': configRole, 'recordingGroup': { 'allSupported': True, 'includeGlobalResourceTypes': True } } )
            print("AWS config recording enabled in: {}".format(region))
            
            if check_delivery_channel_exists(role, region, dcName) is False:
                # put delivery chaneel
                response = client.put_delivery_channel( DeliveryChannel={ 'name': dcName, 's3BucketName': configBucket,'s3KeyPrefix': bucketKey, 'configSnapshotDeliveryProperties': { 'deliveryFrequency': 'TwentyFour_Hours' } } )
            # Start config recording    
            client.start_configuration_recorder( ConfigurationRecorderName=configName )
            print("AWS config DeliveryChannel enabled in : {}".format(region))
        else:
            print("Rcorder {} already exists in {}".format(configName,region))
    except Exception as e:
        print("Could not enable aws config in region {} with exception {}".format(region,e))


def disableAWSconfig(role,region, configName, dcName):
    print("Deleting config in region {}".format(region))
    try:
        client = boto3.client('config',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        
        if check_recorder_exists(role, region, configName) is True:
            # Stop config Recording
            client.stop_configuration_recorder( ConfigurationRecorderName = configName )
            # Delete config recording
            client.delete_configuration_recorder( ConfigurationRecorderName = configName )

        if check_delivery_channel_exists(role, region, dcName) is True:
            # Delete delivery channel 
            client.delete_delivery_channel( DeliveryChannelName = dcName )
    except Exception as e:
        print("Could not delete aws config in region {} with exception {}".format(region,e))


def check_recorder_exists(role, region, configName):
    client = boto3.client('config',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    response = client.describe_configuration_recorder_status()
    #print ("status: {}".format(response['ConfigurationRecordersStatus']))
    for cf in response['ConfigurationRecordersStatus']:
        if configName == cf['name']:
            return True
    return False
    
def check_delivery_channel_exists(role, region, dcName):
    client = boto3.client('config',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    response = client.describe_delivery_channel_status()
    #print ("status: {}".format(response['DeliveryChannelsStatus']))
    for dc in response['DeliveryChannelsStatus']:
        if dcName == dc['name']:
            return True
    return False
