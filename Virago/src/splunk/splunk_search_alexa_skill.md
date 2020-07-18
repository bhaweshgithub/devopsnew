# Splunk Search Sting for Alexa Skill

This Splunk search sting give back a comma seperated list with new created users in all accounts over all AWS Region.
If you like to reduce the output to one account, you need to change the aws_account_id="*" -> to aws_account_id="%accountid%"

## This is the SPL code

´´´
(index="main" OR (index="main" OR index="aws_idx")) sourcetype="aws:cloudtrail" aws_account_id="*" region="*" | lookup all_eventName eventName OUTPUT function | fillnull value="N/A" function | search function="IAM" | eval notable=if(match(eventName, "(^Get*|^List*|^Describe*)"), 0, 1) | search notable=1 eventName=CreateUser "responseElements.user.userName"="*" CreateUser | fields "responseElements.user.userName" | mvcombine delim=", " "responseElements.user.userName" | nomv "responseElements.user.userName"
´´´
