import boto3
import traceback
import json

def errorHandler(e):
    testresults = []
    actionresult='UNKNOWN'
    print(e)
    #traceback.print_exc()
    print("Type is {}".format(type(e)))
    print(e.response['Error']['Code'])
    actionresult = e.response['Error']['Code']
    result = {'actionresult' : str(actionresult),'detail' : str(e)}
    return(result)
def successHandler(result):
    if (result is None):
        successresult = {'actionresult' : 'allow','detail' : "No output from API"}
    else:
        successresult = {'actionresult' : 'allow','detail' : str(result)}
    return(successresult)

def iamtest(testcase,role):
    print(testcase)
    try:
        iamclient = boto3.client('iam',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
        if (testcase['action'] == 'create_group'):
            result = iamclient.create_group(GroupName=testcase['fulltestcase']['groupname'])
            return(successHandler(result))
        if (testcase['action'] == 'attach_group_policy'):
            result = iamclient.attach_group_policy(GroupName=testcase['fulltestcase']['groupname'],PolicyArn=testcase['fulltestcase']['policyarn'])
            return(successHandler(result))
        if (testcase['action'] == 'detach_group_policy'):
            result = iamclient.detach_group_policy(GroupName=testcase['fulltestcase']['groupname'],PolicyArn=testcase['fulltestcase']['policyarn'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_group'):
            result = iamclient.delete_group(GroupName=testcase['fulltestcase']['groupname'])
            return(successHandler(result))
        if (testcase['action'] == 'create_role_without_pb'):
            result = iamclient.create_role(RoleName=testcase['fulltestcase']['rolename'],AssumeRolePolicyDocument=json.dumps(testcase['fulltestcase']['assumepolicy']))
            return(successHandler(result))
        if (testcase['action'] == 'create_role_with_pb'):
            result = iamclient.create_role(RoleName=testcase['fulltestcase']['rolename'],PermissionsBoundary=testcase['fulltestcase']['permissionboundary'],AssumeRolePolicyDocument=json.dumps(testcase['fulltestcase']['assumepolicy']))
            return(successHandler(result))
        if (testcase['action'] == 'create_user_without_pb'):
            result = iamclient.create_user(UserName=testcase['fulltestcase']['username'])
            return(successHandler(result))
        if (testcase['action'] == 'create_user_with_pb'):
            result = iamclient.create_user(UserName=testcase['fulltestcase']['username'],PermissionsBoundary=testcase['fulltestcase']['permissionboundary'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_role'):
            result = iamclient.delete_role(RoleName=testcase['fulltestcase']['rolename'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_user'):
            result = iamclient.delete_user(UserName=testcase['fulltestcase']['username'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_user_permissions_boundary'):
            result = iamclient.delete_user_permissions_boundary(UserName=testcase['fulltestcase']['username'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_role_permissions_boundary'):
            result = iamclient.delete_role_permissions_boundary(RoleName=testcase['fulltestcase']['rolename'])
            return(successHandler(result))
        if (testcase['action'] == 'attach_role_policy'):
            result = iamclient.attach_role_policy(RoleName=testcase['fulltestcase']['rolename'],PolicyArn=testcase['fulltestcase']['policyarn'])
            return(successHandler(result))
        if (testcase['action'] == 'detach_role_policy'):
            result = iamclient.detach_role_policy(RoleName=testcase['fulltestcase']['rolename'],PolicyArn=testcase['fulltestcase']['policyarn'])
            return(successHandler(result))
        if (testcase['action'] == 'rename_group'):
            result = iamclient.update_group(GroupName=testcase['fulltestcase']['groupname'],NewGroupName=testcase['fulltestcase']['newgroupname'])
            return(successHandler(result))
        if (testcase['action'] == 'delete_group_renamed'):
            result = iamclient.delete_group(GroupName=testcase['fulltestcase']['newgroupname'])
            return(successHandler(result))
        else:
            print("UNKNOWN FUNCTION")
    except Exception as e:
        print(e)
        #traceback.print_exc()
        return(errorHandler(e))
        
        