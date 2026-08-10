#!/usr/bin/env python3
"""Audit public human data for a fair zodiac FEMALE/WOMAN stem test.

This is a source-capacity audit only.  It never reads Voynich strings as a
target, scores a stem, or treats a missing human tag as a negative label.
"""

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
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
ROLE_ATLAS = RESULTS / "public_circle_block_role_atlas.tsv"

URLS = {
    "zandbergen_labels": "https://www.voynich.nu/extra/labels.html",
    "stolfi_label_index": (
        "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/"
        "work/Notes/614/labtit-best.idx"
    ),
    "stolfi_f70v1": "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/040/html/f70v1.htm",
    "stolfi_f70v2": "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/040/html/f70v2.htm",
    "stolfi_f72r3": "https://www.ic.unicamp.br/~stolfi/EXPORT/voynich/Notes/040/html/f72r3.htm",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(item: tuple[str, str]) -> tuple[str, bytes]:
    name, url = item
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-ZFC001/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError((name, response.status))
        return name, response.read()


def visible_html(data: bytes) -> str:
    raw = data.decode("latin-1", errors="replace")
    raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.I | re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def breast_table(data: bytes, page: str) -> list[dict[str, str]]:
    raw = html.unescape(data.decode("latin-1", errors="replace"))
    blocks = [b for b in re.findall(r"<pre[^>]*>(.*?)</pre>", raw, re.I | re.S) if "brst" in b]
    if len(blocks) != 1:
        raise AssertionError((page, len(blocks)))
    lines = [re.sub(r"<[^>]+>", "", line) for line in blocks[0].splitlines()]
    patterns = {
        "f70v2": re.compile(r"^\s*(inner|outer)\s+(S[12]\.\d+)\s+\S+\s+(yes|no|\?)\s+"),
        "f70v1": re.compile(r"^\s*(inner|outer)\s+(S[12]\.\d+)\s+\S+\s+\S+\s+\S+\s+(yes|no|\?)\s+"),
        "f72r3": re.compile(r"^\s*(inner|middle|outer)\s+([XYZ]\.\d+)\s+\S+\s+\S+\s+\S+\s+(yes|no|\?)\s+"),
    }
    rows = []
    for line in lines:
        match = patterns[page].match(line)
        if match:
            rows.append({"page": page, "band": match.group(1), "label": match.group(2), "visible_breasts": match.group(3)})
    return rows


def label_counts(data: bytes) -> dict[str, object]:
    rows = []
    for line in data.decode("utf-8").splitlines():
        fields = line.split("|")
        if len(fields) != 11:
            raise AssertionError("public label index schema drift")
        if fields[1].lower() == "zodiac":
            rows.append(fields)
    comments = [row[10].lower() for row in rows]
    male = [comment for comment in comments if re.search(r"\bmale\b", comment)]
    female = [comment for comment in comments if re.search(r"\bfemale\b", comment)]
    uncertain_male = [comment for comment in male if "male?" in comment or "possible male" in comment]
    return {
        "zodiac_records": len(rows),
        "male_mentioned": len(male),
        "male_mentioned_uncertain": len(uncertain_male),
        "male_mentioned_unqualified": len(male) - len(uncertain_male),
        "female_mentioned": len(female),
        "neither_sex_mentioned_unknown": len(rows) - len({i for i, c in enumerate(comments) if re.search(r"\b(?:male|female)\b", c)}),
        "male_pages": sorted({row[2].lower() for row in rows if re.search(r"\bmale\b", row[10].lower())}),
        "female_pages": sorted({row[2].lower() for row in rows if re.search(r"\bfemale\b", row[10].lower())}),
    }


def crosswalk_counts() -> tuple[bytes, dict[str, object]]:
    data = CROSSWALK.read_bytes()
    rows = list(csv.DictReader(data.decode("utf-8").splitlines(), delimiter="\t"))
    chosen = [
        row for row in rows
        if (row["source_page"] == "f70v1" and row["source_unit"] == "s")
        or (row["source_page"] == "f70v2" and row["source_unit"] in {"s1", "s2"})
        or (row["source_page"] == "f72r3" and row["source_unit"] in {"x", "y", "z"})
    ]
    by_page = {}
    for page in ("f70v1", "f70v2", "f72r3"):
        page_rows = [row for row in chosen if row["source_page"] == page]
        by_page[page] = {
            "rows": len(page_rows),
            "all_three_readings": sum(row["all_three_present"] == "1" for row in page_rows),
            "primary_eligible": sum(row["primary_eligible"] == "1" for row in page_rows),
            "match_statuses": dict(sorted(Counter(row["match_status"] for row in page_rows).items())),
        }
    return data, {"rows": len(chosen), "by_page": by_page}


def circle_scope() -> tuple[bytes, dict[str, object]]:
    data = ROLE_ATLAS.read_bytes()
    rows = list(csv.DictReader(data.decode("utf-8").splitlines(), delimiter="\t"))
    pages = sorted({row["page"] for row in rows})
    folios = sorted({row["physical_folio"] for row in rows})
    classes = Counter({page: next(row["public_page_class"] for row in rows if row["page"] == page) for page in pages}.values())
    return data, {
        "page_panels": len(pages),
        "physical_folios": len(folios),
        "includes_f71": "f71r" in pages and "f71v" in pages,
        "public_classes": dict(sorted(classes.items())),
    }


def reconstruct() -> dict[str, object]:
    with ThreadPoolExecutor(max_workers=5) as executor:
        sources = dict(executor.map(fetch, URLS.items()))
    labels_text = visible_html(sources["zandbergen_labels"])
    assert "essentially every degree of each sign has a female figure holding a star" in labels_text
    assert "one is missing so we only have 299" in labels_text

    source_label_counts = label_counts(sources["stolfi_label_index"])
    tables = []
    for page in ("f70v1", "f70v2", "f72r3"):
        tables.extend(breast_table(sources[f"stolfi_{page}"], page))
    table_counts = Counter(row["visible_breasts"] for row in tables)
    per_page = {
        page: dict(sorted(Counter(row["visible_breasts"] for row in tables if row["page"] == page).items()))
        for page in ("f70v1", "f70v2", "f72r3")
    }
    assert per_page == {
        "f70v1": {"?": 4, "no": 3, "yes": 8},
        "f70v2": {"?": 5, "no": 4, "yes": 20},
        "f72r3": {"?": 5, "no": 5, "yes": 20},
    }

    crosswalk_data, crosswalk = crosswalk_counts()
    role_data, scope = circle_scope()
    gates = {
        "public_f67_f73_scope_is_independent_and_includes_f71": True,
        "zodiac_label_comments_supply_exhaustive_slot_sex_states": False,
        "unmentioned_sex_can_be_treated_as_female": False,
        "visible_breast_no_can_be_treated_as_male": False,
        "explicit_three_state_tables_cover_all_four_zodiac_folios": False,
        "explicit_three_state_tables_cover_at_least_three_physical_folios": False,
        "all_table_slots_have_primary_current_locus_mappings": False,
        "fair_held_folio_female_stem_test_is_identified": False,
    }
    return {
        "audit_id": "ZFC001",
        "date": "2026-08-10",
        "method": "PUBLIC_HUMAN_HTML_AND_MANUAL_TRANSCRIPTION_CROSSWALK_ONLY_NO_OCR_NO_IMAGE_MODEL_NO_TARGET_SCORE",
        "sources": {
            name: {"url": URLS[name], "bytes": len(data), "sha256": digest(data)}
            for name, data in sorted(sources.items())
        } | {
            "local_public_circle_role_atlas": {"path": str(ROLE_ATLAS.relative_to(ROOT)), "bytes": len(role_data), "sha256": digest(role_data)},
            "local_public_label_crosswalk": {"path": str(CROSSWALK.relative_to(ROOT)), "bytes": len(crosswalk_data), "sha256": digest(crosswalk_data)},
        },
        "public_circle_scope": scope,
        "public_zodiac_label_comment_capacity": source_label_counts,
        "explicit_visible_breast_tables": {
            "pages": ["f70v1", "f70v2", "f72r3"],
            "physical_folios": ["f70", "f72"],
            "slots": len(tables),
            "states": {"yes": table_counts["yes"], "no": table_counts["no"], "unknown": table_counts["?"]},
            "per_page": per_page,
            "interpretation": "observable visible-breast annotation, not an authorial or biological sex truth",
        },
        "current_locus_crosswalk": crosswalk,
        "gates": gates,
        "decision": "STOP_UNSCORED_NO_INDEPENDENT_FEMALE_NEGATIVE_PANEL",
        "claim_ceiling": (
            "Public human data confirm that female-looking figures dominate the zodiac, but do not provide "
            "an exhaustive, independent slot-level FEMALE versus non-FEMALE truth panel. No Voynich stem "
            "can fairly be called WOMAN or FEMALE from these data."
        ),
        "reopen_only_with": (
            "an exhaustive public/manual slot table with explicit FEMALE, NON_FEMALE, and UNKNOWN states "
            "on all four surviving zodiac folios or an independent multi-folio figure-label panel, plus exact current-locus ownership"
        ),
    }


def report(result: dict[str, object]) -> str:
    comments = result["public_zodiac_label_comment_capacity"]
    tables = result["explicit_visible_breast_tables"]
    mapping = result["current_locus_crosswalk"]["by_page"]
    return f"""# Public zodiac FEMALE/WOMAN capacity audit

Decision: **{result['decision']}**.

The page grouping is public data, not user supplied. The validated public f67--f73 block contains 26 panels on seven folios and includes f71. Its zodiac subset occupies f70--f73.

The broad public description says that essentially every zodiac degree has a female figure holding a star. That is useful document context, but it is not an exhaustive per-slot contrast. The older public label catalogue has {comments['zodiac_records']} zodiac records: {comments['male_mentioned']} mention male ({comments['male_mentioned_uncertain']} hedged), only {comments['female_mentioned']} mentions female, and {comments['neither_sex_mentioned_unknown']} mention neither. The unmentioned records remain **UNKNOWN**, not FEMALE.

The strongest existing per-slot observable is a human `brst` table recording visible female breasts as `yes/no/?`. It covers only f70v1, f70v2, and f72r3: {tables['slots']} slots total ({tables['states']['yes']} yes, {tables['states']['no']} no, {tables['states']['unknown']} unknown) on only two physical folios. Moreover, `no visible breasts` is not `male`; the source itself warns that clothing and drawing quality can hide them.

All 74 table rows have three current manual readings, but f70v1 has only {mapping['f70v1']['primary_eligible']}/15 conservative current-locus mappings; f70v2 and f72r3 have {mapping['f70v2']['primary_eligible']}/29 and {mapping['f72r3']['primary_eligible']}/30. Even perfect mapping would leave only two independent folios.

Therefore a stem search would either turn missing tags into invented negatives, equate an anatomical visibility proxy with sex, or validate on the same folios used to define the classes. No Voynich string was opened or scored.

Reopen only with {result['reopen_only_with']}.

Public sources: [zodiac-label overview]({URLS['zandbergen_labels']}), [human label catalogue]({URLS['stolfi_label_index']}), [f70v1 table]({URLS['stolfi_f70v1']}), [f70v2 table]({URLS['stolfi_f70v2']}), [f72r3 table]({URLS['stolfi_f72r3']}).
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rebuilt = reconstruct()
    rendered = report(rebuilt)
    if args.write:
        RESULT.write_text(json.dumps(rebuilt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT.write_text(rendered, encoding="utf-8")
        print(f"wrote {RESULT.relative_to(ROOT)} and {REPORT.relative_to(ROOT)}")
    else:
        assert json.loads(RESULT.read_text(encoding="utf-8")) == rebuilt
        assert REPORT.read_text(encoding="utf-8") == rendered
        print("ZFC001 producer reconstruction PASS")


if __name__ == "__main__":
    main()
