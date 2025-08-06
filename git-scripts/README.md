# Git Batch Scripts

This directory contains batch scripts to automate common Git workflows for the HIS project.

## Scripts

### `auto-test.sh` - Smart Test Workflow (Recommended) 🤖
**The easiest option** - Automatically handles branch creation and guides you through the testing process.

**What it does:**
1. Auto-creates a test branch if you're on main
2. Stages your changes
3. Prompts you to test your code
4. Based on test results, runs appropriate workflow (OK or NOT OK)

**Usage:**
```bash
./git-scripts/auto-test.sh
```

### `test-ok.sh` - When tests pass ✅
Use this when your feature is complete and tests are passing.

**What it does:**
1. If on main, shows recent branches and lets you choose which to merge
2. Commits any final changes
3. Pushes feature branch to remote
4. Switches to main branch
5. Pulls latest changes from remote
6. Merges feature branch into main
7. Pushes merged changes to remote
8. Cleans up by deleting local and remote feature branches

**Usage:**
```bash
./git-scripts/test-ok.sh
```

### `test-not-ok.sh` - When tests fail ❌
Use this when you need to save progress but tests aren't passing yet.

**What it does:**
1. If on main, helps you create or switch to a feature branch
2. Commits work in progress with WIP message
3. Pushes to remote for backup
4. Shows current status and next steps
5. Provides options for different approaches

**Usage:**
```bash
./git-scripts/test-not-ok.sh
```

## Workflow Examples

### Quick Workflow (Recommended)
```bash
# Start from main, make changes, then:
./git-scripts/auto-test.sh
# Script guides you through testing and next steps
```

### Manual Workflow
```bash
# Traditional approach:
git checkout -b feature/new-functionality
# Make your changes...

# If tests pass:
./git-scripts/test-ok.sh

# If tests fail:
./git-scripts/test-not-ok.sh
```

## Smart Features

### Auto Branch Management
- **`auto-test.sh`**: Creates test branches automatically with timestamps or custom names
- **`test-ok.sh`**: Shows recent branches if you're on main, lets you choose which to merge
- **`test-not-ok.sh`**: Helps create or switch to feature branches, handles uncommitted changes

### Safety Features
- All scripts handle uncommitted changes gracefully
- `test-ok.sh` uses `--no-ff` merge to preserve branch history
- `test-not-ok.sh` backs up your work to remote before suggesting next steps
- All scripts provide clear feedback about what they're doing

### Interactive Guidance
- Branch selection menus
- Clear next-step instructions
- Recovery options when things go wrong
- Descriptive commit messages with branch names

## Requirements

- Git repository with remote origin configured
- Proper permissions to push to main branch
- Scripts should be run from repository root (`/root/his/`)

## Tips

1. **Start Simple**: Use `./git-scripts/auto-test.sh` for most workflows
2. **Branch Naming**: Test branches use `test/` prefix, feature branches use `feature/`
3. **Always Test**: The scripts encourage testing before merging
4. **Stay Safe**: Your work is always backed up to remote before major operations
