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

def s3test(accountId,testcase,role):
    print("Starting s3testTest with testcase: {}".format(testcase))
    try:
        s3testclient = boto3.client('s3',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], 
        aws_session_token=role['Credentials']['SessionToken'],
        region_name=testcase['fulltestcase']['region'])
        print("Aquired s3test credentials and performing testcases")
        if (testcase['action'] == 'create_s3_bucket'):
            print("starting Testcase: create_s3_bucket")
            # Create new bucket with LocationConstraint
            bucket_name = os.environ['branchname'] + "-testslocationconstraint"
            rgn = testcase['fulltestcase']['region']
            
            result = s3testclient.create_bucket(Bucket=bucket_name, 
            CreateBucketConfiguration={'LocationConstraint': rgn})
            
            return(successHandler(result))
        if (testcase['action'] == 'get_s3_object'):
            print("starting Testcase: get_s3_object")
            bucket_name = os.environ['branchname'] + "-testprobucket-s3"
            result = s3testclient.get_object(Bucket=bucket_name, Key='Dummys3.py')
            return(successHandler(result))
        if (testcase['action'] == 'list_s3_objects'):
            print("starting Testcase: list_s3_objects")
            bucket_name = os.environ['branchname'] + "-testprobucket-s3"
            result = s3testclient.list_objects(Bucket=bucket_name, Prefix='Dummys3.py')
            return(successHandler(result))
        if (testcase['action'] == 'head_s3_bucket'):
            print("starting Testcase: head_s3_bucket")
            bucket_name = os.environ['branchname'] + "-testprobucket-s3"
            result = s3testclient.head_bucket(Bucket=bucket_name)
            return(successHandler(result))
        else:
            print("UNKNOWN FUNCTION")
    except Exception as e:
        print("Exception for errorHandler {}".format(type(e)))
        #traceback.print_exc()
        return(errorHandler(e))
        
        
def createTestResources(accountId,Fullrole,testcase):
    print("Test case: s3: Creating Test resources")
    
    # Create S3 bucket for dummys3 code zip file
    s3 = boto3.client('s3',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
    aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
    aws_session_token=Fullrole['Credentials']['SessionToken'],
    region_name=testcase['fulltestcase']['region'])
    
    bucket_name = os.environ['branchname'] + "-testprobucket-s3"
    rgn = testcase['fulltestcase']['region']

    try:     
        bucket = s3.create_bucket(Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': rgn})
       
        dummys3 = b'def s3_handler(event, context): print(event)'
        s3.put_object(
        Bucket=bucket_name,
        Key='Dummys3.py',
        Body=dummys3
        )
        time.sleep(5)
        print("Bucket {} created and object: Dummys3.py pushed into the bucket".format(bucket_name))        
    except Exception as e:
        print("Could not create TestResources:{} Exception: {}".format(bucket_name, e))

        
def clearTestResources(accountId,Fullrole,testcase):
    print("Test case: s3: clear test resources")

    
    bucket_name = os.environ['branchname'] + "-testprobucket-s3"
    # Remove S3 bucket created for dummys3 code zip file
    try:
        s3 = boto3.resource('s3',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
        aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
        aws_session_token=Fullrole['Credentials']['SessionToken'],
        region_name=testcase['fulltestcase']['region'])
  
        bucket_name = os.environ['branchname'] + "-testprobucket-s3"
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        time.sleep(5)
        
        bucket_name = os.environ['branchname'] + "-testslocationconstraint"
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        time.sleep(5)
    except Exception as e:
        print("Could not clear TestResources:{} Exception: {}".format(bucket_name, e))
        