#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立黃曆／奇門／六壬／節氣／個人命理對照資料庫（開源算法彙編，體積精簡）。

資料來源與演算法依據（公有領域／開源慣用表）：
- 農曆與節氣推算：壽星天文曆思路、民間通用 LUNAR_INFO 位元表（與 6tail/lunar 等開源庫同源）
- 建除、黃黑道、神煞：傳統協紀辨方類擇日表（開源黃曆專案通用結構）
- 奇門遁甲：拆補法陰陽遁局數歌訣（與 kinqimen 等開源排盤表一致）
- 大六壬：月將中氣換將、貴人、干寄宮（傳統壬學通行表）
- 個人命理：日主十神、旺衰、冲合刑害（子平術開源常見規則）

輸出：
  data/core-db.json   — 機器可讀
  lib/huangli-db.js   — 瀏覽器直接載入
體積目標：遠低於 500MB（通常 < 2MB）
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LIB = ROOT / "lib"
DATA.mkdir(exist_ok=True)
LIB.mkdir(exist_ok=True)

TG = list("甲乙丙丁戊己庚辛壬癸")
DZ = list("子丑寅卯辰巳午未申酉戌亥")
SX = list("鼠牛虎兔龍蛇馬羊猴雞狗豬")
WX_G = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
WX_Z = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

# 1900–2100 農曆資訊（開源黃曆通用表，16-bit/年）
LUNAR_INFO = [
    0x04BD8, 0x04AE0, 0x0A570, 0x054D5, 0x0D260, 0x0D950, 0x16554, 0x056A0, 0x09AD0, 0x055D2,
    0x04AE0, 0x0A5B6, 0x0A4D0, 0x0D250, 0x1D255, 0x0B540, 0x0D6A0, 0x0ADA2, 0x095B0, 0x14977,
    0x04970, 0x0A4B0, 0x0B4B5, 0x06A50, 0x06D40, 0x1AB54, 0x02B60, 0x09570, 0x052F2, 0x04970,
    0x06566, 0x0D4A0, 0x0EA50, 0x06E95, 0x05AD0, 0x02B60, 0x186E3, 0x092E0, 0x1C8D7, 0x0C950,
    0x0D4A0, 0x1D8A6, 0x0B550, 0x056A0, 0x1A5B4, 0x025D0, 0x092D0, 0x0D2B2, 0x0A950, 0x0B557,
    0x06CA0, 0x0B550, 0x15355, 0x04DA0, 0x0A5B0, 0x14573, 0x052B0, 0x0A9A8, 0x0E950, 0x06AA0,
    0x0AEA6, 0x0AB50, 0x04B60, 0x0AAE4, 0x0A570, 0x05260, 0x0F263, 0x0D950, 0x05B57, 0x056A0,
    0x096D0, 0x04DD5, 0x04AD0, 0x0A4D0, 0x0D4D4, 0x0D250, 0x0D558, 0x0B540, 0x0B6A0, 0x195A6,
    0x095B0, 0x049B0, 0x0A974, 0x0A4B0, 0x0B27A, 0x06A50, 0x06D40, 0x0AF46, 0x0AB60, 0x09570,
    0x04AF5, 0x04970, 0x064B0, 0x074A3, 0x0EA50, 0x06B58, 0x05AC0, 0x0AB60, 0x096D5, 0x092E0,
    0x0C960, 0x0D954, 0x0D4A0, 0x0DA50, 0x07552, 0x056A0, 0x0ABB7, 0x025D0, 0x092D0, 0x0CAB5,
    0x0A950, 0x0B4A0, 0x0BAA4, 0x0AD50, 0x055D9, 0x04BA0, 0x0A5B0, 0x15176, 0x052B0, 0x0A930,
    0x07954, 0x06AA0, 0x0AD50, 0x05B52, 0x04B60, 0x0A6E6, 0x0A4E0, 0x0D260, 0x0EA65, 0x0D530,
    0x05AA0, 0x076A3, 0x096D0, 0x04AFB, 0x04AD0, 0x0A4D0, 0x1D0B6, 0x0D250, 0x0D520, 0x0DD45,
    0x0B5A0, 0x056D0, 0x055B2, 0x049B0, 0x0A577, 0x0A4B0, 0x0AA50, 0x1B255, 0x06D20, 0x0ADA0,
    0x14B63, 0x09370, 0x049F8, 0x04970, 0x064B0, 0x168A6, 0x0EA50, 0x06B20, 0x1A6C4, 0x0AAE0,
    0x0A2E0, 0x0D2E3, 0x0C960, 0x0D557, 0x0D4A0, 0x0DA50, 0x05D55, 0x056A0, 0x0A6D0, 0x055D4,
    0x052D0, 0x0A9B8, 0x0A950, 0x0B4A0, 0x0B6A6, 0x0AD50, 0x055A0, 0x0ABA4, 0x0A5B0, 0x052B0,
    0x0B273, 0x06930, 0x07337, 0x06AA0, 0x0AD50, 0x14B55, 0x04B60, 0x0A570, 0x054E4, 0x0D160,
    0x0E968, 0x0D520, 0x0DAA0, 0x16AA6, 0x056D0, 0x04AE0, 0x0A9D4, 0x0A2D0, 0x0D150, 0x0F252,
    0x0D520,
]

