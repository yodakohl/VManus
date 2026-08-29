#!/usr/bin/env python3
"""Build GDT638: promote concrete exact surfaces one at a time."""

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
BASE_REL = Path("experiments/yolo/gdt638_sequential_compound_promotion")
ART = ROOT / BASE_REL / "artifacts"
G637_BASE = Path("experiments/yolo/gdt637_ladder_completion_one_unknown_passages")
G637_RUN_REL = G637_BASE / "src/run.py"
G637_ALLOW_REL = G637_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G637_STRICT_REL = G637_BASE / "artifacts/STRICT_ONE_UNKNOWN_PASSAGES.tsv"
G637_PROPOSALS_REL = G637_BASE / "artifacts/PROPOSED_UNKNOWN_DEFAULTS.tsv"
G637_COVERAGE_REL = G637_BASE / "artifacts/ALL_LINE_CONCRETE_COVERAGE.tsv"
G637_COMPLETE_REL = G637_BASE / "artifacts/COMPLETE_PASSAGE_CANDIDATES.tsv"
G637_GLOSSARY_REL = G637_BASE / "artifacts/V14_EXACT_TOKEN_GLOSSARY.tsv"
G637_DICT_REL = G637_BASE / "artifacts/WORKING_DICTIONARY_V14.tsv"
G637_RESULT_REL = G637_BASE / "artifacts/RESULT.json"
G622_REPORT_REL = Path("experiments/yolo/gdt622_clm667_temperament_codebook/REPORT.md")
G634_REPORT_REL = Path("experiments/yolo/gdt634_known_core_terminal_semantics/REPORT.md")
G595_REPORT_REL = Path("experiments/yolo/gdt595_remaining_bath_default_source_atlas/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt637_builder", ROOT / G637_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT637 builder helpers")
g637 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g637)

TOKENS_REL = g637.TOKENS_REL
CROSS_REL = g637.CROSS_REL
STATUS = "PASS_13_EXACT_COMPOUNDS_PROMOTED__14_NEW_COMPLETE_LINES__2_HELD"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|führe .* aus|leite .* weiter",
    re.IGNORECASE,
)

