#!/usr/bin/env python3
"""Build GDT650: close five strict V26 holes with concrete family readings."""
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
BASE_REL = Path("experiments/yolo/gdt650_v26_strict_family_completion")
ART = ROOT / BASE_REL / "artifacts"
G649 = Path("experiments/yolo/gdt649_strict_v25_hole_completion")
G649_RUN = G649 / "src/run.py"
G649_ALLOW = G649 / "artifacts/PAGE_ALLOWLIST.tsv"
G649_COVERAGE = G649 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V26.tsv"
G649_COMPLETE = G649 / "artifacts/COMPLETE_PASSAGES_V26.tsv"
G649_ONE = G649 / "artifacts/ONE_UNKNOWN_PASSAGES_V26.tsv"
G649_GLOSSARY = G649 / "artifacts/V26_EXACT_TOKEN_GLOSSARY.tsv"
G649_DICTIONARY = G649 / "artifacts/WORKING_DICTIONARY_V26.tsv"
G649_RESULT = G649 / "artifacts/RESULT.json"
G649_REPORT = G649 / "REPORT.md"
G628_REPORT = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G633_REPORT = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G635_REPORT = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps/REPORT.md")
G636_REPORT = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G642_REPORT = Path("experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/REPORT.md")
G644_REPORT = Path("experiments/yolo/gdt644_downstream_five_surface_completion/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt649_builder_for_gdt650", ROOT / G649_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT649 builder")
g649 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g649)
g637 = g649.g637
TOKENS_REL = g649.TOKENS_REL
CROSS_REL = g649.CROSS_REL
COVERAGE_FIELDS = g649.COVERAGE_FIELDS
ONE_FIELDS = g649.ONE_FIELDS

STATUS = "PASS_7_EXACT_WHOLES__V27_FIVE_STRICT_FAMILIES_CLOSED"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)

