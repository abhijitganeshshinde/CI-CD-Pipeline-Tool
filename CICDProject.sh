#!/bin/bash

# Constants and Configurations
DEFAULT_ENV="cicd"
DEFAULT_LOCATION="/var/www/cicd"
DEFAULT_HTML_FOLDER="default_html_cicd"
DEFAULT_FLASK_FOLDER="default_flaskapp_cicd"
DEFAULT_HTML_URL="html-cicd.local"
DEFAULT_FLASK_URL="flaskapp-cicd.local"
DEFAULT_HTML_MAIN_FILE="index.html"
DEFAULT_PYTHON_MAIN_FILE="app.py"
DEFAULT_APP_NAME="app"
CRON_EXPRESSION="*/1 * * * *"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
CURRENT_USER="$SUDO_USER"
DEFAULT_IP="127.0.0.1"
DEFAULT_HOSTIP="0.0.0.0"
DEFAULT_PORT=5678

# Function to install packages
install_package() {
    package_name=$1
    if ! command -v "$package_name" &>/dev/null; then
        echo "Installing $package_name..."
        sudo apt update
        sudo apt install "$package_name" -y
        echo "$package_name has been installed."
    else
        echo "$package_name is already installed."
    fi
}

# Function to set permissions
set_permissions() {
    path=$1
    sudo chmod 755 "$path"
}

# Install required packages
install_packages() {
    required_packages=(
        "nginx"
        "git"
        "python3"
        "pip3"
        "python3-config"
    )
    
    for package in "${required_packages[@]}"; do
        install_package "$package"
    done
}

# Function to install required Python packages
install_required_python_packages() {
    required_packages=(
        "requests"
        "logging"
        "json"
        "os"
        "tarfile"
        "shutil"
        "re"
        "datetime"
        "zipfile"
        "socket"
        "subprocess"
        "cryptography"
    )

    missing_packages=()

    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &>/dev/null; then
            missing_packages+=("$package")
        fi
    done

    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "The following Python packages are missing and will be installed: ${missing_packages[*]}"
        pip install "${missing_packages[@]}"
        echo "Packages installed successfully."
    else
        echo "All required packages are already installed."
    fi
}

# Function to clone/update repository
clone_or_update_repo() {
    repo_url=$1
    destination_folder=$2
    
    if [ ! -d "$destination_folder" ]; then
        echo "Cloning repository..."
        sudo git clone -b dev "$repo_url" "$destination_folder"
        echo "Repository cloned."
    else
        echo "Repository folder already exists. Updating..."
        pushd "$destination_folder" > /dev/null
        sudo git pull
        popd > /dev/null
        echo "Repository updated."
    fi

    # Encrypt and save the password
    echo $password
    #encrypted_data=$(echo -n "$password" | openssl enc -aes-256-cbc -pbkdf2 -e -a -k cicd)
    echo "$password" > "$destination_folder/files/encrypted_file/encrypted_data.txt"
    echo "Encrypted data stored in $destination_folder/files/encrypted_file/encrypted_data.txt"
}

# Function to create HTML content
create_html_content() {
    local message="CICD Project Is Running"
    cat <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>Message</title>
</head>
<body>
    <div style="text-align: center; padding-top: 100px;">
        <h1>$message</h1>
    </div>
</body>
</html>
EOF
}

# Function to create Flask app
create_flask_app() {
    local message="CICD Project Is Running"
    cat <<EOF
from flask import Flask

app = Flask(__name__)

@app.route('/')
def message():
    return "$message"

if __name__ == '__main__':
    app.run(debug=False,post=$DEFAULT_PORT)
EOF
}

# Function to save content to a file
save_content_to_file() {
    local content="$1"
    local file_path="$2"
    echo "$content" > "$file_path"
}


