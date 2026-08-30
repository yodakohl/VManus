#!/usr/bin/env python3
"""Build GDT649: extend three V25 holes through their observed word families."""
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
BASE_REL = Path("experiments/yolo/gdt649_strict_v25_hole_completion")
ART = ROOT / BASE_REL / "artifacts"
G648 = Path("experiments/yolo/gdt648_strict_v24_hole_completion")
G648_RUN = G648 / "src/run.py"
G648_ALLOW = G648 / "artifacts/PAGE_ALLOWLIST.tsv"
G648_COVERAGE = G648 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V25.tsv"
G648_COMPLETE = G648 / "artifacts/COMPLETE_PASSAGES_V25.tsv"
G648_ONE = G648 / "artifacts/ONE_UNKNOWN_PASSAGES_V25.tsv"
G648_NEW_ONE = G648 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv"
G648_GLOSSARY = G648 / "artifacts/V25_EXACT_TOKEN_GLOSSARY.tsv"
G648_DICTIONARY = G648 / "artifacts/WORKING_DICTIONARY_V25.tsv"
G648_RESULT = G648 / "artifacts/RESULT.json"
G648_REPORT = G648 / "REPORT.md"
G627_REPORT = Path("experiments/yolo/gdt627_value_head_role_atlas/REPORT.md")
G636_REPORT = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G637_REPORT = Path("experiments/yolo/gdt637_ladder_completion_one_unknown_passages/REPORT.md")
G647_REPORT = Path("experiments/yolo/gdt647_quality_subdegree_family_migration/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt648_builder_for_gdt649", ROOT / G648_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT648 builder")
g648 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g648)
g637 = g648.g637
TOKENS_REL = g648.TOKENS_REL
CROSS_REL = g648.CROSS_REL
COVERAGE_FIELDS = g648.COVERAGE_FIELDS
ONE_FIELDS = g648.ONE_FIELDS