# The sidequest explicitly permits replaceable meanings before proof. The tier
# field keeps that permission visible instead of flattening every card to the
# same confidence. Every value is nevertheless concrete enough to render a
# passage and every card remains bound to the exact complete surface.
CANDIDATE_SPECS = (
    {
        "surface": "otcho", "source_locus": "f14r.7", "strict_source": "1",
        "family": "OTCHO_COLD_DRY_PREPARATION", "tier": "STRONG_ATTESTED_FAMILY",
        "working_meaning_de": "kalt-trockene Zubereitung", "composition": "o+(t+ch)+o",
        "rival_de": "kalter Ansatz",
        "decision_basis": "six of seven tokens are all-reader exact; the populated TCHO/OTCHO/QOTCHO closure family and a separated o tcho bridge preserve cold plus dry plus preparation",
        "counterargument": "CH may be lexicalized inside CHO, in which case only cold preparation is secure",
    },
    {
        "surface": "cholor", "source_locus": "f10r.8", "strict_source": "1",
        "family": "CHOL_OR_FUSED_INGREDIENT", "tier": "PROVISIONAL_BOUNDARY_FAMILY",
        "working_meaning_de": "trockene Zutat", "composition": "chol+or",
        "rival_de": "Anteil oder Portion Trockengut",
        "decision_basis": "four all-reader-exact chol or spans plus ol or versus olor and sholor versus shol or establish the visible CHOL+OR fusion family",
        "counterargument": "the literal carrier reading is portion of dry material; ingredient is the shorter workshop-level interpretation",
    },
    {
        "surface": "sheo", "source_locus": "f85r2.4", "strict_source": "1",
        "family": "SH_E_O_PREPARATION_SHELL", "tier": "STRONG_COMPOSITIONAL_SHELL",
        "working_meaning_de": "Feuchtzubereitung", "composition": "sh+e+o",
        "rival_de": "feucht gebundene Zubereitung; Listenfortsetzungsmarker",
        "decision_basis": "the complete CH/SH by E/no-E by O/no-O shell and the sheo cthody boundary bridge identify a moist attributively bound preparation shell",
        "counterargument": "thirty-six of thirty-seven occurrences are medial, so a list-linking role remains a distributional rival",
    },
    {
        "surface": "ycheol", "source_locus": "f108r.34", "strict_source": "1",
        "family": "LOCAL_Y_CH_E_OL_ENTRY", "tier": "STRONG_LOCAL_ENTRY_FAMILY",
        "working_meaning_de": "trockener Drogenstoff dieser Droge", "composition": "y|(ch+e+ol)",
        "rival_de": "Eintrag: trockener Drogenstoff",
        "decision_basis": "the complete Y+CH+E/no-E+OL/OR raster is overwhelmingly line-initial and multiple readers alternate ycheol with y cheol",
        "counterargument": "Y may frame the entry rather than encode an anaphoric current-drug relation",
    },
    {
        "surface": "sheckhy", "source_locus": "f103r.23", "strict_source": "1",
        "family": "SH_E_CKH_SUBDEGREE", "tier": "EXPLORATORY_LEARNED_CKH_HEAD",
        "working_meaning_de": "feuchte Arzneimischung, Anfangsgrad, gebunden", "composition": "sh+e+CKH_LEARNED+y",
        "rival_de": "feuchtes CKH-Drogengut, Anfangsgrad, gebunden",
        "decision_basis": "SHCKH/SHECKH sisters and direct shckhy sheckhy contacts preserve SH plus outer E plus the V26 learned CKH head plus the subdegree ending",
        "counterargument": "Arzneimischung remains a replaceable family noun; CKH has no independently identified object value",
    },
    {
        "surface": "sheckhey", "source_locus": "NONE", "strict_source": "0",
        "family": "SH_E_CKH_SUBDEGREE", "tier": "EXPLORATORY_LEARNED_CKH_HEAD",
        "working_meaning_de": "feuchte Arzneimischung, Mittelgrad, gebunden", "composition": "sh+e+CKH_LEARNED+e+y",
        "rival_de": "feuchtes CKH-Drogengut, Mittelgrad, gebunden",
        "decision_basis": "all four occurrences are all-reader exact and fill the middle cell beside SHECKHY and SHECKHEDY",
        "counterargument": "the CKH object noun remains learned rather than independently decoded",
    },
    {
        "surface": "sheckhedy", "source_locus": "NONE", "strict_source": "0",
        "family": "SH_E_CKH_SUBDEGREE", "tier": "EXPLORATORY_LEARNED_CKH_HEAD",
        "working_meaning_de": "feuchte Arzneimischung, Mittelgrad, gebunden und abgeschlossen", "composition": "sh+e+CKH_LEARNED+e+d+y",
        "rival_de": "feuchtes CKH-Drogengut, Mittelgrad, gebunden und abgeschlossen",
        "decision_basis": "three of four occurrences are all-reader exact and the d/no-d pair repeats the V26 completed-state contrast",
        "counterargument": "the CKH object noun and the completed-state reading remain replaceable family defaults",
    },
)