# Order is compositional: narrow drug/form cells, explicit quality compounds,
# then high-burden quantity/material cards, and finally the very common qoky.
# The two unresolved compounds are audited after the useful deck but not added.
CANDIDATE_SPECS = (
    {
        "surface": "cthoiin", "source_locus": "f15v.10",
        "working_meaning_de": "Blatt-/Krautzubereitung, Form III",
        "composition": "cth+oiin", "scope": "Herbal exact whole surface",
        "rival_de": "allgemeine CTH-Drogenzubereitung, Form III",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "two reader-exact Herbal occurrences; visible cth drug head plus oiin form III",
    },
    {
        "surface": "choiin", "source_locus": "f28v.3",
        "working_meaning_de": "trockene Zubereitungsform III",
        "composition": "ch+oiin", "scope": "exact whole surface",
        "rival_de": "Trockenansatz, Form III",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "ch dry field plus inherited oiin preparation/form III; thirteen occurrences audited",
    },
    {
        "surface": "cthey", "source_locus": "f4r.13",
        "working_meaning_de": "CTH-Drogenmaterial, Form I; im Herbal Blatt-/Krautdroge, Form I",
        "composition": "cth+e+y", "scope": "section-sensitive exact whole surface",
        "rival_de": "CTH-Bindungsform I",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "fills the visible cthy to cthey to ctheey base/form-I/form-II ladder",
    },
    {
        "surface": "cthor", "source_locus": "f15v.12",
        "working_meaning_de": "Drogenteil/-portion; im Herbal Portion Blatt-/Krautdroge",
        "composition": "cth+or", "scope": "section-sensitive exact whole surface",
        "rival_de": "allgemeine Drogenportion",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "cth drug head plus inherited or part/portion carrier; forty-three occurrences audited",
    },
    {
        "surface": "qotchol", "source_locus": "f10r.5",
        "working_meaning_de": "Material: kalt und trocken",
        "composition": "qo+t+ch+ol", "scope": "exact whole surface",
        "rival_de": "kalt-trockener Zubereitungsstoff",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "quality frame plus cold, dry and material fields; thirteen exact-reader occurrences",
    },
    {
        "surface": "otchol", "source_locus": "f4r.3",
        "working_meaning_de": "kalt-trockener Zubereitungsstoff",
        "composition": "o+t+ch+ol", "scope": "exact whole surface",
        "rival_de": "Drogenform: kalt und trocken",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "preparation frame plus cold, dry and material fields; twenty-seven occurrences audited",
    },
    {
        "surface": "kcho", "source_locus": "f49r.12",
        "working_meaning_de": "Zubereitung: heiß und trocken",
        "composition": "k+ch+o", "scope": "exact whole surface",
        "rival_de": "heiß-trockener Ansatz",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "GDT636 concrete span plus seven occurrence contexts; current orientation k hot and ch dry",
    },
    {
        "surface": "chkaiin", "source_locus": "f28v.6",
        "working_meaning_de": "heiß-trocken, Grad III",
        "composition": "ch+k+aiin", "scope": "exact whole surface",
        "rival_de": "trocken-heiß, Klasse III",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "restores the visible hot and grade-III fields omitted by the GDT637 automatic default",
    },
    {
        "surface": "chtain", "source_locus": "f36v.14",
        "working_meaning_de": "kalt-trocken, Grad II",
        "composition": "ch+t+ain", "scope": "exact whole surface",
        "rival_de": "trocken-kalt, Klasse II",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "restores the visible cold and grade-II fields omitted by the GDT637 automatic default",
    },
    {
        "surface": "doiin", "source_locus": "f35v.21",
        "working_meaning_de": "Zubereitungsmaß, Form III",
        "composition": "d+oiin", "scope": "exact whole surface",
        "rival_de": "Dosis/Maß der Zubereitungsform III",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "d value/measure head plus oiin form III; eleven occurrences contain no contrary concrete carrier",
    },
    {
        "surface": "dol", "source_locus": "f93r.21",
        "working_meaning_de": "Materialmaß",
        "composition": "d+ol", "scope": "exact whole surface",
        "rival_de": "abgemessenes Material",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "d value/measure head plus ol material carrier; all seventy-six occurrences audited before admission",
    },
    {
        "surface": "oaiir", "source_locus": "f7r.5",
        "working_meaning_de": "Zubereitung, Teil-/Sortierklasse III",
        "composition": "o+aiir", "scope": "exact whole surface",
        "rival_de": "Zubereitungs-Sortierklasse III",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "direct o preparation plus aiir class-III composition; four occurrences and one informative completion",
    },
    {
        "surface": "qoky", "source_locus": "f13v.5",
        "working_meaning_de": "heiße Grundform",
        "composition": "qo+k+y", "scope": "exact whole surface",
        "rival_de": "heißer Grundzustand; GDT595 OK+Y action parse is out of this reader scope",
        "intended_decision": "ACCEPT", "admission_barrier": "NONE",
        "decision_basis": "quality frame plus hot and base closure; all 138 occurrences audited and promoted last",
    },
    {
        "surface": "keechy", "source_locus": "f47v.4",
        "working_meaning_de": "heiß-trocken, Form II",
        "composition": "k+ee+ch+y", "scope": "worksheet proposal only",
        "rival_de": "heiß gebundene Trockenform II",
        "intended_decision": "HOLD", "admission_barrier": "FIELD_ORDER_AMBIGUITY",
        "decision_basis": "only one of three contexts is informative and the internal ee/ch/y field order is not yet secured",
    },
    {
        "surface": "chokshy", "source_locus": "f29r.6",
        "working_meaning_de": "Trockenform mit heiß-feuchter Qualität",
        "composition": "ch+o+k+sh+y", "scope": "worksheet proposal only",
        "rival_de": "Trockenansatz einer erhitzt eingeweichten Grundform",
        "intended_decision": "HOLD", "admission_barrier": "INTERNAL_DRY_MOIST_SCOPE_COLLISION",
        "decision_basis": "singleton combines dry and moist fields without an independently visible scope or process order",
    },
)

