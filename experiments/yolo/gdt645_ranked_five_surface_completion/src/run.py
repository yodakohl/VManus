#!/usr/bin/env python3
"""Build GDT645: promote the five strongest whole surfaces exposed in V21."""
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
BASE_REL = Path("experiments/yolo/gdt645_ranked_five_surface_completion")
ART = ROOT / BASE_REL / "artifacts"
G644_BASE = Path("experiments/yolo/gdt644_downstream_five_surface_completion")
G644_RUN_REL = G644_BASE / "src/run.py"
G644_ALLOW_REL = G644_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G644_COVERAGE_REL = G644_BASE / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V21.tsv"
G644_COMPLETE_REL = G644_BASE / "artifacts/COMPLETE_PASSAGES_V21.tsv"
G644_ONE_REL = G644_BASE / "artifacts/ONE_UNKNOWN_PASSAGES_V21.tsv"
G644_NEW_ONE_REL = G644_BASE / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv"
G644_GLOSSARY_REL = G644_BASE / "artifacts/V21_EXACT_TOKEN_GLOSSARY.tsv"
G644_DICT_REL = G644_BASE / "artifacts/WORKING_DICTIONARY_V21.tsv"
G644_RESULT_REL = G644_BASE / "artifacts/RESULT.json"
G644_REPORT_REL = G644_BASE / "REPORT.md"
G624_REPORT_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md")
G624_GRID_REL = Path("experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/GRID_CELLS.tsv")
G631_REPORT_REL = Path("experiments/yolo/gdt631_prefixed_cth_quality_parts/REPORT.md")
G628_REPORT_REL = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G633_REPORT_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G626_REPORT_REL = Path("experiments/yolo/gdt626_mobile_operation_lexicon/REPORT.md")
G636_REPORT_REL = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G639_REPORT_REL = Path("experiments/yolo/gdt639_strict_hole_component_repair/REPORT.md")
G640_REPORT_REL = Path("experiments/yolo/gdt640_downstream_component_prediction/REPORT.md")
G529_REPORT_REL = Path("experiments/yolo/gdt529_nearest_terminal_m_square/REPORT.md")
INHERITED_HELPER_RUN_RELS = tuple(
    Path(f"experiments/yolo/{slug}/src/run.py")
    for slug in (
        "gdt631_prefixed_cth_quality_parts",
        "gdt632_cth_interfix_lattice",
        "gdt633_cth_interfix_semantic_contrasts",
        "gdt634_known_core_terminal_semantics",
        "gdt635_initial_head_same_remainder_swaps",
        "gdt636_residual_four_head_semantics",
        "gdt637_ladder_completion_one_unknown_passages",
        "gdt638_sequential_compound_promotion",
        "gdt639_strict_hole_component_repair",
        "gdt640_downstream_component_prediction",
        "gdt641_strict_tch_bound_form_completion",
        "gdt642_exact_e_ol_or_carrier_completion",
        "gdt643_exposed_five_hole_completion",
    )
)

spec = importlib.util.spec_from_file_location("gdt644_builder_for_gdt645", ROOT / G644_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT644 builder helpers")
g644 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g644)
g637 = g644.g637
TOKENS_REL = g644.TOKENS_REL
CROSS_REL = g644.CROSS_REL

STATUS = "PASS_5_RANKED_SURFACES__115_POSITIONS__6_NEW_COMPLETE_LINES"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)

