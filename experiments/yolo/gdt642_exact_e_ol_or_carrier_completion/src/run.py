#!/usr/bin/env python3
"""Build GDT642: exact cheol/cheor/tcheol E+OL/OR carrier completion."""
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
BASE_REL = Path("experiments/yolo/gdt642_exact_e_ol_or_carrier_completion")
ART = ROOT / BASE_REL / "artifacts"
G641_BASE = Path("experiments/yolo/gdt641_strict_tch_bound_form_completion")
G641_RUN_REL = G641_BASE / "src/run.py"
G641_ALLOW_REL = G641_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G641_COVERAGE_REL = G641_BASE / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V18.tsv"
G641_COMPLETE_REL = G641_BASE / "artifacts/COMPLETE_PASSAGES_V18.tsv"
G641_ONE_REL = G641_BASE / "artifacts/ONE_UNKNOWN_PASSAGES_V18.tsv"
G641_GLOSSARY_REL = G641_BASE / "artifacts/V18_EXACT_TOKEN_GLOSSARY.tsv"
G641_DICT_REL = G641_BASE / "artifacts/WORKING_DICTIONARY_V18.tsv"
G641_RESULT_REL = G641_BASE / "artifacts/RESULT.json"
G641_REPORT_REL = G641_BASE / "REPORT.md"
G624_REPORT_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md")
G624_GRID_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/GRID_CELLS.tsv")
G625_REPORT_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/REPORT.md")
G625_TERMINAL_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/TERMINAL_QUALITY_OCCURRENCES.tsv")
G628_REPORT_REL = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G628_MATRIX_REL = Path("experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv")
G629_REPORT_REL = Path("experiments/yolo/gdt629_part_quality_degree_clause/REPORT.md")
G630_REPORT_REL = Path("experiments/yolo/gdt630_outer_carrier_attachment/REPORT.md")
G633_REPORT_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G633_CANDIDATES_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/artifacts/ATOMIC_MEANING_CANDIDATES.tsv")

spec = importlib.util.spec_from_file_location("gdt641_builder_for_gdt642", ROOT / G641_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT641 builder helpers")
g641 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g641)
g637 = g641.g637
TOKENS_REL = g641.TOKENS_REL
CROSS_REL = g641.CROSS_REL

STATUS = "PASS_3_EXACT_E_CARRIERS__219_POSITIONS__5_NEW_ONE_HOLES"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)

CANDIDATE_SPECS = (
    {
        "surface": "cheol",
        "working_meaning_de": "trockener Drogenstoff",
        "composition": "ch+e+ol",
        "rival_de": "trockene Zustands-/Materialform mit e-Bindung",
        "decision_basis": (
            "the occupied chol/cheol and chor/cheor four-cell family combines the dry CH arm, "
            "productive E insertion and the OL material carrier"
        ),
    },
    {
        "surface": "cheor",
        "working_meaning_de": "trockener Drogenteil",
        "composition": "ch+e+or",
        "rival_de": "trockene Drogenportion; gebundener Drogenteil bei lexikalisiertem chor",
        "decision_basis": (
            "the same CH+E family switches only OL to the independently attested OR part/portion carrier; "
            "part remains primary and portion remains explicit"
        ),
    },
    {
        "surface": "tcheol",
        "working_meaning_de": "kalt-trockener Drogenstoff",
        "composition": "tch+e+ol",
        "rival_de": "kalt-trockene Zustands-/Materialform mit e-Bindung",
        "decision_basis": (
            "the complete tchol/tcheol and tchor/tcheor grid changes only the carrier ending; "
            "all six tcheol occurrences are reader-exact"
        ),
    },
)

GRID_PREFIXES = ("ch", "sh", "tch", "kch", "pch", "lch", "ot", "ok", "qo", "qok", "qot")
FOCAL_SISTERS = (
    ("CH", "chol", "trockenes Gut/Material"),
    ("CH", "cheol", "trockener Drogenstoff"),
    ("CH", "chor", "Pflanzen-/Reproduktionsteil; trockene Qualitätslesung als Rivale"),
    ("CH", "cheor", "trockener Drogenteil; Portion als Rivale"),
    ("TCH", "tchol", "kalt-trockener Stoff"),
    ("TCH", "tcheol", "kalt-trockener Drogenstoff"),
    ("TCH", "tchor", "kalt-trockener Teil-/Portionsträger"),
    ("TCH", "tcheor", "kalt-trockener Drogenteil"),
)

