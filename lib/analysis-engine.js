/**
 * 黃曆／奇門／六壬／個人運勢 — 基於 HUANGLI_DB 的天時強化分析引擎
 * 須在 huangli-db.js 之後載入
 */
(function (global) {
  "use strict";
  const DB = global.HUANGLI_DB;
  if (!DB) {
    console.warn("[analysis-engine] HUANGLI_DB missing");
    return;
  }

  const TG = DB.huangli.tianGan;
  const DZ = DB.huangli.diZhi;
  const WX_G = DB.huangli.wuxingGan;
  const WX_Z = DB.huangli.wuxingZhi;
  const W = DB.weights;
  const QM = DB.qimen;
  const LR = DB.liuren;
  const HL = DB.huangli;

  function clamp(n, a, b) {
    return Math.max(a, Math.min(b, n));
  }

  function zhiIndex(z) {
    return DZ.indexOf(z);
  }

  /** 依預計算節氣表取當前節氣名 */
  function currentJieQiName(y, m, d) {
    const arr = DB.jieqi[String(y)];
    if (!arr) return null;
    let cur = "冬至";
    const prev = DB.jieqi[String(y - 1)];
    if (prev) cur = prev[23].n; // 前一年冬至後
    for (const item of arr) {
      if (m > item.m || (m === item.m && d >= item.d)) cur = item.n;
    }
    return cur;
  }

  function yueJian(jieqiName) {
    return DB.jieqiYuejian[jieqiName] || "寅";
  }

  /** 日主 vs 流日干 → 十神 */
  function shiShen(dayMaster, dayGan) {
    const me = WX_G[dayMaster];
    const other = WX_G[dayGan];
    const meY = "甲丙戊庚壬".includes(dayMaster);
    const oY = "甲丙戊庚壬".includes(dayGan);
    const sameYinYang = meY === oY;
    if (me === other) return sameYinYang ? "比肩" : "劫財";
    // 我生
    const sheng = { 木: "火", 火: "土", 土: "金", 金: "水", 水: "木" };
    // 我克
    const ke = { 木: "土", 火: "金", 土: "水", 金: "木", 水: "火" };
    if (sheng[me] === other) return sameYinYang ? "食神" : "傷官";
    if (ke[me] === other) return sameYinYang ? "偏財" : "正財";
    if (ke[other] === me) return sameYinYang ? "七殺" : "正官";
    if (sheng[other] === me) return sameYinYang ? "偏印" : "正印";
    return "比肩";
  }

  function zhiRelationKey(myZhi, dayZhi) {
    if (myZhi === dayZhi) return "值";
    if (HL.chong[myZhi] === dayZhi) return "冲";
    if (LR.liuhe[myZhi] === dayZhi) return "合";
    if (LR.liuhai[myZhi] === dayZhi) return "害";
    const sanhe = [
      ["申", "子", "辰"],
      ["亥", "卯", "未"],
      ["寅", "午", "戌"],
      ["巳", "酉", "丑"],
    ];
    for (const g of sanhe) {
      if (g.includes(myZhi) && g.includes(dayZhi) && myZhi !== dayZhi) return "三合";
    }
    return "平";
  }

  /**
   * 綜合天時評分（0–100）
   * 輸入：建除、青龍、六壬取法、奇門吉凶門、月建旺衰、日主喜用、本命關係
   */
  function scoreTianShi(opts) {
    const {
      jianchu,
      qinglongName,
      liurenMethod,
      qimenLucky,
      monthZhi,
      dayGanWx,
      dayMasterWx,
      xiYong,
      jiYong,
      relKey,
    } = opts;

    let s = 50;
    s += W.jianchu[jianchu] || 0;
    s += W.qinglong[qinglongName] || 0;
    s += W.liurenMethod[liurenMethod] || 0;

    // 奇門
    if (qimenLucky) {
      if (/開門|生門/.test(qimenLucky)) s += W.qimenOpenSheng;
      if (/死門|驚門|傷門/.test(qimenLucky) && !/開門|生門/.test(qimenLucky)) s += W.qimenSiJing;
    }

    // 節氣旺衰：流日干五行在月令的狀態
    const wxState = (HL.wangxiang[monthZhi] || {});
    let state = "休";
    for (const k of ["旺", "相", "休", "囚", "死"]) {
      if (wxState[k] === dayGanWx) {
        state = k;
        break;
      }
    }
    const stateScore = { 旺: W.wang, 相: W.xiang, 休: W.xiu, 囚: W.qiu, 死: W.si };
    s += stateScore[state] || 0;

    // 喜用
    if (xiYong && xiYong.includes(dayGanWx)) s += W.xiYongHit;
    if (jiYong && jiYong.includes(dayGanWx)) s += W.jiYongHit;

    // 本命地支關係
    const relScore = { 合: W.he, 三合: W.he - 2, 冲: W.chong, 害: W.hai, 刑: W.xing, 值: 3, 平: 1 };
    s += relScore[relKey] || 0;

    // 日主五行得令
    if (dayMasterWx && wxState.旺 === dayMasterWx) s += 4;
    if (dayMasterWx && wxState.死 === dayMasterWx) s -= 3;

    return {
      score: clamp(Math.round(s), 5, 98),
      wangxiangState: state,
      monthWang: wxState.旺,
    };
  }

  function modeFromScore(score) {
    if (score >= 75) return { mode: `大吉進取（${score}）`, modeKey: "open" };
    if (score >= 62) return { mode: `小吉可為（${score}）`, modeKey: "mild" };
    if (score >= 48) return { mode: `平穩守中（${score}）`, modeKey: "steady" };
    if (score >= 35) return { mode: `審慎收斂（${score}）`, modeKey: "careful" };
    return { mode: `宜避凶守（${score}）`, modeKey: "guard" };
  }

  /** 強化後的每日分析（覆寫頁面 computeDailyAnalysis 的結果） */
  function enhanceDailyAnalysis(pageAnalysis, ctx) {
    if (!pageAnalysis || !ctx) return pageAnalysis;
    const dayGZ = ctx.dayGZ;
    const monthZhi = ctx.monthGZ ? ctx.monthGZ.zhi : "未";
    const jieqi =
      currentJieQiName(ctx.year || new Date().getFullYear(), ctx.month || 1, ctx.day || 1) ||
      ctx.jieqiName ||
      "";

    const ts = scoreTianShi({
      jianchu: ctx.jianchu,
      qinglongName: ctx.qinglong && ctx.qinglong.name,
      liurenMethod: ctx.liuren && ctx.liuren.sanchuan && ctx.liuren.sanchuan.method,
      qimenLucky: ctx.qimen && ctx.qimen.lucky,
      monthZhi,
      dayGanWx: WX_G[dayGZ.gan],
      dayMasterWx: null,
      xiYong: null,
      jiYong: null,
      relKey: "平",
    });

    const { mode, modeKey } = modeFromScore(ts.score);
    const enhanced = Object.assign({}, pageAnalysis, {
      mode,
      modeKey,
      score: ts.score,
      wangxiangState: ts.wangxiangState,
      monthWang: ts.monthWang,
      jieqi,
      engine: "HUANGLI_DB+v1",
    });

    // 在步驟中注入天時旺衰
    if (enhanced.steps && enhanced.steps[0]) {
      enhanced.steps = enhanced.steps.slice();
      enhanced.steps[0] = Object.assign({}, enhanced.steps[0], {
        content:
          enhanced.steps[0].content +
          ` 月令「${monthZhi}」當旺「${ts.monthWang}」；流日${WX_G[dayGZ.gan]}處「${ts.wangxiangState}」。`,
      });
    }

    // 六壬取法提示
    const method = ctx.liuren && ctx.liuren.sanchuan && ctx.liuren.sanchuan.method;
    if (method && LR.methodTips[method] && enhanced.steps && enhanced.steps[3]) {
      enhanced.steps = enhanced.steps.slice();
      enhanced.steps[3] = Object.assign({}, enhanced.steps[3], {
        content: enhanced.steps[3].content + " " + LR.methodTips[method],
      });
    }

    // 奇門格局提示
    if (ctx.qimen && ctx.qimen.lucky && enhanced.steps && enhanced.steps[2]) {
      const tips = [];
      for (const men of ["開", "休", "生", "死", "驚", "傷", "杜", "景"]) {
        if (ctx.qimen.lucky.includes(men + "門") && QM.patternTips[men + "門"]) {
          tips.push(men + "門：" + QM.patternTips[men + "門"]);
        }
      }
      if (tips.length) {
        enhanced.steps = enhanced.steps.slice();
        enhanced.steps[2] = Object.assign({}, enhanced.steps[2], {
          content: enhanced.steps[2].content + " " + tips.slice(0, 3).join("；") + "。",
        });
      }
    }

    // 依分數微調行動首句語氣
    if (enhanced.actions && enhanced.actions.length) {
      const prefix =
        modeKey === "open"
          ? "天時偏開："
          : modeKey === "guard"
            ? "天時偏斂："
            : modeKey === "careful"
              ? "天時宜慎："
              : "天時平穩：";
      enhanced.actions = enhanced.actions.slice();
      if (!String(enhanced.actions[0]).startsWith("天時")) {
        enhanced.actions[0] = prefix + enhanced.actions[0];
      }
    }

    return enhanced;
  }

  /** 強化個人運勢：十神＋喜用＋月令旺衰 */
  function enhancePersonal(pagePersonal, ctx) {
    if (!pagePersonal || !ctx) return pagePersonal;
    const profiles = DB.personal.profiles || [];
    const person = pagePersonal.person || {};
    const prof = profiles.find((p) => p.id === person.id) || {};
    const dayGZ = ctx.dayGZ;
    const monthZhi = ctx.monthGZ ? ctx.monthGZ.zhi : "未";
    const dm = prof.dayMaster || person.birthDayGZ && person.birthDayGZ.gan;
    if (!dm) return pagePersonal;

    const ss = shiShen(dm, dayGZ.gan);
    const ssTip = DB.personal.shishenRules[ss] || "";
    const ssAct = DB.personal.actionByShishen[ss] || "";
    const dayWx = WX_G[dayGZ.gan];
    const relKey =
      pagePersonal.relation && pagePersonal.relation.key
        ? pagePersonal.relation.key
        : zhiRelationKey(prof.yearZhi || person.yearZhi, dayGZ.zhi);

    const ts = scoreTianShi({
      jianchu: ctx.jianchu,
      qinglongName: ctx.qinglong && ctx.qinglong.name,
      liurenMethod: ctx.liuren && ctx.liuren.sanchuan && ctx.liuren.sanchuan.method,
      qimenLucky: ctx.qimen && ctx.qimen.lucky,
      monthZhi,
      dayGanWx: dayWx,
      dayMasterWx: prof.dayMasterWx || WX_G[dm],
      xiYong: prof.xiYong,
      jiYong: prof.jiYong,
      relKey,
    });

    const notes = (pagePersonal.notes || []).slice();
    // 注入命理天時條目到今日注意最前
    const inject = [
      `【命理天時】日主${dm}（${prof.dayMasterWx || WX_G[dm]}）遇流日${dayGZ.full}，十神「${ss}」：${ssTip}`,
      `【喜用】流日五行為${dayWx}，${
        (prof.xiYong || []).includes(dayWx) ? "合喜用，可積極作為" : (prof.jiYong || []).includes(dayWx) ? "觸忌神，宜守" : "中性，穩進即可"
      }；月令${monthZhi}當旺${ts.monthWang}，流日處「${ts.wangxiangState}」。`,
      `【配合】${ssAct}；天時綜合分 ${ts.score}。`,
    ];
    const merged = [];
    const seen = new Set();
    for (const line of [...inject, ...notes]) {
      if (!line || seen.has(line)) continue;
      seen.add(line);
      merged.push(line);
    }

    // 微調總分展示（不覆蓋原 aspects 結構，只微調 score）
    const adj = clamp(Math.round((pagePersonal.score + ts.score) / 2), 18, 96);
    const level =
      adj >= 85 ? "大吉" : adj >= 72 ? "吉" : adj >= 58 ? "小吉" : adj >= 45 ? "平" : adj >= 32 ? "小凶" : "慎";

    return Object.assign({}, pagePersonal, {
      notes: merged.slice(0, 9),
      score: adj,
      level,
      tianShiScore: ts.score,
      shiShen: ss,
      shiShenTip: ssTip,
      engine: "HUANGLI_DB+personal-v1",
    });
  }

  /** 入口：強化整包 almanac */
  function enhanceAlmanac(data) {
    if (!data) return data;
    const ymd = (data.solar || "").match(/(\d+)年(\d+)月(\d+)日/);
    const year = ymd ? +ymd[1] : new Date().getFullYear();
    const month = ymd ? +ymd[2] : 1;
    const day = ymd ? +ymd[3] : 1;
    const ctx = {
      dayGZ: data.dayGZ,
      monthGZ: data.monthGZ,
      yearGZ: data.yearGZ,
      jianchu: data.jianchu || (data.zhishenPlain || "").replace(/建除|日.*/g, "").trim(),
      qinglong: data.qinglong,
      yiji: { yi: data.yi, ji: data.ji },
      liuren: data.liuren,
      qimen: data.qimen,
      fangwei: data.fangwei,
      year,
      month,
      day,
      jieqiName: currentJieQiName(year, month, day),
    };
    // extract jianchu better
    if (data.zhishenPlain) {
      const m = data.zhishenPlain.match(/建除([建除滿平定執破危成收開閉])日/);
      if (m) ctx.jianchu = m[1];
    }

    if (data.dailyAnalysis) {
      data.dailyAnalysis = enhanceDailyAnalysis(data.dailyAnalysis, ctx);
    }
    if (Array.isArray(data.personals)) {
      data.personals = data.personals.map((p) => enhancePersonal(p, ctx));
    }
    data.dbMeta = DB.meta;
    data.tianShiJieqi = ctx.jieqiName;
    data.tianShiYuejian = yueJian(ctx.jieqiName);
    return data;
  }

  global.HuangliEngine = {
    enhanceAlmanac,
    enhanceDailyAnalysis,
    enhancePersonal,
    scoreTianShi,
    shiShen,
    currentJieQiName,
    yueJian,
    DB,
  };
})(typeof window !== "undefined" ? window : globalThis);
