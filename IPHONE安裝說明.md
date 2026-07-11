# 把「每日黃曆」加到 iPhone

iPhone 無法像 Android 那樣直接安裝任意 App，但可以把這個黃曆 **加到主畫面**，外觀與操作都像獨立 App，**第一次連網開啟後，之後離線也能查**。

---

## 方法一：用免費網址（推薦，隨時隨地可開）

需要先把 `huangli` 資料夾放到一個「公開網址」（HTTPS）。任選一種即可：

### A. Netlify Drop（最簡單，約 1 分鐘）

1. 電腦開啟：https://app.netlify.com/drop  
2. 把整個 **`huangli` 資料夾** 拖進去  
3. 會得到一個網址，例如 `https://xxxxx.netlify.app`  
4. 用 **iPhone 的 Safari** 開啟該網址（不要用 Chrome 加主畫面，效果較差）  
5. 依下方「加入主畫面」步驟操作  

### B. GitHub Pages

1. 把 `huangli` 上傳到 GitHub 儲存庫  
2. 在倉庫 Settings → Pages 啟用，來源選主分支  
3. 用 Safari 開啟 GitHub 給你的網址，再「加入主畫面」

---

## 方法二：同一 Wi‑Fi 下用電腦當伺服器（臨時）

適合先試用，電腦關機後 iPhone 就連不到。

在電腦終端機執行：

```bash
cd /path/to/huangli
python3 -m http.server 8765
```

查電腦區網 IP（Mac 可看「系統設定 → 網路」），例如 `192.168.1.20`。

iPhone Safari 開啟：

```text
http://192.168.1.20:8765
```

再「加入主畫面」。注意：此方式主畫面捷徑在電腦關機後可能無法開啟，**長期使用請用方法一**。

---

## 在 iPhone 上「加入主畫面」

1. 用 **Safari** 打開黃曆網址  
2. 點底部中間的 **分享** 按鈕（方框 + 向上箭頭）  
3. 向下滑，點 **加入主畫面**  
4. 名稱可維持「每日黃曆」，點 **加入**  
5. 回到桌面，會出現圖示，點開即可查詢  

加入後：

- 以全螢幕開啟，沒有 Safari 網址列  
- 第一次成功載入後，會快取在手機上，**沒網路也能看當天黃曆與運勢**

---

## 常見問題

| 問題 | 說明 |
|------|------|
| 找不到「加入主畫面」 | 確認是 **Safari**，不是 Instagram／Line 內建瀏覽器 |
| 圖示是空白或截圖 | 重新用 Safari 開一次完整網址再加入 |
| 離線打不開 | 需至少成功連網開啟過一次，讓 Service Worker 完成快取 |
| 想更新內容 | 之後若改過程式，重新部署網址後，用 Safari 再開一次即可更新快取 |

---

## 檔案清單（部署時請整包上傳）

```text
huangli/
  index.html
  manifest.webmanifest
  sw.js
  icons/
    apple-touch-icon.png
    icon-192.png
    icon-512.png
```