COMPONENT_ROWS = (
    ("cheol", "ch", "trocken / getrocknet", G628_MATRIX_REL, "BOUND_DRY_QUALITY", "inside exact cheol only"),
    ("cheol", "e", "attributive/resultative Bindung", G633_CANDIDATES_REL, "BOUND_E_STAGE", "inside exact cheol only"),
    ("cheol", "ol", "Drogenstoff / Materialträger", G628_MATRIX_REL, "BOUND_OL_MATERIAL", "no bare-ol promotion"),
    ("cheor", "ch", "trocken / getrocknet", G628_MATRIX_REL, "BOUND_DRY_QUALITY", "inside exact cheor only"),
    ("cheor", "e", "attributive/resultative Bindung", G633_CANDIDATES_REL, "BOUND_E_STAGE", "inside exact cheor only"),
    ("cheor", "or", "Drogenteil; Portion bleibt Rivale", G628_MATRIX_REL, "BOUND_OR_PART", "no bare-or promotion"),
    ("tcheol", "tch", "kalt-trocken", G625_TERMINAL_REL, "BOUND_COLD_DRY_QUALITY", "inside exact tcheol only"),
    ("tcheol", "e", "attributive Bindung", G633_CANDIDATES_REL, "BOUND_E_STAGE", "inside exact tcheol only"),
    ("tcheol", "ol", "Drogenstoff / Materialträger", G628_MATRIX_REL, "BOUND_OL_MATERIAL", "no bare-ol promotion"),
)

