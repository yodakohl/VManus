#!/usr/bin/env python3
"""Build a source-native human-review packet for unresolved translation anchors."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
SPEC = BASE / "TRANSLATION_ANCHOR_HUMAN_REVIEW_PANEL_SPEC.md"
REGISTRY = RESULTS / "translation_anchor_acquisition_registry_v1.json"
ANNOTATIONS = RESULTS / "existing_human_exact_locus_annotations.tsv"
MANUALS = {
    "ZL3b": ROOT / "transcription/sources/ZL3b-n.txt",
    "IT2a": ROOT / "transcription/sources/IT2a-n.txt",
    "RF1b": ROOT / "transcription/sources/RF1b-e.txt",
}
CATALOGUES = {
    "f2r": BASE / "cache/public_voynich_nu_catalogue/q01.html",
    "f57v": BASE / "cache/public_voynich_nu_catalogue/q08.html",
    "f68r2": BASE / "cache/public_voynich_nu_catalogue/q09.html",
    "f69v": BASE / "cache/public_voynich_nu_catalogue/q10.html",
}
WITNESS_EXPECTED = {
    "f2r": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006078",
    "f57v": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006187",
    "f68r2": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006196",
    "f69v": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006199",
}
OUT_TSV = RESULTS / "translation_anchor_human_review_panel_v1.tsv"
OUT_JSON = RESULTS / "translation_anchor_human_review_panel_v1.json"
OUT_REPORT = RESULTS / "translation_anchor_human_review_panel_v1_report.md"

FIELDS = (
    "anchor_rank", "anchor_id", "page", "physical_locus", "slot_order",
    "visual_register", "relation_grade", "structural_role_hint",
    "structural_role_status", "ZL3b_raw", "IT2a_raw", "RF1b_raw",
    "present_reading_count", "all_present_readings_identical",
    "annotation_scope", "annotation_text", "official_witness_url",
    "requested_new_observation", "admission_test", "claim_ceiling",
)

REQUESTS = {
    "COL001_UNDERPAINT": (
        "A second provenance-clean Voynich-script note physically under paint with an independently readable colour, or the same complete phrase under another green-painted part on a new folio.",
        "New observation must add a readable contrast or a new-folio same-phrase replication; visual similarity alone is insufficient.",
    ),
    "F57_TWO_REGISTER_WHEEL": (
        "A complete readable homologue preserving the four-person and two-label-register topology, orientation, and explicit slot ownership, or an independent Voynich folio repeating the same owned mapping.",
        "Source must fix owners, start, direction, register correspondence, and readable contrasting role values before comparison with the Voynich strings.",
    ),
    "F68_SUN_RING": (
        "A qualified full diplomatic and palaeographic reading of the complete ring, including script identity and uncertainty for the ending, independently of a proposed Sun gloss.",
        "Reader must classify the complete ending as plain script, Voynich script, or unresolved and document each uncertain glyph without using a desired reading.",
    ),
    "F69_ORDERED_28": (
        "A second independently fixed 28-item roster or an authorial readable slot legend that fixes start, direction, and all values without post-hoc spelling selection.",
        "The source must determine all 28 owned values and the cyclic coordinate before any Voynich-form comparison.",
    ),
}

CEILING = "SOURCE_NATIVE_REVIEW_ONLY_NO_LEXICAL_OR_TRANSLATION_CLAIM"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def parse_manual(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    pattern = re.compile(r"^<([^,>]+),[^>]*>\s+(.*)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        locus, raw = match.groups()
        if locus in rows:
            raise ValueError(f"duplicate manual locus {locus} in {path.name}")
        rows[locus] = raw.strip()
    return rows


def parse_annotations() -> dict[str, dict[str, str]]:
    with ANNOTATIONS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        locus = row["locus"]
        if locus in out:
            raise ValueError(f"duplicate exact annotation locus: {locus}")
        out[locus] = row
    return out


def witness_urls() -> dict[str, str]:
    out: dict[str, str] = {}
    for page, path in CATALOGUES.items():
        html = path.read_text(encoding="utf-8")
        match = re.search(
            rf'<TH CLASS="Ph" ID="{re.escape(page)}">.*?'
            r'<A HREF="(https://collections\.library\.yale\.edu/catalog/2002046\?child_oid=\d+)">',
            html,
            flags=re.S,
        )
        if not match or match.group(1) != WITNESS_EXPECTED[page]:
            raise ValueError(f"official witness link drift: {page}")
        out[page] = match.group(1)
    return out


def declarations() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "anchor_rank": 1, "anchor_id": "COL001_UNDERPAINT", "page": "f2r",
            "physical_locus": "f2r.15", "slot_order": 1,
            "visual_register": "UNDERPAINT_NOTE", "relation_grade": "DIRECT_ENCLOSURE_UNDER_PAINT",
            "structural_role_hint": "UNKNOWN", "structural_role_status": "NO_READABLE_VALUE",
        }
    ]
    f57_hints = {
        6: "HOT_POSITION", 7: "MOIST_POSITION", 8: "COLD_POSITION", 9: "DRY_POSITION",
    }
    for locus_number in range(6, 10):
        rows.append({
            "anchor_rank": 2, "anchor_id": "F57_TWO_REGISTER_WHEEL", "page": "f57v",
            "physical_locus": f"f57v.{locus_number}", "slot_order": locus_number - 5,
            "visual_register": "FIGURE_NEAR_LABEL", "relation_grade": "PROXIMITY_ONLY",
            "structural_role_hint": f57_hints[locus_number],
            "structural_role_status": "STRUCTURAL_ANALOGY_ONLY_NOT_A_WORD_GLOSS",
        })
    for locus_number in range(10, 14):
        rows.append({
            "anchor_rank": 2, "anchor_id": "F57_TWO_REGISTER_WHEEL", "page": "f57v",
            "physical_locus": f"f57v.{locus_number}", "slot_order": locus_number - 5,
            "visual_register": "RADIAL_TITLE", "relation_grade": "BETWEEN_FIGURES_PROXIMITY_ONLY",
            "structural_role_hint": "UNKNOWN", "structural_role_status": "NO_READABLE_VALUE",
        })
    rows.append({
        "anchor_rank": 3, "anchor_id": "F68_SUN_RING", "page": "f68r2",
        "physical_locus": "f68r2.31", "slot_order": 1,
        "visual_register": "CIRCULAR_TEXT_AROUND_BOTTOM_SUN_MEDALLION",
        "relation_grade": "DIRECT_CIRCULAR_REGISTER", "structural_role_hint": "SUN_MEDALLION_REGISTER",
        "structural_role_status": "OBJECT_ROLE_ONLY_ENDING_SCRIPT_UNRESOLVED",
    })
    ordered = [f"f69v.{number}" for number in range(7, 32)] + [f"f69v.{number}" for number in range(4, 7)]
    for index, locus in enumerate(ordered, 1):
        rows.append({
            "anchor_rank": 4, "anchor_id": "F69_ORDERED_28", "page": "f69v",
            "physical_locus": locus, "slot_order": index,
            "visual_register": "ORDERED_RADIAL_LABEL", "relation_grade": "DIRECT_RADIAL_SLOT",
            "structural_role_hint": f"X1.{index}", "structural_role_status": "ANONYMOUS_COORDINATE_ONLY",
        })
    if len(rows) != 38 or len({str(row["physical_locus"]) for row in rows}) != 38:
        raise ValueError("fixed locus inventory drift")
    return rows


def main() -> None:
    for path in (OUT_TSV, OUT_JSON, OUT_REPORT):
        if path.exists():
            raise SystemExit(f"refusing to overwrite: {path}")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry["decision"] != "NO_ADMISSIBLE_UNUSED_TRANSLATION_ANCHOR_ACQUISITION_MAP_READY":
        raise ValueError("acquisition registry decision drift")
    manuals = {edition: parse_manual(path) for edition, path in MANUALS.items()}
    annotations = parse_annotations()
    witnesses = witness_urls()
    output: list[dict[str, object]] = []
    present_rows = 0
    absent_rows = 0
    for item in declarations():
        locus = str(item["physical_locus"])
        readings = {edition: manual.get(locus, "ABSENT") for edition, manual in manuals.items()}
        present = [value for value in readings.values() if value != "ABSENT"]
        if not present:
            raise ValueError(f"locus absent in every reading: {locus}")
        present_rows += len(present)
        absent_rows += 3 - len(present)
        annotation = annotations.get(locus)
        annotation_text = ""
        annotation_scope = "NONE"
        if annotation:
            annotation_scope = annotation["relation_scope"]
            annotation_text = " | ".join(filter(None, (annotation["unit_description"], annotation["local_comment"])))
        request, admission = REQUESTS[str(item["anchor_id"])]
        row = dict(item)
        row.update({
            "ZL3b_raw": readings["ZL3b"], "IT2a_raw": readings["IT2a"], "RF1b_raw": readings["RF1b"],
            "present_reading_count": len(present),
            "all_present_readings_identical": int(len(set(present)) == 1),
            "annotation_scope": annotation_scope, "annotation_text": annotation_text,
            "official_witness_url": witnesses[str(item["page"])],
            "requested_new_observation": request, "admission_test": admission, "claim_ceiling": CEILING,
        })
        output.append(row)
    if present_rows != 113 or absent_rows != 1:
        raise ValueError(f"reading coverage drift: present={present_rows}, absent={absent_rows}")

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    inputs = {str(path.relative_to(ROOT)): sha(path) for path in (
        SPEC, REGISTRY, ANNOTATIONS, *MANUALS.values(), *CATALOGUES.values(),
    )}
    family_counts: dict[str, int] = {}
    for row in output:
        key = str(row["anchor_id"])
        family_counts[key] = family_counts.get(key, 0) + 1
    result = {
        "experiment": "TRANSLATION_ANCHOR_HUMAN_REVIEW_PANEL_V1",
        "status": "PASS_SOURCE_NATIVE_ACQUISITION_PACKET",
        "decision": "HUMAN_REVIEW_PACKET_READY_NO_TRANSLATION_CLAIM",
        "counts": {
            "anchor_families": len(family_counts), "physical_loci": len(output),
            "present_reading_rows": present_rows, "absent_reading_rows": absent_rows,
            "official_witness_urls": len(set(witnesses.values())),
            "family_loci": dict(sorted(family_counts.items())),
        },
        "inputs": dict(sorted(inputs.items())),
        "panel_sha256": sha(OUT_TSV),
        "claim_ceiling": "A compact human-review packet exposes the exact unresolved physical records and the observation needed to reopen each route; it supplies no word, sound, language, cipher, plaintext, meaning, or translation.",
    }
    OUT_JSON.write_text(canonical(result), encoding="utf-8")
    OUT_REPORT.write_text(
        "# Translation-anchor human-review panel v1\n\n"
        "Status: **PASS_SOURCE_NATIVE_ACQUISITION_PACKET**.\n\n"
        "The packet contains **38 physical loci** and **113 present native-manual reading rows** "
        "across four unresolved anchor families. IT2a alone lacks `f2r.15`; no reading is imputed. "
        "Each row carries the official Yale witness link, any exact human annotation, the raw ZL3b/IT2a/RF1b text, "
        "and the precise observation needed to reopen its route.\n\n"
        "The English HOT/MOIST/COLD/DRY strings are suffixed `_POSITION` and are structural homologue positions only. "
        "The f69 values are anonymous `X1.1`–`X1.28` coordinates. Nothing in the packet is a lexical reading.\n\n"
        "This is a human-source acquisition aid. It supplies no word, morpheme, sound, language, cipher operation, "
        "plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
