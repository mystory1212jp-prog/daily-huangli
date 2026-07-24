# 黃曆／奇門／六壬／個人運勢 開源知識庫

## 體積

| 檔案 | 約略大小 |
|------|----------|
| `core-db.json` | ~55 KB |
| `lib/huangli-db.js` | ~55 KB |
| `mapping-db.json` | ~14 KB |
| `personal-bazi.json` | ~2 KB |
| `daily-facts-2024..2028.json` | 各 ~0.79 MB |
| `lib/personal-system.js` | ~16 KB |
| **合計** | **~4 MB**（遠低於 500 MB 上限） |

## 雙層架構

### 確定性計算層（`scripts/build_personal_system.py` + `lunar_python`）

預先精算每日：

- 年月日干支、建除、黃道十二神、二十八宿
- 宜忌、吉神凶煞（董公擇日系）
- 與個人四柱地支的 **刑／冲／合／害**（程式寫死）
- 流日十神、喜用忌神命中、綜合分數

輸出：`daily-facts-YYYY.json`、`personal-bazi.json`

### 語意轉譯層（`mapping-db.json` + `lib/personal-system.js`）

三維映射庫：

1. **十神 → 現代場景**（寫 Code、企劃、合規、控制硬體衝動消費…）
2. **神煞 → 情緒能量**（天乙貴人→開源社群指點；羊刃→部署防粗心…）
3. **節氣 × 中醫養生**（木旺疏肝、大暑養心…）

前端 `PersonalFortuneEngine` 將結構化 JSON 轉成現代生活建議；同時附帶 `llmPayload` 供未來 Batch API。

## 重建

```bash
pip3 install -r requirements.txt
python3 scripts/build_db.py
python3 scripts/build_personal_system.py
```

## 授權說明

表內為傳統曆法／術數**事實與通用口訣結構**（不可著作權的知識），演算法移植自開源黃曆／奇門／六壬／`lunar_python` 通行做法，供學習與民俗參考。
