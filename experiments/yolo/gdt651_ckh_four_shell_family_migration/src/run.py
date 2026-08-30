#!/usr/bin/env python3
"""Build GDT651: migrate the observed four-shell CKH family into V28."""
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
BASE_REL = Path("experiments/yolo/gdt651_ckh_four_shell_family_migration")
ART = ROOT / BASE_REL / "artifacts"
G650 = Path("experiments/yolo/gdt650_v26_strict_family_completion")
G650_RUN = G650 / "src/run.py"
G650_ALLOW = G650 / "artifacts/PAGE_ALLOWLIST.tsv"
G650_COVERAGE = G650 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V27.tsv"
G650_COMPLETE = G650 / "artifacts/COMPLETE_PASSAGES_V27.tsv"
G650_ONE = G650 / "artifacts/ONE_UNKNOWN_PASSAGES_V27.tsv"
G650_GLOSSARY = G650 / "artifacts/V27_EXACT_TOKEN_GLOSSARY.tsv"
G650_DICTIONARY = G650 / "artifacts/WORKING_DICTIONARY_V27.tsv"
G650_RESULT = G650 / "artifacts/RESULT.json"
G650_REPORT = G650 / "REPORT.md"
G633_REPORT = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G647_REPORT = Path("experiments/yolo/gdt647_quality_subdegree_family_migration/REPORT.md")
G649_REPORT = Path("experiments/yolo/gdt649_strict_v25_hole_completion/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt650_builder_for_gdt651", ROOT / G650_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT650 builder")
g650 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g650)
g637 = g650.g637
TOKENS_REL = g650.TOKENS_REL
CROSS_REL = g650.CROSS_REL
COVERAGE_FIELDS = g650.COVERAGE_FIELDS
ONE_FIELDS = g650.ONE_FIELDS

STATUS = "PASS_7_CKH_SISTER_WHOLES__V28_FOUR_SHELL_GRID"
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
        "surface": "checkhy", "source_locus": "f80r.43", "strict_source": "1",
        "family": "FOUR_SHELL_CKH_GRID", "tier": "STRONG_LEARNED_CKH_FAMILY",
        "working_meaning_de": "trockenes Arzneikompositum am Gradanfang", "composition": "ch+E_ATTR+CKH_LEARNED+y",
        "rival_de": "trockenes Arzneigut am Gradanfang, attributiv gefügt",
        "decision_basis": "forty-three of forty-six tokens are all-reader exact; CHECKH is the populated outer-E sister between CHCKH and SHECKH",
        "counterargument": "Arzneikompositum remains a learned family noun and outer E could mark register or form rather than attribution",
    },
    {
        "surface": "checkhey", "source_locus": "NONE", "strict_source": "0",
        "family": "FOUR_SHELL_CKH_GRID", "tier": "STRONG_LEARNED_CKH_FAMILY",
        "working_meaning_de": "trockenes Arzneikompositum in der Gradmitte", "composition": "ch+E_ATTR+CKH_LEARNED+e+y",
        "rival_de": "trockenes Arzneigut in der Gradmitte, attributiv gefügt",
        "decision_basis": "nine of ten tokens are all-reader exact and fill the middle cell beside CHECKHY and CHECKHDY",
        "counterargument": "the CKH object noun remains learned rather than independently decoded",
    },
    {
        "surface": "checkhdy", "source_locus": "NONE", "strict_source": "0",
        "family": "FOUR_SHELL_CKH_GRID", "tier": "PROVISIONAL_LOW_N_CKH_FAMILY",
        "working_meaning_de": "trockenes Arzneikompositum am Gradanfang, abgeschlossen", "composition": "ch+E_ATTR+CKH_LEARNED+d+y",
        "rival_de": "trockenes Arzneigut am Gradanfang, attributiv gefügt und abgeschlossen",
        "decision_basis": "the singleton is all-reader exact and occupies the predicted completed beginning cell of the four-shell grid",
        "counterargument": "singleton; CHECKHEDY has one observed token but no all-reader exact anchor",
    },
    {
        "surface": "shckhy", "source_locus": "NONE", "strict_source": "0",
        "family": "FOUR_SHELL_CKH_GRID", "tier": "STRONG_LEARNED_CKH_FAMILY",
        "working_meaning_de": "Arzneikompositum: feucht, Gradanfang", "composition": "sh+CKH_LEARNED+y",
        "rival_de": "feuchtes Arzneigut am Gradanfang",
        "decision_basis": "forty-four of fifty-one tokens are all-reader exact and supply the direct moist sister of V27 CHCKHY",
        "counterargument": "the CKH object noun remains learned and the moist reading inherits the CH/SH quality axis",
    },
    {
        "surface": "shckhey", "source_locus": "NONE", "strict_source": "0",
        "family": "FOUR_SHELL_CKH_GRID", "tier": "STRONG_LEARNED_CKH_FAMILY",
        "working_meaning_de": "Arzneikompositum: feucht, Gradmitte", "composition": "sh+CKH_LEARNED+e+y",
        "rival_de": "feuchtes Arzneigut in der Gradmitte",
        "decision_basis": "eight of ten tokens are all-reader exact and fill the moist middle cell opposite CHCKHEY",
        "counterargument": "the CKH object noun remains learned rather than independently decoded",
    },
    {
        "surface": "shckhdy", "source_locus": "NONE", "strict_source": "0",
        "family": "FOUR_SHELL_CKH_GRID", "tier": "PROVISIONAL_LOW_N_CKH_FAMILY",
        "working_meaning_de": "Arzneikompositum: feucht, Gradanfang, abgeschlossen", "composition": "sh+CKH_LEARNED+d+y",
        "rival_de": "feuchtes Arzneigut am Gradanfang, abgeschlossen",
        "decision_basis": "the singleton is all-reader exact and fills the completed moist beginning cell",
        "counterargument": "singleton; the reading depends wholly on the populated sister grid",
    },
    {
        "surface": "shckhedy", "source_locus": "NONE", "strict_source": "0",
        "family": "FOUR_SHELL_CKH_GRID", "tier": "PROVISIONAL_LOW_N_CKH_FAMILY",
        "working_meaning_de": "Arzneikompositum: feucht, Gradmitte, abgeschlossen", "composition": "sh+CKH_LEARNED+e+d+y",
        "rival_de": "feuchtes Arzneigut in der Gradmitte, abgeschlossen",
        "decision_basis": "three of five tokens are all-reader exact and complete the observed moist middle d/no-d pair",
        "counterargument": "two reader variants and a still learned CKH object noun",
    },
)

