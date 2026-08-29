#!/usr/bin/env python3
"""Build GDT640: test the four strict holes newly exposed by GDT639."""
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
BASE_REL = Path("experiments/yolo/gdt640_downstream_component_prediction")
ART = ROOT / BASE_REL / "artifacts"
G639_BASE = Path("experiments/yolo/gdt639_strict_hole_component_repair")
G639_RUN_REL = G639_BASE / "src/run.py"
G639_ALLOW_REL = G639_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G639_ONE_REL = G639_BASE / "artifacts/ONE_UNKNOWN_PASSAGES_V16.tsv"
G639_COVERAGE_REL = G639_BASE / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V16.tsv"
G639_COMPLETE_REL = G639_BASE / "artifacts/COMPLETE_PASSAGES_V16.tsv"
G639_GLOSSARY_REL = G639_BASE / "artifacts/V16_EXACT_TOKEN_GLOSSARY.tsv"
G639_DICT_REL = G639_BASE / "artifacts/WORKING_DICTIONARY_V16.tsv"
G639_RESULT_REL = G639_BASE / "artifacts/RESULT.json"
G639_REPORT_REL = G639_BASE / "REPORT.md"
G625_REPORT_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/REPORT.md")
G625_TERMINAL_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/TERMINAL_QUALITY_OCCURRENCES.tsv")
G627_REPORT_REL = Path("experiments/yolo/gdt627_value_head_role_atlas/REPORT.md")
G628_REPORT_REL = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G628_MATRIX_REL = Path("experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv")
G633_REPORT_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G634_REPORT_REL = Path("experiments/yolo/gdt634_known_core_terminal_semantics/REPORT.md")
G636_REPORT_REL = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt639_builder_for_gdt640", ROOT / G639_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT639 builder helpers")
g639 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g639)
g637 = g639.g637
TOKENS_REL = g639.TOKENS_REL
CROSS_REL = g639.CROSS_REL

STATUS = "PASS_3_DOWNSTREAM_EXACT_DEFAULTS__3_NEW_COMPLETE_LINES__1_CONCRETE_HOLD"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|führe .* aus|leite .* weiter",
    re.IGNORECASE,
)

# GDT639 fixed these four surfaces before any GDT640 occurrence audit. The
# first card remains a concrete reading but is held because internal m has no
# independent value; the other three are complete exact-surface transfers.
CANDIDATE_SPECS = (
    {
        "surface": "qotomody", "source_locus": "f37r.6", "decision": "HOLD",
        "working_meaning_de": "kaltes Ansatzmaß, fertig aufbereitete Grundform",
        "composition": "qot+o+m+ody", "scope": "singleton exact whole surface only",
        "rival_de": "gelernte Ganzform qotom plus fertig aufbereitete Grundform",
        "decision_basis": "qot and ody bind, but internal m lacks an independent nonterminal value",
        "barrier": "INTERNAL_M_ROLE_UNBOUND",
    },
    {
        "surface": "qotor", "source_locus": "f37v.16", "decision": "ACCEPT",
        "working_meaning_de": "kalte Drogenportion",
        "composition": "qo+t+or", "scope": "exact whole surface only",
        "rival_de": "kalter Teil-/Nominalträger",
        "decision_basis": "observed qotol/qotor OL-OR pair and the inherited cold qo+t plus OR part carrier",
        "barrier": "NONE",
    },
    {
        "surface": "okal", "source_locus": "f25r.6", "decision": "ACCEPT",
        "working_meaning_de": "Ansatz aus heißem Rohstoff, Form I",
        "composition": "o+k+al", "scope": "exact whole surface only",
        "rival_de": "heißer Ansatz mit Rohstoffträger",
        "decision_basis": "complete o/qo by k/t by al/ar grid; exact okal only, with no bare-al globalization",
        "barrier": "NONE",
    },
    {
        "surface": "chotcheol", "source_locus": "f49r.11", "decision": "ACCEPT",
        "working_meaning_de": "Trockenansatz aus kalt-trockenem Drogenstoff",
        "composition": "cho+tch+e+ol", "scope": "singleton exact whole surface only",
        "rival_de": "kalter Trockenansatz aus Trockengut",
        "decision_basis": "GDT625 binds the complete internal tch cold-dry block under prefix cho; e plus ol supplies attributed drug material",
        "barrier": "NONE",
    },
)

