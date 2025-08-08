#!/bin/bash

# Go to your project directory (optional but recommended)
# cd /path/to/your/project

# Ensure you’re on the main branch
git checkout 1-DepartmentPatient

# Pull latest changes (optional)
git pull origin 1-DepartmentPatient

# Restart the service
sudo systemctl restart his.service

# Confirm it restarted
sudo systemctl status his.service