FAMILY_FORMS = (
    ("OTCHO_COLD_DRY_PREPARATION", "tcho", "(t+ch)+o", "kalt-trockene Zubereitung", "SISTER"),
    ("OTCHO_COLD_DRY_PREPARATION", "tchod", "(t+ch)+o+d", "kalt-trockene Zubereitung, gebunden", "SISTER"),
    ("OTCHO_COLD_DRY_PREPARATION", "tchody", "(t+ch)+o+d+y", "kalt-trockene Zubereitung, abgeschlossene Grundform", "SISTER"),
    ("OTCHO_COLD_DRY_PREPARATION", "otcho", "o+(t+ch)+o", "kalt-trockene Zubereitung", "TARGET"),
    ("OTCHO_COLD_DRY_PREPARATION", "otchod", "o+(t+ch)+o+d", "kalt-trockene Zubereitung im O-Rahmen, gebunden", "SISTER"),
    ("OTCHO_COLD_DRY_PREPARATION", "otchody", "o+(t+ch)+o+d+y", "kalt-trockene Zubereitung im O-Rahmen, abgeschlossene Grundform", "SISTER"),
    ("OTCHO_COLD_DRY_PREPARATION", "qotcho", "qo+(t+ch)+o", "kalt-trockene Zubereitung im QO-Rahmen", "SISTER"),
    ("OTCHO_COLD_DRY_PREPARATION", "qotchod", "qo+(t+ch)+o+d", "kalt-trockene Zubereitung, fertig gebunden", "V26_ANCHOR"),
    ("OTCHO_COLD_DRY_PREPARATION", "qotchody", "qo+(t+ch)+o+d+y", "kalt-trockene Zubereitung im QO-Rahmen, abgeschlossene Grundform", "SISTER"),
    ("CHOL_OR_FUSED_INGREDIENT", "ol", "ol", "Materialträger", "V26_ANCHOR"),
    ("CHOL_OR_FUSED_INGREDIENT", "or", "or", "Anteil oder Portion", "V26_ANCHOR"),
    ("CHOL_OR_FUSED_INGREDIENT", "olor", "ol+or", "Zutat", "V26_ANCHOR"),
    ("CHOL_OR_FUSED_INGREDIENT", "chol", "ch+ol", "Trockengut", "V26_ANCHOR"),
    ("CHOL_OR_FUSED_INGREDIENT", "cholor", "chol+or", "trockene Zutat", "TARGET"),
    ("CHOL_OR_FUSED_INGREDIENT", "sholor", "shol+or", "feuchte Zutat", "SISTER"),
    ("CHOL_OR_FUSED_INGREDIENT", "tolor", "tol+or", "kalte Zutat", "SISTER_LOW_N"),
    ("SH_E_O_PREPARATION_SHELL", "cho", "ch+o", "Trockenansatz", "SISTER"),
    ("SH_E_O_PREPARATION_SHELL", "cheo", "ch+e+o", "trocken gebundene Zubereitung", "V26_ANCHOR"),
    ("SH_E_O_PREPARATION_SHELL", "sho", "sh+o", "Feuchtansatz", "V26_ANCHOR"),
    ("SH_E_O_PREPARATION_SHELL", "sheo", "sh+e+o", "Feuchtzubereitung", "TARGET"),
    ("LOCAL_Y_CH_E_OL_ENTRY", "ychol", "y|(ch+ol)", "Trockengut dieser Droge", "SISTER"),
    ("LOCAL_Y_CH_E_OL_ENTRY", "ycheol", "y|(ch+e+ol)", "trockener Drogenstoff dieser Droge", "TARGET"),
    ("LOCAL_Y_CH_E_OL_ENTRY", "ychor", "y|(ch+or)", "trockener Anteil dieser Droge", "SISTER"),
    ("LOCAL_Y_CH_E_OL_ENTRY", "ycheor", "y|(ch+e+or)", "trockener Drogenteil dieser Droge", "SISTER"),
    ("SH_E_CKH_SUBDEGREE", "shckhy", "sh+CKH_LEARNED+y", "feuchte Arzneimischung, Anfangsgrad", "SISTER"),
    ("SH_E_CKH_SUBDEGREE", "shckhey", "sh+CKH_LEARNED+e+y", "feuchte Arzneimischung, Mittelgrad", "SISTER"),
    ("SH_E_CKH_SUBDEGREE", "shckhdy", "sh+CKH_LEARNED+d+y", "feuchte Arzneimischung, Anfangsgrad, abgeschlossen", "SISTER_LOW_N"),
    ("SH_E_CKH_SUBDEGREE", "shckhedy", "sh+CKH_LEARNED+e+d+y", "feuchte Arzneimischung, Mittelgrad, abgeschlossen", "SISTER"),
    ("SH_E_CKH_SUBDEGREE", "sheckhy", "sh+e+CKH_LEARNED+y", "feuchte Arzneimischung, Anfangsgrad, gebunden", "TARGET"),
    ("SH_E_CKH_SUBDEGREE", "sheckhey", "sh+e+CKH_LEARNED+e+y", "feuchte Arzneimischung, Mittelgrad, gebunden", "TARGET"),
    ("SH_E_CKH_SUBDEGREE", "sheckheey", "sh+e+CKH_LEARNED+ee+y", "feuchte Arzneimischung, Endgrad, gebunden", "ABSENT_PREDICTION"),
    ("SH_E_CKH_SUBDEGREE", "sheckhdy", "sh+e+CKH_LEARNED+d+y", "feuchte Arzneimischung, Anfangsgrad, gebunden und abgeschlossen", "HELD_ZERO_EXACT"),
    ("SH_E_CKH_SUBDEGREE", "sheckhedy", "sh+e+CKH_LEARNED+e+d+y", "feuchte Arzneimischung, Mittelgrad, gebunden und abgeschlossen", "TARGET"),
    ("SH_E_CKH_SUBDEGREE", "sheckheedy", "sh+e+CKH_LEARNED+ee+d+y", "feuchte Arzneimischung, Endgrad, gebunden und abgeschlossen", "ABSENT_PREDICTION"),
)

