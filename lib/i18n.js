/**
 * 輕量 i18n（無外部套件）
 * 使用：I18N.t('key') / I18N.setLang('ja') / data-i18n / data-i18n-aria / data-i18n-html
 */
(function (global) {
  "use strict";

  const STORAGE_KEY = "huangli-lang";

  const ZH = {
    langName: "繁體中文",
    langToggle: "日本語",
    langToggleTitle: "切換為日本語",
    docTitle: "每日黃曆",
    appTitle: "每日黃曆",
    appSubtitle: "擇日 · 宜忌 · 干支",
    seal: "曆",
    today: "今日",
    prevDay: "前一天",
    nextDay: "後一天",
    installTitle: "加到 iPhone 主畫面",
    installBody:
      "，之後可像 App 一樣點開查詢（離線也能用）：",
    installStep1: "1. 點 Safari 底部",
    installShare: "分享",
    installStep1b: "（方框＋向上箭頭）",
    installStep2: "2. 往下滑選",
    installAdd: "加入主畫面",
    installStep2b: "→ 加入",
    gotIt: "知道了",
    neverShow: "不再顯示",
    zodiac: "生肖",
    constellation: "星座",
    jieqi: "節氣",
    siTipDefault: "諸事不宜開張、嫁娶、動土、遠行；宜守成、靜養",
    dailyAnalysis: "每日分析",
    dailyAnalysisAria: "每日分析與今日行動",
    todayActions: "今日行動方案",
    daFoot: "依值神 → 宜忌 → 奇門 → 六壬 四步歸納 · 僅供民俗參考",
    jysTitlePrefix: "節氣養生",
    jysToday: "今日交節",
    jysEmpty: "養生資料未載入",
    jysEmptyTerm: "暫無此節氣養生資料",
    jysWx: "五行",
    jysZang: "臟腑",
    jysNext: "下一節氣",
    jysFocus: "養生重點",
    jysDiet: "飲食建議",
    jysRoutine: "作息／起居",
    jysEmotion: "情志注意",
    jysHerbs: "本草參考（神農本草經等）",
    jysBencao: "《本草》",
    richenTitle: "日辰要覽",
    richenHint: "五行 · 神煞 · 六壬 · 奇門",
    labelWuxing: "五行",
    labelNayin: "納音",
    labelChongsha: "冲煞",
    labelJianchu: "建除值神",
    labelQinglong: "青龍值神",
    labelHuanghei: "黃黑道",
    labelJishen: "吉神宜趨",
    labelXiongshen: "凶神宜忌",
    labelFangwei: "方位參考",
    liurenTitle: "大六壬日課",
    lrYuejiang: "月將",
    lrZhanshi: "占時",
    lrXunkong: "旬空",
    lrGuiren: "貴人",
    lrJigong: "日辰寄宮",
    lrNote: "以月將加時起天地盤 · 四課三傳 · 僅供參考",
    lrChu: "初傳",
    lrZhong: "中傳",
    lrMo: "末傳",
    qimenTitle: "奇門遁甲（日家 · 拆補）",
    qmJu: "用局",
    qmShi: "用日",
    qmZhifu: "值符",
    qmZhishi: "值使",
    qmMeta: "三奇六儀 · 空亡",
    qmLucky: "吉門方位（開／休／生）",
    qmNote: "日家奇門拆補法 · 以日干支起盤 · 僅供民俗參考",
    yijiTitle: "今日宜忌",
    yi: "宜",
    ji: "忌",
    pengzuTitle: "彭祖百忌",
    pengzuLabel: "今日宜謹記",
    pengzuAdviceLabel: "生活白話建議",
    personalTitle: "個人專屬運勢",
    personalAria: "個人運勢列表",
    footer1: "傳統黃曆文化參考 · 個人運勢＝lunar_python 精算＋三維映射語意轉譯",
    footer2: "僅供趣味與民俗參考 · 非專業命理／擇日依據",
    // chips / personal
    gender: "性別",
    male: "男",
    female: "女",
    pillars: "四柱",
    yearPillar: "年柱",
    monthPillar: "月柱",
    dayPillar: "日柱",
    hourPillar: "時柱",
    xuAge: "虛歲",
    zhouAge: "週歲",
    born: "出生",
    lunar: "農曆",
    dayMaster: "日主",
    shiShen: "流日十神",
    jianchuShen: "建除 · 值神",
    xiu28: "二十八宿",
    xiJi: "喜用／忌神",
    xiHit: "流日合喜用",
    jiHit: "流日觸忌",
    neutral: "中性",
    jysPersonal: "節氣養生",
    huangjiTitle: "皇極數讖言",
    huangjiBirth: "本命八字 → 數序",
    huangjiFlow: "流日八字（定午）→ 數序",
    huangjiPillars: "四柱",
    huangjiYing: "應驗讖言 · 序第",
    huangjiGua: "值卦",
    huangjiSynth: "（本命總序×流日柱序合成）",
    baihua: "白話說明",
    doTitle: "● 適合做",
    dontTitle: "● 不適合做",
    noteTitle: "● 今日注意",
    tijiLabel: "趨吉避凶 · 提高運勢",
    sourcePrefix: "運勢來源：",
    aspectCareer: "事業",
    aspectWealth: "財運",
    aspectSide: "偏財",
    aspectLove: "感情",
    aspectSocial: "人際",
    aspectHealth: "健康",
    weekdayPrefix: "星期",
    weekdays: ["日", "一", "二", "三", "四", "五", "六"],
    solarFmt: "{y}年{m}月{d}日",
    tomorrowJieqi: "明日節氣",
    siJue: "四絕日",
    siLi: "四離日",
    todayJieqi: "今日{name}",
    jieqiAfter: "{name} · {n}日後{next}",
    chong: "冲",
    sha: "煞",
    shengxiao: "生肖",
    // analysis step titles
    stepZhishen: "值神判斷",
    stepYiji: "宜忌重點",
    stepQimen: "奇門方位",
    stepLiuren: "六壬節奏",
    // common
    scoreUnit: "分",
    against: "對卦",
    histScale: "史尺",
    hourChar: "時",
    tenGodPrefix: "十神",
    jianchuPrefix: "建除",
    zhishenPrefix: "值神",
    xiuPrefix: "星宿",
    flowDayPrefix: "流日",
    pengzuGan: "日干",
    pengzuZhi: "日支",
  };

  const JA = {
    langName: "日本語",
    langToggle: "繁體中文",
    langToggleTitle: "繁体中国語に切り替え",
    docTitle: "毎日黄暦",
    appTitle: "毎日黄暦",
    appSubtitle: "選日 · 宜忌 · 干支",
    seal: "暦",
    today: "今日",
    prevDay: "前日",
    nextDay: "翌日",
    installTitle: "iPhoneのホーム画面に追加",
    installBody: "。アプリのように開き、オフラインでも使えます：",
    installStep1: "1. Safari下部の",
    installShare: "共有",
    installStep1b: "（四角と上矢印）をタップ",
    installStep2: "2. 下にスクロールして",
    installAdd: "ホーム画面に追加",
    installStep2b: "→ 追加",
    gotIt: "了解",
    neverShow: "今後表示しない",
    zodiac: "十二支",
    constellation: "星座",
    jieqi: "節気",
    siTipDefault:
      "開業・婚姻・土木・遠行は控え、守成と静養を優先してください",
    dailyAnalysis: "毎日の分析",
    dailyAnalysisAria: "毎日の分析と今日の行動",
    todayActions: "今日の行動プラン",
    daFoot: "値神 → 宜忌 → 奇門 → 六壬 の四段で整理 · 民俗参考",
    jysTitlePrefix: "節気養生",
    jysToday: "今日は交節",
    jysEmpty: "養生データ未読込",
    jysEmptyTerm: "この節気の養生データがありません",
    jysWx: "五行",
    jysZang: "臓腑",
    jysNext: "次の節気",
    jysFocus: "養生の要点",
    jysDiet: "食事のすすめ",
    jysRoutine: "起居・生活リズム",
    jysEmotion: "情志（こころ）の注意",
    jysHerbs: "本草参考（神農本草経など）",
    jysBencao: "『本草』",
    richenTitle: "日辰要覧",
    richenHint: "五行 · 神煞 · 六壬 · 奇門",
    labelWuxing: "五行",
    labelNayin: "納音",
    labelChongsha: "冲煞",
    labelJianchu: "建除値神",
    labelQinglong: "青龍値神",
    labelHuanghei: "黄黒道",
    labelJishen: "吉神（向かう）",
    labelXiongshen: "凶神（避ける）",
    labelFangwei: "方位の参考",
    liurenTitle: "大六壬 日課",
    lrYuejiang: "月将",
    lrZhanshi: "占時",
    lrXunkong: "旬空",
    lrGuiren: "貴人",
    lrJigong: "日辰寄宮",
    lrNote: "月将を時に加えて天地盤 · 四課三伝 · 参考",
    lrChu: "初伝",
    lrZhong: "中伝",
    lrMo: "末伝",
    qimenTitle: "奇門遁甲（日家 · 拆補）",
    qmJu: "用局",
    qmShi: "用日",
    qmZhifu: "値符",
    qmZhishi: "値使",
    qmMeta: "三奇六儀 · 空亡",
    qmLucky: "吉門方位（開／休／生）",
    qmNote: "日家奇門拆補法 · 日干支で盤 · 民俗参考",
    yijiTitle: "今日の宜忌",
    yi: "宜",
    ji: "忌",
    pengzuTitle: "彭祖百忌",
    pengzuLabel: "今日の心得",
    pengzuAdviceLabel: "暮らしのひとこと",
    personalTitle: "個人の運勢",
    personalAria: "個人運勢リスト",
    footer1: "伝統黄暦の文化参考 · 個人運勢＝lunar_python精算＋意味マッピング",
    footer2: "趣味・民俗の参考であり、専門の命理／選日根拠ではありません",
    gender: "性別",
    male: "男",
    female: "女",
    pillars: "四柱",
    yearPillar: "年柱",
    monthPillar: "月柱",
    dayPillar: "日柱",
    hourPillar: "時柱",
    xuAge: "数え年",
    zhouAge: "満年齢",
    born: "出生",
    lunar: "旧暦",
    dayMaster: "日主",
    shiShen: "流日の十神",
    jianchuShen: "建除 · 値神",
    xiu28: "二十八宿",
    xiJi: "喜用／忌神",
    xiHit: "流日が喜用に合う",
    jiHit: "流日が忌神に触れる",
    neutral: "中性",
    jysPersonal: "節気養生",
    huangjiTitle: "皇極数 讖言",
    huangjiBirth: "本命八字 → 数序",
    huangjiFlow: "流日八字（定午）→ 数序",
    huangjiPillars: "四柱",
    huangjiYing: "応験讖言 · 序第",
    huangjiGua: "値卦",
    huangjiSynth: "（本命総序×流日柱序の合成）",
    baihua: "わかりやすい説明",
    doTitle: "● 向いていること",
    dontTitle: "● 控えたいこと",
    noteTitle: "● 今日の注意",
    tijiLabel: "趨吉避凶 · 運を整える",
    sourcePrefix: "出典：",
    aspectCareer: "仕事",
    aspectWealth: "財運",
    aspectSide: "偏財",
    aspectLove: "恋愛",
    aspectSocial: "対人",
    aspectHealth: "健康",
    weekdayPrefix: "曜日",
    weekdays: ["日", "月", "火", "水", "木", "金", "土"],
    solarFmt: "{y}年{m}月{d}日",
    tomorrowJieqi: "明日の節気",
    siJue: "四絶日",
    siLi: "四離日",
    todayJieqi: "今日は{name}",
    jieqiAfter: "{name} · {n}日後に{next}",
    chong: "冲",
    sha: "煞",
    shengxiao: "十二支",
    stepZhishen: "値神の判断",
    stepYiji: "宜忌の要点",
    stepQimen: "奇門の方位",
    stepLiuren: "六壬のリズム",
    scoreUnit: "点",
    against: "対応卦",
    histScale: "史尺",
    hourChar: "時",
    tenGodPrefix: "十神",
    jianchuPrefix: "建除",
    zhishenPrefix: "値神",
    xiuPrefix: "星宿",
    flowDayPrefix: "流日",
    pengzuGan: "日干",
    pengzuZhi: "日支",
  };

  /** 彭祖白話日文 */
  const PENGZU_ADVICE_JA = {
    甲: "大きな預金の取り崩しや在庫一掃のような「開倉」的な出費は控え、金の出入りを再確認。",
    乙: "ゼロからの長期計画や「植える」型の投資を無理に始めず、育っているものを大切に。",
    丙: "キッチン大改修やガス・火まわりの工事は控え、火気・電気の安全に注意。",
    丁: "大きな髪型変更や頭の侵襲的施術は必要時以外避け、穏やかなケアを。",
    戊: "土地購入や大きな責任の引き受けは急ぎ契約せず、不動産案件は一日置けます。",
    己: "契約破棄や感情的な絶縁は避け、書類は冷静に話し合いを。",
    庚: "鍼灸などの新治療や空回りするラインの強行は控え、揃えてから着手。",
    辛: "熟していない製品の投入や醸造・仕込み系は、品質が固まってから。",
    壬: "水辺の遠出・水泳は控え、漏水・浸水・防水に注意。",
    癸: "訴訟や強い対立は避け、争いはまず協議。理が弱い時ほど意気が禁物。",
    子: "小事で占いを繰り返したり他人の決断に依存しすぎず、まず自分で考える。",
    丑: "就任・冠帯など新しい役割の儀式は改日でも可。",
    寅: "正式な祭祀・祈願は簡素に。心があれば大仰でなくてよい。",
    卯: "井戸掘りや深い掘削、基盤の水道工事は改日が安心。",
    辰: "大きな悲嘆は自分に余白を。喪事は落ち着いて、無理に強がらない。",
    巳: "遠出の出張・旅行は控え、貴重品を肌身離さず。",
    午: "屋根工事や大がかりな住宅改修は改期を。",
    未: "急病以外は新薬・民間療法の試しを控え、服薬は医師の指示で。",
    申: "ベッドの入れ替えや寝室の大移動は改日が無難。",
    酉: "大宴会や深酒を控え、会合は節度を。",
    戌: "食事は清潔に、出所不明の肉は控え、ペットと家の衛生に注意。",
    亥: "婚姻・婚約など大きな感情の約束は吉日を別途選んでもよい。",
  };

  const dicts = { "zh-Hant": ZH, ja: JA };

  const I18N = {
    lang: "zh-Hant",
    dicts,
    pengzuAdviceJa: PENGZU_ADVICE_JA,
    listeners: [],

    t(key, params) {
      const d = dicts[this.lang] || ZH;
      let s = d[key];
      if (s == null) s = ZH[key];
      if (s == null) return key;
      if (params && typeof s === "string") {
        s = s.replace(/\{(\w+)\}/g, (_, k) =>
          params[k] != null ? String(params[k]) : ""
        );
      }
      return s;
    },

    weekday(i) {
      const arr = (dicts[this.lang] || ZH).weekdays || ZH.weekdays;
      return arr[i] || ZH.weekdays[i];
    },

    formatSolar(y, m, d) {
      return this.t("solarFmt", { y, m, d });
    },

    isJa() {
      return this.lang === "ja";
    },

    getLang() {
      return this.lang;
    },

    setLang(lang, opts) {
      const next = lang === "ja" ? "ja" : "zh-Hant";
      if (this.lang === next && !(opts && opts.force)) return;
      this.lang = next;
      try {
        localStorage.setItem(STORAGE_KEY, next);
      } catch (e) {}
      document.documentElement.lang = next === "ja" ? "ja" : "zh-Hant";
      this.applyDom();
      this.listeners.forEach((fn) => {
        try {
          fn(next);
        } catch (e) {
          console.warn(e);
        }
      });
    },

    onChange(fn) {
      if (typeof fn === "function") this.listeners.push(fn);
    },

    loadSaved() {
      let saved = null;
      try {
        saved = localStorage.getItem(STORAGE_KEY);
      } catch (e) {}
      if (saved === "ja" || saved === "zh-Hant") this.lang = saved;
      document.documentElement.lang = this.lang === "ja" ? "ja" : "zh-Hant";
    },

    applyDom() {
      document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (!key) return;
        const val = this.t(key);
        if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
          el.placeholder = val;
        } else {
          el.textContent = val;
        }
      });
      document.querySelectorAll("[data-i18n-html]").forEach((el) => {
        const key = el.getAttribute("data-i18n-html");
        if (key) el.innerHTML = this.t(key);
      });
      document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
        const key = el.getAttribute("data-i18n-aria");
        if (key) el.setAttribute("aria-label", this.t(key));
      });
      document.querySelectorAll("[data-i18n-title]").forEach((el) => {
        const key = el.getAttribute("data-i18n-title");
        if (key) el.setAttribute("title", this.t(key));
      });
      const title = this.t("docTitle");
      if (title && typeof document !== "undefined") document.title = title;
      // 切換按鈕顯示「另一種語言」
      if (typeof document !== "undefined" && typeof document.getElementById === "function") {
        const btn = document.getElementById("langToggle");
        if (btn) {
          btn.textContent = this.t("langToggle");
          btn.setAttribute("title", this.t("langToggleTitle"));
          btn.setAttribute("aria-label", this.t("langToggleTitle"));
        }
      }
    },

    /** 節氣養生引擎用 locale 代碼 */
    jieqiLocale() {
      return this.lang === "ja" ? "ja" : "zh-Hant";
    },
  };

  I18N.loadSaved();
  global.I18N = I18N;
})(typeof window !== "undefined" ? window : globalThis);
