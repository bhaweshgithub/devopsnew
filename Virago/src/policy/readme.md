### policy folder

This folder contains the policies.
Every policy used by any role must be declared here. The policy metadata contains the type (Managed or Custom), the arn (if managed by AWS), the PolicyName, and source (if it's customer) of the file containing the policy.

##example:

{
        "Policies":
        [
                {
                        "Type": "Managed",
                        "arn": "arn:aws:iam::aws:policy/AdministratorAccess",
                        "PolicyName" : "AdministratorAccess"
                },

                {
                        "Type": "Custom",
                        "PolicyName": "lambdaexecute",
                        "source": "lambdaexecutionerrole.json"
                }
	]
}
