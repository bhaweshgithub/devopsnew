### Cloudformation templates folder

Here the cloudformation templates (used for customer accounts) should be placed, alongside with the metadata.
metadata.json file contains the list of the templates. Currently source, and region must be provided for every entry. 

##example:

{
        "CFTemplates":
        [
                {
                        "source": "baseline.json",
                        "region" :"eu-central-1"
                },

                {
                        "source": "securityalert.json",
                        "region" :"eu-central-1"
                }
                ]
}

