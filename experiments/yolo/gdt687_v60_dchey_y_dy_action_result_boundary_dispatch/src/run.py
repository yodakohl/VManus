#!/usr/bin/env python3
"""Build GDT687/V60 from already published, f84-free reader artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch"
ART = BASE / "artifacts"

V59_READER = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/artifacts/V59_51_LINE_READER.tsv"
V59_RESULT = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/artifacts/RESULT.json"
V57_AUDIT = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts/V57_479_POSITION_INFORMATION_AUDIT.tsv"
DCHEY_CONTEXTS = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/EXACT_OCCURRENCE_CONTEXTS.tsv"
Y_CENSUS = ROOT / "experiments/yolo/gdt659_naked_y_local_reference/artifacts/Y_OCCURRENCE_CENSUS.tsv"
Y_CLASS_SUMMARY = ROOT / "experiments/yolo/gdt659_naked_y_local_reference/artifacts/Y_CONTEXT_CLASS_SUMMARY.tsv"
DY_POSITION_SUMMARY = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts/gdt557_marker_position_summary.tsv"
Y_DY_CLASSES = ROOT / "experiments/yolo/gdt559_argument_carrier_substitution_grammar/artifacts/gdt559_4_y_dy_distinction_classes.tsv"
Y_DY_JOINT = ROOT / "experiments/yolo/gdt559_argument_carrier_substitution_grammar/artifacts/gdt559_28_y_dy_joint_cards.tsv"

TARGET_SPECS = BASE / "src/V60_TARGET_DISPATCH_SPECS.tsv"
BOUND_DY_SPECS = BASE / "src/V60_BOUND_DY_SURFACE_SPECS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_set(value: str) -> set[int]:
    return {int(item) for item in value.split("|") if item and item != "NONE"}


def split_flags(value: str) -> list[str]:
    return [] if value == "NONE" else value.split("|")


def target_family(surface: str) -> str | None:
    if surface == "dchey":
        return "DCHEY"
    if surface == "y":
        return "NAKED_Y"
    if surface == "dy":
        return "FREE_DY"
    if "dy" in surface:
        return "BOUND_DY"
    return None


def aligned_reading(glosses: list[str]) -> str:
    chunks: list[str] = []
    for gloss in glosses:
        if gloss in {";", "."}:
            if chunks:
                chunks[-1] = chunks[-1].rstrip(".;") + gloss
            else:
                chunks.append(gloss)
        else:
            chunks.append(gloss)
    text = " · ".join(chunks)
    if text and not text.endswith((".", ";")):
        text += "."
    return text


def strict_practical_reading(glosses: list[str]) -> str:
    """Render only written token meanings; punctuation targets add no spoken verb."""
    text = ""
    for gloss in glosses:
        if gloss == ";":
            text = text.rstrip(" ,;.") + ";"
        elif gloss == ".":
            text = text.rstrip(" ,;.") + "."
        elif not text:
            text = gloss
        elif text.endswith((";", ".", ":")):
            text += " " + gloss
        else:
            text += "; " + gloss
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:]


def unique_by(rows: list[dict[str, str]], keys: tuple[str, ...], label: str) -> dict[tuple[str, ...], dict[str, str]]:
    out: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        key = tuple(row[name] for name in keys)
        if key in out:
            raise AssertionError(f"duplicate {label}: {key}")
        out[key] = row
    return out


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    v59_rows = read_tsv(V59_READER)
    assert len(v59_rows) == 51
    assert sum(int(row["token_count"]) for row in v59_rows) == 479

    explicit_specs = unique_by(read_tsv(TARGET_SPECS), ("locus", "ordinal"), "target spec")
    bound_specs = {row["surface"]: row for row in read_tsv(BOUND_DY_SPECS)}
    assert len(bound_specs) == 60
    v57_audit = unique_by(read_tsv(V57_AUDIT), ("locus", "ordinal"), "V57 audit row")
    y_census = unique_by(read_tsv(Y_CENSUS), ("locus", "ordinal"), "naked-y occurrence")

    dchey_source_rows = [row for row in read_tsv(DCHEY_CONTEXTS) if row["surface"] == "dchey"]
    dchey_source = unique_by(dchey_source_rows, ("locus", "ordinal"), "dchey occurrence")
    assert len(dchey_source) == 15

    targets: list[dict[str, object]] = []
    targets_by_line: dict[str, list[dict[str, object]]] = defaultdict(list)
    seen_explicit: set[tuple[str, str]] = set()
    seen_bound_surfaces: set[str] = set()

    for line in v59_rows:
        tokens = line["zl3b_line"].split()
        glosses = line["literal_token_glosses_de"].split(" | ")
        actions = int_set(line["action_ordinals"])
        assert len(tokens) == len(glosses) == int(line["token_count"])
        for ordinal, (surface, before_gloss) in enumerate(zip(tokens, glosses), 1):
            family = target_family(surface)
            if family is None:
                continue
            key = (line["locus"], str(ordinal))
            if family == "BOUND_DY":
                spec = bound_specs[surface]
                seen_bound_surfaces.add(surface)
                action_whole = spec["dispatch_class"].startswith("ACTION_")
                if surface == "qody":
                    assert ordinal in actions and not action_whole
                else:
                    assert action_whole == (ordinal in actions), (key, surface, spec["dispatch_class"], actions)
                dispatch_class = spec["dispatch_class"]
                after_gloss = spec["v60_literal_gloss_de"]
                confidence = spec["confidence"]
                evidence_key = "V59_WHOLE_TOKEN_ACTION_LICENSE" if action_whole else "V59_WHOLE_TOKEN_NOMINAL_STATE"
                rival = "dy als selbständiger Befehl innerhalb des Wortes"
                dy_contribution = spec["dy_contribution"]
            else:
                assert key in explicit_specs, ("missing explicit target spec", key, surface)
                spec = explicit_specs[key]
                seen_explicit.add(key)
                assert spec["surface"] == surface
                dispatch_class = spec["dispatch_class"]
                after_gloss = spec["v60_literal_gloss_de"]
                confidence = spec["confidence"]
                evidence_key = spec["evidence_key"]
                rival = spec["strongest_rival_de"]
                dy_contribution = "FREE_BOUNDARY" if family == "FREE_DY" else "NOT_APPLICABLE"

            audit = v57_audit[key]
            assert audit["surface"] == surface
            old_flags = split_flags(audit["mechanical_debt_flags"])
            remaining_flags = [flag for flag in old_flags if flag == "STATE_ONLY_NO_OBJECT"]
            old_union = any(
                int(audit[name])
                for name in ("strict_card_debt", "mechanical_debt", "specificity_open", "low_or_exploratory_card")
            )
            strict_after = 0
            mechanical_after = int(bool(remaining_flags))
            specificity_after = int("STATE_ONLY_NO_OBJECT" in remaining_flags)
            low_after = int(audit["low_or_exploratory_card"])
            new_union = bool(strict_after or mechanical_after or specificity_after or low_after)

            if family == "DCHEY":
                reader = dchey_source[key]["reader_support"]
            elif family == "NAKED_Y":
                yrow = y_census[key]
                reader = "ALL_SEPARATE" if yrow["all_reader_separate_y"] == "1" else (
                    f"IT2a:{yrow['it2a_boundary_class']}|RF1b:{yrow['rf1b_boundary_class']}"
                )
            else:
                reader = "CURRENT_EXACT_SURFACE__FORMAL_DY_PRIOR"

            row: dict[str, object] = {
                "page": line["page"], "locus": line["locus"], "ordinal": ordinal,
                "surface": surface, "target_family": family,
                "line_position": "INITIAL" if ordinal == 1 else ("FINAL" if ordinal == len(tokens) else "MEDIAL"),
                "action_licensed_before": int(ordinal in actions), "dispatch_class": dispatch_class,
                "v59_literal_gloss_de": before_gloss, "v60_literal_gloss_de": after_gloss,
                "dy_contribution": dy_contribution, "confidence": confidence,
                "evidence_key": evidence_key, "strongest_rival_de": rival,
                "left_surface": tokens[ordinal - 2] if ordinal > 1 else "<BOS>",
                "right_surface": tokens[ordinal] if ordinal < len(tokens) else "<EOS>",
                "reader_support": reader,
                "strict_debt_before": int(audit["strict_card_debt"]), "strict_debt_after": strict_after,
                "mechanical_flags_before": audit["mechanical_debt_flags"],
                "mechanical_flags_after": "|".join(remaining_flags) if remaining_flags else "NONE",
                "specificity_open_before": int(audit["specificity_open"]), "specificity_open_after": specificity_after,
                "low_confidence_before": int(audit["low_or_exploratory_card"]), "low_confidence_after": low_after,
                "four_layer_debt_before": int(old_union), "four_layer_debt_after": int(new_union),
            }
            targets.append(row)
            targets_by_line[line["locus"]].append(row)

    assert seen_explicit == set(explicit_specs)
    assert seen_bound_surfaces == set(bound_specs)
    assert len(targets) == 95
    family_counts = Counter(str(row["target_family"]) for row in targets)
    assert family_counts == {"DCHEY": 14, "NAKED_Y": 4, "FREE_DY": 3, "BOUND_DY": 74}
    dispatch_counts = Counter(str(row["dispatch_class"]) for row in targets)
    action_positions = sum(str(row["dispatch_class"]).startswith("ACTION_") for row in targets)
    result_positions = sum(str(row["dispatch_class"]).startswith("NOMINAL_") for row in targets)
    reference_positions = dispatch_counts["RIGHT_REFERENCE"]
    structural_positions = dispatch_counts["CLAUSE_STOP"] + dispatch_counts["LINE_STOP"]
    assert (action_positions, result_positions, reference_positions, structural_positions) == (24, 64, 3, 4)
    assert len(targets_by_line) == 40

    target_fields = [
        "page", "locus", "ordinal", "surface", "target_family", "line_position", "action_licensed_before",
        "dispatch_class", "v59_literal_gloss_de", "v60_literal_gloss_de", "dy_contribution", "confidence",
        "evidence_key", "strongest_rival_de", "left_surface", "right_surface", "reader_support",
        "strict_debt_before", "strict_debt_after", "mechanical_flags_before", "mechanical_flags_after",
        "specificity_open_before", "specificity_open_after", "low_confidence_before", "low_confidence_after",
        "four_layer_debt_before", "four_layer_debt_after",
    ]
    write_tsv(ART / "V60_95_POSITION_SCOPE_DISPATCH.tsv", targets, target_fields)

    dchey_rows: list[dict[str, object]] = []
    for source in sorted(dchey_source_rows, key=lambda row: (row["page"], row["locus"], int(row["ordinal"]))):
        nominal = source["line_position"] == "MEDIAL" or (
            source["locus"] == "f26r.2" and source["right_surface"] == "aiin"
        )
        dchey_rows.append({
            "page": source["page"], "locus": source["locus"], "ordinal": source["ordinal"],
            "line_position": source["line_position"], "right_surface": source["right_surface"],
            "reader_support": source["reader_support"],
            "dispatch_class": "NOMINAL_FINISHED_MIDDLE_DRY_PORTION" if nominal else "ACTION_DRY_MEASURED_PORTION_TO_MIDDLE",
            "v60_reading_de": "fertige abgemessene Mittelstufen-Trockenportion" if nominal else "eine abgemessene Portion bis zur Mittelstufe trocknen",
            "decision_basis": "IMMEDIATE_VALUE_OVERRIDES_LINE_ENTRY" if source["locus"] == "f26r.2" else (
                "MEDIAL_RESULT_SLOT" if nominal else "LINE_ENTRY_ACTION"
            ),
        })
    assert Counter(row["dispatch_class"] for row in dchey_rows) == {
        "ACTION_DRY_MEASURED_PORTION_TO_MIDDLE": 10,
        "NOMINAL_FINISHED_MIDDLE_DRY_PORTION": 5,
    }
    assert Counter(row["reader_support"] for row in dchey_rows) == {"BOTH_EXACT": 13, "ONE_EXACT": 2}
    write_tsv(ART / "DCHEY_15_OCCURRENCE_SCOPE_CENSUS.tsv", dchey_rows, list(dchey_rows[0]))

    dy_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in targets:
        if row["target_family"] == "BOUND_DY":
            dy_groups[str(row["surface"])].append(row)
    bound_summary: list[dict[str, object]] = []
    for surface, group in sorted(dy_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        spec = bound_specs[surface]
        bound_summary.append({
            "surface": surface, "positions": len(group), "lines": len({str(row["locus"]) for row in group}),
            "action_positions": sum(str(row["dispatch_class"]).startswith("ACTION_") for row in group),
            "result_positions": sum(str(row["dispatch_class"]).startswith("NOMINAL_") for row in group),
            "dispatch_class": spec["dispatch_class"], "v60_literal_gloss_de": spec["v60_literal_gloss_de"],
            "dy_contribution": spec["dy_contribution"], "confidence": spec["confidence"],
        })
    assert len(bound_summary) == 60
    write_tsv(ART / "BOUND_DY_60_SURFACE_DISPATCH.tsv", bound_summary, list(bound_summary[0]))

    y_prior = [row for row in read_tsv(Y_CLASS_SUMMARY) if row["layer"] == "FINAL_WITH_LABEL_AND_MATERIA_PRECEDENCE"]
    assert sum(int(row["occurrences"]) for row in y_prior) == 270
    write_tsv(ART / "Y_270_CONTEXT_PRIOR.tsv", y_prior, list(y_prior[0]))

    dy_prior_source = [row for row in read_tsv(DY_POSITION_SUMMARY) if row["cohort"] == "COMBINED30" and row["marker"] == "DY"]
    assert len(dy_prior_source) == 1 and int(dy_prior_source[0]["occurrence_count"]) == 705
    dy_prior = [{
        **dy_prior_source[0],
        "v60_interpretation": "DY marks a completed endpoint; it is punctuation when free and contributes no independent physical verb inside a whole token.",
        "v60_bound_action_positions": 15, "v60_bound_result_positions": 59, "v60_free_boundary_positions": 3,
    }]
    write_tsv(ART / "DY_705_CLOSURE_PRIOR.tsv", dy_prior, list(dy_prior[0]))

    y_dy_classes = read_tsv(Y_DY_CLASSES)
    joint = read_tsv(Y_DY_JOINT)
    assert len(joint) == 28
    distinction_rows = [{
        "source_class": row["distinction_class"], "source_event_count": row["event_count"],
        "source_default_reading_de": row["default_reading_de"],
        "v60_use": "Y_ARGUMENT_OR_REFERENCE" if row["distinction_class"].startswith("Y_") else "DY_ENDPOINT_CONTROL",
    } for row in y_dy_classes]
    write_tsv(ART / "Y_DY_DISTINCTION_PRIOR.tsv", distinction_rows, list(distinction_rows[0]))

    v60_rows: list[dict[str, object]] = []
    patched_lines: list[dict[str, object]] = []
    for line in v59_rows:
        output: dict[str, object] = dict(line)
        local_targets = targets_by_line.get(line["locus"], [])
        if local_targets:
            glosses = line["literal_token_glosses_de"].split(" | ")
            for target in local_targets:
                glosses[int(target["ordinal"]) - 1] = str(target["v60_literal_gloss_de"])
            output["literal_token_glosses_de"] = " | ".join(glosses)
            output["aligned_line_de"] = aligned_reading(glosses)
            output["practical_translation_de"] = strict_practical_reading(glosses)
            output["v60_scope_dispatch"] = " | ".join(
                f"{target['surface']}#{target['ordinal']}={target['dispatch_class']}" for target in local_targets
            )
            output["v60_patch_basis"] = " | ".join(
                f"{target['surface']}#{target['ordinal']}:{target['evidence_key']}" for target in local_targets
            )
            output["v60_semantic_revisions"] = len(local_targets)
            patched_lines.append({
                "page": line["page"], "locus": line["locus"], "target_positions": len(local_targets),
                "target_ordinals": "|".join(str(target["ordinal"]) for target in local_targets),
                "target_surfaces": "|".join(str(target["surface"]) for target in local_targets),
                "v59_practical_translation_de": line["practical_translation_de"],
                "v60_practical_translation_de": output["practical_translation_de"],
            })
        else:
            output["v60_scope_dispatch"] = "NONE"
            output["v60_patch_basis"] = "NONE"
            output["v60_semantic_revisions"] = 0
        old_actions = int_set(line["action_ordinals"])
        new_actions = old_actions - ({13} if line["locus"] == "f105r.2" else set())
        tokens = line["zl3b_line"].split()
        output["action_positions"] = len(new_actions)
        output["action_ordinals"] = "|".join(str(value) for value in sorted(new_actions)) if new_actions else "NONE"
        output["action_surfaces"] = "|".join(tokens[value - 1] for value in sorted(new_actions)) if new_actions else "NONE"
        if line["locus"] == "f105r.2":
            assert old_actions - new_actions == {13} and tokens[12] == "qody"
        else:
            assert new_actions == old_actions
        v60_rows.append(output)
    assert len(patched_lines) == 40
    v60_fields = list(v59_rows[0]) + ["v60_scope_dispatch", "v60_patch_basis", "v60_semantic_revisions"]
    write_tsv(ART / "V60_51_LINE_READER.tsv", v60_rows, v60_fields)
    write_tsv(ART / "V60_40_PATCHED_LINES.tsv", patched_lines, list(patched_lines[0]))

    strict_cleared = sum(int(row["strict_debt_before"]) - int(row["strict_debt_after"]) for row in targets)
    mechanical_union_cleared = sum(
        int(row["mechanical_flags_before"] != "NONE") - int(row["mechanical_flags_after"] != "NONE") for row in targets
    )
    mechanical_memberships_cleared = sum(
        len(split_flags(str(row["mechanical_flags_before"]))) - len(split_flags(str(row["mechanical_flags_after"]))) for row in targets
    )
    specificity_cleared = sum(int(row["specificity_open_before"]) - int(row["specificity_open_after"]) for row in targets)
    four_layer_cleared = sum(int(row["four_layer_debt_before"]) - int(row["four_layer_debt_after"]) for row in targets)
    assert (strict_cleared, mechanical_union_cleared, mechanical_memberships_cleared, specificity_cleared, four_layer_cleared) == (14, 11, 15, 39, 40)

    v59_result = json.loads(V59_RESULT.read_text(encoding="utf-8"))
    before = {
        "strict_card_debt_positions": 120, "mechanical_visible_debt_union_positions": 163,
        "mechanical_flag_memberships": 177, "broad_specificity_open_positions": 324,
        "four_layer_union_with_low_confidence_positions": 370, "without_current_debt_or_confidence_signal": 109,
    }
    after = {
        "strict_card_debt_positions": before["strict_card_debt_positions"] - strict_cleared,
        "mechanical_visible_debt_union_positions": before["mechanical_visible_debt_union_positions"] - mechanical_union_cleared,
        "mechanical_flag_memberships": before["mechanical_flag_memberships"] - mechanical_memberships_cleared,
        "broad_specificity_open_positions": before["broad_specificity_open_positions"] - specificity_cleared,
        "four_layer_union_with_low_confidence_positions": before["four_layer_union_with_low_confidence_positions"] - four_layer_cleared,
        "without_current_debt_or_confidence_signal": before["without_current_debt_or_confidence_signal"] + four_layer_cleared,
    }
    interpretations = {
        "strict_card_debt_positions": "fourteen structural, alternative or generic target cards receive one local function",
        "mechanical_visible_debt_union_positions": "non-single, structural-as-value and hard-generic flags clear; 22 headless states remain",
        "mechanical_flag_memberships": "fifteen resolved memberships are removed without hiding STATE_ONLY_NO_OBJECT",
        "broad_specificity_open_positions": "39 functional action/result/reference/boundary readings become concrete",
        "four_layer_union_with_low_confidence_positions": "40 positions become clean; one old LOW card and 22 objectless states remain",
        "without_current_debt_or_confidence_signal": "the same forty positions enter the clean pool",
    }
    debt_rows = [{
        "metric": metric, "v59_before": value, "v60_after": after[metric],
        "delta": after[metric] - value, "interpretation": interpretations[metric],
    } for metric, value in before.items()]
    write_tsv(ART / "V60_DEBT_SUMMARY.tsv", debt_rows, list(debt_rows[0]))

    delta_rows = [{
        "locus": row["locus"], "ordinal": row["ordinal"], "surface": row["surface"],
        "dispatch_class": row["dispatch_class"],
        "strict_cleared": int(row["strict_debt_before"]) - int(row["strict_debt_after"]),
        "mechanical_memberships_cleared": len(split_flags(str(row["mechanical_flags_before"]))) - len(split_flags(str(row["mechanical_flags_after"]))),
        "specificity_cleared": int(row["specificity_open_before"]) - int(row["specificity_open_after"]),
        "four_layer_position_cleared": int(row["four_layer_debt_before"]) - int(row["four_layer_debt_after"]),
        "remaining_debt": "STATE_ONLY_NO_OBJECT" if row["mechanical_flags_after"] != "NONE" else (
            "LOW_CONFIDENCE" if int(row["low_confidence_after"]) else "NONE"
        ),
    } for row in targets]
    write_tsv(ART / "V60_95_POSITION_DEBT_DELTA.tsv", delta_rows, list(delta_rows[0]))

    hypothesis_rows = [
        {"hypothesis": "UNIVERSAL_DCHEY_ACTION", "fit": "10/15", "failure": "five result slots including line-initial f26r.2", "decision": "REJECT"},
        {"hypothesis": "UNIVERSAL_DCHEY_NOUN", "fit": "5/15", "failure": "ten genuine line-entry drying instructions", "decision": "REJECT"},
        {"hypothesis": "DCHEY_SCOPE_DISPATCH", "fit": "15/15", "failure": "none in admitted circuit", "decision": "SELECT"},
        {"hypothesis": "UNIVERSAL_Y_REFERENCE", "fit": "3/4 current", "failure": "f56r.6 is an exact line stop; global y has eight context classes", "decision": "REJECT"},
        {"hypothesis": "FREE_DY_PHYSICAL_CLOSE_COMMAND", "fit": "0/3", "failure": "all three are punctuation-like block or line boundaries", "decision": "REJECT"},
        {"hypothesis": "DY_SUBSTRING_LICENSES_ACTION", "fit": "15/74", "failure": "59 bound-dy wholes are nominal finished results after qody loses its dy-only verb", "decision": "REJECT"},
        {"hypothesis": "INDEPENDENT_CORE_ACTION_OR_RESULT_PLUS_DY_ENDPOINT", "fit": "74/74", "failure": "none in current reader", "decision": "SELECT"},
    ]
    write_tsv(ART / "HYPOTHESIS_COMPARISON.tsv", hypothesis_rows, list(hypothesis_rows[0]))

    counter_rows = [
        {"case": "f26r.2#1 dchey", "counter_to": "line-entry always action", "observation": "immediate aiin value binds a finished measured result", "v60": "fertige abgemessene Mittelstufen-Trockenportion"},
        {"case": "f7r.2", "counter_to": "one dchey value per line", "observation": "initial dcheey is an action; medial dchey is its result class", "v60": "position controls grammatical orientation"},
        {"case": "f56r.6#2/#6", "counter_to": "free dy/y are spoken commands", "observation": "dy separates action from result; final y ends the line", "v60": "; and ."},
        {"case": "f76v.10#10 dy", "counter_to": "dy names a value field", "observation": "free dy follows the completed three-portion value block at EOS", "v60": "."},
        {"case": "GDT559 28 Y+DY cards", "counter_to": "Y and DY are one hidden word", "observation": "Y precedes a separately ordered DY atom in all joint cards", "v60": "argument/reference then endpoint"},
        {"case": "GDT557 formal DY prior", "counter_to": "formal DY atom equals the exact surface word dy", "observation": "the 705-count prior is a parsed atom layer, not an exact-surface census", "v60": "use as role analogy only; current free dy is decided locally"},
        {"case": "GDT425 exact dchey events", "counter_to": "dchey securely proves D+CH+E+Y plus closure", "observation": "four admitted exact events carry CH+E+Y and has_close=NO", "v60": "retain a learned whole-surface scope card; composition remains open"},
        {"case": "qoeedy versus chedy", "counter_to": "dy-ending surface is automatically imperative", "observation": "qoeedy is action-licensed as take; chedy is a finished dry state", "v60": "whole token licenses the action, not dy"},
    ]
    write_tsv(ART / "COUNTEREXAMPLE_AUDIT.tsv", counter_rows, list(counter_rows[0]))

    reader_lines = [
        "# GDT687 — V60 action/result/boundary reader", "", "```text",
        "dchey am Zeilenanfang      -> abgemessene Portion bis Mittelstufe trocknen",
        "dchey medial/mit Wertkopf  -> fertige abgemessene Mittelstufen-Trockenportion",
        "nacktes y medial           -> dazu / hierzu (lokal)",
        "nacktes y am Zeilenende    -> .", "freies dy intern           -> ;",
        "freies dy am Zeilenende    -> .",
        "gebundenes ...dy           -> Ganzwort-Aktion oder fertiger Resultatzustand; dy gibt nur den Endpunkt",
        "```", "",
        f"Der aktuelle Reader enthält {len(targets)} Zielpositionen auf {len(targets_by_line)} Zeilen: "
        f"{action_positions} Aktionen, {result_positions} fertige Resultate/Zustände, "
        f"{reference_positions} lokale Verweise und {structural_positions} reine Grenzen.",
        "", "## Alle vierzig neu gesetzten Zeilen", "",
    ]
    for row in patched_lines:
        reader_lines.extend([
            f"### {row['locus']}", "",
            f"`{next(line['zl3b_line'] for line in v59_rows if line['locus'] == row['locus'])}`", "",
            str(row["v60_practical_translation_de"]), "",
        ])
    (ART / "GDT687_V60_SCOPE_READER.md").write_text("\n".join(reader_lines), encoding="utf-8")

    generated_files = {
        "BOUND_DY_60_SURFACE_DISPATCH.tsv",
        "COUNTEREXAMPLE_AUDIT.tsv",
        "DCHEY_15_OCCURRENCE_SCOPE_CENSUS.tsv",
        "DY_705_CLOSURE_PRIOR.tsv",
        "GDT687_V60_SCOPE_READER.md",
        "HYPOTHESIS_COMPARISON.tsv",
        "V60_40_PATCHED_LINES.tsv",
        "V60_51_LINE_READER.tsv",
        "V60_95_POSITION_DEBT_DELTA.tsv",
        "V60_95_POSITION_SCOPE_DISPATCH.tsv",
        "V60_DEBT_SUMMARY.tsv",
        "Y_270_CONTEXT_PRIOR.tsv",
        "Y_DY_DISTINCTION_PRIOR.tsv",
    }
    assert all((ART / name).is_file() for name in generated_files)
    result = {
        "status": "PASS_95_POSITION_SCOPE_DISPATCH__V60_24_ACTION_64_RESULT_3_REFERENCE_4_BOUNDARY",
        "basis": {
            "v59_lines": 51, "v59_positions": 479, "target_positions": 95, "target_lines": 40,
            "dchey_current_positions": 14, "dchey_global_positions_including_f81r_source": 15,
            "naked_y_current_positions": 4, "dy_family_current_positions": 77,
            "bound_dy_positions": 74, "free_dy_positions": 3,
            "global_naked_y_prior_positions": 270, "formal_dy_prior_occurrences": 705,
            "y_dy_joint_formal_cards": 28, "new_pages": 0, "f84_access": 0, "f84r_access": 0,
        },
        "dispatch": {
            "action_positions": action_positions, "finished_result_or_state_positions": result_positions,
            "right_reference_positions": reference_positions, "structural_boundary_positions": structural_positions,
            "dchey_actions_global": 10, "dchey_results_global": 5,
            "bound_dy_actions": 15, "bound_dy_results": 59,
        },
        "v60": {
            "positions_revised": 95, "lines_revised": 40,
            "source_action_positions_before": int(v59_result["v59"]["action_positions"]),
            "source_action_positions_after": int(v59_result["v59"]["action_positions"]) - 1,
            "strict_debt_positions_after": after["strict_card_debt_positions"],
            "mechanical_debt_union_after": after["mechanical_visible_debt_union_positions"],
            "mechanical_memberships_after": after["mechanical_flag_memberships"],
            "broad_specificity_after": after["broad_specificity_open_positions"],
            "four_layer_union_after": after["four_layer_union_with_low_confidence_positions"],
            "clean_positions_after": after["without_current_debt_or_confidence_signal"],
            "remaining_state_without_object_targets": 22, "remaining_low_confidence_targets": 1,
        },
        "claim_ceiling": "Exploratory replaceable workshop renderer. It fixes action/result/boundary scope and concrete local defaults, not plaintext, language or historical codebook identity.",
        "files": {name: sha256(ART / name) for name in sorted(generated_files)},
    }
    write_json(ART / "RESULT.json", result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
