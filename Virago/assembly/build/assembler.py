#!/usr/bin/env python3

import boto3
import json
import sys
import os
from cfassembler import cfTemplate
from cfassembler import artifact

srcdir = os.environ['CODEBUILD_SRC_DIR']+"/src/"

with open('{}lambda/metadata.json'.format(srcdir)) as file:
    lambdametas = json.load(file)
with open('{}role/metadata.json'.format(srcdir)) as file:
    rolemetadatas = json.load(file)
with open('{}policy/metadata.json'.format(srcdir)) as file:
    policymetas = json.load(file)
with open('{}stepfunction/metadata.json'.format(srcdir)) as file:
    stepmetas = json.load(file)
with open('{}cloudformationtemplate/metadata.json'.format(srcdir)) as file:
    cfmetas = json.load(file)

rolelistneeds = []
availableroles = []

for rolemetadata in rolemetadatas['Roles']:
    if (not rolemetadata['rolename'] in availableroles):
        availableroles.append(rolemetadata['rolename'])
for lambdameta in lambdametas['Lambdas']:
    if (not lambdameta['rolename'] in availableroles):
        rolelistneeds.append(lambdameta['rolename'])
for stepmeta in stepmetas['StepFunctions']:
    if(not stepmeta['rolename'] in availableroles):
        rolelistneeds.append(stepmeta['rolename'])

for roleneed in rolelistneeds:
    if(not roleneed in availableroles):
        print("ERROR - {} Not in the list".format(roleneed))
        sys.exit(1)

artifact.createDir()

cftemplate = cfTemplate.cfTemplate("{}skeletons/cloudformation.json".format(srcdir))
for lambdaresource in lambdametas['Lambdas']:
    cftemplate.addResource(lambdaresource,"lambda")
    artifact.createArtifact(lambdaresource,"lambda")
for policyresource in policymetas['Policies']:
    cftemplate.addResource(policyresource,"policy")
for roleresource in rolemetadatas['Roles']:
    cftemplate.addResource(roleresource,"role")
for stepresource in stepmetas['StepFunctions']:
    cftemplate.addResource(stepresource,"stepfunction")
for stackset in cfmetas['CFTemplates']:
    artifact.createArtifact(stackset,"cloudformationtemplate")
    

artifact.writeCfTemplate(cftemplate.getJson())
