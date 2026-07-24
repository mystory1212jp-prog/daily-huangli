# 每日黃曆

傳統風格每日黃曆網頁 App：國曆／農曆、宜忌、干支，以及 1985.08.28 個人運勢。

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
- 個人運勢（1985.08.28 辰時、1995.11.08 寅時）
- **開源天時資料庫**（`data/` + `lib/`，約 0.1 MB）驅動節氣旺衰、十神喜用、綜合評分
- 每日分析與行動方案（配合當日天時）
- PWA 離線快取

## 資料庫

```bash
python3 scripts/build_db.py   # 重建 data/core-db.json 與 lib/huangli-db.js
```

詳見 [data/README.md](./data/README.md)。體積遠低於 500 MB。

## 說明

宜忌與運勢依民俗算法簡化，**僅供趣味參考**，不宜作為正式擇日或重大決策依據。