SMOOTHED_NEW_LINES = {
    "f15v.10": "Samenportion; Pflanzenteil; Blatt-/Krautzubereitung Form III; Blatt-/Krautmaterial; heiß Grad III.",
    "f28v.3": "Pflanzenteil; Trockengut; trockene Grundform; Trockenansatz Form III.",
    "f4r.13": "Grad-/Maßwert III; Blatt-/Krautdroge Form I.",
    "f15v.12": "Grad-/Maßwert III; Portion Blatt-/Krautdroge; Trockengut; Pflanzenteil.",
    "f10r.5": "Heiß-trocken; Material kalt und trocken; Trockengut; Blatt-/Krautmaterial.",
    "f4r.3": "Kalt-trockener Zubereitungsstoff; Trockengut; trockene Grundform; trocken Grad III; kalt Grad III; Grad-/Maßwert III; feucht Grad II.",
    "f49r.12": "Pulverzubereitung Dosis III; Trockenansatz; Zubereitung heiß und trocken; Grad-/Maßwert III; trockenes Blatt-/Krautgut.",
    "f28v.6": "Grad-/Maßwert III; heiß-trocken Grad III.",
    "f36v.14": "Samenzubereitung Form III; kalt-trocken Grad II.",
    "f35v.21": "Zubereitungsmaß Form III; Pflanzenteil; Pflanzenteil.",
    "f93r.21": "Materialmaß; feuchtes Material; Qualitätsgrad III; feuchtes Blatt-/Krautgut.",
    "f7r.5": "Zubereitung: Teil-/Sortierklasse III; kalt im Zubereitungsrahmen, Grad III.",
    "f13v.5": "Heiße Grundform; Grad-/Maßwert III.",
    "f79v.4": "Heißer Zustand, Bindungsstufe II; heißer Zustand, Bindungsstufe II; kalt im qo-Rahmen, Grad II; Samenmaterial/Saatgut; getrockneter Zustand; Wurzel/Wurzeldroge, trocken gebunden, Form I; heiße Grundform; getrocknetes Drogenholz.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "PROMOTION_CANDIDATE_DECK.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "SEQUENTIAL_PROMOTION_LEDGER.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "HELD_REJECTED_CANDIDATES.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "V15_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V15.tsv", "COMPLETE_PASSAGES_V15.tsv",
    "ONE_UNKNOWN_PASSAGES_V15.tsv", "WORKING_DICTIONARY_V15.tsv",
)

COVERAGE_FIELDS = (
    "page", "locus", "section", "language", "hand", "token_count", "known_tokens",
    "context_licensed_tokens", "ambiguous_tokens", "reader_unstable_tokens", "unknown_tokens",
    "coverage_fraction", "reader_exact_tokens", "split_normalized_tokens", "all_three_present",
    "all_present_exact", "zl3b_line", "token_glosses_de", "gloss_sources", "scope_states",
    "unknown_ordinals", "unknown_surfaces",
)
ONE_FIELDS = (
    "rank", "score", "strict_eligible", *COVERAGE_FIELDS, "unknown_ordinal", "unknown_surface",
    "previous", "following", "proposed_default_de", "proposal_basis", "proposal_strength",
    "proposed_complete_translation_de",
)


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


def coverage_metrics(
    coverage: list[dict[str, object]], one_unknown: list[dict[str, object]],
    complete: list[dict[str, object]], glossary: dict[str, dict[str, object]],
) -> dict[str, int]:
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