# 節氣名（24）與對應月建
JIEQI_NAMES = [
    "小寒", "大寒", "立春", "雨水", "驚蟄", "春分",
    "清明", "穀雨", "立夏", "小滿", "芒種", "夏至",
    "小暑", "大暑", "立秋", "處暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
]
JIEQI_YUEJIAN = {
    "立春": "寅", "雨水": "寅", "驚蟄": "卯", "春分": "卯",
    "清明": "辰", "穀雨": "辰", "立夏": "巳", "小滿": "巳",
    "芒種": "午", "夏至": "午", "小暑": "未", "大暑": "未",
    "立秋": "申", "處暑": "申", "白露": "酉", "秋分": "酉",
    "寒露": "戌", "霜降": "戌", "立冬": "亥", "小雪": "亥",
    "大雪": "子", "冬至": "子", "小寒": "丑", "大寒": "丑",
}

# 壽星／開源曆常用：節氣儒略日近似係數（世紀單位），精度足夠日常黃曆
# 公式：JDE ≈ 365.242 * (Y-2000) + C[i] 的簡化月日表改為逐年掃近似日
# 這裡用穩定近似：各節氣公曆月日中心值 ± 用年偏移修正
JIEQI_APPROX = [
    (1, 5.4), (1, 20.1), (2, 4.0), (2, 18.7), (3, 5.6), (3, 20.4),
    (4, 5.0), (4, 20.1), (5, 5.7), (5, 21.1), (6, 5.9), (6, 21.4),
    (7, 7.2), (7, 22.8), (8, 7.6), (8, 23.1), (9, 7.8), (9, 23.1),
    (10, 8.3), (10, 23.2), (11, 7.5), (11, 22.3), (12, 7.1), (12, 21.9),
]


def jieqi_date(year: int, idx: int) -> date:
    """開源黃曆慣用近似：節氣公曆日期（足以定月建／陰陽遁）。"""
    m, d = JIEQI_APPROX[idx]
    # 世紀修正（粗）：每百年約 +0.2～0.4 日，取線性
    adj = (year - 2000) * 0.2422 / 365.25  # 天
    day = d + adj
    # 閏年 2 月後微調
    if m >= 3 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        day += 0.0
    di = int(day)
    frac = day - di
    base = date(year, m, min(di, 28 if m == 2 else 30 if m in (4, 6, 9, 11) else 31))
    # 處理溢出
    try:
        base = date(year, m, min(max(di, 1), 28 if m == 2 else 30 if m in (4, 6, 9, 11) else 31))
    except ValueError:
        base = date(year, m, 28)
    if frac > 0.5 and base.day < 28:
        base = base + timedelta(days=1)
    return base


