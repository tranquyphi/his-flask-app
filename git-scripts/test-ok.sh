#!/bin/bash
# Git batch script for when test code is OK and ready to merge

echo "🎉 Test code is OK - Preparing to merge and cleanup..."

# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Handle if we're on main branch
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "📍 Currently on main branch - looking for recent feature branch..."
    
    # Get list of recent branches (excluding main)
    RECENT_BRANCHES=$(git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short)' | grep -v '^main$' | head -5)
    
    if [ -z "$RECENT_BRANCHES" ]; then
        echo "❌ No feature branches found. Please create a feature branch first:"
        echo "   git checkout -b feature/your-feature-name"
        exit 1
    fi
    
    echo "🔍 Recent feature branches:"
    echo "$RECENT_BRANCHES" | nl -w2 -s') '
    echo ""
    echo "Please choose a branch to test and merge:"
    echo "Enter the number (1-5), or 'c' to cancel and create new branch:"
    read -r choice
    
    if [ "$choice" = "c" ]; then
        echo "💡 Create a new branch with: git checkout -b feature/your-feature-name"
        exit 0
    fi
    
    # Get the selected branch
    SELECTED_BRANCH=$(echo "$RECENT_BRANCHES" | sed -n "${choice}p")
    
    if [ -z "$SELECTED_BRANCH" ]; then
        echo "❌ Invalid selection. Exiting."
        exit 1
    fi
    
    echo "� Switching to branch: $SELECTED_BRANCH"
    git checkout "$SELECTED_BRANCH"
    CURRENT_BRANCH="$SELECTED_BRANCH"
fi

echo "📋 Working with branch: $CURRENT_BRANCH"

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
