import json
import os
from email import policy

srcdir = os.environ['CODEBUILD_SRC_DIR']+"/src/"


class cfTemplate():
    def __init__(self,skeletonfile):
        with open(skeletonfile) as file:
            self.json = json.load(file)
        self.bucketname = os.environ['bucketname']
        self.branchname = os.environ['branchname']
        self.accountid = os.environ['accountid']
        self.availablepolicies = {}
        with open('{}policy/metadata.json'.format(srcdir)) as file:
            self.policymetas = json.load(file)
        for policymetadata in self.policymetas['Policies']:
            if (not policymetadata['PolicyName'] in self.availablepolicies):
                self.availablepolicies[policymetadata['PolicyName']] = policymetadata['Type']

    def printJson(self):
        print(json.dumps(self.json))
    def getJson(self):
        return json.dumps(self.json)

    def addResource(self,entry,type):
        if(type == 'lambda'):
            print("Adding LAMBDA: {} lambda function to cftemplate".format(entry['source']))
            resource = {"Type" : "AWS::Lambda::Function",
                        "Properties" : {
                                        "Code":
                                                {
                                                    "S3Bucket" : self.bucketname,
                                                    "S3Key" : "{}/{}.zip".format(os.environ['branchname'],entry['source'])
                                                },
                                        "Handler" : "lambda_function.lambda_handler",
                                        "MemorySize" : "128",
                                        "Role" : "arn:aws:iam::{}:role/{}".format(self.accountid,entry['rolename']+"-"+os.environ['branchname']),
                                        "Runtime" : "python3.6",
                                        "Timeout" : "300",
                                        "FunctionName" : entry['source']+"-"+os.environ['branchname'],
                                        "Environment" : { "Variables" : {"accountid" : os.environ['accountid'], "branchname": os.environ['branchname'], "secdevopsid" : os.environ['secdevopsid'], "kmskeyid" : os.environ['kmskeyid'], "provbucketname" : os.environ['provbucketname'], "secdevopsbucketname" : os.environ['secdevopsbucketname'] ,"bucketname" : os.environ['bucketname'], "mfateamemail" : os.environ['mfateamemail'], "aws_config_role" : os.environ['aws_config_role'], "awsconfigBucket" : os.environ['awsconfigBucket'], "awsconfigname" : os.environ['awsconfigname'], "awsconfigdeliverychannel" : os.environ['awsconfigdeliverychannel'],"terraformbucket" : os.environ['terraformbucket'], "terraformversion" : os.environ['terraformversion'] } }
                                        }
                        }
            if("environment" in entry):
                for variable in entry['environment']:
                    resource['Properties']['Environment']['Variables'][variable] = entry['environment'][variable]
            self.json['Resources'][entry['source'].replace("-","").replace("_","")+os.environ['branchname']] = resource
            self.json['Resources'][entry['source'].replace("-","").replace("_","")+os.environ['branchname']]['DependsOn'] = entry['rolename'].replace("-","").replace("_","")+"role"+os.environ['branchname']
        if((type == 'policy') and (entry['Type'] == 'Custom') ):
            print("Adding POLICY: {} Policy to cftemplate".format(entry['PolicyName']))
            resource = {
                        "Type": "AWS::IAM::ManagedPolicy",
                        "Properties": {
                                        "Description" : "",
                                        "PolicyDocument" : json.loads(open("{}policy/{}".format(srcdir,entry['source']),'r').read().replace("_PROVBUCKETNAME_","arn:aws:s3:::"+os.environ['provbucketname']).replace("_KMSKEYID_",os.environ['kmskeyid'])),
                                        "ManagedPolicyName" : entry['PolicyName']+"-"+os.environ['branchname']
                                        }
                        }
            self.json['Resources'][entry['PolicyName'].replace("-","").replace("_","")+"policy"+os.environ['branchname']] = resource
        if(type == 'role'):
            print("Adding ROLE: {} Policy to cftemplate".format(entry['rolename']))
            policyarns = []
            for arn in entry['policies']:
                if((arn in self.availablepolicies) and (self.availablepolicies[arn] == 'Custom')):
                    policyarns.append("arn:aws:iam::{}:policy/{}".format(self.accountid, arn+"-"+os.environ['branchname']))
                elif((arn in self.availablepolicies) and (self.availablepolicies[arn] == 'Managed')):
                    policyarns.append("arn:aws:iam::aws:policy/{}".format(arn))
            if (entry['service'] == 'lambda'):
                servicename = "lambda.amazonaws.com"
            elif(entry['service'] == 'config'):
                servicename = "config.amazonaws.com"
            elif(entry['service'] == 'states'):
                servicename = "states.amazonaws.com"
                pass
            resource = {
                        "Type": "AWS::IAM::Role",
                        "Properties": {
                            "AssumeRolePolicyDocument": {
                                    "Version" : "2012-10-17",
                                    "Statement": [ {
                                        "Effect": "Allow",
                                        "Principal": {
                                            "Service": [ servicename ]
                                            },
                                        "Action": [ "sts:AssumeRole" ]
                                                    } ]
                            },
                            "ManagedPolicyArns": policyarns,
                            "RoleName": entry['rolename']+"-"+os.environ['branchname']
                            }
                        }
            self.json['Resources'][entry['rolename'].replace("-","").replace("_","")+"role"+os.environ['branchname']] = resource
            self.json['Resources'][entry['rolename'].replace("-","").replace("_","")+"role"+os.environ['branchname']]['DependsOn'] = []
            for dependency in entry['policies']:
                if (self.availablepolicies[dependency] == 'Custom'):
                    self.json['Resources'][entry['rolename'].replace("-","").replace("_","")+"role"+os.environ['branchname']]['DependsOn'].append(dependency.replace("-","").replace("_","")+"policy"+os.environ['branchname'])
        if(type == 'stepfunction'):
            print("Adding Stepfunction: {} Policy to cftemplate".format(entry['machinename']))
            definitionstringfile = open("{}stepfunction/{}".format(srcdir,entry['source']),'r').read().replace("_ACCOUNTID_", self.accountid).replace("_BRANCHNAME_", self.branchname).replace("_SUBNETA_", os.environ['subneta']).replace("_SUBNETB_", os.environ['subnetb'])
            definitionstring = json.loads(definitionstringfile)
            #for state in definitionstring['States']:
            #    if('Resource' in definitionstring['States'][state]):
            #        definitionstring['States'][state]['Resource']+="-"+os.environ['branchname']
            resource = {
                        "Type": "AWS::StepFunctions::StateMachine",
                        "Properties": {
                            "StateMachineName": entry['machinename']+"-"+os.environ['branchname'],
                            "DefinitionString": json.dumps(definitionstring,indent=4),
                            "RoleArn": "arn:aws:iam::{}:role/{}".format(self.accountid,entry['rolename']+"-"+os.environ['branchname'])
                            }
                        }
            self.json['Resources'][entry['machinename'].replace("-","").replace("_","")+"step"+os.environ['branchname']] = resource
            self.json['Resources'][entry['machinename'].replace("-","").replace("_","")+"step"+os.environ['branchname']]['DependsOn'] = entry['rolename'].replace("-","").replace("_","")+"role"+os.environ['branchname']
        if(type == 'cloudformation'):
            pass
