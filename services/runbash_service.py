import subprocess
import logging

def execute_bash_script(script_path):
    result =False
    try:
        subprocess.run(["bash", script_path], check=True)
        result = True
        print("Bash script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error("Error executing Bash script:", e)
        print("Error executing Bash script:", e)
        result =False
    return result

def check_install_nginx():
    try:
        
        result = subprocess.run(['nginx', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            print("Nginx is already installed.")
            return True
        else:
            print("Nginx is not installed.")
            return False
    except Exception as e:
        logging.error("An error occurred while checking Nginx installation: {e}")
        print(f"An error occurred while checking Nginx installation: {e}")
        return False

def install_nginx():
    try:

        subprocess.run(['apt-get', 'update'])
        subprocess.run(['apt-get', 'install', 'nginx'])
        print("Nginx installation complete.")
        return True
    except Exception as e:
        logging.error("An error occurred while installing Nginx: {e}")
        print(f"An error occurred while installing Nginx: {e}")
        return False

def restart_nginx(password):
    try:
        run_command(password,"systemctl restart nginx")
        print("Nginx restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error restarting Nginx: {e}")

def run_command(password,command):
    #password = "abhiroot"
    full_command = f"echo {password} | sudo -S {command}"
    result = subprocess.run(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr.decode('utf-8')}")
    else:
        print(result.stdout.decode('utf-8'))

def restart_all_service(password,service_name):
    run_command(password,"systemctl daemon-reload")
    run_command(password,f"systemctl start {service_name}")
    run_command(password,f"systemctl enable {service_name}")
    restart_nginx(password)