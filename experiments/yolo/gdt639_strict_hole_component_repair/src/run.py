#!/usr/bin/env python3
"""Build GDT639: repair underread strict V15 holes with bound components."""
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
BASE_REL = Path("experiments/yolo/gdt639_strict_hole_component_repair")
ART = ROOT / BASE_REL / "artifacts"
G638_BASE = Path("experiments/yolo/gdt638_sequential_compound_promotion")
G638_RUN_REL = G638_BASE / "src/run.py"
G638_ALLOW_REL = G638_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G638_ONE_REL = G638_BASE / "artifacts/ONE_UNKNOWN_PASSAGES_V15.tsv"
G638_COVERAGE_REL = G638_BASE / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V15.tsv"
G638_COMPLETE_REL = G638_BASE / "artifacts/COMPLETE_PASSAGES_V15.tsv"
G638_GLOSSARY_REL = G638_BASE / "artifacts/V15_EXACT_TOKEN_GLOSSARY.tsv"
G638_DICT_REL = G638_BASE / "artifacts/WORKING_DICTIONARY_V15.tsv"
G638_RESULT_REL = G638_BASE / "artifacts/RESULT.json"
G627_REPORT_REL = Path("experiments/yolo/gdt627_value_head_role_atlas/REPORT.md")
G628_REPORT_REL = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G628_MATRIX_REL = Path("experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_QUALITY_CARRIER_MATRIX.tsv")
G633_REPORT_REL = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G634_REPORT_REL = Path("experiments/yolo/gdt634_known_core_terminal_semantics/REPORT.md")
G635_RUN_REL = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps/src/run.py")
G635_STATE_REL = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/STATE_BODY_HEAD_GRID.tsv")
G636_BODY_REL = Path("experiments/yolo/gdt636_residual_four_head_semantics/artifacts/RESIDUAL_BODY_DEFAULTS.tsv")

spec = importlib.util.spec_from_file_location("gdt638_builder_for_gdt639", ROOT / G638_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT638 builder helpers")
g638 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g638)
g637 = g638.g637
TOKENS_REL = g638.TOKENS_REL
CROSS_REL = g638.CROSS_REL

STATUS = "PASS_8_EXACT_COMPONENT_REPAIRS__9_NEW_COMPLETE_LINES__16_HELD_DEFAULTS"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|führe .* aus|leite .* weiter",
    re.IGNORECASE,
)

# The narrow compounds come first. okeey and shy come last because their 138
# and 95 occurrences carry the largest audit burden; shy's s+hy rival is
# excluded by the inherited parser before the round starts.
CANDIDATE_SPECS = (
    {
        "surface": "qotchor", "source_locus": "f37v.7",
        "working_meaning_de": "kalt-trockene Drogenportion",
        "composition": "qo+t+ch+or", "scope": "exact whole surface only",
        "rival_de": "kalt-trockener Teil-/Nominalträger",
        "decision_basis": "complete GDT628 qo×tch×OR cell; qotchy quality core plus bound OR part carrier",
    },
    {
        "surface": "dchol", "source_locus": "f32r.19",
        "working_meaning_de": "Maß trockenen Materials",
        "composition": "d+ch+ol", "scope": "exact whole surface only",
        "rival_de": "Trockenmaterial, Wertträger",
        "decision_basis": "free d measure head plus the inherited chol dry-material cell",
    },
    {
        "surface": "chotaiin", "source_locus": "f56v.15",
        "working_meaning_de": "trockene Zubereitung: kalt, Grad III",
        "composition": "ch+o+t+aiin", "scope": "exact whole surface only",
        "rival_de": "Trockenansatz mit Kaltwert III",
        "decision_basis": "dry field plus preparation frame plus the complete t-aiin cold-degree series",
    },
    {
        "surface": "cthar", "source_locus": "f17r.11",
        "working_meaning_de": "CTH-Drogenfraktion I; im Herbal Blatt-/Krautfraktion I",
        "composition": "cth+ar", "scope": "section-sensitive exact whole surface only",
        "rival_de": "Drogenteil/-Sortierklasse I",
        "decision_basis": "productive CTH drug head plus scoped ar fraction-class I; no bare-ar globalization",
    },
    {
        "surface": "chear", "source_locus": "f8v.17",
        "working_meaning_de": "trockene Fraktion I",
        "composition": "ch+e+ar", "scope": "exact whole surface only",
        "rival_de": "trocken gebundene Teil-/Sortierklasse I",
        "decision_basis": "dry attributive shell plus scoped ar fraction-class I; no bare-ar globalization",
    },
    {
        "surface": "odaiim", "source_locus": "f24v.16",
        "working_meaning_de": "Ansatzmaß III",
        "composition": "o+d+aiim", "scope": "singleton exact whole surface only",
        "rival_de": "Zubereitungsmaß, Mengenklasse III, mit Schlussform",
        "decision_basis": "preparation frame plus d measure head and the inherited aiim quantity-class III tail",
    },
    {
        "surface": "okeey", "source_locus": "f75v.51",
        "working_meaning_de": "heißer Ansatz, Bindungsstufe II",
        "composition": "o+k+ee+y", "scope": "exact whole surface only",
        "rival_de": "heiße Zubereitung, Form II",
        "decision_basis": "preparation frame plus hot field, ee binding stage II and base closure; qokeeo/qokeedy are inherited parallels",
    },
    {
        "surface": "shy", "source_locus": "f83r.36",
        "working_meaning_de": "feucht, Grundform",
        "composition": "sh+y", "scope": "exact whole surface only; initial s-head parse forbidden",
        "rival_de": "Feuchtzustand in unmarkierter Form",
        "decision_basis": "GDT635 fixes shy/shey/sheey as the moist base/I/II ladder and explicitly excludes sh from s-head parsing",
    },
)

