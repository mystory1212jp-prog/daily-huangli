#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
確定性計算層：以 lunar_python（開源）精算黃曆日課＋個人八字互動。
語意映射層資料：十神→現代場景、神煞→情緒能量、節氣→養生。

輸出：
  data/mapping-db.json
  data/personal-bazi.json
  data/daily-facts-YYYY.json  (按年拆分，體積可控)
  lib/personal-system.js      (映射＋語意轉譯，供前端)
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

from lunar_python import Solar
from lunar_python.util import LunarUtil

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LIB = ROOT / "lib"
DATA.mkdir(exist_ok=True)
LIB.mkdir(exist_ok=True)

# 八節（四絕四離相關）
BA_JIE = {"立春", "立夏", "立秋", "立冬", "春分", "夏至", "秋分", "冬至"}
SI_JUE = {"立春", "立夏", "立秋", "立冬"}
SI_LI = {"春分", "夏至", "秋分", "冬至"}

# 傳統地支刑衝合害（確定性邏輯寫死）
CHONG = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}
LIUHE = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}
LIUHAI = {
    "子": "未", "未": "子", "丑": "午", "午": "丑",
    "寅": "巳", "巳": "寅", "卯": "辰", "辰": "卯",
    "申": "亥", "亥": "申", "酉": "戌", "戌": "酉",
}
# 三刑：寅巳申、丑戌未、子卯、辰午酉亥自刑簡化
SANXING_GROUPS = [
    {"寅", "巳", "申"},
    {"丑", "戌", "未"},
    {"子", "卯"},
]
ZIXING = {"辰", "午", "酉", "亥"}

WX = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}
WX_Z = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
SX = list("鼠牛虎兔龍蛇馬羊猴雞狗豬")
DZ = list("子丑寅卯辰巳午未申酉戌亥")

# lunar_python 多為簡體，前端繁體 UI 需對齊（單字表）
S2T = str.maketrans({
    "执": "執", "满": "滿", "开": "開", "闭": "閉",
    "黄": "黃", "龙": "龍", "贵": "貴", "禄": "祿", "库": "庫",
    "马": "馬", "鸣": "鳴", "对": "對", "时": "時", "败": "敗",
    "丧": "喪", "门": "門", "岁": "歲", "斋": "齋",
    "启": "啟", "钻": "鑽", "彻": "徹", "扫": "掃", "舍": "捨",
    "粪": "糞", "厕": "廁", "阳": "陽", "阴": "陰", "杀": "殺",
    "灾": "災", "恶": "惡", "剑": "劍", "锋": "鋒",
    "为": "為", "与": "與", "无": "無", "东": "東",
    "宠": "寵", "帅": "帥", "进": "進", "产": "產", "纳": "納",
    "财": "財", "词": "詞", "讼": "訟", "远": "遠", "动": "動",
    "盖": "蓋", "竖": "豎", "种": "種", "养": "養", "礼": "禮",
    "仪": "儀", "订": "訂", "会": "會", "亲": "親", "医": "醫",
    "疗": "療", "坏": "壞", "涂": "塗", "货": "貨", "酝": "醞",
    "酿": "釀", "经": "經", "络": "絡", "猎": "獵", "渔": "漁",
    "结": "結", "补": "補", "断": "斷", "蚁": "蟻", "筑": "築",
    "硙": "磑", "绘": "繪", "齐": "齊", "采": "採", "习": "習",
    "艺": "藝", "坟": "墳", "谢": "謝", "诸": "諸", "机": "機",
    "械": "械", "车": "車", "复": "復", "虚": "虛", "飞": "飛",
    "驿": "驛", "华": "華", "红": "紅", "鸾": "鸞", "陈": "陳",
    "惊": "驚", "蛰": "蟄", "谷": "穀", "处": "處", "种": "種",
    "匮": "匱", "敛": "殮", "伤": "傷", "偏": "偏", "正": "正",
    "印": "印", "比": "比", "劫": "劫", "食": "食", "神": "神",
    "官": "官", "杀": "殺", "肩": "肩", "财": "財",
})


