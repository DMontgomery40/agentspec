#!/bin/bash
# Sync AGENTS.md, CLAUDE.md, and .cursor/.rules to all branches without checking out

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# Files to sync
FILES=(
    "AGENTS.md"
    "CLAUDE.md"
    ".cursor/.rules"
)

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Get all branches (local and remote tracking branches)
BRANCHES=$(git branch -a | grep -v "HEAD" | sed 's/^[* ]*//; s/remotes\/origin\///' | sort -u)

# Store current file contents in temp directory
TEMP_DIR=$(mktemp -d)
echo "💾 Storing current file versions in $TEMP_DIR"

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        mkdir -p "$TEMP_DIR/$(dirname "$file")"
        cp "$file" "$TEMP_DIR/$file"
        echo "  ✓ Saved $file"
    else
        echo "  ⚠️  Warning: $file not found"
    fi
done

# Function to update a branch
update_branch() {
    local branch=$1
    
    # Skip current branch (we'll handle it separately)
    if [ "$branch" = "$CURRENT_BRANCH" ]; then
        return
    fi
    
    # Skip remote branches that don't exist locally
    if ! git rev-parse --verify "$branch" >/dev/null 2>&1; then
        return
    fi
    
    echo ""
    echo "🔄 Updating branch: $branch"
    
    # Create a temporary working directory for this branch
    WORK_DIR=$(mktemp -d)
    
    # Use git worktree to work with the branch
    if git worktree add "$WORK_DIR" "$branch" 2>/dev/null; then
        # Copy files to the worktree
        for file in "${FILES[@]}"; do
            if [ -f "$TEMP_DIR/$file" ]; then
                mkdir -p "$WORK_DIR/$(dirname "$file")"
                cp "$TEMP_DIR/$file" "$WORK_DIR/$file"
                echo "  ✓ Copied $file to $branch"
            fi
        done
        
        # Commit changes in the worktree
        cd "$WORK_DIR"
        git add "${FILES[@]}" 2>/dev/null || true
        
        if git diff --cached --quiet; then
            echo "  ℹ️  No changes needed in $branch"
        else
            git commit -m "chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules)" || true
            echo "  ✅ Committed changes to $branch"
        fi
        
        cd "$REPO_ROOT"
        
        # Remove the worktree
        git worktree remove "$WORK_DIR" --force
    else
        echo "  ⚠️  Failed to create worktree for $branch"
    fi
}

# Update all branches except current
echo ""
echo "🚀 Starting branch updates..."
for branch in $BRANCHES; do
    update_branch "$branch"
done

# Update current branch
echo ""
echo "🔄 Updating current branch: $CURRENT_BRANCH"
for file in "${FILES[@]}"; do
    if [ -f "$TEMP_DIR/$file" ]; then
        mkdir -p "$(dirname "$file")"
        cp "$TEMP_DIR/$file" "$file"
        echo "  ✓ Updated $file"
    fi
done

# Add files to current branch (but don't commit - let user decide)
git add "${FILES[@]}" 2>/dev/null || true
echo "  ✅ Files staged in current branch (not committed)"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✨ Done! All branches updated."
echo ""
echo "📝 Note: Changes in current branch are staged but not committed."
echo "   Run 'git commit -m \"chore: sync agent configuration files\"' to commit them."
echo ""
echo "🔁 To push changes to remote branches, run:"
echo "   git push origin --all"



