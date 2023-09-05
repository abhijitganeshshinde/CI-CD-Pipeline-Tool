# CI-CD-Pipeline-Tool

## Setup Script

This Bash script automates the setup process for a Continuous Integration/Continuous Deployment (CICD) project. It installs required packages, configures Nginx, sets up Flask and HTML web applications.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running this script, ensure you have:

- An active Internet connection.
- The necessary permissions to run as root.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/abhijitganeshshinde/CI-CD-Pipeline-Tool.git
   cd CICD-Project
  
2. Run the setup script with sudo:
  
    ```bash
    chmode +x SetupCICDProject.sh
    sudo ./SetupCICDProject.sh

3. Follow the prompts to provide the required information and passwords

## Configuration

### The script automates several configuration steps:
- Installs required packages like Nginx, Git, Python3, pip3, etc.
- Creates and configures HTML and Flask applications.
- Sets up Nginx configurations for both applications.
- Collects deployment configuration details.

## Adding New Configuration
- You can customize the deployment by providing specific configurations in the  `config.json ` and  `deploymentconfig.json ` files.

## Usage
- Run the setup script as described in the Installation section.
- Follow the prompts to provide the necessary information.
- The script will configure Nginx, set up Flask and HTML applications, and deploy them.

## Contributing
 If you want to contribute to this project, please follow these guidelines:

- Fork the repository.
- Create a new branch for your feature or bugfix: git checkout -b feature/your-feature or git checkout -b bugfix/your-bugfix.
-  Make your changes.
- Push to your fork and submit a pull request.

## License
- This project is licensed under the MIT License. See the LICENSE file for details.