# Every strict V15 hole gets a default. Only the six candidates above are
# eligible for V16; the other defaults stay visible and replaceable.
STRICT_DEFAULTS = {
    "keechy": ("heiß-trockene Grundform, Bindungsstufe II", "k+ee+ch+y", "EE_CH_Y_FIELD_ORDER_UNBOUND"),
    "chokshy": ("Trockenpräparat aus heiß-feuchter Droge, Grundform", "ch+o+(k+sh+y)", "TWO_SCOPE_PARSE_NOT_YET_BOUND"),
    "shy": ("feucht, Grundform", "sh+y", "TRIAL"),
    "yty": ("Grundrahmen: kalte Grundform", "y+t+y", "OUTER_Y_SCOPE_UNBOUND"),
    "chotaiin": ("trockene Zubereitung: kalt, Grad III", "ch+o+t+aiin", "TRIAL"),
    "cthar": ("CTH-Drogenfraktion I; im Herbal Blatt-/Krautfraktion I", "cth+ar", "TRIAL_EXACT_ONLY"),
    "cpholdy": ("CPH-Drogenmaterial, gebundene Abschlussform", "cph+ol+dy", "CPH_HEAD_UNBOUND"),
    "cheockhy": ("trocken gebundene heiße Zubereitungsform", "ch+e+o+ckhy", "CKHY_REMAINDER_UNBOUND"),
    "chckhal": ("trocken-heißer Rohstoffträger", "ch+ckh+al", "CKH_SEGMENT_AND_AL_SCOPE_UNBOUND"),
    "chear": ("trockene Fraktion I", "ch+e+ar", "TRIAL_EXACT_ONLY"),
    "dchol": ("Maß trockenen Materials", "d+ch+ol", "TRIAL"),
    "ytoryd": ("kalte Drogenportion, gebundene Abschlussform", "y+t+or+y+d", "SINGLETON_FIELD_ORDER_UNBOUND"),
    "qol": ("Material im qo-Rahmen", "q+ol", "Q_ROLE_UNGROUNDED"),
    "ckhy": ("heiß-trockene Grundform im C-Rahmen", "c+k+h+y", "CKH_SEGMENTATION_UNBOUND"),
    "yto": ("kalte Zubereitung im Y-Rahmen", "y+t+o", "OPAQUE_SINGLETON_Y_SCOPE"),
    "odaiim": ("Ansatzmaß III", "o+d+aiim", "TRIAL_EXACT_ONLY"),
    "qotchor": ("kalt-trockene Drogenportion", "qo+t+ch+or", "TRIAL"),
    "sodal": ("Saatgutzubereitung, Rohstoffmaß", "s+o+d+al", "S_HEAD_REMAINDER_ODAL_UNBOUND"),
    "okeey": ("heißer Ansatz, Bindungsstufe II", "o+k+ee+y", "TRIAL_EXACT_ONLY"),
    "orol": ("Zubereitung aus Wurzelmaterial", "o+r+ol", "OR_OL_PARSE_COLLISION"),
    "olcthr": ("CTH-Drogenteil im Materialrahmen", "ol+cth+r", "SINGLETON_TERMINAL_R_UNBOUND"),
    "olekor": ("heiß gebundene Drogenportion im Materialrahmen", "ol+e+k+or", "SINGLETON_E_BRIDGE_UNBOUND"),
    "ches": ("trockene S-Form, attributiv gebunden", "ch+e+s", "S_REMAINDER_UNBOUND"),
    "ytaiin": ("Grundrahmen: kalt, Grad III", "y+t+aiin", "INITIAL_Y_SCOPE_UNBOUND"),
}

