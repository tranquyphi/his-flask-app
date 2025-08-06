#!/bin/bash
# Git batch script for when test code is NOT OK and needs more work

echo "🔧 Test code needs work - Saving progress and planning next steps..."

# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Ensure we're not on main branch
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "❌ Error: You're on main branch. Switch to a feature branch first."
    exit 1
fi

echo "📋 Current branch: $CURRENT_BRANCH"

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