STATUS = "PASS_11_FAMILY_WHOLES__V26_THREE_STRICT_HOLES_CLOSED"
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
        "surface": "shoiin", "source_locus": "f28v.5", "strict_source": "1",
        "family": "DIRECT_OIIN_QUALITY_ARM", "tier": "STRONG_FAMILY_DEFAULT",
        "working_meaning_de": "Feuchtansatz, Form III", "composition": "sh+(oiin)",
        "rival_de": "feuchtes Zubereitungsgut, Klasse III",
        "decision_basis": "choiin is already dry preparation form III; shoiin supplies the all-reader-exact moist counterpart in all six occurrences",
        "counterargument": "the contexts establish a quality contrast, not water, maceration, juice or another particular moistening process",
    },
    {
        "surface": "toiin", "source_locus": "NONE", "strict_source": "0",
        "family": "DIRECT_OIIN_QUALITY_ARM", "tier": "PROVISIONAL_LOW_N_FAMILY_DEFAULT",
        "working_meaning_de": "kalte Zubereitung, Form III", "composition": "t+(oiin)",
        "rival_de": "kaltes Zubereitungsgut, Klasse III",
        "decision_basis": "the two observed tokens are all-reader exact and fill the cold member beside dry choiin and moist shoiin",
        "counterargument": "only two occurrences and no strict carrier line",
    },
    {
        "surface": "dar", "source_locus": "f78r.43", "strict_source": "0",
        "family": "D_PLUS_AR_FRACTION_LADDER", "tier": "STRONG_FAMILY_DEFAULT",
        "working_meaning_de": "abgemessene Fraktion I", "composition": "d+(ar)",
        "rival_de": "abgemessene Portion I",
        "decision_basis": "d measure head plus the attested ar/air/aiir three-step fraction ladder; six lines contain dar and dair together",
        "counterargument": "the measure head and fraction body were previously calibrated in narrower scopes",
    },
    {
        "surface": "dair", "source_locus": "f32r.7", "strict_source": "0",
        "family": "D_PLUS_AR_FRACTION_LADDER", "tier": "STRONG_FAMILY_DEFAULT",
        "working_meaning_de": "abgemessene Fraktion II", "composition": "d+(air)",
        "rival_de": "abgemessene Portion II",
        "decision_basis": "d measure head plus stage-II air; seven identical local frames exchange dar and dair",
        "counterargument": "the measure head and fraction body were previously calibrated in narrower scopes",
    },
    {
        "surface": "daiir", "source_locus": "NONE", "strict_source": "0",
        "family": "D_PLUS_AR_FRACTION_LADDER", "tier": "STRONG_FAMILY_DEFAULT",
        "working_meaning_de": "abgemessene Fraktion III", "composition": "d+(aiir)",
        "rival_de": "abgemessene Portion III",
        "decision_basis": "d measure head plus stage-III aiir; one identical frame exchanges dair and daiir",
        "counterargument": "only eight of fourteen tokens are all-reader exact",
    },
    {
        "surface": "dairodg", "source_locus": "f5v.6", "strict_source": "1",
        "family": "DAIROD_CLOSURE_MINI_LADDER", "tier": "EXPLORATORY_LEARNED_WHOLE",
        "working_meaning_de": "abgemessene Fraktion II, als Zubereitung abgeschlossen", "composition": "d+air+o+d+g",
        "rival_de": "abgemessene Fraktion II, fertig aufbereitet; Eintrag abgeschlossen",
        "decision_basis": "dair supplies measured fraction II and the observed dairo/dairod/dairody/dairodg mini-family licenses a learned complete-surface result reading",
        "counterargument": "singleton; no split bridge; terminal g is strongly final-biased but not an identified global closure suffix",
    },
    {
        "surface": "chckhy", "source_locus": "f103r.17", "strict_source": "0",
        "family": "CH_CKH_SUBDEGREE_FAMILY", "tier": "EXPLORATORY_LEARNED_HEAD_FAMILY",
        "working_meaning_de": "trockene Arzneimischung am Gradanfang", "composition": "ch+CKH_LEARNED+y",
        "rival_de": "trockenes CKH-Drogengut am Gradanfang",
        "decision_basis": "five observed cells preserve literal CH+CKH and the established y/ey/eey by optional d subdegree axis",
        "counterargument": "Arzneimischung is a learned whole-family noun; CKH has no independently identified object value",
    },
    {
        "surface": "chckhey", "source_locus": "f85r2.9", "strict_source": "0",
        "family": "CH_CKH_SUBDEGREE_FAMILY", "tier": "EXPLORATORY_LEARNED_HEAD_FAMILY",
        "working_meaning_de": "trockene Arzneimischung in der Gradmitte", "composition": "ch+CKH_LEARNED+e+y",
        "rival_de": "trockenes CKH-Drogengut in der Gradmitte",
        "decision_basis": "five observed cells preserve literal CH+CKH and the established y/ey/eey by optional d subdegree axis",
        "counterargument": "Arzneimischung is a learned whole-family noun; CKH has no independently identified object value",
    },
    {
        "surface": "chckheey", "source_locus": "NONE", "strict_source": "0",
        "family": "CH_CKH_SUBDEGREE_FAMILY", "tier": "EXPLORATORY_LEARNED_HEAD_FAMILY",
        "working_meaning_de": "trockene Arzneimischung am Gradende", "composition": "ch+CKH_LEARNED+ee+y",
        "rival_de": "trockenes CKH-Drogengut am Gradende",
        "decision_basis": "the single exact token occupies the end cell predicted by four larger sister cells",
        "counterargument": "singleton and the CKH object value is learned rather than independently decoded",
    },
    {
        "surface": "chckhdy", "source_locus": "NONE", "strict_source": "0",
        "family": "CH_CKH_SUBDEGREE_FAMILY", "tier": "EXPLORATORY_LEARNED_HEAD_FAMILY",
        "working_meaning_de": "trockene Arzneimischung am Gradanfang, abgeschlossen", "composition": "ch+CKH_LEARNED+d+y",
        "rival_de": "trockenes CKH-Drogengut am Gradanfang, abgeschlossen",
        "decision_basis": "the observed d/no-d pair uses the already established exact-whole result contrast at the beginning cell",
        "counterargument": "the CKH object value is learned rather than independently decoded",
    },
    {
        "surface": "chckhedy", "source_locus": "f76v.32", "strict_source": "1",
        "family": "CH_CKH_SUBDEGREE_FAMILY", "tier": "EXPLORATORY_LEARNED_HEAD_FAMILY",
        "working_meaning_de": "trockene Arzneimischung in der Gradmitte, abgeschlossen", "composition": "ch+CKH_LEARNED+e+d+y",
        "rival_de": "trockenes CKH-Drogengut in der Gradmitte, abgeschlossen",
        "decision_basis": "nine observed tokens fill the middle completed cell beside chckhdy and the three no-d cells without reordering CKH into K+CH",
        "counterargument": "the CKH object value is learned rather than independently decoded; CTH or leaf material is not licensed",
    },
)