def to_trad(s: str) -> str:
    if not s:
        return s
    # 多字詞先替換
    multi = {
        "鸣吠对": "鳴吠對", "大时": "大時", "大败": "大敗",
        "开市": "開市", "出火": "出火", "入宅": "入宅", "移徙": "移徙",
        "斋醮": "齋醮", "启钻": "啟攢", "破土": "破土",
        "整手足甲": "整手足甲", "安床": "安床", "沐浴": "沐浴",
        "入殓": "入殮", "移柩": "移柩", "嫁娶": "嫁娶",
        "作灶": "作灶", "安门": "安門", "伐木": "伐木",
        "黄道": "黃道", "黑道": "黑道", "天乙贵人": "天乙貴人",
        "月德合": "月德合", "天德合": "天德合",
        "金匮": "金匱", "玉堂": "玉堂", "明堂": "明堂",
        "天牢": "天牢", "玄武": "玄武", "白虎": "白虎",
        "朱雀": "朱雀", "勾陈": "勾陳", "青龙": "青龍",
        "天刑": "天刑", "司命": "司命", "咸池": "咸池",
        "小耗": "小耗", "大耗": "大耗", "月害": "月害",
        "月空": "月空", "金堂": "金堂", "解神": "解神",
        "驿马": "驛馬", "华盖": "華蓋", "文昌": "文昌",
        "羊刃": "羊刃", "飞刃": "飛刃", "灾煞": "災煞",
        "劫煞": "劫煞", "岁破": "歲破", "月破": "月破",
        "天火": "天火", "五虚": "五虛", "血忌": "血忌",
        "重日": "重日", "复日": "復日", "阴德": "陰德",
        "三合": "三合", "天喜": "天喜", "红鸾": "紅鸞",
        "天德": "天德", "月德": "月德",
        "立春": "立春", "雨水": "雨水", "惊蛰": "驚蟄",
        "春分": "春分", "清明": "清明", "谷雨": "穀雨",
        "立夏": "立夏", "小满": "小滿", "芒种": "芒種",
        "夏至": "夏至", "小暑": "小暑", "大暑": "大暑",
        "立秋": "立秋", "处暑": "處暑", "白露": "白露",
        "秋分": "秋分", "寒露": "寒露", "霜降": "霜降",
        "立冬": "立冬", "小雪": "小雪", "大雪": "大雪",
        "冬至": "冬至", "小寒": "小寒", "大寒": "大寒",
        "祭祀": "祭祀", "祈福": "祈福", "解除": "解除",
        "出行": "出行", "求嗣": "求嗣", "开光": "開光",
        "塑绘": "塑繪", "齐醮": "齊醮", "订盟": "訂盟",
        "纳采": "納采", "冠笄": "冠笄", "裁衣": "裁衣",
        "会亲友": "會親友", "进人口": "進人口", "纳财": "納財",
        "捕捉": "捕捉", "畋猎": "畋獵", "习艺": "習藝",
        "经络": "經絡", "酝酿": "醞釀", "开仓": "開倉",
        "出货财": "出貨財", "安机械": "安機械", "造车器": "造車器",
        "经络": "經絡", "竖柱上梁": "豎柱上梁",
        "平治道涂": "平治道塗", "修造": "修造", "动土": "動土",
        "上梁": "上梁", "安葬": "安葬", "修坟": "修墳",
        "立碑": "立碑", "谢土": "謝土", "斋醮": "齋醮",
        "词讼": "詞訟", "远行": "遠行", "诸事不宜": "諸事不宜",
    }
    out = s
    for a, b in multi.items():
        out = out.replace(a, b)
    return out.translate(S2T)


def trad_list(xs) -> list:
    return [to_trad(x) if isinstance(x, str) else x for x in (xs or [])]


def zhi_relations(my_zhi: str, day_zhi: str) -> list[dict]:
    rels = []
    if my_zhi == day_zhi:
        rels.append({"type": "值", "detail": f"日支同本命{my_zhi}", "score": 4})
    if CHONG.get(my_zhi) == day_zhi:
        rels.append({"type": "冲", "detail": f"{my_zhi}冲{day_zhi}", "score": -14})
    if LIUHE.get(my_zhi) == day_zhi:
        rels.append({"type": "合", "detail": f"{my_zhi}合{day_zhi}", "score": 12})
    if LIUHAI.get(my_zhi) == day_zhi:
        rels.append({"type": "害", "detail": f"{my_zhi}害{day_zhi}", "score": -10})
    for g in SANXING_GROUPS:
        if my_zhi in g and day_zhi in g and my_zhi != day_zhi:
            rels.append({"type": "刑", "detail": f"{my_zhi}与{day_zhi}相刑", "score": -8})
            break
    if my_zhi in ZIXING and my_zhi == day_zhi:
        rels.append({"type": "自刑", "detail": f"{my_zhi}自刑", "score": -5})
    if not rels:
        rels.append({"type": "平", "detail": "无明显刑冲合害", "score": 1})
    return rels


def shi_shen(day_master: str, gan: str) -> str:
    key = day_master + gan
    return LunarUtil.SHI_SHEN.get(key, "比肩")


