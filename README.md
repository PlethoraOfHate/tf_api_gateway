# tf_api_gateway
Python Wrapper gateway for the Terraform Enterprise API

***NOTE*** This is currently a [WIP] and will be evolving until it reaches a 1.0 version

Since HashiCorp has decided to move the interface to Terraform Enteprise (formerly Atlas) to an API instead of using the command-line tool, the need quickly arose for an easy way to interface with this API. As such, I chose to create a python wrapper class that makes it relatively easy to utilize the API, both in day-2-day work, as well as integration into CI/CD pipelines and other similar use-cases. In case it is not clear, this is meant to be a companion framework to be used in other higher-level applications/utilities.

Currently this is still a work in progress, both due to available time, as well as the availability and accuracy of HashiCorp's API documentation, which is in Beta. Currently, the 'workspace', 'oauth', and 'variables' routes are implemented. Methods not yet completed are stubbed but simple return a "Not Completed" string.

In the future, I will be including example utilities to demonstrate various use-cases for this framework.

# Usage

To Install:

```
pip install tf_api_gateway
```

Example of usage:

```
from tf_api_gateway import apiGateway

myToken = '[TF_TOKEN]'
myOrg = '[TERRAFORM_USER]'
myWorkspace = '[WORSPACE_NAME]

myGateway = apiGateway(api_token = myToken, 
                                      organization = myOrg, 
                                      workspace = myWorkspace)

## Add a variable to workspace
myGateway.addVariable( var_name="var_name", 
                       var_value="var_value" )
```

Currently, the following methods are implemented:
* getVariableList()
* addVariable()
* deleteVariable()
* updateVariable()
* getWorkspaceList()
* addWorkspace()
* deleteWorkspace()
* getOauthTokens()
