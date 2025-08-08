#!/bin/bash

# Go to your project directory (optional but recommended)
# cd /path/to/your/project

# Ensure you’re on the main branch
git checkout main

# Pull latest changes (optional)
git pull origin main

# Restart the service
sudo systemctl restart his.service

# Confirm it restarted
sudo systemctl status his.service
