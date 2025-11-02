#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

FILES=(
    "AGENTS.md"
    "CLAUDE.md"
    ".cursor/.rules"
)

echo "🔄 Updating main branch..."

# Create temp worktree for main
TEMP_WT=$(mktemp -d)
git worktree add "$TEMP_WT" main

cd "$TEMP_WT"

# Pull latest
git pull --rebase origin main

# Copy files
for file in "${FILES[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        mkdir -p "$(dirname "$file")"
        cp "$REPO_ROOT/$file" "$file"
        echo "  ✓ Copied $file"
    fi
done

# Commit
git add "${FILES[@]}"
git commit -m "chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules)" || echo "No changes to commit"

# Push
git push origin main

cd "$REPO_ROOT"
git worktree remove "$TEMP_WT" --force

echo "✅ Main branch updated and pushed!"
