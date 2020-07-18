import boto3
import json
import os
import traceback
import iamhandler
import snshandler
import kmshandler
import lambdahandler
import cloudtrailhandler
import cloudformationhandler
import s3handler
import logging

s3 = boto3.client('s3')
sts = boto3.client('sts')
sns = boto3.client('sns')
b_testcase_success=False

def lambda_handler(event, context):
    print("Starting PolicyFuntionTester...")
    accountId = os.environ['accountId']
    print("Test Account ID : {}".format(accountId))
    roleArn = 'arn:aws:iam::' + accountId + ':role/policytestuser' 
    print("Role ARN : {}".format(roleArn))
    try:
        role = sts.assume_role(RoleArn=roleArn,RoleSessionName='rolereation')
    except Exception as e:
        print("Assume Role failed with exception : {}".format(type(e)))
        traceback.print_exc()
    
    # Full Access role for creating Test resources
    fullroleArn = 'arn:aws:iam::'+ accountId +':role/policytestfullRole'
    print("FullRole ARN : {}".format(fullroleArn))
    try:
        Fullrole = sts.assume_role(RoleArn=fullroleArn,RoleSessionName='FullAccessRole')
    except Exception as e:
        print("FullAccess Assume Role failed with exception : {}".format(e))
        traceback.print_exc()

    testuuid = event['uuid']
    testcase = event['testcase']
    resultlist = []
    detaillist = []
    if(testcase['service']=='iam'):
        print("Service: IAM : testcase {}".format(testcase))
        for testaction in testcase['actions']:
            testrun={'action' : testaction, 'testname' : testcase['testname'], 'fulltestcase' : testcase, 'service' : 'iam'}
            print("Testrun {}".format(testrun))
            result = iamhandler.iamtest(testrun,role)
            print("------")
            print("Testrun result {}".format(result))
            print("------")
            resultlist.append(result['actionresult'])
            detaillist.append(result['detail'])
        print("Finished IAM testcase writting results")
        result = {'Status' : 'FINISHED', 'Result' : resultlist, 'Details' : detaillist, 'Wants' : testcase['wants']}
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)
        
        if (testcase['testname'] == 'fail'):
            result = {'Status' : 'FINISHED', 'Result' : 'fail', 'Details' : 'fail', 'Wants' : testcase['wants']}
            s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)
            
    elif(testcase['service']=='sns'):
        print("Service: SNS : testcase {}".format(testcase))
        for testaction in testcase['actions']:
            testrun={'action' : testaction, 'testname' : testcase['testname'], 'fulltestcase' : testcase, 'service' : 'sns'}
            print("Testrun {}".format(testrun))
            result = snshandler.snstest(accountId,testrun,role)
            print("------")
            print("Testrun result {}".format(result))
            print("------")
            resultlist.append(result['actionresult'])
            detaillist.append(result['detail'])
        print("Finished SNS testcase writting results")
        result = {'Status' : 'FINISHED', 'Result' : resultlist, 'Details' : detaillist, 'Wants' : testcase['wants']}
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

        if (testcase['testname'] == 'fail'):
            result = {'Status' : 'FINISHED', 'Result' : 'fail', 'Details' : 'fail', 'Wants' : testcase['wants']}
            s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)
            
    elif(testcase['service']=='kms'):
        print("Service: KMS : testcase {}".format(testcase))
        for testaction in testcase['actions']:
            testrun={'action' : testaction, 'testname' : testcase['testname'], 'fulltestcase' : testcase, 'service' : 'KMS'}
            print("Testrun {}".format(testrun))
            #kmshandler.createTestResources(accountId,Fullrole,testrun)
            result = kmshandler.kmstest(accountId,testrun,role)
            #kmshandler.clearTestResources(accountId,Fullrole,testrun)
            print("------")
            print("Testrun result {}".format(result))
            print("------")
            resultlist.append(result['actionresult'])
            detaillist.append(result['detail'])
        print("Finished KMS testcase writting results")
        result = {'Status' : 'FINISHED', 'Result' : resultlist, 'Details' : detaillist, 'Wants' : testcase['wants']}
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

        if (testcase['testname'] == 'fail'):
            result = {'Status' : 'FINISHED', 'Result' : 'fail', 'Details' : 'fail', 'Wants' : testcase['wants']}
            s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

    elif(testcase['service']=='lambda'):
        print("Service: lambda : testcase {}".format(testcase))
        for testaction in testcase['actions']:
            testrun={'action' : testaction, 'testname' : testcase['testname'], 'fulltestcase' : testcase, 'service' : 'lambda'}
            print("Testrun {}".format(testrun))
            lambdahandler.createTestResources(accountId,Fullrole,testrun)
            result = lambdahandler.lambdatest(accountId,testrun,role)
            lambdahandler.clearTestResources(accountId,Fullrole,testrun)
            print("------")
            print("Testrun result {}".format(result))
            print("------")
            resultlist.append(result['actionresult'])
            detaillist.append(result['detail'])
        print("Finished lambda testcase writting results")
        result = {'Status' : 'FINISHED', 'Result' : resultlist, 'Details' : detaillist, 'Wants' : testcase['wants']}
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

        if (testcase['testname'] == 'fail'):
            result = {'Status' : 'FINISHED', 'Result' : 'fail', 'Details' : 'fail', 'Wants' : testcase['wants']}
            s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)
                    
    elif(testcase['service']=='cloudtrail'):
        print("Service: cloudtrail : testcase {}".format(testcase))
        for testaction in testcase['actions']:
            testrun={'action' : testaction, 'testname' : testcase['testname'], 'fulltestcase' : testcase, 'service' : 'cloudtrail'}
            print("Testrun {}".format(testrun))
            cloudtrailhandler.createTestResources(accountId,Fullrole)
            result = cloudtrailhandler.cloudtrailtest(accountId,testrun,role)
            cloudtrailhandler.clearTestResources(accountId,Fullrole)
            print("------")
            print("Testrun result {}".format(result))
            print("------")
            resultlist.append(result['actionresult'])
            detaillist.append(result['detail'])
        print("Finished cloudtrail testcase writting results")
        result = {'Status' : 'FINISHED', 'Result' : resultlist, 'Details' : detaillist, 'Wants' : testcase['wants']}
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

        if (testcase['testname'] == 'fail'):
            result = {'Status' : 'FINISHED', 'Result' : 'fail', 'Details' : 'fail', 'Wants' : testcase['wants']}
            s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)
            
    elif(testcase['service']=='cloudformation'):
        print("Service: cloudformation : testcase {}".format(testcase))
        for testaction in testcase['actions']:
            testrun={'action' : testaction, 'testname' : testcase['testname'], 'fulltestcase' : testcase, 'service' : 'cloudformation'}
            print("Testrun {}".format(testrun))
            cloudformationhandler.createTestResources(accountId,Fullrole,testrun)
            result = cloudformationhandler.cloudformationtest(accountId,testrun,role)
            cloudformationhandler.clearTestResources(accountId,Fullrole,testrun)
            print("------")
            print("Testrun result {}".format(result))
            print("------")
            resultlist.append(result['actionresult'])
            detaillist.append(result['detail'])
        print("Finished cloudformation testcase writting results")
        result = {'Status' : 'FINISHED', 'Result' : resultlist, 'Details' : detaillist, 'Wants' : testcase['wants']}
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

        if (testcase['testname'] == 'fail'):
            result = {'Status' : 'FINISHED', 'Result' : 'fail', 'Details' : 'fail', 'Wants' : testcase['wants']}
            s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)
            
    elif(testcase['service']=='s3'):
        print("Service: s3 : testcase {}".format(testcase))
        for testaction in testcase['actions']:
            testrun={'action' : testaction, 'testname' : testcase['testname'], 'fulltestcase' : testcase, 'service' : 's3'}
            print("Testrun {}".format(testrun))
            s3handler.createTestResources(accountId,Fullrole,testrun)
            result = s3handler.s3test(accountId,testrun,role)
            s3handler.clearTestResources(accountId,Fullrole,testrun)
            print("------")
            print("Testrun result {}".format(result))
            print("------")
            resultlist.append(result['actionresult'])
            detaillist.append(result['detail'])
        print("Finished s3 testcase writting results")
        result = {'Status' : 'FINISHED', 'Result' : resultlist, 'Details' : detaillist, 'Wants' : testcase['wants']}
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

        if (testcase['testname'] == 'fail'):
            result = {'Status' : 'FINISHED', 'Result' : 'fail', 'Details' : 'fail', 'Wants' : testcase['wants']}
            s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)

    else:
        result="""{"Status" : "PENDING", "Result" : "ongoing"}"""
        s3PutObject(os.environ['bucket'],testuuid,testcase['testname'],result)
    
    
def s3PutObject(bucketName,testuuid,testname,result):
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucketName,
        Key='{}/{}.json'.format(testuuid,testname),
        Body=json.dumps(result),
        ServerSideEncryption='AES256',
        ACL='private')
    print("Result written to S3 for testcase: {} ".format(testname))
    