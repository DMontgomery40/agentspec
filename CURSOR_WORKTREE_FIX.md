# 🚨 CRITICAL: Cursor Worktree "Time Travel" Bug - FIX AND PREVENTION

## Problem Summary

Cursor creates hidden git worktrees in `~/.cursor/worktrees/` that get **stuck on old commits**. When you reopen Cursor, it sometimes opens these old worktrees instead of your main workspace, making your recent work "disappear."

## Current State (Nov 3, 2024)

```
✅ MAIN:      /Users/davidmontgomery/agentspec         → a86e643 (Nov 2, 10:37 AM)
❌ WORKTREE1: ~/.cursor/worktrees/.../m5MSY            → 7d7ee57 (Oct 31) - 14 COMMITS BEHIND
❌ WORKTREE2: ~/.cursor/worktrees/.../sB46O            → 7d7ee57 (Oct 31) - 14 COMMITS BEHIND
```

**Missing commits in worktrees:** 14 commits representing ~12+ hours of work from Nov 1-2.

---

## IMMEDIATE FIXES (Copy & Paste These Commands)

### 1. Commit Your Current Work RIGHT NOW

```bash
cd /Users/davidmontgomery/agentspec
git add -A
git commit -m "fix: add prompts command to help display + save all uncommitted work"
git push
```

### 2. Clean Up The Old Worktrees

```bash
# Remove the worktrees (they're out of date anyway)
git worktree remove ~/.cursor/worktrees/agentspec__SSH__192.168.68.229_/m5MSY --force
git worktree remove ~/.cursor/worktrees/agentspec__SSH__192.168.68.229_/sB46O --force

# Prune worktree references
git worktree prune
```

### 3. Verify You're In The Right Place

Add this to your `~/.zshrc`:

```bash
# Show git status on cd
cd() {
    builtin cd "$@" && pwd && git branch 2>/dev/null | grep '*'
}
```

---

## PREVENTION: Never Lose Work Again

### A. Always Check Your Location When Opening Cursor

Before starting work, run:

```bash
pwd                    # Should show: /Users/davidmontgomery/agentspec
git log --oneline -1   # Should show most recent commit
git status             # Check for uncommitted changes
```

**If you see `/.cursor/worktrees/` in your path → YOU'RE IN THE WRONG PLACE!**

### B. Commit Frequently

```bash
# Every hour or after meaningful changes:
git add -A
git commit -m "wip: <what you just did>"
git push
```

### C. Create A Safety Check Script

Save this as `/Users/davidmontgomery/check-workspace.sh`:

```bash
#!/bin/bash
CWD=$(pwd)
if [[ "$CWD" == *".cursor/worktrees"* ]]; then
    echo "🚨 WARNING: You're in a Cursor worktree!"
    echo "Location: $CWD"
    echo ""
    echo "Switch to main workspace:"
    echo "  cd /Users/davidmontgomery/agentspec"
    exit 1
else
    echo "✅ You're in the main workspace"
    git log --oneline -1
fi
```

Make it executable and run it before working:

```bash
chmod +x ~/check-workspace.sh
~/check-workspace.sh
```

### D. Prevent Cursor from Creating Worktrees

Add to `/Users/davidmontgomery/agentspec/.cursor/settings.json`:

```json
{
  "workbench.editor.enablePreview": false,
  "workbench.startupEditor": "none",
  "git.enableWorktrees": false
}
```

---

## WHAT HAPPENED TO YOUR "PROMPTS" WORK

### Timeline Reconstruction:

1. **Earlier (days ago):** You implemented the `prompts` subcommand (lines 764-854 in cli.py) ✅
2. **You tested it:** `agentspec prompts -h` worked and showed help ✅  
3. **You thought:** "Great, it's done!" ✅
4. **What was MISSING:** Nobody ever added `prompts` to the main `_show_rich_help()` table ❌
5. **Today:** You opened a worktree (14 commits behind) that doesn't even have the prompts command ❌

### Current Status:

✅ The `prompts` command EXISTS and WORKS  
✅ I added it to the help display (uncommitted change)  
❌ This change is NOT YET COMMITTED  
❌ The worktrees don't have ANY of your last 14 commits  

---

## RECOVERY CHECKLIST

- [ ] Run the "IMMEDIATE FIXES" commands above
- [ ] Commit the current cli.py changes
- [ ] Push to GitHub
- [ ] Remove old worktrees
- [ ] Add workspace safety check to your shell init
- [ ] Test: close Cursor, reopen, run `pwd` and `git log -1`
- [ ] Verify `agentspec -h` now shows prompts in the commands table

---

## Why This Happened 3 Times

1. **First time:** Cursor created worktrees, you didn't realize
2. **Second time:** Worktrees still there, Cursor opened them randomly
3. **Third time (today):** Same issue - worktrees are 14 commits behind
4. **Root cause:** Cursor's worktree feature + no commit habits + no location awareness

---

## Long-Term Solution

### Option 1: Disable Cursor Worktrees (Recommended)

```bash
# Add to Cursor settings
"git.enableWorktrees": false
```

### Option 2: Always Sync Worktrees (More Work)

```bash
# Add to ~/.zshrc
alias sync-worktrees='cd ~/agentspec && for wt in ~/.cursor/worktrees/agentspec*/*/; do (cd "$wt" && git fetch && git pull); done'
```

Run `sync-worktrees` daily.

### Option 3: Delete Worktrees On Startup

```bash
# Add to ~/.zshrc
rm -rf ~/.cursor/worktrees/agentspec* 2>/dev/null
```

---

## Final Note

This is NOT a git bug or a Cursor bug in isolation - it's a **workflow bug**. The tools are working as designed, but the combination creates a footgun. The fix is:

1. **Commit more often** (every hour minimum)
2. **Always check `pwd`** before starting work  
3. **Remove or sync worktrees** regularly
4. **Push to GitHub** after every commit (backup!)

---

## Questions?

If work disappears again:

1. `pwd` - where are you?
2. `git log -1` - what commit?
3. `git worktree list` - what worktrees exist?
4. `git reflog` - where did HEAD move?

This will help diagnose what happened.

