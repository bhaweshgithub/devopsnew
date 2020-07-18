import boto3
from time import sleep
from botocore.exceptions import ClientError
import json
from boto3.dynamodb.types import TypeDeserializer
import uuid
import os

def findDiffKeys(newitem, olditem):
    removed = set(olditem.keys()).difference(set(newitem.keys()))
    added = set(newitem.keys()).difference(set(olditem.keys()))
    if (len(added) == 0):
        added = ""
    if(len(removed) ==0):
        removed = ""
    print("Added key : {}, removed keys: {}".format(added,removed))
    return({'removed' : list(removed), 'added' : list(added) })

def findDiffElements(newitem,olditem):
    #We are not diffing for keys not existing in the new and in the old version
    keyDiffs = findDiffKeys(newitem,olditem)
    commonKeys = set(newitem.keys()).intersection(set(olditem.keys()))
    changedKeys = {'new' : {}, 'old': {}}
    for key in commonKeys:
        if newitem[key] != olditem[key]:
            print("{} is changed to : {}".format(key,newitem[key]))
            changedKeys['new'][key] = newitem[key]
            print("{} old value is : {}".format(key, olditem[key]))
            changedKeys['old'][key] = olditem[key]
    return(changedKeys)

def updateTemplate(task,interesting_tasks):
    stepfunctions = boto3.client('stepfunctions')
    deserializer =  TypeDeserializer()
    accountId = task['accountId']
    parameterOverrides = []
    encryptionparams = {}
    newregions = []
    for overridekey in task['diff']['new'].keys():
        if overridekey in interesting_tasks:
            if overridekey == 'enabledregions':
                overrideelement = {}
                overrideelement['ParameterKey'] = overridekey
                overrideelement['ParameterValue'] = ",".join(task['diff']['new'][overridekey])
                parameterOverrides.append(overrideelement)
            else:    
                overrideelement = {}
                overrideelement['ParameterKey'] = overridekey
                overrideelement['ParameterValue'] = task['diff']['new'][overridekey]
                parameterOverrides.append(overrideelement)
    if 'enabledregions' in task['diff']['new'].keys():
        newregions = set(task['diff']['new']['enabledregions'])-set(task['diff']['old']['enabledregions'])
        encryptionparams = {'accountId' : accountId, 'enabledregions' : ",".join(list(newregions))}
    
    if 'awsconfigenabled' in task['diff']['new'].keys():
        newregions = []
        for r in task['newImage']['enabledregions']['L']:
            newregions.append(r['S'])
        encryptionparams = {'accountId' : accountId, 'enabledregions' : ",".join(list(newregions))}

    inputjson = json.dumps({'accountId' : accountId,'encryptionparams' : encryptionparams, 'overrides': parameterOverrides,'newregions' : list(newregions), 'newregionscount' : len(newregions), 'newImage' : task['newImage']})
    print(inputjson)
    statemachinearn = 'arn:aws:states:eu-central-1:'+ os.environ['accountid'] + ':stateMachine:enableRegion-' + os.environ['branchname'] 
    response = stepfunctions.start_execution(
        stateMachineArn=statemachinearn,
        name='{}-{}'.format(accountId,str(uuid.uuid4())),
        input=inputjson
    )
    print(response)
    
def processDynamoDBTrigger(event):
    tasks = []
    deserializer =  TypeDeserializer()
    for item in event['Records']:
    #process only modifications
        if item['eventName'] != 'MODIFY':
            continue
        olditem = {}
        newitem = {}
        for entry in item['dynamodb']['NewImage'].keys() :
            newitem[entry] = deserializer.deserialize(item['dynamodb']['NewImage'][entry])
        for entry in item['dynamodb']['OldImage'].keys() :
            olditem[entry] = deserializer.deserialize(item['dynamodb']['OldImage'][entry])
        task = {'accountId' : str(deserializer.deserialize(item['dynamodb']['NewImage']['accountId'])), 'diff' : findDiffElements(newitem,olditem) , 'newImage' : item['dynamodb']['NewImage']}
        if (len(task['diff']['new']) > 0):
            tasks.append(task)
        if (len(tasks)==0):
            print("no tasks found")
        else:
            for task in tasks:
                interesting_tasks = ["supportenabled", "enabledregions", "awsconfigenabled"]
                if (len(set(interesting_tasks).intersection(set(task['diff']['new'].keys())))>0):
                    updateTemplate(task,interesting_tasks)
                else:
                    print("No interesting tasks")



def lambda_handler(event, context):
    print("Got event from dynamodb")
    processDynamoDBTrigger(event)