def build_mapping_db() -> dict:
    """三維度映射庫（語意轉譯層用）。"""
    return {
        "meta": {
            "name": "personal-mapping-db",
            "version": "2.0.0",
            "architecture": "deterministic + semantic mapping (offline template; JSON-ready for Batch LLM)",
        },
        # 1) 十神 → 現代生活場景
        "tenGodsScenarios": {
            "比肩": {
                "themes": ["團隊協作", "同儕競爭", "自我主張"],
                "work": ["分工對齊", "開源社群交流", "pair programming"],
                "life": ["與友人聚會", "運動結伴"],
                "caution": ["控制衝動消費（如升級硬體）", "避免與同事搶功"],
            },
            "劫財": {
                "themes": ["資源爭奪", "破財風險", "衝動"],
                "work": ["協調資源分配", "慎接非職責外請求"],
                "life": ["少衝動下單", "慎與人合夥金流"],
                "caution": ["避免臨時大額消費", "不輕易擔保借貸"],
            },
            "食神": {
                "themes": ["研發產出", "享受表達", "才藝"],
                "work": ["寫 Code 解 Bug", "技術分享", "文件撰寫"],
                "life": ["享受美食", "輕鬆創作", "嗜好時間"],
                "caution": ["別只玩樂忘進度", "輸出要有交付節點"],
            },
            "傷官": {
                "themes": ["企劃提案", "創新批判", "表現慾"],
                "work": ["企劃提案", "重構優化", "簡報表達"],
                "life": ["創意動手", "風格表達"],
                "caution": ["言談避免頂撞主管", "批評要給替代方案"],
            },
            "正財": {
                "themes": ["正當收入", "務實理財", "工作酬勞"],
                "work": ["收款對帳", "穩健推進本職", "記帳結案"],
                "life": ["規劃預算", "生活開銷盤點"],
                "caution": ["別好高騖遠", "少碰高風險投資"],
            },
            "偏財": {
                "themes": ["橫財機會", "副業", "人脈財"],
                "work": ["副業嘗試", "商務交際", "專案獎金機會"],
                "life": ["人脈維護", "小額試水機會"],
                "caution": ["可小試勿梭哈", "設停損"],
            },
            "正官": {
                "themes": ["專案管理", "規範責任", "體制內表現"],
                "work": ["專案管理", "行政合規", "與主管對齊 KPI"],
                "life": ["守規矩行程", "公眾形象"],
                "caution": ["壓力來自規範", "別遲到違規"],
            },
            "七殺": {
                "themes": ["高壓決策", "挑戰", "競爭"],
                "work": ["高壓決策", "處理客訴／危機", "挑戰性任務"],
                "life": ["高強度運動洩壓", "少硬碰硬衝突"],
                "caution": ["情緒易衝", "部署上線需雙重檢查"],
            },
            "正印": {
                "themes": ["學習進修", "貴人靠山", "覆核"],
                "work": ["系統架構學習", "證照考試準備", "覆核合約帳務"],
                "life": ["閱讀文獻", "求助前輩"],
                "caution": ["別過度依賴他人", "學習要落地"],
            },
            "偏印": {
                "themes": ["偏門靈感", "研究", "非主流技能"],
                "work": ["研究冷門技術", "讀文件挖細節", "獨立分析"],
                "life": ["獨處充電", "興趣鑽研"],
                "caution": ["防多學不精", "靈感需整理成產出"],
            },
        },
        # 2) 神煞 → 情緒／能量
        "shenShaEnergy": {
            "天乙貴人": {"energy": "得貴人", "modern": "遇技術瓶頸易得開源社群或前輩指點", "tone": "吉"},
            "天德": {"energy": "化解", "modern": "出錯較易被原諒，適合補救與協調", "tone": "吉"},
            "月德": {"energy": "平和", "modern": "氣氛較順，適合溝通與收斂成果", "tone": "吉"},
            "天德合": {"energy": "助緣", "modern": "合作與文書較易過關", "tone": "吉"},
            "月德合": {"energy": "助緣", "modern": "人際潤滑，適合請客維繫", "tone": "吉"},
            "天喜": {"energy": "喜慶", "modern": "適合慶祝小里程碑、對外展示成果", "tone": "吉"},
            "紅鸞": {"energy": "桃花", "modern": "社交活躍，注意公私分明", "tone": "中"},
            "文昌": {"energy": "文思", "modern": "適合寫文件、考試、簡報", "tone": "吉"},
            "驛馬": {"energy": "動盪", "modern": "奔波出差、行程多變，預留緩衝", "tone": "中"},
            "華蓋": {"energy": "孤清", "modern": "適合獨處深工，少湊熱鬧", "tone": "中"},
            "羊刃": {"energy": "急躁鋒利", "modern": "情緒易急，伺服器部署或網路線材操作需避免粗心", "tone": "凶"},
            "飛刃": {"energy": "衝動", "modern": "手腳易快易錯，剪線、搬機、動刀事前確認", "tone": "凶"},
            "災煞": {"energy": "驚擾", "modern": "少爭辯、少試險操作，注意交通", "tone": "凶"},
            "劫煞": {"energy": "耗損", "modern": "防臨時破財與資料遺失，先備份", "tone": "凶"},
            "歲破": {"energy": "動盪", "modern": "大事緩決，避免硬推變革", "tone": "凶"},
            "月破": {"energy": "耗泄", "modern": "不宜開張簽約，適合收尾清理", "tone": "凶"},
            "大耗": {"energy": "破財", "modern": "控管支出，少升級非必要設備", "tone": "凶"},
            "天火": {"energy": "急火", "modern": "防火防災，少熬夜動肝火", "tone": "凶"},
            "五虛": {"energy": "虛弱", "modern": "體力一般，深度工作穿插休息", "tone": "凶"},
            "血忌": {"energy": "血光", "modern": "非必要不做侵入性醫療、激烈運動", "tone": "凶"},
            "重日": {"energy": "反覆", "modern": "文件與設定易重複改動，做版本管理", "tone": "中"},
            "復日": {"energy": "反覆", "modern": "舊案重啟，適合複盤非新開", "tone": "中"},
            "陰德": {"energy": "暗助", "modern": "默默做好事有回報，適合幕後支援", "tone": "吉"},
            "三合": {"energy": "聚合", "modern": "團隊氣場合，適合開會對齊", "tone": "吉"},
            "明堂": {"energy": "黃道開朗", "modern": "適合見人提案、公開場合", "tone": "吉"},
            "金匱": {"energy": "財庫", "modern": "適合談錢、對帳、簽合理合約", "tone": "吉"},
            "玉堂": {"energy": "文貴", "modern": "適合文書、學習、面試", "tone": "吉"},
            "司命": {"energy": "安神", "modern": "適合祈福靜心、整理待辦", "tone": "吉"},
            "天刑": {"energy": "刑忌", "modern": "少爭執訴訟，言詞謹慎", "tone": "凶"},
            "朱雀": {"energy": "口舌", "modern": "郵件／訊息先冷卻再送，防口角", "tone": "凶"},
            "白虎": {"energy": "剛烈", "modern": "防衝突與意外，操作硬體要穩", "tone": "凶"},
            "天牢": {"energy": "拘滯", "modern": "易卡關，先解鎖阻塞再開工", "tone": "凶"},
            "玄武": {"energy": "暗耗", "modern": "防詐騙釣魚、檢查權限與備份", "tone": "凶"},
            "勾陳": {"energy": "糾纏", "modern": "舊案拖延，今日清一件積壓", "tone": "凶"},
            "青龍": {"energy": "生發", "modern": "適合開啟新任務、求進展", "tone": "吉"},
            "默认吉": {"energy": "平順", "modern": "氣場尚可，按計畫執行", "tone": "吉"},
            "默认凶": {"energy": "收斂", "modern": "少開新局，以守成為主", "tone": "凶"},
        },
        # 3) 節氣 × 五行養生（中醫）
        "solarTermTcm": {
            "立春": {"wx": "木", "zang": "肝膽", "advice": "舒展筋骨、少熬夜；飲食可偏綠葉與略酸以疏肝"},
            "雨水": {"wx": "木", "zang": "肝", "advice": "潤燥護肝，作息規律，適合溫和拉伸"},
            "驚蟄": {"wx": "木", "zang": "肝", "advice": "氣機升發，宜早起活動，避免暴怒"},
            "春分": {"wx": "木", "zang": "肝膽", "advice": "陰陽平衡，作息勿極端，飲食清淡"},
            "清明": {"wx": "木", "zang": "肝", "advice": "外出踏青舒肝，防過敏，少油膩"},
            "穀雨": {"wx": "土濕", "zang": "脾", "advice": "祛濕健脾，少生冷，可紅豆薏仁類"},
            "立夏": {"wx": "火", "zang": "心", "advice": "養心安神，少大怒大喜，午間可小憩"},
            "小滿": {"wx": "火濕", "zang": "心脾", "advice": "防濕熱，清淡飲食，適度出汗"},
            "芒種": {"wx": "火", "zang": "心", "advice": "忙中留白，補水，避免連續高壓無休"},
            "夏至": {"wx": "火", "zang": "心", "advice": "心火易旺，晚間少螢幕，可苦瓜綠豆清熱"},
            "小暑": {"wx": "火土", "zang": "心脾", "advice": "防中暑，補電解質，工作環境通風"},
            "大暑": {"wx": "火", "zang": "心", "advice": "最熱時段減少戶外奔波，午休養神"},
            "立秋": {"wx": "金", "zang": "肺", "advice": "潤肺防燥，少辛辣，早睡早起"},
            "處暑": {"wx": "金", "zang": "肺", "advice": "餘熱未消，防秋燥咳嗽，多潤燥"},
            "白露": {"wx": "金", "zang": "肺", "advice": "露重易寒，早晚添衣，護呼吸道"},
            "秋分": {"wx": "金", "zang": "肺", "advice": "收斂神氣，適合複盤與整理，少過度發散"},
            "寒露": {"wx": "金水", "zang": "肺腎", "advice": "防寒潤燥，可溫補，注意睡眠"},
            "霜降": {"wx": "土金", "zang": "脾胃肺", "advice": "溫暖飲食，護胃，減少生冷"},
            "立冬": {"wx": "水", "zang": "腎", "advice": "潛藏保暖，適合儲備學習，少透支體力"},
            "小雪": {"wx": "水", "zang": "腎", "advice": "溫補腎氣，早睡，關節保暖"},
            "大雪": {"wx": "水", "zang": "腎", "advice": "極寒養藏，減少無謂應酬，靜心規劃"},
            "冬至": {"wx": "水", "zang": "腎", "advice": "一陽來復，宜養精蓄銳，可溫補但勿過燥"},
            "小寒": {"wx": "水", "zang": "腎", "advice": "防寒保暖，關節護理，作息穩定"},
            "大寒": {"wx": "水", "zang": "腎", "advice": "歲末收心，適合復盤年度，勿硬撐疲勞"},
        },
        # 建除 → 現代行動
        "jianchuModern": {
            "建": {"do": "啟動規劃、對齊目標、見貴人", "dont": "大興土木式重構、大額囤貨"},
            "除": {"do": "清理債務／Bug／雜物、就醫檢查", "dont": "倉促上任、遠途出差"},
            "滿": {"do": "慶祝里程碑、收款、社交", "dont": "過度承諾、身體過度負擔"},
            "平": {"do": "例行維護、文件潤飾、環境整理", "dont": "強推高風險決策"},
            "定": {"do": "拍板定案、簽合理約、安床安居", "dont": "反覆改口、興訟爭執"},
            "執": {"do": "執行落地、追進度、鎖定範圍", "dont": "同時開太多線"},
            "破": {"do": "拆舊重構、結束不良合作", "dont": "開張嫁娶、重大剪綵"},
            "危": {"do": "風險評估、備援方案、安撫情緒", "dont": "冒險操作、登高涉險"},
            "成": {"do": "交付上線、開市成交、團隊慶祝", "dont": "半途而廢"},
            "收": {"do": "結案收款、備份歸檔、學習吸收", "dont": "散財無度"},
            "開": {"do": "開新專案、面試、曝光", "dont": "殯葬類悲傷事"},
            "閉": {"do": "封存、保密、休養生息", "dont": "強行開張擴張"},
        },
        # 刑冲合害 → 現代建議
        "relationModern": {
            "冲": "變動大，行程易改；重大決策可緩一日，改走彈性方案",
            "合": "人緣與合作佳，適合請託、對齊、談條件",
            "三合": "氣場相助，團隊推進順，可開協調會",
            "害": "暗耗與小人風險，合約細節與權限再查一次",
            "刑": "內心急躁易執拗，先深呼吸再回覆訊息",
            "自刑": "自我拉扯，減少內耗，寫下優先級",
            "值": "本命感強，適合反思調整節奏",
            "平": "無大冲合，按計畫穩步即可",
        },
    }


