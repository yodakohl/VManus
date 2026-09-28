#!/usr/bin/env python3
"""Independent arithmetic and fixed-input audit of GDT1075 output."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ART = Path(__file__).resolve().parents[1] / "artifacts"
PARENT = ROOT / "experiments/yolo/gdt1074_physical_paragraph_pair_robustness/artifacts/EVENTS.tsv"
EXPECTED_HASH = "6357927a1a0d4275e057e0bd06043061c5ec749d506dce4174c4924e6abef75f"
BASES = {"aiin", "chedy", "cheol", "cheor", "chor"}
READERS = ("ZL3b", "IT2a", "RF1b")


def rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    checks = {}
    checks["frozen_parent_hash"] = hashlib.sha256(PARENT.read_bytes()).hexdigest() == EXPECTED_HASH
    fixed = [r for r in rows(PARENT) if r["status"] == "INCLUDED" and r["base"] in BASES]
    events = rows(ART / "EVENTS.tsv")
    checks["all_fixed_events_present"] = len(fixed) == len(events) == 214 and {
        (r["edition"], r["base"], r["lead"], r["form"], r["locus"],
         r["physical_folio"], r["physical_paragraph_start"]) for r in fixed
    } == {
        (r["edition"], r["base"], r["lead"], r["form"], r["locus"],
         r["folio"], r["start"]) for r in events
    }
    checks["event_uniqueness_and_domains"] = len({(r["edition"], r["locus"]) for r in events}) == len(events) and all(
        r["edition"] in READERS and r["base"] in BASES and r["lead"] in {"p", "y"}
        and r["form"] == r["lead"] + r["base"] and r["start"] in {"0", "1"}
        and r["section"] and r["hand"] and not r["folio"].startswith("f84")
        for r in events)
    groups = defaultdict(list)
    for r in events:
        groups[(r["edition"], r["base"], r["section"], r["hand"])].append(r)
    strata = rows(ART / "STRATA.tsv")
    checks["one_row_per_stratum"] = len(groups) == len(strata) == 57 and len({
        (r["edition"], r["base"], r["section"], r["hand"]) for r in strata}) == 57
    info = defaultdict(list)
    arithmetic = True
    for s in strata:
        group = groups.get((s["edition"], s["base"], s["section"], s["hand"]), [])
        p = [r for r in group if r["lead"] == "p"]
        y = [r for r in group if r["lead"] == "y"]
        pn, yn = len(p), len(y)
        ps = sum(r["start"] == "1" for r in p)
        ys = sum(r["start"] == "1" for r in y)
        pf = len({r["folio"] for r in p})
        yf = len({r["folio"] for r in y})
        informative = pn >= 2 and yn >= 2 and pf >= 2 and yf >= 2
        direction = "NO_PAIR" if not pn or not yn else (
            "P_GREATER" if ps * yn > ys * pn else
            "Y_GREATER" if ps * yn < ys * pn else "EQUAL")
        expected = (pn, ps, pf, yn, ys, yf, int(informative), direction)
        actual = tuple(int(s[k]) for k in ("p_n", "p_starts", "p_folios", "y_n",
                                         "y_starts", "y_folios", "informative")) + (s["direction"],)
        arithmetic &= expected == actual
        if informative:
            info[s["edition"]].append(s)
    checks["stratum_arithmetic"] = arithmetic
    result = json.loads((ART / "RESULT.json").read_text())
    checks["informative_counts"] = all(
        len(info[ed]) == result["informative_section_hand_strata"][ed]
        and len({s["base"] for s in info[ed]}) == result["informative_bases"][ed]
        and all(s["direction"] == "P_GREATER" for s in info[ed]) for ed in READERS)
    checks["primary_decision"] = (result["primary_decision"] == "WITHIN_REGISTER_FORMAL_DIRECTION"
                                   and len({s["base"] for s in info["ZL3b"]}) >= 3)
    checks["guard_recorded"] = "skipped_forbidden\": 2122" in result["guard"]
    status = "PASS" if all(checks.values()) else "FAIL"
    output = {"status": status, "checks": checks, "event_rows": len(events),
              "strata_rows": len(strata)}
    (ART / "VALIDATION.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
