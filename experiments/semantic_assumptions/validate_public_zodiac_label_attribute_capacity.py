#!/usr/bin/env python3
"""Independent live-source validation of zodiac attribute capacity."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PRODUCTION = RESULTS / "public_zodiac_label_attribute_capacity.json"
PRODUCTION_REPORT = RESULTS / "public_zodiac_label_attribute_capacity_report.md"
OUT = RESULTS / "public_zodiac_label_attribute_capacity_validation.json"
REPORT = RESULTS / "public_zodiac_label_attribute_capacity_validation.md"
URL = (
    "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/"
    "work/Notes/614/labtit-best.idx"
)
EXPECTED_SHA = "9267a2bbf2d485320ce8baaa2e3eeaccb6be7a02aa81ee9422a39ba00bef420a"

PATTERNS = {
    "BARREL_PRESENT": r"\b(?:vert\.?|hor\.?) barrel\b",
    "BARREL_ABSENT": r"\bno barrel\b",
    "VERTICAL_BARREL": r"\bvert\.? barrel\b",
    "HORIZONTAL_BARREL": r"\bhor\.? barrel\b",
    "FACING_LEFT": r"\bfacing left\b",
    "FACING_RIGHT": r"\bfacing right\b",
    "MALE": r"\bmale\??\b",
    "FEMALE": r"\bfemale\b|\bwoman\b|\bwomen\b",
    "DRESSED": r"\bdressed\??\b|\bpartdress\b",
    "CROWN": r"\bcrown(?:ed)?\b",
    "STAR_TAIL": r"\b(?:star with tail|tailed star|tail on star|tail to star|striped tail on star)\b",
    "HAT": r"\bhat\b",
    "STAR_ABSENT": r"\bno star\b",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def physical_folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    assert match
    return match.group(0)


def check(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")

    request = urllib.request.Request(URL, headers={"User-Agent": "VManus independent public-source validator"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    checks: list[str] = []
    check(sha_bytes(raw) == EXPECTED_SHA, "live_source_hash", checks)

    rows = []
    for line in raw.decode("utf-8").splitlines():
        fields = line.split("|")
        check(len(fields) == 11, f"eleven_fields_{len(rows)}", checks)
        source_id, section, page, unit, item, _transcriber, _text, _alternate, _obj, _guess, comments = fields
        if section == "zodiac":
            rows.append({
                "source_record_id": f"STOLFI_BEST_{source_id}",
                "page": page.lower(),
                "location": f"{page}.{unit}.{item}".lower(),
                "comments": comments,
            })
    check(len(rows) == 300, "zodiac_count", checks)
    check(len({row["source_record_id"] for row in rows}) == 300, "unique_ids", checks)
    check(len({row["location"] for row in rows}) == 300, "unique_locations", checks)
    check(len({row["page"] for row in rows}) == 12, "page_count", checks)
    check(len({physical_folio(row["page"]) for row in rows}) == 4, "folio_count", checks)

    counts = {}
    selected = {}
    for name, pattern in PATTERNS.items():
        matches = [row for row in rows if re.search(pattern, row["comments"], re.I)]
        selected[name] = matches
        counts[name] = {
            "records": len(matches),
            "pages": sorted({row["page"] for row in matches}),
            "folios": sorted({physical_folio(row["page"]) for row in matches}),
            "by_page": dict(sorted(Counter(row["page"] for row in matches).items())),
        }

    expected_counts = {
        "BARREL_PRESENT": (79, ["f70", "f71", "f72"]),
        "BARREL_ABSENT": (27, ["f72"]),
        "VERTICAL_BARREL": (69, ["f70", "f71", "f72"]),
        "HORIZONTAL_BARREL": (10, ["f70"]),
        "FACING_LEFT": (10, ["f70", "f72"]),
        "FACING_RIGHT": (1, ["f70"]),
        "MALE": (25, ["f70", "f72", "f73"]),
        "FEMALE": (1, ["f72"]),
        "DRESSED": (32, ["f70", "f71", "f72"]),
        "CROWN": (2, ["f72"]),
        "STAR_TAIL": (40, ["f70", "f72", "f73"]),
        "HAT": (1, ["f70"]),
        "STAR_ABSENT": (1, ["f72"]),
    }
    for name, (number, folios) in expected_counts.items():
        check(counts[name]["records"] == number, f"{name}_count", checks)
        check(counts[name]["folios"] == folios, f"{name}_folios", checks)

    check(
        selected["STAR_ABSENT"][0]["source_record_id"] == "STOLFI_BEST_0684"
        and selected["STAR_ABSENT"][0]["page"] == "f72v2",
        "exact_star_conflict_record",
        checks,
    )
    prod = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    check(prod["status"] == "STOP_UNSCORED_NO_TRANSFERABLE_EXPLICIT_BINARY_ATTRIBUTE", "status", checks)
    check(prod["decision"] == "STOP_BEFORE_VOYNICH_FEATURE_ACCESS", "decision", checks)
    check(prod["public_source"] == {"url": URL, "sha256": EXPECTED_SHA}, "source_binding", checks)
    check(prod["counts"]["zodiac_records"] == 300, "stored_records", checks)
    for name in PATTERNS:
        check(prod["counts"]["attributes"][name] == counts[name], f"stored_{name}", checks)
    check(not any(value["eligible"] for value in prod["binary_contrasts"].values()), "no_eligible_contrast", checks)
    check(prod["source_disagreement"]["adjudication"] == "UNKNOWN", "conflict_unknown", checks)
    check(all(prod["gates"].values()), "all_gates", checks)
    report_text = PRODUCTION_REPORT.read_text(encoding="utf-8")
    for witness in ("all **27** explicit `no barrel` records are on f72", "Stolfi record 0684 says `no star`", "No BARREL, LEFT, RIGHT"):
        check(witness in report_text, f"report_{len(checks)}", checks)

    result = {
        "experiment": "PUBLIC_ZODIAC_LABEL_ATTRIBUTE_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
        "checks": len(checks),
        "failures": [],
        "inputs": {
            "public_source_sha256": EXPECTED_SHA,
            "production_json_sha256": sha(PRODUCTION),
            "production_report_sha256": sha(PRODUCTION_REPORT),
        },
        "reconstructed": {
            "zodiac_records": 300,
            "pages": 12,
            "physical_folios": 4,
            "attribute_counts": counts,
            "eligible_binary_contrasts": 0,
        },
        "decision": prod["decision"],
        "claim_ceiling": prod["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Public zodiac-label attribute capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION**\n\n"
        f"A clean implementation downloaded and hashed the public 1998 catalogue and passed **{len(checks)}** checks. "
        "It reconstructed 300 unique zodiac records, all explicit attribute counts, the one-folio barrel-negative bottleneck, "
        "and the f72v2 star-source conflict. No Voynich string was scored.\n\n"
        "Decision: **STOP_BEFORE_VOYNICH_FEATURE_ACCESS**.\n",
        encoding="utf-8",
    )
    print(json.dumps({"checks": len(checks), "status": result["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
