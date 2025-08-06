# Git Batch Scripts

This directory contains batch scripts to automate common Git workflows for the HIS project.

## Scripts

### `test-ok.sh` - When tests pass ✅
Use this when your feature is complete and tests are passing.

**What it does:**
1. Commits any final changes
2. Pushes feature branch to remote
3. Switches to main branch
4. Pulls latest changes from remote
5. Merges feature branch into main
6. Pushes merged changes to remote
7. Cleans up by deleting local and remote feature branches

**Usage:**
```bash
./git-scripts/test-ok.sh
```

### `test-not-ok.sh` - When tests fail ❌
Use this when you need to save progress but tests aren't passing yet.

**What it does:**
1. Commits work in progress with WIP message
2. Pushes to remote for backup
3. Shows current status and next steps
4. Provides options for different approaches

**Usage:**
```bash
./git-scripts/test-not-ok.sh
```

## Workflow Example

1. Start feature: `git checkout -b feature/new-functionality`
2. Develop and test your changes
3. **If tests pass:** Run `./git-scripts/test-ok.sh`
4. **If tests fail:** Run `./git-scripts/test-not-ok.sh`, fix issues, repeat

## Safety Features

- Both scripts check that you're not on the main branch
- `test-ok.sh` uses `--no-ff` merge to preserve branch history
- `test-not-ok.sh` backs up your work to remote before suggesting next steps
- Both scripts provide clear feedback about what they're doing

## Requirements

- Git repository with remote origin configured
- Proper permissions to push to main branch
- Scripts should be run from repository root (`/root/his/`)
