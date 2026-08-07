#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速檢驗節氣表與兩人八字／日課（供 Docker / CI 使用）。"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    ok: list[str] = []

    def check(cond: bool, msg: str) -> None:
        (ok if cond else errors).append(msg)

    db_path = ROOT / "data" / "core-db.json"
    check(db_path.is_file(), f"core-db exists: {db_path}")
    db = json.loads(db_path.read_text(encoding="utf-8"))
    check(db.get("meta", {}).get("jieqiEngine") == "lunar_python", "jieqiEngine=lunar_python")

    liqiu = next(x for x in db["jieqi"]["2026"] if x["n"] == "立秋")
    check(liqiu["m"] == 8 and liqiu["d"] == 7, f"2026 立秋 = {liqiu['m']}-{liqiu['d']} (expect 8-7)")

    try:
        from lunar_python import Solar
    except ImportError:
        errors.append("lunar_python not installed")
        Solar = None  # type: ignore

    if Solar:
        jq = Solar.fromYmd(2026, 8, 7).getLunar().getJieQi()
        check(jq == "立秋", f"lunar_python 2026-08-07 jieqi={jq}")

        def pillars(ymd: str, hour: int):
            y, m, d = map(int, ymd.split("-"))
            ec = Solar.fromYmdHms(y, m, d, hour, 0, 0).getLunar().getEightChar()
            return ec.getYear(), ec.getMonth(), ec.getDay(), ec.getTime()

        check(
            pillars("1985-08-28", 8) == ("乙丑", "甲申", "己亥", "戊辰"),
            "bazi 1985 乙丑甲申己亥戊辰",
        )
        check(
            pillars("1995-11-08", 4) == ("乙亥", "丙戌", "癸卯", "甲寅"),
            "bazi 1995 乙亥丙戌癸卯甲寅",
        )

    facts_path = ROOT / "data" / "daily-facts-2026.json"
    check(facts_path.is_file(), "daily-facts-2026.json exists")
    if facts_path.is_file():
        facts = json.loads(facts_path.read_text(encoding="utf-8"))
        f07 = facts["2026-08-07"]["fact"]
        check(f07.get("prevJieQi") == "立秋", f"facts 8/7 prevJieQi={f07.get('prevJieQi')}")
        f06 = facts["2026-08-06"]["fact"]
        check(
            f06.get("siJueLi") and f06["siJueLi"].get("jieqi") in ("立秋",),
            f"facts 8/6 四絕日 si={f06.get('siJueLi')}",
        )
        a = facts["2026-08-07"]["personals"]["p1985"]
        b = facts["2026-08-07"]["personals"]["p1995"]
        check(a["flowDay"] == f07["dayGZ"], "p1985 flowDay 對齊")
        check(b["flowDay"] == f07["dayGZ"], "p1995 flowDay 對齊")
        check(
            a["score"] != b["score"] or a["shiShen"] != b["shiShen"],
            f"兩人運勢有差異 {a['score']}/{b['score']} {a['shiShen']}/{b['shiShen']}",
        )

    # 當前節氣函式（與前端 HuangliEngine 相同邏輯）
    def current_jq(y: int, m: int, d: int) -> str:
        arr = db["jieqi"][str(y)]
        cur = "冬至"
        prev = db["jieqi"].get(str(y - 1))
        if prev:
            cur = prev[23]["n"]
        for item in arr:
            if m > item["m"] or (m == item["m"] and d >= item["d"]):
                cur = item["n"]
        return cur

    check(current_jq(2026, 8, 6) == "大暑", "8/6 → 大暑")
    check(current_jq(2026, 8, 7) == "立秋", "8/7 → 立秋")
    check(current_jq(2026, 8, 8) == "立秋", "8/8 → 立秋")

    print(f"OK {len(ok)}")
    for m in ok:
        print("  ✓", m)
    if errors:
        print(f"FAIL {len(errors)}")
        for m in errors:
            print("  ✗", m)
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
