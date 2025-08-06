#!/bin/bash
# Git batch script for when test code is NOT OK and needs more work

echo "🔧 Test code needs work - Saving progress and planning next steps..."

# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Handle if we're on main branch
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "📍 Currently on main branch - need to work on a feature branch..."
    
    # Check if there are uncommitted changes
    if ! git diff --quiet || ! git diff --staged --quiet; then
        echo "⚠️  You have uncommitted changes on main branch!"
        echo "🔧 Creating a new feature branch to save your work..."
        
        # Generate a branch name with timestamp
        TIMESTAMP=$(date +"%Y%m%d-%H%M")
        NEW_BRANCH="feature/work-in-progress-$TIMESTAMP"
        
        echo "🌟 Creating new branch: $NEW_BRANCH"
        git checkout -b "$NEW_BRANCH"
        CURRENT_BRANCH="$NEW_BRANCH"
    else
        # No changes, suggest creating a new branch or switching to existing
        echo "📍 No uncommitted changes found."
        
        # Get list of recent branches (excluding main)
        RECENT_BRANCHES=$(git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short)' | grep -v '^main$' | head -5)
        
        if [ -n "$RECENT_BRANCHES" ]; then
            echo "🔍 Recent feature branches:"
            echo "$RECENT_BRANCHES" | nl -w2 -s') '
            echo ""
            echo "Choose an option:"
            echo "Enter branch number (1-5), 'n' for new branch, or 'c' to cancel:"
            read -r choice
            
            if [ "$choice" = "c" ]; then
                echo "💡 Cancelled. Create a branch when ready: git checkout -b feature/your-feature-name"
                exit 0
            elif [ "$choice" = "n" ]; then
                echo "Enter new branch name (without 'feature/' prefix):"
                read -r branch_name
                NEW_BRANCH="feature/$branch_name"
                echo "🌟 Creating new branch: $NEW_BRANCH"
                git checkout -b "$NEW_BRANCH"
                CURRENT_BRANCH="$NEW_BRANCH"
            else
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
        else
            echo "💡 No feature branches found. Create a new one:"
            echo "Enter branch name (without 'feature/' prefix):"
            read -r branch_name
            NEW_BRANCH="feature/$branch_name"
            echo "🌟 Creating new branch: $NEW_BRANCH"
            git checkout -b "$NEW_BRANCH"
            CURRENT_BRANCH="$NEW_BRANCH"
        fi
    fi
fi

echo "📋 Working with branch: $CURRENT_BRANCH"

# Stage and commit current work in progress
echo "💾 Saving work in progress..."
git add .
git status

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "📭 No changes to commit"
else
    echo "📝 Committing work in progress..."
    git commit -m "WIP: In progress - tests not passing yet on $CURRENT_BRANCH"
fi

# Push current branch to remote for backup
echo "🚀 Pushing $CURRENT_BRANCH to remote for backup..."
git push origin "$CURRENT_BRANCH"

# Show current status
echo "📊 Current status:"
echo "   - Branch: $CURRENT_BRANCH"
echo "   - Last 3 commits:"
git log --oneline -3

echo ""
echo "🎯 Next steps:"
echo "   1. Fix the failing tests"
echo "   2. Run: git add . && git commit -m 'Fix: description of what was fixed'"
echo "   3. Test again"
echo "   4. When tests pass, run: ./git-scripts/test-ok.sh"
echo ""
echo "🔄 Alternative options:"
echo "   - Reset to last working commit: git reset --hard HEAD~1"
echo "   - Create new branch for different approach: git checkout -b ${CURRENT_BRANCH}-v2"
echo "   - Switch to main and start over: git checkout main && git checkout -b new-feature-name"
echo ""
echo "💡 Your work is safely backed up on remote: origin/$CURRENT_BRANCH"
