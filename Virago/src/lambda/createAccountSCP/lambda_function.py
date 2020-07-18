import boto3
import json


#we need to load json file, and manipulate entries according to the parameters got
#DenyConfigDeliveries
#DenyNotEnabledRegions
#Support
def lambda_handler(event,context):
    enabledregions = event['enabledregions'].split(",")
    if 'config' in event:
        config = event['config']
    else:
        config = 'disabled'
    if 'support' in event: 
        support = event['support']
    else: 
        support = 'disabled'
    print(getConfiguredSCP(enabledregions,support,config))
    if 'accountcreate' in event:
        accountId = event['accountcreate']['CreateAccountStatus']['AccountId']
    else:
        accountId = event['accountId']
    if 'customermasteraccountid' in event:
        stsclient = boto3.client('sts')
        accountRole='TSI_Base_FullAccess'
        roleArn = 'arn:aws:iam::' + event['customermasteraccountid'] + ':role/' + accountRole
        role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountcreation')
        organizations = boto3.client('organizations',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    else:
        organizations = boto3.client('organizations')
    #Check if we have account specific policy already
    policyforaccount = {}
    policylistforaccresp = organizations.list_policies_for_target(TargetId=accountId,Filter='SERVICE_CONTROL_POLICY')
    for policy in policylistforaccresp['Policies']:
        policyforaccount[policy['Name']] = policy['Id']
    while 'NextToken' in policylistforaccresp:
        for policy in policylistforaccresp['Policies']:
            policyforaccount[policy['Name']] = policy['Id']
    print(policyforaccount)
    #Check if we have the account configuration policy, if not we need to create one
    if 'Configuration_{}'.format(accountId) in policyforaccount:
        print("Updating configuration for the account")
        print(organizations.update_policy(PolicyId=policyforaccount['Configuration_{}'.format(accountId)],Content=getConfiguredSCP(enabledregions,support,config)))
    else:
        print("Creating new SCP For the account")
        policyresp = organizations.create_policy(Content=getConfiguredSCP(enabledregions,support,config),Name='Configuration_{}'.format(accountId),Type='SERVICE_CONTROL_POLICY',Description = 'Configuration SCP for {}'.format(accountId))
        attachresp = organizations.attach_policy(PolicyId=policyresp['Policy']['PolicySummary']['Id'],TargetId=accountId)
        print(policyresp)
        print(attachresp)




#We need to get array for enabledregions
#support can be enabled or disabled
#config can managed allowd,or denied, if denied only the deliverychannels will be disabled
def getConfiguredSCP(enabledregions,support,config):
    #read json skeleton
    scpjson = json.loads(open('SCP.json','r').read())
    newscp = {'Version' : '2012-10-17','Statement' : []}
    #we need to copy to a new one
    #iterate through the statements, and if the index finds what we want as entry Sid we configure it
    for idx,statement in enumerate(scpjson['Statement']):
        #here we put the region list to the proper place
        if statement['Sid'] == 'DenyNotEnabledRegions':
            statement['Condition']['StringNotEqualsIfExists']['aws:RequestedRegion'] = enabledregions
            newscp['Statement'].append(statement)
        elif statement['Sid'] == 'DenyConfigDeliveries':
            if config == 'enabled':
                pass
            else:
                newscp['Statement'].append(statement)
        elif(statement['Sid'] == 'Support'):
            if (support == 'enabled'):
                pass
            else:
                newscp['Statement'].append(statement)
    return json.dumps(newscp)

