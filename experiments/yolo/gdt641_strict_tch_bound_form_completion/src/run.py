#!/usr/bin/env python3
"""Build GDT641: complete the two reader-exact strict TCH holes exposed by GDT640."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt641_strict_tch_bound_form_completion")
ART = ROOT / BASE_REL / "artifacts"
G640_BASE = Path("experiments/yolo/gdt640_downstream_component_prediction")
G640_RUN_REL = G640_BASE / "src/run.py"
G640_ALLOW_REL = G640_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G640_ONE_REL = G640_BASE / "artifacts/ONE_UNKNOWN_PASSAGES_V17.tsv"
G640_COVERAGE_REL = G640_BASE / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V17.tsv"
G640_COMPLETE_REL = G640_BASE / "artifacts/COMPLETE_PASSAGES_V17.tsv"
G640_GLOSSARY_REL = G640_BASE / "artifacts/V17_EXACT_TOKEN_GLOSSARY.tsv"
G640_DICT_REL = G640_BASE / "artifacts/WORKING_DICTIONARY_V17.tsv"
G640_RESULT_REL = G640_BASE / "artifacts/RESULT.json"
G640_REPORT_REL = G640_BASE / "REPORT.md"
G624_REPORT_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md")
G624_GRID_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/GRID_CELLS.tsv")
G624_BIND_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/LOCAL_HERBAL_BINDINGS.tsv")
G625_REPORT_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/REPORT.md")
G625_TERMINAL_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/TERMINAL_QUALITY_OCCURRENCES.tsv")
G625_ANCHOR_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/ANCHOR_QUALITY_CONTACTS.tsv")
G628_REPORT_REL = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G628_MATRIX_REL = Path("experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv")
G633_REPORT_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G633_DICT_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/WORKING_DICTIONARY_V10.tsv")

spec = importlib.util.spec_from_file_location("gdt640_builder_for_gdt641", ROOT / G640_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT640 builder helpers")
g640 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g640)
g637 = g640.g637
TOKENS_REL = g640.TOKENS_REL
CROSS_REL = g640.CROSS_REL

STATUS = "PASS_2_STRICT_TCH_EXACT_DEFAULTS__2_NEW_COMPLETE_LINES"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)

CANDIDATE_SPECS = (
    {
        "surface": "tcheor", "source_locus": "f15r.12", "decision": "ACCEPT",
        "working_meaning_de": "kalt-trockener Drogenteil",
        "composition": "tch+e+or", "scope": "exact whole surface only",
        "rival_de": "kalt-trockene Drogenportion, gebundene Form",
        "decision_basis": (
            "reader-exact tchol/tchor and tcheol/tcheor OL-OR pairs bind tch, "
            "the inserted e stage and the OR part carrier"
        ),
        "barrier": "NONE",
    },
    {
        "surface": "chetchy", "source_locus": "f37v.8", "decision": "ACCEPT",
        "working_meaning_de": "getrocknete Droge; kalt-trocken, Grundform",
        "composition": "ch+e+tch+y", "scope": "exact whole surface only",
        "rival_de": "attributiv gebundene kalt-trockene Grundform",
        "decision_basis": (
            "four reader-exact occurrences, the GDT624 f29 part-quality binding, "
            "and the che plus TCH plus y cell with hot-arm and cho-frame sisters"
        ),
        "barrier": "NONE",
    },
)

FAMILY_FORMS = (
    ("TCH_E_FORM_LADDER", "tchy", "kalt-trocken, Grundform"),
    ("TCH_E_FORM_LADDER", "tchey", "kalt-trocken, gebundene Form"),
    ("TCH_E_FORM_LADDER", "tcheey", "kalt-trocken, erweiterte Bindungsform"),
    ("TCH_E_OL_OR", "tchol", "kalt-trockener Stoff"),
    ("TCH_E_OL_OR", "tchor", "kalt-trockener Teil-/Portionsträger"),
    ("TCH_E_OL_OR", "tcheol", "kalt-trockener Drogenstoff, e-Bindungsform"),
    ("TCH_E_OL_OR", "tcheor", "kalt-trockener Drogenteil"),
    ("CHE_TCH_FORM", "chetchy", "getrocknete Droge; kalt-trocken, Grundform"),
    ("CHE_TCH_FORM", "chetchdy", "getrocknete kalt-trockene Form mit dy-Abschluss"),
    ("CHE_KCH_HOT_ARM", "chekchy", "getrocknete Droge; heiß-trocken, Grundform"),
    ("CHE_KCH_HOT_ARM", "chekchey", "getrocknete Droge; heiß-trocken, gebundene Form"),
    ("CHE_KCH_HOT_ARM", "chekchdy", "getrocknete Droge; heiß-trocken, dy-Abschluss"),
    ("CHO_TCH_PREPARATION", "chotchy", "Trockenansatz, kalt-trockene Grundform"),
    ("CHO_TCH_PREPARATION", "chotchey", "Trockenansatz, kalt-trockene gebundene Form"),
    ("CHO_TCH_PREPARATION", "chotcheey", "Trockenansatz, kalt-trockene erweiterte Bindungsform"),
)

COMPONENT_ROWS = (
    ("tcheor", "tch", "kalt-trocken", str(G625_TERMINAL_REL), "BOUND_TCH_QUALITY_BLOCK", "inside exact tcheor only"),
    ("tcheor", "e", "attributive Bindungsstufe", str(G624_GRID_REL), "BOUND_E_STAGE", "inside exact tcheor only"),
    ("tcheor", "or", "Drogenteil; Portionslesung bleibt Rivale", str(G628_MATRIX_REL), "BOUND_OR_PART_CARRIER", "no bare-or promotion"),
    ("chetchy", "ch+e", "getrocknet und attributiv gefasst", str(G633_DICT_REL), "DRY_ATTRIBUTIVE_SHELL", "inside exact chetchy only"),
    ("chetchy", "tch", "kalt-trockene Qualitätsklasse", str(G625_TERMINAL_REL), "BOUND_TCH_QUALITY_BLOCK", "inside exact chetchy only"),
    ("chetchy", "y", "Grundformabschluss", str(G624_GRID_REL), "BOUND_BASE_FORM", "inside exact chetchy only"),
)

SMOOTHED_NEW_LINES = {
    "f15r.12": (
        "Kalte Drogenportion; Blüten-/Fruchtstand; kalt-trockener Drogenteil; "
        "trockene Grundform; Blatt-/Krautgut, Klasse III; feucht, Grad I."
    ),
    "f37v.8": (
        "Kalte Drogenportion; Trockenpräparat, Form III; getrocknete Droge, "
        "kalt-trocken, Grundform; Grad III."
    ),
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "SEQUENTIAL_DECISION_LEDGER.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "V18_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V18.tsv",
    "COMPLETE_PASSAGES_V18.tsv", "ONE_UNKNOWN_PASSAGES_V18.tsv",
    "WORKING_DICTIONARY_V18.tsv",
)
COVERAGE_FIELDS = g640.COVERAGE_FIELDS
ONE_FIELDS = g640.ONE_FIELDS


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def dictionary_hash(rows: list[dict[str, object]]) -> str:
    return canonical_hash(rows)


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "exact_glossary_surfaces": len(glossary),
    }


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT641_EXACT_WHOLE",
        "kind": "EXACT_WHOLE_SURFACE_TCH_COMPLETION",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; {occurrences} audited occurrences; {spec_row['scope']}; "
            "no substring, naked-body, wrapper or absent-cell transfer"
        ),
        "status": f"NEW_V18_ACCEPTED_ROUND_{round_number:02d}",
    }


def audit_candidate(
    round_number, spec_row, token_rows, by_line, positions, exact, boundary,
    cross_by_locus, pre_by_locus, trial_by_locus,
) -> list[dict[str, object]]:
    surface = spec_row["surface"]
    members = [row for row in token_rows if row["eva"] == surface]
    rows: list[dict[str, object]] = []
    for member in members:
        locus, token_index = member["locus"], int(member["token_index"])
        ordinal, position = positions[locus, token_index]
        line = by_line[locus]
        target_count = sum(str(token["eva"]) == surface for token in line)
        before, after = pre_by_locus[locus], trial_by_locus[locus]
        known_other = int(before["known_tokens"])
        other_positions = max(len(line) - target_count, 1)
        flags: list[str] = []
        if not exact[locus, token_index]:
            flags.append("READER_SPLIT_OR_FUSION")
        if int(before["ambiguous_tokens"]):
            flags.append("ACTIVE_RIVAL_CONTEXT")
        if int(before["reader_unstable_tokens"]):
            flags.append("OTHER_READER_BOUNDARY_IN_LINE")
        if known_other < 2 and not (other_positions == 1 and known_other == 1):
            flags.append("OPAQUE_OTHER_TOKENS")
        if surface == "tcheor":
            flags.extend(("OR_COMPONENT_EXACT_ONLY", "ATTRIBUTIVE_E_EXACT_ONLY"))
        else:
            flags.extend(("STACKED_DRY_QUALITY_SCOPE", "CHE_WRAPPER_EXACT_ONLY"))
        if not exact[locus, token_index]:
            verdict = "READER_BOUNDARY_WARNING"
            reason = "target surface is split, fused or changed in an alternate reading"
        elif known_other < 2 and not (other_positions == 1 and known_other == 1):
            verdict = "OPAQUE_CONTEXT"
            reason = "too few independently concrete neighbouring positions to test the complete phrase"
        else:
            verdict = "CONSISTENT_CONCRETE"
            reason = "the complete local reading preserves every visible bound field without an opposite value"
        before_glosses = split_pipe(before["token_glosses_de"])
        before_states = split_pipe(before["scope_states"])
        after_glosses = split_pipe(after["token_glosses_de"])
        cross = cross_by_locus.get(locus, {})
        rows.append({
            "audit_id": "", "round": round_number, "surface": surface,
            "page": member["page"], "locus": locus, "section": member["section"],
            "language": member["language"], "hand": member["hand"],
            "token_ordinal": ordinal, "line_position": position,
            "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "zl3b_line": before["zl3b_line"], "it2a_line": cross.get("it2a_clean", ""),
            "rf1b_line": cross.get("rf1b_clean", ""),
            "reader_exact": exact[locus, token_index],
            "split_normalized": boundary[locus, token_index],
            "before_state": before_states[ordinal - 1],
            "before_gloss": before_glosses[ordinal - 1],
            "after_gloss": after_glosses[ordinal - 1],
            "known_other_tokens": known_other, "other_token_positions": other_positions,
            "context_fraction": f"{known_other / other_positions:.6f}",
            "local_before_de": before["token_glosses_de"],
            "local_after_de": after["token_glosses_de"],
            "flags": "|".join(flags), "verdict": verdict, "review_reason": reason,
        })
    rows.sort(key=lambda row: (str(row["locus"]), int(row["token_ordinal"])))
    for index, row in enumerate(rows, 1):
        row["audit_id"] = f"G641-A{round_number:02d}-{index:03d}"
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G640_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)
    positions = g637.g636.position_maps(by_line)

    base_one = read_tsv(ROOT / G640_ONE_REL)
    target_surfaces = {str(row["surface"]) for row in CANDIDATE_SPECS}
    target_rows = [row for row in base_one if int(row["strict_eligible"]) and row["unknown_surface"] in target_surfaces]
    target_by_surface = {row["unknown_surface"]: row for row in target_rows}
    if len(target_rows) != 2 or set(target_by_surface) != target_surfaces:
        raise RuntimeError("GDT640 strict TCH frontier changed")
    for spec_row in CANDIDATE_SPECS:
        if target_by_surface[str(spec_row["surface"])]["locus"] != spec_row["source_locus"]:
            raise RuntimeError(f"source locus drift: {spec_row['surface']}")

    v17_dictionary: list[dict[str, object]] = [dict(row) for row in read_tsv(ROOT / G640_DICT_REL)]
    old_coverage = read_tsv(ROOT / G640_COVERAGE_REL)
    old_complete = read_tsv(ROOT / G640_COMPLETE_REL)
    old_glossary = read_tsv(ROOT / G640_GLOSSARY_REL)
    if len(v17_dictionary) != 283 or len(old_coverage) != 4128 or len(old_complete) != 42 or len(old_glossary) != 236:
        raise RuntimeError("GDT640 frozen base count changed")
    glossary = {row["surface"]: dict(row) for row in old_glossary}
    initial_glossary = {surface: dict(row) for surface, row in glossary.items()}
    initial_dictionary = [dict(row) for row in v17_dictionary]
    coverage, one_unknown, _, complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
    if len(coverage) != 4128 or len(complete) != 42 or len(one_unknown) != 62:
        raise RuntimeError("replayed V17 reader count changed")
    base_complete_loci = {str(row["locus"]) for row in complete}

    family_rows: list[dict[str, object]] = []
    for family, surface, reading in FAMILY_FORMS:
        members = [row for row in token_rows if row["eva"] == surface]
        family_rows.append({
            "family": family, "surface": surface, "observed": int(bool(members)),
            "occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "working_reading_de": reading,
        })
    component_rows = [
        {"component_id": f"G641-B{index:02d}", "surface": surface, "segment": segment,
         "working_value_de": value, "evidence_path": evidence_path,
         "evidence_kind": kind, "licensed_use": licensed_use}
        for index, (surface, segment, value, evidence_path, kind, licensed_use)
        in enumerate(COMPONENT_ROWS, 1)
    ]

    accepted_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = []
    new_complete_rows: list[dict[str, object]] = []
    round_rows.append({
        "round": 0, "surface": "BASE_V17", "decision": "BASE",
        "dictionary_entries": len(v17_dictionary), "dictionary_sha256": dictionary_hash(v17_dictionary),
        **metrics(coverage, one_unknown, complete, glossary),
    })

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if surface in glossary or GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"invalid strict TCH target: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        pre_dictionary = [*v17_dictionary, *accepted_rows]
        pre_hash = dictionary_hash(pre_dictionary)
        pre_coverage, pre_one, _, pre_complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
        pre_by_locus = {str(row["locus"]): row for row in pre_coverage}
        pre_complete_loci = {str(row["locus"]) for row in pre_complete}
        pre_strict_loci = {str(row["locus"]) for row in pre_complete if int(row["strict_complete"])}

        trial_glossary = {key: dict(value) for key, value in glossary.items()}
        g637.set_gloss(
            trial_glossary, surface, spec_row["working_meaning_de"], f"GDT641:ROUND_{round_number:02d}",
            "EXACT_WHOLE_SURFACE_TCH_COMPLETION", "KNOWN_EXACT_WHOLE", 122,
        )
        trial_coverage, trial_one, _, trial_complete = g637.build_line_coverage(
            by_line, trial_glossary, exact, boundary, cross_by_locus,
        )
        trial_by_locus = {str(row["locus"]): row for row in trial_coverage}
        trial_complete_loci = {str(row["locus"]) for row in trial_complete}
        trial_strict_loci = {str(row["locus"]) for row in trial_complete if int(row["strict_complete"])}
        trial_new = sorted(trial_complete_loci - pre_complete_loci)
        trial_new_strict = sorted(trial_strict_loci - pre_strict_loci)
        candidate_audit = audit_candidate(
            round_number, spec_row, token_rows, by_line, positions, exact, boundary,
            cross_by_locus, pre_by_locus, trial_by_locus,
        )
        audit_rows.extend(candidate_audit)
        verdicts = Counter(str(row["verdict"]) for row in candidate_audit)
        exact_anchors = sum(int(row["reader_exact"]) for row in candidate_audit)
        if (
            spec_row["decision"] != "ACCEPT" or not trial_new
            or spec_row["source_locus"] not in trial_new_strict
            or exact_anchors != len(members) or verdicts["READER_BOUNDARY_WARNING"]
        ):
            raise RuntimeError(f"strict TCH target failed its frozen acceptance: {surface}")

        glossary = trial_glossary
        coverage, one_unknown, complete = trial_coverage, trial_one, trial_complete
        accepted_rows.append(dictionary_row(spec_row, round_number, len(members)))
        for locus in trial_new:
            before, after = pre_by_locus[locus], trial_by_locus[locus]
            if locus not in SMOOTHED_NEW_LINES:
                raise RuntimeError(f"missing manual reading: {locus}")
            new_complete_rows.append({
                "round": round_number, "surface": surface, "page": after["page"], "locus": locus,
                "strict_complete": int(locus in trial_strict_loci), "zl3b_line": after["zl3b_line"],
                "before_glosses_de": before["token_glosses_de"],
                "literal_after_de": "; ".join(split_pipe(after["token_glosses_de"])),
                "smoothed_working_reading_de": SMOOTHED_NEW_LINES[locus],
                "all_present_exact": after["all_present_exact"],
                "scope_clean": int(int(after["ambiguous_tokens"]) == 0 and int(after["reader_unstable_tokens"]) == 0),
            })

        post_dictionary = [*v17_dictionary, *accepted_rows]
        post_hash = dictionary_hash(post_dictionary)
        ledger_rows.append({
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "decision_reason": spec_row["decision_basis"], "barrier": "NONE",
            "pre_dictionary_entries": len(pre_dictionary), "post_dictionary_entries": len(post_dictionary),
            "pre_dictionary_sha256": pre_hash, "post_dictionary_sha256": post_hash,
            "occurrences": len(members), "audited_occurrences": len(candidate_audit),
            "reader_exact_occurrences": exact_anchors,
            "consistent_concrete": verdicts["CONSISTENT_CONCRETE"], "opaque_context": verdicts["OPAQUE_CONTEXT"],
            "reader_boundary_warning": verdicts["READER_BOUNDARY_WARNING"],
            "trial_complete_gain": len(trial_new), "trial_strict_complete_gain": len(trial_new_strict),
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "strict_complete_before": len(pre_strict_loci),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "trial_new_complete_loci": "|".join(trial_new),
        })
        round_rows.append({
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": post_hash,
            **metrics(coverage, one_unknown, complete, glossary),
        })
        source = target_by_surface[surface]
        target_deck.append({
            "candidate_id": f"G641-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "gdt640_rank": source["rank"], "gdt640_source_locus": source["locus"],
            "gdt640_frozen_default_de": source["proposed_default_de"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "scope": spec_row["scope"], "rival_de": spec_row["rival_de"],
            "occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_anchors, "decision": "ACCEPT", "barrier": "NONE",
            "decision_basis": spec_row["decision_basis"],
        })

    final_dictionary = [*v17_dictionary, *accepted_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
    final_complete_loci = {str(row["locus"]) for row in final_complete}
    final_glossary_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    accepted_defaults = [
        {**row, "accepted_round": int(row["status"].rsplit("_", 1)[1]),
         "surface": row["entry"].split("@", 1)[0],
         "source_locus": next(item["gdt640_source_locus"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
         "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0])}
        for row in accepted_rows
    ]

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "gdt640_rank", "gdt640_source_locus",
        "gdt640_frozen_default_de", "working_meaning_de", "composition", "scope", "rival_de",
        "occurrences", "pages", "reader_exact_occurrences", "decision", "barrier", "decision_basis",
    ))
    write_tsv(output_dir / "FORM_FAMILY_ATLAS.tsv", family_rows, (
        "family", "surface", "observed", "occurrences", "pages", "reader_exact_occurrences", "working_reading_de",
    ))
    write_tsv(output_dir / "COMPONENT_BINDING_AUDIT.tsv", component_rows, (
        "component_id", "surface", "segment", "working_value_de", "evidence_path", "evidence_kind", "licensed_use",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line",
        "rf1b_line", "reader_exact", "split_normalized", "before_state", "before_gloss",
        "after_gloss", "known_other_tokens", "other_token_positions", "context_fraction",
        "local_before_de", "local_after_de", "flags", "verdict", "review_reason",
    ))
    write_tsv(output_dir / "SEQUENTIAL_DECISION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "decision", "decision_reason", "barrier", "pre_dictionary_entries",
        "post_dictionary_entries", "pre_dictionary_sha256", "post_dictionary_sha256",
        "occurrences", "audited_occurrences", "reader_exact_occurrences", "consistent_concrete",
        "opaque_context", "reader_boundary_warning", "trial_complete_gain", "trial_strict_complete_gain",
        "complete_before", "complete_after", "strict_complete_before", "strict_complete_after",
        "one_unknown_before", "one_unknown_after", "trial_new_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "decision", "dictionary_entries", "dictionary_sha256",
        "physical_lines", "known_token_positions", "unknown_token_positions", "complete_multi_token_lines",
        "strict_complete_lines", "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule",
        "status", "accepted_round", "source_locus", "occurrences",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "round", "surface", "page", "locus", "strict_complete", "zl3b_line",
        "before_glosses_de", "literal_after_de", "smoothed_working_reading_de", "all_present_exact", "scope_clean",
    ))
    write_tsv(output_dir / "V18_EXACT_TOKEN_GLOSSARY.tsv", final_glossary_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V18.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V18.tsv", final_complete, ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V18.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V18.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G640_RUN_REL, G640_ALLOW_REL, G640_ONE_REL, G640_COVERAGE_REL, G640_COMPLETE_REL,
        G640_GLOSSARY_REL, G640_DICT_REL, G640_RESULT_REL, G640_REPORT_REL,
        G624_REPORT_REL, G624_GRID_REL, G624_BIND_REL, G625_REPORT_REL, G625_TERMINAL_REL,
        G625_ANCHOR_REL, G628_REPORT_REL, G628_MATRIX_REL, G633_REPORT_REL, G633_DICT_REL,
        TOKENS_REL, CROSS_REL,
    )
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    verdict_counts = Counter(str(row["verdict"]) for row in audit_rows)
    result_core = {
        "schema": "GDT641_STRICT_TCH_BOUND_FORM_COMPLETION_RESULT_V1",
        "experiment_id": "GDT641", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
                  "new_pages": 0, "new_images": 0, "allowed_pages": len(pages),
                  "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {"candidates": len(target_deck), "accepted": len(accepted_rows), "held": 0,
                       "audited_occurrences": len(audit_rows), "verdicts": dict(sorted(verdict_counts.items())),
                       "accepted_surfaces": [row["surface"] for row in target_deck]},
        "coverage": {"base_complete_multi_token_lines": len(old_complete),
                     "base_strict_complete_lines": sum(int(row["strict_complete"]) for row in old_complete),
                     "newly_completed_lines": len(final_complete_loci - base_complete_loci), **final_metrics},
        "working_dictionary": {"v17_entries": len(v17_dictionary), "v18_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_rows),
                               "v17_prefix_sha256": dictionary_hash(initial_dictionary),
                               "v18_sha256": dictionary_hash(final_dictionary),
                               "base_glossary_surfaces": len(initial_glossary),
                               "v18_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT641 tests exactly the two reader-exact strict TCH holes exposed by GDT640. "
            "tcheor and chetchy enter V18 only as complete exact surfaces after all seven occurrences are rendered. "
            "No E, OR, CHE, TCH, Y, substring, wrapper, naked body or absent cell is newly globalized. "
            "The readings are replaceable technical-codebook defaults, not confirmed plaintext, phonetics, historical words or a language identification."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = build(ART)
    run, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT641 built: candidates={run['candidates']} accepted={run['accepted']} "
        f"audits={run['audited_occurrences']} complete={coverage['complete_multi_token_lines']} "
        f"strict={coverage['strict_complete_lines']} one_unknown={coverage['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
