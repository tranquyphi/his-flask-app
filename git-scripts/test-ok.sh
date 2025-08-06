#!/bin/bash
# Git batch script for when test code is OK and ready to merge

echo "🎉 Test code is OK - Preparing to merge and cleanup..."

# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Ensure we're not on main branch
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "❌ Error: You're on main branch. Switch to a feature branch first."
    exit 1
fi

echo "📋 Current branch: $CURRENT_BRANCH"

# Stage and commit any final changes
echo "📝 Staging and committing final changes..."
git add .
git commit -m "Final changes - tests passing on $CURRENT_BRANCH" || echo "No changes to commit"

# Push current branch to remote
echo "🚀 Pushing $CURRENT_BRANCH to remote..."
git push origin "$CURRENT_BRANCH"

# Switch to main branch
echo "🔄 Switching to main branch..."
git checkout main

# Pull latest changes from remote main
echo "⬇️ Pulling latest changes from remote main..."
git pull origin main

# Merge the feature branch
echo "🔀 Merging $CURRENT_BRANCH into main..."
git merge "$CURRENT_BRANCH" --no-ff -m "Merge $CURRENT_BRANCH - tests passing"

# Push merged changes to remote main
echo "⬆️ Pushing merged changes to remote main..."
git push origin main

# Delete the feature branch locally
echo "🗑️ Cleaning up - deleting local branch $CURRENT_BRANCH..."
git branch -d "$CURRENT_BRANCH"

# Delete the feature branch on remote
echo "🗑️ Cleaning up - deleting remote branch $CURRENT_BRANCH..."
git push origin --delete "$CURRENT_BRANCH"

echo "✅ Success! Feature merged and branches cleaned up."
echo "📊 Current status:"
git log --oneline -5
