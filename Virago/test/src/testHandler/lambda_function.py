import boto3
import json
import os
import uuid
import time
import sys
import traceback

s3 = boto3.client('s3')
code_pipeline = boto3.client('codepipeline')
lambdaclient = boto3.client('lambda')

def lambda_handler(event, context):
    testsfailed = 0
    testcasenames = []
    try:
        job_id = event['CodePipeline.job']['id']
        job_data = event['CodePipeline.job']['data']
        params = json.loads(job_data['actionConfiguration']['configuration']['UserParameters'])
        testcases = json.loads(s3.get_object(
            Bucket=os.environ['bucket'],
            Key='test/testcases.json')['Body'].read())
        if( 'continuationToken' in job_data):
            #This is not the first run, get uuid from the continuationToken
            conttoken = json.loads(job_data['continuationToken'])
            testuuid = conttoken['testuuid']
            print("testuuid from continuationToken: {} ".format(testuuid))
            testcaseresults = json.loads(s3.get_object(
                Bucket=os.environ['bucket'],
                Key='{}/result.json'.format(testuuid))['Body'].read())
            starttime = testcaseresults['Starttime']
            #enough time passed from run
            if(time.time()-starttime>100):
                testcasenames = testcaseresults['Results']
                #Collect all status files
                #Key='{}/{}.json'.format(testuuid,testcase['testname']),
                for testcasename in testcasenames:
                    result = json.loads(s3.get_object(
                        Bucket=os.environ['bucket'],
                        Key='{}/{}.json'.format(testuuid,testcasename))['Body'].read())
                    testcaseresults['Results'][testcasename]=result
                s3.put_object(
                    Bucket=os.environ['bucket'],
                    Key='{}/result.json'.format(testuuid),
                    Body=json.dumps(testcaseresults),
                    ServerSideEncryption='AES256',
                    ACL='private')
                for testcasename in testcasenames:
                    if(testcaseresults['Results'][testcasename]['Status'] == 'PENDING'):
                        testsfailed=testsfailed+1
                    else:
                        print("Test : {} - FINISHED with {}".format(testcasename,testcaseresults['Results'][testcasename]['Status']))
                if (testsfailed>0):
                    print("Failed due to timeout")
                    code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'type': 'JobFailed', 'message' : 'Timeout'})
                    return("Timeout part finished")
                else:
                    testsfailed = 0
                    for testcasename in testcasenames:
                        if (testcaseresults['Results'][testcasename]['Result'] == testcaseresults['Results'][testcasename]['Wants']):
                            print("Test case {} SUCCEEDED".format(testcasename))
                        else:
                            print("Test case {} FAILED".format(testcasename))
                            testsfailed = testsfailed + 1
                    if (testsfailed>0):
                        print("{} tests has been failed".format(testsfailed))
                        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'type': 'JobFailed', 'message' : 'Timeout'})
                        return("FAILED with {} unsuccessfull tests".format(testsfailed))
                    else:
                        print("Succeeded")
                        code_pipeline.put_job_success_result(jobId=job_id)
                        return("Succeeded part finished")
                #code_pipeline.put_job_success_result(jobId=job_id)
            print(testcaseresults)
            testcasenames = testcaseresults['Results']
            for testcasename in testcasenames.keys():
                print("--------")
                print (testcasename)
                if(testcaseresults['Results'][testcasename]['Status'] == 'PENDING'):
                    testcase = json.loads(s3.get_object(
                    Bucket=os.environ['bucket'],
                    Key='{}/{}.json'.format(testuuid,testcasename))['Body'].read())
                    testcaseresults['Results'][testcasename]['Status']  = testcase['Status']
                else:
                    pass
            #update the results.json file
            s3.put_object(
                    Bucket=os.environ['bucket'],
                    Key='{}/result.json'.format(testuuid),
                    Body=json.dumps(testcaseresults),
                    ServerSideEncryption='AES256',
                    ACL='private')
            continuation_token = json.dumps({'testuuid': testuuid})
            print("Continuing {}".format(job_id))
            code_pipeline.put_job_success_result(jobId=job_id, continuationToken=continuation_token)
            return("Continue part finished")
        else:
            testuuid = str(uuid.uuid4())
            initial_result = {}
            for testcase in testcases:
                #collect test names
                testcasenames.append(testcase['testname'])
                #create initial file for test cases
                initial_result[testcase['testname']] = {'Status' :'PENDING', 'Result' : ""}
                s3.put_object(
                    Bucket=os.environ['bucket'],
                    Key='{}/{}.json'.format(testuuid,testcase['testname']),
                    Body="""{"Status" : "PENDING", "Result" : ""}""",
                    ServerSideEncryption='AES256',
                    ACL='private')
                #Create payload
                lambdapayload = {'uuid' : testuuid, 'testcase': testcase}
                #start the policy tester with the event from json file
                lambdaclient.invoke(FunctionName='policyFunctionTester', InvocationType='Event', Payload=json.dumps(lambdapayload))
                statusfilecontent = {'Starttime' : time.time(), 'Results' : initial_result}
            s3.put_object(
                    Bucket=os.environ['bucket'],
                    Key='{}/result.json'.format(testuuid),
                    Body=json.dumps(statusfilecontent),
                    ServerSideEncryption='AES256',
                    ACL='private')
            #Return to codepipeline the uuid for the test
            continuation_token = json.dumps({'testuuid': testuuid})
            print("Continue line 109 {}".format(job_id))
            code_pipeline.put_job_success_result(jobId=job_id, continuationToken=continuation_token)
            return("Continue part finished - 111")
                
            
    except Exception as e:
        print(e)
        traceback.print_exc()
        code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'type': 'JobFailed', 'message' : str(e)})
        return("Exception handler")