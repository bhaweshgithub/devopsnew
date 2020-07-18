### Directory structure

* assembler.py The main script which is creating the cloudformation template with roles, and zip files
* cfassembler Contains the cfTemplate class, and methods to assembly the zip files 
* cloudformationtemplate Contains cloudformation templates used to provision customer account
* globalconfig.json Contains Parameters for assembly
* lambda Contains lambda functions to be packaged (plus metadata)
* policy Contains metadata for policies plus the policies itself
* role Contains the roles (used by lambda, and step functions)
* skeletons Cloudformation template (used by assembly script)
* stepfunction Contains step function state machines

##assembler.py

This file generates the artifacts, used later steps

Currently 3 environment variables are neccessary, and used for generate the deployment package
branchname, accountid,bucketname.

branchname used for suffixes in all objects
accountid is the accountid where the objects will be created
bucketname where the zip files are located

Running the assembler.py will create a folder (branchname) with all the neccessary objects added.

#TODO
