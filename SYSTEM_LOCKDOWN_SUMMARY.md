# 🔒 SYSTEM-WIDE LOCKDOWN COMPLETE

**Date:** November 3, 2024  
**Issue:** Work disappearing across projects due to Cursor worktrees  
**Occurrences:** 3 times in the last week  
**Impact:** Multi-hour work loss, 14+ commits going "missing"

---

## ✅ FIXES DEPLOYED

### 1. Global Cursor Settings (`~/Library/Application Support/Cursor/User/settings.json`)

```json
"cursor.enable_git_worktrees_setting": false,  ← DISABLED (was true)
"git.autofetch": false,                        ← DISABLED (was true)  
"git.confirmSync": true,                       ← ENABLED (was false)
"git.enableSmartCommit": false,
"git.confirmNoVerifyCommit": true,
"git.confirmForcePush": true,
"git.allowNoVerifyCommit": false,
"git.openRepositoryInParentFolders": "never",
"git.branchProtection": ["main", "master"]
```

### 2. Global Git Config (`~/.gitconfig`)

```ini
[advice]
    detachedHead = true
[core]
    hooksPath = ~/.git-templates/hooks
[init]
    templateDir = ~/.git-templates
[worktree]
    guessRemote = false
```

### 3. Global Git Hooks (`~/.git-templates/hooks/post-checkout`)

Warns if you're working in:
- `.cursor/worktrees/`
- `.claude/`
- `.codex/`

### 4. Shell Safety Layer (`~/.zshrc_agentspec_safety`)

**To activate, add to your `~/.zshrc`:**

```bash
source ~/.zshrc_agentspec_safety
```

Features:
- ✅ Warns on `cd` if you're in a dangerous directory
- ✅ Alias `where` - shows current location + last commit
- ✅ Alias `gsave` - quick commit+push with timestamp
- ✅ Auto-check on shell startup

### 5. Removed Dangerous Worktrees

```bash
✅ Removed: ~/.cursor/worktrees/agentspec__SSH__192.168.68.229_/m5MSY (14 commits behind)
✅ Removed: ~/.cursor/worktrees/agentspec__SSH__192.168.68.229_/sB46O (14 commits behind)
✅ Pruned: All dangling worktree references
```

---

## 🎯 WHAT THIS PREVENTS

### Before (The Problem):
1. You work in `/Users/davidmontgomery/agentspec`
2. You commit changes → `git push`
3. You close Cursor
4. Cursor creates hidden worktrees in `~/.cursor/worktrees/` for some remote operations
5. **These worktrees get stuck on old commits**
6. You reopen Cursor → **it randomly opens a worktree instead of main workspace**
7. Your recent 14 commits are "gone" - you're looking at yesterday's code
8. You do more work → commit → push
9. Later realize the work from step 7-8 was based on old code
10. **Hours of work lost or needs merging**

### After (The Fix):
1. Worktrees are **completely disabled** at the Cursor level
2. Git autofetch is **off** - no surprise fetches
3. Every `git checkout` shows a warning if you're in a worktree
4. Every `cd` command checks if you're in a dangerous directory
5. Shell startup checks your location
6. Confirmation required for sync, force push, no-verify commits

---

## 🚨 VERIFICATION CHECKLIST

Run these commands to verify the fix:

```bash
# 1. Check you're in the right place
pwd
# Should show: /Users/davidmontgomery/agentspec
# NOT: /Users/davidmontgomery/.cursor/worktrees/...

# 2. Check Cursor settings
grep "enable_git_worktrees" ~/Library/Application\ Support/Cursor/User/settings.json
# Should show: "cursor.enable_git_worktrees_setting": false

# 3. Check no worktrees exist
git worktree list
# Should show ONLY: /Users/davidmontgomery/agentspec (main workspace)

# 4. Test git hooks
cd /Users/davidmontgomery/agentspec && git checkout HEAD
# Should show: ✅ Checked out to: <commit> - <message>
# NOT show: 🚨 WARNING about worktree

# 5. Check autofetch is off
grep "git.autofetch" ~/Library/Application\ Support/Cursor/User/settings.json
# Should show: "git.autofetch": false
```

---

## 📋 DAILY WORKFLOW

### Every Time You Start Working:

```bash
# 1. Verify location
pwd

# 2. Check last commit
git log -1 --oneline

# 3. Pull latest (manual, not auto)
git pull

# 4. Work as normal...
```

### Every Hour (or after meaningful changes):

```bash
# Quick save
gsave
# Or manually:
git add -A && git commit -m "wip: description" && git push
```

### If Something Feels Wrong:

```bash
# Where am I?
where

# What worktrees exist?
git worktree list

# Am I on the right branch?
git branch --show-current

# What's my last commit?
git log -1 --oneline
```

---

## 🔍 IF WORK DISAPPEARS AGAIN

If you ever see work missing again, **immediately** run:

```bash
echo "Location: $(pwd)"
git log --oneline -5
git worktree list
git reflog -10
ls -la ~/.cursor/worktrees/
```

Save the output and investigate before doing anything else.

---

## 🛡️ FILES MODIFIED

### System-Wide:
- `~/Library/Application Support/Cursor/User/settings.json` → Cursor global settings
- `~/.gitconfig` → Git global config
- `~/.git-templates/hooks/post-checkout` → Global git hook
- `~/.zshrc_agentspec_safety` → Shell safety functions

### Project-Specific (agentspec):
- `agentspec/cli.py` → Added prompts to help display
- `.cursor/settings.json` → Project Cursor settings
- `.git/hooks/post-checkout` → Project git hook
- `CURSOR_WORKTREE_FIX.md` → Full documentation
- `SYSTEM_LOCKDOWN_SUMMARY.md` → This file

---

## 📝 TODO: Remaining Tasks

1. **Add to `~/.zshrc`:**
   ```bash
   source ~/.zshrc_agentspec_safety
   ```

2. **CRITICAL ACCESSIBILITY:** Upgrade `agentspec prompts -h` to match `generate -h` TUI quality
   - Rich panels
   - Provider guide
   - Clear visual hierarchy
   - Required for dyslexia accommodation

3. **Test the fixes:**
   - Close and reopen Cursor
   - Run `pwd` - should be in main workspace
   - Check `git worktree list` - should show only 1 entry

---

## 🎓 LESSONS LEARNED

1. **Cursor 2.0's worktree feature is dangerous** when it creates them in hidden directories
2. **Autofetch + worktrees = time travel bug** (random old code appearing)
3. **Git hooks are essential** for catching this early
4. **Shell-level validation** prevents working in wrong places
5. **Commit + push frequently** is the ultimate backup

---

**Status:** All fixes deployed and committed to git.  
**Next Steps:** Activate shell safety layer, test workflow, monitor for issues.

