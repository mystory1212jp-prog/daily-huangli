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

SSH=(ssh -p "$VPS_PORT" -o StrictHostKeyChecking=accept-new "${VPS_USER}@${VPS_HOST}")
RSYNC_SSH="ssh -p ${VPS_PORT} -o StrictHostKeyChecking=accept-new"

echo "==> 檢查遠端 Docker..."
"${SSH[@]}" 'command -v docker >/dev/null || { echo "遠端未安裝 Docker"; exit 1; }; docker compose version >/dev/null 2>&1 || docker-compose version >/dev/null 2>&1 || { echo "需要 docker compose"; exit 1; }'

echo "==> 同步專案到 ${VPS_USER}@${VPS_HOST}:${VPS_PATH}"
"${SSH[@]}" "mkdir -p '${VPS_PATH}'"

# 只同步站台與 Docker 定義（不含 .git）
rsync -az --delete \
  -e "$RSYNC_SSH" \
  --exclude '.git/' \
  --exclude '_site/' \
  --exclude '__pycache__/' \
  --exclude '.DS_Store' \
  --exclude '*.pyc' \
  ./ "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/"

# 正式 nginx 設定覆寫映像內預設（建置時用 prod conf）
echo "==> 使用正式 nginx 設定建置並啟動"
"${SSH[@]}" "cd '${VPS_PATH}' && \
  cp -f docker/nginx.prod.conf docker/nginx.conf && \
  export HUANGLI_PUBLISH='${HUANGLI_PUBLISH}' && \
  (docker compose -f docker-compose.prod.yml up -d --build || \
   docker-compose -f docker-compose.prod.yml up -d --build)"

echo "==> 健康檢查"
sleep 2
"${SSH[@]}" "docker ps --filter name=daily-huangli --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
"${SSH[@]}" "curl -s -o /dev/null -w 'local_http=%{http_code}\n' http://127.0.0.1:${HUANGLI_PUBLISH}/ || curl -s -o /dev/null -w 'local_http=%{http_code}\n' http://127.0.0.1/"

echo ""
echo "完成。請用瀏覽器開啟："
echo "  http://${VPS_HOST}/"
echo "若有網域與 HTTPS，請在主機 nginx/Caddy 反代到 127.0.0.1:${HUANGLI_PUBLISH}"
