import json
import boto3
import gzip
import os

def lambda_handler(event, context):
    # TODO implement
    accountId = context.invoked_function_arn.split(":")[4]
    #print("Evnet received: {}".format(event))
    bktName = os.environ['BucketName']
    logkey = accountId + "_CloudTrail"
    
    #file_key = 
    #response = s3Client.list_objects_v2( Bucket=bktName, Prefix="AWSLogs/808065542248/CloudTrail/")
    #for k in response['Contents']:
    #    print("Key file name: {}".format(k['Key']))
    #    if 'pending_' in k['Key']: 
    #        file_key = k['Key']
    #        print("File Key: {}".format(file_key))
    file_key_list = get_all_s3_keys(bktName,accountId) 
    print("Total keys {}".format(len(file_key_list)))
    for file_key in file_key_list:
        if logkey in file_key:
            print("File Key: {}".format(file_key))
            process_event(accountId, bktName,file_key)

    #for rd in event['Records']:
    #    process_event(accountId, rd, bktName,file_key)

def get_all_s3_keys(bucket,accountId):
    """Get a list of all keys in an S3 bucket."""
    s3 = boto3.client("s3")
    px = "AWSLogs/" + accountId + "/CloudTrail/"
    keys = []

    kwargs = {'Bucket': bucket, 'Prefix' : px }
    while True:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            keys.append(obj['Key'])

        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

    return keys
        
        
def process_event(accountId, BUCKET,FILE_TO_READ):
    #BUCKET = records['s3']['bucket']['name']
    #FILE_TO_READ = records['s3']['object']['key']
    print("File name to read {}".format(FILE_TO_READ))
    logkey = accountId + "_CloudTrail"
    
    #roleArn = 'arn:aws:iam::' + accountId + ':role/TSI_Base_FullAccess' 
    #print("Role ARN : {}".format(roleArn))
    try:
        #role = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
        client = boto3.client('s3')

        result = client.get_object(Bucket=BUCKET, Key=FILE_TO_READ) 
        #print("result : {}".format(result))
        # open archive - parse JSON contents to dictionary
        fp = gzip.open(result["Body"],'rb')
        cloudtrail_data = json.loads(fp.read())
        fp.close()

        if ('Records' in cloudtrail_data):
            for trail_item in cloudtrail_data['Records']:
                    print("Trail before sns: {}".format(trail_item))
                    if trail_item['eventSource'] == 'kms.amazonaws.com': 
                        send_sns(trail_item)
        new_file =  FILE_TO_READ.replace(logkey,"processedTrail")
        print("new_file {}".format(new_file))
        kwargs = {'Bucket': BUCKET, 'Key' : FILE_TO_READ }
        client.copy_object(CopySource=kwargs, Bucket=BUCKET,Key=new_file)
        client.delete_object(Bucket=BUCKET, Key=FILE_TO_READ) 
        print("Bucket Key processed: {}".format(FILE_TO_READ))
    except Exception as e:
        print("Exception : {}".format(e))
        

def send_sns(trail):
    print("Trail in SNS {}".format(trail))
    msg = ""
    snsregion = os.environ['SNSTopicArn'].split(":")[3]
    SNSClient = boto3.client('sns',region_name=snsregion)
    if trail['eventName'] == 'ScheduleKeyDeletion': 
        for rs in trail['resources']:
            KMS_key = rs['ARN'] 
            dt = trail['responseElements']['deletionDate']
            msg = "This is to notify that KMS key {} has been schedule for deletion and will be deleted on {} if no action taken".format(KMS_key,dt)
            print("Sending SNS meg: {}".format(msg))
            SNSClient.publish(TopicArn=os.environ['SNSTopicArn'],Message=msg)

    if trail['eventName'] == 'PutKeyPolicy':
        for rs in trail['resources']:
            KMS_key = rs['ARN'] 
            policyName = rs['PolicyName']
            msg = "This is to notify that for KMS key {} policy {} has been updated".format(KMS_key,policyName)
            print("Sending SNS meg: {}".format(msg))
            SNSClient.publish(TopicArn=os.environ['SNSTopicArn'],Message=msg)
    
    if trail['eventName'] == 'DisableKey': 
        for rs in trail['resources']:
            KMS_key = rs['ARN'] 
            msg = "This is to notify that for KMS key {} has been disabled".format(KMS_key)
            print("Sending SNS meg: {}".format(msg))
            SNSClient.publish(TopicArn=os.environ['SNSTopicArn'],Message=msg)