BRIDGE_SPECS = (
    ("G650-B01", "OTCHO_COLD_DRY_PREPARATION", "f47v.10", "o tcho", "separated O plus TCHO witness"),
    ("G650-B02", "OTCHO_COLD_DRY_PREPARATION", "f2v.6", "o tchor|otchor", "same-span O plus TCHOR boundary alternation"),
    ("G650-B03", "CHOL_OR_FUSED_INGREDIENT", "f49r.6", "ol or|olor", "OL OR versus OLOR boundary alternation"),
    ("G650-B04", "CHOL_OR_FUSED_INGREDIENT", "f86v3.22", "sholor|shol or", "SHOLOR versus SHOL OR boundary alternation"),
    ("G650-B05", "CHOL_OR_FUSED_INGREDIENT", "f10r.3", "chol or", "all-reader separated CHOL OR witness"),
    ("G650-B06", "CHOL_OR_FUSED_INGREDIENT", "f17r.3", "chol or", "all-reader separated CHOL OR witness"),
    ("G650-B07", "CHOL_OR_FUSED_INGREDIENT", "f24v.9", "chol or", "all-reader separated CHOL OR witness"),
    ("G650-B08", "CHOL_OR_FUSED_INGREDIENT", "f39r.4", "chol or", "all-reader separated CHOL OR witness"),
    ("G650-B09", "LOCAL_Y_CH_E_OL_ENTRY", "f24r.18", "ycheol|y cheol", "Y CHEOL fused/split reader alternation"),
    ("G650-B10", "LOCAL_Y_CH_E_OL_ENTRY", "f112v.40", "y cheol", "all-reader separated Y CHEOL witness"),
    ("G650-B11", "LOCAL_Y_CH_E_OL_ENTRY", "f95r2.8", "y cheol|ycheol", "Y CHEOL fused/split reader alternation"),
    ("G650-B12", "LOCAL_Y_CH_E_OL_ENTRY", "f102v1.12", "y cheol|ycheol", "Y CHEOL fused/split reader alternation"),
    ("G650-B13", "LOCAL_Y_CH_E_OL_ENTRY", "f113v.48", "y cheol|ycheol", "Y CHEOL fused/split reader alternation"),
    ("G650-B14", "LOCAL_Y_CH_E_OL_ENTRY", "f114v.32", "y cheol|ycheol", "Y CHEOL fused/split reader alternation"),
    ("G650-B15", "SH_E_CKH_SUBDEGREE", "f103v.45", "shckhy sheckhy", "direct E/no-E SHECKH sister contact"),
    ("G650-B16", "SH_E_CKH_SUBDEGREE", "f80r.43", "sheckhy checkhy sheckhy", "SH-E and CH-E CKH sister contact"),
)

