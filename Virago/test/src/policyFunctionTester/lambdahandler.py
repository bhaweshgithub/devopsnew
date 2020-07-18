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

def lambdatest(accountId,testcase,role):
    print("Starting lambdatest with testcase: {}".format(testcase))
    try:
        lambdatestclient = boto3.client('lambda',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        print("Aquired lambdatest credentials and performing testcases")
        if (testcase['action'] == 'create_lambda_function'):
            print("starting Testcase: create_lambda_function")
            # Global role used to ensure role exists in test account
            lambdaRole = 'arn:aws:iam::'+ accountId +':role/TSI_Base_FullAccess'
            bucket_name = os.environ['branchname'] + "-testprobucket-lambda"
            bucket_key = 'DummyLambda.py'
            result = lambdatestclient.create_function(FunctionName=testcase['fulltestcase']['functionname'], 
            Runtime="python3.7",
            Role=lambdaRole,
            Handler="{0}.lambda_handler".format(testcase['fulltestcase']['functionname']),
            # DummyLambda.zip is dummy lambda funtion which just prints its event
            Code={ 'S3Bucket': bucket_name, 'S3Key': bucket_key }
            )
            return(successHandler(result))
        if (testcase['action'] == 'invoke_lambda_function'):
            print("starting Testcase: invoke_lambda_function")
            result = lambdatestclient.invoke(FunctionName=testcase['fulltestcase']['functionname'])
            return(successHandler(result))
        if (testcase['action'] == 'update_lambda_code'):
            print("starting Testcase: update_lambda_code")
            result = lambdatestclient.update_function_code(FunctionName=testcase['fulltestcase']['functionname'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_lambda_function'):
            print("starting Testcase: delete_lambda_function")
            result = lambdatestclient.delete_function(FunctionName=testcase['fulltestcase']['functionname'])
            return(successHandler(result))
        if (testcase['action'] == 'update_lambda_function_configuration'):
            print("starting Testcase: update_lambda_function_configuration")
            result = lambdatestclient.update_function_configuration(FunctionName=testcase['fulltestcase']['functionname'],Timeout=60)
            return(successHandler(result))
        else:
            print("UNKNOWN FUNCTION")
    except Exception as e:
        print("Exception for errorHandler {}".format(type(e)))
        #traceback.print_exc()
        return(errorHandler(e))
        
        
def createTestResources(accountId,Fullrole,testcase):
    print("Test case: lambda: Creating Test resources")
    print("Test case: {}".format(testcase))
    
    # Create S3 bucket for dummyLambda code zip file
    s3 = boto3.client('s3',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
    aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
    aws_session_token=Fullrole['Credentials']['SessionToken'],
    region_name='eu-central-1')
    
    bucket_name = os.environ['branchname'] + "-testprobucket-lambda"
    rgn = 'eu-central-1'
    try:
        bucket = s3.create_bucket(Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': rgn})
        
        dummyLambda = b'def lambda_handler(event, context): print(event)'
        s3.put_object(
        Bucket=bucket_name,
        Key='DummyLambda.py',
        Body=dummyLambda
        )
        time.sleep(5)
    except Exception as e:
        print("Could not create TestResources: {} Exception: {}".format(bucket_name, e))

        
def clearTestResources(accountId,Fullrole,testcase):
    print("Test case: lambda: clear test resources")
    print("Test case: {}".format(testcase))

    bucket_name = os.environ['branchname'] + "-testprobucket-lambda"
    # Remove S3 bucket created for dummyLambda code zip file
    try:
        s3 = boto3.resource('s3',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
        aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
        aws_session_token=Fullrole['Credentials']['SessionToken'],
        region_name='eu-central-1')
        
        bucket_name = os.environ['branchname'] + "-testprobucket-lambda"
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        time.sleep(5)
    except Exception as e:
        print("Could not clear TestResources: {} Exception: {}".format(bucket_name, e))
        