def compute_bazi(solar_ymd: str, hour: int, minute: int = 0) -> dict:
    y, m, d = map(int, solar_ymd.split("-"))
    s = Solar.fromYmdHms(y, m, d, hour, minute, 0)
    l = s.getLunar()
    ec = l.getEightChar()
    return {
        "solar": solar_ymd,
        "hour": hour,
        "year": ec.getYear(),
        "month": ec.getMonth(),
        "day": ec.getDay(),
        "time": ec.getTime(),
        "dayMaster": ec.getDayGan(),
        "dayZhi": ec.getDayZhi(),
        "dayMasterWx": WX.get(ec.getDayGan(), ""),
        "yearGan": ec.getYearGan(),
        "yearZhi": ec.getYearZhi(),
        "monthGan": ec.getMonthGan(),
        "monthZhi": ec.getMonthZhi(),
        "timeGan": ec.getTimeGan(),
        "timeZhi": ec.getTimeZhi(),
        "dayNaYin": ec.getDayNaYin(),
        "xunKong": ec.getDayXunKong(),
        "taiYuan": ec.getTaiYuan(),
        "mingGong": ec.getMingGong(),
    }


def build_personal_bazi() -> dict:
    # 辰時取 8:00，寅時取 4:00
    p1985 = compute_bazi("1985-08-28", 8)
    p1985.update({
        "id": "p1985",
        "label": "1985.08.28",
        "birthHourZhi": "辰",
        "gender": "male",
        "genderLabel": "男",
        "xiao": "牛",
        "xiYong": ["火", "土", "金"],
        "jiYong": ["木", "水"],
        "luckyColors": ["黃", "棕", "紅", "金"],
        "constellation": "處女座",
    })
    p1995 = compute_bazi("1995-11-08", 4)
    p1995.update({
        "id": "p1995",
        "label": "1995.11.08",
        "birthHourZhi": "寅",
        "gender": "female",
        "genderLabel": "女",
        "xiao": "豬",
        "xiYong": ["金", "水", "木"],
        "jiYong": ["土", "火"],
        "luckyColors": ["黑", "深藍", "金", "綠"],
        "constellation": "天蠍座",
    })
    return {"profiles": [p1985, p1995], "source": "lunar_python EightChar"}


