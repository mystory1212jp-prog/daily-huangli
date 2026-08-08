# 部署到 ConoHa VPS

GitHub Pages 可繼續使用；VPS 是**額外**一份相同靜態站（Docker + nginx）。

## 你需要提供（本機目前沒有）

| 項目 | 例 |
|------|-----|
| VPS IP 或主機名 | `133.x.x.x` / `huangli.example.com` |
| SSH 使用者 | `root` 或 `ubuntu` |
| 登入方式 | SSH 私鑰，或已設好的 `ssh user@host` |
| （可選）網站埠 | 預設 `80`；若 80 已被佔用可改 `8080` 再反代 |

本機 `~/.ssh` 目前是空的，需先能：

```bash
ssh root@你的IP
```

## 伺服器一次性準備（ConoHa Ubuntu 例）

```bash
# 安裝 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # 非 root 時
# 重新登入後：
docker compose version
```

### 防火牆（必做，否則外網打不開）

伺服器內 `ufw` 已需允許 80/443；**ConoHa 控制面板**還要放行，否則只有 SSH(22) 通、網站會連線逾時：

1. 登入 [ConoHa 控制面板](https://manage.conoha.jp/)
2. **VPS** → 選取主機 → **網絡**／**安全組**／**パケットフィルター**（名稱因方案而異）
3. 入站規則新增：
   - **TCP 80**（HTTP）
   - **TCP 443**（之後若上 HTTPS）
4. 儲存後等 1～2 分鐘，再開 `http://你的IP/`

本機可用以下確認埠是否對公網開放：

```bash
nc -z -G 5 你的IP 80 && echo open || echo blocked
```

## 從本機一鍵部署

```bash
cd /Users/wan/Downloads/daily-huangli
chmod +x scripts/deploy-vps.sh

VPS_HOST=你的IP \
VPS_USER=root \
VPS_PATH=/opt/daily-huangli \
HUANGLI_PUBLISH=80 \
./scripts/deploy-vps.sh
```

之後改碼推 GitHub 的同時，若要同步 VPS：

```bash
VPS_HOST=你的IP ./scripts/deploy-vps.sh
```

## 架構（多專案子路徑）

```
本機 rsync ──► VPS /opt/daily-huangli
                    │
                    docker compose -f docker-compose.prod.yml up
                    │
                    nginx gateway :80
                      ├─ http://IP/                 → 專案入口
                      └─ http://IP/daily-huangli/   → 每日黃曆
```

之後新系統：在 `docker/nginx.prod.conf` 加 `location /新路徑/`，映像裡放對應子目錄即可。

- **不影響** GitHub Pages（仍是 `…/daily-huangli/` 倉庫根路徑）  
- 訪客開 VPS 子路徑即可，**不必**在瀏覽器裝 Docker  


## HTTPS（建議）

用主機 Caddy 或 nginx 憑證反代到 `127.0.0.1:80`（或把 `HUANGLI_PUBLISH=8080`，容器只聽 localhost）。

## 與 GitHub 雙軌

| 管道 | 用途 |
|------|------|
| GitHub Pages | 原本網址、PWA 安裝 |
| ConoHa VPS | 自有 IP／網域、可自管 |