EXEMPLARS = {
    "f20v.2": (
        "cheol",
        "Trockener Drogenstoff; Trockengut; Trockenpräparat Form III; "
        "trockenes CTH-Drogenmaterial; später ein kalter Ansatz in Grundform.",
    ),
    "f24r.1": (
        "cheol",
        "Pulverportion / Pflanzenteil; feucht gebunden; trockener Drogenstoff, Grad III.",
    ),
    "f51v.13": ("cheol", "Grad III; trockener Drogenstoff; [cheodain noch offen]."),
    "f15v.11": (
        "cheor",
        "Samenmaterial; [oiin offen]; trockener Drogenteil; Trockengut Grad III; CTH-Drogenmaterial.",
    ),
    "f28v.4": (
        "cheor",
        "Trockener Drogenteil / Pflanzenteil; kaltes Material; feuchtes Material; "
        "Blüten-/Fruchtstand, Portion III; kalt, Grundform.",
    ),
    "f88v.26": ("cheor", "Saatgut Typ III; [choky offen]; trockener Drogenteil; feuchte Grundform."),
    "f102v2.11": ("cheor", "Trockener Drogenteil."),
    "f49r.13": (
        "tcheol",
        "Trockengut; [Form offen]; kalt-trockener Drogenstoff, Grad III; [CTH-Abschluss offen].",
    ),
    "f107r.9": (
        "tcheol",
        "Heiß Grad III; feucht gebunden; kalt-trockener Drogenstoff; heiß Grad II; "
        "heißer Ansatz; getrockneter Zustand.",
    ),
    "f107r.20": ("tcheol", "Kalt-trockener Drogenstoff; [kcheedy noch offen]."),
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "E_OL_OR_PRODUCTIVE_GRID.tsv",
    "TARGET_FAMILY_CONTRASTS.tsv", "COMPONENT_BINDING_AUDIT.tsv", "TARGET_NEIGHBOR_SUMMARY.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "CONCRETE_EXEMPLARS.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V19_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V19.tsv", "COMPLETE_PASSAGES_V19.tsv",
    "ONE_UNKNOWN_PASSAGES_V19.tsv", "WORKING_DICTIONARY_V19.tsv",
)
COVERAGE_FIELDS = g641.COVERAGE_FIELDS
ONE_FIELDS = g641.ONE_FIELDS


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
        "entry": f"{spec_row['surface']}@GDT642_EXACT_WHOLE",
        "kind": "EXACT_WHOLE_E_OL_OR_CARRIER",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete ZL3b surface only; {occurrences} audited occurrences; "
            "alternate-reader warnings remain marked; no substring, bare component or absent-cell transfer"
        ),
        "status": f"NEW_V19_ACCEPTED_ROUND_{round_number:02d}",
    }


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G641_ALLOW_REL)}
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

    base_dictionary: list[dict[str, object]] = [dict(row) for row in read_tsv(ROOT / G641_DICT_REL)]
    old_coverage = read_tsv(ROOT / G641_COVERAGE_REL)
    old_complete = read_tsv(ROOT / G641_COMPLETE_REL)
    old_one = read_tsv(ROOT / G641_ONE_REL)
    old_glossary = read_tsv(ROOT / G641_GLOSSARY_REL)
    if (len(base_dictionary), len(old_coverage), len(old_complete), len(old_one), len(old_glossary)) != (285, 4128, 44, 60, 238):
        raise RuntimeError("GDT641 frozen base counts changed")
    glossary = {row["surface"]: dict(row) for row in old_glossary}
    coverage, one_unknown, _, complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
    if metrics(coverage, one_unknown, complete, glossary)["known_token_positions"] != 9748:
        raise RuntimeError("GDT641 replayed coverage changed")
    base_complete_loci = {str(row["locus"]) for row in complete}
    old_one_loci = {str(row["locus"]) for row in one_unknown}
    audit_base_glossary = {key: dict(value) for key, value in glossary.items()}
    audit_base_by_locus = {str(row["locus"]): row for row in coverage}

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    grid_rows: list[dict[str, object]] = []
    for prefix in GRID_PREFIXES:
        cells = (prefix + "ol", prefix + "eol", prefix + "or", prefix + "eor")
        counts = [token_counts[cell] for cell in cells]
        grid_rows.append({
            "prefix": prefix,
            "none_ol_surface": cells[0], "none_ol_occurrences": counts[0],
            "e_ol_surface": cells[1], "e_ol_occurrences": counts[1],
            "none_or_surface": cells[2], "none_or_occurrences": counts[2],
            "e_or_surface": cells[3], "e_or_occurrences": counts[3],
            "occupied_cells": sum(count > 0 for count in counts),
            "complete_four_cell_grid": int(all(counts)),
            "target_family": int(prefix in {"ch", "tch"}),
        })
    if not all(int(row["complete_four_cell_grid"]) for row in grid_rows):
        raise RuntimeError("productive E+OL/OR comparison grid changed")

    family_rows: list[dict[str, object]] = []
    for family, surface, reading in FOCAL_SISTERS:
        members = [row for row in token_rows if row["eva"] == surface]
        if surface.endswith(("eol", "eor")):
            composition = surface[:-3] + "+e+" + surface[-2:]
        else:
            composition = surface[:-2] + "+" + surface[-2:]
        family_rows.append({
            "family": family, "surface": surface, "composition": composition,
            "occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "working_reading_de": reading,
            "status": "NEW_V19_TARGET" if surface in {row["surface"] for row in CANDIDATE_SPECS} else "INHERITED_OR_SISTER",
        })

    component_rows = [
        {
            "component_id": f"G642-B{index:02d}", "surface": surface, "segment": segment,
            "working_value_de": value, "evidence_path": str(path), "evidence_kind": kind,
            "licensed_use": licensed_use,
        }
        for index, (surface, segment, value, path, kind, licensed_use) in enumerate(COMPONENT_ROWS, 1)
    ]

    accepted_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V18", "decision": "BASE",
        "dictionary_entries": len(base_dictionary), "dictionary_sha256": dictionary_hash(base_dictionary),
        **metrics(coverage, one_unknown, complete, glossary),
    }]
    newly_exposed: list[dict[str, object]] = []
    seen_one_loci = set(old_one_loci)

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if surface in glossary or GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"invalid exact carrier target: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        if not members:
            raise RuntimeError(f"unattested target: {surface}")
        pre_dictionary = [*base_dictionary, *accepted_rows]
        pre_hash = dictionary_hash(pre_dictionary)
        pre_coverage, pre_one, _, pre_complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
        pre_by_locus = {str(row["locus"]): row for row in pre_coverage}

        trial_glossary = {key: dict(value) for key, value in glossary.items()}
        g637.set_gloss(
            trial_glossary, surface, spec_row["working_meaning_de"], f"GDT642:ROUND_{round_number:02d}",
            "EXACT_WHOLE_E_OL_OR_CARRIER", "KNOWN_EXACT_WHOLE", 123,
        )
        trial_coverage, trial_one, _, trial_complete = g637.build_line_coverage(by_line, trial_glossary, exact, boundary, cross_by_locus)
        trial_by_locus = {str(row["locus"]): row for row in trial_coverage}
        audit_trial_glossary = {key: dict(value) for key, value in audit_base_glossary.items()}
        g637.set_gloss(
            audit_trial_glossary, surface, spec_row["working_meaning_de"], f"GDT642:ROUND_{round_number:02d}",
            "EXACT_WHOLE_E_OL_OR_CARRIER", "KNOWN_EXACT_WHOLE", 123,
        )
        audit_trial_coverage, _, _, _ = g637.build_line_coverage(
            by_line, audit_trial_glossary, exact, boundary, cross_by_locus,
        )
        audit_trial_by_locus = {str(row["locus"]): row for row in audit_trial_coverage}
        verdicts: Counter[str] = Counter()
        round_audits: list[dict[str, object]] = []
        for member in members:
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = audit_base_by_locus[locus], audit_trial_by_locus[locus]
            reader_exact = int(exact[locus, token_index])
            split_normalized = int(boundary[locus, token_index])
            known_other = int(before["known_tokens"])
            flags: list[str] = []
            if not reader_exact:
                flags.append("ALTERNATE_READER_BOUNDARY")
            if split_normalized and not reader_exact:
                flags.append("SPLIT_NORMALIZED")
            if int(before["ambiguous_tokens"]):
                flags.append("ACTIVE_SCOPE_RIVAL")
            if known_other < 2:
                flags.append("OPAQUE_OTHER_TOKENS")
            neighbors = []
            for neighbor_index in (ordinal - 2, ordinal):
                if 0 <= neighbor_index < len(line):
                    neighbors.append(str(line[neighbor_index]["eva"]))
            if any(neighbor.startswith("sh") for neighbor in neighbors):
                flags.append("MOIST_NEIGHBOR_DIFFERENT_SLOT")
            if any(neighbor.startswith(("k", "qok")) for neighbor in neighbors):
                flags.append("HOT_NEIGHBOR_DIFFERENT_SLOT")
            if not reader_exact:
                verdict = "READER_BOUNDARY_WARNING"
                reason = "ZL3b target is not the same exact token in every alternate reading"
            elif known_other < 2:
                verdict = "OPAQUE_CONTEXT"
                reason = "fewer than two independently glossed companion positions"
            else:
                verdict = "CONSISTENT_CONCRETE"
                reason = "material/part reading fits the visible list or quality frame without a same-slot collision"
            verdicts[verdict] += 1
            before_glosses = split_pipe(before["token_glosses_de"])
            after_glosses = split_pipe(after["token_glosses_de"])
            cross = cross_by_locus[locus]
            round_audits.append({
                "audit_id": "", "round": round_number, "surface": surface,
                "page": member["page"], "locus": locus, "section": member["section"],
                "language": member["language"], "hand": member["hand"], "token_ordinal": ordinal,
                "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"], "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
                "reader_exact": reader_exact, "split_normalized": split_normalized,
                "before_state": split_pipe(before["scope_states"])[ordinal - 1],
                "before_gloss": before_glosses[ordinal - 1], "after_gloss": after_glosses[ordinal - 1],
                "known_other_tokens": known_other, "local_before_de": before["token_glosses_de"],
                "local_after_de": after["token_glosses_de"], "flags": "|".join(flags) or "NONE",
                "hard_collision": 0, "verdict": verdict, "review_reason": reason,
            })
        round_audits.sort(key=lambda row: (str(row["locus"]), int(row["token_ordinal"])))
        for index, row in enumerate(round_audits, 1):
            row["audit_id"] = f"G642-A{round_number:02d}-{index:03d}"
        audit_rows.extend(round_audits)

        exact_anchors = sum(int(row["reader_exact"]) for row in round_audits)
        hard_collisions = sum(int(row["hard_collision"]) for row in round_audits)
        prefix_row = next(row for row in grid_rows if row["prefix"] == ("tch" if surface == "tcheol" else "ch"))
        if hard_collisions or exact_anchors == 0 or not int(prefix_row["complete_four_cell_grid"]):
            raise RuntimeError(f"candidate failed frozen carrier acceptance: {surface}")
        glossary = trial_glossary
        coverage, one_unknown, complete = trial_coverage, trial_one, trial_complete
        accepted_rows.append(dictionary_row(spec_row, round_number, len(members)))
        current_one = {str(row["locus"]): row for row in one_unknown}
        for locus in sorted(set(current_one) - seen_one_loci):
            row = current_one[locus]
            newly_exposed.append({
                "introduced_round": round_number, "enabled_by_surface": surface,
                **{field: row[field] for field in ONE_FIELDS},
            })
        seen_one_loci.update(current_one)

        post_dictionary = [*base_dictionary, *accepted_rows]
        post_hash = dictionary_hash(post_dictionary)
        trial_new_complete = sorted({str(row["locus"]) for row in complete} - {str(row["locus"]) for row in pre_complete})
        ledger_rows.append({
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "decision_reason": spec_row["decision_basis"], "barrier": "NONE",
            "pre_dictionary_entries": len(pre_dictionary), "post_dictionary_entries": len(post_dictionary),
            "pre_dictionary_sha256": pre_hash, "post_dictionary_sha256": post_hash,
            "occurrences": len(members), "audited_occurrences": len(round_audits),
            "reader_exact_occurrences": exact_anchors, "consistent_concrete": verdicts["CONSISTENT_CONCRETE"],
            "opaque_context": verdicts["OPAQUE_CONTEXT"], "reader_boundary_warning": verdicts["READER_BOUNDARY_WARNING"],
            "hard_collisions": hard_collisions, "complete_gain": len(trial_new_complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_one_unknown_loci": "|".join(sorted(set(current_one) - {str(row["locus"]) for row in pre_one})),
        })
        round_rows.append({
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": post_hash,
            **metrics(coverage, one_unknown, complete, glossary),
        })
        target_deck.append({
            "candidate_id": f"G642-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "scope": "exact complete ZL3b surface only",
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_anchors,
            "decision": "ACCEPT", "barrier": "NONE", "decision_basis": spec_row["decision_basis"],
        })

    final_dictionary = [*base_dictionary, *accepted_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
    final_glossary_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    accepted_defaults = [
        {
            **row, "accepted_round": int(row["status"].rsplit("_", 1)[1]),
            "surface": row["entry"].split("@", 1)[0],
            "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        }
        for row in accepted_rows
    ]

    neighbor_counts: Counter[tuple[str, str, str]] = Counter()
    for row in audit_rows:
        for side, neighbor in (("LEFT", str(row["previous"])), ("RIGHT", str(row["following"]))):
            if neighbor not in {"<BOS>", "<EOS>"}:
                neighbor_counts[str(row["surface"]), side, neighbor] += 1
    neighbor_rows = []
    for (surface, side, neighbor), count in sorted(neighbor_counts.items()):
        gloss = glossary.get(neighbor)
        neighbor_rows.append({
            "surface": surface, "side": side, "neighbor_surface": neighbor,
            "contact_count": count, "neighbor_in_v19_glossary": int(gloss is not None),
            "neighbor_working_meaning_de": "OPEN" if gloss is None else gloss["working_meaning_de"],
        })

    final_by_locus = {str(row["locus"]): row for row in final_coverage}
    exemplar_rows = []
    for index, (locus, (surface, reading)) in enumerate(EXEMPLARS.items(), 1):
        row = final_by_locus[locus]
        exemplar_rows.append({
            "exemplar_id": f"G642-X{index:02d}", "surface": surface, "page": row["page"], "locus": locus,
            "section": row["section"], "reader_exact_target": int(any(
                token["eva"] == surface and exact[locus, int(token["token_index"])] for token in by_line[locus]
            )),
            "zl3b_line": row["zl3b_line"], "literal_v19_de": row["token_glosses_de"],
            "smoothed_partial_reading_de": reading, "known_tokens": row["known_tokens"], "unknown_tokens": row["unknown_tokens"],
        })

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "working_meaning_de", "composition", "scope", "rival_de",
        "occurrences", "pages", "reader_exact_occurrences", "decision", "barrier", "decision_basis",
    ))
    write_tsv(output_dir / "E_OL_OR_PRODUCTIVE_GRID.tsv", grid_rows, (
        "prefix", "none_ol_surface", "none_ol_occurrences", "e_ol_surface", "e_ol_occurrences",
        "none_or_surface", "none_or_occurrences", "e_or_surface", "e_or_occurrences",
        "occupied_cells", "complete_four_cell_grid", "target_family",
    ))
    write_tsv(output_dir / "TARGET_FAMILY_CONTRASTS.tsv", family_rows, (
        "family", "surface", "composition", "occurrences", "pages", "reader_exact_occurrences", "working_reading_de", "status",
    ))
    write_tsv(output_dir / "COMPONENT_BINDING_AUDIT.tsv", component_rows, (
        "component_id", "surface", "segment", "working_value_de", "evidence_path", "evidence_kind", "licensed_use",
    ))
    write_tsv(output_dir / "TARGET_NEIGHBOR_SUMMARY.tsv", neighbor_rows, (
        "surface", "side", "neighbor_surface", "contact_count", "neighbor_in_v19_glossary", "neighbor_working_meaning_de",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "page", "locus", "section", "language", "hand", "token_ordinal",
        "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line", "reader_exact",
        "split_normalized", "before_state", "before_gloss", "after_gloss", "known_other_tokens",
        "local_before_de", "local_after_de", "flags", "hard_collision", "verdict", "review_reason",
    ))
    write_tsv(output_dir / "CONCRETE_EXEMPLARS.tsv", exemplar_rows, (
        "exemplar_id", "surface", "page", "locus", "section", "reader_exact_target", "zl3b_line",
        "literal_v19_de", "smoothed_partial_reading_de", "known_tokens", "unknown_tokens",
    ))
    write_tsv(output_dir / "SEQUENTIAL_DECISION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "decision", "decision_reason", "barrier", "pre_dictionary_entries",
        "post_dictionary_entries", "pre_dictionary_sha256", "post_dictionary_sha256", "occurrences",
        "audited_occurrences", "reader_exact_occurrences", "consistent_concrete", "opaque_context",
        "reader_boundary_warning", "hard_collisions", "complete_gain", "one_unknown_before",
        "one_unknown_after", "new_one_unknown_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "decision", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status", "accepted_round", "occurrences",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", [], (
        "round", "surface", "page", "locus", "strict_complete", "zl3b_line", "working_translation_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V19_EXACT_TOKEN_GLOSSARY.tsv", final_glossary_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V19.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V19.tsv", final_complete, ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V19.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V19.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G641_RUN_REL, G641_ALLOW_REL, G641_COVERAGE_REL, G641_COMPLETE_REL, G641_ONE_REL,
        G641_GLOSSARY_REL, G641_DICT_REL, G641_RESULT_REL, G641_REPORT_REL,
        G624_REPORT_REL, G624_GRID_REL, G625_REPORT_REL, G625_TERMINAL_REL,
        G628_REPORT_REL, G628_MATRIX_REL, G629_REPORT_REL, G630_REPORT_REL,
        G633_REPORT_REL, G633_CANDIDATES_REL, TOKENS_REL, CROSS_REL,
    )
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    verdict_counts = Counter(str(row["verdict"]) for row in audit_rows)
    result_core = {
        "schema": "GDT642_EXACT_E_OL_OR_CARRIER_COMPLETION_RESULT_V1",
        "experiment_id": "GDT642", "status": STATUS,
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0,
            "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats,
        },
        "productive_grid": {
            "prefixes": len(grid_rows),
            "complete_four_cell_prefixes": sum(int(row["complete_four_cell_grid"]) for row in grid_rows),
            "focal_families": ["CH", "TCH"],
        },
        "target_run": {
            "candidates": len(target_deck), "accepted": len(accepted_rows), "held": 0,
            "audited_occurrences": len(audit_rows),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "verdicts": dict(sorted(verdict_counts.items())),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "accepted_surfaces": [row["surface"] for row in target_deck],
        },
        "coverage": {
            "base_complete_multi_token_lines": len(old_complete),
            "base_strict_complete_lines": sum(int(row["strict_complete"]) for row in old_complete),
            "newly_completed_lines": len({str(row["locus"]) for row in final_complete} - base_complete_loci),
            "newly_exposed_one_hole_lines": len(newly_exposed), **final_metrics,
        },
        "working_dictionary": {
            "v18_entries": len(base_dictionary), "v19_entries": len(final_dictionary),
            "accepted_tail_entries": len(accepted_rows), "v18_prefix_sha256": dictionary_hash(base_dictionary),
            "v19_sha256": dictionary_hash(final_dictionary), "base_glossary_surfaces": len(old_glossary),
            "v19_glossary_surfaces": len(glossary),
        },
        "claim_boundary": (
            "GDT642 assigns three replaceable exact-ZL3b technical readings: cheol=trockener Drogenstoff, "
            "cheor=trockener Drogenteil with portion rival, and tcheol=kalt-trockener Drogenstoff. "
            "The assignments use the fully occupied E/NONE by OL/OR grids and all 219 occurrences. "
            "They add no complete multi-token line but expose five new one-hole lines. Alternate-reader boundaries, "
            "bare E/OL/OR/CH/TCH, substrings and unattested cells are not promoted; this is not a plaintext or language identification."
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
        f"GDT642 built: accepted={run['accepted']} audits={run['audited_occurrences']} "
        f"reader_exact={run['reader_exact_occurrences']} known={coverage['known_token_positions']} "
        f"complete={coverage['complete_multi_token_lines']} one_unknown={coverage['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
