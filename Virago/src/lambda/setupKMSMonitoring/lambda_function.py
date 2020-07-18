import json
import boto3
import os
import gzip
import zipfile
import io
import zlib 
import base64
import time

def lambda_handler(event, context):
    # TODO implement
    #print("Event: {}".format(event))
    accountId = str(event['accountId'])
    region = 'eu-central-1'
    kmsLambdaName = "kms-test"
    kmsLambdaRole = "TSI_KMSMonitoringRole"
    masterBucket = os.environ['bucketname'] 
    branchname = os.environ['branchname']
    #kmsbucketkey = os.environ['branchname'] + "/" + kmsLambdaName + ".zip"
    bucketName = accountId + "cloudtrail"
    snstopicArn = "arn:aws:sns:us-east-1:" + accountId + ":TSI_Base_Security_Incident"
    
    sts = boto3.client('sts')
    roleArn = 'arn:aws:iam::' + accountId + ':role/TSI_Base_FullAccess' 
    #print("Role ARN : {}".format(roleArn))
    try:
        role = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')

        # Create s3 bucket
        client = boto3.client('s3',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        
        if check_bucket_exists(client,bucketName) == "False":
            client.create_bucket(Bucket=bucketName, CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'}) 

        rules = {"Rules":[{"Expiration":{'Days':7},"ID":"Delete8daysoldlogs","Prefix":"AWSLogs/","Status":"Enabled",'AbortIncompleteMultipartUpload': {'DaysAfterInitiation':7}}]}

        client.put_bucket_lifecycle_configuration(Bucket=bucketName, LifecycleConfiguration=rules)
        print("Bucket lifecycle rules are created for {}".format(bucketName))

        rs01 = "arn:aws:s3:::" + bucketName
        rs02 = "arn:aws:s3:::" + bucketName + "/AWSLogs/" + accountId + "/*",

        policy = {'Version':'2012-10-17','Statement':[{'Sid':'AWSCloudTrailAclCheck','Effect':'Allow','Principal':{'Service':'cloudtrail.amazonaws.com'},'Action':'s3:GetBucketAcl','Resource': "%s" % rs01},{'Sid':'AWSCloudTrailWrite','Effect':'Allow','Principal':{'Service':'cloudtrail.amazonaws.com'},'Action':'s3:PutObject','Resource': "%s" % rs02,'Condition':{'StringEquals':{'s3:x-amz-acl':'bucket-owner-full-control'}}}]}

        bucket_policy = json.dumps(policy)
        print("bucket_policy {}".format(bucket_policy))

        client.put_bucket_policy( Bucket=bucketName,Policy=bucket_policy)

        # Create cloudtrail
        trailclient = boto3.client('cloudtrail',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])

        trailclient.create_trail(Name=bucketName, S3BucketName=bucketName,IsMultiRegionTrail=True,EnableLogFileValidation=True)
        trailclient.start_logging(Name=bucketName)

        # create policy

        iamclient = boto3.client('iam',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])

        pd = {'Version':'2012-10-17','Statement':[{'Effect':'Allow','Action':'logs:CreateLogGroup','Resource':"arn:aws:logs:{}:{}:*".format(region,accountId)},{'Effect':'Allow','Action':['logs:CreateLogStream','logs:PutLogEvents'],'Resource':["arn:aws:logs:{}:{}:log-group:/aws/lambda/{}:*".format(region,accountId,kmsLambdaName)]}]}

        policyDoc = json.dumps(pd)
        print("policyDoc {}".format(policyDoc))

        awslambdapolicy = iamclient.create_policy(PolicyName='AWSLambdaBasicExecutionRole-setupKMSMonitoring',PolicyDocument=policyDoc,Description='lambda execution role for setupKMSMonitoring')
        print("Policy Created {}".format(awslambdapolicy['Policy']['Arn']))

        # create role
        ap = {'Version':'2012-10-17','Statement':[{'Effect':'Allow','Principal':{'Service': [ 'lambda.amazonaws.com', 'events.amazonaws.com']},'Action':'sts:AssumeRole'}]}
        asumeRolePolicy = json.dumps(ap)

        setupKMSRole = iamclient.create_role(RoleName=kmsLambdaRole, AssumeRolePolicyDocument=asumeRolePolicy, Description='Role for setupKMSMonitoring lambda')
        print("Role Created {}".format(setupKMSRole['Role']['Arn']))

        # Attache policies to role
        iamclient.attach_role_policy(RoleName=kmsLambdaRole,PolicyArn=awslambdapolicy['Policy']['Arn'])
        iamclient.attach_role_policy(RoleName=kmsLambdaRole,PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')
        iamclient.attach_role_policy(RoleName=kmsLambdaRole,PolicyArn='arn:aws:iam::aws:policy/AmazonSNSFullAccess')
        print("Role policies has been attached for role {}".format(setupKMSRole['Role']['Arn']))
        # wait for role creation and policy to settle
        time.sleep(10)
        
        # Copy lambda code to client bucket
        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=masterBucket, Key= "{}/kms-test.zip".format(branchname))

        z = zipfile.ZipFile(io.BytesIO(obj['Body'].read()))

        lambdaString = z.read("{}/lambda_function.py".format(kmsLambdaName))

        print("fp {}".format(lambdaString))
        
        #client.put_object(Body = obj['Body'].read(), Bucket=bucketName, Key= "{}.zip".format(kmsLambdaName))
        #client.put_object(Body = lambdaString, Bucket=bucketName, Key= "{}.py".format(kmsLambdaName))
        #print("Lambda Object copied to client bucket {}".format(bucketName))

        #obj = client.get_object(Bucket=bucketName, Key= "{}.py".format(kmsLambdaName))
        #zobj = base64.b64encode(obj['Body'].read())


        #print("Zip {}".format(zobj))
        #client.put_object(Body = zobj, Bucket=bucketName, Key= "{}.zip".format(kmsLambdaName))

        #lambdaRole =setupKMSRole['Role']['Arn']
        lambdaRole = "arn:aws:iam::"+ accountId +":role/setupKMSMonitoringRole"
        # create lambda
        lmdclient = boto3.client('lambda',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])


        lambdafuntion  = lmdclient.create_function(FunctionName=kmsLambdaName,Runtime='python3.6', Role=lambdaRole, Handler='lambda_function.lambda_handler',Code={'ZipFile' : process_lambda(lambdaString) },Description='Lambda function to process cloudtrail logs and send snsnotification for KMSspecifiedactivities',Timeout=300,Publish=False,Environment={'Variables':{'BucketName': "{}".format(bucketName),'SNSTopicArn': "{}".format(snstopicArn)}})

        # crete cloudwatch rule 
        crule = boto3.client('events',region_name=region,aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])

        crule.put_rule( Name=kmsLambdaName, ScheduleExpression="rate(15 minutes)", State='ENABLED', Description='CW event for KMS events notification', RoleArn=lambdaRole)

        crule.put_targets( Rule=kmsLambdaName, Targets=[{'Arn': lambdafuntion['FunctionArn'],'Id': "{}CWEventsTarget".format(kmsLambdaName)}])

    except Exception as e:
        print("Exception Occured : {}".format(e))


def check_bucket_exists(client, bkt):
    try:
        status = client.head_bucket(Bucket=bkt)
    except Exception as e:
        print("Bucket {} does not exist.".format(bkt))
        return "False"
    print("Bucket {} exists already".format(bkt))    
    return "True"


# funtion to zip/compress python funtion string
def process_lambda(func_str):
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED)
    zinfo = zipfile.ZipInfo('lambda_function.py')
    zinfo.external_attr = 0o777 << 16  # give full access to included file
    zip_file.writestr(zinfo, func_str)
    zip_file.close()
    zip_output.seek(0)
    return zip_output.read()