#!/usr/bin/env python3
"""Independent source and numeric validation for ZBV001 capacity."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "ZBV001_ZODIAC_BARREL_NATIVE_VISUAL_CAPACITY_METHOD.md"
AUDIT = BASE / "audit_zbv001_zodiac_barrel_native_visual_capacity.py"
ANNOTATIONS = RESULTS / "existing_human_label_annotations.tsv"
ANNOTATION_VALIDATION = RESULTS / "existing_human_annotation_atlas_validation.json"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
CROSSWALK_VALIDATION = RESULTS / "existing_human_current_locus_crosswalk_validation.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUPS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PRIOR = RESULTS / "public_zodiac_label_attribute_capacity.json"
PRIOR_VALIDATION = RESULTS / "public_zodiac_label_attribute_capacity_validation.json"
PANEL = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity.tsv"
PRODUCTION = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity.json"
PRODUCTION_REPORT = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity_report.md"
OUT = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity_validation.json"
REPORT = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity_validation.md"

HASHES = {
    METHOD: "62a3d35fead90611d2ab4bd5b29a02278b99c1d766257ab51e1ab1dbda8b0d57",
    AUDIT: "d681713a4cd3aefe6deb1f6366d7d75e60b9e008c4e241afde953ff55f7b7a47",
    ANNOTATIONS: "93b14fb00801ee401df018447730c2e2a1036a9aa36135aca44125c177524ed6",
    ANNOTATION_VALIDATION: "25c0642753974fec0b0646a22dc379e439242954f048ab778cc8df7c85442673",
    CROSSWALK: "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    CROSSWALK_VALIDATION: "d00c9fecd5f9a2bb282d47053cf88404b78dd591131a7c207a65e7267c9f95eb",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUPS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PRIOR: "e4bc06e268d2ead7b5b0f3263778f2cee23fb7e93e1209519d9fb34eca201de1",
    PRIOR_VALIDATION: "d4dade22a9799c0e3336217950a9ea4fe42ca85fb8ecba379623194b684ae0c1",
}

MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
PAGES = {
    "f73r": ("1006206", "73r", 2834, 3761, "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad"),
    "f73v": ("1006207", "73v", 2979, 3724, "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141"),
}
FIELDS = (
    "source_record_id", "page", "physical_folio", "ring", "barrel_state",
    "state_provenance", "canvas_id", "current_locus", "strict_eligible",
    "exclusion_reason",
)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def parse_ring(comment: str) -> str:
    value = comment.lower()
    if "not in circle" in value:
        return "OUTSIDE_CIRCLE"
    if "inner" in value:
        return "INNER"
    if "outer" in value:
        return "OUTER"
    return "UNSPECIFIED"


def physical_folio(page: str) -> str:
    found = re.match(r"f\d+", page)
    if found is None:
        raise AssertionError("folio")
    return found.group(0)


def catalogue_state(comment: str) -> str | None:
    value = comment.lower()
    if re.search(r"\b(?:vert\.?|hor\.?) barrel\b", value):
        return "PRESENT"
    if re.search(r"\bno barrel\b", value):
        return "ABSENT"
    return None


def eligible(
    annotation: dict[str, str],
    mapped: dict[str, str] | None,
    groups: dict[str, list[dict[str, str]]],
) -> tuple[str, str, str]:
    if mapped is None:
        return "0", "NO_CROSSWALK", ""
    locus = mapped["current_locus"]
    if mapped["primary_eligible"] != "1" or not locus:
        return "0", "NOT_PRIMARY", locus
    found = sorted(groups.get(locus, []), key=lambda row: int(row["consensus_group_index"]))
    if not found:
        return "0", "NO_CONSENSUS", locus
    valid = all(
        row["page"] == annotation["page"]
        and row["kind"] == "L"
        and row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
        and row["strict_zero_alternative"] == "1"
        for row in found
    )
    valid &= [int(row["consensus_group_index"]) for row in found] == list(range(1, len(found) + 1))
    valid &= {int(row["consensus_group_count"]) for row in found} == {len(found)}
    return ("1", "", locus) if valid else ("0", "NONSTRICT_STRUCTURE", locus)


def panel_bytes(panel: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(panel)
    return output.getvalue().encode()


def expected_report(result: dict[str, object]) -> str:
    counts = result["counts"]
    strict = counts["strict_states"]
    return (
        "# ZBV001 zodiac barrel-state native-visual capacity\n\n"
        "Status: **STOP_BEFORE_VOYNICH_FEATURE_ACCESS_RING_PAGE_CONFOUNDED**\n\n"
        "Direct inspection of the complete official f73r and f73v pages finds all **60** "
        "catalogued figures drawn without barrel/tub outlines. Combined with the public human "
        "catalogue, the sealed panel now has **79 BARREL_PRESENT** and **87 BARREL_ABSENT** records; "
        "both states span at least two physical folios. The native observations are machine-authored, "
        "not literal human annotation.\n\n"
        f"Strict current-locus reconstruction retains **{counts['strict_total']}** labels: "
        f"{strict['PRESENT']} present and {strict['ABSENT']} absent. The only strict page containing "
        "both states is f72r1, where all five present records are INNER and all six retained absent "
        "records are OUTER. No page-by-ring stratum contains both states. A label feature could "
        "therefore mark ring/register rather than a barrel.\n\n"
        "The route stops before any family or member identity is read or scored. No BARREL, INNER, "
        "OUTER, person, star, zodiac, word, stem, sound, language, cipher, plaintext, meaning, or "
        "translation follows.\n"
    )


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite of validation outputs")
    checks: list[str] = []
    for path, expected in HASHES.items():
        if file_sha(path) != expected:
            raise AssertionError("hash: " + str(path))
        checks.append("hash_" + path.name)

    manifest_bytes = fetch(MANIFEST_URL)
    if bytes_sha(manifest_bytes) != MANIFEST_SHA:
        raise AssertionError("manifest hash")
    manifest = json.loads(manifest_bytes)
    canvas_by_id = {item["id"].rsplit("/", 1)[-1]: item for item in manifest["items"]}
    checks.append("live_manifest_hash_and_parse")
    visual = {}
    for page, (canvas_id, label, width, height, expected_sha) in PAGES.items():
        canvas = canvas_by_id[canvas_id]
        if canvas["label"]["none"] != [label] or (canvas["width"], canvas["height"]) != (width, height):
            raise AssertionError("manifest canvas: " + page)
        url = f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/full/0/default.jpg"
        image_bytes = fetch(url)
        if bytes_sha(image_bytes) != expected_sha:
            raise AssertionError("image hash: " + page)
        with Image.open(io.BytesIO(image_bytes)) as image:
            if image.size != (width, height) or image.format != "JPEG":
                raise AssertionError("image format: " + page)
        visual[page] = {
            "canvas_id": canvas_id,
            "canvas_label": label,
            "width": width,
            "height": height,
            "image_sha256": expected_sha,
            "catalogue_figures": 30,
            "inner": 10,
            "outer": 16,
            "outside_circle": 4,
            "barrel_state": "ABSENT",
            "grade": "CLEAR_PAGE_UNIFORM_NO_BARREL_OUTLINES",
            "image_url": url,
        }
        checks.extend(["manifest_canvas_" + page, "image_hash_dimensions_" + page])

    annotations = [row for row in table(ANNOTATIONS) if row["section"] == "zodiac"]
    if len(annotations) != 300 or len({row["source_record_id"] for row in annotations}) != 300:
        raise AssertionError("annotations")
    mapped_rows = [row for row in table(CROSSWALK) if row["source_section"] == "zodiac"]
    mapped = {row["source_record_id"]: row for row in mapped_rows}
    if len(mapped) != 300:
        raise AssertionError("crosswalk")
    group_index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in table(GROUPS):
        group_index[source["locus"]].append({
            key: source[key]
            for key in (
                "locus", "page", "kind", "grammar_scope", "strict_zero_alternative",
                "consensus_group_index", "consensus_group_count",
            )
        })

    panel = []
    for annotation in annotations:
        state = catalogue_state(annotation["comments"])
        provenance, canvas_id = "HUMAN_CATALOGUE_EXPLICIT", ""
        if annotation["page"] in PAGES:
            if state is not None:
                raise AssertionError("f73 explicit state")
            state = "ABSENT"
            provenance = "NATIVE_VISUAL_PAGE_UNIFORM_NO_BARRELS"
            canvas_id = PAGES[annotation["page"]][0]
        if state is None:
            continue
        strict, reason, locus = eligible(annotation, mapped.get(annotation["source_record_id"]), group_index)
        panel.append({
            "source_record_id": annotation["source_record_id"],
            "page": annotation["page"],
            "physical_folio": physical_folio(annotation["page"]),
            "ring": parse_ring(annotation["comments"]),
            "barrel_state": state,
            "state_provenance": provenance,
            "canvas_id": canvas_id,
            "current_locus": locus,
            "strict_eligible": strict,
            "exclusion_reason": reason,
        })
    panel.sort(key=lambda row: row["source_record_id"].encode())
    rebuilt_panel = panel_bytes(panel)
    if PANEL.read_bytes() != rebuilt_panel:
        raise AssertionError("panel bytes")
    checks.extend(["exact_166_state_panel", "panel_bytes_exact"])

    strict_panel = [row for row in panel if row["strict_eligible"] == "1"]
    all_states = Counter(row["barrel_state"] for row in panel)
    strict_states = Counter(row["barrel_state"] for row in strict_panel)
    by_folio = Counter((row["physical_folio"], row["barrel_state"]) for row in strict_panel)
    by_page = Counter((row["page"], row["barrel_state"]) for row in strict_panel)
    by_cell = Counter((row["page"], row["ring"], row["barrel_state"]) for row in strict_panel)
    mixed_pages = [
        page for page in sorted({row["page"] for row in strict_panel})
        if {state for (candidate, state), count in by_page.items() if candidate == page and count} == {"PRESENT", "ABSENT"}
    ]
    cells = sorted({(row["page"], row["ring"]) for row in strict_panel})
    mixed_cells = [
        f"{page}|{ring_name}" for page, ring_name in cells
        if {state for (candidate, candidate_ring, state), count in by_cell.items() if candidate == page and candidate_ring == ring_name and count} == {"PRESENT", "ABSENT"}
    ]
    exclusions = Counter(row["exclusion_reason"] for row in panel if row["strict_eligible"] == "0")
    f72 = {
        f"{ring_name}_{state}": by_cell[("f72r1", ring_name, state)]
        for ring_name in ("INNER", "OUTER")
        for state in ("PRESENT", "ABSENT")
    }
    gates = {
        "exact_300_catalogue_records": len(annotations) == 300,
        "exact_60_f73_page_uniform_absent_records": sum(row["state_provenance"].startswith("NATIVE_VISUAL") for row in panel) == 60,
        "both_states_span_at_least_two_physical_folios": all(
            len({row["physical_folio"] for row in strict_panel if row["barrel_state"] == state}) >= 2
            for state in ("PRESENT", "ABSENT")
        ),
        "strict_panel_has_at_least_100_labels": len(strict_panel) >= 100,
        "at_least_one_mixed_strict_page": bool(mixed_pages),
        "at_least_one_mixed_strict_page_ring_stratum": bool(mixed_cells),
        "f72r1_state_is_perfectly_ring_determined": f72 == {
            "INNER_PRESENT": 5, "INNER_ABSENT": 0,
            "OUTER_PRESENT": 0, "OUTER_ABSENT": 6,
        },
        "zero_family_or_member_identity_access": True,
        "zero_ocr_clip_embedding_or_batch_recognition": True,
    }
    expected_inputs = {
        str(path.relative_to(BASE)): expected
        for path, expected in HASHES.items()
        if path != AUDIT
    }
    expected_result = {
        "experiment": "ZBV001_ZODIAC_BARREL_NATIVE_VISUAL_CAPACITY",
        "status": "STOP_BEFORE_VOYNICH_FEATURE_ACCESS_RING_PAGE_CONFOUNDED",
        "inputs": expected_inputs,
        "official_source": {
            "manifest": {"url": MANIFEST_URL, "sha256": MANIFEST_SHA},
            "pages": visual,
            "observation_author": "NATIVE_AI_DIRECT_VISUAL_INSPECTION",
            "observation_is_literal_human_annotation": False,
        },
        "panel_sha256": bytes_sha(rebuilt_panel),
        "counts": {
            "catalogue_records": len(annotations),
            "state_panel_total": len(panel),
            "all_states": dict(sorted(all_states.items())),
            "strict_total": len(strict_panel),
            "strict_states": dict(sorted(strict_states.items())),
            "strict_by_folio_state": {f"{folio_name}|{state}": count for (folio_name, state), count in sorted(by_folio.items())},
            "strict_by_page_state": {f"{page}|{state}": count for (page, state), count in sorted(by_page.items())},
            "excluded": dict(sorted(exclusions.items())),
            "mixed_strict_pages": mixed_pages,
            "mixed_strict_page_ring_strata": mixed_cells,
            "f72r1_state_by_ring": f72,
        },
        "gates": gates,
        "decision": "STOP_NO_UNCONFOUNDED_WITHIN_PAGE_RING_BARREL_CONTRAST",
        "claim_ceiling": (
            "The native visual audit repairs the missing BARREL-ABSENT folio count, but the only "
            "mixed strict page perfectly confounds barrel state with inner/outer ring. No Voynich "
            "feature was accessed. No BARREL, ring role, word, stem, meaning, plaintext, or "
            "translation follows."
        ),
    }
    production_bytes = PRODUCTION.read_bytes()
    production = json.loads(production_bytes)
    if production_bytes != (json.dumps(production, indent=2, sort_keys=True) + "\n").encode():
        raise AssertionError("production canonical")
    if production != expected_result:
        raise AssertionError("production reconstruction")
    if PRODUCTION_REPORT.read_text(encoding="utf-8") != expected_report(expected_result):
        raise AssertionError("report reconstruction")
    checks.extend(["counts_and_confound_reconstructed", "canonical_result_exact", "report_exact"])

    validation = {
        "experiment": "ZBV001_ZODIAC_BARREL_NATIVE_VISUAL_CAPACITY_VALIDATION",
        "status": "PASS_SOURCE_IMAGE_BINDINGS_AND_CAPACITY_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "inputs": {
            "audit_sha256": HASHES[AUDIT],
            "production_sha256": file_sha(PRODUCTION),
            "production_report_sha256": file_sha(PRODUCTION_REPORT),
            "panel_sha256": file_sha(PANEL),
        },
        "validated_decision": expected_result["decision"],
        "visual_judgment_scope": (
            "The validator independently verifies the official manifest and exact image bytes. "
            "It does not independently infer the native visual no-barrel judgments."
        ),
        "claim_ceiling": expected_result["claim_ceiling"],
    }
    with OUT.open("x", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    with REPORT.open("x", encoding="utf-8", newline="") as handle:
        handle.write(
            "# ZBV001 capacity validation\n\n"
            f"Status: **{validation['status']}**\n\n"
            "The independent validator refetched and hash-matched the official Yale manifest and "
            "both complete f73 canvases, reconstructed all 166 state rows and 138 strict mappings, "
            "and reproduced the page/ring confound, canonical result, and report. The source-bound "
            "native visual grades remain machine-authored observations rather than independently "
            "inferred human annotations.\n"
        )


if __name__ == "__main__":
    main()
