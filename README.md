# 每日黃曆

傳統風格每日黃曆網頁 App：國曆／農曆、宜忌、干支，以及兩位個人專屬運勢。

可安裝到 iPhone 主畫面（PWA），離線也能查。

## 線上使用

**網站：** https://mystory1212jp-prog.github.io/daily-huangli/

**倉庫：** https://github.com/mystory1212jp-prog/daily-huangli

### 加到 iPhone 主畫面

1. 用 **Safari** 開啟上方網站  
2. 點 **分享** → **加入主畫面** → 加入  
3. 之後從桌面圖示開啟即可（第一次連網後可離線使用）

詳見 [IPHONE安裝說明.md](./IPHONE安裝說明.md)

## 本機預覽

```bash
python3 -m http.server 8765
# 開啟 http://localhost:8765
```

## 功能

- 國曆／農曆（約 1900–2100）
- 年月日干支、生肖、建除宜忌
- 五行、納音、冲煞、方位、彭祖百忌
- 日家奇門、六壬日課
- **個人運勢雙層架構**（1985.08.28 辰時、1995.11.08 寅時）
  - 確定性層：`lunar_python` 精算日干支、建除、二十八宿、神煞、與本命刑冲合害
  - 語意層：十神→現代場景、神煞→情緒能量、節氣→養生映射，輸出現代生活建議
  - 結構化 `llmPayload` 可直接餵 Batch LLM
- 開源天時資料庫（`data/` + `lib/`）
- 每日分析與行動方案
- PWA 離線快取（含 2024–2028 日課精算檔）

## 資料庫重建

```bash
pip3 install -r requirements.txt
python3 scripts/build_db.py              # core-db + huangli-db.js
python3 scripts/build_personal_system.py # mapping-db + personal-bazi + daily-facts-YYYY + personal-system.js
```

體積約 **4 MB**，遠低於 500 MB。

## 說明

宜忌與運勢依民俗算法與開源曆法套件簡化，**僅供趣味參考**，不宜作為正式擇日或重大決策依據。
