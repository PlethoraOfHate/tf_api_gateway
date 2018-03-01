from datetime import datetime
import sys, traceback
import json
import requests



class apiGateway(object):
    
    def __init__(self, api_token, organization, **kwargs):
        """ Initializes the class object

        Input vars:
            api_token - Terraform Enterprise access token
            organization - Terraform username
        *Optional Vars*:
            workspace - Name of the workspace you're working with (Defaults to 'new_workspace' when not provided)
            tf_end_point = URL of the Terraform API endpoint
        """
        self.api_token = api_token
        self.organization = organization
        
        self.workspace = kwargs.pop('workspace', 'new_workspace')
        self.end_point = kwargs.pop('tf_end_point', 'https://atlas.hashicorp.com/api/v2')


#variables

    def getVariableList(self):
        """ Gets a list of all variables on the current workspace """
        end_point = self.end_point + "/vars"
        org_filter = "?filter[organization][username]=" + self.organization
        workspace_filter = "filter[workspace][name]=" + self.workspace

        web_request = end_point + org_filter + "&" + workspace_filter

        headers = {'Authorization': 'Bearer ' + self.api_token,
                   'Content-Type': 'application/vnd.api+json'}

        response = requests.get(web_request, headers=headers)
        
        data = json.loads(response.text)

        return(data)

    def addVariable(self, var_name, var_value):
        """ Adds a new variable to the current workspace

        Input Vars:
            var_name - Name of the variable to add
            var_value = Value to assign to the variable you're adding
        """

        end_point = self.end_point + "/vars"
        headers = {'Authorization': 'Bearer ' + self.api_token,
                   'Content-Type': 'application/vnd.api+json'}

        payload = json.dumps( self.__buildNewVariable( var_name, var_value ) )

        response = requests.post(end_point, headers=headers, data=payload)

        data = json.loads(response.text)

        return(data)

    def deleteVariable(self):
        return("Not implemented yet")

    def updateVariable(self, var_name, var_value):
        """ Updates the specified variable with the supplied value

        Input Vars:
            var_name - Name of the variable to add
            var_value = Value to assign to the variable you're adding
        """

        current_vars = self.getVariableList().get("data", [])
        end_point = self.end_point + "/vars/"
        headers = {'Authorization': 'Bearer ' + self.api_token,
                   'Content-Type': 'application/vnd.api+json'}

        try:
            var_dict = {d["attributes"]["key"]: d for d in current_vars}
            specific_var = var_dict[var_name]

        except:
            return("Error: Variable - " + var_name + " - not found.")

        end_point = end_point + specific_var['id']

        new_var = self.__buildNewVariable(var_name, var_value)
        new_var['data']['attributes']['category'] = specific_var['attributes']['category']
        new_var['data']['attributes']['hcl'] = specific_var['attributes']['hcl']
        new_var['data']['attributes']['sensitive'] = specific_var['attributes']['sensitive']
        new_var['data']['id]'] = specific_var['id']
        new_var.pop('filter',None)

        payload = json.dumps(new_var)

        response = requests.patch(end_point, data=payload, headers=headers)

        data = json.loads(response.text)

        return(data)

    def __buildNewVariable(self, var_name, var_value):
        """ Private method to create a new variable json structure """

        full_array = {}
        data = {}
        attributes = {}
        filter = {}
        organization = {}
        workspace = {}

        workspace['name'] = self.workspace
        organization['username'] = self.organization

        filter['organization'] = organization
        filter['workspace'] = workspace

        attributes['key'] = var_name
        attributes['value'] = var_value
        attributes['category'] = "terraform"
        attributes['hcl'] = False
        attributes['sensitive'] = False

        data['type'] = "vars"
        data['attributes'] = attributes

        full_array['data'] = data
        full_array['filter'] = filter

        return(full_array)

#endvariables


#workspaces
    def getWorkspaceList(self):
        """ Returns a list of all the current workspaces on your account """

        end_point = self.end_point + "/organizations/" + self.organization +"/workspaces"

        headers = {'Authorization': 'Bearer ' + self.api_token,
                   'Content-Type': 'application/vnd.api+json'}

        response = requests.get(end_point, headers=headers)
        
        data = json.loads(response.text)

        return(data)

    def addWorkspace(self, workspace_name):
        """ Adds a new workspace to Terraform

        Input Vars:
            workspace_name = Name of the workspace to add
        """

        end_point = self.end_point + "/organizations/" + self.organization +"/workspaces"
        headers = {'Authorization': 'Bearer ' + self.api_token,
                   'Content-Type': 'application/vnd.api+json'}

        payload = json.dumps( self.__buildNewWorkspace(workspace_name) )

        response = requests.post(end_point, headers=headers, data=payload)

        data = json.loads(response.text)

        return(data)

    def addWorkspaceWithVcs(self):
        return("Not implemented yet")

    def deleteWorkspace(self, workspace_name):
        """ Deletes the named workspace from Terraform

        input_vars:
            workspace_name - Name of the workspace to delete
        """
        end_point = self.end_point + "/organizations/" + self.organization +"/workspaces/" + workspace_name
        headers = {'Authorization': 'Bearer ' + self.api_token,
                   'Content-Type': 'application/vnd.api+json'}

        response = requests.delete(end_point, headers=headers)

        data = json.loads(response.text)

        return(data)

    def updateWorkspace(self):
        return("Not implemented yet")

    def __buildNewWorkspace(self, workspace_name, **kwargs):
        """ Private method to build a new workspace json structure. Support both basic and VCS workspaceds """
        full_array = {}
        data = {}
        attributes = {}

        if len(kwargs) > 0:
            ingress_trigger_attributes = {}

            attributes['name'] = workspace_name
            attributes['working-directory'] = workspace_name
            if kwargs['git_repo_name']:
                attributes['linkable-repo-id'] = kwargs['git_repo_name']
            else:
                return("Error: Git Repo Name Required")
            
            if kwargs['oauth-token-id']:
                attributes['oauth-token-id'] = kwargs['oauth-token-id']
            else:
                return("Error: OAuth Token ID Required")

            if kwargs['git_branch']:
                ingress_trigger_attributes['branch'] = kwargs['git_branch']
                ingress_trigger_attributes['default-branch'] = False
            else:
                ingress_trigger_attributes['branch'] = ""
                ingress_trigger_attributes['default-branch'] = True

            ingress_trigger_attributes['vcs-root-path'] = kwargs.pop('vcs-root-path', '')

            attributes["ingress-trigger-attributes"] = ingress_trigger_attributes

            data['type'] = "compound-workspaces"
            data['attributes'] = attributes

            full_array['data'] = data
        else:
            attributes['name'] = workspace_name

            data['type'] = "workspaces"
            data['attributes'] = attributes

            full_array['data'] = data

        return(full_array)

#endworkspaces

#OAuthTokens

    def getOauthTokens(self):
        """ Gets a list of all the OAuth tokens configured for your account """
        end_point = self.end_point + "/organizations/" + self.organization +"/oauth-tokens"

        headers = {'Authorization': 'Bearer ' + self.api_token,
                   'Content-Type': 'application/vnd.api+json'}

        response = requests.get(end_point, headers=headers)
        
        data = json.loads(response.text)

        return(data)

#endOAuthTokens


    