CANDIDATE_SPECS = (
    {
        "surface": "oky", "source_locus": "f36v.13",
        "working_meaning_de": "heißer Ansatz, Grundform",
        "composition": "o+k+y",
        "rival_de": "heiße Grundform der Zubereitung",
        "scope": "exact complete ZL3b surface only",
        "reader_gate": "AT_LEAST_ONE_ALL_READER_EXACT",
        "decision_basis": "the complete bare/o/qo by k/t by y grid gives oky a hot preparation counterpart to accepted oty",
    },
    {
        "surface": "otchor", "source_locus": "f35r.14",
        "working_meaning_de": "kalt-trockene Drogenportion im Ansatz",
        "composition": "o+t+ch+or",
        "rival_de": "kalt markierter Pflanzenteil des Ansatzes",
        "scope": "exact complete ZL3b surface only",
        "reader_gate": "AT_LEAST_ONE_ALL_READER_EXACT",
        "decision_basis": "all 32 frame by k/t by optional ch by ol/or cells are observed and the material/portion contrast selects o+t+ch+or",
    },
    {
        "surface": "ychair", "source_locus": "f18r.12",
        "working_meaning_de": "zweiter trockener Anteil dieser Droge",
        "composition": "y+(ch+air)",
        "rival_de": "zweite trockene Sorte dieser Droge",
        "scope": "exact complete ZL3b surface only; initial y and air remain whole-bound",
        "reader_gate": "AT_LEAST_ONE_ALL_READER_EXACT",
        "decision_basis": "15 of 16 y/no-y by k/t/ch/sh by ar/air cells are observed and bind the exact singleton to dry fraction II in local Y scope",
    },
    {
        "surface": "cheaiin", "source_locus": "f19v.14",
        "working_meaning_de": "trocken im dritten Grad",
        "composition": "ch+e+(a+iin)",
        "rival_de": "getrocknete Droge, Menge III",
        "scope": "exact complete ZL3b surface only; e and a+iin remain whole-bound",
        "reader_gate": "AT_LEAST_ONE_ALL_READER_EXACT",
        "decision_basis": "chean/cheain/cheaiin occupy grades I/II/III and the sheain/sheaiin arm preserves the dry/moist contrast",
    },
    {
        "surface": "cthom", "source_locus": "f4r.7",
        "working_meaning_de": "eine Handvoll Blatt- oder Krautansatz",
        "composition": "cth+o+[m]_whole",
        "rival_de": "Blatt- oder Krautansatz, Form oder Einheit I",
        "scope": "exact complete ZL3b surface only; terminal m remains whole-bound",
        "reader_gate": "AT_LEAST_ONE_ALL_READER_EXACT",
        "decision_basis": "all five exact tokens are Herbal; the CTH preparation family, bounded terminal-m square and period M=manipulus comparator select a handful as the concrete whole-word default without freeing m",
    },
)

def framed_carrier_reading(frame: str, thermal: str, dry: str, carrier: str) -> str:
    quality = {"k": "heiß", "t": "kalt"}[thermal] + ("-trocken" if dry else "")
    noun = {"ol": "Drogenstoff", "or": "Drogenportion"}[carrier]
    scope = {"": "", "o": " des Ansatzes", "qo": " der Zubereitung", "y": " dieser Droge"}[frame]
    return f"{noun}{scope}, {quality}"


OTCHOR_FAMILY = tuple(
    ("OTCHOR_GRID", f"{frame}{thermal}{dry}{carrier}", framed_carrier_reading(frame, thermal, dry, carrier))
    for frame in ("", "o", "qo", "y")
    for thermal in ("k", "t")
    for dry in ("", "ch")
    for carrier in ("ol", "or")
)

YCHAIR_FAMILY = tuple(
    (
        "YCHAIR_GRID",
        f"{frame}{quality}{carrier}",
        f"{'Fraktion I' if carrier == 'ar' else 'Fraktion II'}"
        f"{' dieser Droge' if frame == 'y' else ''}, "
        f"{ {'k': 'heiß', 't': 'kalt', 'ch': 'trocken', 'sh': 'feucht'}[quality] }",
    )
    for frame in ("", "y")
    for quality in ("k", "t", "ch", "sh")
    for carrier in ("ar", "air")
)