def build_jieqi_index(y0=1980, y1=2040):
    """預計算節氣日期表（約 60 年 × 24 ≈ 1440 條，極小）。"""
    table = {}
    for y in range(y0, y1 + 1):
        arr = []
        for i, name in enumerate(JIEQI_NAMES):
            d = jieqi_date(y, i)
            arr.append({"n": name, "m": d.month, "d": d.day})
        table[str(y)] = arr
    return table


def build_huangli_tables():
    jianchu = ["建", "除", "滿", "平", "定", "執", "破", "危", "成", "收", "開", "閉"]
    jianchu_huang = ["除", "危", "定", "執", "成", "開"]
    # 建除宜忌（開源黃曆通用簡表，可依神煞再濾）
    jianchu_yiji = {
        "建": {"yi": ["出行", "上任", "會友", "上書", "見貴"], "ji": ["動土", "開倉", "掘井", "乘船"]},
        "除": {"yi": ["醫療", "破屋", "求醫", "針灸", "掃舍", "沐浴"], "ji": ["結婚", "赴任", "遠行", "開市"]},
        "滿": {"yi": ["祈福", "祭祀", "結親", "開市", "交易", "求財"], "ji": ["服藥", "栽種", "安葬", "針灸"]},
        "平": {"yi": ["修飾垣牆", "平治道塗", "修造", "裝飾"], "ji": ["嫁娶", "開市", "安床", "掘井"]},
        "定": {"yi": ["嫁娶", "動土", "安床", "造屋", "納財", "栽種"], "ji": ["訴訟", "出行", "赴任", "詞訟"]},
        "執": {"yi": ["捕捉", "開渠", "修造", "捕捉"], "ji": ["嫁娶", "開市", "安葬", "移徙"]},
        "破": {"yi": ["求醫", "治病", "破屋", "壞垣"], "ji": ["諸事不宜", "嫁娶", "開市", "移徙", "安床"]},
        "危": {"yi": ["安床", "入宅", "祭祀", "祈福", "求嗣"], "ji": ["登山", "乘船", "遠行", "開倉"]},
        "成": {"yi": ["入學", "開市", "出行", "嫁娶", "移徙", "上樑", "求財"], "ji": ["詞訟", "安葬", "針灸"]},
        "收": {"yi": ["納財", "開市", "交易", "入學", "求醫"], "ji": ["嫁娶", "造酒", "安葬", "行喪"]},
        "開": {"yi": ["祭祀", "祈福", "開光", "入宅", "出行", "開市", "動土", "求嗣"], "ji": ["安葬", "行喪", "破土"]},
        "閉": {"yi": ["築堤", "補垣", "塞穴"], "ji": ["開市", "出行", "嫁娶", "開倉", "安床"]},
    }
    qinglong = ["青龍", "明堂", "天刑", "朱雀", "金匱", "天德", "白虎", "玉堂", "天牢", "玄武", "司命", "勾陳"]
    qinglong_huang = ["青龍", "明堂", "金匱", "天德", "玉堂", "司命"]
    qinglong_start = {
        "寅": "子", "申": "子", "卯": "寅", "酉": "寅", "辰": "辰", "戌": "辰",
        "巳": "午", "亥": "午", "子": "申", "午": "申", "丑": "戌", "未": "戌",
    }
    qinglong_hint = {
        "青龍": "利有攸往、求謀可成", "明堂": "利見貴人、諸事可為",
        "天刑": "忌詞訟、刑罰", "朱雀": "防口舌文書糾紛",
        "金匱": "利財帛契約納財", "天德": "百事可為、化煞",
        "白虎": "忌爭鬥血光", "玉堂": "利文事見貴安居",
        "天牢": "忌拘束糾紛", "玄武": "防盜失欺瞞",
        "司命": "利祈福安神", "勾陳": "忌田土糾纏",
    }
    # 月德／天德（協紀通用）
    yue_de = {"寅": "丙", "午": "丙", "戌": "丙", "申": "壬", "子": "壬", "辰": "壬",
              "亥": "甲", "卯": "甲", "未": "甲", "巳": "庚", "酉": "庚", "丑": "庚"}
    tian_de = {
        "寅": "丁", "卯": "坤", "辰": "壬", "巳": "辛", "午": "乾", "未": "甲",
        "申": "癸", "酉": "艮", "戌": "丙", "亥": "乙", "子": "巽", "丑": "庚",
    }
    chong = dict(zip(DZ, ["午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳"]))
    sha = {"子": "南", "午": "北", "卯": "西", "酉": "東", "寅": "南", "申": "北",
           "巳": "西", "亥": "東", "辰": "南", "戌": "北", "丑": "東", "未": "西"}
    # 日干喜神／財神／福神簡表
    xi = {"甲": "東北", "乙": "西北", "丙": "西南", "丁": "正南", "戊": "東南",
          "己": "東北", "庚": "西北", "辛": "西南", "壬": "正南", "癸": "東南"}
    fu = {"甲": "東南", "乙": "正東", "丙": "北", "丁": "南", "戊": "東南",
          "己": "正東", "庚": "北", "辛": "南", "壬": "東南", "癸": "正東"}
    cai = {"甲": "東北", "乙": "正東", "丙": "西南", "丁": "正西", "戊": "東北",
           "己": "正東", "庚": "西南", "辛": "正西", "壬": "東北", "癸": "正東"}
    pengzu = {
        "甲": "甲不開倉財物耗散", "乙": "乙不栽植千株不長", "丙": "丙不修灶必見災殃",
        "丁": "丁不剃頭頭必生瘡", "戊": "戊不受田田主不祥", "己": "己不破券二比並亡",
        "庚": "庚不經絡織機虛張", "辛": "辛不合醬主人不嘗", "壬": "壬不泱水更難提防",
        "癸": "癸不詞訟理弱敵強",
        "子": "子不問卜自惹禍殃", "丑": "丑不冠帶主不還鄉", "寅": "寅不祭祀神鬼不嘗",
        "卯": "卯不穿井水泉不香", "辰": "辰不哭泣必主重喪", "巳": "巳不遠行財物伏藏",
        "午": "午不苫蓋屋主更張", "未": "未不服藥毒氣入腸", "申": "申不安床鬼祟入房",
        "酉": "酉不會客醉坐顛狂", "戌": "戌不吃犬作怪上床", "亥": "亥不嫁娶不利新郎",
    }
    # 五行旺相休囚死（以月支季節）
    season_wx = {
        "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土",
        "申": "金", "酉": "金", "戌": "土", "亥": "水", "子": "水", "丑": "土",
    }
    # 旺相休囚死順序：當令為旺，我生為相，生我為休，克我為囚，我克為死
    order = ["木", "火", "土", "金", "水"]

    def wangxiang(month_zhi: str):
        wang = season_wx[month_zhi]
        i = order.index(wang)
        return {
            "旺": wang,
            "相": order[(i + 1) % 5],
            "休": order[(i + 4) % 5],
            "囚": order[(i + 3) % 5],
            "死": order[(i + 2) % 5],
        }

    wangxiang_table = {z: wangxiang(z) for z in DZ}

    return {
        "jianchu": jianchu,
        "jianchuHuang": jianchu_huang,
        "jianchuYiji": jianchu_yiji,
        "qinglong": qinglong,
        "qinglongHuang": qinglong_huang,
        "qinglongStart": qinglong_start,
        "qinglongHint": qinglong_hint,
        "yueDe": yue_de,
        "tianDe": tian_de,
        "chong": chong,
        "sha": sha,
        "xiShen": xi,
        "fuShen": fu,
        "caiShen": cai,
        "pengzu": pengzu,
        "wangxiang": wangxiang_table,
        "wuxingGan": WX_G,
        "wuxingZhi": WX_Z,
        "tianGan": TG,
        "diZhi": DZ,
        "shengXiao": SX,
    }


