#!/usr/bin/env python3
"""Build GDT686's exhaustive value-head census and V59 local dispatch."""

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
EXP = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch"
ART = EXP / "artifacts"

MINIM_PATH = ROOT / "experiments/yolo/gdt626_mobile_operation_lexicon/artifacts/MINIM_SUFFIX_OCCURRENCES.tsv"
HEAD_PATH = ROOT / "experiments/yolo/gdt627_value_head_role_atlas/artifacts/HEAD_ROLE_ATLAS.tsv"
PART_PATH = ROOT / "experiments/yolo/gdt627_value_head_role_atlas/artifacts/D_PART_CONTACTS.tsv"
QUALITY_PATH = ROOT / "experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_QUALITY_D_VALUE_PHRASES.tsv"
OR_PATH = ROOT / "experiments/yolo/gdt628_chol_measure_frame/artifacts/OR_CARRIER_D_VALUE_PHRASES.tsv"
VALUE_PATH = ROOT / "experiments/yolo/gdt630_outer_carrier_attachment/artifacts/VALUE_EXPRESSION_OCCURRENCES.tsv"
QOD_READER_PATH = ROOT / "experiments/yolo/gdt662_seventy_six_residual_family_completion/artifacts/READER_VARIANT_AUDIT.tsv"
QOD_DECISION_PATH = ROOT / "experiments/yolo/gdt662_seventy_six_residual_family_completion/artifacts/TARGET_DECISION_DECK.tsv"
GLOSSARY_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/V48_WORKING_TOKEN_GLOSSARY.tsv"
DEBT_PATH = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts/V57_479_POSITION_INFORMATION_AUDIT.tsv"
V58_PATH = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts/V58_51_LINE_READER.tsv"
V58_RESULT_PATH = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts/RESULT.json"
V58_DEBT_PATH = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts/V58_DEBT_SUMMARY.tsv"
PATCH_PATH = EXP / "src/V59_VALUE_PATCH_SPECS.tsv"

