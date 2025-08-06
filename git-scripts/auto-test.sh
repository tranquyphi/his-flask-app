#!/bin/bash
# Git batch script - Auto-creates test branch and handles OK/NOT OK scenarios

echo "🧪 Git Test Workflow - Auto Branch Management"

# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# If on main, auto-create a test branch
if [ "$CURRENT_BRANCH" = "main" ]; then
    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --staged --quiet; then
        echo "📍 On main with changes - creating test branch..."
        TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
        TEST_BRANCH="test/auto-$TIMESTAMP"
        git checkout -b "$TEST_BRANCH"
        echo "🌟 Created and switched to: $TEST_BRANCH"
    else
        echo "📍 On main with no changes - creating clean test branch..."
        echo "Enter test description (or press Enter for timestamp):"
        read -r test_desc
        
        if [ -z "$test_desc" ]; then
            TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
            TEST_BRANCH="test/auto-$TIMESTAMP"
        else
            # Clean the description for branch name
            clean_desc=$(echo "$test_desc" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
            TEST_BRANCH="test/$clean_desc"
        fi
        
        git checkout -b "$TEST_BRANCH"
        echo "🌟 Created and switched to: $TEST_BRANCH"
    fi
    CURRENT_BRANCH="$TEST_BRANCH"
fi

echo "📋 Current branch: $CURRENT_BRANCH"

# Stage any changes
if ! git diff --quiet || ! git diff --staged --quiet; then
    echo "📝 Staging changes..."
    git add .
fi

echo ""
echo "🧪 Test your code now!"
echo ""
echo "When done testing, choose what to do:"
echo "  1) Tests PASSED - merge to main and cleanup"
echo "  2) Tests FAILED - save progress and continue working"
echo "  3) Cancel - stay on current branch"
echo ""
echo -n "Enter choice (1/2/3): "
read -r choice

case $choice in
    1)
        echo "✅ Running test-ok workflow..."
        # Commit if there are staged changes
        if ! git diff --staged --quiet; then
            git commit -m "Tests passing - ready for merge from $CURRENT_BRANCH"
        fi
        # Run the test-ok script logic
        ./git-scripts/test-ok.sh
        ;;
    2)
        echo "🔧 Running test-not-ok workflow..."
        # Commit work in progress
        if ! git diff --staged --quiet; then
            git commit -m "WIP: Tests not passing yet on $CURRENT_BRANCH"
        fi
        # Run the test-not-ok script logic
        ./git-scripts/test-not-ok.sh
        ;;
    3)
        echo "⏸️  Staying on $CURRENT_BRANCH - no changes made"
        echo "💡 Your changes are staged. Commit when ready:"
        echo "   git commit -m 'Your commit message'"
        ;;
    *)
        echo "❌ Invalid choice. Staying on $CURRENT_BRANCH"
        ;;
esac
