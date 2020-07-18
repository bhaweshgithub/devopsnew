import boto3
import traceback
import json
import os
import time

def errorHandler(e):
    print("Test failed..")
    testresults = []
    actionresult='UNKNOWN'
    #traceback.print_exc()
    print("Type is {}".format(type(e)))
    print(e.response['Error']['Code'])
    actionresult = e.response['Error']['Code']
    result = {'actionresult' : str(actionresult),'detail' : str(e)}
    return(result)
def successHandler(result):
    print("Test successful..")
    if (result is None):
        successresult = {'actionresult' : 'allow','detail' : "No output from API"}
    else:
        successresult = {'actionresult' : 'allow','detail' : str(result)}
    return(successresult)

def cloudtrailtest(accountId,testcase,role):
    print("Starting cloudtrailTest with testcase: {}".format(testcase))
    try:
        cloudtrailclient = boto3.client('cloudtrail',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        print("Aquired cloudtrail credentials and performing testcases")
        if (testcase['action'] == 'create_cloudtrail'):
            print("starting Testcase: create_cloudtrail")
            bucket_name = os.environ['branchname'] + "-testprobucket-trail"
            result = cloudtrailclient.create_trail(Name=testcase['fulltestcase']['cloudtrailname'],S3BucketName=bucket_name)
            return(successHandler(result))
        if (testcase['action'] == 'update_cloudtrail'):
            print("starting Testcase: update_cloudtrail")
            bucket_name = os.environ['branchname'] + "-testprobucket-trail"
            result = cloudtrailclient.update_trail(Name=testcase['fulltestcase']['cloudtrailname'],S3BucketName=bucket_name)
            return(successHandler(result))
        if (testcase['action'] == 'delete_cloudtrail'):
            print("starting Testcase: delete_cloudtrail")
            result = cloudtrailclient.delete_trail(Name=testcase['fulltestcase']['cloudtrailname'])
            return(successHandler(result))
        else:
            print("UNKNOWN FUNCTION")
    except Exception as e:
        print("Exception for errorHandler {}".format(type(e)))
        #traceback.print_exc()
        return(errorHandler(e))
        

def createTestResources(accountId,Fullrole):
    print("Test case: cloudtrail: Creating Test resources")
    
    # Create S3 bucket 
    s3 = boto3.client('s3',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
    aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
    aws_session_token=Fullrole['Credentials']['SessionToken'])
    
    bucket_name = os.environ['branchname'] + "-testprobucket-trail"
    try:
        bucket = s3.create_bucket(Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})
        time.sleep(5)
    except Exception as e:
        print ("Could not create TestResources:{} Exception: {}".format(bucket_name,e))

        
def clearTestResources(accountId,Fullrole):
    print ("Test case: cloudtrail: clear test resources")
    
    # Remove S3 bucket created.
    try:
        s3 = boto3.resource('s3',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
        aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
        aws_session_token=Fullrole['Credentials']['SessionToken'])
        
        bucket_name = os.environ['branchname'] + "-testprobucket-trail"
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        time.sleep(5)
    except Exception as e:
        print ("Could not clear TestResources: {} Exception: {}".format(bucket_name, e))
        
        