def day_fact(y: int, m: int, d: int) -> dict:
    s = Solar.fromYmd(y, m, d)
    l = s.getLunar()
    prev_jq = l.getPrevJieQi()
    next_jq = l.getNextJieQi()
    prev_name = prev_jq.getName() if prev_jq else ""
    next_name = next_jq.getName() if next_jq else ""

    # 四絕四離：看「明天」是否為八節
    tomorrow = date(y, m, d) + timedelta(days=1)
    st = Solar.fromYmd(tomorrow.year, tomorrow.month, tomorrow.day)
    lt = st.getLunar()
    # 若明天的 prevJieQi 日期就是明天… 用 jieqi table 比對較穩
    si = None
    # 用當天 nextJieQi：若 next 在明天
    if next_jq:
        ns = next_jq.getSolar()
        if ns.getYear() == tomorrow.year and ns.getMonth() == tomorrow.month and ns.getDay() == tomorrow.day:
            nn = next_jq.getName()
            if nn in SI_JUE:
                si = {"type": "jue", "label": "四絕日", "jieqi": nn}
            elif nn in SI_LI:
                si = {"type": "li", "label": "四離日", "jieqi": nn}

    si_out = None
    if si:
        si_out = {
            "type": si["type"],
            "label": to_trad(si["label"]),
            "jieqi": to_trad(si["jieqi"]),
        }

    return {
        "date": f"{y:04d}-{m:02d}-{d:02d}",
        "yearGZ": to_trad(l.getYearInGanZhiExact()),
        "monthGZ": to_trad(l.getMonthInGanZhiExact()),
        "dayGZ": to_trad(l.getDayInGanZhi()),
        "dayGan": to_trad(l.getDayGan()),
        "dayZhi": to_trad(l.getDayZhi()),
        "zhiXing": to_trad(l.getZhiXing()),  # 建除
        "tianShen": to_trad(l.getDayTianShen()),
        "tianShenType": to_trad(l.getDayTianShenType()),
        "tianShenLuck": to_trad(l.getDayTianShenLuck()),
        "xiu": to_trad(l.getXiu()),
        "xiuLuck": to_trad(l.getXiuLuck()),
        "yi": trad_list(l.getDayYi()[:10]),
        "ji": trad_list(l.getDayJi()[:10]),
        "jiShen": trad_list(l.getDayJiShen()[:8]),
        "xiongSha": trad_list(l.getDayXiongSha()[:8]),
        "chong": to_trad(l.getDayChong()),
        "chongShengXiao": to_trad(l.getDayChongShengXiao()),
        "sha": to_trad(l.getDaySha()),
        "naYin": to_trad(l.getDayNaYin()),
        "pengZuGan": to_trad(l.getPengZuGan()),
        "pengZuZhi": to_trad(l.getPengZuZhi()),
        "posXi": to_trad(l.getDayPositionXiDesc()),
        "posFu": to_trad(l.getDayPositionFuDesc()),
        "posCai": to_trad(l.getDayPositionCaiDesc()),
        "prevJieQi": to_trad(prev_name),
        "nextJieQi": to_trad(next_name),
        "siJueLi": si_out,
    }


