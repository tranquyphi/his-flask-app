#!/bin/bash

# Get current branch name
current_branch=$(git branch --show-current)

# Get current timestamp
current_time=$(date '+%Y-%m-%d %H:%M:%S')

# Create commit message
commit_message="${current_branch} - ${current_time}"

# Execute git commands
git add .
git commit -m "$commit_message"
git push

echo "Committed and pushed with message: $commit_message"