def build_qimen_tables():
    """奇門日家／拆補：陰陽遁局數（與開源 kinqimen 歌訣一致）。"""
    yang_ju = {
        "冬至": [1, 7, 4], "驚蟄": [1, 7, 4], "小寒": [2, 8, 5],
        "大寒": [3, 9, 6], "春分": [3, 9, 6], "雨水": [9, 6, 3],
        "清明": [4, 1, 7], "立夏": [4, 1, 7], "穀雨": [5, 2, 8],
        "小滿": [5, 2, 8], "立春": [8, 5, 2], "芒種": [6, 3, 9],
    }
    yin_ju = {
        "夏至": [9, 3, 6], "白露": [9, 3, 6], "小暑": [8, 2, 5],
        "大暑": [7, 1, 4], "秋分": [7, 1, 4], "立秋": [2, 5, 8],
        "處暑": [1, 4, 7], "寒露": [6, 9, 3], "立冬": [6, 9, 3],
        "霜降": [5, 8, 2], "小雪": [5, 8, 2], "大雪": [4, 7, 1],
    }
    yang_set = set(yang_ju.keys())
    # 九星、八門、八神、三奇六儀
    jiu_xing = ["", "天蓬", "天芮", "天沖", "天輔", "天禽", "天心", "天柱", "天任", "天英"]
    ba_men = ["休", "生", "傷", "杜", "景", "死", "驚", "開"]
    men_path_yang = [1, 8, 3, 4, 9, 2, 7, 6]
    men_path_yin = [9, 7, 6, 1, 8, 3, 4, 2]
    ba_shen_yang = ["值符", "螣蛇", "太陰", "六合", "白虎", "玄武", "九地", "九天"]
    ba_shen_yin = ["值符", "螣蛇", "太陰", "六合", "勾陳", "朱雀", "九地", "九天"]
    # 地支→宮
    zhi_gong = {
        "子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4,
        "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6,
    }
    gong_dir = {1: "北", 2: "西南", 3: "東", 4: "東南", 5: "中", 6: "西北", 7: "西", 8: "東北", 9: "南"}
    gong_name = {1: "坎一", 2: "坤二", 3: "震三", 4: "巽四", 5: "中五", 6: "乾六", 7: "兌七", 8: "艮八", 9: "離九"}
    # 日家格局斷語（開源常見簡表）
    pattern_tips = {
        "開門": "利開張、求職、見貴、出行",
        "休門": "利休息、養病、求安",
        "生門": "利求財、置產、求醫（生機）",
        "傷門": "忌鬥毆、手術非急；可捕捉競爭",
        "杜門": "利隱藏、技術、避災；忌張揚",
        "景門": "利考試、文書、傳媒",
        "死門": "忌嫁娶動土；可弔唁決絕",
        "驚門": "忌驚恐官非；可刑偵口才",
    }
    return {
        "yangJu": yang_ju,
        "yinJu": yin_ju,
        "yangJieqi": sorted(yang_set),
        "jiuXing": jiu_xing,
        "baMen": ba_men,
        "menPathYang": men_path_yang,
        "menPathYin": men_path_yin,
        "baShenYang": ba_shen_yang,
        "baShenYin": ba_shen_yin,
        "zhiGong": zhi_gong,
        "gongDir": gong_dir,
        "gongName": gong_name,
        "yiOrder": ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"],
        "patternTips": pattern_tips,
        "xunShouYi": ["戊", "己", "庚", "辛", "壬", "癸"],
        "xunShouName": ["甲子", "甲戌", "甲申", "甲午", "甲辰", "甲寅"],
    }


