#!/usr/bin/env bash
# 把「訪客需要的靜態檔」同步到 _site/（本機或 CI 皆可用）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-"$ROOT/_site"}"
rm -rf "$DEST"
mkdir -p "$DEST"
cp -a "$ROOT/index.html" "$ROOT/sw.js" "$ROOT/manifest.webmanifest" "$ROOT/.nojekyll" "$DEST/"
cp -a "$ROOT/lib" "$ROOT/icons" "$ROOT/data" "$DEST/"
if [[ -f "$ROOT/IPHONE安裝說明.md" ]]; then
  cp "$ROOT/IPHONE安裝說明.md" "$DEST/" || true
fi
find "$DEST" -name '.DS_Store' -delete 2>/dev/null || true
echo "Staged → $DEST ($(find "$DEST" -type f | wc -l | tr -d ' ') files)"
