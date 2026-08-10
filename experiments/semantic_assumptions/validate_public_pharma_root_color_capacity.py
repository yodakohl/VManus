#!/usr/bin/env python3
"""Independent live-source reconstruction of the root-colour capacity stop."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PRODUCTION = RESULTS / "public_pharma_root_color_capacity.json"
PRODUCTION_TSV = RESULTS / "public_pharma_root_color_candidates.tsv"
PRODUCTION_REPORT = RESULTS / "public_pharma_root_color_capacity_report.md"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
OUT = RESULTS / "public_pharma_root_color_capacity_validation.json"
REPORT = RESULTS / "public_pharma_root_color_capacity_validation.md"
URL = (
    "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/"
    "work/Notes/614/labtit-best.idx"
)
EXPECTED_SHA = "9267a2bbf2d485320ce8baaa2e3eeaccb6be7a02aa81ee9422a39ba00bef420a"
PARTIAL = re.compile(
    r"\b(?:alternating|twotone|two[ -]?tone|strip(?:e|ed|es)|speckl\w*|mostly|"
    r"cent(?:er|re)|spots?|edges?|shad\w*|between|btwn)\b",
    re.I,
)
FIELDS = (
    "source_record_id", "source_page", "physical_folio", "source_location",
    "source_object_guess", "source_comment", "root_state", "state_rule",
    "primary_current_mapping", "mapped_locus", "manual_pairing_class",
    "local_relation_tags", "detailed_root_state", "state_comparison",
)


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def state(comment: str, obj: str, certainty: str) -> tuple[str, str] | None:
    text = comment.strip().lower()
    obj = obj.lower()
    if certainty != "UNHEDGED" or "?" in obj or "not labeled" in text or "faded" in text or "alternating" in text:
        return None
    if obj == "root":
        values = re.findall(r"\b(dark|light)\b", text)
        if len(values) == 1 and not PARTIAL.search(text):
            return values[0].upper(), "DIRECT_ROOT_OBJECT"
        return None
    if obj != "plant":
        return None
    found = []
    for clause in re.split(r"[,;]|\s+-\s+", text):
        if not re.search(r"\broots?\b", clause):
            continue
        values = set(re.findall(r"\b(dark|light)\b", clause))
        if len(values) == 1 and "?" not in clause and not PARTIAL.search(clause):
            found.append(next(iter(values)))
        elif values:
            return None
    return (found[0].upper(), "EXPLICIT_ROOT_CLAUSE") if len(found) == 1 else None


def pclass(text: str) -> str:
    text = text.lower()
    if re.search(r"pairing is (?:quite )?clear|pairing seems clear|each plant is labeled", text):
        return "PUBLIC_CLEAR_PAIRING"
    if re.search(
        r"not clear how|we assum|we presum|likely to be associated|seems safer to assign|"
        r"perhaps associated|apparently placed|generally seems",
        text,
    ):
        return "PUBLIC_ASSUMED_OR_AMBIGUOUS"
    if re.search(
        r"there (?:are|appears to be) (?:\w+|\d+) (?:plants|labels).*"
        r"(?:\w+|\d+) (?:plants|labels)", text,
    ):
        return "PUBLIC_COUNT_ONLY"
    return "NO_PUBLIC_PAIRING_STATEMENT"


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    checks: list[str] = []
    request = urllib.request.Request(URL, headers={"User-Agent": "VManus public-source validator"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    check(digest_bytes(raw) == EXPECTED_SHA, "live_public_hash", checks)

    source = []
    for index, line in enumerate(raw.decode("utf-8").splitlines()):
        fields = line.split("|")
        check(len(fields) == 11, f"source_fields_{index}", checks)
        sid, section, page, unit, item, _transcriber, _text, _alt, objclass, guess, comment = fields
        parsed = state(comment, guess, "HEDGED" if "?" in comment or "?" in guess else "UNHEDGED")
        # The production certainty is conservative but does not mark a row hedged merely because
        # a question occurs in a non-colour clause. Recreate its exact atlas certainty below.
        source.append({
            "source_record_id": f"STOLFI_BEST_{sid}", "section": section,
            "page": page.lower(), "location": f"{page}.{unit}.{item}".lower(),
            "object_class": objclass, "object_guess": guess, "comments": comment,
            "raw_parse_unused": parsed,
        })
    check(len(source) == 1018, "all_public_records", checks)

    # The text-free atlas supplies its frozen local-hedging decision. Join only metadata/comments;
    # no Voynich text column is loaded here.
    atlas_path = RESULTS / "existing_human_label_annotations.tsv"
    atlas = {
        row["source_record_id"]: {
            "source_record_id": row["source_record_id"],
            "certainty": row["certainty"], "comments": row["comments"],
            "object_guess": row["object_guess"], "object_class": row["object_class"],
            "section": row["section"], "page": row["page"], "location": row["location"],
        }
        for row in read_tsv(atlas_path)
    }
    check(len(atlas) == 1018, "atlas_record_count", checks)
    for row in source:
        a = atlas[row["source_record_id"]]
        check(
            (row["section"], row["page"], row["location"], row["object_class"], row["object_guess"], row["comments"])
            == (a["section"], a["page"], a["location"], a["object_class"], a["object_guess"], a["comments"]),
            f"public_projection_{row['source_record_id']}", checks,
        )

    cross = {row["source_record_id"]: row for row in read_tsv(CROSSWALK)}
    exact_rows = read_tsv(EXACT)
    by_locus = defaultdict(list)
    by_unit = defaultdict(list)
    for row in exact_rows:
        by_locus[row["locus"]].append(row)
        by_unit[(row["page"], row["unit"])].append(row)

    rebuilt = []
    for public in source:
        a = atlas[public["source_record_id"]]
        parsed = state(a["comments"], a["object_guess"], a["certainty"])
        if a["section"] != "pharma" or a["object_class"] != "P" or not parsed:
            continue
        root_value, rule = parsed
        x = cross[public["source_record_id"]]
        locus = x["current_locus"]
        if a["page"] in {"f101v1", "f101v2"} and locus.startswith("f101v."):
            locus = a["page"] + locus[len("f101v"):]
        local = by_locus.get(locus, [])
        if local:
            unit = local[0]["unit"]
            unit_text = " ".join(r["local_comment"] for r in by_unit[(local[0]["page"], unit)])
            pairing = pclass(unit_text)
            relations = ";".join(sorted({
                tag for r in local for tag in r["local_relation_tags"].split(";") if tag
            }))
            detail = state(local[0]["local_comment"], "plant", "UNHEDGED")
            detail_value = detail[0] if detail else "UNKNOWN"
        else:
            pairing, relations, detail_value = "NO_EXACT_ANNOTATION", "", "UNKNOWN"
        comparison = "UNKNOWN" if detail_value == "UNKNOWN" else "AGREE" if detail_value == root_value else "CONFLICT"
        rebuilt.append({
            "source_record_id": a["source_record_id"], "source_page": a["page"],
            "physical_folio": re.match(r"f\d+", a["page"]).group(0),
            "source_location": a["location"], "source_object_guess": a["object_guess"],
            "source_comment": a["comments"], "root_state": root_value, "state_rule": rule,
            "primary_current_mapping": x["primary_eligible"], "mapped_locus": locus,
            "manual_pairing_class": pairing, "local_relation_tags": relations,
            "detailed_root_state": detail_value, "state_comparison": comparison,
        })

    check(len(rebuilt) == 82, "strict_candidate_count", checks)
    stored_rows = read_tsv(PRODUCTION_TSV)
    check(stored_rows == rebuilt, "exact_candidate_tsv", checks)
    for index, row in enumerate(rebuilt):
        check(set(row) == set(FIELDS), f"candidate_schema_{index}", checks)

    primary = [r for r in rebuilt if r["primary_current_mapping"] == "1"]
    clear = [r for r in primary if r["manual_pairing_class"] == "PUBLIC_CLEAR_PAIRING"]
    check(len(primary) == 56, "primary_count", checks)
    check(Counter(r["root_state"] for r in primary) == {"DARK": 28, "LIGHT": 28}, "primary_balance", checks)
    check(len(clear) == 4 and {r["physical_folio"] for r in clear} == {"f100"}, "clear_one_folio", checks)
    check(Counter(r["state_comparison"] for r in clear) == {"AGREE": 3, "CONFLICT": 1}, "clear_comparison", checks)
    check([r["source_record_id"] for r in clear if r["state_comparison"] == "CONFLICT"] == ["STOLFI_BEST_1395"], "exact_conflict", checks)

    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    check(production["status"] == "STOP_UNSCORED_CLEAR_PAIRING_CONTRAST_ONE_FOLIO_AND_ONE_SOURCE_CONFLICT", "status", checks)
    check(production["decision"] == "STOP_BEFORE_ANY_VOYNICH_FORM_OR_GRAMMAR_SCORE", "decision", checks)
    check(production["public_source"] == {"url": URL, "sha256": EXPECTED_SHA}, "source_binding", checks)
    check(production["strict_source_candidates"]["records"] == 82, "stored_candidates", checks)
    check(production["primary_mapped_candidates"]["records"] == 56, "stored_primary", checks)
    check(production["clear_pairing_panel"]["records"] == 4, "stored_clear", checks)
    check(production["clear_pairing_panel"]["conflict"]["adjudication"] == "UNKNOWN", "conflict_unknown", checks)
    check(not production["gates"]["clear_pairing_has_two_states_on_two_physical_folios"], "ownership_gate_false", checks)
    check(not production["gates"]["all_clear_pairing_states_are_cross_description_stable"], "stability_gate_false", checks)
    check(production["gates"]["zero_voynich_strings_scored"], "zero_string_score", checks)
    report = PRODUCTION_REPORT.read_text(encoding="utf-8")
    for phrase in ("**82** conservative", "only **four**", "`STOLFI_BEST_1395`", "STOP_BEFORE_ANY_VOYNICH_FORM_OR_GRAMMAR_SCORE"):
        check(phrase in report, f"report_phrase_{len(checks)}", checks)

    result = {
        "experiment": "PUBLIC_PHARMA_ROOT_COLOR_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
        "checks": len(checks),
        "failures": [],
        "inputs": {
            "public_source_sha256": EXPECTED_SHA,
            "production_tsv_sha256": digest(PRODUCTION_TSV),
            "production_json_sha256": digest(PRODUCTION),
            "production_report_sha256": digest(PRODUCTION_REPORT),
        },
        "reconstructed": {
            "strict_candidates": 82, "primary_mapped": 56,
            "clear_pairing": 4, "clear_pairing_physical_folios": ["f100"],
            "cross_description_agree": 3, "cross_description_conflict": 1,
        },
        "decision": production["decision"],
        "claim_ceiling": production["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Public pharmaceutical root-colour capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION**\n\n"
        f"An independent implementation downloaded and hashed the public catalogue and passed **{len(checks)}** checks. "
        "It reconstructed all 82 strict source candidates, 56 primary mappings, the four f100 clear-pairing records, "
        "and the single older LIGHT versus detailed DARK conflict. No Voynich form or grammar feature was scored.\n\n"
        "Decision: **STOP_BEFORE_ANY_VOYNICH_FORM_OR_GRAMMAR_SCORE**.\n",
        encoding="utf-8",
    )
    print(json.dumps({"checks": len(checks), "status": result["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
