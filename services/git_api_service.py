import requests
import logging
import json
import os

class GitHubEndpoints:
    def __init__(self, config_path):
        self.endpoints = {}
        self.load_endpoints(config_path)
    
    def load_endpoints(self, config_path):
        with open(config_path) as config_file:
            config_data = json.load(config_file)
            if "GitHub" in config_data:
                self.endpoints = config_data["GitHub"]
            else:
                print("GitHub endpoints not found in config.")
    
    def format_endpoint(self, endpoint, **kwargs):
        base_url = self.endpoints.get("baseurl", "")
        full_endpoint = self.endpoints.get(endpoint, "")
        return (base_url + full_endpoint).format(**kwargs)

github_endpoints = GitHubEndpoints(os.path.join(os.getcwd(),"files","configuration_files","api_urls.json"))

def check_repository_exists(owner, repo_name, access_token):
    restult = False
    api_url = github_endpoints.format_endpoint("check_repository_exists", repository_owner=owner, repository_name=repo_name)
    # api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            restult = True
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while checking repository: {e}")
        print(f"An error occurred while checking repository: {e}")

    return restult

def check_branch_exists(owner, repo_name, branch_name, access_token):
    restult = False
    api_url = github_endpoints.format_endpoint("check_branch_exists", repository_owner=owner, repository_name = repo_name, _branch_name=branch_name)
    #api_url = f"https://api.github.com/repos/{owner}/{repo_name}/branches/{branch_name}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
           restult = True
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while checking branch exist or not: {e}")
        #print(f"An error occurred while checking branch exist or not: {e}")

    return restult


def get_commit_sha(access_token, owner, repo,branch,commit_index=0):
    restult = False
    commit_sha = None
    api_url = github_endpoints.format_endpoint("get_commit_sha", repository_owner=owner, repository_name=repo, _branch_name=branch)
    #api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?sha={branch}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        
        response = requests.get(api_url,headers=headers)
        
        if response.status_code == 200:
            
            commits = response.json()
            commit_sha = commits[commit_index]['sha']
            restult = True

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while getting branch commit : {e}")
        #print(f"An error occurred while branch commit : {e}")

    return restult,commit_sha

def download_updated_code(access_token,owner, repo, commit_sha, download_path):
    restult = False
    api_url = github_endpoints.format_endpoint("download_updated_code", repository_owner=owner, repository_name=repo, _commit_sha=commit_sha)
    #api_url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{commit_sha}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(api_url,headers=headers)
        if response.status_code == 200:

            tarball_content = response.content

            with open(download_path, "wb") as f:
                f.write(tarball_content)

            #print("Code downloaded and saved:", download_path)
            restult = True
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while downloading code: {e}")
        #print(f"An error occurred while downloading code: {e}")
    
    return restult