def build_liuren_tables():
    """大六壬：月將、貴人、干寄宮、天將（開源壬學通行表）。"""
    yuejiang_names = {
        "子": "神後", "丑": "大吉", "寅": "功曹", "卯": "太沖",
        "辰": "天罡", "巳": "太乙", "午": "勝光", "未": "小吉",
        "申": "傳送", "酉": "從魁", "戌": "河魁", "亥": "登明",
    }
    # 中氣換將
    yuejiang_by_zhongqi = [
        ("雨水", "亥"), ("春分", "戌"), ("穀雨", "酉"), ("小滿", "申"),
        ("夏至", "未"), ("大暑", "午"), ("處暑", "巳"), ("秋分", "辰"),
        ("霜降", "卯"), ("小雪", "寅"), ("冬至", "丑"), ("大寒", "子"),
    ]
    gan_jigong = {
        "甲": "寅", "乙": "辰", "丙": "巳", "丁": "未", "戊": "巳",
        "己": "未", "庚": "申", "辛": "戌", "壬": "亥", "癸": "丑",
    }
    guiren_day = {"甲": "丑", "戊": "丑", "庚": "丑", "乙": "子", "己": "子",
                  "丙": "亥", "丁": "亥", "壬": "巳", "癸": "巳", "辛": "午"}
    guiren_night = {"甲": "未", "戊": "未", "庚": "未", "乙": "申", "己": "申",
                    "丙": "酉", "丁": "酉", "壬": "卯", "癸": "卯", "辛": "寅"}
    tianjiang = ["貴人", "螣蛇", "朱雀", "六合", "勾陳", "青龍", "天空", "白虎", "太常", "玄武", "太陰", "天后"]
    # 三傳取法提示
    method_tips = {
        "重審（下賊上）": "下賊上為用，事情由內而發，宜先處理隱患再推進",
        "元首（上克下）": "上克下為用，外力主導，宜順勢而為、借力使力",
        "比用（多賊）": "多課相比，取與日干相比和者，宜擇一正途專攻",
        "比用（多克）": "多克取比，勿三心二意",
        "遙克": "遠克為用，宜遠交近攻、借遠力",
        "伏吟": "伏吟不動，宜守不宜攻，防重複糾結",
        "返吟": "返吟多反覆，合約行程須再三確認",
        "昂星（簡）": "無克取昂星，宜觀望後定",
    }
    return {
        "yuejiangNames": yuejiang_names,
        "yuejiangByZhongqi": [{"jie": a, "zhi": b} for a, b in yuejiang_by_zhongqi],
        "ganJigong": gan_jigong,
        "guirenDay": guiren_day,
        "guirenNight": guiren_night,
        "tianjiang": tianjiang,
        "methodTips": method_tips,
        "liuhe": {"子": "丑", "丑": "子", "寅": "亥", "亥": "寅", "卯": "戌", "戌": "卯",
                  "辰": "酉", "酉": "辰", "巳": "申", "申": "巳", "午": "未", "未": "午"},
        "liuhai": {"子": "未", "未": "子", "丑": "午", "午": "丑", "寅": "巳", "巳": "寅",
                   "卯": "辰", "辰": "卯", "申": "亥", "亥": "申", "酉": "戌", "戌": "酉"},
    }


