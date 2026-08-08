#!/usr/bin/env bash
# 部署 daily-huangli 到遠端 VPS（Docker）
#
# 必要環境變數或參數：
#   VPS_HOST   例：133.x.x.x 或 example.com
#   VPS_USER   例：root 或 ubuntu（預設 root）
#   VPS_PATH   遠端目錄（預設 /opt/daily-huangli）
#   VPS_PORT   SSH 埠（預設 22）
#   HUANGLI_PUBLISH  容器對外埠（預設 80）
#
# 例：
#   VPS_HOST=133.x.x.x VPS_USER=root ./scripts/deploy-vps.sh
#   ./scripts/deploy-vps.sh 133.x.x.x root /opt/daily-huangli

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VPS_HOST="${VPS_HOST:-${1:-}}"
VPS_USER="${VPS_USER:-${2:-root}}"
VPS_PATH="${VPS_PATH:-${3:-/opt/daily-huangli}}"
VPS_PORT="${VPS_PORT:-22}"
HUANGLI_PUBLISH="${HUANGLI_PUBLISH:-80}"

if [[ -z "$VPS_HOST" ]]; then
  echo "用法: VPS_HOST=<IP或域名> [VPS_USER=root] [VPS_PATH=/opt/daily-huangli] $0"
  echo "  或: $0 <host> [user] [path]"
  exit 1
fi

# 優先使用 ConoHa 專用金鑰（若存在）
SSH_ID_OPTS=()
RSYNC_E="ssh -p ${VPS_PORT} -o StrictHostKeyChecking=accept-new"
if [[ -f "${HOME}/.ssh/id_ed25519_conoha" ]]; then
  SSH_ID_OPTS=(-i "${HOME}/.ssh/id_ed25519_conoha" -o IdentitiesOnly=yes)
  RSYNC_E="ssh -p ${VPS_PORT} -i ${HOME}/.ssh/id_ed25519_conoha -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
fi
SSH=(ssh -p "$VPS_PORT" "${SSH_ID_OPTS[@]}" -o StrictHostKeyChecking=accept-new "${VPS_USER}@${VPS_HOST}")
RSYNC_SSH="$RSYNC_E"

echo "==> 檢查遠端 Docker..."
"${SSH[@]}" 'command -v docker >/dev/null || { echo "遠端未安裝 Docker"; exit 1; }; docker compose version >/dev/null 2>&1 || docker-compose version >/dev/null 2>&1 || { echo "需要 docker compose"; exit 1; }'

echo "==> 同步專案到 ${VPS_USER}@${VPS_HOST}:${VPS_PATH}"
"${SSH[@]}" "mkdir -p '${VPS_PATH}'"

# 只同步站台與 Docker 定義（不含 .git）
rsync -az --delete \
  -e "$RSYNC_E" \
  --exclude '.git/' \
  --exclude '_site/' \
  --exclude '__pycache__/' \
  --exclude '.DS_Store' \
  --exclude '*.pyc' \
  ./ "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/"

echo "==> 建置並啟動（gateway + /daily-huangli/）"
"${SSH[@]}" "cd '${VPS_PATH}' && \
  export HUANGLI_PUBLISH='${HUANGLI_PUBLISH}' && \
  (docker compose -f docker-compose.prod.yml up -d --build || \
   docker-compose -f docker-compose.prod.yml up -d --build)"

echo "==> 健康檢查"
sleep 2
"${SSH[@]}" "docker ps --filter name=daily-huangli --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
"${SSH[@]}" "curl -s -o /dev/null -w 'portal=%{http_code}\n' http://127.0.0.1:${HUANGLI_PUBLISH}/"
"${SSH[@]}" "curl -s -o /dev/null -w 'huangli=%{http_code}\n' http://127.0.0.1:${HUANGLI_PUBLISH}/daily-huangli/"

echo ""
echo "完成。請開啟："
echo "  入口    http://${VPS_HOST}/"
echo "  黃曆    http://${VPS_HOST}/daily-huangli/"
echo "（若外網逾時，請在 ConoHa 安全組放行 TCP 80）"
