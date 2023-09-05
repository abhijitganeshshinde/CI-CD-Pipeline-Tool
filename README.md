# CI-CD-Pipeline-Tool Script

## Overview

The CICD (Continuous Integration and Continuous Deployment) script is designed to automate the deployment process for a set of Git repositories. It streamlines the process of checking for updates in specified branches, downloading and extracting the code, and deploying it to the designated environment.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Configuration](#configuration)
- [Logging](#logging)
- [License](#license)

## Features

- Automatically checks for updates in specified Git repositories and branches.
- Downloads and extracts the latest code from the Git repository.
- Deploys the code to the specified environment (e.g., QA, UAT, or PROD).
- Supports both HTML and Python (Flask) projects.
- Manages Nginx configuration for web applications.
- Keeps track of the last commit to avoid redundant deployments.

## Prerequisites

Before using the script, make sure you have the following prerequisites in place:

- Python 3.x
- Required Python packages (specified in the script)
- Git
- Nginx (for web application deployment)
- Internet connection for accessing Git repositories
- Access tokens for private repositories (if applicable)

## Usage

1. Clone the repository containing the CICD script.
2. Configure the deployment settings in the `config.json` file.
3. Run the script using the following command:

   ```python
   python CICD.py
The script will automate the deployment process based on the configuration provided.

## Configuration
The `config.json` file contains the configuration for your CICD process. It specifies the Git repositories, branches, and deployment environments.

Example `config.json` format:
```json
{
    "RepositoriesDetail": [
        {
            "Access_Token": "your_access_token",
            "Repository_Owner": "repository_owner",
            "Repository_Name": "repository_name",
            "CICD": [
                {
                    "Target_Branch": "dev",
                    "Deployment_On": "qa"
                },
                {
                    "Target_Branch": "preprod",
                    "Deployment_On": "uat"
                },
                {
                    "Target_Branch": "main",
                    "Deployment_On": "prod"
                }
            ]
        }
    ]
}
```

The `deploymentconfig,json` file contains the deployment configuration for your CICD process. It specifies the Git repositories, branches, deployment environments, project location, folder, url and main file of your project.

Example `deploymentconfig.json` format for Html & Python:
```json
{
        "Nginx_Config_File_Location": "/etc/nginx/sites-available",
        "Nginx_Config_File": "default",
        "DeploymentDetails": [
            {
                "Repository_Name": "repository_name",
                "Deploy": [
                    {
                        "Env": "prod",
                        "Target_Branch": "main",
                        "Location": "/var/www/prod",
                        "FolderName": "hello",
                        "Url": "prod-api-hello.com",
                        "MainFile": "hello.py"
                    }
                ]
            }
        ]
    }

```

```json
{
        "Nginx_Config_File_Location": "/etc/nginx/sites-available",
        "Nginx_Config_File": "default",
        "DeploymentDetails": [
            {
                "Repository_Name": "repository_name",
                "Deploy": [
                    {
                        "Env": "prod",
                        "Target_Branch": "main",
                        "Location": "/var/www/prod",
                        "FolderName": "hello",
                        "Url": "prod-hello.com",
                        "MainFile": "index.html"
                    }
                ]
            }
        ]
    }

```

Customize the configuration according to your project's needs.

## Logging
- The script logs its activities to a log file, which is stored in the logs directory. 
  You can review the log file to track the script's execution and troubleshoot any issues.

## License
- This project is licensed under the MIT License.