def build_personal_profiles():
    """兩位命主：八字要點＋喜用＋與流日互動權重（開源子平規則）。"""
    # 1985-08-28 辰時 → 己亥日 戊辰時；年乙丑（立春後）
    # 1995-11-08 寅時 → 癸卯日 甲寅時；年乙亥
    return {
        "profiles": [
            {
                "id": "p1985",
                "label": "1985.08.28",
                "birthSolar": "1985-08-28",
                "birthHour": "辰",
                "gender": "male",
                "genderLabel": "男",
                "dayMaster": "己",
                "dayMasterWx": "土",
                "yearZhi": "丑",
                "yearGan": "乙",
                "xiao": "牛",
                # 己土日主：喜火暖土、喜土帮身、喜金洩秀（簡化喜用）
                "xiYong": ["火", "土", "金"],
                "jiYong": ["木", "水"],
                "luckyColors": ["黃", "棕", "紅", "金"],
                "luckyNums": [5, 6, 8],
                "constellation": "處女座",
                "traitDo": "檢查細節、校對文件、優化流程",
                "traitDont": "完美主義過度苛責",
                "wxTone": "己土",
                "summaryTone": "處女座",
                "hourNote": "辰時土氣，宜穩重務實",
            },
            {
                "id": "p1995",
                "label": "1995.11.08",
                "birthSolar": "1995-11-08",
                "birthHour": "寅",
                "gender": "female",
                "genderLabel": "女",
                "dayMaster": "癸",
                "dayMasterWx": "水",
                "yearZhi": "亥",
                "yearGan": "乙",
                "xiao": "豬",
                # 癸水日主：喜金生水、喜水帮身、喜木洩秀
                "xiYong": ["金", "水", "木"],
                "jiYong": ["土", "火"],
                "luckyColors": ["黑", "深藍", "金", "綠"],
                "luckyNums": [1, 3, 6],
                "constellation": "天蠍座",
                "traitDo": "深度思考、獨處充電、溫柔表達",
                "traitDont": "悶情緒、過度猜疑",
                "wxTone": "癸水",
                "summaryTone": "天蠍座",
                "hourNote": "寅時木氣，宜條理表達情感",
            },
        ],
        # 日干對日主：十神（以日主為我）
        # 同我比肩、我生食傷、我克財、克我官殺、生我印
        "shishenRules": {
            "比肩": "同黨助力，宜合作亦防爭功",
            "劫財": "争夺資源，防破財口角",
            "食神": "表達才藝，利進修創作",
            "傷官": "聰慧外露，慎頂撞權威",
            "正財": "正當收入，宜務實理財",
            "偏財": "橫財機會，可小試勿梭哈",
            "正官": "責任規範，利職涯考試",
            "七殺": "壓力挑戰，宜轉壓力為動力",
            "正印": "貴人學業，利進修靠山",
            "偏印": "偏門靈感，防多學不精",
        },
        # 五行生克 → 十神（日主五行 vs 流日干五行 + 陰陽）
        "actionByShishen": {
            "比肩": "宜結伴共事、分工明確",
            "劫財": "少借貸擔保、防臨時破財",
            "食神": "宜寫作分享、輕鬆表達",
            "傷官": "創意可發，言談宜柔",
            "正財": "宜記帳收款、穩健工作",
            "偏財": "副業機會，小額嘗試即可",
            "正官": "宜見主管、守規則、辦公文",
            "七殺": "高壓日，運動紓壓、少硬碰",
            "正印": "宜學習進修、求助長輩",
            "偏印": "靈感日，適合研究偏門技能",
        },
    }