FAMILY_FORMS = (
    ("OKY_GRID", "ky", "heiße Grundform"),
    ("OKY_GRID", "ty", "kalte Grundform"),
    ("OKY_GRID", "oky", "heißer Ansatz, Grundform"),
    ("OKY_GRID", "oty", "kalter Ansatz, Grundform"),
    ("OKY_GRID", "qoky", "heiße Zubereitungsgrundform"),
    ("OKY_GRID", "qoty", "kalte Zubereitungsgrundform"),
) + OTCHOR_FAMILY + YCHAIR_FAMILY + (
    ("CHEAIIN_LADDER", "chean", "trocken gebundene Form, Grad I"),
    ("CHEAIIN_LADDER", "cheain", "trocken gebundene Form, Grad II"),
    ("CHEAIIN_LADDER", "cheaiin", "trocken gebundene Form, Grad III"),
    ("CHEAIIN_LADDER", "cheaiiin", "trocken gebundene Form, Grad IV"),
    ("CHEAIIN_LADDER", "shean", "feucht gebundene Form, Grad I"),
    ("CHEAIIN_LADDER", "sheain", "feucht gebundene Form, Grad II"),
    ("CHEAIIN_LADDER", "sheaiin", "feucht gebundene Form, Grad III"),
    ("CHEAIIN_LADDER", "sheaiiin", "feucht gebundene Form, Grad IV"),
    ("CTHOM_FAMILY", "ctho", "CTH-Zubereitung"),
    ("CTHOM_FAMILY", "cthom", "eine Handvoll Blatt- oder Krautansatz"),
    ("CTHOM_FAMILY", "cthal", "CTH-Rohstoffform I"),
    ("CTHOM_FAMILY", "cthar", "CTH-Drogenfraktion I"),
    ("CTHOM_FAMILY", "cthol", "CTH-Drogenstoff"),
    ("CTHOM_FAMILY", "cthor", "CTH-Drogenportion"),
)

COMPONENT_ROWS = (
    ("oky", "o", "Ansatz/Zubereitung", G633_REPORT_REL, "PREPARATION_HEAD"),
    ("oky", "k", "heiß; nur in oky gebunden", G624_GRID_REL, "BOUND_HOT_QUALITY"),
    ("oky", "y", "Grundform; nur in oky gebunden", G624_GRID_REL, "BOUND_BASE_FORM"),
    ("otchor", "o", "Ansatz", G633_REPORT_REL, "PREPARATION_HEAD"),
    ("otchor", "t+ch", "kalt-trocken", G624_GRID_REL, "COLD_DRY_QUALITY"),
    ("otchor", "or", "Drogenportion", G628_REPORT_REL, "PORTION_CARRIER"),
    ("ychair", "y", "kein Einzelwert; nur in ychair gebunden", G644_REPORT_REL, "BOUND_CURRENT_DRUG_FRAME"),
    ("ychair", "ch", "trocken", G624_GRID_REL, "DRY_QUALITY"),
    ("ychair", "air", "zweiter Anteil; nur in ychair gebunden", G636_REPORT_REL, "BOUND_FRACTION_II"),
    ("cheaiin", "ch+e", "trocken gebunden", G633_REPORT_REL, "ATTRIBUTIVE_DRY"),
    ("cheaiin", "a+iin", "dritter Grad; nur in cheaiin gebunden", G626_REPORT_REL, "BOUND_GRADE_III"),
    ("cthom", "cth", "Drogenklasse; im Kräuterbuch Blatt/Kraut", G631_REPORT_REL, "CTH_DRUG_CLASS"),
    ("cthom", "o", "Zubereitung", G633_REPORT_REL, "PREPARATION_HEAD"),
    ("cthom", "[m]", "Handvoll nur als cthom-Ganzwortwert; kein freies m", G640_REPORT_REL, "WHOLE_BOUND_M_WITH_PERIOD_MANIPULUS_PRIOR"),
)

SMOOTHED_LINES = {
    "f36v.13": "Heißer Ansatz, Grundform; feucht gebundene Droge; Blatt- oder Krautdroge; kalter Ansatz, Grundform.",
    "f35r.14": "Blatt- oder Krautdroge; trockene Droge; Menge III; kalt-trocken; kalt-trockene Drogenportion im Ansatz; Portion III; feuchte Droge; kalt, Grad III.",
    "f18r.12": "Zweiter trockener Anteil dieser Droge; Blatt- oder Krautdroge; Grad III; heiß-trocken; CTH-Droge.",
    "f19v.14": "Kalt-trockener Zubereitungsstoff; trocken im dritten Grad; Blatt- oder Krautdroge.",
    "f4r.7": "Kalt, Grad III; Blatt- oder Krautdroge; Grad III; eine Handvoll Blatt- oder Krautansatz.",
    "f6r.12": "Drogenteil; feuchte Droge; eine Handvoll Blatt- oder Krautansatz; Pflanzenteil; CTH-Droge.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V22_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V22.tsv",
    "COMPLETE_PASSAGES_V22.tsv", "ONE_UNKNOWN_PASSAGES_V22.tsv", "WORKING_DICTIONARY_V22.tsv",
)
COVERAGE_FIELDS = g644.COVERAGE_FIELDS
ONE_FIELDS = g644.ONE_FIELDS


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