def promotion_dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT638_EXACT_WHOLE",
        "kind": "EXACT_WHOLE_SURFACE_PROMOTION",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; {occurrences} audited occurrences; {spec_row['scope']}; "
            "no substring, bare-body or absent-cell transfer"
        ),
        "status": f"NEW_V15_ACCEPTED_ROUND_{round_number:02d}",
    }


def audit_candidate(
    round_number: int, spec_row: dict[str, str], token_rows: list[dict[str, str]],
    by_line: dict[str, list[dict[str, object]]], positions: dict[tuple[str, int], tuple[int, str]],
    exact: dict[tuple[str, int], int], boundary: dict[tuple[str, int], int],
    cross_by_locus: dict[str, dict[str, str]], pre_by_locus: dict[str, dict[str, object]],
    trial_by_locus: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    surface = spec_row["surface"]
    members = [row for row in token_rows if row["eva"] == surface]
    rows: list[dict[str, object]] = []
    for member in members:
        locus, token_index = member["locus"], int(member["token_index"])
        ordinal, position = positions[locus, token_index]
        line = by_line[locus]
        target_count = sum(str(token["eva"]) == surface for token in line)
        before = pre_by_locus[locus]
        after = trial_by_locus[locus]
        known_other = int(before["known_tokens"])
        other_positions = max(len(line) - target_count, 1)
        context_fraction = known_other / other_positions
        flags: list[str] = []
        if not exact[locus, token_index]:
            flags.append("READER_SPLIT_OR_FUSION")
        if int(before["ambiguous_tokens"]):
            flags.append("ACTIVE_RIVAL_CONTEXT")
        if known_other < 2 or context_fraction < 0.5:
            flags.append("OPAQUE_OTHER_TOKENS")
        if spec_row["admission_barrier"] != "NONE":
            flags.append(spec_row["admission_barrier"])
        if spec_row["admission_barrier"] == "INTERNAL_DRY_MOIST_SCOPE_COLLISION":
            verdict = "HARD_CONTRADICTION"
            reason = "dry and moist fields collide inside the singleton without a separately observed scope"
        elif not exact[locus, token_index]:
            verdict = "READER_BOUNDARY_WARNING"
            reason = "target surface is split, fused or changed in at least one alternate reading"
        elif known_other < 2 or context_fraction < 0.5:
            verdict = "OPAQUE_CONTEXT"
            reason = "too few independently concrete neighbouring positions to test prose coherence"
        else:
            verdict = "CONSISTENT_CONCRETE"
            reason = "the proposed short value introduces no opposite quality, carrier or class conflict in this rendered line"
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
            "local_before_de": before["token_glosses_de"],
            "local_after_de": after["token_glosses_de"],
            "flags": "|".join(flags) if flags else "NONE", "verdict": verdict,
            "review_reason": reason,
        })
    rows.sort(key=lambda row: (str(row["locus"]), int(row["token_ordinal"])))
    for index, row in enumerate(rows, 1):
        row["audit_id"] = f"G638-A{round_number:02d}-{index:03d}"
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G637_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    token_rows, token_stats = g637.g636.g635.g634.g633.g632.g631.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = g637.g636.g635.g634.g633.g632.g631.guarded_query(
        CROSS_REL, pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)
    positions = g637.g636.position_maps(by_line)

    strict_rows = read_tsv(ROOT / G637_STRICT_REL)
    strict_by_surface = {row["unknown_surface"]: row for row in strict_rows}
    proposals = {row["surface"]: row for row in read_tsv(ROOT / G637_PROPOSALS_REL)}
    v14_dictionary: list[dict[str, object]] = [dict(row) for row in read_tsv(ROOT / G637_DICT_REL)]
    old_coverage = read_tsv(ROOT / G637_COVERAGE_REL)
    old_complete = read_tsv(ROOT / G637_COMPLETE_REL)
    old_glossary = read_tsv(ROOT / G637_GLOSSARY_REL)
    if len(v14_dictionary) != 259 or len(old_coverage) != 4128 or len(old_complete) != 16 or len(old_glossary) != 212:
        raise RuntimeError("GDT637 frozen base count changed")

    v13 = g637.read_tsv(ROOT / g637.G636_DICT_REL)
    grid = g637.build_target_grid(token_rows, positions, exact)
    glossary = g637.build_exact_glossary(v13, grid)
    if len(glossary) != 212:
        raise RuntimeError("GDT637 executable glossary changed")
    initial_glossary = {surface: dict(row) for surface, row in glossary.items()}
    initial_dictionary = [dict(row) for row in v14_dictionary]

    coverage, one_unknown, _, complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    base_complete_loci = {str(row["locus"]) for row in complete}
    accepted_rows: list[dict[str, object]] = []
    candidate_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = []
    new_complete_rows: list[dict[str, object]] = []
    held_rows: list[dict[str, object]] = []

    base_metrics = coverage_metrics(coverage, one_unknown, complete, glossary)
    round_rows.append({
        "round": 0, "surface": "BASE_V14", "decision": "BASE",
        "dictionary_entries": len(v14_dictionary), "dictionary_sha256": dictionary_hash(v14_dictionary),
        **base_metrics,
    })

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if surface not in strict_by_surface:
            raise RuntimeError(f"candidate is not a strict GDT637 hole: {surface}")
        source = strict_by_surface[surface]
        if source["locus"] != spec_row["source_locus"]:
            raise RuntimeError(f"candidate source locus drift: {surface}")
        if surface in glossary:
            raise RuntimeError(f"candidate already present before round: {surface}")
        if GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"generic filler in candidate meaning: {surface}")

        members = [row for row in token_rows if row["eva"] == surface]
        pre_dictionary = [*v14_dictionary, *accepted_rows]
        pre_hash = dictionary_hash(pre_dictionary)
        pre_coverage, pre_one, _, pre_complete = g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        pre_by_locus = {str(row["locus"]): row for row in pre_coverage}
        pre_complete_loci = {str(row["locus"]) for row in pre_complete}
        pre_strict_loci = {str(row["locus"]) for row in pre_complete if int(row["strict_complete"])}

        trial_glossary = {key: dict(value) for key, value in glossary.items()}
        g637.set_gloss(
            trial_glossary, surface, spec_row["working_meaning_de"], f"GDT638:ROUND_{round_number:02d}",
            "EXACT_WHOLE_SURFACE_PROMOTION", "KNOWN_EXACT_WHOLE", 110,
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
        hard = verdicts["HARD_CONTRADICTION"]
        nonsense = verdicts["NONSENSE"]
        exact_anchors = sum(int(row["reader_exact"]) for row in candidate_audit)
        decision = spec_row["intended_decision"]
        if decision == "ACCEPT" and (
            spec_row["admission_barrier"] != "NONE" or hard or nonsense or not trial_new or not exact_anchors
        ):
            decision = "HOLD"
        accepted = decision == "ACCEPT"
        if accepted:
            glossary = trial_glossary
            coverage, one_unknown, complete = trial_coverage, trial_one, trial_complete
            dictionary_row = promotion_dictionary_row(spec_row, round_number, len(members))
            accepted_rows.append(dictionary_row)
            applied_new = trial_new
            applied_new_strict = trial_new_strict
            for locus in applied_new:
                before = pre_by_locus[locus]
                after = trial_by_locus[locus]
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
        else:
            coverage, one_unknown, complete = pre_coverage, pre_one, pre_complete
            applied_new, applied_new_strict = [], []
            held_rows.append({
                "surface": surface, "round": round_number, "decision": "HOLD",
                "veto_codes": spec_row["admission_barrier"],
                "veto_loci": spec_row["source_locus"], "trial_complete_loci": "|".join(trial_new) or "NONE",
                "provisional_default_de": spec_row["working_meaning_de"],
                "reason": spec_row["decision_basis"],
            })

        post_dictionary = [*v14_dictionary, *accepted_rows]
        post_hash = dictionary_hash(post_dictionary)
        post_metrics = coverage_metrics(coverage, one_unknown, complete, glossary)
        ledger_rows.append({
            "round": round_number, "surface": surface, "decision": decision,
            "decision_reason": spec_row["decision_basis"],
            "pre_dictionary_entries": len(pre_dictionary), "post_dictionary_entries": len(post_dictionary),
            "pre_dictionary_sha256": pre_hash, "post_dictionary_sha256": post_hash,
            "occurrences": len(members), "audited_occurrences": len(candidate_audit),
            "reader_exact_occurrences": exact_anchors,
            "consistent_concrete": verdicts["CONSISTENT_CONCRETE"],
            "opaque_context": verdicts["OPAQUE_CONTEXT"],
            "reader_boundary_warning": verdicts["READER_BOUNDARY_WARNING"],
            "hard_contradiction": hard, "nonsense": nonsense,
            "trial_complete_gain": len(trial_new), "trial_strict_complete_gain": len(trial_new_strict),
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "marginal_complete": len(applied_new),
            "strict_complete_before": len(pre_strict_loci),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "marginal_strict_complete": len(applied_new_strict),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_complete_loci": "|".join(applied_new) or "NONE",
            "new_strict_complete_loci": "|".join(applied_new_strict) or "NONE",
        })
        round_rows.append({
            "round": round_number, "surface": surface, "decision": decision,
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": post_hash,
            **post_metrics,
        })
        candidate_deck.append({
            "candidate_id": f"G638-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "g637_strict_rank": source["rank"],
            "g637_source_locus": source["locus"],
            "g637_default_de": proposals[surface]["proposed_default_de"],
            "working_meaning_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "scope": spec_row["scope"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_anchors,
            "admission_barrier": spec_row["admission_barrier"],
            "decision": decision, "decision_basis": spec_row["decision_basis"],
        })

    final_dictionary = [*v14_dictionary, *accepted_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_complete_loci = {str(row["locus"]) for row in final_complete}
    final_glossary_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "PROMOTION_CANDIDATE_DECK.tsv", candidate_deck, (
        "candidate_id", "candidate_order", "surface", "g637_strict_rank", "g637_source_locus",
        "g637_default_de", "working_meaning_de", "composition", "scope", "rival_de",
        "occurrences", "pages", "reader_exact_occurrences", "admission_barrier", "decision",
        "decision_basis",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line",
        "rf1b_line", "reader_exact", "split_normalized", "before_state", "before_gloss",
        "after_gloss", "known_other_tokens", "other_token_positions", "context_fraction",
        "local_before_de", "local_after_de", "flags", "verdict", "review_reason",
    ))
    write_tsv(output_dir / "SEQUENTIAL_PROMOTION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "decision", "decision_reason", "pre_dictionary_entries",
        "post_dictionary_entries", "pre_dictionary_sha256", "post_dictionary_sha256",
        "occurrences", "audited_occurrences", "reader_exact_occurrences", "consistent_concrete",
        "opaque_context", "reader_boundary_warning", "hard_contradiction", "nonsense",
        "trial_complete_gain", "trial_strict_complete_gain", "complete_before", "complete_after",
        "marginal_complete", "strict_complete_before", "strict_complete_after",
        "marginal_strict_complete", "one_unknown_before", "one_unknown_after",
        "new_complete_loci", "new_strict_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "decision", "dictionary_entries", "dictionary_sha256",
        "physical_lines", "known_token_positions", "unknown_token_positions",
        "complete_multi_token_lines", "strict_complete_lines", "one_unknown_lines",
        "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    accepted_defaults = [
        {
            **row, "accepted_round": int(row["status"].rsplit("_", 1)[1]),
            "surface": row["entry"].split("@", 1)[0],
            "source_locus": next(
                item["g637_source_locus"] for item in candidate_deck
                if item["surface"] == row["entry"].split("@", 1)[0]
            ),
            "occurrences": next(
                item["occurrences"] for item in candidate_deck
                if item["surface"] == row["entry"].split("@", 1)[0]
            ),
        }
        for row in accepted_rows
    ]
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule",
        "status", "accepted_round", "source_locus", "occurrences",
    ))
    write_tsv(output_dir / "HELD_REJECTED_CANDIDATES.tsv", held_rows, (
        "surface", "round", "decision", "veto_codes", "veto_loci", "trial_complete_loci",
        "provisional_default_de", "reason",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "round", "surface", "page", "locus", "strict_complete", "zl3b_line",
        "before_glosses_de", "literal_after_de", "smoothed_working_reading_de",
        "all_present_exact", "scope_clean",
    ))
    write_tsv(output_dir / "V15_EXACT_TOKEN_GLOSSARY.tsv", final_glossary_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V15.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V15.tsv", final_complete,
              ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V15.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V15.tsv", final_dictionary,
              ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G637_RUN_REL, G637_ALLOW_REL, G637_STRICT_REL, G637_PROPOSALS_REL, G637_COVERAGE_REL,
        G637_COMPLETE_REL, G637_GLOSSARY_REL, G637_DICT_REL, G637_RESULT_REL,
        G622_REPORT_REL, G634_REPORT_REL, G595_REPORT_REL, TOKENS_REL, CROSS_REL,
    )
    final_metrics = coverage_metrics(final_coverage, final_one, final_complete, glossary)
    verdict_counts = Counter(str(row["verdict"]) for row in audit_rows)
    result_core = {
        "schema": "GDT638_SEQUENTIAL_COMPOUND_PROMOTION_RESULT_V1",
        "experiment_id": "GDT638", "status": STATUS,
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "new_pages": 0, "new_images": 0, "allowed_pages": len(pages),
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "candidate_run": {
            "candidates": len(candidate_deck),
            "accepted": sum(row["decision"] == "ACCEPT" for row in candidate_deck),
            "held": sum(row["decision"] == "HOLD" for row in candidate_deck),
            "audited_occurrences": len(audit_rows),
            "verdicts": dict(sorted(verdict_counts.items())),
            "accepted_surfaces": [row["surface"] for row in candidate_deck if row["decision"] == "ACCEPT"],
            "held_surfaces": [row["surface"] for row in candidate_deck if row["decision"] == "HOLD"],
        },
        "coverage": {
            "base_complete_multi_token_lines": len(old_complete),
            "base_strict_complete_lines": sum(int(row["strict_complete"]) for row in old_complete),
            "newly_completed_lines": len(final_complete_loci - base_complete_loci),
            **final_metrics,
        },
        "working_dictionary": {
            "v14_entries": len(v14_dictionary), "v15_entries": len(final_dictionary),
            "accepted_tail_entries": len(accepted_rows),
            "v14_prefix_sha256": dictionary_hash(initial_dictionary),
            "v15_sha256": dictionary_hash(final_dictionary),
            "base_glossary_surfaces": len(initial_glossary), "v15_glossary_surfaces": len(glossary),
        },
        "claim_boundary": (
            "GDT638 promotes only complete exact surfaces from reader-stable GDT637 one-hole lines. "
            "Every candidate is rendered at every guarded occurrence before a sequential decision. "
            "Thirteen short defaults add fourteen complete lines; keechy and chokshy remain explicit worksheet values because field order or dry/moist scope is unresolved. "
            "The accepted cards are scoped working defaults, not confirmed plaintext, words, phonetics or a language identification."
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
    run = result["candidate_run"]
    coverage = result["coverage"]
    print(
        f"GDT638 built: candidates={run['candidates']} accepted={run['accepted']} held={run['held']} "
        f"audits={run['audited_occurrences']} complete={coverage['complete_multi_token_lines']} "
        f"strict={coverage['strict_complete_lines']} one_unknown={coverage['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
