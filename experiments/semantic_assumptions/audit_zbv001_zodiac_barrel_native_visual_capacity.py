#!/usr/bin/env python3
"""Build the text-sealed ZBV001 zodiac barrel-state capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "ZBV001_ZODIAC_BARREL_NATIVE_VISUAL_CAPACITY_METHOD.md"
ANNOTATIONS = RESULTS / "existing_human_label_annotations.tsv"
ANNOTATION_VALIDATION = RESULTS / "existing_human_annotation_atlas_validation.json"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
CROSSWALK_VALIDATION = RESULTS / "existing_human_current_locus_crosswalk_validation.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUPS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PRIOR = RESULTS / "public_zodiac_label_attribute_capacity.json"
PRIOR_VALIDATION = RESULTS / "public_zodiac_label_attribute_capacity_validation.json"
OUT_TSV = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity.tsv"
OUT = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity.json"
REPORT = RESULTS / "zbv001_zodiac_barrel_native_visual_capacity_report.md"

EXPECTED = {
    METHOD: "62a3d35fead90611d2ab4bd5b29a02278b99c1d766257ab51e1ab1dbda8b0d57",
    ANNOTATIONS: "93b14fb00801ee401df018447730c2e2a1036a9aa36135aca44125c177524ed6",
    ANNOTATION_VALIDATION: "25c0642753974fec0b0646a22dc379e439242954f048ab778cc8df7c85442673",
    CROSSWALK: "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    CROSSWALK_VALIDATION: "d00c9fecd5f9a2bb282d47053cf88404b78dd591131a7c207a65e7267c9f95eb",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUPS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PRIOR: "e4bc06e268d2ead7b5b0f3263778f2cee23fb7e93e1209519d9fb34eca201de1",
    PRIOR_VALIDATION: "d4dade22a9799c0e3336217950a9ea4fe42ca85fb8ecba379623194b684ae0c1",
}

MANIFEST = {
    "url": "https://collections.library.yale.edu/manifests/2002046",
    "sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
}
VISUAL = {
    "f73r": {
        "canvas_id": "1006206",
        "canvas_label": "73r",
        "width": 2834,
        "height": 3761,
        "image_sha256": "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad",
        "catalogue_figures": 30,
        "inner": 10,
        "outer": 16,
        "outside_circle": 4,
        "barrel_state": "ABSENT",
        "grade": "CLEAR_PAGE_UNIFORM_NO_BARREL_OUTLINES",
    },
    "f73v": {
        "canvas_id": "1006207",
        "canvas_label": "73v",
        "width": 2979,
        "height": 3724,
        "image_sha256": "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141",
        "catalogue_figures": 30,
        "inner": 10,
        "outer": 16,
        "outside_circle": 4,
        "barrel_state": "ABSENT",
        "grade": "CLEAR_PAGE_UNIFORM_NO_BARREL_OUTLINES",
    },
}

FIELDS = (
    "source_record_id", "page", "physical_folio", "ring", "barrel_state",
    "state_provenance", "canvas_id", "current_locus", "strict_eligible",
    "exclusion_reason",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    if not match:
        raise AssertionError(page)
    return match.group(0)


def ring(comments: str) -> str:
    lower = comments.lower()
    if "not in circle" in lower:
        return "OUTSIDE_CIRCLE"
    if "inner" in lower:
        return "INNER"
    if "outer" in lower:
        return "OUTER"
    return "UNSPECIFIED"


def explicit_state(comments: str) -> str | None:
    lower = comments.lower()
    if re.search(r"\b(?:vert\.?|hor\.?) barrel\b", lower):
        return "PRESENT"
    if re.search(r"\bno barrel\b", lower):
        return "ABSENT"
    return None


def strict_status(
    annotation: dict[str, str],
    crosswalk: dict[str, str] | None,
    group_lookup: dict[str, list[dict[str, str]]],
) -> tuple[bool, str, str]:
    if crosswalk is None:
        return False, "NO_CROSSWALK", ""
    locus = crosswalk["current_locus"]
    if crosswalk["primary_eligible"] != "1" or not locus:
        return False, "NOT_PRIMARY", locus
    groups = sorted(group_lookup.get(locus, ()), key=lambda row: int(row["consensus_group_index"]))
    if not groups:
        return False, "NO_CONSENSUS", locus
    if (
        any(
            row["page"] != annotation["page"]
            or row["kind"] != "L"
            or row["grammar_scope"] != "DIAGNOSTIC_NONPROSE"
            or row["strict_zero_alternative"] != "1"
            for row in groups
        )
        or [int(row["consensus_group_index"]) for row in groups] != list(range(1, len(groups) + 1))
        or {int(row["consensus_group_count"]) for row in groups} != {len(groups)}
    ):
        return False, "NONSTRICT_STRUCTURE", locus
    return True, "", locus


def write_tsv(path: Path, panel: list[dict[str, str]]) -> None:
    if path.exists():
        raise SystemExit("refusing overwrite: " + str(path))
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(panel)


def render_report(result: dict[str, object]) -> str:
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
    if any(path.exists() for path in (OUT_TSV, OUT, REPORT)):
        raise SystemExit("refusing overwrite of ZBV001 outputs")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise AssertionError("hash mismatch: " + str(path))
    statuses = {
        ANNOTATION_VALIDATION: "PASS_EXISTING_HUMAN_ANNOTATION_ATLAS_VALIDATION",
        CROSSWALK_VALIDATION: "PASS_INDEPENDENT_CLUSTERED_CURRENT_LOCUS_CROSSWALK_VALIDATION",
        GROUPS_VALIDATION: "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION",
        PRIOR_VALIDATION: "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
    }
    for path, status in statuses.items():
        if json.loads(path.read_text(encoding="utf-8"))["status"] != status:
            raise AssertionError("validation status: " + str(path))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    if prior["decision"] != "STOP_BEFORE_VOYNICH_FEATURE_ACCESS":
        raise AssertionError("prior capacity stop")

    annotations = [row for row in read_tsv(ANNOTATIONS) if row["section"] == "zodiac"]
    if len(annotations) != 300 or len({row["source_record_id"] for row in annotations}) != 300:
        raise AssertionError("zodiac catalogue")
    crosswalk_rows = [row for row in read_tsv(CROSSWALK) if row["source_section"] == "zodiac"]
    crosswalk = {row["source_record_id"]: row for row in crosswalk_rows}
    if len(crosswalk) != 300:
        raise AssertionError("zodiac crosswalk")
    group_lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in read_tsv(GROUPS):
        group_lookup[source["locus"]].append({
            name: source[name]
            for name in (
                "locus", "page", "kind", "grammar_scope", "strict_zero_alternative",
                "consensus_group_index", "consensus_group_count",
            )
        })

    panel = []
    for annotation in annotations:
        state = explicit_state(annotation["comments"])
        provenance = "HUMAN_CATALOGUE_EXPLICIT"
        canvas_id = ""
        if annotation["page"] in VISUAL:
            if state is not None:
                raise AssertionError("f73 catalogue already supplies barrel state")
            state = "ABSENT"
            provenance = "NATIVE_VISUAL_PAGE_UNIFORM_NO_BARRELS"
            canvas_id = VISUAL[annotation["page"]]["canvas_id"]
        if state is None:
            continue
        strict, reason, locus = strict_status(annotation, crosswalk.get(annotation["source_record_id"]), group_lookup)
        panel.append({
            "source_record_id": annotation["source_record_id"],
            "page": annotation["page"],
            "physical_folio": folio(annotation["page"]),
            "ring": ring(annotation["comments"]),
            "barrel_state": state,
            "state_provenance": provenance,
            "canvas_id": canvas_id,
            "current_locus": locus,
            "strict_eligible": "1" if strict else "0",
            "exclusion_reason": reason,
        })
    panel.sort(key=lambda row: row["source_record_id"].encode())
    if len(panel) != 166:
        raise AssertionError("state panel")
    write_tsv(OUT_TSV, panel)

    strict_panel = [row for row in panel if row["strict_eligible"] == "1"]
    state_counts = Counter(row["barrel_state"] for row in panel)
    strict_counts = Counter(row["barrel_state"] for row in strict_panel)
    by_folio = Counter((row["physical_folio"], row["barrel_state"]) for row in strict_panel)
    by_page = Counter((row["page"], row["barrel_state"]) for row in strict_panel)
    by_page_ring = Counter((row["page"], row["ring"], row["barrel_state"]) for row in strict_panel)
    pages = sorted({row["page"] for row in strict_panel})
    mixed_pages = [page for page in pages if {state for (candidate, state), count in by_page.items() if candidate == page and count} == {"PRESENT", "ABSENT"}]
    page_ring_pairs = sorted({(row["page"], row["ring"]) for row in strict_panel})
    mixed_page_rings = [
        f"{page}|{ring_name}"
        for page, ring_name in page_ring_pairs
        if {state for (candidate_page, candidate_ring, state), count in by_page_ring.items() if candidate_page == page and candidate_ring == ring_name and count} == {"PRESENT", "ABSENT"}
    ]
    exclusion_counts = Counter(row["exclusion_reason"] for row in panel if row["strict_eligible"] == "0")
    f72 = {
        f"{ring_name}_{state}": by_page_ring[("f72r1", ring_name, state)]
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
        "at_least_one_mixed_strict_page_ring_stratum": bool(mixed_page_rings),
        "f72r1_state_is_perfectly_ring_determined": f72 == {
            "INNER_PRESENT": 5, "INNER_ABSENT": 0,
            "OUTER_PRESENT": 0, "OUTER_ABSENT": 6,
        },
        "zero_family_or_member_identity_access": True,
        "zero_ocr_clip_embedding_or_batch_recognition": True,
    }
    result = {
        "experiment": "ZBV001_ZODIAC_BARREL_NATIVE_VISUAL_CAPACITY",
        "status": "STOP_BEFORE_VOYNICH_FEATURE_ACCESS_RING_PAGE_CONFOUNDED",
        "inputs": {str(path.relative_to(BASE)): expected for path, expected in EXPECTED.items()},
        "official_source": {
            "manifest": MANIFEST,
            "pages": {
                page: {
                    **observation,
                    "image_url": f"https://collections.library.yale.edu/iiif/2/{observation['canvas_id']}/full/full/0/default.jpg",
                }
                for page, observation in VISUAL.items()
            },
            "observation_author": "NATIVE_AI_DIRECT_VISUAL_INSPECTION",
            "observation_is_literal_human_annotation": False,
        },
        "panel_sha256": sha(OUT_TSV),
        "counts": {
            "catalogue_records": len(annotations),
            "state_panel_total": len(panel),
            "all_states": dict(sorted(state_counts.items())),
            "strict_total": len(strict_panel),
            "strict_states": dict(sorted(strict_counts.items())),
            "strict_by_folio_state": {f"{folio_name}|{state}": count for (folio_name, state), count in sorted(by_folio.items())},
            "strict_by_page_state": {f"{page}|{state}": count for (page, state), count in sorted(by_page.items())},
            "excluded": dict(sorted(exclusion_counts.items())),
            "mixed_strict_pages": mixed_pages,
            "mixed_strict_page_ring_strata": mixed_page_rings,
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
    if not all(value for name, value in gates.items() if name != "at_least_one_mixed_strict_page_ring_stratum"):
        raise AssertionError("capacity prerequisites")
    if gates["at_least_one_mixed_strict_page_ring_stratum"]:
        raise AssertionError("unexpected unconfounded contrast")
    with OUT.open("x", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with REPORT.open("x", encoding="utf-8", newline="") as handle:
        handle.write(render_report(result))


if __name__ == "__main__":
    main()