def personal_day_payload(profile: dict, fact: dict) -> dict:
    dm = profile["dayMaster"]
    day_gan = fact["dayGan"]
    day_zhi = fact["dayZhi"]
    ss = to_trad(shi_shen(dm, day_gan))

    # 與本命四柱地支關係
    pillars = {
        "年": profile["yearZhi"],
        "月": profile["monthZhi"],
        "日": profile["dayZhi"],
        "時": profile["timeZhi"],
    }
    rels = []
    for name, z in pillars.items():
        for r in zhi_relations(z, day_zhi):
            if r["type"] != "平":
                rels.append({
                    **r,
                    "detail": to_trad(r["detail"]),
                    "pillar": name,
                })
    if not rels:
        rels = [{"type": "平", "detail": "四柱與日支無明顯刑冲合害", "score": 1, "pillar": "-"}]

    rel_score = sum(r["score"] for r in rels)
    # 喜用
    day_wx = WX.get(day_gan, "")
    xi_hit = day_wx in profile.get("xiYong", [])
    ji_hit = day_wx in profile.get("jiYong", [])

    # 建除分
    jx = fact["zhiXing"]
    jianchu_score = {
        "建": 2, "除": 3, "滿": 6, "平": 0, "定": 7, "執": 1,
        "破": -12, "危": -3, "成": 10, "收": 5, "開": 9, "閉": -8,
    }.get(jx, 0)

    ts_score = fact.get("tianShenLuck") == "吉"
    xiu_score = 3 if fact.get("xiuLuck") == "吉" else (-3 if fact.get("xiuLuck") == "凶" else 0)

    total = 55 + rel_score + jianchu_score + (8 if xi_hit else 0) + (-10 if ji_hit else 0)
    total += 5 if ts_score else -4
    total += xiu_score
    if fact.get("siJueLi"):
        total -= 15
    total = max(15, min(96, int(total)))

    # 結構化輸出（給語意層／未來 Batch LLM）
    return {
        "profileId": profile["id"],
        "date": fact["date"],
        "dayMaster": dm,
        "dayMasterWx": profile["dayMasterWx"],
        "flowDay": fact["dayGZ"],
        "shiShen": ss,
        "xiYongHit": xi_hit,
        "jiYongHit": ji_hit,
        "dayWx": day_wx,
        "relations": rels,
        "relationScore": rel_score,
        "zhiXing": jx,
        "tianShen": fact["tianShen"],
        "tianShenType": fact["tianShenType"],
        "xiu": fact["xiu"],
        "xiuLuck": fact["xiuLuck"],
        "yi": fact["yi"][:6],
        "ji": fact["ji"][:6],
        "jiShen": fact["jiShen"][:5],
        "xiongSha": fact["xiongSha"][:5],
        "chongShengXiao": fact["chongShengXiao"],
        "sha": fact["sha"],
        "prevJieQi": fact["prevJieQi"],
        "siJueLi": fact["siJueLi"],
        "score": total,
        "level": (
            "大吉" if total >= 85 else "吉" if total >= 72 else "小吉" if total >= 58
            else "平" if total >= 45 else "小凶" if total >= 32 else "慎"
        ),
    }