TARGETS = {
    "dain": {"head": "d", "value": 2, "roman": "II", "composition": "D+A+II"},
    "daiin": {"head": "d", "value": 3, "roman": "III", "composition": "D+A+III"},
    "qodaiin": {"head": "qod", "value": 3, "roman": "III", "composition": "QOD+A+III"},
}
NUMBER_WORD = {2: "zwei", 3: "drei"}
QUALITY_CUE = re.compile(r"(?:heiß|kalt|trocken|feucht|Grad)", re.IGNORECASE)
MATERIAL_CUE = re.compile(
    r"(?:Ansatz|Droge|Drogen|Material|Stoff|Teil|Blatt|Kraut|Wurzel|Frucht|Blüt|Kompositum|Portion|Rohstoff|Fraktion)",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        if not rows:
            raise AssertionError(f"cannot infer fields for empty table {path.name}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def line_context(row: dict[str, str]) -> tuple[list[str], str, str, str]:
    tokens = row["surface_line"].split()
    index = int(row["token_index"])
    if tokens[index - 1] != row["surface"]:
        raise AssertionError(f"token index mismatch at {row['locus']}#{index}")
    left = tokens[index - 2] if index > 1 else "<START>"
    right = tokens[index] if index < len(tokens) else "<END>"
    position = "FIRST" if index == 1 else "LAST" if index == len(tokens) else "MIDDLE"
    return tokens, left, right, position


def split_aligned_chunks(text: str, expected: int) -> tuple[list[str], str]:
    terminal = "." if text.endswith(".") else ""
    body = text[:-1] if terminal else text
    chunks = body.split(" · ")
    if len(chunks) != expected:
        raise AssertionError(f"aligned chunk mismatch: expected {expected}, got {len(chunks)}")
    return chunks, terminal


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_minims = read_tsv(MINIM_PATH)
    target_source = [row for row in all_minims if row["surface"] in TARGETS]
    if Counter(row["surface"] for row in target_source) != {"dain": 193, "daiin": 721, "qodaiin": 41}:
        raise AssertionError("target value family counts changed")
    if any(row["page"].lower().startswith("f84") for row in target_source):
        raise AssertionError("sealed page leaked into value census")

    target_by_key: dict[tuple[str, int], dict[str, str]] = {}
    context_by_key: dict[tuple[str, int], tuple[list[str], str, str, str]] = {}
    for row in target_source:
        key = (row["locus"], int(row["token_index"]))
        if key in target_by_key:
            raise AssertionError(f"duplicate target key {key}")
        target_by_key[key] = row
        context_by_key[key] = line_context(row)
    if len(target_by_key) != 955:
        raise AssertionError("expected 955 unique value targets")

    quality_rows = [
        row for row in read_tsv(QUALITY_PATH) if row["d_value_surface"] in {"dain", "daiin"}
    ]
    quality_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in quality_rows:
        key = (row["locus"], int(row["token_index"]) + 1)
        if key not in target_by_key or target_by_key[key]["surface"] != row["d_value_surface"]:
            raise AssertionError(f"quality phrase does not hit target {key}")
        quality_by_key[key] = row
    if len(quality_by_key) != 75:
        raise AssertionError(f"expected 75 direct quality frames, got {len(quality_by_key)}")

    or_rows = [row for row in read_tsv(OR_PATH) if row["d_value_surface"] in {"dain", "daiin"}]
    or_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in or_rows:
        key = (row["locus"], int(row["token_index"]) + 1)
        if key not in target_by_key or target_by_key[key]["surface"] != row["d_value_surface"]:
            raise AssertionError(f"OR phrase does not hit target {key}")
        or_by_key[key] = row
    if len(or_by_key) != 25:
        raise AssertionError(f"expected 25 target OR frames, got {len(or_by_key)}")

    part_rows = [row for row in read_tsv(PART_PATH) if row["d_surface"] in {"dain", "daiin"}]
    part_by_key: dict[tuple[str, int], dict[str, str]] = {}
    candidates_by_locus_surface: dict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)
    for key, row in target_by_key.items():
        if row["surface"] in {"dain", "daiin"}:
            candidates_by_locus_surface[(row["locus"], row["surface"])].append(key)
    for row in part_rows:
        candidates = []
        for key in candidates_by_locus_surface[(row["locus"], row["d_surface"])]:
            _, left, right, _ = context_by_key[key]
            if left == row["left_surface"] and right == row["right_surface"]:
                candidates.append(key)
        if len(candidates) != 1:
            raise AssertionError(f"part contact key ambiguity {row['contact_id']}: {candidates}")
        part_by_key[candidates[0]] = row
    if len(part_by_key) != 46:
        raise AssertionError(f"expected 46 target part contacts, got {len(part_by_key)}")

    bare_rows = [
        row for row in read_tsv(VALUE_PATH)
        if row["realization_mode"] == "SEPARATE_D_VALUE"
        and row["base_surface"] == "ol"
        and row["surface_expression"].split()[-1] in {"dain", "daiin"}
    ]
    bare_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in bare_rows:
        key = (row["locus"], int(row["token_index_end"]))
        if key not in target_by_key:
            raise AssertionError(f"bare OL phrase does not hit target {key}")
        bare_by_key[key] = row
    if len(bare_by_key) != 11:
        raise AssertionError(f"expected 11 naked-OL target frames, got {len(bare_by_key)}")

    quality_keys = set(quality_by_key)
    amount_keys = (set(or_by_key) | set(part_by_key)) - quality_keys
    bare_keys = set(bare_by_key) - quality_keys - amount_keys
    d_keys = {key for key, row in target_by_key.items() if row["surface"] in {"dain", "daiin"}}
    open_d_keys = d_keys - quality_keys - amount_keys - bare_keys
    if (len(quality_keys), len(amount_keys), len(bare_keys), len(open_d_keys)) != (75, 53, 11, 775):
        raise AssertionError(
            f"direct axis partition changed: {len(quality_keys)}, {len(amount_keys)}, {len(bare_keys)}, {len(open_d_keys)}"
        )

    glossary = {row["surface"]: row["working_meaning_de"] for row in read_tsv(GLOSSARY_PATH)}
    qod_decisions = [row for row in read_tsv(QOD_DECISION_PATH) if row["surface"] == "qodaiin"]
    if len(qod_decisions) != 1 or qod_decisions[0]["occurrences"] != "41":
        raise AssertionError("published qodaiin decision row changed")
    qod_reader_rows = [row for row in read_tsv(QOD_READER_PATH) if row["surface"] == "qodaiin"]
    if len(qod_reader_rows) != 41:
        raise AssertionError("expected 41 qodaiin reader rows")
    qod_reader_by_key = {(row["locus"], int(row["ordinal"])): row for row in qod_reader_rows}
    if len(qod_reader_by_key) != 41:
        raise AssertionError("qodaiin reader keys are not unique")

    qod_audit_rows: list[dict[str, object]] = []
    for key in sorted(qod_reader_by_key):
        source = target_by_key[key]
        _, left, right, position = context_by_key[key]
        reader = qod_reader_by_key[key]
        left_gloss = glossary.get(left, "OPEN")
        right_gloss = glossary.get(right, "OPEN")
        cue_text = f"{left_gloss} | {right_gloss}"
        has_quality = bool(QUALITY_CUE.search(cue_text))
        has_material = bool(MATERIAL_CUE.search(cue_text))
        if has_quality and not has_material:
            local_rival = "QUALITY_GRADE_III"
        elif has_material and not has_quality:
            local_rival = "LOCAL_AMOUNT_III"
        elif has_quality and has_material:
            local_rival = "GRADE_OR_AMOUNT_CONTEXT_RIVAL"
        else:
            local_rival = "NO_TYPED_NEIGHBOUR"
        boundary = (
            "RF1B_QOD_AIIN_SPLIT" if key == ("f86v3.25", 1)
            else "RF1B_QO_DAIIN_SPLIT" if key == ("f95r2.1", 5)
            else "TRIPLE_READER_EXACT" if reader["reader_exact"] == "1"
            else "SPLIT_NORMALIZED_VARIANT" if reader["split_normalized"] == "1"
            else "ALTERNATE_READER_VARIANT"
        )
        qod_audit_rows.append({
            "occurrence_id": source["occurrence_id"],
            "page": source["page"],
            "locus": source["locus"],
            "token_index": source["token_index"],
            "line_position": position,
            "left_surface": left,
            "left_gloss_de": left_gloss,
            "right_surface": right,
            "right_gloss_de": right_gloss,
            "quality_cue": int(has_quality),
            "material_or_part_cue": int(has_material),
            "local_axis_rival": local_rival,
            "global_dispatch": "QOD_VALUE_III__HEAD_AND_AXIS_OPEN",
            "reader_boundary": boundary,
            "reader_exact": reader["reader_exact"],
            "split_normalized": reader["split_normalized"],
            "zl3b_line": reader["zl3b_line"],
            "it2a_line": reader["it2a_line"],
            "rf1b_line": reader["rf1b_line"],
        })

    census_rows: list[dict[str, object]] = []
    for serial, key in enumerate(sorted(target_by_key, key=lambda item: (target_by_key[item]["surface"], item[0], item[1])), 1):
        source = target_by_key[key]
        target = TARGETS[source["surface"]]
        _, left, right, position = context_by_key[key]
        evidence_id = "NONE"
        head_surface = "NONE"
        head_gloss = "NONE"
        if source["surface"] == "qodaiin":
            mode = "QOD_HEAD_AXIS_OPEN"
            axis = "OPEN"
            renderer = "dritte qod-Wertstufe; qod-Kopf und Achse lokal bestimmen"
            evidence_source = str(QOD_DECISION_PATH.relative_to(ROOT))
        elif key in quality_by_key:
            phrase = quality_by_key[key]
            mode = "DIRECT_QUALITY_GRADE"
            axis = "GRADE"
            head_surface = phrase["carrier_surface"]
            head_gloss = phrase["working_reading_de"]
            renderer = phrase["working_reading_de"]
            evidence_id = phrase["phrase_id"]
            evidence_source = str(QUALITY_PATH.relative_to(ROOT))
        elif key in amount_keys:
            mode = "DIRECT_PART_OR_MATERIAL_AMOUNT"
            axis = "AMOUNT"
            amount = NUMBER_WORD[int(target["value"])]
            if key in or_by_key:
                phrase = or_by_key[key]
                head_surface = phrase["carrier_surface"]
                head_gloss = phrase["working_reading_de"]
                evidence_id = phrase["phrase_id"]
                evidence_source = str(OR_PATH.relative_to(ROOT))
            else:
                contact = part_by_key[key]
                head_surface = contact["left_surface"] if contact["direction"] == "PART_THEN_D" else contact["right_surface"]
                head_gloss = contact["working_local_de"]
                evidence_id = contact["contact_id"]
                evidence_source = str(PART_PATH.relative_to(ROOT))
            renderer = f"{amount} lokale Portionen/Maße; Kopf {head_surface}; absolute Einheit offen"
        elif key in bare_by_key:
            phrase = bare_by_key[key]
            mode = "BARE_OL_VALUE_AXIS_OPEN"
            axis = "OPEN"
            head_surface = "ol"
            head_gloss = phrase["working_reading_de"]
            renderer = f"{target['roman']}. Wertstufe des OL-Trägers; Sachachse offen"
            evidence_id = phrase["expression_id"]
            evidence_source = str(VALUE_PATH.relative_to(ROOT))
        else:
            mode = "D_VALUE_OUTER_HEAD_OPEN"
            axis = "OPEN"
            renderer = f"{target['roman']}. Wertstufe des laufenden Postens; äußerer Kopf bestimmt Grad, Menge oder Klasse"
            evidence_source = str(HEAD_PATH.relative_to(ROOT))

        census_rows.append({
            "case_id": f"G686-V{serial:04d}",
            "occurrence_id": source["occurrence_id"],
            "surface": source["surface"],
            "composition": target["composition"],
            "head": target["head"],
            "working_value": target["value"],
            "working_roman": target["roman"],
            "page": source["page"],
            "locus": source["locus"],
            "token_index": source["token_index"],
            "section": source["section"],
            "hand": source["hand"],
            "line_position": position,
            "triple_reader_token_stable": source["triple_reading_token_stable"],
            "global_context_mode": mode,
            "global_axis": axis,
            "contextual_renderer_de": renderer,
            "visible_head_surface": head_surface,
            "visible_head_gloss_de": head_gloss,
            "evidence_id": evidence_id,
            "evidence_source": evidence_source,
            "left_surface": left,
            "left_gloss_de": glossary.get(left, "OPEN"),
            "right_surface": right,
            "right_gloss_de": glossary.get(right, "OPEN"),
            "decision": "VALUE_LEVEL_FIXED__AXIS_BY_VISIBLE_OR_KEYED_HEAD",
            "surface_line": source["surface_line"],
        })

    mode_counts = Counter(row["global_context_mode"] for row in census_rows)
    expected_modes = {
        "DIRECT_QUALITY_GRADE": 75,
        "DIRECT_PART_OR_MATERIAL_AMOUNT": 53,
        "BARE_OL_VALUE_AXIS_OPEN": 11,
        "D_VALUE_OUTER_HEAD_OPEN": 775,
        "QOD_HEAD_AXIS_OPEN": 41,
    }
    if mode_counts != expected_modes:
        raise AssertionError(f"unexpected context modes {mode_counts}")

    surface_summary_rows: list[dict[str, object]] = []
    for surface in ("dain", "daiin", "qodaiin"):
        members = [row for row in census_rows if row["surface"] == surface]
        surface_summary_rows.append({
            "surface": surface,
            "composition": TARGETS[surface]["composition"],
            "portable_default_de": (
                f"d-Wertzelle {TARGETS[surface]['roman']}; Achse durch sichtbaren Kopf"
                if surface != "qodaiin" else "qod-Wertzelle III; qod-Kopf und Achse offen"
            ),
            "occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "loci": len({row["locus"] for row in members}),
            "triple_reader_exact_occurrences": sum(int(row["triple_reader_token_stable"]) for row in members),
            "line_first": sum(row["line_position"] == "FIRST" for row in members),
            "line_middle": sum(row["line_position"] == "MIDDLE" for row in members),
            "line_last": sum(row["line_position"] == "LAST" for row in members),
            "direct_quality_grade": sum(row["global_context_mode"] == "DIRECT_QUALITY_GRADE" for row in members),
            "direct_part_or_material_amount": sum(row["global_context_mode"] == "DIRECT_PART_OR_MATERIAL_AMOUNT" for row in members),
            "bare_ol_axis_open": sum(row["global_context_mode"] == "BARE_OL_VALUE_AXIS_OPEN" for row in members),
            "outer_or_qod_head_open": sum(row["global_context_mode"] in {"D_VALUE_OUTER_HEAD_OPEN", "QOD_HEAD_AXIS_OPEN"} for row in members),
        })

    head_rows = {row["head"]: row for row in read_tsv(HEAD_PATH)}
    da_head = head_rows["da"]
    qoda_head = head_rows["qoda"]
    if (da_head["count_I"], da_head["count_II"], da_head["count_III"], da_head["count_IV"]) != ("17", "193", "721", "17"):
        raise AssertionError("da four-cell family changed")
    if (qoda_head["count_I"], qoda_head["count_II"], qoda_head["count_III"], qoda_head["count_IV"]) != ("0", "10", "41", "1"):
        raise AssertionError("qoda family changed")

    axis_summary_rows = []
    for mode in expected_modes:
        members = [row for row in census_rows if row["global_context_mode"] == mode]
        axis_summary_rows.append({
            "context_mode": mode,
            "positions": len(members),
            "triple_reader_exact_positions": sum(int(row["triple_reader_token_stable"]) for row in members),
            "surfaces": "|".join(sorted({str(row["surface"]) for row in members})),
            "axis": "GRADE" if mode == "DIRECT_QUALITY_GRADE" else "AMOUNT" if mode == "DIRECT_PART_OR_MATERIAL_AMOUNT" else "OPEN",
            "renderer_policy": (
                "quality-bearing OL head selects degree"
                if mode == "DIRECT_QUALITY_GRADE"
                else "visible part/material/OR carrier selects local amount; unit stays unnamed"
                if mode == "DIRECT_PART_OR_MATERIAL_AMOUNT"
                else "naked OL supplies a carrier but not the value dimension"
                if mode == "BARE_OL_VALUE_AXIS_OPEN"
                else "qod value level composes but qod head has no global semantic axis"
                if mode == "QOD_HEAD_AXIS_OPEN"
                else "retain ordered value level and wait for an outer or keyed head"
            ),
        })

    patch_specs = read_tsv(PATCH_PATH)
    if len(patch_specs) != 11:
        raise AssertionError("expected eleven V59 patch specs")
    spec_by_key = {(row["locus"], int(row["ordinal"])): row for row in patch_specs}
    if len(spec_by_key) != 11:
        raise AssertionError("V59 patch keys are not unique")
    if Counter(row["axis"] for row in patch_specs) != {"GRADE": 4, "AMOUNT": 7}:
        raise AssertionError("V59 must contain four grade and seven amount defaults")

    v58_rows = read_tsv(V58_PATH)
    v59_rows: list[dict[str, object]] = []
    patched_lines: list[dict[str, object]] = []
    used_specs: set[tuple[str, int]] = set()
    for source in v58_rows:
        tokens = source["zl3b_line"].split()
        old_literals = source["literal_token_glosses_de"].split(" | ")
        old_aligned, terminal = split_aligned_chunks(source["aligned_line_de"], len(tokens))
        if len(tokens) != len(old_literals):
            raise AssertionError(f"V58 literal alignment mismatch at {source['locus']}")
        new_literals = list(old_literals)
        new_aligned = list(old_aligned)
        line_specs = sorted(
            (spec for key, spec in spec_by_key.items() if key[0] == source["locus"]),
            key=lambda item: int(item["ordinal"]),
        )
        dispatches = []
        for spec in line_specs:
            ordinal = int(spec["ordinal"])
            key = (source["locus"], ordinal)
            if tokens[ordinal - 1] != spec["surface"]:
                raise AssertionError(f"V59 spec surface mismatch at {key}")
            if key not in target_by_key:
                raise AssertionError(f"V59 spec absent from global census {key}")
            new_literals[ordinal - 1] = spec["new_literal_gloss_de"]
            new_aligned[ordinal - 1] = spec["new_aligned_chunk_de"]
            dispatches.append(
                f"{spec['surface']}#{ordinal}={spec['axis']}:{spec['bind_direction']}:{spec['head_surface']}"
            )
            used_specs.add(key)
        row: dict[str, object] = dict(source)
        row["literal_token_glosses_de"] = " | ".join(new_literals)
        row["aligned_line_de"] = " · ".join(new_aligned) + terminal
        if line_specs:
            practical_values = {spec["practical_translation_de"] for spec in line_specs}
            if len(practical_values) != 1:
                raise AssertionError(f"conflicting V59 prose at {source['locus']}")
            row["practical_translation_de"] = practical_values.pop()
            row["review_note"] = source["review_note"] + " GDT686: " + " | ".join(dispatches)
            row["v59_value_dispatch"] = " | ".join(dispatches)
            row["v59_patch_basis"] = " | ".join(spec["rationale"] for spec in line_specs)
            row["v59_value_confidence"] = "|".join(spec["confidence"] for spec in line_specs)
        else:
            row["v59_value_dispatch"] = "NONE"
            row["v59_patch_basis"] = "NONE"
            row["v59_value_confidence"] = "NONE"
        row["v59_semantic_revisions"] = len(line_specs)
        row["v59_target_surfaces"] = "|".join(spec["surface"] for spec in line_specs) if line_specs else "NONE"
        v59_rows.append(row)
        if line_specs:
            patched_lines.append({
                "page": source["page"],
                "locus": source["locus"],
                "target_surfaces": "|".join(spec["surface"] for spec in line_specs),
                "revisions": len(line_specs),
                "axes": "|".join(spec["axis"] for spec in line_specs),
                "old_literal_token_glosses_de": source["literal_token_glosses_de"],
                "new_literal_token_glosses_de": row["literal_token_glosses_de"],
                "old_aligned_line_de": source["aligned_line_de"],
                "new_aligned_line_de": row["aligned_line_de"],
                "old_practical_translation_de": source["practical_translation_de"],
                "new_practical_translation_de": row["practical_translation_de"],
                "local_dispatch": row["v59_value_dispatch"],
                "confidence": row["v59_value_confidence"],
            })
    if used_specs != set(spec_by_key):
        raise AssertionError("not all V59 specs were applied")
    if len(v59_rows) != 51 or len(patched_lines) != 10:
        raise AssertionError("V59 line inventory must be 51 total / 10 patched")
    if sum(int(row["v59_semantic_revisions"]) for row in v59_rows) != 11:
        raise AssertionError("V59 must revise eleven positions")

    debt_rows = read_tsv(DEBT_PATH)
    debt_by_key = {(row["locus"], int(row["ordinal"])): row for row in debt_rows}
    debt_delta_rows: list[dict[str, object]] = []
    for key in sorted(spec_by_key):
        spec = spec_by_key[key]
        old = debt_by_key[key]
        if old["surface"] != spec["surface"] or old["strict_card_debt"] != "1":
            raise AssertionError(f"unexpected inherited debt at {key}")
        debt_delta_rows.append({
            "page": old["page"],
            "locus": old["locus"],
            "ordinal": old["ordinal"],
            "surface": old["surface"],
            "old_literal_gloss_de": old["literal_gloss_de"],
            "new_literal_gloss_de": spec["new_literal_gloss_de"],
            "new_axis": spec["axis"],
            "bind_direction": spec["bind_direction"],
            "head_surface": spec["head_surface"],
            "confidence": spec["confidence"],
            "old_primary_class": old["primary_class"],
            "new_primary_class": "A3_BOUND_QUALITY_GRADE" if spec["axis"] == "GRADE" else "A4_BOUND_LOCAL_AMOUNT",
            "old_debt_severity": old["debt_severity"],
            "new_debt_severity": "NONE",
            "old_strict_card_debt": old["strict_card_debt"],
            "new_strict_card_debt": 0,
            "old_mechanical_debt": old["mechanical_debt"],
            "new_mechanical_debt": 0,
            "old_mechanical_debt_flags": old["mechanical_debt_flags"],
            "new_mechanical_debt_flags": "NONE",
            "old_specificity_open": old["specificity_open"],
            "new_specificity_open": 0,
            "information_gain": f"value level {spec['value_roman']} bound as {spec['axis']} to {spec['head_surface']}",
            "live_rival_de": spec["live_rival_de"],
            "remaining_caveat": "local exploratory dispatch; exact historical unit or quality name remains replaceable",
        })
    if Counter(row["old_mechanical_debt"] for row in debt_delta_rows) != {"1": 9, "0": 2}:
        raise AssertionError("expected nine old slash debts and two single-value cards")

    v58_result = json.loads(V58_RESULT_PATH.read_text(encoding="utf-8"))
    v58_debt = {row["metric"]: row for row in read_tsv(V58_DEBT_PATH)}
    debt_before = {
        "strict": int(v58_result["v58"]["strict_card_debt_positions_after"]),
        "mechanical_union": int(v58_result["v58"]["mechanical_visible_debt_union_positions_after"]),
        "memberships": int(v58_result["v58"]["mechanical_flag_memberships_after"]),
        "broad": int(v58_result["v58"]["broad_specificity_open_positions_after"]),
        "four": int(v58_result["v58"]["four_layer_union_positions_after"]),
    }
    debt_after = {
        "strict": debt_before["strict"] - 11,
        "mechanical_union": debt_before["mechanical_union"] - 9,
        "memberships": debt_before["memberships"] - 9,
        "broad": debt_before["broad"] - 11,
        "four": debt_before["four"] - 11,
    }
    debt_summary_rows = [
        {"metric": "strict_card_debt_positions", "v58_before": debt_before["strict"], "v59_after": debt_after["strict"], "delta": -11, "interpretation": "all eleven current value positions receive one keyed local axis"},
        {"metric": "mechanical_visible_debt_union_positions", "v58_before": debt_before["mechanical_union"], "v59_after": debt_after["mechanical_union"], "delta": -9, "interpretation": "nine slash-separated Grad/Maß cards become single local defaults"},
        {"metric": "mechanical_flag_memberships", "v58_before": debt_before["memberships"], "v59_after": debt_after["memberships"], "delta": -9, "interpretation": "no new mechanical class is introduced"},
        {"metric": "broad_specificity_open_positions", "v58_before": debt_before["broad"], "v59_after": debt_after["broad"], "delta": -11, "interpretation": "value level, axis, direction and local head are all explicit in V59"},
        {"metric": "four_layer_union_with_low_confidence_positions", "v58_before": debt_before["four"], "v59_after": debt_after["four"], "delta": -11, "interpretation": "the keyed working defaults remain replaceable but no longer semantically empty"},
    ]
    for flag in ("OPEN_COMPOSITION", "NON_SINGLE_GLOSS", "STRUCTURAL_META_AS_VALUE", "HARD_GENERIC_CARRIER", "STATE_ONLY_NO_OBJECT"):
        before = int(v58_debt[f"mechanical_class:{flag}"]["v58_after"])
        after = before - 9 if flag == "NON_SINGLE_GLOSS" else before
        debt_summary_rows.append({
            "metric": f"mechanical_class:{flag}",
            "v58_before": before,
            "v59_after": after,
            "delta": after - before,
            "interpretation": "class-level literal renderer count",
        })

    evidence_rows = [
        {
            "evidence_id": "G686-E01",
            "evidence": "bare d four-cell family",
            "observed": "dan/dain/daiin/daiiin = 17/193/721/17; 27 fixed multi-value frames and 49 mixed-value lines",
            "consequence": "d words encode an ordered value level, not an invariant operation or connective",
            "source": str(HEAD_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G686-E02",
            "evidence": "direct core-bearing OL quality heads",
            "observed": "75 dain/daiin positions; 60 expression-level reader exact",
            "consequence": "a visible quality carrier selects degree II or III",
            "source": str(QUALITY_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G686-E03",
            "evidence": "visible OR and part heads",
            "observed": "53 non-quality dain/daiin positions after target-level overlap removal",
            "consequence": "a visible material or part carrier supports local amount/portion as primary",
            "source": f"{OR_PATH.relative_to(ROOT)} | {PART_PATH.relative_to(ROOT)}",
        },
        {
            "evidence_id": "G686-E04",
            "evidence": "naked OL frames",
            "observed": "11 separated ol dain/daiin expressions",
            "consequence": "a carrier alone does not identify degree, amount or class",
            "source": str(VALUE_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G686-E05",
            "evidence": "qod value family",
            "observed": "qodain/qodaiin/qodaiiin = 10/41/1; no qodan, fixed multi-value frame or mixed-value line",
            "consequence": "qodaiin keeps level III but qod and its axis remain globally open",
            "source": str(HEAD_PATH.relative_to(ROOT)),
        },
        {
            "evidence_id": "G686-E06",
            "evidence": "same-span qodaiin boundary rivals",
            "observed": "f86v3.25 qodaiin versus qod aiin; f95r2.1 qodaiin versus qo daiin",
            "consequence": "whole-word dispatch is safe but neither internal segmentation may export a universal gloss",
            "source": str(QOD_READER_PATH.relative_to(ROOT)),
        },
    ]

    hypothesis_rows = [
        {"rank": 1, "hypothesis": "ORDERED_VALUE_LEVEL_PLUS_VISIBLE_OR_KEYED_HEAD", "coverage": 955, "default": "II/III fixed; axis selected locally", "strength": "four-cell d family plus 139 direct d-head contexts and two qod boundary rivals", "weakness": "775 d positions and all 41 qod positions lack a globally typed immediate head", "disposition": "PRIMARY"},
        {"rank": 2, "hypothesis": "UNIVERSAL_QUALITY_DEGREE", "coverage": 955, "default": "Grad II/III", "strength": "75 direct OL-quality frames and many quality neighbours", "weakness": "visible part/OR frames, quantity lists and untyped value runs", "disposition": "REJECT_GLOBAL__ALLOW_LOCAL"},
        {"rank": 3, "hypothesis": "UNIVERSAL_CARDINAL_AMOUNT", "coverage": 955, "default": "zwei/drei Portionen", "strength": "53 direct part/material frames and recipe-list analogy", "weakness": "complete hot/cold/dry/moist degree paradigms and right-position quality clauses", "disposition": "REJECT_GLOBAL__ALLOW_LOCAL"},
        {"rank": 4, "hypothesis": "QO_PLUS_FREE_D_VALUE", "coverage": 41, "default": "qo + d-Wert III", "strength": "same-span qo daiin split at f95r2.1", "weakness": "qod aiin split at f86v3.25 and no license to export free qo action semantics", "disposition": "LOCAL_BOUNDARY_RIVAL"},
        {"rank": 5, "hypothesis": "THREE_LEARNED_WHOLE_WORDS", "coverage": 955, "default": "memorized dain/daiin/qodaiin", "strength": "fits exact surfaces", "weakness": "fails to predict four value rungs and head-conditioned axis changes", "disposition": "POSSIBLE_BUT_UNECONOMICAL"},
    ]

    counterexample_rows = [
        {"counterexample": "MIXED_D_VALUE_RUN", "example": "f38v.6 daiin daiiin dain dain", "blocks": "a universal axis or invisible repeated noun", "surviving_rule": "preserve four ordered cells; head outside visible run"},
        {"counterexample": "ONE_LINE_PART_AND_QUALITY", "example": "f42v.2 dan dain otol daiin", "blocks": "surface-only d gloss", "surviving_rule": "only otol daiin has a directly written quality head"},
        {"counterexample": "QOD_DOUBLE_VALUE", "example": "f104r.4 qodaiin qodaiin", "blocks": "automatic single hidden quality or portion head", "surviving_rule": "two separate qod level-III cells"},
        {"counterexample": "QOD_BOUNDARY_RIVALS", "example": "f86v3.25 qod|aiin; f95r2.1 qo|daiin", "blocks": "one proven internal segmentation", "surviving_rule": "exact qodaiin dispatch plus locally open boundary"},
        {"counterexample": "V58_OPERATION_DRIFT", "example": "f10r.2 and f8r.15", "blocks": "value token licensing abnehmen", "surviving_rule": "value supplies level/axis only; verbs require their own token"},
    ]

    write_tsv(output_dir / "TARGET_955_VALUE_HEAD_CENSUS.tsv", census_rows)
    write_tsv(output_dir / "SURFACE_VALUE_DISPATCH_SUMMARY.tsv", surface_summary_rows)
    write_tsv(output_dir / "DIRECT_AXIS_EVIDENCE_SUMMARY.tsv", axis_summary_rows)
    write_tsv(output_dir / "QODAIIN_41_CONTEXT_AUDIT.tsv", qod_audit_rows)
    write_tsv(output_dir / "COMPOSITION_EVIDENCE.tsv", evidence_rows)
    write_tsv(output_dir / "HYPOTHESIS_COMPARISON.tsv", hypothesis_rows)
    write_tsv(output_dir / "COUNTEREXAMPLE_AUDIT.tsv", counterexample_rows)
    write_tsv(output_dir / "V59_51_LINE_READER.tsv", v59_rows)
    write_tsv(output_dir / "V59_PATCHED_LINES.tsv", patched_lines)
    write_tsv(output_dir / "V59_TARGET_POSITION_DEBT_DELTA.tsv", debt_delta_rows)
    write_tsv(output_dir / "V59_DEBT_SUMMARY.tsv", debt_summary_rows)

    reader_lines = [
        "# GDT686 — V59 local value-head reader",
        "",
        "Portable rule: `dain = d-value II`, `daiin = d-value III`, `qodaiin = qod-value III`.",
        "The visible or keyed local head selects degree, amount or class; the value token never supplies an operation.",
        "",
        "## Ten revised lines",
        "",
    ]
    for row in patched_lines:
        reader_lines.extend([
            f"### {row['locus']}",
            "",
            str(row["new_practical_translation_de"]),
            "",
            f"Dispatch: `{row['local_dispatch']}`",
            f"Confidence: `{row['confidence']}`",
            "",
        ])
    (output_dir / "GDT686_V59_LOCAL_VALUE_READER.md").write_text("\n".join(reader_lines), encoding="utf-8")

    generated = [
        "TARGET_955_VALUE_HEAD_CENSUS.tsv",
        "SURFACE_VALUE_DISPATCH_SUMMARY.tsv",
        "DIRECT_AXIS_EVIDENCE_SUMMARY.tsv",
        "QODAIIN_41_CONTEXT_AUDIT.tsv",
        "COMPOSITION_EVIDENCE.tsv",
        "HYPOTHESIS_COMPARISON.tsv",
        "COUNTEREXAMPLE_AUDIT.tsv",
        "V59_51_LINE_READER.tsv",
        "V59_PATCHED_LINES.tsv",
        "V59_TARGET_POSITION_DEBT_DELTA.tsv",
        "V59_DEBT_SUMMARY.tsv",
        "GDT686_V59_LOCAL_VALUE_READER.md",
    ]
    result = {
        "status": "PASS_955_VALUE_HEAD_CENSUS__REJECT_UNIVERSAL_AXIS__V59_FOUR_GRADES_SEVEN_AMOUNTS",
        "basis": {
            "target_occurrences": 955,
            "target_pages_union": len({row["page"] for row in census_rows}),
            "target_loci_union": len({row["locus"] for row in census_rows}),
            "triple_reader_exact_occurrences": sum(int(row["triple_reader_token_stable"]) for row in census_rows),
            "d_head_occurrences": len(d_keys),
            "qod_head_occurrences": 41,
            "direct_quality_grade_positions": len(quality_keys),
            "direct_part_or_material_amount_positions": len(amount_keys),
            "bare_ol_axis_open_positions": len(bare_keys),
            "d_outer_head_open_positions": len(open_d_keys),
            "qod_head_axis_open_positions": 41,
            "qod_reader_exact_positions": sum(int(row["reader_exact"]) for row in qod_audit_rows),
            "qod_split_normalized_positions": sum(int(row["split_normalized"]) for row in qod_audit_rows),
            "new_pages_opened": 0,
            "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN",
        },
        "portable_dictionary": {
            "dain": "d-Wertzelle II; Achse durch sichtbaren Kopf",
            "daiin": "d-Wertzelle III; Achse durch sichtbaren Kopf",
            "qodaiin": "qod-Wertzelle III; qod-Kopf und Achse global offen",
        },
        "direct_axis_partition": dict(sorted(mode_counts.items())),
        "v59": {
            "lines": 51,
            "positions": 479,
            "lines_revised": 10,
            "positions_revised": 11,
            "grade_bindings": 4,
            "amount_bindings": 7,
            "action_positions": sum(int(row["action_positions"]) for row in v59_rows),
            "strict_card_debt_positions_after": debt_after["strict"],
            "mechanical_visible_debt_union_positions_after": debt_after["mechanical_union"],
            "mechanical_flag_memberships_after": debt_after["memberships"],
            "broad_specificity_open_positions_after": debt_after["broad"],
            "four_layer_union_positions_after": debt_after["four"],
            "positions_without_current_debt_or_confidence_flag": 479 - debt_after["four"],
        },
        "claim_ceiling": "The ordered II/III value levels are portable; their semantic axis is not. All 955 already admitted exact dain, daiin and qodaiin positions receive a structural value-level dispatch, while only visible or keyed local heads select degree, amount or another axis. V59 makes eleven exploratory local choices—four grades and seven amounts—so every current target has one practical default and no value token invents an operation. These local choices remain replaceable, qod is globally open, no absolute historical unit or quality name is identified, and no ingredient, liquid, plant, disease, patient, cure, language, phonetics, codebook, new page or sealed material is claimed.",
        "files": {name: sha256(output_dir / name) for name in generated},
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = build(ART)
    print(json.dumps({
        "status": result["status"],
        "target_occurrences": result["basis"]["target_occurrences"],
        "triple_reader_exact_occurrences": result["basis"]["triple_reader_exact_occurrences"],
        "direct_quality_grade_positions": result["basis"]["direct_quality_grade_positions"],
        "direct_part_or_material_amount_positions": result["basis"]["direct_part_or_material_amount_positions"],
        "v59_positions_revised": result["v59"]["positions_revised"],
        "strict_debt_positions_after": result["v59"]["strict_card_debt_positions_after"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
