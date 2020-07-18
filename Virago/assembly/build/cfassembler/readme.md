###cfassembler folder

This directory contains the modules cfassembler. 
The module has a class called cfTemplate, which generates the cloudformation template (used for deploying the artifacts).

##cfTemplate class

The class having 3 methods:
printJson - prints the Json into stdout
getJson - returns the json object
addResource - Adds the resource into the cloudformation template

#addResource

The function gets an entry, and a type as parameters.
The entry depends on the type, and defined in the metadata files. 

##artifact module
The artifact module responsible to create to create the artifact packaging.

createDir - creates directory according to the branchname variable
writeCfTemplate - writes the template file into the folder
createArtifact - adds the lambda_function.py file in the lambda function to a zip file, inside the folder, cloudformationtemplate copied into the folder
