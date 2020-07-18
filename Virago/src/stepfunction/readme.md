### stepfunction folder

This folder contains the stepfunctions and the metadata.json file for each state machines.
The entry must contain the machinename,rolename,and source filename. 

##example:

{
"StepFunctions" :
[
        {
                "machinename" : "createNewAccount",
                "rolename": "StatesExecutionRole-eu-central-1",
                "source" : "createNewAccount.json"
        }
]
