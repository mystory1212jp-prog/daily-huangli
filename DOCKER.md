# Docker 開發說明

本專案**線上仍是 GitHub Pages 純靜態站**，不依賴 Docker 執行。  
Docker 只負責：**本機預覽、重建節氣／運勢資料、在隔離環境開發並 git push**。

```
┌─────────────────────┐     git push main      ┌──────────────────┐
│  Docker（本機開發）  │ ───────────────────►  │ GitHub Pages     │
│  nginx 預覽 + tools │     靜態 HTML/JS/JSON   │ 使用者照常開啟   │
└─────────────────────┘                        └──────────────────┘
```

## 前置

- 已安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)（或 Docker Engine + Compose v2）
- 專案目錄：`daily-huangli/`

## 快速開始

```bash
# 1. 建置映像（首次或 Dockerfile 變更後）
make docker-build
# 或：docker compose build web && docker compose --profile tools build tools

# 2. 啟動預覽（不影響主機其他服務；預設埠 8765）
make docker-up
# 開啟 http://localhost:8765

# 3. 停止預覽
make docker-down
```

換埠：

```bash
make docker-up PORT=9080
```

## 在容器內重建資料（寫回本機檔案）

`tools` 服務把專案目錄掛到 `/app`，執行腳本會直接改你磁碟上的 `data/`、`lib/`。

```bash
# 節氣精算 → core-db.json + huangli-db.js
make docker-rebuild-db

# 個人運勢 daily-facts + personal-system.js
make docker-rebuild-personal

# 節氣養生嵌入
make docker-rebuild-jieqi

# 一次全做
make docker-rebuild-all

# 快速檢驗（立秋日期、八字、兩人運勢）
make docker-test
```

互動 shell：

```bash
make docker-shell
# 容器內：
python scripts/build_db.py
python scripts/verify_calendar.py
git status
```

## 從 Docker 環境上傳 GitHub

1. 在**主機**或 `make docker-shell` 內改碼、重建資料  
2. 提交並推送（Pages 仍讀 `main` 靜態檔，與以前相同）：

```bash
# 建議在主機執行 git（憑證較單純）
git add -A
git status
git commit -m "說明這次變更"
git push origin main
```

容器內 push 時已掛載：

- `~/.gitconfig`（唯讀）
- `~/.ssh`（唯讀）

若使用 HTTPS + `gh auth`，可在主機先 `gh auth login`，再視需要把 token 以環境變數傳入（勿寫進映像）。

**不會影響：**

- 既有 GitHub Pages 網址與 PWA 快取策略（仍靠 `sw.js` 版號）
- 未開 Docker 時仍可 `python3 -m http.server` 本機預覽
- 訪客端無需安裝 Docker

## 服務一覽

| 服務 | 用途 | 常駐？ |
|------|------|--------|
| `web` | nginx 提供靜態站 | `docker compose up -d web` |
| `tools` | Python + git + gh | 否（`run --rm` 用完即刪） |

## 目錄與掛載

| 路徑 | 說明 |
|------|------|
| `.:/usr/share/nginx/html` | web 即時看本機碼（唯讀） |
| `.:/app` | tools 讀寫本機碼與 data/lib |

## 疑難

- **埠被占用**：`make docker-up PORT=9080`
- **節氣腳本失敗**：先 `make docker-build` 確保裝了 `lunar_python`
- **改了 JS 仍舊畫面**：加瀏覽器強制重新整理，或升 `sw.js` 的 `CACHE` 版號後再 push