def build_daily_years(start_year: int, end_year: int, profiles: list) -> dict:
    """逐年輸出，控制單檔大小。"""
    sizes = {}
    for y in range(start_year, end_year + 1):
        days = {}
        d0 = date(y, 1, 1)
        d1 = date(y, 12, 31)
        cur = d0
        while cur <= d1:
            fact = day_fact(cur.year, cur.month, cur.day)
            personals = {p["id"]: personal_day_payload(p, fact) for p in profiles}
            days[fact["date"]] = {"fact": fact, "personals": personals}
            cur += timedelta(days=1)
        path = DATA / f"daily-facts-{y}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(days, f, ensure_ascii=False, separators=(",", ":"))
        sizes[path.name] = path.stat().st_size
        print(f"  wrote {path.name} {sizes[path.name]/1024:.1f} KB, days={len(days)}")
    return sizes


def write_personal_system_js(mapping: dict, bazi: dict):
    """前端語意轉譯層（確定性模板，結構可直接餵 LLM Batch）。"""
    # 僅打包映射與八字，每日 facts 按需 fetch 年檔
    payload = {
        "mapping": mapping,
        "bazi": bazi,
        "dailyFactsYears": list(range(2024, 2029)),
        "dailyFactsPath": "data/daily-facts-{year}.json",
    }
    path = LIB / "personal-system.js"
    with open(path, "w", encoding="utf-8") as f:
        f.write("/* Auto-generated by scripts/build_personal_system.py */\n")
        f.write("window.PERSONAL_SYSTEM = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
        # 語意轉譯引擎
        f.write(r'''
(function(global){
  "use strict";
  const PS = global.PERSONAL_SYSTEM;
  if(!PS) return;
  const cache = {};

  async function loadDay(dateStr){
    const y = dateStr.slice(0,4);
    if(!cache[y]){
      const url = PS.dailyFactsPath.replace("{year}", y);
      const res = await fetch(url);
      if(!res.ok) throw new Error("load daily facts fail "+url);
      cache[y] = await res.json();
    }
    return cache[y][dateStr] || null;
  }

  function pickScenarios(ss){
    const alias = {伤官:"傷官",正财:"正財",偏财:"偏財",七杀:"七殺",劫财:"劫財",正印:"正印",偏印:"偏印",食神:"食神",比肩:"比肩",正官:"正官"};
    const key = alias[ss] || ss;
    return PS.mapping.tenGodsScenarios[key] || PS.mapping.tenGodsScenarios["比肩"];
  }

  function energyOf(name, typeLuck){
    const db = PS.mapping.shenShaEnergy;
    if(db[name]) return db[name];
    if(typeLuck === "吉") return db["默认吉"];
    if(typeLuck === "凶") return db["默认凶"];
    return {energy:"平", modern:"按計畫執行即可", tone:"中"};
  }

  function tcmOf(jieqi){
    return PS.mapping.solarTermTcm[jieqi] || null;
  }

  /** 語意轉譯層：結構化 JSON → 現代生活建議（離線模板，可替換成 Batch LLM） */
  function interpret(profileId, dayPack){
    if(!dayPack) return null;
    const p = dayPack.personals[profileId];
    const f = dayPack.fact;
    if(!p) return null;
    const sc = pickScenarios(p.shiShen);
    const jc = PS.mapping.jianchuModern[p.zhiXing] || {do:"穩步執行", dont:"衝動決策"};
    const relMain = (p.relations && p.relations[0]) || {type:"平"};
    const relText = PS.mapping.relationModern[relMain.type] || PS.mapping.relationModern["平"];
    const tsEnergy = energyOf(p.tianShen, p.tianShenType === "黄道" || p.tianShenType === "黃道" ? "吉" : (p.tianShenLuck==="吉"?"吉":"凶"));
    const xiongE = (p.xiongSha||[]).slice(0,2).map(n=>energyOf(n,"凶"));
    const tcm = tcmOf(f.prevJieQi);

    const workTips = sc.work.slice(0,2);
    const lifeTips = sc.life.slice(0,2);
    const cautions = [].concat(sc.caution||[], jc.dont?[jc.dont]:[], xiongE.map(e=>e.modern));

    const actions = [];
    actions.push(`【十神·${p.shiShen}】今日適合：${workTips.join("、")}；生活面：${lifeTips.join("、")}`);
    actions.push(`【建除·${p.zhiXing}】宜：${jc.do}；忌：${jc.dont}`);
    actions.push(`【刑衝合害】${relMain.detail||relMain.type} → ${relText}`);
    actions.push(`【黃道神煞·${p.tianShen}】${tsEnergy.modern}`);
    if(tcm) actions.push(`【節氣養生·${f.prevJieQi}】五行偏${tcm.wx}（${tcm.zang}）：${tcm.advice}`);
    if(p.siJueLi) actions.push(`【${p.siJueLi.label}】明日${p.siJueLi.jieqi}，今日勿開張嫁娶動土，宜靜守`);
    if(p.xiYongHit) actions.push(`【喜用】流日${p.dayWx}合你喜用，可積極推進交付`);
    if(p.jiYongHit) actions.push(`【忌神】流日${p.dayWx}觸忌，少硬推、多覆核`);

    // 宜忌現代轉寫（抽前 3）
    const yiModern = (p.yi||[]).slice(0,3).map(x=>`可安排：${x}`);
    const jiModern = (p.ji||[]).slice(0,3).map(x=>`避開：${x}`);

    // 面向 LLM Batch 的乾淨 JSON
    const llmPayload = {
      profileId,
      date: p.date,
      deterministic: p,
      mappingsUsed: {
        shiShen: p.shiShen,
        scenarios: sc,
        jianchu: jc,
        relation: relMain,
        tianShenEnergy: tsEnergy,
        tcm
      },
      instruction: "請只根據 deterministic 與 mappingsUsed 生成 3-5 條具體今日行動，禁止改口干支與神煞名稱。"
    };

    return {
      score: p.score,
      level: p.level,
      shiShen: p.shiShen,
      zhiXing: p.zhiXing,
      tianShen: p.tianShen,
      tianShenType: p.tianShenType,
      xiu: p.xiu,
      xiuLuck: p.xiuLuck,
      relations: p.relations,
      yi: p.yi,
      ji: p.ji,
      jiShen: p.jiShen,
      xiongSha: p.xiongSha,
      actions: actions.slice(0, 7),
      workTips,
      lifeTips,
      cautions: [...new Set(cautions)].slice(0, 5),
      yiModern,
      jiModern,
      tcm,
      llmPayload,
      source: "lunar_python+mapping-db+semantic-templates"
    };
  }

  function toDateKey(d){
    const y=d.getFullYear(), m=String(d.getMonth()+1).padStart(2,"0"), day=String(d.getDate()).padStart(2,"0");
    return `${y}-${m}-${day}`;
  }

  async function getPersonalFortune(profileId, dateObj){
    const key = toDateKey(dateObj instanceof Date ? dateObj : new Date(dateObj));
    const pack = await loadDay(key);
    return interpret(profileId, pack);
  }

  global.PersonalFortuneEngine = {
    loadDay,
    interpret,
    getPersonalFortune,
    profiles: PS.bazi.profiles,
    mapping: PS.mapping
  };
})(typeof window!=="undefined"?window:globalThis);
''')
    return path


def main():
    print("Building mapping DB...")
    mapping = build_mapping_db()
    with open(DATA / "mapping-db.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print("Building personal bazi via lunar_python...")
    bazi = build_personal_bazi()
    with open(DATA / "personal-bazi.json", "w", encoding="utf-8") as f:
        json.dump(bazi, f, ensure_ascii=False, indent=2)
    print(json.dumps(bazi["profiles"], ensure_ascii=False, indent=2)[:800])

    print("Building daily facts 2024-2028 (deterministic)...")
    sizes = build_daily_years(2024, 2028, bazi["profiles"])

    print("Writing personal-system.js ...")
    write_personal_system_js(mapping, bazi)

    total = sum(p.stat().st_size for p in DATA.glob("**/*") if p.is_file())
    total += sum(p.stat().st_size for p in LIB.glob("**/*") if p.is_file())
    report = {
        "total_bytes": total,
        "total_MB": round(total / 1024 / 1024, 3),
        "under_500MB": total < 500 * 1024 * 1024,
        "daily_files": sizes,
        "profiles": [p["id"] + " " + p["year"] + " " + p["month"] + " " + p["day"] + " " + p["time"] for p in bazi["profiles"]],
    }
    with open(DATA / "PERSONAL_BUILD_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("DONE")


if __name__ == "__main__":
    main()
