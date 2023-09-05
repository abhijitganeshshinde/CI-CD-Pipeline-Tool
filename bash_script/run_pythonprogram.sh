#!/bin/bash

CURRENT_USER="$SUDO_USER"
project_dir="/home/$CURRENT_USER"
project_folder_name="CICD-Project"
destination_folder="$project_dir/$project_folder_name"
cd $destination_folder

# Run the Python program
python3 checknewcommit.py
