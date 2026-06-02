#!/usr/bin/env bash
set -euo pipefail

# Resolves the known conflict set by keeping the current branch versions.
# Usage:
#   git checkout <your-branch>
#   git merge <base-branch>   # if conflicts occur
#   bash mpgu_chatbot/resolve_branch_conflicts.sh
#   git commit -m "Resolve merge conflicts"

CONFLICT_FILES=(
  "mpgu_chatbot/README.md"
  "mpgu_chatbot/backend/app/config.py"
  "mpgu_chatbot/backend/app/main.py"
  "mpgu_chatbot/backend/app/services/chat_engine.py"
  "mpgu_chatbot/backend/run.py"
)

if [[ ! -f .git/MERGE_HEAD ]]; then
  echo "No merge in progress. Nothing to resolve."
  exit 0
fi

for file in "${CONFLICT_FILES[@]}"; do
  if git ls-files -u -- "$file" | grep -q .; then
    echo "Resolving: $file"
    git checkout --ours -- "$file"
    git add "$file"
  else
    echo "Skipping (no conflict): $file"
  fi
done

if git diff --name-only --diff-filter=U | grep -q .; then
  echo "Some conflicts remain. Resolve manually:"
  git diff --name-only --diff-filter=U
  exit 1
fi

echo "✅ Conflicts resolved for listed files."
echo "Now run: git commit -m 'Resolve merge conflicts'"
