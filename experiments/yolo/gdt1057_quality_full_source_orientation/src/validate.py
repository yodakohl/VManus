#!/usr/bin/env python3
"""Independent artifact/source audit for the bounded historical control."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
ART = HERE / "artifacts"
QUADS = ("hot_dry", "hot_moist", "cold_dry", "cold_moist")


def table(name: str) -> list[dict]:
    with (ART / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def probability(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.get(q, 0) for q in QUADS) + 2
    return {q: (counts.get(q, 0) + .5) / total for q in QUADS}


def main() -> None:
    checks = []
    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    raw = (HERE / "runtime/G600005.html").read_bytes()
    check(hashlib.sha256(raw).hexdigest() == result["source_sha256"], "source hash")
    target_path = ROOT / result["target_artifact"]
    check(hashlib.sha256(target_path.read_bytes()).hexdigest() == result["target_sha256"], "target hash")
    source = raw.decode("latin1")
    markers = [m.end() for m in re.finditer(re.escape("<h2>An Irish Materia Medica</h2>"), source)]
    check(len(markers) == 3, "third part boundary")
    body = source[markers[-1]:]
    starts = list(re.finditer(r"<p>\s*([0-9]+)\.\s*", body, re.I))
    entries = table("SOURCE_ENTRIES.tsv")
    check(len(starts) == len(entries) == result["entry_count"] == 286, "numbered entry census")
    numbers = [int(m.group(1)) for m in starts]
    check(numbers == sorted(set(numbers)), "monotonic unique source numbers")
    missing = sorted(set(range(1, 293)) - set(numbers))
    check(missing == result["missing_numbered_starts"] == [7, 20, 160, 181, 220, 244], "six unnumbered positions retained")
    for index, (start, row) in enumerate(zip(starts, entries)):
        check(int(row["ordinal"]) == index + 1 and int(row["source_number"]) == numbers[index], f"entry identity {index+1}")
        end = starts[index+1].start() if index+1 < len(starts) else len(body)
        stripped = re.sub(r"<[^>]+>", " ", body[start.end():end])
        opening = " ".join(html.unescape(stripped).split())[:320]
        check(hashlib.sha256(opening.encode("utf-8")).hexdigest() == row["opening_sha256"], f"opening conservation {index+1}")
        terms = re.findall(r"\b(?:hot|cold|dry|wet|moist)\b", opening, re.I)
        temps = [x.lower() for x in terms if x.lower() in ("hot", "cold")]
        moist = [x.lower() for x in terms if x.lower() in ("dry", "wet", "moist")]
        expected = temps[0] + "_" + ("dry" if moist[0] == "dry" else "moist") if len(temps) == len(moist) == 1 else ""
        check(expected == row["auto_category"], f"fixed first320 classification {index+1}")
    candidates = [r for r in entries if r["auto_category"]]
    auto = table("AUTO_CANDIDATES.tsv")
    check(candidates == auto and len(auto) == result["automatic_candidates"] == 213, "all auto candidates")
    manual = table("MANUAL_AUDIT.tsv")
    check(len(manual) == result["manual_audited"] == 213, "complete manual decisions")
    by_id = {int(r["ordinal"]): r for r in manual}
    check(set(by_id) == {int(r["ordinal"]) for r in candidates}, "no manual omission or addition")
    excluded = {n for n, r in by_id.items() if r["decision"] == "EXCLUDE"}
    check(excluded == {31, 250, 276}, "three documented non-drug or split-source exclusions")
    check(all(r["decision"] in ("ACCEPT", "EXCLUDE") and r["reason"] for r in manual), "audits have decisions and reasons")
    counts = Counter(r["auto_category"] for r in candidates if by_id[int(r["ordinal"])]["decision"] == "ACCEPT")
    check(dict(counts) == result["source_counts"] and sum(counts.values()) == result["accepted_count"] == 210, "audited category counts")
    check(counts["hot_dry"] == 125 and counts["cold_dry"] == 52 and counts["hot_moist"] == 25 and counts["cold_moist"] == 8, "source totals")
    check(abs(result["dry_fraction_lower_bound_all_292"] - 177/292) < 1e-12, "all missing moist lower bound")
    published = [r for r in table("ORIENTATION_RECHECK.tsv")]
    with target_path.open(newline="", encoding="utf-8") as handle:
        frozen = [r for r in csv.DictReader(handle, delimiter="\t") if r["scope"] == "ALL_SAFE_NO_F1R" and r["mode"] == "EXACT_Y_EY"]
    check(len(frozen) == len(published) == 8, "all frozen orientations")
    source_p = probability(counts)
    for row in frozen:
        actual = next(x for x in published if x["assignment_id"] == row["assignment_id"])
        values = {q: int(row[q]) for q in QUADS}
        check(sum(values.values()) == 192 and all(int(actual[q]) == values[q] for q in QUADS), "unchanged target row " + row["assignment_id"])
        other_p = probability(values)
        distance = sum(abs(source_p[q] - other_p[q]) for q in QUADS) / 2
        check(abs(float(actual["total_variation_smoothed"]) - distance) < .0000006, "TV replay " + row["assignment_id"])
    check([r["assignment_id"] for r in published] == [r["assignment_id"] for r in sorted(published, key=lambda r: (float(r["total_variation_smoothed"]), r["assignment_id"]))], "rank order")
    check(published[0]["assignment_id"] == "KT_THERMAL__K_HOT__CH_DRY", "working orientation first")
    output = {"status": "PASS", "checks": len(checks), "entry_count": len(entries), "accepted": sum(counts.values()), "excluded": sorted(excluded), "missing_numbered_starts": missing}
    (ART / "VALIDATION.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output))


if __name__ == "__main__":
    main()