def build_score_weights():
    """分析系統權重：讓天時（節氣旺衰、建除、神煞、奇門、六壬）進入評分。"""
    return {
        "jianchu": {
            "建": 2, "除": 3, "滿": 6, "平": 0, "定": 7, "執": 1,
            "破": -14, "危": -3, "成": 10, "收": 5, "開": 9, "閉": -8,
        },
        "qinglong": {
            "青龍": 10, "明堂": 9, "金匱": 8, "天德": 10, "玉堂": 7, "司命": 6,
            "天刑": -10, "朱雀": -7, "白虎": -12, "天牢": -9, "玄武": -6, "勾陳": -5,
        },
        "liurenMethod": {
            "重審（下賊上）": 6, "元首（上克下）": 5, "比用（多賊）": 2, "比用（多克）": 2,
            "遙克": 1, "伏吟": -8, "返吟": -6, "昂星（簡）": 0,
        },
        "xiYongHit": 8,
        "jiYongHit": -10,
        "wang": 6,
        "xiang": 3,
        "xiu": 0,
        "qiu": -4,
        "si": -7,
        "he": 12,
        "chong": -14,
        "hai": -10,
        "xing": -6,
        "qimenOpenSheng": 7,
        "qimenSiJing": -5,
    }


def main():
    db = {
        "meta": {
            "name": "daily-huangli-core-db",
            "version": "1.0.0",
            "maxSizeHintMB": 500,
            "license": "Public-domain traditional tables + open algorithm ports (non-copyrightable facts/rules)",
            "sources": [
                "Traditional Chinese almanac tables (建除/黃黑道/神煞) as used in open 黃曆 projects",
                "Lunar year bit table (1900-2100) shared by open lunar libs (e.g. 6tail/lunar lineage)",
                "Qimen chaibu ju songs as in open qimen projects (e.g. kinqimen-compatible tables)",
                "Liu Ren yuejiang/guiren/jigong traditional tables (open liuren ports)",
                "Ziping day-master relations for personal daily fortune",
            ],
            "jieqiRange": [1980, 2040],
            "note": "精簡結構化知識庫，非爬取整站；演算法在前端結合本庫即時推算。",
        },
        "jieqi": build_jieqi_index(1980, 2040),
        "jieqiNames": JIEQI_NAMES,
        "jieqiYuejian": JIEQI_YUEJIAN,
        "lunarInfo": LUNAR_INFO,  # 數字陣列，體積極小
        "huangli": build_huangli_tables(),
        "qimen": build_qimen_tables(),
        "liuren": build_liuren_tables(),
        "personal": build_personal_profiles(),
        "weights": build_score_weights(),
        # 皇極六十四卦讖言+白話（保留既有品質）
        "huangji": {
            "gua64": [
                "乾為天", "坤為地", "水雷屯", "山水蒙", "水天需", "天水訟", "地水師", "水地比",
                "風天小畜", "天澤履", "地天泰", "天地否", "天火同人", "火天大有", "地山謙", "雷地豫",
                "澤雷隨", "山風蠱", "地澤臨", "風地觀", "火雷噬嗑", "山火賁", "山地剝", "地雷復",
                "天雷無妄", "山天大畜", "山雷頤", "澤風大過", "坎為水", "離為火", "澤山咸", "雷風恆",
                "天山遯", "雷天大壯", "火地晉", "地火明夷", "風火家人", "火澤睽", "水山蹇", "雷水解",
                "山澤損", "風雷益", "澤天夬", "天風姤", "澤地萃", "地風升", "澤水困", "水風井",
                "澤火革", "火風鼎", "震為雷", "艮為山", "風山漸", "雷澤歸妹", "雷火豐", "火山旅",
                "巽為風", "兌為澤", "風水渙", "水澤節", "風澤中孚", "雷山小過", "水火既濟", "火水未濟",
            ],
        },
    }

    # 寫入 JSON
    json_path = DATA / "core-db.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))

    # 寫入 JS bundle（供 GitHub Pages 靜態載入）
    js_path = LIB / "huangli-db.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("/* Auto-generated by scripts/build_db.py — do not edit by hand */\n")
        f.write("window.HUANGLI_DB = ")
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    size_json = json_path.stat().st_size
    size_js = js_path.stat().st_size
    total = size_json + size_js
    report = {
        "core-db.json_bytes": size_json,
        "huangli-db.js_bytes": size_js,
        "total_bytes": total,
        "total_MB": round(total / (1024 * 1024), 3),
        "under_500MB": total < 500 * 1024 * 1024,
        "jieqi_years": len(db["jieqi"]),
    }
    with open(DATA / "BUILD_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("OK →", json_path, js_path)


if __name__ == "__main__":
    main()