FAMILY_FORMS = (
    ("DIRECT_OIIN_QUALITY_ARM", "oiin", "oiin", "Zubereitungsform III", "BASE_ANCHOR"),
    ("DIRECT_OIIN_QUALITY_ARM", "koiin", "k+(oiin)", "heiße Zubereitung, Form III", "HELD_READER_UNSTABLE"),
    ("DIRECT_OIIN_QUALITY_ARM", "toiin", "t+(oiin)", "kalte Zubereitung, Form III", "TARGET"),
    ("DIRECT_OIIN_QUALITY_ARM", "choiin", "ch+(oiin)", "trockene Zubereitung, Form III", "BASE_ANCHOR"),
    ("DIRECT_OIIN_QUALITY_ARM", "shoiin", "sh+(oiin)", "Feuchtansatz, Form III", "TARGET"),
    ("D_PLUS_AR_FRACTION_LADDER", "ar", "ar", "Fraktion I", "BASE_BODY"),
    ("D_PLUS_AR_FRACTION_LADDER", "air", "air", "Fraktion II", "BASE_BODY"),
    ("D_PLUS_AR_FRACTION_LADDER", "aiir", "aiir", "Fraktion III", "BASE_BODY"),
    ("D_PLUS_AR_FRACTION_LADDER", "dar", "d+(ar)", "abgemessene Fraktion I", "TARGET"),
    ("D_PLUS_AR_FRACTION_LADDER", "dair", "d+(air)", "abgemessene Fraktion II", "TARGET"),
    ("D_PLUS_AR_FRACTION_LADDER", "daiir", "d+(aiir)", "abgemessene Fraktion III", "TARGET"),
    ("DAIROD_CLOSURE_MINI_LADDER", "dairo", "d+air+o", "abgemessene Fraktion II im Zubereitungsfeld", "OBSERVED_RIVAL"),
    ("DAIROD_CLOSURE_MINI_LADDER", "dairod", "d+air+o+d", "abgemessene Fraktion II als Zubereitung", "OBSERVED_RIVAL"),
    ("DAIROD_CLOSURE_MINI_LADDER", "dairody", "d+air+o+d+y", "abgemessene Fraktion II als fertige Zubereitung", "OBSERVED_RIVAL"),
    ("DAIROD_CLOSURE_MINI_LADDER", "dairodg", "d+air+o+d+g", "abgemessene Fraktion II, als Zubereitung abgeschlossen", "TARGET"),
    ("CH_CKH_SUBDEGREE_FAMILY", "chckhy", "ch+CKH_LEARNED+y", "trockene Arzneimischung am Gradanfang", "TARGET"),
    ("CH_CKH_SUBDEGREE_FAMILY", "chckhey", "ch+CKH_LEARNED+e+y", "trockene Arzneimischung in der Gradmitte", "TARGET"),
    ("CH_CKH_SUBDEGREE_FAMILY", "chckheey", "ch+CKH_LEARNED+ee+y", "trockene Arzneimischung am Gradende", "TARGET"),
    ("CH_CKH_SUBDEGREE_FAMILY", "chckhdy", "ch+CKH_LEARNED+d+y", "trockene Arzneimischung am Gradanfang, abgeschlossen", "TARGET"),
    ("CH_CKH_SUBDEGREE_FAMILY", "chckhedy", "ch+CKH_LEARNED+e+d+y", "trockene Arzneimischung in der Gradmitte, abgeschlossen", "TARGET"),
    ("CH_CKH_SUBDEGREE_FAMILY", "chckheedy", "ch+CKH_LEARNED+ee+d+y", "trockene Arzneimischung am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
)

SMOOTHED_SOURCE_LINES = {
    "f28v.5": "Kaltes Zubereitungsgut; Trockengut; Grad III; heiß-trocken im Grad III; Feuchtansatz, Form III; kalt-trocken in der Gradmitte; kalt-feucht in der Gradmitte; Wert IV.",
    "f5v.6": "Kaltes Zubereitungsgut; Trockengut; abgemessene Fraktion II, als Zubereitung abgeschlossen.",
    "f76v.32": "Kalt, Grad II; feucht am Gradende; kalt, Grad II; trocken in der Gradmitte, abgeschlossen; heiß, Grad III; trocken in der Gradmitte, abgeschlossen; kalt, Grad III; trockene Arzneimischung in der Gradmitte, abgeschlossen; kaltes Zubereitungsgut; kalter Ansatz am Gradanfang.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_EVIDENCE_ATLAS.tsv",
    "RISK_AND_RIVAL_REGISTER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "AFFECTED_LINE_TRANSLATIONS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V26_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V26.tsv",
    "COMPLETE_PASSAGES_V26.tsv", "ONE_UNKNOWN_PASSAGES_V26.tsv",
    "WORKING_DICTIONARY_V26.tsv",
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
        "entry": f"{spec_row['surface']}@GDT649_EXACT_WHOLE",
        "kind": f"EXACT_ZL3B_WHOLE_{spec_row['tier']}",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; tier={spec_row['tier']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; learned components remain family-bound"
        ),
        "status": f"NEW_V26_ACCEPTED_ROUND_{round_number:02d}",
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G648_ALLOW)}
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

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G648_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G648_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G648_COVERAGE)
    base_complete = read_tsv(ROOT / G648_COMPLETE)
    base_one = read_tsv(ROOT / G648_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (417, 354, 4128, 87, 151):
        raise RuntimeError("GDT648 V25 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT648 V25 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 13995,
        "unknown_token_positions": 18344, "complete_multi_token_lines": 87,
        "strict_complete_lines": 49, "one_unknown_lines": 151,
        "strict_one_unknown_lines": 44, "exact_glossary_surfaces": 354,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT648 V25 metrics changed: {base_metrics!r}")

    targets = {str(row["surface"]) for row in CANDIDATE_SPECS}
    if targets & set(base_glossary):
        raise RuntimeError("a GDT649 target is already in the V25 glossary")
    if "koiin" in targets:
        raise RuntimeError("reader-unstable koiin may not enter V26")
    source_frontier = read_tsv(ROOT / G648_NEW_ONE)
    strict_source = {str(row["surface"]): str(row["source_locus"]) for row in CANDIDATE_SPECS if row["strict_source"] == "1"}
    source_pairs = {(row["unknown_surface"], row["locus"]): row for row in source_frontier}
    for surface, locus in strict_source.items():
        source = source_pairs.get((surface, locus))
        if source is None or int(source["strict_eligible"]) != 1:
            raise RuntimeError(f"strict GDT648 source frontier changed: {(surface, locus)}")
    if strict_source != {"shoiin": "f28v.5", "dairodg": "f5v.6", "chckhedy": "f76v.32"}:
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
                "ACCEPTED_V26" if surface in targets else
                "ABSENT_HOLD" if not members else planned_status
            ),
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
        "round": 0, "surface": "BASE_V25", "tier": "BASE", "dictionary_entries": len(base_dictionary),
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
            glossary, surface, spec_row["working_meaning_de"], f"GDT649:{spec_row['tier']}",
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
                "audit_id": f"G649-A{round_number:02d}-{occurrence:03d}", "round": round_number,
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
            "round": round_number, "surface": surface, "tier": spec_row["tier"], "decision": "ACCEPT_V26_EXACT_WHOLE",
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
            "candidate_id": f"G649-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "source_locus": spec_row["source_locus"], "strict_source": spec_row["strict_source"],
            "family": spec_row["family"], "acceptance_tier": spec_row["tier"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": split_count, "decision": "ACCEPT_V26_EXACT_WHOLE",
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
            "replace if a better object identity explains all five CHCKH cells without reordering CKH"
            if row["family"] == "CH_CKH_SUBDEGREE_FAMILY" else
            "replace if a split bridge or a larger DAIROD ladder assigns O/D/G differently"
            if row["surface"] == "dairodg" else
            "replace if a same-frame family contrast contradicts the assigned quality or ladder stage"
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
            "zl3b_line": row["zl3b_line"], "v25_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v26_tokenwise_de": row["token_glosses_de"],
            "v26_working_reading_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "complete_v26": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v26_de": "; ".join(split_pipe(row["token_glosses_de"])),
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
        "page", "locus", "target_surfaces", "zl3b_line", "v25_tokenwise_de", "v26_tokenwise_de",
        "v26_working_reading_de", "complete_v26",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v26_de",
        "curated_source_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V26_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V26.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V26.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V26.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V26.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G648_RUN, G648_ALLOW, G648_COVERAGE, G648_COMPLETE, G648_ONE, G648_NEW_ONE,
        G648_GLOSSARY, G648_DICTIONARY, G648_RESULT, G648_REPORT,
        G627_REPORT, G636_REPORT, G637_REPORT, G647_REPORT, TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    tiers = Counter(row["acceptance_tier"] for row in target_deck)
    result_core = {
        "schema": "GDT649_STRICT_V25_HOLE_COMPLETION_RESULT_V1",
        "experiment_id": "GDT649", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_exact_wholes": len(target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "strict_v25_holes_closed": len(strict_source), "acceptance_tiers": dict(sorted(tiers.items())),
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
            "held_family_cells": ["koiin", "chckheedy"],
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v25_entries": len(base_dictionary), "v26_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v25_prefix_sha256": canonical_hash(base_dictionary),
                               "v26_sha256": canonical_hash(final_dictionary),
                               "v25_glossary_surfaces": len(base_glossary), "v26_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT649 is an exploratory working translation, not a decipherment claim. It adds exact-whole defaults for the direct OIIN quality arm, "
            "the observed D+AR fraction ladder, one DAIRODG learned whole and five observed CH+CKH subdegree cells. SHOIIN and the D+AR ladder are "
            "family-led; TOIIN is low-n; DAIRODG and the CHCKH object noun are deliberately replaceable learned hypotheses. CKH is not reordered "
            "to K+CH, CTH/leaf is not imported, G is not globalized, KOIIN stays reader-unstable, and absent CHCKHEEDY stays outside the dictionary. "
            "No plaintext, phonetics, language, ingredient identity, global suffix, bare component, f1r, new page or new image is asserted."
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
        f"GDT649 built: accepted={target['accepted_exact_wholes']} audits={target['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
