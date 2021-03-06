import json

import requests


class apiGateway(object):

    def __init__(self, api_token, organization, **kwargs):
        """ Initializes the class object

        Args:
            api_token (str): Terraform Enterprise access token
            organization (str): Terraform username
            workspace (str): *OPTIONAL* Name of the workspace you're working with (Defaults to 'new_workspace' when not provided)
            tf_end_point (str): *OPTIONAL* URL of the Terraform API endpoint
        """  # noqa
        self.api_token = api_token
        self.organization = organization

        self.workspace = kwargs.pop('workspace', 'new_workspace')
        self.end_point = kwargs.pop(
            'tf_end_point', 'https://app.terraform.io/api/v2',
        )

    # variables
    def getVariableList(self):
        """ Gets a list of all variables on the current workspace

        Returns:
            dict: The list of variables

        """
        end_point = self.end_point + "/vars?"
        org_filter = "filter[organization][name]=" + self.organization
        workspace_filter = "filter[workspace][name]=" + self.workspace

        web_request = end_point + org_filter + "&" + workspace_filter

        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        response = requests.get(web_request, headers=headers)

        data = json.loads(response.text)

        return(data)

    def addVariable(self, var_name, var_value, **kwargs):
        """ Adds a new variable to the current workspace

        Args:
            var_name (str): Name of the variable to add
            var_value (str): Value to assign to the variable you're adding

        Returns:
            dict: The JSON response from the API
        """

        end_point = self.end_point + "/vars"
        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        new_variable = self.__buildNewVariable(var_name, str(var_value))

        if isinstance(var_value, dict):
            new_variable['data']['attributes']['hcl'] = True

        new_variable['data']['attributes']['sensitive'] = kwargs.pop(
            'is_sensitive', False,
        )

        payload = json.dumps(new_variable)

        response = requests.post(end_point, headers=headers, data=payload)

        data = json.loads(response.text)

        return(data)

    def deleteVariable(self, var_name):
        """ Deletes the specified variable

        Args:
            var_name (str): Name of the variable to add

        Returns:
            dict: The JSON response from the API
        """

        current_vars = self.getVariableList().get("data", [])
        end_point = self.end_point + "/vars/"
        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        try:
            var_dict = {d["attributes"]["key"]: d for d in current_vars}
            specific_var = var_dict[var_name]

        except KeyError:
            return("Error: Variable - " + var_name + " - not found.")

        end_point = end_point + specific_var['id']

        response = requests.delete(end_point, headers=headers)

        return(response.text)

    def updateVariable(self, var_name, var_value):
        """ Updates the specified variable with the supplied value

        Args:
            var_name (str): Name of the variable to add
            var_value (str): Value to assign to the variable you're adding

        Returns:
            dict: The JSON response from the API
        """

        current_vars = self.getVariableList().get("data", [])
        end_point = self.end_point + "/vars/"
        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        try:
            var_dict = {d["attributes"]["key"]: d for d in current_vars}
            specific_var = var_dict[var_name]

        except KeyError:
            return("Error: Variable - " + var_name + " - not found.")

        end_point = end_point + specific_var['id']

        new_var = self.__buildNewVariable(var_name, var_value)
        new_var['data']['attributes']['category'] = specific_var['attributes']['category']
        new_var['data']['attributes']['hcl'] = specific_var['attributes']['hcl']
        new_var['data']['attributes']['sensitive'] = specific_var['attributes']['sensitive']
        new_var['data']['id]'] = specific_var['id']
        new_var.pop('filter', None)

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
        organization['name'] = self.organization

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
    # endvariables

    # workspaces
    def getWorkspaceList(self):
        """ Returns a list of all the current workspaces on your account

        Returns:
            dict: The JSON list of workspaces from the API

        """

        end_point = self.end_point + "/organizations/" + \
            self.organization + "/workspaces?size=100"

        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        response = requests.get(end_point, headers=headers)

        data = json.loads(response.text)

        nextPage = data

        totalPages = data['meta']['pagination']['total-pages']

        x = 1
        while x < totalPages:
            nextPage = requests.get(nextPage['links']['next'], headers=headers)
            nextPage = json.loads(nextPage.text)
            data['data'] = data['data'] + nextPage['data']
            x += 1

        return(data)

    def addWorkspace(self, workspace_name):
        """ Adds a new workspace to Terraform

        Args:
            workspace_name (str): Name of the workspace to add

        Returns:
            dict: The JSON response from the API
        """

        end_point = self.end_point + "/organizations/" + self.organization + "/workspaces"
        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        payload = json.dumps(self.__buildNewWorkspace(workspace_name))

        response = requests.post(end_point, headers=headers, data=payload)

        data = json.loads(response.text)

        return(data)

    def addWorkspaceWithVcs(self, workspace_name, git_repo_name):
        """ Adds a new workspace to Terraform

        Args:
            workspace_name (str): Name of the workspace to add
            git_repo_name (str): Path of the git project on the server (e.g. attainia-development/svc-atainia-api)

        Returns:
            dict: The JSON response from the API
        """
        oauth_token = self.getOauthTokens()
        end_point = self.end_point + "/organizations/" + self.organization + "/workspaces"
        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        payload = json.dumps(self.__buildNewWorkspace(
            workspace_name, git_repo_name=git_repo_name, oauth_token_id=oauth_token[
                'data'
            ][0]['id'],
        ))

        response = requests.post(end_point, headers=headers, data=payload)

        data = json.loads(response.text)

        return(data)

    def deleteWorkspace(self, workspace_name):
        """ Deletes the named workspace from Terraform

        Args:
            workspace_name (str): Name of the workspace to delete

        Returns:
            dict: The JSON response from the API
        """
        end_point = self.end_point + "/organizations/" + \
            self.organization + "/workspaces/" + workspace_name
        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

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
        vcs_repo = {}

        if len(kwargs) > 0:
            vcs_repo = {}

            attributes['name'] = workspace_name
            attributes['working-directory'] = ""
            if ('git_repo_name' in kwargs):
                vcs_repo['identifier'] = kwargs['git_repo_name']
            else:
                return("Error: Git Repo Name Required")

            if ('oauth_token_id' in kwargs):
                vcs_repo['oauth-token-id'] = kwargs['oauth_token_id']
            else:
                return("Error: OAuth Token ID Required")

            if ('git_branch' in kwargs):
                vcs_repo['branch'] = kwargs['git_branch']
                vcs_repo['default-branch'] = False
            else:
                vcs_repo['branch'] = ""
                vcs_repo['default-branch'] = True

            attributes["vcs-repo"] = vcs_repo

            data['type'] = "workspaces"
            data['attributes'] = attributes

            full_array['data'] = data
        else:
            attributes['name'] = workspace_name

            data['type'] = "workspaces"
            data['attributes'] = attributes

            full_array['data'] = data

        return(full_array)
    # endworkspaces

    # OAuthTokens
    def getOauthTokens(self):
        """ Gets a list of all the OAuth tokens configured for your account

        Returns:
            dict: The JSON list of OAuth tokens from the API
        """
        end_point = self.end_point + "/organizations/" + \
            self.organization + "/oauth-tokens"

        headers = {
            'Authorization': 'Bearer ' + self.api_token,
            'Content-Type': 'application/vnd.api+json',
        }

        response = requests.get(end_point, headers=headers)

        data = json.loads(response.text)

        return(data)
    # endOAuthTokens