FAMILY_FORMS = (
    ("QO_KT_OL_OR", "qokol", "heißes Material im qo-Rahmen"),
    ("QO_KT_OL_OR", "qokor", "heiße Portion im qo-Rahmen"),
    ("QO_KT_OL_OR", "qotol", "kaltes Material im qo-Rahmen"),
    ("QO_KT_OL_OR", "qotor", "kalte Portion im qo-Rahmen"),
    ("QO_KTCH_OL_OR", "qokchol", "heiß-trockenes Material"),
    ("QO_KTCH_OL_OR", "qokchor", "heiß-trockene Portion"),
    ("QO_KTCH_OL_OR", "qotchol", "kalt-trockenes Material"),
    ("QO_KTCH_OL_OR", "qotchor", "kalt-trockene Portion"),
    ("O_QO_KT_AL_AR", "okal", "Ansatz aus heißem Rohstoff, Form I"),
    ("O_QO_KT_AL_AR", "okar", "heiße Zubereitungsfraktion I"),
    ("O_QO_KT_AL_AR", "otal", "kalter Zubereitungsrohstoff I"),
    ("O_QO_KT_AL_AR", "otar", "kalte Zubereitungsfraktion I"),
    ("O_QO_KT_AL_AR", "qokal", "heißer Rohstoff im qo-Rahmen"),
    ("O_QO_KT_AL_AR", "qokar", "heiße Fraktion im qo-Rahmen"),
    ("O_QO_KT_AL_AR", "qotal", "kalter Rohstoff im qo-Rahmen"),
    ("O_QO_KT_AL_AR", "qotar", "kalte Fraktion im qo-Rahmen"),
    ("CHOT_INNER_FORM", "chotchy", "Trockenansatz, kalt-trockene Grundform"),
    ("CHOT_INNER_FORM", "chotchey", "Trockenansatz, kalt-trocken gebundene Form I"),
    ("CHOT_INNER_FORM", "chotcheey", "Trockenansatz, kalt-trocken gebundene Form II"),
    ("CHOT_INNER_FORM", "chotcheol", "Trockenansatz aus kalt-trockenem Drogenstoff"),
    ("QOTOMODY_NEIGHBOUR", "qotom", "kalter Ansatz mit terminalem m"),
    ("QOTOMODY_NEIGHBOUR", "qotody", "kalte fertig aufbereitete Grundform"),
    ("QOTOMODY_NEIGHBOUR", "qotokody", "kalter Ansatz mit k-ody Innenform"),
    ("QOTOMODY_NEIGHBOUR", "qotomody", "kaltes Ansatzmaß, fertig aufbereitete Grundform"),
)

COMPONENT_ROWS = (
    ("qotomody", "qot+o", "kalter Ansatz im qo-Rahmen", str(G633_REPORT_REL), "COLD_PREPARATION_FRAME", "inside exact qotomody only"),
    ("qotomody", "m", "Einheits-/Abschlussmarker, genaue interne Rolle offen", str(G634_REPORT_REL), "UNBOUND_INTERNAL_MARKER", "forces HOLD"),
    ("qotomody", "ody", "fertig aufbereitete Grundform", str(G636_REPORT_REL), "PREPARED_RESULT_FORM", "inside exact qotomody only"),
    ("qotor", "qo+t", "kalt im qo-Rahmen", str(G628_MATRIX_REL), "BOUND_COLD_QO_FRAME", "inside exact qotor only"),
    ("qotor", "or", "Teil-/Nominalträger; praktisch Drogenportion", str(G628_REPORT_REL), "BOUND_OR_CARRIER", "no bare-or promotion"),
    ("okal", "o+k", "heißer Zubereitungs-/Ansatzrahmen", str(G633_REPORT_REL), "HOT_PREPARATION_FRAME", "inside exact okal only"),
    ("okal", "al", "Rohstoffform I", str(G636_REPORT_REL), "SCOPED_RAW_MATERIAL_BODY", "no bare-al promotion"),
    ("chotcheol", "cho", "Trockenansatz", str(G633_REPORT_REL), "DRY_PREPARATION_PREFIX", "inside exact chotcheol only"),
    ("chotcheol", "tch", "kalt-trocken", str(G625_TERMINAL_REL), "BOUND_TCH_QUALITY_BLOCK", "inside exact chotcheol only"),
    ("chotcheol", "e+ol", "attributiv gebundener Drogenstoff", str(G628_REPORT_REL), "ATTRIBUTIVE_MATERIAL_CARRIER", "no cheol or substring promotion"),
)

