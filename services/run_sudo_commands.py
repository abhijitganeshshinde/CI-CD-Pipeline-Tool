import subprocess

def sudo_daemon_reload():
    """Calls the sudo_daemon-reload alias."""

    args = ["sudo", "sudo_daemon-reload"]
    process = subprocess.Popen(args)
    process.wait()

if __name__ == "__main__":
    try:
        sudo_daemon_reload()
        print("sudo_daemon-reload exited successfully")
    except subprocess.CalledProcessError as e:
        print(f"sudo_daemon-reload exited with error: {e.output}")
