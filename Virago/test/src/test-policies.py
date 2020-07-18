#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import datetime
import logging
import os
import json
import ptvsd

debugging=int(os.environ.get("debugging", 0))
if debugging == 1:
    # Allow other computers to attach to ptvsd at this IP address and port.
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)

    # Pause the program until a remote debugger is attached
    ptvsd.wait_for_attach()

# in case of a proxy
proxy=int(os.environ.get("proxy", 0))
if proxy:
    #os.environ["HTTP_PROXY"] = "http://proxy.mms-dresden.de:8080"
    #os.environ["HTTPS_PROXY"] = "https://proxy.mms-dresden.de:8080"
    os.environ["HTTP_PROXY"] = "192.168.199.10:8000"
    os.environ["HTTPS_PROXY"] = "192.168.199.10:8000"

# Resource types this function can evaluate
APPLICABLE_RESOURCES = ["AWS::IAM::User"]
# Actions that we will simulate to determine compliance
POWERFUL_ACTIONS = ['iam:Create*', 'iam:Delete*']

today = datetime.datetime.today()
now = datetime.datetime.now()
current_date = today.strftime("%Y%m%d_%H%M")

def evaluate_compliance(configuration_item, result_token):
    resource_name = configuration_item["resourceName"]
    resource_arn = configuration_item["ARN"]
    resource_type = configuration_item["resourceType"]
    resource_id = configuration_item["resourceId"]
    account_id = configuration_item["awsAccountId"]
    policies = configuration_item["policies"]

    # Error out if resource is not applicable
    if resource_type not in APPLICABLE_RESOURCES:
        return "NOT_APPLICABLE - resourcetype '"+resource_type+"' not implemented."

    # Create clients to call other services
    iam = boto3.client("iam")
    config = boto3.client("config")

    # logic for entity type and simulation
    compliance_status = simulate_principal_policy(iam, resource_arn, policies)

    # ... more tests, e.g. as function list

    # ....

    # sum up results

    result = 'NOT OK'
    if compliance_status == 'COMPLIANT':
        result = 'OK'
    
    return result

def simulate_principal_policy(iam, resource_arn, policies):
    # Call IAM to simulate the policy on restricted actions.
    response = iam.simulate_principal_policy(PolicySourceArn=resource_arn,ActionNames=POWERFUL_ACTIONS,ResourceArns=['*'])
    results = response['EvaluationResults']
    
    allows_powerful_action = False
    allows_powerful_action_is_compliant = False
    print("Policies:")
    print(policies)
    if 'POWERFUL_ACTIONS' in policies:
        allows_powerful_action_is_compliant = (policies['POWERFUL_ACTIONS'] == 'allowed')
        print("Override Policies:")
        print(allows_powerful_action_is_compliant)

    # Determine if any restricted actions are allowed.
    for actions in results:
        eval_decision = actions['EvalDecision']

        if(eval_decision == 'allowed'):
            action_name = actions['EvalActionName']
            print("Restricted action " + action_name + " was granted to resource " + resource_arn)
            allows_powerful_action = True

    # If any restricted actions were allowed, consider the resource non-compliant.
    if(allows_powerful_action and not allows_powerful_action_is_compliant):
        return "NON_COMPLIANT"
    return "COMPLIANT"

def lambda_handler(event, context):
    #invoking_event = json.loads(event["invokingEvent"])
    configuration_item = event["configurationItem"]
    result_token = "mydummyToken"
    if "resultToken" in event:
        result_token = event["resultToken"]

    # Evaluate whether the resource is compliant
    result = evaluate_compliance(configuration_item, result_token)

    return result