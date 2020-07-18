import boto3
import traceback
import json

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

def snstest(accountId,testcase,role):
    print("Starting snsTest with testcase: {}".format(testcase))
    try:
        snsclient = boto3.client('sns',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        print("Aquired sns credentials and performing testcases")
        if (testcase['action'] == 'create_sns_topic'):
            print("starting Testcase: create_sns_topic")
            result = snsclient.create_topic(Name=testcase['fulltestcase']['topicname'])
            return(successHandler(result))
        if (testcase['action'] == 'subscribe_sns_topic'):
            print("starting Testcase: subscribe_sns_topic")
            TpcArn= "arn:aws:sns:eu-central-1:" + accountId + ":" + testcase['fulltestcase']['topicname']
            # test with dummy email address
            result = snsclient.subscribe(TopicArn=TpcArn,Protocol="email",Endpoint="snsTestCaseEmail@t-systems.com")
            return(successHandler(result))
        if (testcase['action'] == 'delete_sns_topic'):
            print("starting Testcase: delete_sns_topic")
            TpcArn= "arn:aws:sns:eu-central-1:" + accountId + ":" + testcase['fulltestcase']['topicname']
            result = snsclient.delete_topic(TopicArn=TpcArn)
            return(successHandler(result))
        else:
            print("UNKNOWN FUNCTION")
    except Exception as e:
        print("Exception for errorHandler {}".format(type(e)))
        #traceback.print_exc()
        return(errorHandler(e))
        
        