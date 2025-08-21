#!/bin/bash

# Get current branch name
current_branch=$(git branch --show-current)

# Get current timestamp in GMT+7
current_time=$(TZ='Asia/Bangkok' date '+%Y-%m-%d %H:%M:%S')

# Create commit message
commit_message="${current_branch} - ${current_time}"

# Execute git commands
git add .
git commit -m "$commit_message"
git push

echo "Committed and pushed with message: $commit_message"