# GDT649/GDT650 used "Arzneimischung" for the learned CKH object and treated
# outer E like a physical binding.  The audits found no mixing act and no
# physical bond.  V28 uses the historically plausible learned class
# "Arzneikompositum" and renders outer E as an attributive-fusion hypothesis;
# neither CKH nor E is exported as a free dictionary component.
REVISION_SPECS = (
    ("chckhy", "Arzneikompositum: trocken, Gradanfang", "ch+CKH_LEARNED+y"),
    ("chckhey", "Arzneikompositum: trocken, Gradmitte", "ch+CKH_LEARNED+e+y"),
    ("chckheey", "Arzneikompositum: trocken, Gradende", "ch+CKH_LEARNED+ee+y"),
    ("chckhdy", "Arzneikompositum: trocken, Gradanfang, abgeschlossen", "ch+CKH_LEARNED+d+y"),
    ("chckhedy", "Arzneikompositum: trocken, Gradmitte, abgeschlossen", "ch+CKH_LEARNED+e+d+y"),
    ("sheckhy", "feuchtes Arzneikompositum am Gradanfang", "sh+E_ATTR+CKH_LEARNED+y"),
    ("sheckhey", "feuchtes Arzneikompositum in der Gradmitte", "sh+E_ATTR+CKH_LEARNED+e+y"),
    ("sheckhedy", "feuchtes Arzneikompositum in der Gradmitte, abgeschlossen", "sh+E_ATTR+CKH_LEARNED+e+d+y"),
)

