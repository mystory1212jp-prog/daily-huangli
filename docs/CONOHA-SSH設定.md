# ConoHa VPS：密碼登入 → SSH 金鑰（一步步）

本機已可產生專用金鑰：`~/.ssh/id_ed25519_conoha`  
**私鑰絕對不要傳給任何人、不要貼到聊天或 GitHub。**

---

## 步驟 1：確認本機公鑰

在 Mac 終端機執行：

```bash
cat ~/.ssh/id_ed25519_conoha.pub
```

會出現一行，類似：

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... daily-huangli-conoha-...
```

**整行複製**（從 `ssh-ed25519` 到結尾）。

若還沒有金鑰：

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_conoha -N "" -C "conoha-huangli"
cat ~/.ssh/id_ed25519_conoha.pub
```

---

## 步驟 2：用「密碼」登入 VPS 一次，寫入公鑰

把下面的 `你的IP`、`使用者` 換成 ConoHa 面板上的資料  
（常見使用者：`root`，或建立的 `ubuntu`／`centos`）。

```bash
# 第一次會問 yes/no，再問密碼（ConoHa 當初寄的 root 密碼）
ssh root@你的IP
```

登入成功後，**在 VPS 上**執行：

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# 下一行：把「整行公鑰」貼在兩個引號中間
echo "這裡貼上公鑰整行" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

### 或用本機一行完成（仍會問一次密碼）

```bash
# macOS 若無 ssh-copy-id，用這段：
PUB=$(cat ~/.ssh/id_ed25519_conoha.pub)
ssh root@你的IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$PUB' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

---

## 步驟 3：設定本機 SSH 別名（之後免記參數）

編輯（沒有就新建）`~/.ssh/config`：

```sshconfig
Host conoha-huangli
  HostName 你的IP
  User root
  IdentityFile ~/.ssh/id_ed25519_conoha
  IdentitiesOnly yes
```

測試：

```bash
ssh conoha-huangli
# 應可「不用密碼」進入
```

---

## 步驟 4：VPS 安裝 Docker（只做一次）

```bash
ssh conoha-huangli
curl -fsSL https://get.docker.com | sh
docker compose version
# ConoHa 安全群組／防火牆放行 TCP 80（與 443 若要用 HTTPS）
exit
```

---

## 步驟 5：部署黃曆

在本機專案目錄：

```bash
cd /Users/wan/Downloads/daily-huangli

VPS_HOST=你的IP \
VPS_USER=root \
VPS_PATH=/opt/daily-huangli \
HUANGLI_PUBLISH=80 \
./scripts/deploy-vps.sh
```

若已設 `Host conoha-huangli`，也可：

```bash
VPS_HOST=conoha-huangli VPS_USER=root ./scripts/deploy-vps.sh
```

瀏覽器開啟：`http://你的IP/`

---

## ConoHa 控制面板注意

1. **VPS 清單** → 記下 **IP 位址**  
2. **網絡 / 安全組**（名稱因方案而異）→ 入站允許 **80/tcp**（HTTP）  
3. 若用 **固定密碼** 且改過，以面板「重設密碼」為準  
4. 建議設好金鑰後，再考慮關閉密碼登入（進階，可之後做）

---

## 設好金鑰後回報我

請回覆這三樣（**不要**貼私鑰）：

1. IP 或網域  
2. SSH 使用者（如 `root`）  
3. 是否已 `ssh conoha-huangli` 成功  

我就可以幫你執行 `deploy-vps.sh` 完成部署。

---

## 與 GitHub Pages

| 位址 | 說明 |
|------|------|
| `https://mystory1212jp-prog.github.io/daily-huangli/` | 原本 Pages，繼續可用 |
| `http://你的VPS_IP/` | ConoHa 上的 Docker 站 |

兩邊內容相同架構；之後改碼可 `git push` + 再跑一次 `deploy-vps.sh` 同步 VPS。
