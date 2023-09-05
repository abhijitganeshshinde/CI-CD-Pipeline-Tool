import os
import tarfile
import json
import logging
import shutil
import re
import datetime
import zipfile
import socket
import services.runbash_service as runbash_service

def read_jsonfile(filepath):
    result = False
    data = None
    try:
        with open(filepath, "r") as json_file:
            data = json.load(json_file)
            result = True
            print("JSON data has been read successfully:")
            print(data)
    except FileNotFoundError as e:
        logging.error(f"{filepath} not found.\n Error:{e}")
        print(f"{filepath} not found.")
        result = False
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in {filepath}.\n Error:{e}")
        print(f"Error decoding JSON in {filepath}.")
        result = False

    return result,data

def create_lastcommitfile(filepath):
    result = False
    data = None
    try:
        data = {
            "Repositories": []
        }
        with open(filepath, "w") as json_file:
            json.dump(data, json_file, indent=4)
            print(f"Data has been written to {filepath}")
        result = True
        
    except Exception as e:
        logging.error(f"An error occurred while creating lastcommit file: {e}")
        print(f"An error occurred while creating lastcommit file: {e}")
        
    return result, data
    
def add_repository(data, repo_name):
    result = False
    try:
        if any(repo["Repository_Name"] == repo_name for repo in data["Repositories"]):
            print(f"Repository '{repo_name}' already exists.")
        else:
            repository = {
                "Repository_Name": repo_name,
                "Branches": []
            }
            data["Repositories"].append(repository)
            print(f"Repository '{repo_name}' added.")
            result = True
           
    except KeyError:
        logging.error(f"An error occurred while adding repository : Invalid data structure. 'Repositories' key not found.")
        print("Invalid data structure. 'Repositories' key not found.")
    except Exception as e:
        logging.error(f"An error occurred while adding repository: {e}")
        print(f"An error occurred while adding repository: {e}")
    
    return result

def add_branch(data, repo_name, branch_name, commit_id):
    result = False
    try:
        repository = next((repo for repo in data["Repositories"] if repo["Repository_Name"] == repo_name), None)
        if repository is None:
            result = False
            print(f"Repository '{repo_name}' not found.")
        elif any(branch["Branch_Name"] == branch_name for branch in repository["Branches"]):
            result = False
            print(f"Branch '{branch_name}' already exists for repository '{repo_name}'.")
        else:
            branch = {
                "Branch_Name": branch_name,
                "Commit_SHA": commit_id
            }
            repository["Branches"].append(branch)
            print(f"Branch '{branch_name}' added to repository '{repo_name}'")
            result = True
    except KeyError:
        logging.error("An error occurred while adding branch: Invalid data structure. 'Repositories' or 'Branches' key not found.")
        print("An error occurred while adding branch: Invalid data structure. 'Repositories' or 'Branches' key not found.")
    except Exception as e:
        logging.error(f"An error occurred while adding branch: {e}")
        print(f"An error occurred while adding branch: {e}")
  
    return result


def update_file(file_path, data):
    try:
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data updated in {file_path}")
        return True
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return False
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file '{file_path}'.")
        print(f"Error decoding JSON from file '{file_path}'.")
        return False
    except Exception as e:
        logging.error(f"An error occurred while updating file: {e}")
        print(f"An error occurred while updating file: {e}")
        return False

def update_commit(data, repo_name, branch_name, new_commit_id):
    try:
        for repository in data["Repositories"]:
            if repository["Repository_Name"] == repo_name:
                for branch in repository["Branches"]:
                    if branch["Branch_Name"] == branch_name:
                        branch["Commit_SHA"] = new_commit_id
                        print(f"Commit updated for branch '{branch_name}' in repository '{repo_name}'")
                        return True
                print(f"Branch '{branch_name}' not found in repository '{repo_name}'")
                return False
        print(f"Repository '{repo_name}' not found.")
        return False
    except KeyError:
        logging.error("An error occurred while updating commit:Invalid data structure. 'Repositories' or 'Branches' key not found.")
        print("An error occurred while updating commit:Invalid data structure. 'Repositories' or 'Branches' key not found.")
        return False
    except Exception as e:
        logging.error(f"An error occurred while updating file: {e}")
        print(f"An error occurred while updating file: {e}")
        return False