# Function to create nginx configuration
create_nginx_config() {
    local server_name="$1"
    local root_path="$2"
    local index_file="$3"

    cat <<EOF
server {
    listen 80;
    listen [::]:80;

    server_name $server_name;

    root $root_path;
    index $index_file;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF
}

# Function to create nginx configuration for Flask
create_flask_nginx_config() {
    local server_name="$1"
    local proxy_pass_url="$2"

    cat <<EOF
server {
    listen 80;
    listen [::]:80;

    server_name $server_name;

    location / {
        include proxy_params;
        proxy_pass $proxy_pass_url;
    }
}
EOF
}

# Function to generate Gunicorn service content
generate_gunicorn_service_content() {
    local app_name="${1:-$DEFAULT_APP_NAME}"
    local env="${2:-$DEFAULT_ENV}"
    local project_path="${3:-$DEFAULT_LOCATION/$DEFAULT_FLASK_FOLDER}"

    cat <<EOF
[Unit]
Description=Gunicorn instance to serve your Flask $app_name
After=network.target

[Service]
User=$CURRENT_USER
Group=www-data
WorkingDirectory=$project_path
Environment="PATH=$project_path/${env}_${app_name}_venv/bin"
ExecStart=$project_path/${env}_${app_name}_venv/bin/gunicorn -w 4 -b {$DEFAULT_HOSTIP}:{$DEFAULT_PORT} $app_name:app

[Install]
WantedBy=multi-user.target
EOF
}

# Function to add nginx configuration
add_nginx_config() {
    local service_name="$1"
    local nginx_config="$2"
    local nginx_config_file_path="$NGINX_SITES_AVAILABLE/$service_name"
    local tmp_nginx_config_file_path="/tmp/$service_name.conf"

    echo "$nginx_config" > "$tmp_nginx_config_file_path"
    sudo mv "$tmp_nginx_config_file_path" "$nginx_config_file_path"
    sudo ln -sf "$nginx_config_file_path" "$NGINX_SITES_ENABLED"
    sudo nginx -t && sudo systemctl restart nginx
}

# Function to deploy a Flask app
function deploy_flask_app() {
    local app_name="${1:-$DEFAULT_APP_NAME}"
    local env="${2:-$DEFAULT_ENV}"
    local project_path="${3:-$DEFAULT_LOCATION/$DEFAULT_FLASK_FOLDER}"
    
    cd "$project_path" || { echo "Could not change directory to $project_path"; exit 1; }
    
     # Create and activate the virtual environment
    python3 -m venv "${env}_${app_name}_venv"
    source "${env}_${app_name}_venv/bin/activate"
    
    # Install required packages including gunicorn
    pip install -r "$project_path/requirements.txt" wheel flask gunicorn
    
    # Deactivate the virtual environment
    deactivate
    
    # Generate and save the WSGI code
    echo "from $app_name import app" > "$project_path/wsgi.py"
    echo "" >> "$project_path/wsgi.py"
    echo "if __name__ == '__main__':" >> "$project_path/wsgi.py"
    echo "    app.run(post=$DEFAULT_PORT)" >> "$project_path/wsgi.py"
    
    # Add Gunicorn service content and start it using the add_gunicorn_service function
    add_gunicorn_service "$env" "$app_name" "$project_path"
    
    echo "Flask app '$app_name' deployment completed successfully."
}

# Function to add Gunicorn service
add_gunicorn_service() {
    local env="${1:-$DEFAULT_ENV}"
    local app_name="${2:-$DEFAULT_APP_NAME}"
    local project_path="${3:-$DEFAULT_LOCATION/$DEFAULT_FLASK_FOLDER}"
    local service_file_path="/etc/systemd/system/${env}_${app_name}.service"

    # Generate Gunicorn service content using the function
    gunicorn_service_content=$(generate_gunicorn_service_content "$app_name" "$env" "$project_path")

    # Save the Gunicorn service content to a file
    echo "$gunicorn_service_content" | sudo tee "$service_file_path" > /dev/null

    sudo systemctl daemon-reload
    sudo systemctl start "${env}_${app_name}"
    sudo systemctl enable "${env}_${app_name}"

    echo "Gunicorn service for '$app_name' added and started."
}

# Function to create deployment configuration JSON
create_deployment_config() {
    local access_token="$1"
    local repo_owner="$2"
    local repo_name="$3"
    local target_branch="$4"
    local deployment_on="$5"
    
    cat <<EOF
{
    "RepositoriesDetail": [
        {
            "Access_Token": "$access_token",
            "Repository_Owner": "$repo_owner",
            "Repository_Name": "$repo_name",
            "CICD": [
                {
                    "Target_Branch": "$target_branch",
                    "Deployment_On": "$deployment_on"
                }
            ]
        }
    ]
}
EOF
}

# Function to add cron job
add_cron_job() {
    local bash_script_path="$destination_folder/bash_script/run_pythonprogram.sh"
    
    if crontab -l | grep -q "$bash_script_path"; then
        echo "Cron job already exists."
    else
        (crontab -l ; echo "$CRON_EXPRESSION  $bash_script_path") | crontab -
        echo "Cron job added successfully."
    fi
}

# Function to create deployment JSON
create_deployment_json() {
    local env="${1:-$DEFAULT_ENV}"
    local location="${2:-$DEFAULT_LOCATION}"
    local folder_name="${3:-$DEFAULT_FOLDER}"
    local url="${4:-$DEFAULT_URL}"
    local main_file="${5:-$DEFAULT_HTML_MAIN_FILE}"
    
    cat <<EOF
{
    "Nginx_Config_File_Location": "/etc/nginx/sites-available",
    "Nginx_Config_File": "default",
    "DeploymentDetails": [
        {
            "Repository_Name": "$repo_name",
            "Deploy": [
                {
                    "Env": "$env",
                    "Target_Branch": "$target_branch",
                    "Location": "$location",
                    "FolderName": "$folder_name",
                    "Url": "$url",
                    "MainFile": "$main_file"
                }
            ]
        }
    ]
}
EOF
}

# Function to collect deployment configuration
collect_deployment_config() {
    echo "Select deployment configuration:"
    echo "1. Default"
    echo "2. Custom"
    read deployment_choice

    local env
    local location
    local folder_name
    local url
    local main_file

    if [ "$deployment_choice" == "2" ]; then
        read -p "Enter Environment (qa/uat/prod): " env
        read -p "Enter Location (/var/www/): " location
        read -p "Enter Folder Name: " folder_name
        read -p "Enter URL: " url

        echo "Select project type:"
        echo "1. HTML"
        echo "2. Python"
        read project_type

        if [ "$project_type" == "1" ]; then
            main_file="$DEFAULT_HTML_MAIN_FILE"
        elif [ "$project_type" == "2" ]; then
            main_file="$DEFAULT_PYTHON_MAIN_FILE"
        else
            echo "Invalid project type. Using default HTML."
            main_file="$DEFAULT_HTML_MAIN_FILE"
        fi
    else
        env="$DEFAULT_ENV"
        location="$DEFAULT_LOCATION"
        folder_name="$DEFAULT_FOLDER"
        url="$DEFAULT_URL"
        main_file="$DEFAULT_HTML_MAIN_FILE"
    fi
    


    project_dir="/home/$CURRENT_USER"
    project_folder_name="CICD-Project"
    destination_folder="$project_dir/$project_folder_name"
    #deploymentcofig_file="$destination_folder/deploymentconfig.json"
    # create_deployment_json "$env" "$location" "$folder_name" "$url" "$main_file" > "$deploymentcofig_file"
    deployment_config=$(create_deployment_json "$env" "$location" "$folder_name" "$url" "$main_file")
    deploymentcofig_file="$destination_folder/files/configuration_files/deploymentconfig.json"
    echo "$deployment_config" > "$deploymentcofig_file"
    echo "Deployment configuration applied."
}

# Function to add entry to hosts file
add_hosts_entry() {
    local domain="$1"
    local ip_address="$2"
    
    # Check if the entry already exists in the hosts file
    if grep -q "$domain" /etc/hosts; then
        echo "Hosts entry for $domain already exists."
    else
        # Add the entry to the hosts file
        sudo bash -c "echo '$ip_address    $domain' >> /etc/hosts"
        echo "Added hosts entry for $domain."
    fi
}

# Main Script
main() {

    # Check for root privileges
    if [ "$EUID" -ne 0 ]; then
        echo "This script must be run as root."
        exit 1
    fi

    # Check for Internet connection
    url="http://www.google.com"
    if ! wget -q --spider "$url"; then
        echo "Internet connection is not active."
        echo "Please connect to the Internet connection."
        exit 1
    fi

    echo "Welcome to the CICD Project Setup Script"
    echo "---------------------------------------"
    echo "   Devlop By Abhijit"
    echo "---------------------------------------"
    
    read -s -p "Enter the $CURRENT_USER password: " password

    # Install required packages
    install_packages
    install_required_python_packages

    project_dir="/home/$CURRENT_USER"
    project_folder_name="CICD-Project"
    destination_folder="$project_dir/$project_folder_name"
    repository_url="https://github.com/abhijitganeshshinde/CI-CD-Pipeline-Tool.git"

    clone_or_update_repo "$repository_url" "$destination_folder"

    # Set permissions
    set_permissions "/var/www"
    set_permissions "$project_dir"
    set_permissions "$destination_folder"


    # Create and save HTML content
    html_content=$(create_html_content)
    html_folder_path="$DEFAULT_LOCATION/$DEFAULT_HTML_FOLDER"
    save_html_location="$html_folder_path/$DEFAULT_HTML_MAIN_FILE"
    
    # Check if the directory exists, if not, create it
    if [ ! -d "$html_folder_path" ]; then
        sudo mkdir -p "$html_folder_path"
        echo "Created directory: $html_folder_path"
    fi
    
    save_content_to_file "$html_content" "$save_html_location"
    add_hosts_entry "$DEFAULT_HTML_URL" "$DEFAULT_IP"

    # Create and save Flask app
    flask_app=$(create_flask_app)
    flask_folder_path="$DEFAULT_LOCATION/$DEFAULT_FLASK_FOLDER"
    save_flask_app_location="$flask_folder_path/$DEFAULT_PYTHON_MAIN_FILE"
    
    # Check if the directory exists, if not, create it
    if [ ! -d "$flask_folder_path" ]; then
        sudo mkdir -p "$flask_folder_path"
        echo "Created directory: $flask_folder_path"
    fi
    
    save_content_to_file "$flask_app" "$save_flask_app_location"

    add_hosts_entry "$DEFAULT_FLASK_URL" "$DEFAULT_IP"
    
    # Create requirements.txt
    requirements_file="$flask_folder_path/requirements.txt"
    if [ ! -f "$requirements_file" ]; then
        save_content_to_file "flask" "$requirements_file"
        echo "Created requirements file: $requirements_file"
    fi

    # Nginx configuration block
    nginx_config=$(create_nginx_config "$DEFAULT_HTML_URL" "$DEFAULT_LOCATION/$DEFAULT_HTML_FOLDER" "$DEFAULT_HTML_MAIN_FILE")

    # Usage
    add_nginx_config "$DEFAULT_HTML_FOLDER" "$nginx_config"

    # Flask Nginx configuration block
    flask_nginx_config=$(create_flask_nginx_config "$DEFAULT_FLASK_URL" "http://0.0.0.0:5678")

    
    # Usage
    deploy_flask_app "$DEFAULT_APP_NAME" "$DEFAULT_ENV" "$DEFAULT_LOCATION/$DEFAULT_FLASK_FOLDER"
    add_nginx_config "$DEFAULT_FLASK_FOLDER" "$flask_nginx_config"

    # Collect deployment configuration
    read -p "Enter Access Token: " access_token
    read -p "Enter Repository Owner: " repo_owner
    read -p "Enter Repository Name: " repo_name
    read -p "Enter Target Branch: " target_branch
    read -p "Enter Deployment On (qa/uat/prod): " deployment_on

    # Create deployment configuration JSON
    config=$(create_deployment_config "$access_token" "$repo_owner" "$repo_name" "$target_branch" "$deployment_on")
    cofig_file="$destination_folder/files/configuration_files/config.json"
    echo "$config" > "$cofig_file"
    # deployment_config=$(create_deployment_config "$access_token" "$repo_owner" "$repo_name" "$target_branch" "$deployment_on")
    # deploymentcofig_file="$destination_folder/deploymentcofig.json"
    # echo "$deployment_config" > "$deploymentcofig_file"

    # Create configuration JSON
    collect_deployment_config
    
    # Add cron job
    add_cron_job

    # Restart services
    sudo systemctl restart nginx
    sudo systemctl restart cron
    echo "Nginx and cron service restarted."
    echo "Setup completed."
}

# Run the main function
main
