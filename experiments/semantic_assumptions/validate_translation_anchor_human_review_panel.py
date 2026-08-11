#!/usr/bin/env python3
"""Independent validation of the translation-anchor human-review panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
SPEC = BASE / "TRANSLATION_ANCHOR_HUMAN_REVIEW_PANEL_SPEC.md"
BUILDER = BASE / "build_translation_anchor_human_review_panel.py"
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
WITNESSES = {
    "f2r": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006078",
    "f57v": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006187",
    "f68r2": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006196",
    "f69v": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006199",
}
TSV = RESULTS / "translation_anchor_human_review_panel_v1.tsv"
RESULT = RESULTS / "translation_anchor_human_review_panel_v1.json"
REPORT = RESULTS / "translation_anchor_human_review_panel_v1_report.md"
OUT_JSON = RESULTS / "translation_anchor_human_review_panel_v1_validation.json"
OUT_REPORT = RESULTS / "translation_anchor_human_review_panel_v1_validation_report.md"

FROZEN = {
    SPEC: "562b2b9fd0daeef9e3f368726721574e478f3bcf14ca8b58f8ed66d270c1d5b2",
    BUILDER: "0604fb625149cf61d0779958dc8e991e4d0c25ba93dde0b46fa661e9cc1e4e62",
    REGISTRY: "0a285cccbe9507987978157d4511ce099e2a3ff54e22f416297337c89089ad14",
    ANNOTATIONS: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    MANUALS["ZL3b"]: "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    MANUALS["IT2a"]: "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    MANUALS["RF1b"]: "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
    CATALOGUES["f2r"]: "6c82ec816e5b4b320d87551af34eaec768531e32bde00afc4415652f5ddc10a4",
    CATALOGUES["f57v"]: "ce3df63cb48cf440faa2d637b382b7665b992a55709b5a721fdce078e21e42d7",
    CATALOGUES["f68r2"]: "56b592284239fbd4d2ffabac2c534207c2e8a6da00ce4570d526544b9793f977",
    CATALOGUES["f69v"]: "2f15159cd9ea04213f2031fbbebe33e3b057795656e349bf765e4f0344ff2ec5",
    TSV: "20134182f439a742a3de825858aae4f879faab8f5f17f28a676f48b318a7d563",
    RESULT: "4549089c4f60d95f941ec4d91413212710a5fb86d6e5d7bddbfa515500a40409",
    REPORT: "1fe64eeb40f5db20580d75a268bad35267a3b01f19d3d08f215d47b5fa4e238b",
}

F57_HINTS = ("HOT_POSITION", "MOIST_POSITION", "COLD_POSITION", "DRY_POSITION")
F69_ORDER = tuple([f"f69v.{n}" for n in range(7, 32)] + [f"f69v.{n}" for n in range(4, 7)])
CEILING = "SOURCE_NATIVE_REVIEW_ONLY_NO_LEXICAL_OR_TRANSLATION_CLAIM"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def strict_json(path: Path) -> object:
    raw = path.read_text(encoding="utf-8")
    value = json.loads(raw, object_pairs_hook=reject_duplicates)
    if json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n" != raw:
        raise ValueError(f"noncanonical JSON: {path.name}")
    return value


def tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def manual_rows(path: Path) -> dict[str, str]:
    pattern = re.compile(r"^<([^,>]+),[^>]*>\s+(.*)$")
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            locus, value = match.groups()
            if locus in out:
                raise ValueError(f"duplicate source locus: {locus}")
            out[locus] = value.strip()
    return out


def expected_descriptor(locus: str) -> tuple[str, str, str, str, str, str]:
    if locus == "f2r.15":
        return ("1", "COL001_UNDERPAINT", "1", "UNDERPAINT_NOTE", "DIRECT_ENCLOSURE_UNDER_PAINT", "UNKNOWN")
    if locus.startswith("f57v."):
        n = int(locus.split(".")[1])
        if 6 <= n <= 9:
            return ("2", "F57_TWO_REGISTER_WHEEL", str(n - 5), "FIGURE_NEAR_LABEL", "PROXIMITY_ONLY", F57_HINTS[n - 6])
        if 10 <= n <= 13:
            return ("2", "F57_TWO_REGISTER_WHEEL", str(n - 5), "RADIAL_TITLE", "BETWEEN_FIGURES_PROXIMITY_ONLY", "UNKNOWN")
    if locus == "f68r2.31":
        return ("3", "F68_SUN_RING", "1", "CIRCULAR_TEXT_AROUND_BOTTOM_SUN_MEDALLION", "DIRECT_CIRCULAR_REGISTER", "SUN_MEDALLION_REGISTER")
    if locus in F69_ORDER:
        index = F69_ORDER.index(locus) + 1
        return ("4", "F69_ORDERED_28", str(index), "ORDERED_RADIAL_LABEL", "DIRECT_RADIAL_SLOT", f"X1.{index}")
    raise ValueError(f"unexpected locus: {locus}")


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite validation artifacts")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")

    table = tsv_rows(TSV)
    if len(table) != 38 or len({row["physical_locus"] for row in table}) != 38:
        raise ValueError("physical-locus inventory mismatch")
    expected_order = ["f2r.15"] + [f"f57v.{n}" for n in range(6, 14)] + ["f68r2.31"] + list(F69_ORDER)
    if [row["physical_locus"] for row in table] != expected_order:
        raise ValueError("physical-locus order mismatch")
    checks.extend(("exact_38_physical_loci", "frozen_locus_order"))

    source = {edition: manual_rows(path) for edition, path in MANUALS.items()}
    annotation = {row["locus"]: row for row in tsv_rows(ANNOTATIONS)}
    present_total = 0
    absent_total = 0
    family_requests: dict[str, tuple[str, str]] = {}
    for row in table:
        locus = row["physical_locus"]
        expected = expected_descriptor(locus)
        observed = tuple(row[key] for key in (
            "anchor_rank", "anchor_id", "slot_order", "visual_register", "relation_grade", "structural_role_hint",
        ))
        if observed != expected or row["claim_ceiling"] != CEILING:
            raise ValueError(f"descriptor mismatch: {locus}")
        if row["page"] != locus.split(".")[0]:
            raise ValueError(f"page/locus mismatch: {locus}")
        values: list[str] = []
        for edition in ("ZL3b", "IT2a", "RF1b"):
            expected_raw = source[edition].get(locus, "ABSENT")
            if row[f"{edition}_raw"] != expected_raw:
                raise ValueError(f"raw reading mismatch: {edition} {locus}")
            if expected_raw != "ABSENT":
                values.append(expected_raw)
        present_total += len(values)
        absent_total += 3 - len(values)
        if int(row["present_reading_count"]) != len(values):
            raise ValueError(f"reading count mismatch: {locus}")
        if int(row["all_present_readings_identical"]) != int(len(set(values)) == 1):
            raise ValueError(f"reading equality mismatch: {locus}")
        source_annotation = annotation.get(locus)
        expected_scope = source_annotation["relation_scope"] if source_annotation else "NONE"
        expected_text = "" if not source_annotation else " | ".join(filter(None, (
            source_annotation["unit_description"], source_annotation["local_comment"],
        )))
        if row["annotation_scope"] != expected_scope or row["annotation_text"] != expected_text:
            raise ValueError(f"annotation mismatch: {locus}")
        if row["official_witness_url"] != WITNESSES[row["page"]]:
            raise ValueError(f"witness mismatch: {locus}")
        request_pair = (row["requested_new_observation"], row["admission_test"])
        if not all(request_pair) or family_requests.setdefault(row["anchor_id"], request_pair) != request_pair:
            raise ValueError(f"family request drift: {locus}")
        checks.append(f"row:{locus}")
    if present_total != 113 or absent_total != 1:
        raise ValueError("reading coverage mismatch")
    if table[0]["IT2a_raw"] != "ABSENT" or any(row["IT2a_raw"] == "ABSENT" for row in table[1:]):
        raise ValueError("IT2a absence pattern mismatch")
    checks.extend(("exact_113_present_reading_rows", "sole_absent_IT2a_f2r15", "four_consistent_family_requests"))

    for page, path in CATALOGUES.items():
        html = path.read_text(encoding="utf-8")
        start = html.index(f'ID="{page}"')
        next_page = html.find('CLASS="Ph" ID=', start + 1)
        block = html[start:next_page if next_page >= 0 else len(html)]
        links = re.findall(r'https://collections\.library\.yale\.edu/catalog/2002046\?child_oid=\d+', block)
        if not links or links[0] != WITNESSES[page]:
            raise ValueError(f"catalogue reconstruction mismatch: {page}")
        checks.append(f"official_witness:{page}")

    result = strict_json(RESULT)
    if not isinstance(result, dict):
        raise ValueError("result must be object")
    if result["experiment"] != "TRANSLATION_ANCHOR_HUMAN_REVIEW_PANEL_V1":
        raise ValueError("experiment mismatch")
    if result["status"] != "PASS_SOURCE_NATIVE_ACQUISITION_PACKET" or result["decision"] != "HUMAN_REVIEW_PACKET_READY_NO_TRANSLATION_CLAIM":
        raise ValueError("status/decision mismatch")
    expected_counts = {
        "absent_reading_rows": 1, "anchor_families": 4,
        "family_loci": {"COL001_UNDERPAINT": 1, "F57_TWO_REGISTER_WHEEL": 8, "F68_SUN_RING": 1, "F69_ORDERED_28": 28},
        "official_witness_urls": 4, "physical_loci": 38, "present_reading_rows": 113,
    }
    if result["counts"] != expected_counts or result["panel_sha256"] != FROZEN[TSV]:
        raise ValueError("summary reconstruction mismatch")
    expected_inputs = {str(path.relative_to(ROOT)): FROZEN[path] for path in (
        SPEC, REGISTRY, ANNOTATIONS, *MANUALS.values(), *CATALOGUES.values(),
    )}
    if result["inputs"] != dict(sorted(expected_inputs.items())):
        raise ValueError("input binding mismatch")
    checks.extend(("canonical_result_json", "status_decision", "summary_counts", "input_bindings"))

    expected_report = (
        "# Translation-anchor human-review panel v1\n\n"
        "Status: **PASS_SOURCE_NATIVE_ACQUISITION_PACKET**.\n\n"
        "The packet contains **38 physical loci** and **113 present native-manual reading rows** across four unresolved anchor families. IT2a alone lacks `f2r.15`; no reading is imputed. Each row carries the official Yale witness link, any exact human annotation, the raw ZL3b/IT2a/RF1b text, and the precise observation needed to reopen its route.\n\n"
        "The English HOT/MOIST/COLD/DRY strings are suffixed `_POSITION` and are structural homologue positions only. The f69 values are anonymous `X1.1`–`X1.28` coordinates. Nothing in the packet is a lexical reading.\n\n"
        "This is a human-source acquisition aid. It supplies no word, morpheme, sound, language, cipher operation, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != expected_report:
        raise ValueError("report mismatch")
    checks.append("exact_report_bytes")

    validation = {
        "experiment": "TRANSLATION_ANCHOR_HUMAN_REVIEW_PANEL_V1_VALIDATION",
        "status": "PASS_INDEPENDENT_SOURCE_NATIVE_RECONSTRUCTION",
        "decision": "VALIDATED_HUMAN_REVIEW_PACKET_NO_TRANSLATION_CLAIM",
        "check_count": len(checks), "checks": checks,
        "validated_result_sha256": FROZEN[RESULT], "validated_panel_sha256": FROZEN[TSV],
        "counts": expected_counts,
        "claim_ceiling": "Validation confirms only the source-native review packet, physical-locus order, alternate readings, annotations, witness links, and acquisition requests; no lexical or translation claim follows.",
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# Translation-anchor human-review panel validation\n\n"
        f"PASS: **{len(checks)}** checks independently reconstruct the 38-locus inventory, 113 present readings, sole IT2a absence, four official witness links, role safeguards, annotations, source bindings, summary, and report.\n\n"
        "This validates an acquisition packet only. No word, sound, language, cipher, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
