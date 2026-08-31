#!/usr/bin/env python3
"""Build GDT685's exhaustive CH/SH/T+OL state-cell dispatch."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch"
ART = EXP / "artifacts"

OCCURRENCE_PATH = ROOT / "experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_CARRIER_OCCURRENCES.tsv"
MATRIX_PATH = ROOT / "experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv"
CHOL_VALUE_PATH = ROOT / "experiments/yolo/gdt628_chol_measure_frame/artifacts/CHOL_VALUE_REALIZATIONS.tsv"
VALUE_PATH = ROOT / "experiments/yolo/gdt630_outer_carrier_attachment/artifacts/VALUE_EXPRESSION_OCCURRENCES.tsv"
PART_PATH = ROOT / "experiments/yolo/gdt630_outer_carrier_attachment/artifacts/IMMEDIATE_PART_QUALITY_ATTACHMENTS.tsv"
E_OL_PATH = ROOT / "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv"
STEM_PATH = ROOT / "experiments/yolo/gdt664_one_hundred_forty_residual_family_completion/artifacts/STEM_MODEL_V41.tsv"
GLOSSARY_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/V48_WORKING_TOKEN_GLOSSARY.tsv"
OL_RESULT_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/RESULT.json"
OL_AUDIT_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/OL_463_OCCURRENCE_AUDIT.tsv"
V57_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/V57_51_LINE_READER.tsv"
DEBT_PATH = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts/V57_479_POSITION_INFORMATION_AUDIT.tsv"
DEBT_RESULT_PATH = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts/RESULT.json"
PATCH_SPECS_PATH = EXP / "src/V58_LINE_PATCH_SPECS.tsv"

TARGETS = {
    "chol": {
        "core": "ch",
        "state_de": "trocken",
        "state_card": "TROCKENQUALITAET",
        "composition": "CH_DRY+OL_STATE_CARRIER",
    },
    "shol": {
        "core": "sh",
        "state_de": "feucht",
        "state_card": "FEUCHTQUALITAET",
        "composition": "SH_MOIST+OL_STATE_CARRIER",
    },
    "tol": {
        "core": "t",
        "state_de": "kalt",
        "state_card": "KALTQUALITAET",
        "composition": "T_COLD+OL_STATE_CARRIER",
    },
}

LITERAL_REPLACEMENTS = {
    "chol": ("trocken; nominal trockenes Gut/Material", "trocken"),
    "shol": ("feucht; nominal feuchtes Gut/Material", "feucht"),
    "tol": ("kalt; nominal kaltes Gut/Material", "kalt"),
}

ALIGNED_REPLACEMENTS = {
    "Trockengut": "trocken",
    "Feuchtgut": "feucht",
    "Kaltes Gut": "kalt",
}

MATERIA_RE = re.compile(
    r"Wurzel|Samen|Saatgut|Holz|Kraut|Blatt|Blüt|Frucht|Pulver|Harz|Gummi|Species|Arzneikompositum",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        if not rows:
            raise ValueError(f"cannot infer fields for empty table {path}")
        fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_all(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def make_glossary(rows: list[dict[str, str]]) -> dict[str, str]:
    glossary: dict[str, str] = {}
    for row in rows:
        surface = row["surface"]
        gloss = row["working_meaning_de"]
        if surface in glossary and glossary[surface] != gloss:
            raise AssertionError(f"non-unique current gloss for {surface}")
        glossary[surface] = gloss
    return glossary


def local_materia_neighbors(
    tokens: list[str], token_index: int, glossary: dict[str, str]
) -> list[tuple[int, str, str]]:
    found: list[tuple[int, str, str]] = []
    for distance in (1, 2):
        for offset in (-distance, distance):
            index = token_index - 1 + offset
            if not 0 <= index < len(tokens):
                continue
            surface = tokens[index]
            gloss = glossary.get(surface, "")
            if gloss and MATERIA_RE.search(gloss):
                found.append((offset, surface, gloss))
    return found


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_carrier_rows = read_tsv(OCCURRENCE_PATH)
    target_rows = [row for row in all_carrier_rows if row["surface"] in TARGETS]
    matrix_rows = read_tsv(MATRIX_PATH)
    value_rows = [row for row in read_tsv(VALUE_PATH) if row["base_surface"] in TARGETS]
    direct_chol_rows = [
        row for row in read_tsv(CHOL_VALUE_PATH) if row["realization_mode"] == "DIRECT_A_VALUE"
    ]
    part_rows = [row for row in read_tsv(PART_PATH) if row["base_surface"] in TARGETS]
    glossary = make_glossary(read_tsv(GLOSSARY_PATH))
    v57_rows = read_tsv(V57_PATH)
    debt_rows = read_tsv(DEBT_PATH)
    debt_result = json.loads(DEBT_RESULT_PATH.read_text(encoding="utf-8"))
    ol_result = json.loads(OL_RESULT_PATH.read_text(encoding="utf-8"))
    patch_specs = {row["locus"]: row for row in read_tsv(PATCH_SPECS_PATH)}

    if len(target_rows) != 540:
        raise AssertionError(f"expected 540 target rows, got {len(target_rows)}")
    if any(row["page"].lower().startswith("f84") for row in target_rows):
        raise AssertionError("sealed page leaked into target circuit")
    target_keys = {(row["locus"], int(row["token_index"])) for row in target_rows}
    if len(target_keys) != len(target_rows):
        raise AssertionError("target occurrence keys are not unique")
    if Counter(row["role"] for row in target_rows) != {"QUALITY_STATE_CARRIER": 540}:
        raise AssertionError("target role changed from quality/state carrier")

    separate_values: dict[tuple[str, int], dict[str, str]] = {}
    for row in value_rows:
        if row["realization_mode"] != "SEPARATE_D_VALUE":
            continue
        key = (row["locus"], int(row["token_index_start"]))
        if key in separate_values:
            raise AssertionError(f"duplicate value expression {key}")
        separate_values[key] = row
    if len(separate_values) != 49:
        raise AssertionError(f"expected 49 exact separate target values, got {len(separate_values)}")
    if len(value_rows) != 54 or len(direct_chol_rows) != 3:
        raise AssertionError("expected 54 d-value plus three direct-a value expressions")

    parts_by_expression = {row["expression_id"]: row for row in part_rows}
    if len(part_rows) != 7:
        raise AssertionError("expected seven visible part contacts for target bases")

    core_surfaces = {
        row["surface"] for row in matrix_rows
        if row["ending"] == "OL" and row["quality_core"] != "NONE" and row["occupied"] == "1"
    }
    core_carrier_rows = [
        row for row in all_carrier_rows
        if row["ending"] == "OL" and row["quality_core"] != "NONE"
    ]
    if len(core_surfaces) != 23 or len(core_carrier_rows) != 935:
        raise AssertionError("core-bearing OL family changed")

    census_rows: list[dict[str, object]] = []
    for serial, source in enumerate(sorted(
        target_rows,
        key=lambda row: (row["surface"], row["page"], row["locus"], int(row["token_index"])),
    ), 1):
        surface = source["surface"]
        target = TARGETS[surface]
        key = (source["locus"], int(source["token_index"]))
        value = separate_values.get(key)
        part = parts_by_expression.get(value["expression_id"]) if value else None
        tokens = source["surface_line"].split()
        token_index = int(source["token_index"])
        if tokens[token_index - 1] != surface:
            raise AssertionError(f"token index mismatch at {key}")
        local_heads = local_materia_neighbors(tokens, token_index, glossary)
        free_ol_contact = source["left_surface"] == "ol" or source["right_surface"] == "ol"
        quality_neighbor = source["left_surface"] in core_surfaces or source["right_surface"] in core_surfaces

        if part:
            context_mode = "QUALITY_DEGREE_WITH_VISIBLE_PART_HEAD"
            renderer = part["working_reading_de"]
            head_policy = f"VISIBLE_PART:{part['part_surface']}"
        elif value:
            context_mode = "QUALITY_DEGREE_HEAD_OPEN"
            renderer = f"{target['state_de']}, Grad {value['working_roman']}; Kopf offen"
            head_policy = "OUTER_OR_INHERITED_HEAD_OPEN"
        elif free_ol_contact:
            context_mode = "QUALITY_CELL_NEXT_TO_OL_CONTACT"
            renderer = f"{target['state_de']}; benachbartes ol separat beziehungsweise lesergebunden prüfen"
            head_policy = "DO_NOT_SILENTLY_ABSORB_ADJACENT_OL"
        elif local_heads:
            context_mode = "QUALITY_WITH_LOCAL_MATERIA_CANDIDATE"
            renderer = f"{local_heads[0][2]}: {target['state_de']}"
            head_policy = f"LOCAL_CANDIDATE:{local_heads[0][1]}"
        elif quality_neighbor:
            context_mode = "PARALLEL_OR_CONTRASTING_QUALITY_CELLS"
            renderer = target["state_de"]
            head_policy = "PRESERVE_SEPARATE_QUALITY_CELL"
        else:
            context_mode = "QUALITY_STATE_HEAD_OPEN"
            renderer = target["state_de"]
            head_policy = "OUTER_OR_INHERITED_HEAD_OPEN"

        first_head = local_heads[0] if local_heads else None
        reader_status = (
            "TRIPLE_READER_EXACT" if source["triple_reading_token_stable"] == "1"
            else "ZL3B_EXACT__ALTERNATE_READER_VARIANT"
        )
        census_rows.append({
            "case_id": f"G685-O{serial:04d}",
            "surface": surface,
            "page": source["page"],
            "locus": source["locus"],
            "token_index": source["token_index"],
            "section": source["section"],
            "hand": source["hand"],
            "line_position": source["position"],
            "reader_status": reader_status,
            "composition": target["composition"],
            "quality_core": target["core"],
            "state_card": target["state_card"],
            "default_de": target["state_de"],
            "ol_function": "QUALITY_STATE_CARRIER__GERMAN_CONTRIBUTION_ZERO_WITH_VISIBLE_CORE",
            "context_mode": context_mode,
            "contextual_renderer_de": renderer,
            "head_policy": head_policy,
            "degree_expression_id": value["expression_id"] if value else "NONE",
            "degree_roman": value["working_roman"] if value else "NONE",
            "visible_part_surface": part["part_surface"] if part else "NONE",
            "visible_part_role": part["part_role"] if part else "NONE",
            "local_materia_surface": first_head[1] if first_head else "NONE",
            "local_materia_gloss_de": first_head[2] if first_head else "NONE",
            "local_materia_offset": first_head[0] if first_head else 0,
            "all_local_materia_neighbors": " | ".join(
                f"{offset:+d}:{neighbor_surface}={gloss}" for offset, neighbor_surface, gloss in local_heads
            ) if local_heads else "NONE",
            "left_surface": source["left_surface"],
            "left_gloss_de": glossary.get(source["left_surface"], "OPEN"),
            "right_surface": source["right_surface"],
            "right_gloss_de": glossary.get(source["right_surface"], "OPEN"),
            "old_generic_gloss_de": source["working_meaning_de"],
            "rejected_universal_default_de": (
                "Trockenansatz" if surface == "chol" else "Feuchtansatz" if surface == "shol" else "Kaltansatz"
            ),
            "live_rival_de": "nominale Materialform nur bei lokal sichtbarem oder geerbtem Kopf",
            "decision": "ACCEPT_STATE_CELL__REJECT_UNIVERSAL_ANSATZ_HEAD",
            "surface_line": source["surface_line"],
        })

    related_value_rows: list[dict[str, object]] = []
    for row in sorted(value_rows, key=lambda item: (item["base_surface"], item["page"], item["locus"], int(item["token_index_start"]))):
        part = parts_by_expression.get(row["expression_id"])
        related_value_rows.append({
            "expression_id": row["expression_id"],
            "surface": row["base_surface"],
            "page": row["page"],
            "locus": row["locus"],
            "realization_mode": row["realization_mode"],
            "surface_expression": row["surface_expression"],
            "working_roman": row["working_roman"],
            "state_renderer_de": TARGETS[row["base_surface"]]["state_de"],
            "visible_part_surface": part["part_surface"] if part else "NONE",
            "contextual_renderer_de": (
                part["working_reading_de"] if part else row["working_reading_de"]
            ),
            "expression_triple_reader_stable": row["expression_triple_reader_stable"],
            "source": "GDT630",
            "surface_line": row["surface_line"],
        })
    for row in sorted(direct_chol_rows, key=lambda item: (item["page"], item["locus"], int(item["token_index"]))):
        related_value_rows.append({
            "expression_id": row["realization_id"],
            "surface": "chol",
            "page": row["page"],
            "locus": row["locus"],
            "realization_mode": row["realization_mode"],
            "surface_expression": row["surface_expression"],
            "working_roman": row["working_roman"],
            "state_renderer_de": "trocken",
            "visible_part_surface": "NONE",
            "contextual_renderer_de": row["working_reading_de"],
            "expression_triple_reader_stable": row["all_expression_tokens_stable"],
            "source": "GDT628",
            "surface_line": row["surface_line"],
        })
    related_value_rows.sort(key=lambda row: (str(row["surface"]), str(row["page"]), str(row["locus"]), str(row["expression_id"])))

    counts = Counter(row["surface"] for row in census_rows)
    triple_counts = Counter(row["surface"] for row in census_rows if row["reader_status"] == "TRIPLE_READER_EXACT")
    exact_degree_counts = Counter(row["surface"] for row in census_rows if row["degree_expression_id"] != "NONE")
    pages_by_surface: dict[str, set[str]] = defaultdict(set)
    loci_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in census_rows:
        pages_by_surface[str(row["surface"])].add(str(row["page"]))
        loci_by_surface[str(row["surface"])].add(str(row["locus"]))

    ol_contact_rows = [row for row in census_rows if row["context_mode"] == "QUALITY_CELL_NEXT_TO_OL_CONTACT"]
    ol_audit = read_tsv(OL_AUDIT_PATH)
    ol_by_locus_ordinal = {(row["locus"], row["ordinal"]): row for row in ol_audit}
    free_ol_contact_rows: list[dict[str, object]] = []
    for row in ol_contact_rows:
        target_index = int(row["token_index"])
        ol_index = target_index - 1 if row["left_surface"] == "ol" else target_index + 1
        ol_row = ol_by_locus_ordinal.get((str(row["locus"]), str(ol_index)))
        contact_class = (
            "BOUND_READER_COMPOUND"
            if ol_row and ol_row["semantic_decision"] == "BOUND_OL_MATERIAL_COMPONENT"
            else "FREE_SEPARATE_OL"
        )
        free_ol_contact_rows.append({
            "surface": row["surface"],
            "page": row["page"],
            "locus": row["locus"],
            "target_token_index": row["token_index"],
            "ol_token_index": ol_index,
            "order": "OL_XOL" if row["left_surface"] == "ol" else "XOL_OL",
            "target_default_de": row["default_de"],
            "ol_working_translation_de": ol_row["working_translation_de"] if ol_row else "Grundansatz",
            "ol_semantic_decision": ol_row["semantic_decision"] if ol_row else "BILATERAL_PORTABLE_OL_BASE",
            "reader_scope": ol_row["reader_scope"] if ol_row else "INHERITED_FROM_GDT683",
            "contact_class": contact_class,
            "consequence": (
                "free OL remains a separately licensed Grundansatz card"
                if contact_class == "FREE_SEPARATE_OL"
                else "alternate readers bind the apparent ZL3b contact; render the GDT683 span once"
            ),
            "surface_line": row["surface_line"],
        })
    if len(free_ol_contact_rows) != 10:
        raise AssertionError("expected ten visible target/ol contacts")
    true_free_ol_rows = [row for row in free_ol_contact_rows if row["contact_class"] == "FREE_SEPARATE_OL"]
    if len(true_free_ol_rows) != 8:
        raise AssertionError("expected eight genuinely free target/ol contacts")

    v58_rows: list[dict[str, object]] = []
    patched_lines: list[dict[str, object]] = []
    v57_target_counts: Counter[str] = Counter()
    total_revisions = 0
    for source in v57_rows:
        row: dict[str, object] = dict(source)
        surfaces = source["zl3b_line"].split()
        old_glosses = source["literal_token_glosses_de"].split(" | ")
        if len(surfaces) != len(old_glosses):
            raise AssertionError(f"V57 alignment mismatch at {source['locus']}")
        new_glosses = list(old_glosses)
        revised_surfaces: list[str] = []
        for index, surface in enumerate(surfaces):
            if surface not in TARGETS:
                continue
            expected, replacement = LITERAL_REPLACEMENTS[surface]
            if new_glosses[index] != expected:
                raise AssertionError(f"unexpected inherited gloss at {source['locus']}#{index + 1}")
            new_glosses[index] = replacement
            revised_surfaces.append(surface)
            v57_target_counts[surface] += 1
            total_revisions += 1
        row["literal_token_glosses_de"] = " | ".join(new_glosses)
        row["aligned_line_de"] = replace_all(source["aligned_line_de"], ALIGNED_REPLACEMENTS)
        if revised_surfaces:
            if source["locus"] not in patch_specs:
                raise AssertionError(f"missing V58 line patch spec {source['locus']}")
            spec = patch_specs[source["locus"]]
            row["practical_translation_de"] = spec["practical_translation_de"]
            row["review_note"] = source["review_note"] + " GDT685: " + spec["local_dispatch"]
            row["v58_local_dispatch"] = spec["local_dispatch"]
            row["v58_patch_basis"] = spec["basis"]
        else:
            row["v58_local_dispatch"] = "NONE"
            row["v58_patch_basis"] = "NONE"
        row["v58_semantic_revisions"] = len(revised_surfaces)
        row["v58_target_surfaces"] = "|".join(revised_surfaces) if revised_surfaces else "NONE"
        v58_rows.append(row)
        if revised_surfaces:
            patched_lines.append({
                "page": source["page"],
                "locus": source["locus"],
                "target_surfaces": "|".join(revised_surfaces),
                "revisions": len(revised_surfaces),
                "old_literal_token_glosses_de": source["literal_token_glosses_de"],
                "new_literal_token_glosses_de": row["literal_token_glosses_de"],
                "old_aligned_line_de": source["aligned_line_de"],
                "new_aligned_line_de": row["aligned_line_de"],
                "old_practical_translation_de": source["practical_translation_de"],
                "new_practical_translation_de": row["practical_translation_de"],
                "local_dispatch": row["v58_local_dispatch"],
                "basis": row["v58_patch_basis"],
            })
    if total_revisions != 8 or len(patched_lines) != 7:
        raise AssertionError("V58 target patch is not exactly 8 positions / 7 lines")
    if v57_target_counts != Counter({"chol": 6, "shol": 1, "tol": 1}):
        raise AssertionError(f"unexpected V58 surface counts {v57_target_counts}")

    target_debts = [row for row in debt_rows if row["surface"] in TARGETS]
    if len(target_debts) != 8:
        raise AssertionError("expected eight V57 target debt rows")
    debt_delta_rows: list[dict[str, object]] = []
    for row in target_debts:
        state = TARGETS[row["surface"]]["state_de"]
        debt_delta_rows.append({
            "page": row["page"],
            "locus": row["locus"],
            "ordinal": row["ordinal"],
            "surface": row["surface"],
            "old_literal_gloss_de": row["literal_gloss_de"],
            "new_literal_gloss_de": state,
            "old_primary_class": row["primary_class"],
            "new_primary_class": "C2_STATE_WITHOUT_OBJECT",
            "old_debt_severity": row["debt_severity"],
            "new_debt_severity": "MAJOR",
            "old_strict_card_debt": row["strict_card_debt"],
            "new_strict_card_debt": 0,
            "old_mechanical_debt": row["mechanical_debt"],
            "new_mechanical_debt": 1,
            "old_mechanical_debt_flags": row["mechanical_debt_flags"],
            "new_mechanical_debt_flags": "STATE_ONLY_NO_OBJECT",
            "old_specificity_open": row["specificity_open"],
            "new_specificity_open": 1,
            "information_gain": "single concrete state; slash alternative and invented generic noun removed",
            "remaining_debt": "outer or inherited object head is not always identified",
        })

    mechanical_before = debt_result["mechanical_visible_debt"]["classes"]
    mechanical_after = dict(mechanical_before)
    mechanical_after["NON_SINGLE_GLOSS"] -= 8
    mechanical_after["HARD_GENERIC_CARRIER"] -= 8
    mechanical_after["STATE_ONLY_NO_OBJECT"] += 8
    debt_summary_rows = [
        {
            "metric": "strict_card_debt_positions",
            "v57_before": debt_result["strict_card_debt_positions"],
            "v58_after": int(debt_result["strict_card_debt_positions"]) - 8,
            "delta": -8,
            "interpretation": "the three exact state cards no longer use generic Gut/Material alternatives",
        },
        {
            "metric": "mechanical_visible_debt_union_positions",
            "v57_before": debt_result["mechanical_visible_debt"]["union_positions"],
            "v58_after": debt_result["mechanical_visible_debt"]["union_positions"],
            "delta": 0,
            "interpretation": "each repaired card remains an objectless state until a local head binds",
        },
        {
            "metric": "mechanical_flag_memberships",
            "v57_before": debt_result["mechanical_visible_debt"]["class_memberships"],
            "v58_after": int(debt_result["mechanical_visible_debt"]["class_memberships"]) - 8,
            "delta": -8,
            "interpretation": "sixteen old generic/multivalue flags become eight honest state-only flags",
        },
        {
            "metric": "broad_specificity_open_positions",
            "v57_before": debt_result["broad_specificity_open_positions"],
            "v58_after": debt_result["broad_specificity_open_positions"],
            "delta": 0,
            "interpretation": "the exact ingredient or outer head remains open",
        },
        {
            "metric": "four_layer_union_with_low_confidence_positions",
            "v57_before": debt_result["four_layer_union_with_low_confidence_positions"],
            "v58_after": debt_result["four_layer_union_with_low_confidence_positions"],
            "delta": 0,
            "interpretation": "all eight revised positions remain in the broad and mechanical layers",
        },
    ]
    for flag in ("OPEN_COMPOSITION", "NON_SINGLE_GLOSS", "STRUCTURAL_META_AS_VALUE", "HARD_GENERIC_CARRIER", "STATE_ONLY_NO_OBJECT"):
        debt_summary_rows.append({
            "metric": f"mechanical_class:{flag}",
            "v57_before": mechanical_before[flag],
            "v58_after": mechanical_after[flag],
            "delta": mechanical_after[flag] - mechanical_before[flag],
            "interpretation": "class-level literal renderer count",
        })

    surface_summary_rows: list[dict[str, object]] = []
    for surface in ("chol", "shol", "tol"):
        target_values = [row for row in related_value_rows if row["surface"] == surface]
        surface_summary_rows.append({
            "surface": surface,
            "composition": TARGETS[surface]["composition"],
            "default_de": TARGETS[surface]["state_de"],
            "state_card": TARGETS[surface]["state_card"],
            "occurrences": counts[surface],
            "pages": len(pages_by_surface[surface]),
            "loci": len(loci_by_surface[surface]),
            "triple_reader_exact_occurrences": triple_counts[surface],
            "alternate_reader_variant_occurrences": counts[surface] - triple_counts[surface],
            "exact_separate_degree_positions": exact_degree_counts[surface],
            "all_value_realizations": len(target_values),
            "direct_or_fused_value_realizations": sum(
                row["realization_mode"] != "SEPARATE_D_VALUE" for row in target_values
            ),
            "free_ol_contacts": sum(row["surface"] == surface for row in true_free_ol_rows),
            "reader_bound_ol_contacts": sum(
                row["surface"] == surface and row["contact_class"] == "BOUND_READER_COMPOUND"
                for row in free_ol_contact_rows
            ),
            "v57_positions_revised": v57_target_counts[surface],
            "rejected_universal_noun": (
                "Trockenansatz" if surface == "chol" else "Feuchtansatz" if surface == "shol" else "Kaltansatz"
            ),
            "decision": "STATE_CELL_WITH_OUTER_OR_INHERITED_HEAD",
        })

    context_counts = Counter(row["context_mode"] for row in census_rows)
    context_summary_rows = [
        {
            "context_mode": mode,
            "positions": count,
            "surfaces": "|".join(sorted({str(row["surface"]) for row in census_rows if row["context_mode"] == mode})),
            "renderer_policy": (
                "bind the explicit part and render PART: quality, degree"
                if mode == "QUALITY_DEGREE_WITH_VISIBLE_PART_HEAD"
                else "render quality and degree; leave the outer head open"
                if mode == "QUALITY_DEGREE_HEAD_OPEN"
                else "adjudicate whether ol is free or reader-bound; never absorb it silently"
                if mode == "QUALITY_CELL_NEXT_TO_OL_CONTACT"
                else "offer the adjacent materia card as a local candidate, never a global export"
                if mode == "QUALITY_WITH_LOCAL_MATERIA_CANDIDATE"
                else "preserve each quality cell separately"
                if mode == "PARALLEL_OR_CONTRASTING_QUALITY_CELLS"
                else "render the concrete state and leave the head open"
            ),
        }
        for mode, count in sorted(context_counts.items())
    ]

    e_ol_cards = read_tsv(E_OL_PATH)
    evidence_rows = [
        {
            "evidence_id": "G685-E01",
            "evidence": "productive core-bearing OL lattice",
            "observed": f"23/24 cells; {len(core_carrier_rows)} tokens on {len({row['page'] for row in core_carrier_rows})} pages; {sum(int(row['triple_reading_token_stable']) for row in core_carrier_rows)} reader-exact",
            "consequence": "OL is a reusable state carrier under visible quality cores",
            "source": str(MATRIX_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G685-E02",
            "evidence": "all target source roles",
            "observed": "540/540 QUALITY_STATE_CARRIER; 0 PREPARATION; 0 ACTION",
            "consequence": "the common portable value is state/quality, not a preparation noun",
            "source": str(OCCURRENCE_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G685-E03",
            "evidence": "degree realization",
            "observed": "49 exact separate target tokens plus 8 direct/fused forms",
            "consequence": "trocken/feucht/kalt behave as values before an outer or inherited head",
            "source": f"{VALUE_PATH.relative_to(ROOT)} | {CHOL_VALUE_PATH.relative_to(ROOT)}",
        },
        {
            "evidence_id": "G685-E04",
            "evidence": "visible outer parts",
            "observed": "7 target-base contacts: 5 chol, 2 shol; six retain an exact separate target token",
            "consequence": "written part heads bind the state; X+OL does not need to contain Ansatz",
            "source": str(PART_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G685-E05",
            "evidence": "E+OL exact whole contrast",
            "observed": "; ".join(f"{row['surface']}={row['working_meaning_de']} ({row['occurrences']}x)" for row in e_ol_cards),
            "consequence": "the explicit Drogenstoff head appears in exact E+OL wholes; it is not back-exported to bare X+OL",
            "source": str(E_OL_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G685-E06",
            "evidence": "target next to separately written free ol",
            "observed": "10 visible contacts: 8 genuinely free, 2 reader-bound; f21r.6 binds chol|ol as dry material in Grundansatz",
            "consequence": "free Grundansatz belongs to its own OL card; bound cases require one local span, never universal suffix export",
            "source": f"{OCCURRENCE_PATH.relative_to(ROOT)} | {OL_AUDIT_PATH.relative_to(ROOT)}",
        },
        {
            "evidence_id": "G685-E07",
            "evidence": "current stem directions",
            "observed": "ch=trocken; sh=feucht/einweichen; t=kalt/abkühlen; ol naked whole=Grundansatz MEDIUM",
            "consequence": "retain the three state cores but block whole-word OL semantics from substring export",
            "source": f"{STEM_PATH.relative_to(ROOT)} | {OL_RESULT_PATH.relative_to(ROOT)}",
        },
    ]

    hypothesis_rows = [
        {
            "rank": 1,
            "hypothesis": "STATE_CELL_WITH_OUTER_OR_INHERITED_HEAD",
            "defaults_de": "chol=trocken; shol=feucht; tol=kalt",
            "coverage": 540,
            "strength": "all target roles, 23/24 OL lattice, 57 value realizations, visible part clauses and E+OL contrast",
            "weakness": "some standalone cells retain an unidentified head",
            "disposition": "PRIMARY",
        },
        {
            "rank": 2,
            "hypothesis": "NOMINAL_STATE_MATERIAL_FALLBACK",
            "defaults_de": "Trockengut/Feuchtgut/Kaltgut",
            "coverage": 540,
            "strength": "supplies a noun in elliptical lists",
            "weakness": "adds an unobserved generic object and caused the V57 information complaint",
            "disposition": "REJECT_AS_DEFAULT__LOCAL_FALLBACK_ONLY",
        },
        {
            "rank": 3,
            "hypothesis": "UNIVERSAL_STATE_PLUS_OL_ANSATZ_HEAD",
            "defaults_de": "Trockenansatz/Feuchtansatz/Kaltansatz",
            "coverage": 540,
            "strength": "reuses the learned naked ol=Grundansatz card",
            "weakness": "GDT628 says OL contributes zero under quality cores; visible outer heads, E+OL contrast and free-ol contacts contradict universal nominalization",
            "disposition": "REJECT_GLOBAL__ALLOW_ONLY_WITH_VISIBLE_ANSATZ_HEAD",
        },
        {
            "rank": 4,
            "hypothesis": "CHO_OR_SHO_PLUS_L_WOOD",
            "defaults_de": "chol=cho+l; shol=sho+l; tol needs a new to+l card",
            "coverage": 506,
            "strength": "cho/sho preparation shells and bound l=Holzdroge are independently live",
            "weakness": "fails as one rule for tol and overpredicts wood in part-quality-degree clauses",
            "disposition": "LIVE_LOCAL_BOUNDARY_RIVAL",
        },
        {
            "rank": 5,
            "hypothesis": "THREE_LEARNED_WHOLES",
            "defaults_de": "memorize all three target forms",
            "coverage": 540,
            "strength": "fits the observed surfaces",
            "weakness": "does not predict the wider quality lattice",
            "disposition": "POSSIBLE_BUT_UNECONOMICAL",
        },
    ]

    counterexample_rows = [
        {
            "counterexample": "VISIBLE_PART_QUALITY_DEGREE",
            "cases": 7,
            "example_loci": "f100r.25|f15v.11|f21r.12|f32v.10|f3r.3|f5v.4|f8r.9",
            "failure_of_universal_ansatz": "the written plant/leaf/flower head already owns dry or moist degree N",
            "surviving_reading": "PART: state, degree",
        },
        {
            "counterexample": "FREE_OL_CONTACT",
            "cases": 8,
            "example_loci": "|".join(str(row["locus"]) for row in true_free_ol_rows),
            "failure_of_universal_ansatz": "a separate ol can carry Grundansatz beside chol/shol",
            "surviving_reading": "state cell plus separately written Grundansatz",
        },
        {
            "counterexample": "QUALITY_CELL_RUNS",
            "cases": sum(row["context_mode"] == "PARALLEL_OR_CONTRASTING_QUALITY_CELLS" for row in census_rows),
            "example_loci": "f21r.11|f42r.20|f42r.21|f44v.1|f47r.6|f56v.7",
            "failure_of_universal_ansatz": "sequences of contrasting state cells become gratuitous lists of invented preparations",
            "surviving_reading": "keep every state cell separate and inherit the outer head",
        },
        {
            "counterexample": "E_OL_HEAD_CONTRAST",
            "cases": sum(int(row["occurrences"]) for row in e_ol_cards),
            "example_loci": "cheol|cheor|tcheol occurrence circuits",
            "failure_of_universal_ansatz": "only exact E+OL wholes are licensed as Drogenstoff/Drogenteil",
            "surviving_reading": "no bare-OL or substring head promotion",
        },
        {
            "counterexample": "ALTERNATE_READER_BOUNDARY",
            "cases": len(census_rows) - sum(triple_counts.values()),
            "example_loci": "all rows marked ZL3B_EXACT__ALTERNATE_READER_VARIANT",
            "failure_of_universal_ansatz": "the exact word boundary is not portable at every target locus",
            "surviving_reading": "state default stays ZL3b-local with the variant visible",
        },
    ]

    write_tsv(output_dir / "TARGET_540_STATE_CELL_CENSUS.tsv", census_rows)
    write_tsv(output_dir / "RELATED_57_VALUE_REALIZATIONS.tsv", related_value_rows)
    write_tsv(output_dir / "TARGET_OL_CONTACTS.tsv", free_ol_contact_rows)
    write_tsv(output_dir / "SURFACE_STATE_DISPATCH_SUMMARY.tsv", surface_summary_rows)
    write_tsv(output_dir / "CONTEXT_MODE_SUMMARY.tsv", context_summary_rows)
    write_tsv(output_dir / "COMPOSITION_EVIDENCE.tsv", evidence_rows)
    write_tsv(output_dir / "HYPOTHESIS_COMPARISON.tsv", hypothesis_rows)
    write_tsv(output_dir / "COUNTEREXAMPLE_AUDIT.tsv", counterexample_rows)
    write_tsv(output_dir / "V58_51_LINE_READER.tsv", v58_rows)
    write_tsv(output_dir / "V58_PATCHED_LINES.tsv", patched_lines)
    write_tsv(output_dir / "V58_TARGET_POSITION_DEBT_DELTA.tsv", debt_delta_rows)
    write_tsv(output_dir / "V58_DEBT_SUMMARY.tsv", debt_summary_rows)

    reader_lines = [
        "# GDT685 — V58 state-cell patch reader",
        "",
        "The tested universal nouns `Trockenansatz / Feuchtansatz / Kaltansatz` do not survive the full occurrence circuit.",
        "The portable defaults are `chol = trocken`, `shol = feucht`, and `tol = kalt`; a visible or inherited outer head supplies the material.",
        "",
        "## Revised V57 lines",
        "",
    ]
    for row in patched_lines:
        reader_lines.extend([
            f"### {row['locus']}",
            "",
            str(row["new_practical_translation_de"]),
            "",
            f"Dispatch: {row['local_dispatch']}",
            "",
        ])
    reader_lines.extend([
        "## Working limit",
        "",
        "These are concrete state cards, not ingredient identities. A nominal `-gut/-stoff` fallback is no longer printed by default; where no head is visible, the state remains explicit and the head remains open.",
    ])
    (output_dir / "GDT685_V58_STATE_CELL_READER.md").write_text(
        "\n".join(reader_lines).rstrip() + "\n", encoding="utf-8"
    )

    artifact_names = [
        "TARGET_540_STATE_CELL_CENSUS.tsv",
        "RELATED_57_VALUE_REALIZATIONS.tsv",
        "TARGET_OL_CONTACTS.tsv",
        "SURFACE_STATE_DISPATCH_SUMMARY.tsv",
        "CONTEXT_MODE_SUMMARY.tsv",
        "COMPOSITION_EVIDENCE.tsv",
        "HYPOTHESIS_COMPARISON.tsv",
        "COUNTEREXAMPLE_AUDIT.tsv",
        "V58_51_LINE_READER.tsv",
        "V58_PATCHED_LINES.tsv",
        "V58_TARGET_POSITION_DEBT_DELTA.tsv",
        "V58_DEBT_SUMMARY.tsv",
        "GDT685_V58_STATE_CELL_READER.md",
    ]
    result: dict[str, object] = {
        "status": "REJECT_UNIVERSAL_ANSATZ_HEAD__PASS_540_STATE_CELL_DISPATCH__V58_EIGHT_GENERIC_HEADS_REMOVED",
        "basis": {
            "target_occurrences": len(census_rows),
            "target_pages_union": len({str(row["page"]) for row in census_rows}),
            "triple_reader_exact_occurrences": sum(triple_counts.values()),
            "alternate_reader_variant_occurrences": len(census_rows) - sum(triple_counts.values()),
            "core_ol_occurrences": len(core_carrier_rows),
            "core_ol_pages": len({row["page"] for row in core_carrier_rows}),
            "core_ol_triple_reader_exact_occurrences": sum(int(row["triple_reading_token_stable"]) for row in core_carrier_rows),
            "occupied_core_ol_cells": len(core_surfaces),
            "possible_core_ol_cells": 24,
            "value_realizations": len(related_value_rows),
            "exact_separate_degree_target_positions": len(separate_values),
            "visible_part_contacts": len(part_rows),
            "visible_ol_contacts": len(free_ol_contact_rows),
            "free_ol_contacts": len(true_free_ol_rows),
            "reader_bound_ol_contacts": len(free_ol_contact_rows) - len(true_free_ol_rows),
            "new_pages_opened": 0,
            "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN",
        },
        "surface_dispatch": {
            row["surface"]: {
                "default_de": row["default_de"],
                "state_card": row["state_card"],
                "occurrences": row["occurrences"],
                "triple_reader_exact_occurrences": row["triple_reader_exact_occurrences"],
                "v57_positions_revised": row["v57_positions_revised"],
            }
            for row in surface_summary_rows
        },
        "context_modes": dict(sorted(context_counts.items())),
        "v58": {
            "lines": len(v58_rows),
            "positions": sum(int(row["token_count"]) for row in v58_rows),
            "lines_revised": len(patched_lines),
            "positions_revised": total_revisions,
            "action_positions": sum(int(row["action_positions"]) for row in v58_rows),
            "strict_card_debt_positions_after": int(debt_result["strict_card_debt_positions"]) - 8,
            "mechanical_visible_debt_union_positions_after": debt_result["mechanical_visible_debt"]["union_positions"],
            "mechanical_flag_memberships_after": int(debt_result["mechanical_visible_debt"]["class_memberships"]) - 8,
            "broad_specificity_open_positions_after": debt_result["broad_specificity_open_positions"],
            "four_layer_union_positions_after": debt_result["four_layer_union_with_low_confidence_positions"],
        },
        "decision": {
            "primary": "STATE_CELL_WITH_OUTER_OR_INHERITED_HEAD",
            "defaults_de": {"chol": "trocken", "shol": "feucht", "tol": "kalt"},
            "rejected_global": "Trockenansatz / Feuchtansatz / Kaltansatz",
            "allowed_local": "Ansatz only when a separate visible or inherited preparation head licenses it",
            "live_boundary_rival": "CHO_OR_SHO_PLUS_L_WOOD",
        },
        "claim_ceiling": (
            "All 540 already admitted exact ZL3b chol, shol and tol positions are assigned the single replaceable state defaults trocken, feucht and kalt, with visible or inherited head dispatch. The proposed universal Trockenansatz, Feuchtansatz and Kaltansatz nouns are rejected: all 540 source roles are QUALITY_STATE_CARRIER, 57 value realizations and seven visible part contacts use the forms as qualities, exact E+OL wholes carry the explicit drug head, and eight targets stand beside a genuinely free separately licensed ol while two further visible contacts are reader-bound compounds. V58 removes eight slash-separated generic Gut/Material cards from seven lines while retaining their honest object-head debt and all 86 action licenses. No ingredient, liquid, plant, disease, patient, cure, language, phonetics or historical codebook is identified; 64 target positions retain alternate-reader variants, the thermal orientation of tol remains a working default, and no new page or sealed material was opened."
        ),
        "files": {},
    }
    result["files"] = {name: sha256(output_dir / name) for name in artifact_names}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    build(ART)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
