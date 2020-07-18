import boto3

def lambda_handler(event,context):
    if('customermasteraccountid' in event):
        stsclient = boto3.client('sts')
        accountRole='TSI_Base_FullAccess'
        roleArn = 'arn:aws:iam::' + event['customermasteraccountid'] + ':role/' + accountRole
        role = stsclient.assume_role(RoleArn=roleArn,RoleSessionName='accountcreation')
        organizations = boto3.client('organizations',aws_access_key_id=role['Credentials']['AccessKeyId'],aws_secret_access_key=role['Credentials']['SecretAccessKey'], aws_session_token=role['Credentials']['SessionToken'])
    else:
        #Get root ou id, and check the first level 
        #session = boto3.Session(profile_name='newroot')
        #session = boto3.Session()
        #organizations = session.client('organizations')
        organizations = boto3.client('organizations')
    masterorganizationroot = organizations.describe_organization()
    masteraccountorgid = masterorganizationroot['Organization']['Id']
    masteraccountrootid = organizations.list_roots()['Roots'][0]['Id']
    parentid = masteraccountrootid
    #We need to construct the array from the parameter which is coma seperated value
    oustruct = event['ouname'].split(",")
    #We need to have the first one existing, otherwise let's fail it#####
    if (checkforOU(organizations,parentid,oustruct[0]) == None):
        raise SystemExit("Top OU Not found")
    #We need to loop over the array, and check the subsequent organization unit id, at the last one we stop
    for ouname in oustruct:
        print("Starting loop")
        print(parentid)
        parentid = checkforOUandCreate(organizations,parentid,ouname)
        print(parentid)
    print("Here comes the parentid where we will put the account")
    print(parentid)
    return(parentid)


def checkforOUandCreate(organizations,parentid,ouname):
        #returns the id of the ou, if not existing, will create one, and gives back the id of the new ou :)
        print("checking for {}".format(ouname))
        ounames = {}
        orgunitsforparent = organizations.list_organizational_units_for_parent(ParentId=parentid)
        #{'OrganizationalUnits': [{'Id': 'ou-wmts-9zdpteqq', 'Arn': 'arn:aws:organizations::129287509598:ou/o-zibiay9yta/ou-wmts-9zdpteqq', 'Name': 'root6'}
        for entry in orgunitsforparent['OrganizationalUnits']:
            ounames[entry['Name']] = entry['Id']
        while('NextToken' in orgunitsforparent):
            orgunitsforparent = organizations.list_organizational_units_for_parent(ParentId=parentid,NextToken = orgunitsforparent['NextToken'])
            for entry in orgunitsforparent['OrganizationalUnits']:
                ounames[entry['Name']] = entry['Id']
        print(ounames)
        if (ouname not in ounames.keys()):
                print("We need to create one")
                oucreateresp = organizations.create_organizational_unit(ParentId=parentid,Name=ouname)
                return(oucreateresp['OrganizationalUnit']['Id'])

        else:
                print("Found it")
                return(ounames[ouname])

def checkforOU(organizations,parentid,ouname):
        #returns the id of the ou, if not existing, will create one, and gives back the id of the new ou :)
        print("checking for {}".format(ouname))
        ounames = {}
        orgunitsforparent = organizations.list_organizational_units_for_parent(ParentId=parentid)
        #{'OrganizationalUnits': [{'Id': 'ou-wmts-9zdpteqq', 'Arn': 'arn:aws:organizations::129287509598:ou/o-zibiay9yta/ou-wmts-9zdpteqq', 'Name': 'root6'}
        for entry in orgunitsforparent['OrganizationalUnits']:
            ounames[entry['Name']] = entry['Id']
        while('NextToken' in orgunitsforparent):
            orgunitsforparent = organizations.list_organizational_units_for_parent(ParentId=parentid,NextToken = orgunitsforparent['NextToken'])
            for entry in orgunitsforparent['OrganizationalUnits']:
                ounames[entry['Name']] = entry['Id']
        print(ounames)
        if (ouname not in ounames.keys()):
            print("Ou not found")
            return(None)

        else:
            print("Found it")
            return(ounames[ouname])
