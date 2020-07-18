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

def kmstest(accountId,testcase,role):
    print("Starting kmsTest with testcase: {}".format(testcase))
    try:
        kmsclient = boto3.client('kms',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        print("Aquired kms credentials and performing testcases")
        if (testcase['action'] == 'create_kms_alias'):
            print("starting Testcase: create_kms_alias")
            als = "alias/" + testcase['fulltestcase']['aliasname']
            result = kmsclient.create_alias(AliasName=als,TargetKeyId=testcase['fulltestcase']['targetkeyid'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_kms_alias'):
            print("starting Testcase: delete_kms_alias")
            als = "alias/TSI_TEST"
            result = kmsclient.delete_alias(AliasName=als)
            return(successHandler(result))
        if (testcase['action'] == 'update_kms_alias'):
            print("starting Testcase: update_kms_alias")
            als = "alias/TSI_TEST"
            result = kmsclient.update_alias(AliasName=als,TargetKeyId=testcase['fulltestcase']['targetkeyid'])
            return(successHandler(result))
        else:
            print("UNKNOWN FUNCTION")
    except Exception as e:
        print("Exception for errorHandler {}".format(type(e)))
        #traceback.print_exc()
        return(errorHandler(e))
        

#def createTestResources(accountId,Fullrole,testcase):
#    print("Test case: KMS : Creating Test resources")
#    print("Test case: {}".format(testcase))
#       
#def clearTestResources(accountId,Fullrole,testcase):
#    print("Test case: kms: clear test resources")
#    print("Test case: {}".format(testcase))

        
        