SMOOTHED_SOURCE_LINES = {
    "f10r.8": "Kalt-trockene Drogenportion; Pflanzenteil; kaltes Zubereitungsgut; Trockengut; trockene Zutat; Trockengut im dritten Grad; abgemessene Fraktion I.",
    "f14r.7": "Kalt-trockene Zubereitung; Grad- oder Maßwert II; trockene Arzneimischung am Anfangsgrad.",
    "f32r.13": "Kalt-trockene Zubereitung; Wurzelstoff; Qualitätsgrad II; Grad- oder Maßwert III; CTH-Drogenmaterial.",
    "f81r.23": "Trocken im Mittelgrad; heißer Ansatz Grad II; gebundene feuchte Arzneimischung am Anfangsgrad; Samenzubereitung Form III; trocken im Mittelgrad; getrocknetes Drogenholz Form I.",
    "f85r2.4": "Abgemessene Fraktion II; Feuchtzubereitung, Portion III; Trockengut im dritten Grad.",
    "f103r.23": "Grad- oder Maßwert III; gebundene feuchte Arzneimischung am Anfangsgrad; getrocknetes Drogenholz; trockene Arzneimischung am Anfangsgrad; Feuchtgut.",
    "f108r.34": "Trockener Drogenstoff dieser Droge; trockene Arzneimischung am Anfangsgrad; heiß im Mittelgrad und abgeschlossen; heißer Ansatz Grad II.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_EVIDENCE_ATLAS.tsv",
    "BOUNDARY_BRIDGE_ATLAS.tsv", "RISK_AND_RIVAL_REGISTER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "AFFECTED_LINE_TRANSLATIONS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V27_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V27.tsv",
    "COMPLETE_PASSAGES_V27.tsv", "ONE_UNKNOWN_PASSAGES_V27.tsv",
    "WORKING_DICTIONARY_V27.tsv",
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


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int, exact_count: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT650_EXACT_WHOLE",
        "kind": f"EXACT_ZL3B_WHOLE_{spec_row['tier']}",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; tier={spec_row['tier']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; learned components remain family-bound"
        ),
        "status": f"NEW_V27_ACCEPTED_ROUND_{round_number:02d}",
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G649_ALLOW)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G649_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G649_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G649_COVERAGE)
    base_complete = read_tsv(ROOT / G649_COMPLETE)
    base_one = read_tsv(ROOT / G649_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (428, 365, 4128, 96, 158):
        raise RuntimeError("GDT649 V26 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT649 V26 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 14516,
        "unknown_token_positions": 17823, "complete_multi_token_lines": 96,
        "strict_complete_lines": 53, "one_unknown_lines": 158,
        "strict_one_unknown_lines": 46, "exact_glossary_surfaces": 365,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT649 V26 metrics changed: {base_metrics!r}")

    targets = {str(row["surface"]) for row in CANDIDATE_SPECS}
    if targets & set(base_glossary):
        raise RuntimeError("a GDT650 target is already in the V26 glossary")
    strict_source = {str(row["surface"]): str(row["source_locus"]) for row in CANDIDATE_SPECS if row["strict_source"] == "1"}
    source_pairs = {(row["unknown_surface"], row["locus"]): row for row in base_one}
    for surface, locus in strict_source.items():
        source = source_pairs.get((surface, locus))
        if source is None or int(source["strict_eligible"]) != 1:
            raise RuntimeError(f"strict GDT649 source frontier changed: {(surface, locus)}")
    if strict_source != {
        "otcho": "f14r.7", "cholor": "f10r.8", "sheo": "f85r2.4",
        "ycheol": "f108r.34", "sheckhy": "f103r.23",
    }:
        raise RuntimeError("strict source deck changed")

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    family_rows: list[dict[str, object]] = []
    for family, surface, composition, reading, planned_status in FAMILY_FORMS:
        members = [row for row in token_rows if row["eva"] == surface]
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        normalized_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        family_rows.append({
            "family": family, "surface": surface, "composition": composition,
            "predicted_reading_de": reading, "zl3b_occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": normalized_count,
            "planned_status": planned_status,
            "final_status": (
                "ACCEPTED_V27" if surface in targets else
                "V26_ANCHOR" if surface in base_glossary else
                "ABSENT_HOLD" if not members else planned_status
            ),
        })

    bridge_rows: list[dict[str, object]] = []
    for bridge_id, family, locus, diagnostic, support in BRIDGE_SPECS:
        row = cross_by_locus.get(locus)
        if row is None:
            raise RuntimeError(f"missing bridge locus: {locus}")
        bridge_rows.append({
            "bridge_id": bridge_id, "family": family, "page": row["page"], "locus": locus,
            "diagnostic_surface": diagnostic, "zl3b_line": row["zl3b_clean"],
            "it2a_line": row["it2a_clean"], "rf1b_line": row["rf1b_clean"],
            "supports": support,
        })

    glossary = {key: dict(value) for key, value in base_glossary.items()}
    coverage, one_unknown, complete = replay_coverage, replay_one, replay_complete
    base_complete_loci = {row["locus"] for row in base_complete}
    seen_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    newly_exposed_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V26", "tier": "BASE", "dictionary_entries": len(base_dictionary),
        "dictionary_sha256": canonical_hash(base_dictionary), **base_metrics,
    }]

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"generic filler in target: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        if not members or len(members) != token_counts[surface]:
            raise RuntimeError(f"target occurrence drift: {surface}")
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        split_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        if exact_count == 0:
            raise RuntimeError(f"accepted target lacks an all-reader exact anchor: {surface}")

        pre_coverage, pre_one, pre_complete = coverage, one_unknown, complete
        pre_by_locus = {row["locus"]: row for row in pre_coverage}
        pre_complete_loci = {row["locus"] for row in pre_complete}
        if spec_row["strict_source"] == "1":
            source = {row["locus"]: row for row in pre_one}.get(spec_row["source_locus"])
            if source is None or source["unknown_surface"] != surface or int(source["strict_eligible"]) != 1:
                raise RuntimeError(f"source line no longer strict one-hole: {surface}")

        g637.set_gloss(
            glossary, surface, spec_row["working_meaning_de"], f"GDT650:{spec_row['tier']}",
            "EXACT_WHOLE_FAMILY_EXTENSION", "KNOWN_EXACT_WHOLE", 145,
        )
        coverage, one_unknown, _, complete = g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        post_by_locus = {row["locus"]: row for row in coverage}
        new_complete_loci = sorted({row["locus"] for row in complete} - pre_complete_loci)
        if spec_row["strict_source"] == "1" and spec_row["source_locus"] not in new_complete_loci:
            raise RuntimeError(f"target failed to close strict source: {surface}")

        verdicts: Counter[str] = Counter()
        members.sort(key=lambda row: (row["page"], row["locus"], int(row["token_index"])))
        for occurrence, member in enumerate(members, 1):
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = pre_by_locus[locus], post_by_locus[locus]
            before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
            reader_exact = exact[locus, token_index]
            normalized = boundary[locus, token_index]
            support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "READER_VARIANT"
            known_other = int(before["known_tokens"])
            clean_other = known_other - int(before["ambiguous_tokens"]) - int(before["reader_unstable_tokens"])
            if support == "READER_VARIANT":
                verdict = "READER_VARIANT_WARNING"
            elif spec_row["tier"].startswith("EXPLORATORY"):
                verdict = "EXPLORATORY_CONTEXT_NO_RECORDED_COLLISION" if clean_other >= 2 else "EXPLORATORY_SHORT_OR_OPAQUE"
            elif clean_other >= 2:
                verdict = "FAMILY_CONTEXT_COMPATIBLE"
            else:
                verdict = "SHORT_OR_OPAQUE_CONTEXT"
            verdicts[verdict] += 1
            audit_rows.append({
                "audit_id": f"G650-A{round_number:02d}-{occurrence:03d}", "round": round_number,
                "surface": surface, "tier": spec_row["tier"], "page": member["page"], "locus": locus,
                "section": member["section"], "language": member["language"], "hand": member["hand"],
                "token_ordinal": ordinal,
                "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                "reader_exact": reader_exact, "split_normalized": normalized,
                "before_gloss_de": before_glosses[ordinal - 1], "after_gloss_de": after_glosses[ordinal - 1],
                "known_other_tokens": known_other, "clean_known_other_tokens": clean_other,
                "local_before_de": before["token_glosses_de"], "local_after_de": after["token_glosses_de"],
                "hard_collision": 0, "verdict": verdict,
            })
            if support != "ALL_THREE_EXACT":
                variant_rows.append({
                    "surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                    "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                    "working_meaning_de": spec_row["working_meaning_de"],
                    "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })

        accepted_dictionary_rows.append(dictionary_row(spec_row, round_number, len(members), exact_count))
        current_one_by_locus = {row["locus"]: row for row in one_unknown}
        for locus in sorted(set(current_one_by_locus) - seen_one_loci):
            newly_exposed_rows.append({
                "introduced_round": round_number, "enabled_by_surface": surface,
                **{field: current_one_by_locus[locus][field] for field in ONE_FIELDS},
            })
        seen_one_loci.update(current_one_by_locus)
        post_dictionary = [*base_dictionary, *accepted_dictionary_rows]
        ledger_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"], "decision": "ACCEPT_V27_EXACT_WHOLE",
            "decision_reason": spec_row["decision_basis"], "pre_dictionary_entries": len(post_dictionary) - 1,
            "post_dictionary_entries": len(post_dictionary), "occurrences": len(members),
            "all_reader_exact": exact_count, "split_normalized": split_count,
            "reader_variant": len(members) - split_count, "hard_collisions": 0,
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_complete_loci": "|".join(new_complete_loci) or "NONE",
        })
        target_deck.append({
            "candidate_id": f"G650-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "source_locus": spec_row["source_locus"], "strict_source": spec_row["strict_source"],
            "family": spec_row["family"], "acceptance_tier": spec_row["tier"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": split_count, "decision": "ACCEPT_V27_EXACT_WHOLE",
            "decision_basis": spec_row["decision_basis"], "strongest_counterargument": spec_row["counterargument"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"],
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *accepted_dictionary_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_by_locus = {row["locus"]: row for row in final_coverage}
    base_by_locus = {row["locus"]: row for row in base_coverage}
    final_complete_by_locus = {row["locus"]: row for row in final_complete}
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    final_gloss_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    accepted_defaults = [{
        "surface": row["entry"].split("@", 1)[0], **row,
        "source_locus": next(item["source_locus"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "acceptance_tier": next(item["acceptance_tier"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
    } for row in accepted_dictionary_rows]

    risk_rows = [{
        "surface": row["surface"], "acceptance_tier": row["acceptance_tier"],
        "working_meaning_de": row["working_meaning_de"], "rival_de": row["rival_de"],
        "strongest_support": row["decision_basis"], "strongest_counterargument": row["strongest_counterargument"],
        "replacement_trigger": (
            "replace the CKH noun if one better object value explains CHCKH, SHCKH and SHECKH together"
            if row["family"] == "SH_E_CKH_SUBDEGREE" else
            "replace ingredient with portion of dry material if that carrier reading yields more coherent complete lists"
            if row["surface"] == "cholor" else
            "replace the anaphoric wording with entry frame if transfer preserves position but not current-drug reference"
            if row["surface"] == "ycheol" else
            "replace if a populated sister family or repeated complete passage contradicts the assigned object and quality"
        ),
    } for row in target_deck]

    reality_rows: list[dict[str, object]] = []
    for surface, locus in strict_source.items():
        row = final_by_locus[locus]
        reality_rows.append({
            "surface": surface, "page": row["page"], "locus": locus,
            "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "zl3b_line": row["zl3b_line"], "tokenwise_translation_de": row["token_glosses_de"],
            "smoothed_working_reading_de": SMOOTHED_SOURCE_LINES[locus],
            "acceptance_tier": next(item["acceptance_tier"] for item in target_deck if item["surface"] == surface),
        })
    reality_rows.sort(key=lambda row: row["locus"])

    affected_rows: list[dict[str, object]] = []
    for locus in sorted(by_line):
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        if not present:
            continue
        row = final_by_locus[locus]
        affected_rows.append({
            "page": row["page"], "locus": locus, "target_surfaces": "|".join(present),
            "zl3b_line": row["zl3b_line"], "v26_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v27_tokenwise_de": row["token_glosses_de"],
            "v27_working_reading_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "complete_v27": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v27_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "curated_source_reading_de": SMOOTHED_SOURCE_LINES.get(locus, "NOT_CURATED_SOURCE_LINE"),
        })

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "source_locus", "strict_source", "family",
        "acceptance_tier", "working_meaning_de", "composition", "rival_de", "occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "decision", "decision_basis",
        "strongest_counterargument",
    ))
    write_tsv(output_dir / "FAMILY_EVIDENCE_ATLAS.tsv", family_rows, (
        "family", "surface", "composition", "predicted_reading_de", "zl3b_occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "planned_status", "final_status",
    ))
    write_tsv(output_dir / "BOUNDARY_BRIDGE_ATLAS.tsv", bridge_rows, (
        "bridge_id", "family", "page", "locus", "diagnostic_surface", "zl3b_line",
        "it2a_line", "rf1b_line", "supports",
    ))
    write_tsv(output_dir / "RISK_AND_RIVAL_REGISTER.tsv", risk_rows, (
        "surface", "acceptance_tier", "working_meaning_de", "rival_de", "strongest_support",
        "strongest_counterargument", "replacement_trigger",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "tier", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "reader_exact", "split_normalized", "before_gloss_de", "after_gloss_de",
        "known_other_tokens", "clean_known_other_tokens", "local_before_de", "local_after_de",
        "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "working_meaning_de", "decision",
    ))
    write_tsv(output_dir / "SEQUENTIAL_DECISION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "tier", "decision", "decision_reason", "pre_dictionary_entries",
        "post_dictionary_entries", "occurrences", "all_reader_exact", "split_normalized", "reader_variant",
        "hard_collisions", "complete_before", "complete_after", "strict_complete_after", "one_unknown_before",
        "one_unknown_after", "new_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "tier", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "source_locus", "occurrences", "acceptance_tier",
    ))
    write_tsv(output_dir / "SOURCE_PASSAGE_REALITY_CHECK.tsv", reality_rows, (
        "surface", "page", "locus", "strict_complete", "zl3b_line", "tokenwise_translation_de",
        "smoothed_working_reading_de", "acceptance_tier",
    ))
    write_tsv(output_dir / "AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, (
        "page", "locus", "target_surfaces", "zl3b_line", "v26_tokenwise_de", "v27_tokenwise_de",
        "v27_working_reading_de", "complete_v27",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v27_de",
        "curated_source_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V27_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V27.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V27.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V27.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V27.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G649_RUN, G649_ALLOW, G649_COVERAGE, G649_COMPLETE, G649_ONE,
        G649_GLOSSARY, G649_DICTIONARY, G649_RESULT, G649_REPORT,
        G628_REPORT, G633_REPORT, G635_REPORT, G636_REPORT, G642_REPORT, G644_REPORT,
        TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    tiers = Counter(row["acceptance_tier"] for row in target_deck)
    result_core = {
        "schema": "GDT650_V26_STRICT_FAMILY_COMPLETION_RESULT_V1",
        "experiment_id": "GDT650", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_exact_wholes": len(target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "strict_v26_holes_closed": len(strict_source), "acceptance_tiers": dict(sorted(tiers.items())),
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
            "held_family_cells": ["sheckhdy", "sheckheey", "sheckheedy"],
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v26_entries": len(base_dictionary), "v27_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v26_prefix_sha256": canonical_hash(base_dictionary),
                               "v27_sha256": canonical_hash(final_dictionary),
                               "v26_glossary_surfaces": len(base_glossary), "v27_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT650 is an exploratory working translation, not a solved plaintext. It adds seven exact whole-surface defaults that close five strict V26 holes. "
            "OTCHO, CHOLOR, SHEO and YCHEOL are family-led; the three SHECKH cards retain the replaceable V26 CKH object noun. CHOLOR is parsed CHOL+OR, "
            "YCHEOL keeps Y local to its entry family, and SHECKH is SH+E+CKH rather than S+HECKH. No free component, global suffix, absent cell, plaintext, "
            "phonetics, language, ingredient identity, f1r, new page or new image is asserted."
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
    target, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT650 built: accepted={target['accepted_exact_wholes']} audits={target['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
