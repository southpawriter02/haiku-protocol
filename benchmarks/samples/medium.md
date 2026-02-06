# Save and Restore Work in Progress with Git Stash

## Prerequisites

- Git 2.13 or later installed
- A Git repository with at least one commit
- Uncommitted changes in your working directory

## When to Use

Use `git stash` when you need to switch branches but have uncommitted changes that are not ready to commit. The stash saves modified tracked files and staged changes, then reverts your working directory to match HEAD.

## Steps

### Step 1: Stash Your Changes

Save current work in progress to the stash stack:

```bash
git stash push -m "work in progress on feature X"
```

Warning: Untracked files are not included by default. Add the `-u` flag to include them:

```bash
git stash push -u -m "WIP including new files"
```

### Step 2: Verify the Stash

List all stash entries:

```bash
git stash list
```

Expected output:

```
stash@{0}: On main: work in progress on feature X
```

### Step 3: Switch Branches

Your working directory is now clean. Switch branches as needed:

```bash
git checkout other-branch
```

Complete your work, commit it, then switch back:

```bash
git checkout original-branch
```

### Step 4: Restore Stashed Changes

Apply the most recent stash and remove it from the stack:

```bash
git stash pop
```

Note: If the stash cannot apply cleanly due to conflicts, Git will not drop the stash entry. Resolve conflicts manually, then run:

```bash
git stash drop stash@{0}
```

### Step 5: Inspect a Stash Before Applying

If you have multiple entries and want to preview one:

```bash
git stash show -p stash@{1}
```

This displays the full diff without modifying your working directory.

## Troubleshooting

- **Stash apply fails with conflicts:** Resolve conflicts, stage with `git add`, then drop with `git stash drop`.
- **Stashed on wrong branch:** Stashes are not branch-specific. Use `git stash pop` on any branch.
- **Stash specific files only:** Use pathspec: `git stash push -m "partial" -- path/to/file.py`.
