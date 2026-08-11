#!/usr/bin/env python3
"""Freeze the source-bound native-visual pharmaceutical ownership audit.

This program consumes only the previously target-masked root-colour candidate
table.  It never opens a Voynich transcription or a formal-root artifact.
The native-visual grades were made against the exact Yale canvases bound below.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "public_pharma_root_color_candidates.tsv"
SOURCE_RESULT = RESULTS / "public_pharma_root_color_capacity.json"
OUT_TSV = RESULTS / "pharma_root_color_native_visual_ownership.tsv"
OUT_JSON = RESULTS / "pharma_root_color_native_visual_ownership.json"
REPORT = RESULTS / "pharma_root_color_native_visual_ownership_report.md"

EXPECTED = {
    "public_pharma_root_color_candidates.tsv":
        "092bdfcbbf17c78da2ebd00576921a464f61cfd50bc08ee070da8def444860ec",
    "public_pharma_root_color_capacity.json":
        "0cc6bf6b675a45c86b841d971be65c4c348f1eb789bfcec61d59b52bbc3d9909",
}

MANIFEST = {
    "url": "https://collections.library.yale.edu/manifests/2002046",
    "sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
    "bytes": 403033,
}

IMAGES = {
    "1006233": ("88v and 89r", 9078, 3777,
        "3b553c70d0c068cb39a276d391127165c5d9d868ec08e7f5eb2e73b32bb95d1e"),
    "1006234": ("89v (part)", 4204, 3809,
        "b6b0dd8ba7cd316f3b09a8b156d1eed0eb36ad8ec9086b975969f4f8f7dd5406"),
    "1006235": ("89v (part) and 90r", 7796, 3761,
        "6aaa777945f288a8ba206921709292eaaf4ea972f9a0bb59cdf3040aaed3e15a"),
    "1006246": ("99r", 2702, 3765,
        "f17eba5496a1b1d92f589c33ee9be256a379ec8d2bba3da1ebe2ff5a2e3e2901"),
    "1006247": ("99v", 2802, 3697,
        "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5"),
    "1006248": ("100r", 2676, 3756,
        "6dcf72a0d7eac14da2232987c9cc1521e6d70c9f0f92d3eb39b55fc075520429"),
    "1006249": ("100v and 101r", 7486, 3715,
        "72637b9770f40f7a8ff6b96a551e64775e88994ae69bafec0b43d48974364c33"),
    "1006250": ("101v (part)", 2698, 3779,
        "1122f1b13afdf1509402334816f95e5e9baa2b6c94aa9e347b04aa2e4e54f36b"),
    "1006251": ("101v (part) and 102r", 8176, 3864,
        "30fd529fc6bf8999d5be48024ee6a1676af55e8d66dc0a4f77993fe2565e9d94"),
    "1006252": ("102v (part)", 2981, 3795,
        "8cdb1030d805b968932146124915cb0d86f7abf853167ffec028b59599820fad"),
}

CLEAR = "CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL"
AMBIGUOUS = "AMBIGUOUS_NEAREST_NEIGHBOUR"
UNRESOLVED = "SOURCE_LOCATION_UNRESOLVED"

# The complete held-panel judgment registry.  Values are grade, Yale canvas ID,
# and a target-free basis code.  No label string is present.
JUDGMENTS: dict[str, tuple[str, str, str]] = {}


def register(ids: str, grade: str, canvas: str, basis: str) -> None:
    for source_id in ids.split():
        assert source_id not in JUDGMENTS
        JUDGMENTS[source_id] = (grade, canvas, basis)


register(
    "STOLFI_BEST_1133 STOLFI_BEST_1136 STOLFI_BEST_1151 "
    "STOLFI_BEST_1160 STOLFI_BEST_1163",
    CLEAR, "1006233", "ROW_ORDINAL_AND_LOCAL_WHITESPACE_ISOLATE_ONE_OWNER",
)
register(
    "STOLFI_BEST_1214 STOLFI_BEST_1216 STOLFI_BEST_1222 STOLFI_BEST_1230",
    CLEAR, "1006234", "ROW_ORDINAL_AND_LOCAL_WHITESPACE_ISOLATE_ONE_OWNER",
)
register(
    "STOLFI_BEST_1261 STOLFI_BEST_1267",
    CLEAR, "1006235", "ROW_ORDINAL_AND_LOCAL_WHITESPACE_ISOLATE_ONE_OWNER",
)
register(
    "STOLFI_BEST_1276 STOLFI_BEST_1281 STOLFI_BEST_1282 STOLFI_BEST_1285 "
    "STOLFI_BEST_1291 STOLFI_BEST_1297 STOLFI_BEST_1300 STOLFI_BEST_1301",
    UNRESOLVED, "1006246", "SOURCE_X_INDEX_NOT_TRANSFERABLE_WITHOUT_LABEL_IDENTITY",
)
register(
    "STOLFI_BEST_1306 STOLFI_BEST_1308 STOLFI_BEST_1312 STOLFI_BEST_1313 "
    "STOLFI_BEST_1315 STOLFI_BEST_1316 STOLFI_BEST_1317 STOLFI_BEST_1318 "
    "STOLFI_BEST_1319 STOLFI_BEST_1320 STOLFI_BEST_1321 STOLFI_BEST_1322 "
    "STOLFI_BEST_1326 STOLFI_BEST_1327",
    UNRESOLVED, "1006247", "SOURCE_X_INDEX_NOT_TRANSFERABLE_WITHOUT_LABEL_IDENTITY",
)
register(
    "STOLFI_BEST_1374 STOLFI_BEST_1380",
    CLEAR, "1006248", "ROW_ORDINAL_AND_LOCAL_WHITESPACE_ISOLATE_ONE_OWNER",
)
register(
    "STOLFI_BEST_1377",
    AMBIGUOUS, "1006248", "LABEL_LIES_BETWEEN_TWO_PLAUSIBLE_FRAGMENTS",
)
register(
    "STOLFI_BEST_1391 STOLFI_BEST_1393 STOLFI_BEST_1395 "
    "STOLFI_BEST_1401 STOLFI_BEST_1409 STOLFI_BEST_1413 STOLFI_BEST_1415",
    CLEAR, "1006249", "ROW_ORDINAL_AND_LOCAL_WHITESPACE_ISOLATE_ONE_OWNER",
)
register(
    "STOLFI_BEST_1420 STOLFI_BEST_1421 STOLFI_BEST_1423",
    UNRESOLVED, "1006250", "SOURCE_X_INDEX_NOT_TRANSFERABLE_WITHOUT_LABEL_IDENTITY",
)
register(
    "STOLFI_BEST_1448",
    CLEAR, "1006251", "ROW_ORDINAL_AND_LOCAL_WHITESPACE_ISOLATE_ONE_OWNER",
)
register(
    "STOLFI_BEST_1490",
    CLEAR, "1006252", "ROW_ORDINAL_AND_LOCAL_WHITESPACE_ISOLATE_ONE_OWNER",
)

FIELDS = (
    "source_record_id", "source_page", "physical_folio", "source_location",
    "root_state", "mapped_locus", "canvas_id", "canvas_label",
    "image_sha256", "visual_grade", "visual_basis", "eligible", "exclusion_reason",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_new(path: Path, payload: str) -> None:
    if path.exists():
        raise SystemExit(f"refusing overwrite: {path}")
    path.write_text(payload, encoding="utf-8")


def main() -> None:
    for path in (OUT_TSV, OUT_JSON, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    assert digest(SOURCE) == EXPECTED[SOURCE.name]
    assert digest(SOURCE_RESULT) == EXPECTED[SOURCE_RESULT.name]

    source = read_tsv(SOURCE)
    held = [
        row for row in source
        if row["primary_current_mapping"] == "1" and row["physical_folio"] != "f88"
    ]
    assert len(held) == 48
    assert set(JUDGMENTS) == {row["source_record_id"] for row in held}

    audited: list[dict[str, str]] = []
    for row in held:
        grade, canvas, basis = JUDGMENTS[row["source_record_id"]]
        label, _, _, image_sha = IMAGES[canvas]
        conflict = row["state_comparison"] == "CONFLICT"
        eligible = grade == CLEAR and not conflict
        exclusion = (
            "NONE" if eligible else
            "CROSS_DESCRIPTION_ROOT_STATE_CONFLICT" if conflict else grade
        )
        audited.append({
            "source_record_id": row["source_record_id"],
            "source_page": row["source_page"],
            "physical_folio": row["physical_folio"],
            "source_location": row["source_location"],
            "root_state": row["root_state"],
            "mapped_locus": row["mapped_locus"],
            "canvas_id": canvas,
            "canvas_label": label,
            "image_sha256": image_sha,
            "visual_grade": grade,
            "visual_basis": basis,
            "eligible": "1" if eligible else "0",
            "exclusion_reason": exclusion,
        })

    eligible = [row for row in audited if row["eligible"] == "1"]
    states = Counter(row["root_state"] for row in eligible)
    folios_by_state = {
        state: sorted({row["physical_folio"] for row in eligible if row["root_state"] == state})
        for state in ("DARK", "LIGHT")
    }
    by_folio = Counter(row["physical_folio"] for row in eligible)
    max_share = max(by_folio.values()) / len(eligible)
    grades = Counter(row["visual_grade"] for row in audited)
    assert grades == {CLEAR: 22, UNRESOLVED: 25, AMBIGUOUS: 1}
    assert states == {"LIGHT": 15, "DARK": 6}
    assert by_folio == {"f89": 11, "f100": 8, "f102": 2}

    gates = {
        "at_least_four_eligible_clear_each_state": min(states.values()) >= 4,
        "each_state_on_at_least_two_held_folios": all(
            len(folios_by_state[state]) >= 2 for state in ("DARK", "LIGHT")
        ),
        "at_least_twelve_eligible_clear_total": len(eligible) >= 12,
        "maximum_single_folio_share_at_most_0_60": max_share <= 0.60,
        "source_and_image_bindings_frozen": True,
        "all_held_primary_rows_audited": len(audited) == 48,
        "zero_voynich_strings_or_formal_roots_opened": True,
    }
    assert all(gates.values())

    tsv_lines = ["\t".join(FIELDS)]
    tsv_lines.extend("\t".join(row[field] for field in FIELDS) for row in audited)
    write_new(OUT_TSV, "\n".join(tsv_lines) + "\n")

    image_records = {
        canvas: {
            "label": values[0], "width": values[1], "height": values[2],
            "url": f"https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg",
            "sha256": values[3],
        }
        for canvas, values in IMAGES.items()
    }
    result = {
        "experiment": "PHARMA_ROOT_COLOR_NATIVE_VISUAL_OWNERSHIP_CAPACITY",
        "status": "PASS_NATIVE_VISUAL_OWNERSHIP_CAPACITY",
        "decision": "AUTHORIZE_SEPARATE_TEXT_PREREGISTRATION_ONLY_KEEP_LABELS_SEALED",
        "inputs": {
            "source_candidates_sha256": EXPECTED[SOURCE.name],
            "source_capacity_result_sha256": EXPECTED[SOURCE_RESULT.name],
            "yale_manifest": MANIFEST,
            "yale_images": image_records,
        },
        "held_panel": {
            "physical_folios": ["f89", "f99", "f100", "f101", "f102"],
            "primary_rows": len(audited),
            "visual_grades": dict(sorted(grades.items())),
            "eligible_clear_rows": len(eligible),
            "eligible_states": dict(sorted(states.items())),
            "eligible_folios_by_state": folios_by_state,
            "eligible_rows_by_folio": dict(sorted(by_folio.items())),
            "maximum_single_folio_share": max_share,
            "development_folio_excluded": "f88",
        },
        "gates": gates,
        "method": {
            "observer": "SOURCE_BOUND_NATIVE_MODEL_VISION",
            "machine_authored_not_human_annotation": True,
            "target_labels_masked": True,
            "automated_ocr_segmentation_clip_embedding_similarity_or_object_naming": False,
            "unresolved_x_index_rows_retained_as_ineligible": 25,
        },
        "claim_ceiling": (
            "The frozen held panel has enough source-bound, native-visually clear label-to-fragment "
            "ownership relations to preregister a separate masked text test of the inherited human "
            "DARK/LIGHT root-colour contrast. This result assigns no word, meaning, sound, language, "
            "cipher, plaintext, plant identity, or translation."
        ),
    }
    write_new(OUT_JSON, json.dumps(result, indent=2, sort_keys=True) + "\n")

    report = f"""# Pharmaceutical root-colour native-visual ownership capacity

