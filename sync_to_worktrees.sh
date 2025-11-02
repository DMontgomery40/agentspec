#!/bin/bash
# Copy agent files to active worktrees

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

FILES=(
    "AGENTS.md"
    "CLAUDE.md"
    ".cursor/.rules"
)

# Get worktrees
WORKTREES=$(git worktree list --porcelain | grep "worktree" | cut -d' ' -f2)

echo "🔄 Syncing files to active worktrees..."
echo ""

for wt in $WORKTREES; do
    # Skip main worktree
    if [ "$wt" = "$REPO_ROOT" ]; then
        continue
    fi
    
    branch=$(basename "$wt")
    echo "📁 Worktree: $wt"
    echo "   Branch: $branch"
    
    # Copy files
    for file in "${FILES[@]}"; do
        if [ -f "$REPO_ROOT/$file" ]; then
            mkdir -p "$wt/$(dirname "$file")"
            cp "$REPO_ROOT/$file" "$wt/$file"
            echo "   ✓ Copied $file"
        fi
    done
    echo ""
done

echo "✅ All worktrees updated!"
echo ""
echo "📝 Note: Files copied but not committed. Other agents working in those"
echo "   worktrees will see the changes and can commit them when ready."
