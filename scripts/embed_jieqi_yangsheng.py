#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""將 data/jieqi-yangsheng.json 嵌入 lib/jieqi-yangsheng.js（引擎模板固定）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "jieqi-yangsheng.json"
OUT = ROOT / "lib" / "jieqi-yangsheng.js"

ENGINE = r'''
(function (global) {
  "use strict";
  const DB = global.JIEQI_YANGSHENG_DB;
  if (!DB || !DB.terms) {
    console.warn("[jieqi-yangsheng] DB missing");
    return;
  }

  const ORDER = [
    "小寒","大寒","立春","雨水","驚蟄","春分","清明","穀雨",
    "立夏","小滿","芒種","夏至","小暑","大暑","立秋","處暑",
    "白露","秋分","寒露","霜降","立冬","小雪","大雪","冬至"
  ];

  function pad(n) { return String(n).padStart(2, "0"); }

  function resolveJieqi(date) {
    const y = date.getFullYear();
    const m = date.getMonth() + 1;
    const d = date.getDate();
    let name = null;
    let isToday = false;
    let nextName = null;
    let nextDate = null;
    let currentStart = null;

    const engine = global.HuangliEngine;
    const jieqiTable = (global.HUANGLI_DB && global.HUANGLI_DB.jieqi) || null;

    if (engine && typeof engine.currentJieQiName === "function") {
      name = engine.currentJieQiName(y, m, d);
    }

    if (jieqiTable) {
      const arr = jieqiTable[String(y)] || [];
      const prevYear = jieqiTable[String(y - 1)] || [];
      const seq = [];
      for (const it of prevYear) {
        if (it.m >= 11) seq.push({ y: y - 1, m: it.m, d: it.d, n: it.n });
      }
      for (const it of arr) seq.push({ y: y, m: it.m, d: it.d, n: it.n });
      const nextArr = jieqiTable[String(y + 1)];
      if (nextArr && nextArr[0]) {
        seq.push({ y: y + 1, m: nextArr[0].m, d: nextArr[0].d, n: nextArr[0].n });
      }

      let curIdx = -1;
      for (let i = 0; i < seq.length; i++) {
        const it = seq[i];
        const after =
          y > it.y ||
          (y === it.y && m > it.m) ||
          (y === it.y && m === it.m && d >= it.d);
        if (after) curIdx = i;
      }
      if (curIdx >= 0) {
        name = seq[curIdx].n;
        currentStart = { y: seq[curIdx].y, m: seq[curIdx].m, d: seq[curIdx].d };
        isToday = seq[curIdx].y === y && seq[curIdx].m === m && seq[curIdx].d === d;
        if (curIdx + 1 < seq.length) {
          nextName = seq[curIdx + 1].n;
          nextDate =
            seq[curIdx + 1].y +
            "-" +
            pad(seq[curIdx + 1].m) +
            "-" +
            pad(seq[curIdx + 1].d);
        }
      }
    }

    if (!name) name = "冬至";
    return { name, isToday, nextName, nextDate, currentStart };
  }

  function pickLocale(term, locale) {
    if (!term) return null;
    const loc = locale || (DB.meta && DB.meta.defaultLocale) || "zh-Hant";
    if (loc === "ja" || loc === "ja-JP") {
      const ja = term.ja || {};
      const zh = term.zh || {};
      const filled = ja.summary || (ja.focus && ja.focus.length);
      if (filled) return Object.assign({}, ja, { name: ja.name || zh.name });
      return Object.assign({}, zh);
    }
    return term.zh || term.ja || null;
  }

  function getYangsheng(date, opts) {
    opts = opts || {};
    const locale = opts.locale || "zh-Hant";
    const jq = resolveJieqi(date instanceof Date ? date : new Date(date));
    const term = DB.terms[jq.name];
    if (!term) {
      return {
        name: jq.name,
        isToday: jq.isToday,
        nextName: jq.nextName,
        nextDate: jq.nextDate,
        missing: true,
        content: null,
        meta: DB.meta
      };
    }
    const content = pickLocale(term, locale);
    return {
      name: (content && content.name) || jq.name,
      isToday: jq.isToday,
      nextName: jq.nextName,
      nextDate: jq.nextDate,
      currentStart: jq.currentStart,
      wx: term.wx,
      zang: term.zang,
      order: term.order,
      id: term.id,
      content: content,
      meta: DB.meta,
      missing: false
    };
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderHtml(pack) {
    if (!pack || !pack.content) {
      return '<div class="jys-empty">暫無此節氣養生資料</div>';
    }
    const c = pack.content;
    const badge = pack.isToday
      ? '<span class="jys-badge today">今日交節</span>'
      : "";
    const focus = (c.focus || [])
      .map(function (t) {
        return "<li>" + escapeHtml(t) + "</li>";
      })
      .join("");
    const herbs = (c.herbs || [])
      .map(function (h) {
        return (
          "<li><strong>" +
          escapeHtml(h.name) +
          "</strong>" +
          (h.note ? " — " + escapeHtml(h.note) : "") +
          (h.bencao
            ? '<span class="jys-bencao">《本草》' + escapeHtml(h.bencao) + "</span>"
            : "") +
          "</li>"
        );
      })
      .join("");
    const nextLine = pack.nextName
      ? '<div class="jys-next">下一節氣：' +
        escapeHtml(pack.nextName) +
        (pack.nextDate ? "（" + escapeHtml(pack.nextDate) + "）" : "") +
        "</div>"
      : "";
    return (
      '<div class="jys-meta-row">' +
      '<span class="jys-wx">五行 ' +
      escapeHtml(pack.wx || "—") +
      "</span>" +
      '<span class="jys-zang">臟腑 ' +
      escapeHtml(pack.zang || "—") +
      "</span>" +
      badge +
      "</div>" +
      '<p class="jys-summary">' +
      escapeHtml(c.summary || "") +
      "</p>" +
      nextLine +
      '<div class="jys-block"><h5>養生重點</h5><ul class="jys-focus">' +
      focus +
      "</ul></div>" +
      '<div class="jys-block"><h5>飲食建議</h5><p>' +
      escapeHtml(c.diet || "") +
      "</p></div>" +
      '<div class="jys-block"><h5>作息／起居</h5><p>' +
      escapeHtml(c.routine || "") +
      "</p></div>" +
      (c.emotion
        ? '<div class="jys-block"><h5>情志注意</h5><p>' +
          escapeHtml(c.emotion) +
          "</p></div>"
        : "") +
      (herbs
        ? '<div class="jys-block herbs"><h5>本草參考（神農本草經等）</h5><ul class="jys-herbs">' +
          herbs +
          "</ul></div>"
        : "") +
      '<p class="jys-disc">' +
      escapeHtml((pack.meta && pack.meta.disclaimer) || "") +
      "</p>"
    );
  }

  global.JieqiYangsheng = {
    DB: DB,
    ORDER: ORDER,
    resolveJieqi: resolveJieqi,
    getYangsheng: getYangsheng,
    renderHtml: renderHtml,
    pickLocale: pickLocale
  };
})(typeof window !== "undefined" ? window : globalThis);
'''


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    if len(data.get("terms", {})) != 24:
        raise SystemExit(f"expected 24 terms, got {len(data.get('terms', {}))}")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    out = (
        "/* Auto-generated by scripts/embed_jieqi_yangsheng.py — edit data/jieqi-yangsheng.json */\n"
        f"window.JIEQI_YANGSHENG_DB = {blob};\n"
        f"{ENGINE}"
    )
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
