#!/usr/bin/env python3
"""Independent nonimporting validation of the ZFC001 public-data stop."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments/semantic_assumptions/results"
RESULT = RESULTS / "public_zodiac_female_capacity.json"
REPORT = RESULTS / "public_zodiac_female_capacity_report.md"
VALIDATION = RESULTS / "public_zodiac_female_capacity_validation.json"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
ROLE_ATLAS = RESULTS / "public_circle_block_role_atlas.tsv"

SOURCES = [
    ("stolfi_f70v1", "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/040/html/f70v1.htm"),
    ("stolfi_f70v2", "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/040/html/f70v2.htm"),
    ("stolfi_f72r3", "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/040/html/f72r3.htm"),
    ("stolfi_label_index", "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/work/Notes/614/labtit-best.idx"),
    ("zandbergen_labels", "https://www.voynich.nu/extra/labels.html"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retrieve(item: tuple[str, str]) -> tuple[str, str, bytes]:
    name, url = item
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-ZFC001-validator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise AssertionError((name, response.status))
        return name, url, response.read()


def plain(data: bytes) -> str:
    text = data.decode("latin-1", "replace")
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def table_states(data: bytes, page: str) -> Counter:
    text = html.unescape(data.decode("latin-1", "replace"))
    block = next(block for block in re.findall(r"<pre[^>]*>(.*?)</pre>", text, re.I | re.S) if "brst" in block)
    clean = "\n".join(re.sub(r"<[^>]+>", "", line) for line in block.splitlines())
    patterns = {
        "f70v1": r"^[ \t]*(?:inner|outer)[ \t]+S[12]\.\d+[ \t]+\S+[ \t]+\S+[ \t]+\S+[ \t]+(yes|no|\?)[ \t]+",
        "f70v2": r"^[ \t]*(?:inner|outer)[ \t]+S[12]\.\d+[ \t]+\S+[ \t]+(yes|no|\?)[ \t]+",
        "f72r3": r"^[ \t]*(?:inner|middle|outer)[ \t]+[XYZ]\.\d+[ \t]+\S+[ \t]+\S+[ \t]+\S+[ \t]+(yes|no|\?)[ \t]+",
    }
    return Counter(re.findall(patterns[page], clean, re.M))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = json.loads(RESULT.read_text("utf-8"))
    checks = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        fetched = {name: (url, data) for name, url, data in executor.map(retrieve, SOURCES)}
    for name, (url, data) in fetched.items():
        assert result["sources"][name] == {"url": url, "bytes": len(data), "sha256": sha(data)}
        checks += 3

    overview = plain(fetched["zandbergen_labels"][1])
    assert "essentially every degree of each sign has a female figure holding a star" in overview
    assert "one is missing so we only have 299" in overview
    checks += 2

    zodiac = []
    for line in fetched["stolfi_label_index"][1].decode("utf-8").splitlines():
        fields = line.split("|")
        assert len(fields) == 11
        if fields[1] == "zodiac":
            zodiac.append(fields)
    comments = [row[10].lower() for row in zodiac]
    male_indices = {i for i, value in enumerate(comments) if re.search(r"\bmale\b", value)}
    female_indices = {i for i, value in enumerate(comments) if re.search(r"\bfemale\b", value)}
    uncertain = {i for i in male_indices if "male?" in comments[i] or "possible male" in comments[i]}
    counts = result["public_zodiac_label_comment_capacity"]
    assert len(zodiac) == counts["zodiac_records"] == 300
    assert len(male_indices) == counts["male_mentioned"] == 25
    assert len(uncertain) == counts["male_mentioned_uncertain"] == 21
    assert len(male_indices - uncertain) == counts["male_mentioned_unqualified"] == 4
    assert len(female_indices) == counts["female_mentioned"] == 1
    assert len(zodiac) - len(male_indices | female_indices) == counts["neither_sex_mentioned_unknown"] == 274
    checks += 6

    expected = {
        "f70v1": Counter({"yes": 8, "?": 4, "no": 3}),
        "f70v2": Counter({"yes": 20, "?": 5, "no": 4}),
        "f72r3": Counter({"yes": 20, "?": 5, "no": 5}),
    }
    actual = {page: table_states(fetched[f"stolfi_{page}"][1], page) for page in expected}
    assert actual == expected
    combined = sum(actual.values(), Counter())
    tables = result["explicit_visible_breast_tables"]
    assert tables["slots"] == sum(combined.values()) == 74
    assert tables["states"] == {"yes": 48, "no": 12, "unknown": 14}
    assert tables["physical_folios"] == ["f70", "f72"]
    checks += 4

    crosswalk_data = CROSSWALK.read_bytes()
    atlas_data = ROLE_ATLAS.read_bytes()
    assert result["sources"]["local_public_label_crosswalk"]["sha256"] == sha(crosswalk_data)
    assert result["sources"]["local_public_circle_role_atlas"]["sha256"] == sha(atlas_data)
    checks += 2
    crosswalk = list(csv.DictReader(crosswalk_data.decode().splitlines(), delimiter="\t"))
    specs = {"f70v1": {"s"}, "f70v2": {"s1", "s2"}, "f72r3": {"x", "y", "z"}}
    for page, units in specs.items():
        rows = [row for row in crosswalk if row["source_page"] == page and row["source_unit"] in units]
        stored = result["current_locus_crosswalk"]["by_page"][page]
        assert len(rows) == stored["rows"]
        assert sum(row["all_three_present"] == "1" for row in rows) == stored["all_three_readings"]
        assert sum(row["primary_eligible"] == "1" for row in rows) == stored["primary_eligible"]
        assert dict(sorted(Counter(row["match_status"] for row in rows).items())) == stored["match_statuses"]
        checks += 4

    atlas = list(csv.DictReader(atlas_data.decode().splitlines(), delimiter="\t"))
    pages = {row["page"] for row in atlas}
    folios = {row["physical_folio"] for row in atlas}
    assert len(pages) == result["public_circle_scope"]["page_panels"] == 26
    assert len(folios) == result["public_circle_scope"]["physical_folios"] == 7
    assert {"f71r", "f71v"} <= pages and result["public_circle_scope"]["includes_f71"] is True
    checks += 3

    assert result["decision"] == "STOP_UNSCORED_NO_INDEPENDENT_FEMALE_NEGATIVE_PANEL"
    assert all(value is False for key, value in result["gates"].items() if key != "public_f67_f73_scope_is_independent_and_includes_f71")
    assert result["gates"]["public_f67_f73_scope_is_independent_and_includes_f71"] is True
    assert "No Voynich stem can fairly be called WOMAN or FEMALE" in result["claim_ceiling"]
    checks += 4

    report = REPORT.read_text("utf-8")
    for phrase in [
        "public data, not user supplied",
        "274 mention neither",
        "48 yes, 12 no, 14 unknown",
        "only two physical folios",
        "No Voynich string was opened or scored",
    ]:
        assert phrase in report
        checks += 1

    validation = {
        "audit_id": "ZFC001",
        "checks": checks,
        "decision": result["decision"],
        "discrepancies": 0,
        "method": "INDEPENDENT_NONIMPORTING_LIVE_PUBLIC_TEXT_RECONSTRUCTION_NO_OCR_NO_IMAGE_MODEL_NO_TARGET_SCORE",
        "status": "PASS",
    }
    if args.write:
        VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {VALIDATION.relative_to(ROOT)}")
    else:
        assert json.loads(VALIDATION.read_text("utf-8")) == validation
        print(f"ZFC001 independent validation PASS ({checks} checks)")


if __name__ == "__main__":
    main()
