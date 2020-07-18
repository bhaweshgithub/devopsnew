import boto3
import traceback
import json
import os


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

def cloudformationtest(accountId,testcase,role):
    print("Starting cloudformationtestTest with testcase: {}".format(testcase))
    try:
        cloudformationtestclient = boto3.client('cloudformation',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        print("Aquired cloudformationtest credentials and performing testcases")
        if (testcase['action'] == 'create_stack'):
            print("starting Testcase: create_stack")
            cfttemp = '{"Parameters":{},"Resources":{"TestCFT":{"Type":"AWS::IAM::Group","Properties":{"GroupName":"TestCFT"}}}}'
            result = cloudformationtestclient.create_stack(StackName=testcase['fulltestcase']['stackname'], TemplateBody=cfttemp)
            return(successHandler(result))
        if (testcase['action'] == 'update_stack'):
            print("starting Testcase: update_stack")
            cfttemp = '{"Parameters":{},"Resources":{"TestCFT":{"Type":"AWS::IAM::Group","Properties":{"GroupName":"TestCFT"}}}}'
            result = cloudformationtestclient.update_stack(StackName=testcase['fulltestcase']['stackname'], 
            UsePreviousTemplate=True,
            Parameters=[
            {'ParameterKey': 'GroupName', 'ParameterValue': 'Test'}
            ])
            return(successHandler(result))
        if (testcase['action'] == 'delete_stack'):
            print("starting Testcase: delete_stack")
            result = cloudformationtestclient.delete_stack(StackName=testcase['fulltestcase']['stackname'])
            return(successHandler(result))
        else:
            print("UNKNOWN FUNCTION")
    except Exception as e:
        print("Exception for errorHandler {}".format(type(e)))
        #traceback.print_exc()
        return(errorHandler(e))
        
def createTestResources(accountId,Fullrole,testcase):
    print("Test case: cloudformationtest: Creating Test resources")
    
    cft_full = boto3.client('cloudformation',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
    aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
    aws_session_token=Fullrole['Credentials']['SessionToken'])
    
    try:
        # No Test resources for this test case as of now 
        print("Test case: cloudformationtest: No Test resources to create")
    except Exception as e:
        print("Could not create TestResources: Exception: {}".format(e))

        
def clearTestResources(accountId,Fullrole,testcase):
    print("Test case: cloudformationtest: clear test resources")
    
    cft_name=testcase['fulltestcase']['stackname']
    # Remove S3 bucket created for dummys3 code zip file
    try:
        cft_full = boto3.resource('cloudformation',aws_access_key_id=Fullrole['Credentials']['AccessKeyId'],
        aws_secret_access_key=Fullrole['Credentials']['SecretAccessKey'], 
        aws_session_token=Fullrole['Credentials']['SessionToken'])
        
        cft_full.delete_stack(StackName=cft_name)
    except Exception as e:
        print("Could not clear TestResources: {} Exception: {}".format(cft_name, e))
        