SMOOTHED_NEW_LINES = {
    "f37v.16": "Kalte Drogenportion; Menge/Portion III; trockene Zubereitung: kalt, Grad III.",
    "f25r.6": "Ansatz aus heißem Rohstoff, Form I; trockene Zubereitung: kalt, Grad III.",
    "f49r.11": "Trockenansatz aus kalt-trockenem Drogenstoff; Maß trockenen Materials.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_PREDICTION_DECK.tsv", "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "SEQUENTIAL_DECISION_LEDGER.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "HELD_TARGET_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "V17_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V17.tsv", "COMPLETE_PASSAGES_V17.tsv",
    "ONE_UNKNOWN_PASSAGES_V17.tsv", "WORKING_DICTIONARY_V17.tsv",
)
COVERAGE_FIELDS = g639.COVERAGE_FIELDS
ONE_FIELDS = g639.ONE_FIELDS


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
        "entry": f"{spec_row['surface']}@GDT640_EXACT_WHOLE",
        "kind": "EXACT_WHOLE_SURFACE_DOWNSTREAM_PREDICTION",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; {occurrences} audited occurrences; {spec_row['scope']}; "
            "no substring, naked-body, wrapper or absent-cell transfer"
        ),
        "status": f"NEW_V17_ACCEPTED_ROUND_{round_number:02d}",
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
        context_fraction = known_other / other_positions
        flags: list[str] = []
        if not exact[locus, token_index]:
            flags.append("READER_SPLIT_OR_FUSION")
        if int(before["ambiguous_tokens"]):
            flags.append("ACTIVE_RIVAL_CONTEXT")
        if known_other < 2 and not (other_positions == 1 and known_other == 1):
            flags.append("OPAQUE_OTHER_TOKENS")
        if surface == "qotomody":
            flags.append("INTERNAL_M_ROLE_UNBOUND")
        elif surface == "qotor":
            flags.append("OR_COMPONENT_EXACT_ONLY")
        elif surface == "okal":
            flags.append("AL_COMPONENT_EXACT_ONLY")
        elif surface == "chotcheol":
            flags.append("DOUBLE_DRY_SCOPE_EXACT_ONLY")
        if not exact[locus, token_index]:
            verdict = "READER_BOUNDARY_WARNING"
            reason = "target surface is split, fused or changed in at least one alternate reading"
        elif spec_row["decision"] == "HOLD":
            verdict = "UNBOUND_COMPONENT"
            reason = "the complete reading is concrete, but internal m has no independent nonterminal value"
        elif known_other < 2 and not (other_positions == 1 and known_other == 1):
            verdict = "OPAQUE_CONTEXT"
            reason = "too few independently concrete neighbouring positions to test the complete noun phrase"
        else:
            verdict = "CONSISTENT_CONCRETE"
            reason = "all visible candidate fields remain present and no opposite bound component is introduced"
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
            "reader_exact": exact[locus, token_index], "split_normalized": boundary[locus, token_index],
            "before_state": before_states[ordinal - 1], "before_gloss": before_glosses[ordinal - 1],
            "after_gloss": after_glosses[ordinal - 1],
            "known_other_tokens": known_other, "other_token_positions": other_positions,
            "context_fraction": f"{context_fraction:.6f}",
            "local_before_de": before["token_glosses_de"], "local_after_de": after["token_glosses_de"],
            "flags": "|".join(flags) if flags else "NONE", "verdict": verdict,
            "review_reason": reason,
        })
    rows.sort(key=lambda row: (str(row["locus"]), int(row["token_ordinal"])))
    for index, row in enumerate(rows, 1):
        row["audit_id"] = f"G640-A{round_number:02d}-{index:03d}"
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G639_ALLOW_REL)}
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

    base_one = read_tsv(ROOT / G639_ONE_REL)
    target_surfaces = {str(row["surface"]) for row in CANDIDATE_SPECS}
    target_rows = [
        row for row in base_one
        if int(row["strict_eligible"]) and row["unknown_surface"] in target_surfaces
    ]
    target_by_surface = {row["unknown_surface"]: row for row in target_rows}
    if len(target_rows) != 4 or set(target_by_surface) != target_surfaces:
        raise RuntimeError("GDT639 downstream target frontier changed")
    for spec_row in CANDIDATE_SPECS:
        if target_by_surface[str(spec_row["surface"])]["locus"] != spec_row["source_locus"]:
            raise RuntimeError(f"source locus drift: {spec_row['surface']}")

    v16_dictionary: list[dict[str, object]] = [dict(row) for row in read_tsv(ROOT / G639_DICT_REL)]
    old_coverage = read_tsv(ROOT / G639_COVERAGE_REL)
    old_complete = read_tsv(ROOT / G639_COMPLETE_REL)
    old_glossary = read_tsv(ROOT / G639_GLOSSARY_REL)
    if len(v16_dictionary) != 280 or len(old_coverage) != 4128 or len(old_complete) != 39 or len(old_glossary) != 233:
        raise RuntimeError("GDT639 frozen base count changed")
    glossary = {row["surface"]: dict(row) for row in old_glossary}
    initial_glossary = {surface: dict(row) for surface, row in glossary.items()}
    initial_dictionary = [dict(row) for row in v16_dictionary]
    coverage, one_unknown, _, complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    if len(coverage) != 4128 or len(complete) != 39 or len(one_unknown) != 62:
        raise RuntimeError("replayed V16 reader count changed")
    base_complete_loci = {str(row["locus"]) for row in complete}

    all_members = Counter(row["eva"] for row in token_rows)
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
        {
            "component_id": f"G640-B{index:02d}", "surface": surface, "segment": segment,
            "working_value_de": value, "evidence_path": evidence_path,
            "evidence_kind": kind, "licensed_use": licensed_use,
        }
        for index, (surface, segment, value, evidence_path, kind, licensed_use)
        in enumerate(COMPONENT_ROWS, 1)
    ]

    accepted_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = []
    new_complete_rows: list[dict[str, object]] = []
    held_rows: list[dict[str, object]] = []
    base_metrics = metrics(coverage, one_unknown, complete, glossary)
    round_rows.append({
        "round": 0, "surface": "BASE_V16", "decision": "BASE",
        "dictionary_entries": len(v16_dictionary), "dictionary_sha256": dictionary_hash(v16_dictionary),
        **base_metrics,
    })

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if surface in glossary or GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"invalid downstream surface: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        pre_dictionary = [*v16_dictionary, *accepted_rows]
        pre_hash = dictionary_hash(pre_dictionary)
        pre_coverage, pre_one, _, pre_complete = g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        pre_by_locus = {str(row["locus"]): row for row in pre_coverage}
        pre_complete_loci = {str(row["locus"]) for row in pre_complete}
        pre_strict_loci = {str(row["locus"]) for row in pre_complete if int(row["strict_complete"])}

        trial_glossary = {key: dict(value) for key, value in glossary.items()}
        g637.set_gloss(
            trial_glossary, surface, spec_row["working_meaning_de"], f"GDT640:ROUND_{round_number:02d}",
            "EXACT_WHOLE_SURFACE_DOWNSTREAM_PREDICTION", "KNOWN_EXACT_WHOLE", 121,
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
        source_completed = spec_row["source_locus"] in trial_new_strict
        decision = spec_row["decision"]
        if not trial_new or not source_completed or not exact_anchors:
            raise RuntimeError(f"downstream trial does not close its frozen source: {surface}")
        if decision == "ACCEPT":
            if verdicts["HARD_CONTRADICTION"] or verdicts["NONSENSE"] or verdicts["UNBOUND_COMPONENT"]:
                raise RuntimeError(f"accepted downstream trial has a blocking verdict: {surface}")
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
                    "scope_clean": int(
                        int(after["ambiguous_tokens"]) == 0 and int(after["reader_unstable_tokens"]) == 0
                    ),
                })
        elif decision == "HOLD":
            held_rows.append({
                "surface": surface, "source_locus": spec_row["source_locus"],
                "default_meaning_de": spec_row["working_meaning_de"],
                "composition": spec_row["composition"], "occurrences": len(members),
                "reader_exact_occurrences": exact_anchors, "decision": "HOLD",
                "barrier": spec_row["barrier"], "rival_de": spec_row["rival_de"],
                "trial_complete_loci": "|".join(trial_new),
                "status": "CONCRETE_DEFAULT_RETAINED_OUTSIDE_V17",
            })
        else:
            raise RuntimeError(f"unknown decision: {decision}")

        post_dictionary = [*v16_dictionary, *accepted_rows]
        post_hash = dictionary_hash(post_dictionary)
        post_metrics = metrics(coverage, one_unknown, complete, glossary)
        ledger_rows.append({
            "round": round_number, "surface": surface, "decision": decision,
            "decision_reason": spec_row["decision_basis"], "barrier": spec_row["barrier"],
            "pre_dictionary_entries": len(pre_dictionary), "post_dictionary_entries": len(post_dictionary),
            "pre_dictionary_sha256": pre_hash, "post_dictionary_sha256": post_hash,
            "occurrences": len(members), "audited_occurrences": len(candidate_audit),
            "reader_exact_occurrences": exact_anchors,
            "consistent_concrete": verdicts["CONSISTENT_CONCRETE"],
            "opaque_context": verdicts["OPAQUE_CONTEXT"],
            "reader_boundary_warning": verdicts["READER_BOUNDARY_WARNING"],
            "unbound_component": verdicts["UNBOUND_COMPONENT"],
            "trial_complete_gain": len(trial_new), "trial_strict_complete_gain": len(trial_new_strict),
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "strict_complete_before": len(pre_strict_loci),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "trial_new_complete_loci": "|".join(trial_new),
            "accepted_new_complete_loci": "|".join(trial_new) if decision == "ACCEPT" else "NONE",
        })
        round_rows.append({
            "round": round_number, "surface": surface, "decision": decision,
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": post_hash,
            **post_metrics,
        })
        source = target_by_surface[surface]
        target_deck.append({
            "candidate_id": f"G640-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "gdt639_rank": source["rank"],
            "gdt639_source_locus": source["locus"],
            "gdt639_frozen_default_de": source["proposed_default_de"],
            "working_meaning_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "scope": spec_row["scope"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_anchors, "decision": decision,
            "barrier": spec_row["barrier"], "decision_basis": spec_row["decision_basis"],
        })

    final_dictionary = [*v16_dictionary, *accepted_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_complete_loci = {str(row["locus"]) for row in final_complete}
    final_glossary_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    accepted_defaults = [
        {
            **row, "accepted_round": int(row["status"].rsplit("_", 1)[1]),
            "surface": row["entry"].split("@", 1)[0],
            "source_locus": next(item["gdt639_source_locus"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
            "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        }
        for row in accepted_rows
    ]

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_PREDICTION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "gdt639_rank", "gdt639_source_locus",
        "gdt639_frozen_default_de", "working_meaning_de", "composition", "scope", "rival_de",
        "occurrences", "pages", "reader_exact_occurrences", "decision", "barrier", "decision_basis",
    ))
    write_tsv(output_dir / "FORM_FAMILY_ATLAS.tsv", family_rows, (
        "family", "surface", "observed", "occurrences", "pages", "reader_exact_occurrences",
        "working_reading_de",
    ))
    write_tsv(output_dir / "COMPONENT_BINDING_AUDIT.tsv", component_rows, (
        "component_id", "surface", "segment", "working_value_de", "evidence_path",
        "evidence_kind", "licensed_use",
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
        "opaque_context", "reader_boundary_warning", "unbound_component", "trial_complete_gain",
        "trial_strict_complete_gain", "complete_before", "complete_after", "strict_complete_before",
        "strict_complete_after", "one_unknown_before", "one_unknown_after",
        "trial_new_complete_loci", "accepted_new_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "decision", "dictionary_entries", "dictionary_sha256",
        "physical_lines", "known_token_positions", "unknown_token_positions",
        "complete_multi_token_lines", "strict_complete_lines", "one_unknown_lines",
        "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule",
        "status", "accepted_round", "source_locus", "occurrences",
    ))
    write_tsv(output_dir / "HELD_TARGET_DEFAULTS.tsv", held_rows, (
        "surface", "source_locus", "default_meaning_de", "composition", "occurrences",
        "reader_exact_occurrences", "decision", "barrier", "rival_de", "trial_complete_loci", "status",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "round", "surface", "page", "locus", "strict_complete", "zl3b_line",
        "before_glosses_de", "literal_after_de", "smoothed_working_reading_de",
        "all_present_exact", "scope_clean",
    ))
    write_tsv(output_dir / "V17_EXACT_TOKEN_GLOSSARY.tsv", final_glossary_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V17.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V17.tsv", final_complete,
              ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V17.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V17.tsv", final_dictionary,
              ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G639_RUN_REL, G639_ALLOW_REL, G639_ONE_REL, G639_COVERAGE_REL, G639_COMPLETE_REL,
        G639_GLOSSARY_REL, G639_DICT_REL, G639_RESULT_REL, G639_REPORT_REL,
        G625_REPORT_REL, G625_TERMINAL_REL, G627_REPORT_REL, G628_REPORT_REL, G628_MATRIX_REL, G633_REPORT_REL,
        G634_REPORT_REL, G636_REPORT_REL, TOKENS_REL, CROSS_REL,
    )
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    verdict_counts = Counter(str(row["verdict"]) for row in audit_rows)
    result_core = {
        "schema": "GDT640_DOWNSTREAM_COMPONENT_PREDICTION_RESULT_V1",
        "experiment_id": "GDT640", "status": STATUS,
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "new_pages": 0, "new_images": 0, "allowed_pages": len(pages),
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "target_run": {
            "candidates": len(target_deck), "accepted": len(accepted_rows), "held": len(held_rows),
            "audited_occurrences": len(audit_rows), "verdicts": dict(sorted(verdict_counts.items())),
            "accepted_surfaces": [row["surface"] for row in target_deck if row["decision"] == "ACCEPT"],
            "held_surfaces": [row["surface"] for row in target_deck if row["decision"] == "HOLD"],
        },
        "coverage": {
            "base_complete_multi_token_lines": len(old_complete),
            "base_strict_complete_lines": sum(int(row["strict_complete"]) for row in old_complete),
            "newly_completed_lines": len(final_complete_loci - base_complete_loci),
            **final_metrics,
        },
        "working_dictionary": {
            "v16_entries": len(v16_dictionary), "v17_entries": len(final_dictionary),
            "accepted_tail_entries": len(accepted_rows),
            "v16_prefix_sha256": dictionary_hash(initial_dictionary),
            "v17_sha256": dictionary_hash(final_dictionary),
            "base_glossary_surfaces": len(initial_glossary), "v17_glossary_surfaces": len(glossary),
        },
        "claim_boundary": (
            "GDT640 tests exactly the four strict one-hole surfaces exposed by GDT639 before inspecting their full occurrence circuits. "
            "qotor, okal and chotcheol enter V17 only as complete exact surfaces; qotomody retains a concrete reading but remains held because internal m is unbound. "
            "No OR, AL, M, CHEOL, substring, wrapper or absent cell is globalized. The readings are replaceable technical-codebook defaults, not confirmed plaintext, phonetics, historical words or a language identification."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return result


def main() -> int:
    result = build(ART)
    run, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT640 built: candidates={run['candidates']} accepted={run['accepted']} held={run['held']} "
        f"audits={run['audited_occurrences']} complete={coverage['complete_multi_token_lines']} "
        f"strict={coverage['strict_complete_lines']} one_unknown={coverage['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