def get_commit(data, repo_name, branch_name):
    try:
        for repository in data["Repositories"]:
            if repository["Repository_Name"] == repo_name:
                for branch in repository["Branches"]:
                    if branch["Branch_Name"] == branch_name:
                        return branch["Commit_SHA"]
                print(f"Branch '{branch_name}' not found in repository '{repo_name}'")
                return None
        print(f"Repository '{repo_name}' not found.")
        return None
    except KeyError:
        logging.error(f"An error occurred while getting commit: Invalid data structure. 'Repositories' or 'Branches' key not found.")
        print(f"An error occurred while getting commit: Invalid data structure. 'Repositories' or 'Branches' key not found.")
        return None
    except Exception as e:
        logging.error(f"An error occurred while getting commit: {e}")
        print(f"An error occurred while getting commit: {e}")
        return None

def extract_archive(archive_path, extract_path):
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_path)
        print("Archive extracted successfully.")
        return True
    except tarfile.TarError as e:
        logging.error(f"An error occurred while extracting the archive: {e}")
        print(f"An error occurred while extracting the archive: {e}")
        return False
    except Exception as e:
        logging.error(f"An error occurred while extracting the archive: {e}")
        print(f"An error occurred while extracting the archive: {e}")
        return False

def rename_folder(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        print(f"Folder '{old_name}' renamed to '{new_name}'.")
        return True
    except OSError as e:
        logging.error(f"An error occurred while renaming folder: {e}")
        print("An error occurred while renaming folder: {e}")
        return False

def repository_exists(data, repo_name):
    try:
        for repository in data["Repositories"]:
            if repository["Repository_Name"] == repo_name:
                return True
        return False
    except KeyError:
        logging.error(f"An error occurred while checking repostitory exist or not: Invalid data structure. 'Repositories' key not found.")
        print(f"An error occurred while checking repostitory exist or not: Invalid data structure. 'Repositories' key not found.")
        return False
    except Exception as e:
        logging.error(f"An error occurred while checking repostitory exist or not: {e}")
        print(f"An error occurred while checking repostitory exist or not: {e}")
        return False

def branch_exists(repositories, repo_name,branch_name):
    try:
        for repository in repositories["Repositories"]:
            if repository["Repository_Name"] == repo_name:
                for branch in repository["Branches"]:
                    if branch["Branch_Name"] == branch_name:
                        return True
        return False
    except KeyError:
        logging.error(f"An error occurred while checking branch exist or not: Invalid repository data structure. 'Branches' key not found.")
        print("Invalid repository data structure. 'Branches' key not found.")
        return False
    except Exception as e:
        logging.error(f"An error occurred while checking branch exist or not: {e}")
        print(f"An error occurred: {e}")
        return False

def commit_exists(branch, commit_sha):
    try:
        for commit in branch["Branches"]:
            if commit["Commit_SHA"] == commit_sha:
                return True
        return False
    except KeyError:
        logging.error(f"An error occurred while checking commit exist or not: Invalid branch data structure. 'Branches' key not found.")
        print("Invalid branch data structure. 'Branches' key not found.")
        return False
    except Exception as e:
        logging.error(f"An error occurred while checking commit exist or not: {e}")
        print(f"An error occurred: {e}")
        return False

def get_commit_sha(data, repo_name, branch_name):
    try:
        for repository in data["Repositories"]:
            if repository["Repository_Name"] == repo_name:
                for branch in repository["Branches"]:
                    if branch["Branch_Name"] == branch_name:
                        return branch["Commit_SHA"]
                return None
        return None
    except KeyError:
        logging.error(f"An error occurred while getting commit : Invalid data structure. 'Repositories' or 'Branches' key not found.")
        print("Invalid data structure. 'Repositories' or 'Branches' key not found.")
        return None
    except Exception as e:
        logging.error(f"An error occurred while getting commit : {e}")
        print(f"An error occurred: {e}")
        return None

def backup_and_compress_folder(password,source_folder, backup_parent_folder):
    try:
        # Get the source folder's name
        source_folder_name = os.path.basename(source_folder)
        
        # Create a backup folder using the source folder's name and timestamp
        timestamp = datetime.datetime.now().strftime("Date_%d-%m-%Y_Time_%H-%M-%S")

        runbash_service.run_command(password,f"zip -r {backup_parent_folder}_{timestamp}.zip {source_folder}" )

        # backup_folder_base = os.path.join(backup_parent_folder, f"{source_folder_name}_{timestamp}")
        # backup_folder = backup_folder_base
        # # Copy the source folder to the backup location
        # suffix = 1
        # while os.path.exists(backup_folder):
        #     backup_folder = f"{backup_folder_base}_{suffix}"
        #     suffix += 1
        
        # ##os.makedirs(backup_folder)
        
        # shutil.copytree(source_folder, backup_folder)

        # # Create a compressed archive of the backup folder
        # compressed_filename = os.path.join(backup_parent_folder, f"{source_folder_name}_{timestamp}.zip")
        # with zipfile.ZipFile(compressed_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        #     for root, _, files in os.walk(backup_folder):
        #         for file in files:
        #             file_path = os.path.join(root, file)
        #             arcname = os.path.relpath(file_path, backup_folder)
        #             zipf.write(file_path, arcname)
        #             shutil.rmtree(backup_folder)
        print("Backup and compression completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred while backup and compressfolder: {e}")
        print("An error occurred:", str(e))

def copy_data(password,source_folder, destination_folder):
    try:
        source_folderescaped_path = source_folder.replace(" ", r"\ ")
        destination_folderescaped_path = destination_folder.replace(" ", r"\ ")
        if os.path.exists(destination_folder):
            #shutil.rmtree(destination_folder)
            runbash_service.run_command(password,f"rm -rf {destination_folderescaped_path}" )
        runbash_service.run_command(password,f"cp -r {source_folderescaped_path} {destination_folderescaped_path}" )
        #shutil.copytree(source_folder, destination_folder)
        
        #logging.info("Data copied from %s to %s", source_folder, destination_folder)
        print("Data copied:", destination_folder)
        return True
    except Exception as e:
        logging.error("An error occurred while copying data: %s", e)
        print(f"An error occurred while copying data: {e}")
        return False

def create_folder(password,folder_path):
    try:
        
        if not os.path.exists(folder_path):
            runbash_service.run_command(password,f"mkdir {folder_path}")
            #os.makedirs(folder_path,exist_ok=True)
            print(f"Folder created successfully.")
            return True
        else:
            print(f"Folder already exists.")
            return True
    except OSError as e:
        logging.error(f"An error occurred while creating folder '{folder_path}': {e}")
        print(f"An error occurred while creating folder '{folder_path}': {e}")
        return False


def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            #logging.info("File deleted: %s", file_path)
            print("File deleted:", file_path)
            return True
        else:
            #logging.info("File does not exist: %s", file_path)
            print("File does not exist:", file_path)
            return False
    except Exception as e:
        logging.error("An error occurred while deleting file: %s", e)
        print(f"An error occurred while deleting file: {e}")
        return False

def delete_folder(folder_path):
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            logging.info("Folder deleted: %s", folder_path)
            print("Folder deleted:", folder_path)
            return True
        else:
            logging.info("Folder does not exist: %s", folder_path)
            print("Folder does not exist:", folder_path)
            return False
    except Exception as e:
        logging.error("An error occurred while deleting folder: %s", e)
        print(f"An error occurred while deleting folder: {e}")
        return False

def get_deployment_details(data, repository_name, target_branch):
    try:
        for deployment in data["DeploymentDetails"]:
            if deployment["Repository_Name"] == repository_name:
                for deploy in deployment["Deploy"]:
                    if deploy["Target_Branch"] == target_branch:
                        return True, deploy
        return False, None
    except KeyError as e:
        logging.error("An error occurred while getting deplyment details: %s", e)
        print(f"KeyError: {e} - Check your JSON structure.")
        return False,None


def give_permissions_to_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            current_permissions = os.stat(folder_path).st_mode
            if not current_permissions & 0o777:  # Check if permissions are not already set
                os.chmod(folder_path, 0o777)
                print(f"Permissions set for {folder_path}")
            else:
                print(f"Permissions already set for {folder_path}")
        except OSError as e:
            logging.error("An error occurred while giving permissions to folder: %s", e)
            print(f"Error setting permissions: {e}")
    else:
        print(f"Folder path does not exist at {folder_path}")

def read_nginx_config(nginx_config_path):
    try:
        with open(nginx_config_path, "r") as file:
            nginx_config = file.read()
            return True,nginx_config
    except IOError as e:
        logging.error(f"An error occurred while greading Nginx configuration:  {e}")
        print(f"Error reading Nginx configuration: {e}")
        return False,None

def read_all_server_blocks(nginx_config):
    try:
        # Use regular expression to find all server blocks
        pattern = re.compile(r"server\s*{[^}]*}")
        server_blocks = pattern.findall(nginx_config)
        return True,server_blocks
    except Exception as e:
        logging.error(f"An error occurred while read all server blocks: {e}")
        print(f"Error reading server blocks: {e}")
        return False,[]

def read_server_block_by_name(nginx_config, server_name):
    try:
        # Use regular expression to find the specific server block by name
        pattern = re.compile(r"server\s*{[^}]*server_name\s+" + re.escape(server_name) + r";[^}]*}")
        match = pattern.search(nginx_config)
        if match:
            return True,match.group(0)
        else:
            return False,None
    except Exception as e:
        logging.error(f"An error occurred while read server block by name: {e}")
        print(f"Error reading server block: {e}")
        return False, None

def update_nginx_config(nginx_config_path, updated_config):
    try:
        with open(nginx_config_path, "w") as file:
            file.write(updated_config)
        print("Nginx configuration updated successfully.")
        return True
    except IOError as e:
        logging.error(f"An error occurred while updating Nginx configuration: {e}")
        print(f"Error updating Nginx configuration: {e}")
        return False

def add_server_block(nginx_config, new_server_block):
    try:
        updated_config = nginx_config + "\n" + new_server_block + "\n"
        return True,updated_config
    except Exception as e:
        logging.error(f"An error occurred while add server block: {e}")
        print(f"Error adding server block: {e}")
        return False,None

def is_host_entry_present(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False

def add_host_entry(hostname):
    ip_address = "127.0.0.1"
    hosts_path = "/etc/hosts"
    new_entry = f"{ip_address} {hostname}\n"

    try:
        with open(hosts_path, "a") as hosts_file:
            hosts_file.write(new_entry)
        print(f"Added entry for {hostname}")
        return True
    except Exception as e:
        logging.error(f"An error occurred while adding entry for {hostname}: {e}")
        print(f"Error adding entry for {hostname}: {e}")
        return False

def get_file_name_and_extension(filename):
    try:
        name, extension = os.path.splitext(filename)
        return name,extension[1:]
    except Exception as  e:
        logging.error(f"An error occurred while getting file extension {filename}: {e}")
        return None,None
    
def service_exists(app_name):
    service_file_path = f"/etc/systemd/system/{app_name}.service"
    return os.path.exists(service_file_path)

def nginx_config_exists(app_name):
    config_file_path = f"/etc/nginx/sites-available/{app_name}"
    return os.path.exists(config_file_path)

def deploy_flask_app(password,app_name,env,project_path,current_path):
    try:
        runbash_service.run_command(password,f"systemctl stop {env}_{app_name}")
        venv_dir = os.path.join(project_path, f"{env}_{app_name}_venv")
        if os.path.exists(venv_dir):
            os.system(f"echo {password} | sudo -S rm -r {venv_dir}")
        
        os.chdir(project_path)
        os.system(f"echo {password} | sudo -S python3 -m venv {env}_{app_name}_venv")
        
        #os.system(f"source {env}_{app_name}_venv/bin/activate")
        os.system(f"echo {password} | sudo -S  {env}_{app_name}_venv/bin/pip install -r requirements.txt")
        os.system(f"echo {password} | sudo -S  {env}_{app_name}_venv/bin/pip install wheel")
        os.system(f"echo {password} | sudo -S  {env}_{app_name}_venv/bin/pip install flask gunicorn")
        is_readable,wsgi_code = read_nginx_config(os.path.join(current_path,"files","sample_files","wsgi_code_sample.txt"))
        wsgi_code = wsgi_code.replace("@mainfile",app_name)

        wsgi_file_path = f"{project_path}/wsgi.py"

        tmp_wsgi_file_path = f"/tmp/wsgi.py"

        with open(tmp_wsgi_file_path, "w") as tmp_wsgi_file:
            tmp_wsgi_file.write(wsgi_code)

        os.system(f"echo {password} | sudo -S mv {tmp_wsgi_file_path} {wsgi_file_path}")
        # with open("wsgi.py", "w") as wsgi_file:
        #     wsgi_file.write(wsgi_code)
        
        #os.system("deactivate")
        print("App deployment completed successfully.")
        return True
    except OSError as os_error:
        print("Operating System Error:", os_error)
        return False
    except Exception as e:
        print("An error occurred:", e)
        return False
    
    #os.system(f"{env}_{app_name}_venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 {app_name}:app")


def add_gunicorn_service(password,env,app_name,gunicorn_service):
    try:
        service_file_path = f"/etc/systemd/system/{env}_{app_name}.service"

        tmp_service_file_path = f"/tmp/{env}_{app_name}.service"
        with open(tmp_service_file_path, "w") as tmp_service_file:
            tmp_service_file.write(gunicorn_service)

        os.system(f"echo {password} | sudo -S mv {tmp_service_file_path} {service_file_path}")
        # with open(f"/etc/systemd/system/{app_name}.service", "w") as service_file:
        #     service_file.write(gunicorn_service)
        runbash_service.run_command(password,"systemctl daemon-reload")
        runbash_service.run_command(password,f"systemctl start {env}_{app_name}")
        runbash_service.run_command(password,f"systemctl enable {env}_{app_name}")
        return True  
    except OSError as os_error:
        print("Operating System Error:", os_error)
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False  


def add_nginx_config(password,service_name,app_name,nginx_config):
    try:
        nginx_config_file_path = f"/etc/nginx/sites-available/{service_name}"

        tmp_nginx_config_file_path = f"/tmp/{service_name}.conf"
        with open(tmp_nginx_config_file_path, "w") as tmp_nginx_config_file:
            tmp_nginx_config_file.write(nginx_config)
        
        os.system(f"echo {password} | sudo -S mv {tmp_nginx_config_file_path} {nginx_config_file_path}")

            # Step 9: Create a symbolic link and test configuration
        runbash_service.run_command(password,f"ln -s /etc/nginx/sites-available/{service_name} /etc/nginx/sites-enabled")
        runbash_service.run_command(password,"nginx -t")

            # Step 10: Restart Nginx
        runbash_service.run_command(password,"systemctl restart nginx")
        return True
    except OSError as os_error:
        print("Operating System Error:", os_error)
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False  # An error occurred

def read_text_file(file_path):
    try:
        with open(file_path, "r") as file:
            _text_file = file.read()
            return True,_text_file
    except IOError as e:
        logging.error(f"An error occurred while greading Nginx configuration:  {e}")
        print(f"Error reading Nginx configuration: {e}")
        return False,None