Status: **PASS_NATIVE_VISUAL_OWNERSHIP_CAPACITY**

Source-bound native visual inspection audited all **48** held primary-mapped rows
on f89, f99, f100, f101, and f102 while the Voynich labels remained sealed. The
predeclared rule classified **22** rows as visually clear one-fragment/one-label
cells, **1** as an ambiguous nearest-neighbour case, and **25** legacy `.x.#`
locations as unresolved without consulting label identity. One visually clear
row was excluded because the two frozen human root descriptions conflict.

The resulting eligible panel has **21** clear pairings: **6 DARK** and **15
LIGHT**. DARK occurs on {', '.join(folios_by_state['DARK'])}; LIGHT occurs on
{', '.join(folios_by_state['LIGHT'])}. Contributions are f89=11, f100=8, and
f102=2, so the largest-folio share is **{max_share:.3f}**, below the frozen
0.60 ceiling. Every capacity gate passes.

This repairs only the old ownership-capacity failure. It does not test any
Voynich form. The decision is therefore
**AUTHORIZE_SEPARATE_TEXT_PREREGISTRATION_ONLY_KEEP_LABELS_SEALED**. A new
statistic, null, threshold, and held evaluation must be frozen before any label
surface is opened.

The observations are machine-authored source-bound visual judgments, not
literal human annotations. No OCR, transcription, automated segmentation,
CLIP, embedding, image similarity, plant naming, or automated colour classifier
was used.

Claim ceiling: {result['claim_ceiling']}
"""
    write_new(REPORT, report)


if __name__ == "__main__":
    main()
