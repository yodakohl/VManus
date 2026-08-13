#!/usr/bin/env python3
"""Build the source-only GDT002 visual/grammar checkpoint.

This builder performs no image access and no semantic inference.  It reuses
published human description rows, keeps prior AI visual adjudications in a
separate field, exports the three alternate readings for discovery pages, and
commits (without publishing) the mechanically generated f84r text projection.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/semantic_assumptions/results"
TARGET_PAGES = ("f80r", "f82r", "f84r")
DISCOVERY_PAGES = ("f80r", "f82r")
HOLDOUT_PAGE = "f84r"
EDITION_ORDER = {"ZL3b": 0, "IT2a": 1, "RF1b": 2}

INPUTS = {
    "page_annotations": RESULTS / "existing_human_page_annotations.tsv",
    "page_roles": RESULTS / "existing_human_page_role_matrix.tsv",
    "exact_loci": RESULTS / "existing_human_exact_locus_annotations.tsv",
    "crosswalk": RESULTS / "existing_human_current_locus_crosswalk.tsv",
    "source_roles": RESULTS / "existing_human_source_role_matrix.tsv",
    "source_alignment": RESULTS / "source_sta_group_alignment.tsv",
    "source_separators": RESULTS / "source_separator_transcription.tsv",
    "consensus_loci": RESULTS / "source_sta_family_consensus_loci.tsv",
    "structural_groups": RESULTS / "source_native_structural_interlinear_v1.tsv",
    "bfe001": RESULTS / "bfe001_bio_figure_enclosure_capacity.json",
    "apparatus": RESULTS / "apparatus_component_caption_capacity.json",
    "rra001": RESULTS / "rra001_recurrent_label_owner_atlas_result.json",
    "q13": ROOT / "experiments/semantic_assumptions/cache/public_voynich_nu_catalogue/q13.html",
    "stolfi_exact_source": ROOT / "transcription/sources/Stolfi_text25e1-52.evt",
    "grammar": ROOT / "experiments/semantic_assumptions/grammar/CONFIRMED_GRAMMAR.md",
}

DOCUMENTS = (
    "YOLO_MODE.md", "GDT002_METHOD.md", "GDT002_EXISTING_VISUAL_EVIDENCE_AUDIT.md",
    "GDT002_DISCOVERY_REPORT.md", "GDT002_YOLO_LEDGER.tsv",
    "build_gdt002_checkpoint.py", "validate_gdt002_checkpoint.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_bytes(rows: list[dict[str, object]], fields: list[str]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, delimiter="\t", fieldnames=fields,
                            lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fields})
    return out.getvalue().encode("utf-8")


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.write_bytes(tsv_bytes(rows, fields))


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value))


def locus_key(locus: str) -> tuple[int, int]:
    match = re.match(r"f(\d+)[a-z]\.(\d+)$", locus)
    if not match:
        return (10**9, 10**9)
    return int(match.group(1)), int(match.group(2))


# These are clause-level neutralizations of the cached human catalogue prose.
# They are not new image observations.
PAGE_VISUAL_UNITS = [
    ("f80r", "PAGE_TOP_FIGURE_ROW", "FIGURE_ARRAY", "F80_TOP_FIGURE_ARRAY", "UPPER", "", "",
     "A row of small figures across the top of the page, mostly, but not all, female.",
     "Repeated small-figure row along the upper page edge."),
    ("f80r", "PAGE_RIGHT_CONNECTOR_TO_MIDDLE", "LINEAR_CONNECTOR", "", "MIDDLE_RIGHT", "", "f80r:PAGE_MIDDLE_BLUE_REGION",
     "A tube in the right margin ends in a pool of blue water spanning the middle of the page.",
     "A right-margin linear element terminates at a blue bounded region spanning the page middle."),
    ("f80r", "PAGE_MIDDLE_BLUE_REGION", "BOUNDED_REGION", "", "MIDDLE", "BLUE", "",
     "A pool of blue water spanning the middle of the page has female figures at both ends.",
     "A blue bounded region spans the page middle and has figures at both ends."),
    ("f80r", "PAGE_RIGHT_DESCENDING_CONNECTOR", "LINEAR_CONNECTOR", "", "RIGHT_LOWER", "", "f80r:PAGE_LOWER_RIGHT_FIGURE",
     "In the right margin there is another tube going down to another female figure.",
     "A second right-margin linear element descends to a figure."),
    ("f80r", "PAGE_LOWER_RIGHT_FIGURE", "FIGURE", "", "RIGHT_LOWER", "", "",
     "In the right margin there is another tube going down to another female figure.",
     "A figure terminates the second descending right-margin linear element."),
    ("f80r", "PAGE_LOWER_LEFT_FIGURE", "FIGURE", "", "LOWER_LEFT", "", "",
     "A further [female figure] is in the lower left corner.",
     "A further figure occupies the lower-left corner."),
    ("f82r", "PAGE_UPPER_CONNECTION_SYSTEM", "CONNECTED_FIGURE_SYSTEM", "F82_PAIRED_CONNECTION_SYSTEMS", "UPPER", "", "",
     "Two nymphs in the left and right margin near the top are connected by two tubes with a joining element.",
     "Two upper marginal figures are joined by two linear elements and one joining element."),
    ("f82r", "PAGE_LOWER_CONNECTION_SYSTEM", "CONNECTED_FIGURE_SYSTEM", "F82_PAIRED_CONNECTION_SYSTEMS", "UPPER_MIDDLE", "", "",
     "Two more nymphs just below them [have] a different type of connection.",
     "Two further figures below the upper pair have a visibly different connection."),
    ("f82r", "PAGE_BOTTOM_GREEN_REGION", "BOUNDED_REGION", "", "LOWER", "GREEN", "",
     "There is a green pool at the bottom of the page with a wavy outline, with several female figures.",
     "A green, wavy-edged bounded region at the page bottom contains several figures."),
    ("f82r", "PAGE_SEPARATE_BLUE_REGION", "BOUNDED_REGION", "", "LOWER", "BLUE", "",
     "One nymph is standing in a separate blue pool.",
     "One figure occupies a separate blue bounded region."),
    ("f84r", "PAGE_TOP_ROOFED_GREEN_REGION", "BOUNDED_REGION", "", "UPPER", "GREEN", "",
     "There is a green pool with a roof across the full width of the top of the page, populated by female figures mostly in pairs.",
     "A roofed green bounded region spans the upper page and contains figures, mostly paired."),
    ("f84r", "PAGE_LEFT_CONNECTOR_UPPER_MIDDLE", "LINEAR_CONNECTOR", "F84_LEFT_CONNECTORS", "LEFT", "BLUE", "f84r:PAGE_MIDDLE_GREEN_REGION",
     "A thin blue tube along the left margin leads to another pool in the middle.",
     "A thin blue left-margin linear element connects toward a middle bounded region."),
    ("f84r", "PAGE_MIDDLE_GREEN_REGION", "BOUNDED_REGION", "", "MIDDLE", "GREEN", "",
     "Another pool in the middle [has] green water and more nymphs.",
     "A middle green bounded region contains several figures."),
    ("f84r", "PAGE_SEPARATE_SMALL_BLUE_REGION", "BOUNDED_REGION", "", "MIDDLE", "BLUE", "",
     "There is a separate small blue pool.",
     "A separate small blue bounded region is visible."),
    ("f84r", "PAGE_RED_CONTAINER", "COLORED_BOUNDED_OBJECT", "", "MIDDLE", "RED", "",
     "There is ... one red bucket.",
     "One small red bounded object is visible."),
    ("f84r", "PAGE_LEFT_CONNECTOR_MIDDLE_BOTTOM", "LINEAR_CONNECTOR", "F84_LEFT_CONNECTORS", "LEFT_LOWER", "BLUE", "f84r:PAGE_BOTTOM_ROUND_REGION",
     "A further thin blue tube leads to a round pool at the bottom.",
     "A further thin blue linear element connects toward a round bottom region."),
    ("f84r", "PAGE_BOTTOM_ROUND_REGION", "BOUNDED_REGION", "", "LOWER", "FAINT_BLUE", "",
     "A round pool at the bottom [has] faint blue water and many nymphs closely packed together.",
     "A round faint-blue bottom region contains many closely packed figures."),
]


def annotation_position(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    page, locus, comment = row["page"], row["locus"], row["local_comment"]
    suffix = int(locus.rsplit(".", 1)[1])
    if page == "f80r":
        x = {1: "1", 2: "2", 3: "3", 4: "3.5", 5: "4.5", 6: "5.5", 7: "7", 8: "8", 9: "8.5", 10: "8.5"}.get(suffix, "")
        y = "UPPER_2" if suffix == 10 else "UPPER_1"
        return "F80_TOP_TEXT_POSITIONS", str(suffix), x, y, "UPPER"
    if page == "f82r":
        if suffix == 10:
            return "F82_COMPONENT_POSITION", "1", "", "MIDDLE", "MIDDLE"
        if suffix in (35, 38):
            return "F82_LATERAL_CONNECTOR_POSITIONS", "1" if suffix == 35 else "2", "1" if suffix == 35 else "2", "LOWER", "LOWER"
        if "Top row" in comment:
            order = {34: 1, 36: 2, 37: 3, 39: 4}.get(suffix, "")
            return "F82_BOTTOM_REGION_TOP_ROW", str(order), str(order), "LOWER_1", "LOWER"
        order = {40: 1, 41: 2, 42: 3, 43: 5, 44: 6, 45: 7}.get(suffix, "")
        return "F82_BOTTOM_REGION_BOTTOM_ROW", str(order), str(order), "LOWER_2", "LOWER"
    if suffix in (1, 2, 3, 4, 6, 8, 10, 11, 12):
        return "F84_TOP_TEXT_POSITIONS", str(suffix), str(suffix), "UPPER", "UPPER"
    if suffix in (13, 17, 20, 24, 25):
        return "F84_PROSE_ABOVE_MIDDLE_REGION", str(suffix), "", "MIDDLE", "MIDDLE"
    if suffix == 27:
        return "F84_HEDGED_TEN_GROUP_ROW", "1", "", "MIDDLE_LOWER", "MIDDLE_LOWER"
    return "F84_LEFT_MARGIN_TEXT_POSITION", "1", "LEFT", "LOWER", "LOWER"


def neutralize_annotation(row: dict[str, str]) -> str:
    comment = row["local_comment"] or row["unit_description"]
    replacements = {
        "nymphs": "figures", "nymph": "figure", "waterfalls": "drawn vertical features",
        "waterfall": "drawn vertical feature", "tubs or tubes": "drawn apparatus",
        "tube": "linear component", "pond": "bounded region", "vat": "bounded region",
    }
    value = comment
    for old, new in replacements.items():
        value = re.sub(old, new, value, flags=re.IGNORECASE)
    return value.strip()


def visual_inventory() -> list[dict[str, object]]:
    exact = [r for r in read_tsv(INPUTS["exact_loci"]) if r["page"] in TARGET_PAGES]
    exact_loci = {r["locus"] for r in exact}
    page_annotations = {r["page"]: r for r in read_tsv(INPUTS["page_annotations"])}
    prior: dict[str, list[str]] = defaultdict(list)
    prior_sources: dict[str, list[str]] = defaultdict(list)
    bfe = json.loads(INPUTS["bfe001"].read_text())
    for obs in bfe["observations"]:
        if obs["page"] in TARGET_PAGES:
            prior[obs["current_locus"]].append("BFE001:" + obs["state"])
            prior_sources[obs["current_locus"]].append("bfe001_bio_figure_enclosure_capacity.json")
    app = json.loads(INPUTS["apparatus"].read_text())
    for obs in app["generous_singular_observations"]:
        if obs["locus"].split(".")[0] in TARGET_PAGES:
            prior[obs["locus"]].append("APPARATUS_CAPACITY:" + obs["grade"])
            prior_sources[obs["locus"]].append("apparatus_component_caption_capacity.json")
    rra = json.loads(INPUTS["rra001"].read_text())
    for obs in rra["observations"]:
        if obs["page"] in TARGET_PAGES:
            prior[obs["locus"]].append("RRA001:" + obs["outcome"])
            prior_sources[obs["locus"]].append("rra001_recurrent_label_owner_atlas_result.json")

    rows: list[dict[str, object]] = []
    q13_hash = sha256(INPUTS["q13"])
    for page, unit_id, unit_type, group, relpos, color, connected, raw, neutral in PAGE_VISUAL_UNITS:
        rows.append({
            "evidence_record_id": f"HUMAN_PAGE_{page}_{unit_id}", "folio": page,
            "panel_id": f"{page}_PAGE", "visual_unit_id": f"{page}:{unit_id}",
            "provenance": "EXISTING_HUMAN_ANNOTATION", "annotation_source": "voynich.nu q13 catalogue",
            "source_sha256": q13_hash, "source_locator": f"q13.html#{page}", "confidence": "SOURCE_ASSERTED",
            "unit_type": unit_type, "repetition_group": group, "ordinal_in_group": "",
            "x_order": "", "y_order": "", "relative_position": relpos, "inside_outside": "UNKNOWN",
            "left_right": "LEFT" if "LEFT" in relpos else ("RIGHT" if "RIGHT" in relpos else ""),
            "upper_lower": "UPPER" if "UPPER" in relpos else ("LOWER" if "LOWER" in relpos else ""),
            "mirror_role": "", "contained_in": "", "connected_to": connected,
            "connection_type": "DRAWN_LINEAR_CONNECTION" if "CONNECTOR" in unit_type else "",
            "endpoint_role": "TERMINATES_AT_DRAWN_UNIT" if connected else "UNKNOWN", "repeated_shape_class": group,
            "visible_color_state": color, "visible_pose_class": "", "local_text_loci": "",
            "ownership_evidence": "UNKNOWN", "prior_ai_visual_state": "",
            "prior_ai_visual_source": "", "raw_source_description": page_annotations[page]["illustrations"],
            "neutral_description": neutral,
            "interpretation_excluded": "OBJECT_IDENTITY;PROCESS;MATERIAL;MEDICAL_FUNCTION;LEXICAL_MEANING",
        })

    exact_hash = sha256(INPUTS["exact_loci"])
    stolfi_hash = sha256(INPUTS["stolfi_exact_source"])
    for row in sorted(exact, key=lambda r: (TARGET_PAGES.index(r["page"]), locus_key(r["locus"]))):
        group, ordinal, x_order, y_order, relative = annotation_position(row)
        tags = set(filter(None, row["object_tags"].split(";")))
        if row["locus"] == "f82r.10":
            ownership = "CONNECTED_COMPONENT"
            connected_to = "f82r:PAGE_UPPER_CONNECTION_SYSTEM"
        elif "REL_ARRAY_OR_GROUP" in row["unit_relation_tags"] or "REL_PROXIMITY" in row["local_relation_tags"]:
            ownership = "PROXIMITY_ONLY"
            connected_to = ""
        else:
            ownership = "UNKNOWN"
            connected_to = ""
        if row["normalized_code"].endswith("P0"):
            unit_type = "TEXT_BLOCK_POSITION"
        elif "WATER_OR_APPARATUS" in tags and "FIGURE" not in tags:
            unit_type = "APPARATUS_ASSOCIATED_TEXT_POSITION"
        else:
            unit_type = "FIGURE_ASSOCIATED_TEXT_POSITION"
        rows.append({
            "evidence_record_id": f"HUMAN_LOCUS_{row['locus']}", "folio": row["page"],
            "panel_id": f"{row['page']}_TEXT_ASSOCIATED", "visual_unit_id": f"{row['page']}:{row['locus']}",
            "provenance": "EXISTING_HUMAN_ANNOTATION", "annotation_source": f"{row['source_path']}#{row['locus']};derived=existing_human_exact_locus_annotations.tsv@{exact_hash}",
            "source_sha256": stolfi_hash, "source_locator": row["locus"], "confidence": row["certainty"],
            "unit_type": unit_type, "repetition_group": group, "ordinal_in_group": ordinal,
            "x_order": x_order, "y_order": y_order, "relative_position": relative,
            "inside_outside": "UNKNOWN", "left_right": "", "upper_lower": "UPPER" if "UPPER" in relative else ("LOWER" if "LOWER" in relative else ""),
            "mirror_role": "", "contained_in": "", "connected_to": connected_to,
            "connection_type": "DRAWN_COMPONENT_ASSOCIATION" if row["locus"] == "f82r.10" else "",
            "endpoint_role": "UNKNOWN", "repeated_shape_class": "", "visible_color_state": "",
            "visible_pose_class": "", "local_text_loci": row["locus"],
            "ownership_evidence": ownership, "prior_ai_visual_state": ";".join(sorted(prior[row["locus"]])),
            "prior_ai_visual_source": ";".join(sorted(set(prior_sources[row["locus"]]))),
            "raw_source_description": " | ".join(filter(None, [row["unit_description"], row["local_comment"]])),
            "neutral_description": neutralize_annotation(row),
            "interpretation_excluded": "FIGURE_IDENTITY;APPARATUS_FUNCTION;FLOW;ACTION;LEXICAL_MEANING",
        })
    # The current catalogue count has three f84r label loci whose only local
    # human description is the older hedged crosswalk record.  Preserve these
    # as explicit gaps rather than silently dropping them or inventing detail.
    crosswalk_hash = sha256(INPUTS["crosswalk"])
    for row in read_tsv(INPUTS["crosswalk"]):
        locus = row["current_locus"]
        if row["current_page"] not in TARGET_PAGES or not locus or locus in exact_loci:
            continue
        if row["current_kind"] != "L":
            continue
        rows.append({
            "evidence_record_id": f"HUMAN_CROSSWALK_GAP_{locus}", "folio": row["current_page"],
            "panel_id": f"{row['current_page']}_TEXT_ASSOCIATED", "visual_unit_id": f"{row['current_page']}:{locus}",
            "provenance": "EXISTING_HUMAN_ANNOTATION", "annotation_source": "existing_human_current_locus_crosswalk.tsv",
            "source_sha256": crosswalk_hash, "source_locator": row["source_record_id"], "confidence": row["source_certainty"],
            "unit_type": "FIGURE_ASSOCIATED_TEXT_POSITION_UNRESOLVED", "repetition_group": "F84_TOP_TEXT_POSITIONS",
            "ordinal_in_group": locus.rsplit(".", 1)[1], "x_order": locus.rsplit(".", 1)[1], "y_order": "UPPER",
            "relative_position": "UPPER", "inside_outside": "UNKNOWN", "left_right": "", "upper_lower": "UPPER",
            "mirror_role": "", "contained_in": "", "connected_to": "", "connection_type": "",
            "endpoint_role": "UNKNOWN", "repeated_shape_class": "", "visible_color_state": "", "visible_pose_class": "",
            "local_text_loci": locus, "ownership_evidence": "UNKNOWN", "prior_ai_visual_state": "",
            "prior_ai_visual_source": "", "raw_source_description": row["source_comments"],
            "neutral_description": "Legacy hedged figure-associated position; no exact local human description is available.",
            "interpretation_excluded": "FIGURE_IDENTITY;OWNER;APPARATUS_FUNCTION;LEXICAL_MEANING",
        })
    rows.sort(key=lambda r: (TARGET_PAGES.index(str(r["folio"])), 0 if not r["local_text_loci"] else 1,
                             locus_key(str(r["local_text_loci"])) if r["local_text_loci"] else (0, 0),
                             str(r["visual_unit_id"])))
    return rows


PROJECTION_FIELDS = [
    "evidence_class", "holdout_role", "semantic_role", "source_group_id", "edition", "locus", "page",
    "grammar_scope", "code", "kind", "source_group_index", "source_group_count", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw", "sta_group_raw",
    "primary_sta_codes", "primary_sta_families", "primary_sta_symbol_count", "alternative_site_count",
]


def alternate_projection(page_filter: tuple[str, ...]) -> list[dict[str, object]]:
    alignment = {r["source_group_id"]: r for r in read_tsv(INPUTS["source_alignment"])}
    rows = []
    for sep in read_tsv(INPUTS["source_separators"]):
        if sep["page"] not in page_filter:
            continue
        aligned = alignment[sep["source_group_id"]]
        assert aligned["edition"] == sep["edition"] and aligned["locus"] == sep["locus"]
        rows.append({
            "evidence_class": "FORMAL_STRUCTURE", "holdout_role": "DISCOVERY" if sep["page"] in DISCOVERY_PAGES else "HOLDOUT",
            "semantic_role": "UNASSIGNED", "source_group_id": sep["source_group_id"], "edition": sep["edition"],
            "locus": sep["locus"], "page": sep["page"], "grammar_scope": sep["grammar_scope"],
            "code": sep["code"], "kind": sep["kind"], "source_group_index": sep["source_group_index"],
            "source_group_count": sep["source_group_count"], "paragraph_start": sep["paragraph_start"],
            "paragraph_end": sep["paragraph_end"], "left_separator": sep["left_separator"],
            "right_separator": sep["right_separator"], "ivtff_group_raw": sep["ivtff_group_raw"],
            "sta_group_raw": aligned["sta_group_raw"], "primary_sta_codes": aligned["primary_sta_codes"],
            "primary_sta_families": aligned["primary_sta_families"],
            "primary_sta_symbol_count": aligned["primary_sta_symbol_count"],
            "alternative_site_count": aligned["alternative_site_count"],
        })
    rows.sort(key=lambda r: (TARGET_PAGES.index(str(r["page"])), locus_key(str(r["locus"])),
                             EDITION_ORDER[str(r["edition"])], int(str(r["source_group_index"]))))
    return rows


CONSENSUS_FIELDS = [
    "evidence_class", "holdout_role", "semantic_role", "coverage_state", "consensus_group_id", "locus",
    "page", "grammar_scope", "code", "kind", "group_index", "group_count", "factual_position",
    "family_surface", "zl_sta_codes", "it_sta_codes", "rf_sta_codes", "left_boundary_profile",
    "left_boundary_support", "right_boundary_profile", "right_boundary_support", "descriptive_only_full_corpus_tags_excluded",
]


def consensus_projection(page_filter: tuple[str, ...]) -> list[dict[str, object]]:
    locus_rows = {r["locus"]: r for r in read_tsv(INPUTS["consensus_loci"]) if r["page"] in page_filter}
    all_loci = {}
    for r in read_tsv(INPUTS["source_separators"]):
        if r["page"] in page_filter:
            all_loci[r["locus"]] = r
    groups_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in read_tsv(INPUTS["structural_groups"]):
        if r["page"] in page_filter:
            groups_by_locus[r["locus"]].append(r)
    rows: list[dict[str, object]] = []
    for locus, meta in sorted(all_loci.items(), key=lambda kv: (TARGET_PAGES.index(kv[1]["page"]), locus_key(kv[0]))):
        consensus = locus_rows.get(locus)
        if consensus is None:
            coverage = "NO_EXACT_FAMILY_CONSENSUS"
        elif consensus["strict_zero_alternative"] != "1":
            coverage = "EXACT_FAMILY_WITH_ALTERNATIVE"
        else:
            coverage = "STRICT_EXACT_FAMILY"
        groups = sorted(groups_by_locus.get(locus, []), key=lambda r: int(r["group_index"]))
        if not groups:
            groups = [{}]
        for group in groups:
            rows.append({
                "evidence_class": "FORMAL_STRUCTURE", "holdout_role": "DISCOVERY" if meta["page"] in DISCOVERY_PAGES else "HOLDOUT",
                "semantic_role": "UNASSIGNED", "coverage_state": coverage,
                "consensus_group_id": group.get("consensus_group_id", ""), "locus": locus, "page": meta["page"],
                "grammar_scope": meta["grammar_scope"], "code": meta["code"], "kind": meta["kind"],
                "group_index": group.get("group_index", ""), "group_count": group.get("group_count", ""),
                "factual_position": group.get("factual_position", ""), "family_surface": group.get("family_surface", ""),
                "zl_sta_codes": group.get("zl_sta_codes", ""), "it_sta_codes": group.get("it_sta_codes", ""),
                "rf_sta_codes": group.get("rf_sta_codes", ""), "left_boundary_profile": group.get("left_boundary_profile", ""),
                "left_boundary_support": group.get("left_boundary_support", ""), "right_boundary_profile": group.get("right_boundary_profile", ""),
                "right_boundary_support": group.get("right_boundary_support", ""),
                "descriptive_only_full_corpus_tags_excluded": "exact_first_last;exact_edge_core;opening;closing;transition;favored_path",
            })
    return rows


ATLAS_FIELDS = [
    "folio", "visual_unit_id", "local_text_locus", "provenance", "repetition_group", "ownership_evidence",
    "prior_ai_visual_state", "visual_position_summary", "formal_access_state", "coverage_state", "code", "kind",
    "consensus_group_count", "family_expression", "boundary_expression", "latent_role", "interpretation",
]


def discovery_atlas(inventory: list[dict[str, object]], discovery_consensus: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    coverage = {}
    for row in discovery_consensus:
        coverage[str(row["locus"])] = str(row["coverage_state"])
        if row["consensus_group_id"]:
            groups[str(row["locus"])].append(row)
    rows = []
    for item in inventory:
        locus = str(item["local_text_loci"])
        page = str(item["folio"])
        if not locus:
            access = "NO_ASSOCIATED_LOCUS"
            state = "NOT_APPLICABLE"
        elif page == HOLDOUT_PAGE:
            access = "SEALED_HOLDOUT_NOT_OPENED_FOR_DISCOVERY"
            state = "SEALED"
        else:
            access = "DISCOVERY_FORMAL_STRUCTURE_OPEN"
            state = coverage.get(locus, "NO_EXACT_FAMILY_CONSENSUS")
        formal = groups.get(locus, []) if page in DISCOVERY_PAGES else []
        rows.append({
            "folio": page, "visual_unit_id": item["visual_unit_id"], "local_text_locus": locus,
            "provenance": item["provenance"], "repetition_group": item["repetition_group"],
            "ownership_evidence": item["ownership_evidence"], "prior_ai_visual_state": item["prior_ai_visual_state"],
            "visual_position_summary": item["neutral_description"], "formal_access_state": access,
            "coverage_state": state, "code": formal[0]["code"] if formal else "",
            "kind": formal[0]["kind"] if formal else "", "consensus_group_count": len(formal) if formal else "",
            "family_expression": " ".join(str(x["family_surface"]) for x in formal),
            "boundary_expression": " || ".join(f"{x['left_boundary_profile']}->{x['right_boundary_profile']}" for x in formal),
            "latent_role": "UNASSIGNED", "interpretation": "NONE",
        })
    return rows


def build() -> None:
    inventory = visual_inventory()
    projection = alternate_projection(DISCOVERY_PAGES)
    consensus = consensus_projection(DISCOVERY_PAGES)
    holdout_projection = alternate_projection((HOLDOUT_PAGE,))
    holdout_consensus = consensus_projection((HOLDOUT_PAGE,))
    atlas = discovery_atlas(inventory, consensus)

    inventory_fields = [
        "evidence_record_id", "folio", "panel_id", "visual_unit_id", "provenance", "annotation_source",
        "source_sha256", "source_locator", "confidence", "unit_type", "repetition_group", "ordinal_in_group",
        "x_order", "y_order", "relative_position", "inside_outside", "left_right", "upper_lower", "mirror_role",
        "contained_in", "connected_to", "connection_type", "endpoint_role", "repeated_shape_class",
        "visible_color_state", "visible_pose_class", "local_text_loci", "ownership_evidence", "prior_ai_visual_state",
        "prior_ai_visual_source", "raw_source_description", "neutral_description", "interpretation_excluded",
    ]
    write_tsv(ROOT / "gdt002_visual_inventory.tsv", inventory, inventory_fields)
    write_tsv(ROOT / "gdt002_grammar_projection.tsv", projection, PROJECTION_FIELDS)
    write_tsv(ROOT / "gdt002_grammar_consensus_projection.tsv", consensus, CONSENSUS_FIELDS)
    write_tsv(ROOT / "gdt002_repeated_structure_atlas.tsv", atlas, ATLAS_FIELDS)

    holdout_commitment = {
        "artifact": "GDT002_F84R_TEXT_PROJECTION_COMMITMENT_V1",
        "page": HOLDOUT_PAGE,
        "physical_folio": "f84",
        "access_state": "MECHANICALLY_MATERIALIZED_IN_ISOLATED_BUILDER_MEMORY_FOR_COMMITMENT_HASHING;NOT_PUBLISHED_INSPECTED_JOINED_OR_USED_FOR_DISCOVERY;PRIOR_REPOSITORY_TEXT_EXPOSURE_DISCLOSED",
        "alternate_projection": {
            "rows": len(holdout_projection),
            "sha256": hashlib.sha256(tsv_bytes(holdout_projection, PROJECTION_FIELDS)).hexdigest(),
        },
        "consensus_projection": {
            "rows": len(holdout_consensus),
            "strict_group_rows": sum(bool(r["consensus_group_id"]) for r in holdout_consensus),
            "sha256": hashlib.sha256(tsv_bytes(holdout_consensus, CONSENSUS_FIELDS)).hexdigest(),
        },
        "selection_rule": "page == f84r; identical schemas and ordering as discovery projections",
        "opening_rule": "Open only after visual schema, role vocabulary, grammar primitives, complexity penalties, and candidate discovery worlds are frozen.",
        "transcription_readings_are_alternates_not_replications": True,
        "blinding_note": "This is not a pristine observer-blind holdout: f84r strings appeared in prior repository work. The exact GDT002 projection was mechanically materialized in isolated builder memory solely to compute commitments; it was not published, inspected by the discovery analyst, joined, or used to tune this checkpoint. Future scoring must be deterministic from a frozen discovery model.",
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in INPUTS.values()},
    }
    write_json(ROOT / "gdt002_f84r_holdout_projection_commitment.json", holdout_commitment)

    linked = [r for r in atlas if r["formal_access_state"] == "DISCOVERY_FORMAL_STRUCTURE_OPEN"]
    strict_linked = [r for r in linked if r["coverage_state"] == "STRICT_EXACT_FAMILY"]
    family_occ = defaultdict(list)
    for row in strict_linked:
        if row["family_expression"]:
            family_occ[row["family_expression"]].append(row["local_text_locus"])
    repeats = {k: v for k, v in family_occ.items() if len(v) > 1}
    discovery_coverage = Counter(str(r["coverage_state"]) for r in consensus if not r["consensus_group_id"])
    strict_loci = {str(r["locus"]) for r in consensus if r["coverage_state"] == "STRICT_EXACT_FAMILY"}
    strict_prose_loci = {
        str(r["locus"]) for r in consensus
        if r["coverage_state"] == "STRICT_EXACT_FAMILY" and r["grammar_scope"] == "CONFIRMED_PROSE"
    }
    summary = {
        "artifact": "GDT002_DISCOVERY_ATLAS_SUMMARY_V1",
        "status": "CHECKPOINT_COMPLETE_CURRENT_PANEL_NOT_IDENTIFIABLE_SOLVER_NOT_RUN",
        "pages": {"discovery": list(DISCOVERY_PAGES), "sealed_holdout": HOLDOUT_PAGE},
        "counts": {
            "visual_inventory_rows": len(inventory),
            "existing_human_rows": sum(r["provenance"] == "EXISTING_HUMAN_ANNOTATION" for r in inventory),
            "new_ai_direct_visual_observation_rows": sum(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in inventory),
            "discovery_alternate_rows": len(projection),
            "discovery_consensus_rows": len(consensus),
            "atlas_rows": len(atlas),
            "text_linked_discovery_rows": len(linked),
            "strict_text_linked_discovery_rows": len(strict_linked),
            "repeated_strict_family_expressions": len(repeats),
            "discovery_loci": len({str(r["locus"]) for r in consensus}),
            "discovery_strict_exact_family_loci": len(strict_loci),
            "discovery_strict_confirmed_prose_loci": len(strict_prose_loci),
            "discovery_strict_confirmed_prose_groups": sum(
                bool(r["consensus_group_id"]) and r["coverage_state"] == "STRICT_EXACT_FAMILY"
                and r["grammar_scope"] == "CONFIRMED_PROSE" for r in consensus
            ),
        },
        "repeated_strict_family_expressions": repeats,
        "constraints": [
            {
                "id": "C01_AQABA_SINGULAR_OWNER_UNRESOLVED",
                "observation": "The same strict family expression AQABA occurs at visual-linked f80r.3 and f80r.4; prior source-bound AI adjudication grades f80r.3 singularly figure-owned, while the human description supplies only ambiguous between-figure proximity for f80r.4. AQABA also occurs in confirmed prose f80r.31 and f80r.51.",
                "effect": "Current evidence does not support a universal singular-owner mapping for AQABA; the ambiguous occurrence is not itself proof of nonsingular ownership.",
            },
            {
                "id": "C02_AQAC_CROSS_PAGE_PROXIMITY_COMPATIBLE",
                "observation": "Strict family expression AQAC has two visual-linked occurrences, f80r.9 and f82r.34, both in group/proximity figure contexts on two physical folios. It also occurs in confirmed prose f80r.15 and f80r.37.",
                "effect": "This is a weak joint-role candidate only; two occurrences and uncertain ownership do not identify a semantic role.",
            },
            {
                "id": "C03_DIRECT_COMPONENT_LOCUS_LACKS_STRICT_PROJECTION",
                "observation": "f82r.10 is the sole human-described label on a cross-shaped component and has a prior singular component grade, but it is outside the strict exact-family projection.",
                "effect": "The strongest component association cannot seed a strict-family mapping without modeling transcription uncertainty.",
            },
            {
                "id": "C04_ARRAY_FORMAL_DIVERSITY",
                "observation": "The covered f80r and f82r repeated visual-array positions contain diverse family expressions.",
                "effect": "There is no single array-wide family invariant; a future solver would need new relation evidence rather than an exact-label mapping.",
            },
        ],
        "claim_ceiling": "Descriptive source-only atlas. No semantic role, object name, word, POS, sound, language, plaintext, meaning, or translation is assigned.",
    }
    write_json(ROOT / "gdt002_discovery_atlas.json", summary)

    hypotheses = {
        "artifact": "GDT002_INITIAL_JOINT_HYPOTHESIS_SCHEMA_V1",
        "status": "CAPACITY_BLOCKED_NO_IDENTIFIABLE_WORLD_TEMPLATES",
        "evidence_class": "LATENT_ROLE_HYPOTHESIS",
        "role_vocabulary": [
            "OBJECT_ENTITY", "PROCESS_OPERATION", "PROCESS_STAGE", "STATE_PROPERTY", "RELATION",
            "SOURCE_DESTINATION", "POSITION", "QUANTITY_DEGREE", "CASE_INDICATION",
            "MATERIAL_SUBSTANCE", "DISCOURSE_RECORD_STATE", "UNKNOWN",
        ],
        "templates": [],
        "score_state": "NOT_RUN",
        "selection_state": "NO_BEST_HYPOTHESIS",
        "note": "The current visual/text links reduce to isolated one-group labels and do not identify a joint role world. Exact-family-to-role templates are prohibited as a renamed label decoder. A solver requires a new repeated author-visible relation with at least two competing formal states and held support.",
    }
    write_json(ROOT / "gdt002_joint_hypotheses.json", hypotheses)

    discovery_result = {
        "experiment": "GDT002_VISUAL_GRAMMAR_CONSTRAINTS",
        "phase": "DISCOVERY_SOLVER",
        "status": "NO_IDENTIFIABLE_SOLVER_FROM_CURRENT_PANEL",
        "discovery_pages": list(DISCOVERY_PAGES),
        "holdout_page": HOLDOUT_PAGE,
        "atlas_sha256": sha256(ROOT / "gdt002_discovery_atlas.json"),
        "hypothesis_templates_sha256": sha256(ROOT / "gdt002_joint_hypotheses.json"),
        "retained_hypotheses": [],
        "scores": [],
        "claim_ceiling": "No semantic role or interpretation has been selected.",
    }
    write_json(ROOT / "gdt002_discovery_results.json", discovery_result)

    outputs = [
        "gdt002_visual_inventory.tsv", "gdt002_grammar_projection.tsv",
        "gdt002_grammar_consensus_projection.tsv", "gdt002_repeated_structure_atlas.tsv",
        "gdt002_f84r_holdout_projection_commitment.json", "gdt002_discovery_atlas.json",
        "gdt002_joint_hypotheses.json", "gdt002_discovery_results.json",
    ]
    result = {
        "experiment": "GDT002_VISUAL_GRAMMAR_CONSTRAINTS",
        "phase": "FIRST_CHECKPOINT",
        "status": "PASS_INVENTORY_NO_IDENTIFIABLE_SOLVER_CURRENT_PANEL",
        "access": {
            "images_opened": False, "ocr_or_automated_vision_used": False,
            "new_ai_direct_visual_observations": False,
            "f84r_exact_projection_generated_transiently_for_commitment": True,
            "f84r_exact_projection_published": False,
            "f84r_exact_projection_displayed_or_manually_inspected": False,
            "f84r_exact_projection_joined_or_used_for_discovery": False,
            "f84r_prior_repository_text_exposure_disclosed": True,
            "joint_solver_run": False,
        },
        "counts": summary["counts"],
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in INPUTS.values()},
        "outputs": {name: sha256(ROOT / name) for name in outputs},
        "claim_ceiling": summary["claim_ceiling"],
        "next": "Acquire one new repeated author-visible relation with contrasting formal states and held support; only then freeze a joint solver. Do not open the committed f84r payload before a valid discovery-world freeze.",
    }
    result["documents_and_implementation"] = {name: sha256(ROOT / name) for name in DOCUMENTS}
    write_json(ROOT / "gdt002_checkpoint_result.json", result)


if __name__ == "__main__":
    build()