def string_rows(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    return [{str(key): str(value) for key, value in row.items()} for row in rows]


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


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def reader_support(
    surface: str, cross: dict[str, str], reader_exact: int, split_normalized: int,
) -> tuple[str, str, int]:
    if reader_exact:
        return "ALL_THREE_EXACT", "all three readers retain the exact token", 0
    if split_normalized:
        return "ALL_THREE_SPLIT_NORMALIZED", "alternate reader changes only the boundary", 0
    return "READER_VARIANT", "one or more readers change the target beyond boundary normalization", 0


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int, support: str) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT645_EXACT_ZL3B_WHOLE",
        "kind": "EXACT_ZL3B_WHOLE_DOWNSTREAM_COMPLETION",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"{spec_row['scope']}; {occurrences} audited occurrences; reader gate {support}; "
            "alternate-reader variants stay explicit; no substring, bare component or absent-cell transfer"
        ),
        "status": f"NEW_V22_ACCEPTED_ROUND_{round_number:02d}",
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G644_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary: list[dict[str, object]] = [dict(row) for row in read_tsv(ROOT / G644_DICT_REL)]
    old_coverage = read_tsv(ROOT / G644_COVERAGE_REL)
    old_complete = read_tsv(ROOT / G644_COMPLETE_REL)
    old_one = read_tsv(ROOT / G644_ONE_REL)
    old_glossary = read_tsv(ROOT / G644_GLOSSARY_REL)
    source_rows = read_tsv(ROOT / G644_NEW_ONE_REL)
    source_pairs = {(row["unknown_surface"], row["locus"]) for row in source_rows}
    targets = {str(row["surface"]) for row in CANDIDATE_SPECS}
    if not all((str(row["surface"]), str(row["source_locus"])) in source_pairs for row in CANDIDATE_SPECS):
        raise RuntimeError("GDT644 ranked source frontier changed")
    if (len(base_dictionary), len(old_coverage), len(old_complete), len(old_one), len(old_glossary)) != (298, 4128, 54, 75, 251):
        raise RuntimeError("GDT644 frozen base counts changed")
    for spec_row in CANDIDATE_SPECS:
        if (str(spec_row["surface"]), str(spec_row["source_locus"])) not in source_pairs:
            raise RuntimeError(f"source locus drift: {spec_row['surface']}")

    glossary = {row["surface"]: dict(row) for row in old_glossary}
    if len(glossary) != len(old_glossary):
        raise RuntimeError("GDT644 glossary contains duplicate surfaces")
    coverage, one_unknown, _, complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
    base_metrics = metrics(coverage, one_unknown, complete, glossary)
    expected_base_metrics = {
        "physical_lines": 4128, "known_token_positions": 10230,
        "unknown_token_positions": 22109, "complete_multi_token_lines": 54,
        "strict_complete_lines": 38, "one_unknown_lines": 75,
        "strict_one_unknown_lines": 26, "exact_glossary_surfaces": 251,
    }
    if base_metrics != expected_base_metrics:
        raise RuntimeError(f"GDT644 replayed metrics changed: {base_metrics!r}")
    if string_rows(coverage) != string_rows(old_coverage):
        raise RuntimeError("GDT644 coverage edition does not replay row-for-row")
    if string_rows(complete) != string_rows(old_complete):
        raise RuntimeError("GDT644 complete-passage edition does not replay row-for-row")
    if string_rows(one_unknown) != string_rows(old_one):
        raise RuntimeError("GDT644 one-hole edition does not replay row-for-row")
    audit_base_glossary = {key: dict(value) for key, value in glossary.items()}
    audit_base_by_locus = {str(row["locus"]): row for row in coverage}
    base_complete_loci = {str(row["locus"]) for row in complete}
    base_one_loci = {str(row["locus"]) for row in one_unknown}

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    family_rows: list[dict[str, object]] = []
    for family, surface, reading in FAMILY_FORMS:
        members = [row for row in token_rows if row["eva"] == surface]
        family_rows.append({
            "family": family, "surface": surface, "zl3b_occurrences": token_counts[surface],
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "cross_reader_only": 0,
            "surface_status": "OBSERVED" if members else "ABSENT_PREDICTION_HOLD",
            "working_reading_de": reading,
        })

    component_rows = [
        {
            "component_id": f"G645-B{index:02d}", "surface": surface, "segment": segment,
            "working_value_de": value, "evidence_path": str(path), "evidence_kind": kind,
            "licensed_use": f"inside exact {surface} only",
        }
        for index, (surface, segment, value, path, kind) in enumerate(COMPONENT_ROWS, 1)
    ]

    accepted_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    new_complete_rows: list[dict[str, object]] = []
    newly_exposed: list[dict[str, object]] = []
    seen_one_loci = set(base_one_loci)
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V21", "decision": "BASE",
        "dictionary_entries": len(base_dictionary), "dictionary_sha256": dictionary_hash(base_dictionary),
        **metrics(coverage, one_unknown, complete, glossary),
    }]

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if surface in glossary or GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"invalid downstream target: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        if not members:
            raise RuntimeError(f"unattested target: {surface}")
        pre_dictionary = [*base_dictionary, *accepted_rows]
        pre_coverage, pre_one, _, pre_complete = g637.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
        pre_complete_loci = {str(row["locus"]) for row in pre_complete}

        trial_glossary = {key: dict(value) for key, value in glossary.items()}
        g637.set_gloss(
            trial_glossary, surface, spec_row["working_meaning_de"], f"GDT645:ROUND_{round_number:02d}",
            "EXACT_ZL3B_WHOLE_DOWNSTREAM_COMPLETION", "KNOWN_EXACT_WHOLE", 125,
        )
        trial_coverage, trial_one, _, trial_complete = g637.build_line_coverage(by_line, trial_glossary, exact, boundary, cross_by_locus)
        trial_by_locus = {str(row["locus"]): row for row in trial_coverage}

        audit_trial_glossary = {key: dict(value) for key, value in audit_base_glossary.items()}
        g637.set_gloss(
            audit_trial_glossary, surface, spec_row["working_meaning_de"], f"GDT645:ROUND_{round_number:02d}",
            "EXACT_ZL3B_WHOLE_DOWNSTREAM_COMPLETION", "KNOWN_EXACT_WHOLE", 125,
        )
        audit_trial_coverage, _, _, _ = g637.build_line_coverage(by_line, audit_trial_glossary, exact, boundary, cross_by_locus)
        audit_trial_by_locus = {str(row["locus"]): row for row in audit_trial_coverage}
        verdicts: Counter[str] = Counter()
        round_audits: list[dict[str, object]] = []
        support_classes: Counter[str] = Counter()
        thermal_rivals = 0
        for member in members:
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = audit_base_by_locus[locus], audit_trial_by_locus[locus]
            support, support_note, thermal = reader_support(
                surface, cross_by_locus[locus], exact[locus, token_index], boundary[locus, token_index],
            )
            support_classes[support] += 1
            thermal_rivals += thermal
            known_other = int(before["known_tokens"])
            clean_known_other = known_other - int(before["ambiguous_tokens"]) - int(before["reader_unstable_tokens"])
            if support == "ALL_THREE_EXACT" and clean_known_other >= 2:
                verdict, reason = "CLEAN_CONTEXT_COMPATIBLE", "complete reading fits at least two clean already glossed companion positions"
            elif support == "ALL_THREE_EXACT":
                verdict, reason = "OPAQUE_OR_UNSTABLE_CONTEXT", "all-reader exact target but fewer than two clean already glossed companion positions"
            elif support == "ALL_THREE_SPLIT_NORMALIZED":
                verdict, reason = "READER_SPLIT_NORMALIZED", support_note
            else:
                verdict, reason = "READER_VARIANT_WARNING", support_note
            verdicts[verdict] += 1
            flags: list[str] = []
            if support != "ALL_THREE_EXACT":
                flags.append(support)
            if thermal:
                flags.append("THERMAL_POLARITY_RIVAL")
            if clean_known_other < 2:
                flags.append("FEWER_THAN_TWO_CLEAN_COMPANIONS")
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
                "reader_support": support, "reader_support_note": support_note,
                "reader_exact": exact[locus, token_index], "split_normalized": boundary[locus, token_index],
                "before_state": split_pipe(before["scope_states"])[ordinal - 1],
                "before_gloss": before_glosses[ordinal - 1], "after_gloss": after_glosses[ordinal - 1],
                "known_other_tokens": known_other, "clean_known_other_tokens": clean_known_other,
                "local_before_de": before["token_glosses_de"],
                "local_after_de": after["token_glosses_de"], "flags": "|".join(flags) or "NONE",
                "thermal_reader_rival": thermal, "hard_collision": 0, "verdict": verdict, "review_reason": reason,
            })
        round_audits.sort(key=lambda row: (str(row["locus"]), int(row["token_ordinal"])))
        for index, row in enumerate(round_audits, 1):
            row["audit_id"] = f"G645-A{round_number:02d}-{index:03d}"
        audit_rows.extend(round_audits)
        for row in round_audits:
            if row["reader_support"] != "ALL_THREE_EXACT":
                variant_rows.append({
                    "surface": surface, "locus": row["locus"], "zl3b_line": row["zl3b_line"],
                    "it2a_line": row["it2a_line"], "rf1b_line": row["rf1b_line"],
                    "reader_gate": spec_row["reader_gate"], "working_meaning_de": spec_row["working_meaning_de"],
                    "rival_de": spec_row["rival_de"], "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })

        if spec_row["reader_gate"] == "AT_LEAST_ONE_ALL_READER_EXACT":
            gate_pass = support_classes["ALL_THREE_EXACT"] > 0
        else:
            raise RuntimeError(f"unknown reader gate: {spec_row['reader_gate']}")
        trial_new = sorted({str(row["locus"]) for row in trial_complete} - pre_complete_loci)
        if not gate_pass or spec_row["source_locus"] not in trial_new:
            raise RuntimeError(f"downstream target failed acceptance: {surface}")

        glossary = trial_glossary
        coverage, one_unknown, complete = trial_coverage, trial_one, trial_complete
        accepted_rows.append(dictionary_row(spec_row, round_number, len(members), spec_row["reader_gate"]))
        trial_complete_by_locus = {str(row["locus"]): row for row in trial_complete}
        for locus in trial_new:
            row = trial_by_locus[locus]
            if locus not in SMOOTHED_LINES:
                raise RuntimeError(f"missing smoothed complete reading: {locus}")
            new_complete_rows.append({
                "round": round_number, "surface": surface, "page": row["page"], "locus": locus,
                "strict_complete": trial_complete_by_locus[locus]["strict_complete"],
                "zl3b_line": row["zl3b_line"], "literal_v22_de": "; ".join(split_pipe(row["token_glosses_de"])),
                "smoothed_working_reading_de": SMOOTHED_LINES[locus],
                "all_present_exact": row["all_present_exact"],
                "scope_clean": int(int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0),
            })
        current_one = {str(row["locus"]): row for row in one_unknown}
        for locus in sorted(set(current_one) - seen_one_loci):
            row = current_one[locus]
            newly_exposed.append({
                "introduced_round": round_number, "enabled_by_surface": surface,
                **{field: row[field] for field in ONE_FIELDS},
            })
        seen_one_loci.update(current_one)

        post_dictionary = [*base_dictionary, *accepted_rows]
        ledger_rows.append({
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "decision_reason": spec_row["decision_basis"], "reader_gate": spec_row["reader_gate"],
            "pre_dictionary_entries": len(pre_dictionary), "post_dictionary_entries": len(post_dictionary),
            "pre_dictionary_sha256": dictionary_hash(pre_dictionary), "post_dictionary_sha256": dictionary_hash(post_dictionary),
            "occurrences": len(members), "audited_occurrences": len(round_audits),
            "all_reader_exact": support_classes["ALL_THREE_EXACT"],
            "split_normalized": support_classes["ALL_THREE_SPLIT_NORMALIZED"],
            "reader_variant": verdicts["READER_VARIANT_WARNING"],
            "clean_context_compatible": verdicts["CLEAN_CONTEXT_COMPATIBLE"],
            "opaque_or_unstable_context": verdicts["OPAQUE_OR_UNSTABLE_CONTEXT"],
            "thermal_reader_rivals": thermal_rivals, "hard_collisions": 0,
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_complete_loci": "|".join(trial_new),
        })
        round_rows.append({
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": dictionary_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })
        target_deck.append({
            "candidate_id": f"G645-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "source_locus": spec_row["source_locus"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "scope": spec_row["scope"], "rival_de": spec_row["rival_de"],
            "occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in round_audits),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in round_audits),
            "reader_gate": spec_row["reader_gate"], "decision": "ACCEPT", "decision_basis": spec_row["decision_basis"],
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
            "source_locus": next(item["source_locus"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
            "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        }
        for row in accepted_rows
    ]

    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    expected_final_metrics = {
        "physical_lines": 4128, "known_token_positions": 10345,
        "unknown_token_positions": 21994, "complete_multi_token_lines": 60,
        "strict_complete_lines": 42, "one_unknown_lines": 71,
        "strict_one_unknown_lines": 22, "exact_glossary_surfaces": 256,
    }
    verdict_counts = Counter(str(row["verdict"]) for row in audit_rows)
    expected_verdicts = Counter({
        "CLEAN_CONTEXT_COMPATIBLE": 60,
        "OPAQUE_OR_UNSTABLE_CONTEXT": 45,
        "READER_VARIANT_WARNING": 10,
    })
    exact_target_state = (
        [row["surface"] for row in target_deck], len(accepted_rows), len(audit_rows),
        sum(int(row["reader_exact"]) for row in audit_rows),
        sum(int(row["split_normalized"]) for row in audit_rows),
        len(variant_rows), verdict_counts, len(family_rows), len(component_rows),
        len(new_complete_rows), len(newly_exposed), len(final_dictionary), len(glossary),
    )
    expected_target_state = (
        ["oky", "otchor", "ychair", "cheaiin", "cthom"], 5, 115, 105, 105,
        10, expected_verdicts, 68, 14, 6, 2, 303, 256,
    )
    if exact_target_state != expected_target_state:
        raise RuntimeError(f"GDT645 target invariant changed: {exact_target_state!r}")
    if final_metrics != expected_final_metrics:
        raise RuntimeError(f"GDT645 final metrics changed: {final_metrics!r}")
    if {str(row["locus"]) for row in new_complete_rows} != {
        "f36v.13", "f35r.14", "f18r.12", "f19v.14", "f4r.7", "f6r.12",
    }:
        raise RuntimeError("GDT645 completion locus set changed")
    if {str(row["unknown_surface"]) for row in newly_exposed} != {"s", "tcheey"}:
        raise RuntimeError(
            f"GDT645 newly exposed surface set changed: "
            f"{sorted(str(row['unknown_surface']) for row in newly_exposed)!r}"
        )

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "source_locus", "working_meaning_de", "composition",
        "scope", "rival_de", "occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences",
        "reader_gate", "decision", "decision_basis",
    ))
    write_tsv(output_dir / "FORM_FAMILY_ATLAS.tsv", family_rows, (
        "family", "surface", "zl3b_occurrences", "pages", "reader_exact_occurrences", "cross_reader_only",
        "surface_status", "working_reading_de",
    ))
    write_tsv(output_dir / "COMPONENT_BINDING_AUDIT.tsv", component_rows, (
        "component_id", "surface", "segment", "working_value_de", "evidence_path", "evidence_kind", "licensed_use",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_gate",
        "working_meaning_de", "rival_de", "decision",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "page", "locus", "section", "language", "hand", "token_ordinal",
        "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "reader_support_note", "reader_exact", "split_normalized", "before_state", "before_gloss", "after_gloss",
        "known_other_tokens", "clean_known_other_tokens", "local_before_de", "local_after_de", "flags", "thermal_reader_rival",
        "hard_collision", "verdict", "review_reason",
    ))
    write_tsv(output_dir / "SEQUENTIAL_DECISION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "decision", "decision_reason", "reader_gate", "pre_dictionary_entries",
        "post_dictionary_entries", "pre_dictionary_sha256", "post_dictionary_sha256", "occurrences",
        "audited_occurrences", "all_reader_exact", "split_normalized", "reader_variant", "clean_context_compatible",
        "opaque_or_unstable_context", "thermal_reader_rivals", "hard_collisions", "complete_before", "complete_after",
        "strict_complete_after", "one_unknown_before", "one_unknown_after", "new_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "decision", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "accepted_round", "source_locus", "occurrences",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "round", "surface", "page", "locus", "strict_complete", "zl3b_line", "literal_v22_de",
        "smoothed_working_reading_de", "all_present_exact", "scope_clean",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V22_EXACT_TOKEN_GLOSSARY.tsv", final_glossary_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V22.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V22.tsv", final_complete, ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V22.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V22.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        *INHERITED_HELPER_RUN_RELS,
        G644_RUN_REL, G644_ALLOW_REL, G644_COVERAGE_REL, G644_COMPLETE_REL, G644_ONE_REL,
        G644_NEW_ONE_REL, G644_GLOSSARY_REL, G644_DICT_REL, G644_RESULT_REL, G644_REPORT_REL,
        G529_REPORT_REL, G624_REPORT_REL, G624_GRID_REL, G626_REPORT_REL, G628_REPORT_REL,
        G631_REPORT_REL, G633_REPORT_REL, G636_REPORT_REL, G639_REPORT_REL, G640_REPORT_REL,
        TOKENS_REL, CROSS_REL,
    )
    result_core = {
        "schema": "GDT645_RANKED_FIVE_SURFACE_COMPLETION_RESULT_V1",
        "experiment_id": "GDT645", "status": STATUS,
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
            "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats,
        },
        "target_run": {
            "candidates": len(target_deck), "accepted": len(accepted_rows), "held": 0,
            "audited_occurrences": len(audit_rows), "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "thermal_reader_rivals": sum(int(row["thermal_reader_rival"]) for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdict_counts.items())), "accepted_surfaces": [row["surface"] for row in target_deck],
        },
        "coverage": {
            "base_complete_multi_token_lines": len(old_complete),
            "base_strict_complete_lines": sum(int(row["strict_complete"]) for row in old_complete),
            "newly_completed_lines": len({str(row["locus"]) for row in final_complete} - base_complete_loci),
            "newly_exposed_one_hole_lines": len(newly_exposed), **final_metrics,
        },
        "working_dictionary": {
            "v21_entries": len(base_dictionary), "v22_entries": len(final_dictionary),
            "accepted_tail_entries": len(accepted_rows), "v21_prefix_sha256": dictionary_hash(base_dictionary),
            "v22_sha256": dictionary_hash(final_dictionary), "base_glossary_surfaces": len(old_glossary),
            "v22_glossary_surfaces": len(glossary),
        },
        "claim_boundary": (
            "GDT645 promotes the five strongest exact whole surfaces on the GDT644 one-hole frontier with replaceable working readings. "
            "oky=hot preparation/base form, otchor=cold-dry drug portion in the preparation, ychair=second dry portion of this drug, "
            "cheaiin=dry in the third degree, and cthom=one handful of leaf/herb preparation render all 115 target positions and close six lines; "
            "105 positions are all-reader exact. The cthom handful is a period-informed exact-whole hypothesis, not a free m reading. "
            "The values of initial y in ychair, air, a+iin and terminal m remain bound to their complete surfaces. No bare component, "
            "substring, absent cell, plaintext, phonetics or language identification is promoted."
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
        f"GDT645 built: accepted={run['accepted']} audits={run['audited_occurrences']} "
        f"complete={coverage['complete_multi_token_lines']} strict={coverage['strict_complete_lines']} "
        f"one_unknown={coverage['one_unknown_lines']} known={coverage['known_token_positions']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