SMOOTHED_NEW_LINES = {
    "f37v.7": "Kalt-trockene Drogenportion; Menge/Portion III.",
    "f32r.19": "Materialmaß; Maß trockenen Materials; Qualitätsgrad I.",
    "f56v.15": "Kalt-trockener Zubereitungsstoff; Trockengut; Trockengut; Qualitätsgrad III; trockene Zubereitung: kalt, Grad III.",
    "f17r.11": "Kalt-trockener Zubereitungsstoff; Blatt-/Krautfraktion I; heiß im Ansatzrahmen, Grad III; Trockengut; Qualitätsgrad IV.",
    "f8v.17": "Grad-/Maßwert II; trockene Fraktion I; Grad-/Maßwert III.",
    "f24v.16": "Kalt-trockener Zubereitungsstoff; Ansatzmaß III.",
    "f75v.51": "Heißer Ansatz, Bindungsstufe II; Holzstoff.",
    "f83r.36": "Samenportion; Menge III; feuchte Grundform; feucht attributiv gebunden; eingeweichtes Drogenholz; heiße Grundform.",
    "f32r.18": "Zubereitungsmaß Form III; feuchter Ansatz; feuchte Grundform.",
}

COMPONENT_ROWS = (
    ("qotchor", "qo+t+ch", "kalt-trocken im qo-Rahmen", str(G628_MATRIX_REL), "COMPLETE_OL_OR_GRID_CELL", "exact qotchor only"),
    ("qotchor", "or", "Teil-/Nominalträger; praktisch Drogenportion", str(G628_REPORT_REL), "BOUND_OR_CARRIER", "inside exact qotchor only"),
    ("dchol", "d", "freier Wert-/Maßkopf", str(G627_REPORT_REL), "FREE_MEASURE_HEAD", "inside exact dchol only"),
    ("dchol", "chol", "trockenes Gut/Material", str(G628_REPORT_REL), "DRY_MATERIAL_CELL", "inside exact dchol only"),
    ("chotaiin", "ch+o", "trockene Zubereitung", str(G633_REPORT_REL), "DRY_PREPARATION_SHELL", "inside exact chotaiin only"),
    ("chotaiin", "t+aiin", "kalt, Grad III", str(G627_REPORT_REL), "QUALITY_DEGREE_SERIES", "inside exact chotaiin only"),
    ("cthar", "cth", "CTH-Drogenmaterial; Herbal Blatt/Kraut", str(G633_REPORT_REL), "CTH_MATERIAL_HEAD", "section-sensitive exact cthar only"),
    ("cthar", "ar", "Fraktionsklasse I", str(G636_BODY_REL), "SCOPED_RESIDUAL_BODY", "no bare-ar glossary row"),
    ("chear", "ch+e", "trocken, attributiv gebunden", str(G633_REPORT_REL), "ATTRIBUTIVE_DRY_SHELL", "inside exact chear only"),
    ("chear", "ar", "Fraktionsklasse I", str(G636_BODY_REL), "SCOPED_RESIDUAL_BODY", "no bare-ar glossary row"),
    ("odaiim", "o", "Zubereitung/Ansatz", str(G633_REPORT_REL), "PREPARATION_FRAME", "singleton exact odaiim only"),
    ("odaiim", "d+aiim", "Maß, Mengenklasse III", str(G638_DICT_REL), "BOUND_MEASURE_CLASS_TAIL", "no bare-aiim globalization"),
    ("okeey", "o+k", "heißer Ansatz", str(G633_REPORT_REL), "HOT_PREPARATION_FRAME", "exact okeey only"),
    ("okeey", "ee+y", "Bindungsstufe II, Grundform", str(G634_REPORT_REL), "EE_STAGE_AND_BASE_CLOSURE", "no transfer to keey/qokeey/okeedy"),
    ("shy", "sh", "feucht", str(G635_RUN_REL), "MOIST_STATE_AXIS", "exact shy; never s+hy"),
    ("shy", "y", "Grundform", str(G635_STATE_REL), "ZERO_E_STATE_LADDER", "exact shy; no bare-y globalization"),
)

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "STRICT_CANDIDATE_CENSUS.tsv", "COMPONENT_BINDING_AUDIT.tsv",
    "PROMOTION_CANDIDATE_DECK.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "SEQUENTIAL_PROMOTION_LEDGER.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "HELD_STRICT_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "V16_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V16.tsv", "COMPLETE_PASSAGES_V16.tsv",
    "ONE_UNKNOWN_PASSAGES_V16.tsv", "WORKING_DICTIONARY_V16.tsv",
)
COVERAGE_FIELDS = g638.COVERAGE_FIELDS
ONE_FIELDS = g638.ONE_FIELDS


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
        "entry": f"{spec_row['surface']}@GDT639_EXACT_WHOLE",
        "kind": "EXACT_WHOLE_SURFACE_COMPONENT_REPAIR",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; {occurrences} audited occurrences; {spec_row['scope']}; "
            "no substring, bare-body, wrapper or absent-cell transfer"
        ),
        "status": f"NEW_V16_ACCEPTED_ROUND_{round_number:02d}",
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
        if known_other < 2 or context_fraction < 0.5:
            flags.append("OPAQUE_OTHER_TOKENS")
        if surface in {"cthar", "chear"}:
            flags.append("AR_COMPONENT_EXACT_ONLY")
        if surface == "shy":
            flags.append("S_HEAD_PARSE_FORBIDDEN")
        if not exact[locus, token_index]:
            verdict = "READER_BOUNDARY_WARNING"
            reason = "target surface is split, fused or changed in at least one alternate reading"
        elif known_other < 2 or context_fraction < 0.5:
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
        row["audit_id"] = f"G639-A{round_number:02d}-{index:03d}"
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G638_ALLOW_REL)}
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

    base_one = read_tsv(ROOT / G638_ONE_REL)
    strict_rows = [row for row in base_one if int(row["strict_eligible"])]
    strict_by_surface = {row["unknown_surface"]: row for row in strict_rows}
    if len(strict_rows) != len(strict_by_surface) or set(strict_by_surface) != set(STRICT_DEFAULTS):
        raise RuntimeError("strict V15 candidate census changed")
    v15_dictionary: list[dict[str, object]] = [dict(row) for row in read_tsv(ROOT / G638_DICT_REL)]
    old_coverage = read_tsv(ROOT / G638_COVERAGE_REL)
    old_complete = read_tsv(ROOT / G638_COMPLETE_REL)
    old_glossary = read_tsv(ROOT / G638_GLOSSARY_REL)
    if len(v15_dictionary) != 272 or len(old_coverage) != 4128 or len(old_complete) != 30 or len(old_glossary) != 225:
        raise RuntimeError("GDT638 frozen base count changed")
    glossary = {row["surface"]: dict(row) for row in old_glossary}
    initial_glossary = {surface: dict(row) for surface, row in glossary.items()}
    initial_dictionary = [dict(row) for row in v15_dictionary]
    coverage, one_unknown, _, complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    if len(coverage) != 4128 or len(complete) != 30 or len(one_unknown) != 62:
        raise RuntimeError("replayed V15 reader count changed")
    base_complete_loci = {str(row["locus"]) for row in complete}

    all_members = Counter(row["eva"] for row in token_rows)
    census_rows: list[dict[str, object]] = []
    trial_surfaces = {spec_row["surface"] for spec_row in CANDIDATE_SPECS}
    for row in sorted(strict_rows, key=lambda item: int(item["rank"])):
        surface = row["unknown_surface"]
        meaning, composition, barrier = STRICT_DEFAULTS[surface]
        members = [item for item in token_rows if item["eva"] == surface]
        census_rows.append({
            "gdt638_rank": row["rank"], "surface": surface, "strict_locus": row["locus"],
            "occurrences": all_members[surface], "pages": len({item["page"] for item in members}),
            "reader_exact_occurrences": sum(exact[item["locus"], int(item["token_index"])] for item in members),
            "gdt638_automatic_default_de": row["proposed_default_de"],
            "default_meaning_de": meaning, "composition": composition,
            "promotion_state": "TRIAL" if surface in trial_surfaces else "HELD_FOR_NEXT_ROUTE",
            "barrier": barrier,
        })

    component_rows = [
        {
            "component_id": f"G639-B{index:02d}", "surface": surface, "segment": segment,
            "working_value_de": value, "evidence_path": evidence_path,
            "evidence_kind": kind, "licensed_use": licensed_use,
        }
        for index, (surface, segment, value, evidence_path, kind, licensed_use)
        in enumerate(COMPONENT_ROWS, 1)
    ]

    accepted_rows: list[dict[str, object]] = []
    candidate_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = []
    new_complete_rows: list[dict[str, object]] = []
    base_metrics = metrics(coverage, one_unknown, complete, glossary)
    round_rows.append({
        "round": 0, "surface": "BASE_V15", "decision": "BASE",
        "dictionary_entries": len(v15_dictionary), "dictionary_sha256": dictionary_hash(v15_dictionary),
        **base_metrics,
    })

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        source = strict_by_surface.get(surface)
        if source is None or source["locus"] != spec_row["source_locus"]:
            raise RuntimeError(f"strict source drift: {surface}")
        if surface in glossary or GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"invalid trial surface: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        pre_dictionary = [*v15_dictionary, *accepted_rows]
        pre_hash = dictionary_hash(pre_dictionary)
        pre_coverage, pre_one, _, pre_complete = g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        pre_by_locus = {str(row["locus"]): row for row in pre_coverage}
        pre_complete_loci = {str(row["locus"]) for row in pre_complete}
        pre_strict_loci = {str(row["locus"]) for row in pre_complete if int(row["strict_complete"])}

        trial_glossary = {key: dict(value) for key, value in glossary.items()}
        g637.set_gloss(
            trial_glossary, surface, spec_row["working_meaning_de"], f"GDT639:ROUND_{round_number:02d}",
            "EXACT_WHOLE_SURFACE_COMPONENT_REPAIR", "KNOWN_EXACT_WHOLE", 120,
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
        accepted = bool(
            trial_new and source_completed and exact_anchors
            and not verdicts["HARD_CONTRADICTION"] and not verdicts["NONSENSE"]
        )
        decision = "ACCEPT" if accepted else "HOLD"
        if not accepted:
            raise RuntimeError(f"bound trial failed its admission gate: {surface}")
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
        post_dictionary = [*v15_dictionary, *accepted_rows]
        post_hash = dictionary_hash(post_dictionary)
        post_metrics = metrics(coverage, one_unknown, complete, glossary)
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
            "hard_contradiction": verdicts["HARD_CONTRADICTION"], "nonsense": verdicts["NONSENSE"],
            "trial_complete_gain": len(trial_new), "trial_strict_complete_gain": len(trial_new_strict),
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "marginal_complete": len(trial_new), "strict_complete_before": len(pre_strict_loci),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "marginal_strict_complete": len(trial_new_strict),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_complete_loci": "|".join(trial_new),
            "new_strict_complete_loci": "|".join(trial_new_strict),
        })
        round_rows.append({
            "round": round_number, "surface": surface, "decision": decision,
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": post_hash,
            **post_metrics,
        })
        candidate_deck.append({
            "candidate_id": f"G639-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "gdt638_strict_rank": source["rank"],
            "gdt638_source_locus": source["locus"],
            "gdt638_default_de": source["proposed_default_de"],
            "working_meaning_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "scope": spec_row["scope"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_anchors, "decision": decision,
            "decision_basis": spec_row["decision_basis"],
        })

    final_dictionary = [*v15_dictionary, *accepted_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_complete_loci = {str(row["locus"]) for row in final_complete}
    final_glossary_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    held_rows = [
        {
            "surface": row["surface"], "strict_locus": row["strict_locus"],
            "default_meaning_de": row["default_meaning_de"], "composition": row["composition"],
            "occurrences": row["occurrences"], "reader_exact_occurrences": row["reader_exact_occurrences"],
            "decision": "HOLD", "barrier": row["barrier"],
            "status": "DEFAULT_RETAINED_OUTSIDE_V16",
        }
        for row in census_rows if row["surface"] not in trial_surfaces
    ]

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "STRICT_CANDIDATE_CENSUS.tsv", census_rows, (
        "gdt638_rank", "surface", "strict_locus", "occurrences", "pages",
        "reader_exact_occurrences", "gdt638_automatic_default_de", "default_meaning_de",
        "composition", "promotion_state", "barrier",
    ))
    write_tsv(output_dir / "COMPONENT_BINDING_AUDIT.tsv", component_rows, (
        "component_id", "surface", "segment", "working_value_de", "evidence_path",
        "evidence_kind", "licensed_use",
    ))
    write_tsv(output_dir / "PROMOTION_CANDIDATE_DECK.tsv", candidate_deck, (
        "candidate_id", "candidate_order", "surface", "gdt638_strict_rank",
        "gdt638_source_locus", "gdt638_default_de", "working_meaning_de", "composition",
        "scope", "rival_de", "occurrences", "pages", "reader_exact_occurrences",
        "decision", "decision_basis",
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
            "source_locus": next(item["gdt638_source_locus"] for item in candidate_deck if item["surface"] == row["entry"].split("@", 1)[0]),
            "occurrences": next(item["occurrences"] for item in candidate_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        }
        for row in accepted_rows
    ]
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule",
        "status", "accepted_round", "source_locus", "occurrences",
    ))
    write_tsv(output_dir / "HELD_STRICT_DEFAULTS.tsv", held_rows, (
        "surface", "strict_locus", "default_meaning_de", "composition", "occurrences",
        "reader_exact_occurrences", "decision", "barrier", "status",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "round", "surface", "page", "locus", "strict_complete", "zl3b_line",
        "before_glosses_de", "literal_after_de", "smoothed_working_reading_de",
        "all_present_exact", "scope_clean",
    ))
    write_tsv(output_dir / "V16_EXACT_TOKEN_GLOSSARY.tsv", final_glossary_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V16.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V16.tsv", final_complete,
              ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V16.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V16.tsv", final_dictionary,
              ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G638_RUN_REL, G638_ALLOW_REL, G638_ONE_REL, G638_COVERAGE_REL, G638_COMPLETE_REL,
        G638_GLOSSARY_REL, G638_DICT_REL, G638_RESULT_REL, G627_REPORT_REL, G628_REPORT_REL,
        G628_MATRIX_REL, G633_REPORT_REL, G634_REPORT_REL, G635_RUN_REL, G635_STATE_REL, G636_BODY_REL,
        TOKENS_REL, CROSS_REL,
    )
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    verdict_counts = Counter(str(row["verdict"]) for row in audit_rows)
    result_core = {
        "schema": "GDT639_STRICT_HOLE_COMPONENT_REPAIR_RESULT_V1",
        "experiment_id": "GDT639", "status": STATUS,
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "new_pages": 0, "new_images": 0, "allowed_pages": len(pages),
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "strict_census": {
            "strict_surfaces": len(census_rows), "trial_surfaces": len(candidate_deck),
            "held_defaults": len(held_rows), "every_surface_has_default": all(row["default_meaning_de"] for row in census_rows),
        },
        "candidate_run": {
            "candidates": len(candidate_deck), "accepted": len(accepted_rows), "held": 0,
            "audited_occurrences": len(audit_rows), "verdicts": dict(sorted(verdict_counts.items())),
            "accepted_surfaces": [row["surface"] for row in candidate_deck],
        },
        "coverage": {
            "base_complete_multi_token_lines": len(old_complete),
            "base_strict_complete_lines": sum(int(row["strict_complete"]) for row in old_complete),
            "newly_completed_lines": len(final_complete_loci - base_complete_loci),
            **final_metrics,
        },
        "working_dictionary": {
            "v15_entries": len(v15_dictionary), "v16_entries": len(final_dictionary),
            "accepted_tail_entries": len(accepted_rows),
            "v15_prefix_sha256": dictionary_hash(initial_dictionary),
            "v16_sha256": dictionary_hash(final_dictionary),
            "base_glossary_surfaces": len(initial_glossary), "v16_glossary_surfaces": len(glossary),
        },
        "claim_boundary": (
            "GDT639 repairs eight underread strict V15 holes only as complete exact surfaces after all-occurrence rendering. "
            "It publishes a provisional default for every other strict surface but retains sixteen outside V16. "
            "Scoped ar and y bodies are not globalized, shy cannot use the forbidden s-head parse, and no held wrapper or substring receives a global value. "
            "The readings are concrete replaceable codebook defaults, not confirmed plaintext, phonetics, historical words or a language identification."
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
    run, coverage = result["candidate_run"], result["coverage"]
    print(
        f"GDT639 built: candidates={run['candidates']} accepted={run['accepted']} "
        f"audits={run['audited_occurrences']} complete={coverage['complete_multi_token_lines']} "
        f"strict={coverage['strict_complete_lines']} one_unknown={coverage['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