FAMILY_FORMS = (
    ("FOUR_SHELL_CKH_GRID", "chckhy", "ch+CKH_LEARNED+y", "Arzneikompositum: trocken, Gradanfang", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "chckhey", "ch+CKH_LEARNED+e+y", "Arzneikompositum: trocken, Gradmitte", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "chckheey", "ch+CKH_LEARNED+ee+y", "Arzneikompositum: trocken, Gradende", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "chckhdy", "ch+CKH_LEARNED+d+y", "Arzneikompositum: trocken, Gradanfang, abgeschlossen", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "chckhedy", "ch+CKH_LEARNED+e+d+y", "Arzneikompositum: trocken, Gradmitte, abgeschlossen", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "chckheedy", "ch+CKH_LEARNED+ee+d+y", "Arzneikompositum: trocken, Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("FOUR_SHELL_CKH_GRID", "checkhy", "ch+E_ATTR+CKH_LEARNED+y", "trockenes Arzneikompositum am Gradanfang", "TARGET"),
    ("FOUR_SHELL_CKH_GRID", "checkhey", "ch+E_ATTR+CKH_LEARNED+e+y", "trockenes Arzneikompositum in der Gradmitte", "TARGET"),
    ("FOUR_SHELL_CKH_GRID", "checkheey", "ch+E_ATTR+CKH_LEARNED+ee+y", "trockenes Arzneikompositum am Gradende", "ABSENT_PREDICTION"),
    ("FOUR_SHELL_CKH_GRID", "checkhdy", "ch+E_ATTR+CKH_LEARNED+d+y", "trockenes Arzneikompositum am Gradanfang, abgeschlossen", "TARGET"),
    ("FOUR_SHELL_CKH_GRID", "checkhedy", "ch+E_ATTR+CKH_LEARNED+e+d+y", "trockenes Arzneikompositum in der Gradmitte, abgeschlossen", "HELD_ZERO_EXACT"),
    ("FOUR_SHELL_CKH_GRID", "checkheedy", "ch+E_ATTR+CKH_LEARNED+ee+d+y", "trockenes Arzneikompositum am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("FOUR_SHELL_CKH_GRID", "shckhy", "sh+CKH_LEARNED+y", "Arzneikompositum: feucht, Gradanfang", "TARGET"),
    ("FOUR_SHELL_CKH_GRID", "shckhey", "sh+CKH_LEARNED+e+y", "Arzneikompositum: feucht, Gradmitte", "TARGET"),
    ("FOUR_SHELL_CKH_GRID", "shckheey", "sh+CKH_LEARNED+ee+y", "Arzneikompositum: feucht, Gradende", "ABSENT_PREDICTION"),
    ("FOUR_SHELL_CKH_GRID", "shckhdy", "sh+CKH_LEARNED+d+y", "Arzneikompositum: feucht, Gradanfang, abgeschlossen", "TARGET"),
    ("FOUR_SHELL_CKH_GRID", "shckhedy", "sh+CKH_LEARNED+e+d+y", "Arzneikompositum: feucht, Gradmitte, abgeschlossen", "TARGET"),
    ("FOUR_SHELL_CKH_GRID", "shckheedy", "sh+CKH_LEARNED+ee+d+y", "Arzneikompositum: feucht, Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("FOUR_SHELL_CKH_GRID", "sheckhy", "sh+E_ATTR+CKH_LEARNED+y", "feuchtes Arzneikompositum am Gradanfang", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "sheckhey", "sh+E_ATTR+CKH_LEARNED+e+y", "feuchtes Arzneikompositum in der Gradmitte", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "sheckheey", "sh+E_ATTR+CKH_LEARNED+ee+y", "feuchtes Arzneikompositum am Gradende", "ABSENT_PREDICTION"),
    ("FOUR_SHELL_CKH_GRID", "sheckhdy", "sh+E_ATTR+CKH_LEARNED+d+y", "feuchtes Arzneikompositum am Gradanfang, abgeschlossen", "HELD_ZERO_EXACT"),
    ("FOUR_SHELL_CKH_GRID", "sheckhedy", "sh+E_ATTR+CKH_LEARNED+e+d+y", "feuchtes Arzneikompositum in der Gradmitte, abgeschlossen", "V27_REVISED_ANCHOR"),
    ("FOUR_SHELL_CKH_GRID", "sheckheedy", "sh+E_ATTR+CKH_LEARNED+ee+d+y", "feuchtes Arzneikompositum am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
)

BRIDGE_SPECS = (
    ("G651-B01", "FOUR_SHELL_CKH_GRID", "f80r.43", "sheckhy checkhy sheckhy", "bound moist/dry CKH sister contact"),
    ("G651-B02", "FOUR_SHELL_CKH_GRID", "f103v.45", "shckhy sheckhy", "moist E/no-E CKH sister contact"),
    ("G651-B03", "FOUR_SHELL_CKH_GRID", "f103r.38", "chckhy ... checkhy", "dry E/no-E CKH same-line contact"),
    ("G651-B04", "FOUR_SHELL_CKH_GRID", "f103v.28", "checkhy ... shckhy", "dry-bound/moist-unbound CKH same-line contact"),
    ("G651-B05", "FOUR_SHELL_CKH_GRID", "f50v.3", "checkhy shckhy", "direct dry-bound/moist-unbound CKH contact"),
    ("G651-B06", "FOUR_SHELL_CKH_GRID", "f76r.20", "chckhy shckhy", "direct dry/moist unbound CKH contact"),
)

SMOOTHED_SOURCE_LINES = {
    "f80r.43": "Samenportion; feuchtes Arzneikompositum am Gradanfang; heiße Portion; trockenes Arzneikompositum am Gradanfang; heißer Ansatz Grad II; feuchtes Arzneikompositum am Gradanfang; heiß am Gradende; rohes Drogenholz.",
    "f30v.4": "Kalt-trockener Ansatz im Mittelgrad; Grad- oder Maßwert III; Pflanzenteil; trockenes Arzneikompositum am Gradanfang; kalt-trockene Zubereitung, fertig gebunden; Grad- oder Maßwert III.",
    "f83r.27": "Grad- oder Maßwert II; trocken im Mittelgrad und abgeschlossen; heiß am Gradende und abgeschlossen; zweimal Arzneikompositum: feucht, Gradmitte, abgeschlossen.",
    "f76v.33": "Samencharge III; kalter Ansatz Grad III; Arzneikompositum: feucht, Gradmitte, abgeschlossen.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_EVIDENCE_ATLAS.tsv",
    "BOUNDARY_BRIDGE_ATLAS.tsv", "RISK_AND_RIVAL_REGISTER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "REVISED_EXISTING_WHOLE_DEFAULTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "AFFECTED_LINE_TRANSLATIONS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V28_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V28.tsv",
    "COMPLETE_PASSAGES_V28.tsv", "ONE_UNKNOWN_PASSAGES_V28.tsv",
    "WORKING_DICTIONARY_V28.tsv",
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
        "entry": f"{spec_row['surface']}@GDT651_EXACT_WHOLE",
        "kind": f"EXACT_ZL3B_WHOLE_{spec_row['tier']}",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; tier={spec_row['tier']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; learned components remain family-bound"
        ),
        "status": f"NEW_V28_ACCEPTED_ROUND_{round_number:02d}",
    }


def revision_dictionary_row(surface: str, meaning: str, composition: str, occurrences: int, exact_count: int) -> dict[str, object]:
    return {
        "entry": f"{surface}@GDT651_REVISED_WHOLE",
        "kind": "REVISED_EXACT_ZL3B_WHOLE_FOUR_SHELL_CKH_GRID",
        "working_meaning_de": meaning,
        "composition": composition,
        "context_rule": (
            f"exact complete surface only; {occurrences} audited occurrences; {exact_count} all-reader exact; "
            "CKH and E_ATTR remain family-bound; this row supersedes the earlier Arzneimischung wording"
        ),
        "status": "REVISED_V28_FAMILY_DEFAULT",
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G650_ALLOW)}
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

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G650_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G650_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G650_COVERAGE)
    base_complete = read_tsv(ROOT / G650_COMPLETE)
    base_one = read_tsv(ROOT / G650_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (435, 372, 4128, 103, 153):
        raise RuntimeError("GDT650 V27 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT650 V27 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 14617,
        "unknown_token_positions": 17722, "complete_multi_token_lines": 103,
        "strict_complete_lines": 59, "one_unknown_lines": 153,
        "strict_one_unknown_lines": 41, "exact_glossary_surfaces": 372,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT650 V27 metrics changed: {base_metrics!r}")

    targets = {str(row["surface"]) for row in CANDIDATE_SPECS}
    revision_surfaces = {surface for surface, _, _ in REVISION_SPECS}
    if targets & set(base_glossary):
        raise RuntimeError("a GDT651 target is already in the V27 glossary")
    if revision_surfaces - set(base_glossary) or targets & revision_surfaces:
        raise RuntimeError("GDT651 revision deck no longer matches the V27 glossary")
    strict_source = {str(row["surface"]): str(row["source_locus"]) for row in CANDIDATE_SPECS if row["strict_source"] == "1"}
    source_pairs = {(row["unknown_surface"], row["locus"]): row for row in base_one}
    for surface, locus in strict_source.items():
        source = source_pairs.get((surface, locus))
        if source is None or int(source["strict_eligible"]) != 1:
            raise RuntimeError(f"strict GDT650 source frontier changed: {(surface, locus)}")
    if strict_source != {"checkhy": "f80r.43"}:
        raise RuntimeError("strict source deck changed")
    second_checkhy = source_pairs.get(("checkhy", "f30v.4"))
    if second_checkhy is None or int(second_checkhy["strict_eligible"]) != 1:
        raise RuntimeError("second strict CHECKHY source changed")
    strict_hole_rows = sorted(
        (row for row in base_one if row["unknown_surface"] in targets and int(row["strict_eligible"]) == 1),
        key=lambda row: row["locus"],
    )
    if [(row["unknown_surface"], row["locus"]) for row in strict_hole_rows] != [
            ("checkhy", "f30v.4"), ("checkhy", "f80r.43")]:
        raise RuntimeError("GDT651 strict-hole frontier changed")

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
                "ACCEPTED_V28" if surface in targets else
                "REVISED_V28_ANCHOR" if surface in revision_surfaces else
                "V27_ANCHOR" if surface in base_glossary else
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
    revision_rows: list[dict[str, object]] = []
    revision_dictionary_rows: list[dict[str, object]] = []
    for surface, meaning, composition in REVISION_SPECS:
        members = [row for row in token_rows if row["eva"] == surface]
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        split_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        old_meaning = glossary[surface]["working_meaning_de"]
        if "Arzneimischung" not in old_meaning or GENERIC_FILLER.search(meaning):
            raise RuntimeError(f"CKH revision precondition changed: {surface}")
        g637.set_gloss(
            glossary, surface, meaning, "GDT651:REVISED_FOUR_SHELL_CKH_GRID",
            "EXACT_WHOLE_FAMILY_REVISION", "KNOWN_EXACT_WHOLE", 147,
        )
        revision_dictionary_rows.append(
            revision_dictionary_row(surface, meaning, composition, len(members), exact_count)
        )
        revision_rows.append({
            "surface": surface, "old_working_meaning_de": old_meaning,
            "new_working_meaning_de": meaning, "composition": composition,
            "occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_count, "split_normalized_occurrences": split_count,
            "decision": "REVISE_V28_FAMILY_DEFAULT",
            "reason": "replace unsupported mixing/binding wording with learned Arzneikompositum and family-bound E_ATTR",
        })
    coverage, one_unknown, _, complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    if metrics(coverage, one_unknown, complete, glossary) != base_metrics:
        raise RuntimeError("meaning-only CKH revision changed V27 coverage metrics")
    base_complete_loci = {row["locus"] for row in base_complete}
    seen_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    newly_exposed_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V27", "tier": "BASE", "dictionary_entries": len(base_dictionary),
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
            glossary, surface, spec_row["working_meaning_de"], f"GDT651:{spec_row['tier']}",
            "EXACT_WHOLE_FAMILY_EXTENSION", "KNOWN_EXACT_WHOLE", 147,
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
                "audit_id": f"G651-A{round_number:02d}-{occurrence:03d}", "round": round_number,
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
        post_dictionary = [*base_dictionary, *revision_dictionary_rows, *accepted_dictionary_rows]
        ledger_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"], "decision": "ACCEPT_V28_EXACT_WHOLE",
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
            "candidate_id": f"G651-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "source_locus": spec_row["source_locus"], "strict_source": spec_row["strict_source"],
            "family": spec_row["family"], "acceptance_tier": spec_row["tier"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": split_count, "decision": "ACCEPT_V28_EXACT_WHOLE",
            "decision_basis": spec_row["decision_basis"], "strongest_counterargument": spec_row["counterargument"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"],
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *revision_dictionary_rows, *accepted_dictionary_rows]
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
            "replace Arzneikompositum if one better learned object value explains all four CKH shells; replace E_ATTR if direct sister lines prefer a physical or register contrast"
        ),
    } for row in target_deck]

    reality_rows: list[dict[str, object]] = []
    for strict_hole in strict_hole_rows:
        surface, locus = strict_hole["unknown_surface"], strict_hole["locus"]
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
        present = list(dict.fromkeys(
            token["eva"] for token in by_line[locus] if token["eva"] in targets | revision_surfaces
        ))
        if not present:
            continue
        row = final_by_locus[locus]
        affected_rows.append({
            "page": row["page"], "locus": locus, "target_surfaces": "|".join(present),
            "zl3b_line": row["zl3b_line"], "v27_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v28_tokenwise_de": row["token_glosses_de"],
            "v28_working_reading_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "complete_v28": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v28_de": "; ".join(split_pipe(row["token_glosses_de"])),
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
    write_tsv(output_dir / "REVISED_EXISTING_WHOLE_DEFAULTS.tsv", revision_rows, (
        "surface", "old_working_meaning_de", "new_working_meaning_de", "composition", "occurrences",
        "pages", "reader_exact_occurrences", "split_normalized_occurrences", "decision", "reason",
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
        "page", "locus", "target_surfaces", "zl3b_line", "v27_tokenwise_de", "v28_tokenwise_de",
        "v28_working_reading_de", "complete_v28",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v28_de",
        "curated_source_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V28_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V28.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V28.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V28.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V28.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G650_RUN, G650_ALLOW, G650_COVERAGE, G650_COMPLETE, G650_ONE,
        G650_GLOSSARY, G650_DICTIONARY, G650_RESULT, G650_REPORT,
        G633_REPORT, G647_REPORT, G649_REPORT,
        TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    tiers = Counter(row["acceptance_tier"] for row in target_deck)
    result_core = {
        "schema": "GDT651_CKH_FOUR_SHELL_FAMILY_MIGRATION_RESULT_V1",
        "experiment_id": "GDT651", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_exact_wholes": len(target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "strict_v27_holes_closed": len(strict_hole_rows), "acceptance_tiers": dict(sorted(tiers.items())),
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
            "held_observed_cells": ["checkhedy", "sheckhdy"],
            "held_absent_cells": [
                "chckheedy", "checkheey", "checkheedy", "shckheey",
                "shckheedy", "sheckheey", "sheckheedy",
            ],
        },
        "family_revision": {
            "revised_existing_wholes": len(revision_rows),
            "revised_surfaces": [row["surface"] for row in revision_rows],
            "revised_occurrences": sum(int(row["occurrences"]) for row in revision_rows),
            "old_noun": "Arzneimischung", "new_learned_noun": "Arzneikompositum",
            "outer_e_working_role": "E_ATTRIBUTIVE_FUSION_FAMILY_BOUND",
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v27_entries": len(base_dictionary), "v28_entries": len(final_dictionary),
                               "revision_tail_entries": len(revision_dictionary_rows),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v27_prefix_sha256": canonical_hash(base_dictionary),
                               "v28_sha256": canonical_hash(final_dictionary),
                               "v27_glossary_surfaces": len(base_glossary), "v28_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT651 is an exploratory working translation, not a solved plaintext. It revises eight existing and adds seven new exact whole-surface CKH defaults, "
            "closing two strict V27 holes. The four parses are CH+CKH, CH+E_ATTR+CKH, SH+CKH and SH+E_ATTR+CKH; E_ATTR and CKH remain family-bound. "
            "Arzneikompositum is a replaceable learned family noun, not a free CKH translation or proof of ingredients. CHECKHEDY and SHECKHDY remain held for "
            "zero exact anchors; seven absent cells remain unwritten. No free component, global suffix, absent-cell meaning, plaintext, phonetics, language, "
            "ingredient identity, f1r, new page or new image is asserted."
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
        f"GDT651 built: accepted={target['accepted_exact_wholes']} audits={target['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
