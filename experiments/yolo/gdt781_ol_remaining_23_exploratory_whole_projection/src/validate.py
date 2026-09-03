#!/usr/bin/env python3
"""Independent validator for GDT781's fixed 23-whole exploratory projection."""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
SPECS = SRC / "WHOLE_23_SPECS.tsv"
LOCKS = SRC / "SOURCE_LOCK.tsv"
REPORT = EXP / "REPORT.md"

PARENT = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_376_RENDERER.tsv"
PARENT_RESULT = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/RESULT.json"
PARENT_RESIDUAL = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_RESIDUAL_129_FALLBACK_CENSUS.tsv"
PARENT_INTAKE = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_25_EXACT_CARDLESS_INTAKE.tsv"
G779_DICTIONARY = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_WORKING_DICTIONARY.tsv"
G734 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G739_AXES = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G745 = ROOT / "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/CROSS_PAGE_ROLE_CARDS.tsv"
G762_NEIGHBORS = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/CANDIDATE_DIRECT_NEIGHBOR_DECK.tsv"
G762_NULLS = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/DIRECTED_PATTERN_NULL_CENSUS.tsv"
G748 = ROOT / "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/COLLAPSED_POSITION_EVIDENCE.tsv"
G775 = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/RIGHT_COMPLEMENT_SURFACE_CENSUS.tsv"
G780_SUPPLEMENT = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_2_WORKING_DICTIONARY_EVIDENCE.tsv"

COHORT_OUT = ART / "GDT781_23_COHORT_INTAKE.tsv"
RAW_RELATIONS_OUT = ART / "GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv"
EVIDENCE_OUT = ART / "GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv"
ATLAS_OUT = ART / "GDT781_23_SELECTED_ATLAS.tsv"
PRECEDENCE_OUT = ART / "GDT781_23_PRECEDENCE_AUDIT.tsv"
RENDERER_OUT = ART / "GDT781_376_RENDERER.tsv"
PASSAGES_OUT = ART / "GDT781_23_PASSAGE_PATCHES.tsv"
RESIDUAL_OUT = ART / "GDT781_RESIDUAL_106_FALLBACK_CENSUS.tsv"
PACKET_OUT = ART / "GDT781_GDT388_RELATION_PACKET.tsv"
CROSSWALK_OUT = ART / "GDT781_RELATION_EDGE_CROSSWALK.tsv"
EDGE_INTAKE_OUT = ART / "RELATION_PACKET_INTAKE.json"
RESULT_OUT = ART / "RESULT.json"
ARTIFACT_README = ART / "README.md"
REPLAY_OUTPUTS = (
    COHORT_OUT, RAW_RELATIONS_OUT, EVIDENCE_OUT, ATLAS_OUT, PRECEDENCE_OUT,
    RENDERER_OUT, PASSAGES_OUT, RESIDUAL_OUT, PACKET_OUT, CROSSWALK_OUT,
    EDGE_INTAKE_OUT, RESULT_OUT, ARTIFACT_README, REPORT,
)

SPEC_SHA256 = "96f34e57f97e06c2386e37bc4e9de3561bde8dd0b99b9c944835d9016a6c912e"
EXPECTED_LOCKS = {
    "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_376_RENDERER.tsv":
        "1f45349aab7247478690366b37bbffd19511921c3f4033005d74af79a9772525",
    "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/RESULT.json":
        "ebf440a2c2ee8ee49baee72b862559291f5e39f7b1b62b0697f587f7d1038ec2",
    "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_RESIDUAL_129_FALLBACK_CENSUS.tsv":
        "8ec2053a0f56eaf2c1144dad527b6f16a84928592a4180f616b4db466bfbf8da",
    "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_25_EXACT_CARDLESS_INTAKE.tsv":
        "209ec6c2a3518f6b1ceaec023f3c517d681a933cd9fdc64be3228f21656c4836",
    "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_WORKING_DICTIONARY.tsv":
        "a6a425c6fec7a93237e42545debf39118e2c2d072d1071010782857ad5c81c51",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv":
        "9646b8960840f0a6bb10985f0f9d7eef1237725f0763b712a96f0190aeaf7816",
    "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv":
        "0561329a79ce6c32e8eea4ca58a38e5a5f9602bf181beb79d741543b95aa2b53",
    "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/CROSS_PAGE_ROLE_CARDS.tsv":
        "733d6ee845cc465b8c47a3df6915922b52c30df8253c3ec9d5ce32aa646e5588",
    "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/CANDIDATE_DIRECT_NEIGHBOR_DECK.tsv":
        "54e8c3066c66dd38d81f8da4c2d2ca07206b969ddf19aa7da13edd09ad349cc3",
    "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/DIRECTED_PATTERN_NULL_CENSUS.tsv":
        "595c4a1388606ed8b5ce7936921c4e4097e4805809a29936d47cf4221ac12a61",
    "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/COLLAPSED_POSITION_EVIDENCE.tsv":
        "7532ba59ae4fcf190b4e178a9dfdbb1109eec34195ceb8e1a585eff2aa250689",
    "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/RIGHT_COMPLEMENT_SURFACE_CENSUS.tsv":
        "4d2d94c4b6f46701d0d6464f1cbf99838dd0c1d088e60985230676be27d18e36",
    "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts/GDT780_2_WORKING_DICTIONARY_EVIDENCE.tsv":
        "42c10d951a9dba42509a8ca77eefe8f6f211a6d9e73bf0c2b4947aec6f6946d9",
    "tools/relation_edge_intake.py":
        "fb8447470aa81ed608b90aedf7478893ddf6a445351aa12ab23c6fd725be3a47",
}

EXPECTED_SPEC = {
    # default, tier, raw consensus/local axes, cache occurrences, exact occurrences, exact pages
    "chockhar": ("Trockenzubereitung", "A2_DISTANCE2_MULTIWHOLE_CONSENSUS", "DRY|PREPARATION", 2, 2, 2),
    "sheeoy": ("feuchter Endzustand", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "MOIST|END_STAGE", 1, 1, 1),
    "ear": ("Stoffanteil", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "PART|MATERIAL", 1, 1, 1),
    "cheedaiin": ("Trockenmenge, Mittelstufe", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "DRY|AMOUNT|MIDDLE_STAGE", 5, 4, 3),
    "keeor": ("erhitzter Arzneistoff", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "HOT|MATERIAL", 6, 2, 2),
    "keeed": ("vollständig erhitzt", "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS", "HOT|END_STAGE", 1, 1, 1),
    "otlaiin": ("Kaltansatz, Stufe III", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "COLD|PREPARATION|LEVEL_III", 1, 1, 1),
    "chlor": ("trockener Arzneistoff", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "DRY|MATERIAL", 1, 1, 1),
    "lkan": ("erhitzt", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "HOT", 1, 1, 1),
    "chesey": ("Trockenzustand", "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS", "DRY", 1, 1, 1),
    "okes": ("Heißansatz", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "HOT|PREPARATION", 1, 1, 1),
    "kcheeky": ("heiß und trocken, Endstufe", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "HOT|DRY|END_STAGE", 1, 1, 1),
    "chedor": ("trockene Stoffportion", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "DRY|AMOUNT|MATERIAL", 3, 2, 2),
    "chealor": ("trockener Arzneistoff", "A2_DISTANCE2_MULTIWHOLE_CONSENSUS", "DRY|MATERIAL", 1, 1, 1),
    "okalor": ("erhitzter Arzneiansatz", "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS", "HOT|MATERIAL|PREPARATION", 2, 2, 2),
    "eses": ("Zubereitung", "A2_DISTANCE2_MULTIWHOLE_CONSENSUS", "PREPARATION", 1, 1, 1),
    "sheckhal": ("feuchte Arzneimischung", "A2_DISTANCE2_MULTIWHOLE_CONSENSUS", "MOIST|MATERIAL|PREPARATION", 2, 2, 2),
    "shdair": ("Arzneistoff", "A2_DISTANCE2_MULTIWHOLE_CONSENSUS", "MATERIAL", 2, 2, 2),
    "sheoly": ("Feuchtzustand", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "MOIST", 1, 1, 1),
    "chsky": ("heiß und trocken", "A3_DISTANCE1_MULTIWHOLE_CONSENSUS", "HOT|DRY", 3, 1, 1),
    "chorcholsal": ("getrocknete Stoffzubereitung", "A0_NO_CLEAN_NEIGHBOR", "DRY|PART|MATERIAL|PREPARATION", 1, 1, 1),
    "cheokchey": ("Trockenzubereitung, Mittelstufe", "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS", "DRY|PREPARATION|MIDDLE_STAGE", 1, 1, 1),
    "okachey": ("erhitzte Trockenzubereitung", "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS", "HOT|DRY|PREPARATION", 1, 1, 1),
}
EXPECTED_ORDER = tuple(EXPECTED_SPEC)
SELECTION_RULE = "GDT780_RENDERER_CONTEXTUAL_0_AND_RIGHT_READER_EXACT_1_AND_COMPLETE_RIGHT_SURFACE_IN_FROZEN_WHOLE_23_SPECS"
EXPECTED_STATUS = "PASS__23_EXPLORATORY_EXACT_WHOLES__23_FORMS__23_LOCI__270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__12_A3__10_A2__1_A0__NO_COMPONENT_EXPORT"
EXPECTED_EDGE_INTAKE = {
    "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 23,
    "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
    "holdout_edges": 0, "mobile_edges": 0,
    "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
    "mobile_null_gate": False, "score_ready": False, "errors": [],
}
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)
STAGE_PATTERNS = {
    "BEGIN_STAGE": re.compile(r"anfangsstufe|gradanfang|anfang des grades|grundform|grundstufe", re.I),
    "MIDDLE_STAGE": re.compile(r"mittelstufe|gradmitte|mitte des grades|mittlere|mittelstufig", re.I),
    "END_STAGE": re.compile(r"endstufe|gradende|ende des grades|vollständig|fertig|abgeschlossen", re.I),
    "LEVEL_II": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) ii\b", re.I),
    "LEVEL_III": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) iii\b", re.I),
}
RETIRED_LITERAL_PATIENTS = ("pulver", "samen", "saat", "wurzel", "holz")
SEALED_RE = re.compile(r"(?<![A-Za-z0-9])f84r?(?![A-Za-z0-9])", re.I)


class Audit:
    def __init__(self) -> None:
        self.count = 0
        self.labels: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        self.count += 1
        self.labels.append(label)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def unique(rows: Sequence[Mapping[str, str]], field: str) -> dict[str, Mapping[str, str]]:
    result: dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = row[field]
        if key in result:
            raise AssertionError("duplicate " + field + ": " + key)
        result[key] = row
    return result


def joined(items: Iterable[str]) -> str:
    members = set(items)
    return "|".join(item for item in AXIS_ORDER if item in members) or "NONE"


def zero_fields(rows: Iterable[Mapping[str, str]], fields: Sequence[str]) -> bool:
    return all(row.get(field, "0") == "0" for row in rows for field in fields if field in row)


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + int(left_char != right_char),
            ))
        previous = current
    return previous[-1]


def analogy_class(tags: set[str]) -> str:
    quality = tags & {"HOT", "COLD", "DRY", "MOIST"}
    carrier = tags & {"MATERIAL", "PREPARATION"}
    quantity = tags & {"AMOUNT", "PART"}
    process = tags & {"PROCESS", "CLOSE", "PASS"}
    stage = tags & {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III"}
    if quality and carrier:
        return "QUALIFIED_MATERIAL_OR_PREPARATION_WHOLE"
    if quality and process:
        return "QUALITY_PROCESS_OR_RESULT_WHOLE"
    if quality:
        return "QUALITY_OR_STATE_WHOLE"
    if quantity and carrier:
        return "QUANTIFIED_MATERIAL_OR_PREPARATION_WHOLE"
    if quantity:
        return "QUANTITY_OR_PART_WHOLE"
    if carrier:
        return "MATERIAL_OR_PREPARATION_WHOLE"
    if process:
        return "PROCESS_OR_RESULT_WHOLE"
    if stage:
        return "STAGE_OR_RESULT_WHOLE"
    return "MIXED_OR_OPEN_WHOLE"


def validate_source_locks(audit: Audit) -> dict[str, str]:
    rows = read_tsv(LOCKS)
    audit.check(len(rows) == 14, "fourteen source locks")
    by_path = unique(rows, "path")
    audit.check(set(by_path) == set(EXPECTED_LOCKS), "exact frozen source path set")
    observed: dict[str, str] = {}
    for relative, expected in EXPECTED_LOCKS.items():
        path = Path(relative)
        audit.check(not path.is_absolute() and ".." not in path.parts, "safe relative lock " + relative)
        audit.check(by_path[relative]["expected_sha256"] == expected, "hard-coded lock " + relative)
        actual = sha256(ROOT / path)
        audit.check(actual == expected, "source rehash " + relative)
        observed[relative] = actual
    return observed


def validate_specs(audit: Audit) -> dict[str, dict[str, str]]:
    audit.check(sha256(SPECS) == SPEC_SHA256, "exact preregistered 23-card spec hash")
    rows = read_tsv(SPECS)
    audit.check(len(rows) == 23, "spec deck has 23 rows")
    audit.check(tuple(row["surface"] for row in rows) == EXPECTED_ORDER, "spec order and surfaces exact")
    by_surface = {key: dict(value) for key, value in unique(rows, "surface").items()}
    for surface, expected in EXPECTED_SPEC.items():
        row = by_surface[surface]
        observed = (
            row["default_de"], row["analogy_tier"], row["functional_axes"],
            int(row["cache_occurrences"]), int(row["reader_exact_occurrences"]),
            int(row["reader_exact_pages"]),
        )
        audit.check(observed == expected, "frozen wording tier axes and recurrence " + surface)
        audit.check(
            len({row["default_de"], row["alternate_1_de"], row["alternate_2_de"]}) == 3,
            "one default and two distinct rivals " + surface,
        )
        audit.check(
            all(row[field].strip() for field in (
                "default_de", "alternate_1_de", "alternate_2_de", "confidence",
                "positive_evidence", "counterevidence", "source_evidence", "card_class",
            )), "nonempty wording and evidence " + surface,
        )
    audit.check(Counter(row["analogy_tier"].split("_")[0] for row in rows) == Counter({"A3": 12, "A2": 10, "A0": 1}),
                "spec tier split is 12 A3 10 A2 1 A0")
    audit.check(sum(int(row["reader_exact_occurrences"]) for row in rows) == 32,
                "spec recurrence totals 32 reader-exact occurrences")
    audit.check(
        all(row["selected_by_exploratory_policy"] == "1" and row["literal_identity"] == "OPEN" for row in rows),
        "every spec selected by policy with literal identity open",
    )
    audit.check(
        zero_fields(rows, (
            "confirmed_lexeme", "component_export_credit", "numeric_identity_confirmed",
            "specific_substance_confirmed", "default_is_translation",
        )), "spec exports no translation lexeme component number or substance",
    )
    audit.check(
        by_surface["chorcholsal"]["renderer_scope"] == "EXACT_ENUMERATED_OL_CHORCHOLSAL_SPAN_ONLY"
        and by_surface["chorcholsal"]["card_class"] == "A0_TARGET_FRAME_ONLY_EXPLORATORY_DEFAULT"
        and all(
            row["renderer_scope"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY"
            for surface, row in by_surface.items() if surface != "chorcholsal"
        ), "whole-only scope plus one enumerated A0 scope exact",
    )
    return by_surface


def validate_runner_ast(audit: Audit) -> None:
    tree = ast.parse(RUN.read_text(encoding="utf-8"), filename=str(RUN))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "select_gdt781_row"]
    audit.check(len(functions) == 1, "one named GDT781 selector")
    function = functions[0]
    args = [arg.arg for arg in function.args.args]
    audit.check(
        args == ["parent_contextual", "right_reader_exact", "right_surface", "frozen_surfaces"]
        and not function.args.defaults and function.args.vararg is None and function.args.kwarg is None,
        "selector exposes only parent state exactness surface and frozen deck",
    )
    returns = [node for node in ast.walk(function) if isinstance(node, ast.Return)]
    audit.check(len(returns) == 1, "selector has one return")
    expected = ast.parse(
        "parent_contextual == '0' and right_reader_exact == '1' and right_surface in frozen_surfaces",
        mode="eval",
    ).body
    audit.check(ast.dump(returns[0].value, include_attributes=False) == ast.dump(expected, include_attributes=False),
                "selector AST is exact fallback exact-reader frozen-deck membership")
    audit.check(
        not any(isinstance(node, (ast.Subscript, ast.Call, ast.Attribute, ast.BinOp, ast.IfExp, ast.Lambda))
                for node in ast.walk(returns[0].value)),
        "selector contains no lookup call substring arithmetic or conditional",
    )
    names = {node.id for node in ast.walk(returns[0].value) if isinstance(node, ast.Name)}
    audit.check(names == set(args), "selector references every and only declared inputs")
    forbidden = ("occurrence", "target", "page", "folio", "locus", "ordinal", "neighbor", "frequency", "count", "edit", "substring", "meaning", "semantic", "default", "evidence", "confidence")
    audit.check(not any(any(term in name.lower() for term in forbidden) for name in names),
                "selector names exclude IDs locations neighbors frequency and semantics")
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "select_gdt781_row"]
    audit.check(len(calls) >= 1, "runner invokes pure selector")
    audit.check(all(
        len(call.args) == 4 and [ast.unparse(arg) for arg in call.args] == [
            "row['gdt780_renderer_contextual']", "row['right_reader_exact']",
            "row['right_surface']", "FROZEN_SURFACES",
        ] for call in calls
    ), "every selector call uses only parent columns and frozen deck")


def build_clean_pool(audit: Audit) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    axis_rows = read_tsv(G739_AXES)
    expected_axes = ["HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART", "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS"]
    audit.check([row["axis_id"] for row in axis_rows] == expected_axes, "axis source order exact")
    patterns = {
        row["axis_id"]: re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.I)
        for row in axis_rows
    }

    def tags(text: str) -> set[str]:
        result = {axis for axis, pattern in patterns.items() if pattern.search(text)}
        if re.search(r"koch|ausgekoch", text, re.I):
            result.add("HOT")
        result.update(axis for axis, pattern in STAGE_PATTERNS.items() if pattern.search(text))
        return result

    dictionary = read_tsv(G734)
    audit.check(len(dictionary) == 1606, "GDT734 dictionary has 1606 rows")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dictionary:
        meaning = row["working_meaning_de"]
        if not row["working_model_level"].startswith(("W2", "W3")):
            continue
        if row["gdt734_composition_semantic_credit"] != "0":
            continue
        if row["gdt734_component_export_allowed"] != "0":
            continue
        if row["gdt734_renderer_decision"] == "HOLD_UNCHANGED":
            continue
        if any(word in meaning.lower() for word in RETIRED_LITERAL_PATIENTS):
            continue
        if not tags(meaning):
            continue
        grouped[row["surface"]].append(row)
    audit.check(sum(map(len, grouped.values())) == 770, "clean axis pool has 770 reading rows")
    pool: dict[str, dict[str, object]] = {}
    for surface, rows in grouped.items():
        reading_tags = [tags(row["working_meaning_de"]) for row in rows]
        core = set.intersection(*reading_tags)
        if core:
            ranked = sorted(rows, key=lambda row: (
                -int(row["working_model_level"].startswith("W3")),
                -int(row["working_model_score_0_100_not_probability"]),
                row["reading_id"],
            ))
            glosses = list(dict.fromkeys(row["working_meaning_de"] for row in ranked))
            pool[surface] = {
                "core_tags": core, "union_tags": set.union(*reading_tags), "rows": rows,
                "reading_ids": "|".join(row["reading_id"] for row in ranked),
                "levels": "|".join(sorted({row["working_model_level"] for row in rows})),
                "max_score": max(int(row["working_model_score_0_100_not_probability"]) for row in rows),
                "occurrences": max(int(row["occurrence_count"]) for row in rows),
                "pages": max(int(row["page_count"]) for row in rows),
                "best_gloss": glosses[0], "all_glosses": " || ".join(glosses),
            }
    audit.check(len(pool) == 769, "clean axis pool has 769 complete wholes")
    audit.check("eees" not in pool and "sheeol" not in pool,
                "later GDT780 supplements absent from frozen old pool")

    summaries: dict[str, dict[str, object]] = {}
    for candidate in EXPECTED_ORDER:
        neighbors = sorted(
            (levenshtein(candidate, surface), surface, record)
            for surface, record in pool.items()
            if surface != candidate and levenshtein(candidate, surface) <= 2
        )
        if not neighbors:
            summaries[candidate] = {
                "minimum": "NA", "radius": 0, "neighbors": (), "closest": (),
                "consensus": "NONE", "rivals": "NONE", "support": "NONE",
                "nearest_glosses": "NONE", "functional_class": "MIXED_OR_OPEN_WHOLE",
                "tier": "A0_NO_CLEAN_NEIGHBOR",
            }
            continue
        minimum = neighbors[0][0]
        closest = [record for record in neighbors if record[0] == minimum]
        radius = minimum if len(closest) >= 2 or minimum == 2 else 2
        selected = [record for record in neighbors if record[0] <= radius]
        counts = Counter(tag for _, _, record in selected for tag in record["core_tags"])
        consensus = {tag for tag, count in counts.items() if tag != "VALUE" and count >= 2 and count / len(selected) >= .60}
        rivals = {tag for tag, count in counts.items() if tag != "VALUE" and tag not in consensus and count >= 1}
        if consensus and minimum == 1 and len(closest) >= 2:
            tier = "A3_DISTANCE1_MULTIWHOLE_CONSENSUS"
        elif consensus and minimum == 1:
            tier = "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS"
        elif consensus:
            tier = "A2_DISTANCE2_MULTIWHOLE_CONSENSUS"
        elif len(selected) == 1:
            tier = "A1_SINGLE_NEIGHBOR_LEAD"
        else:
            tier = "A1_MIXED_NEIGHBORHOOD"
        summaries[candidate] = {
            "minimum": minimum, "radius": radius,
            "neighbors": tuple(surface for _, surface, _ in selected),
            "closest": tuple(surface for _, surface, _ in closest),
            "consensus": joined(consensus), "rivals": joined(rivals),
            "support": "|".join(f"{axis}:{counts[axis]}" for axis in AXIS_ORDER if counts[axis]) or "NONE",
            "nearest_glosses": " || ".join(
                f"{surface}={record['best_gloss']}" for _, surface, record in closest
            ),
            "functional_class": analogy_class(consensus), "tier": tier,
        }
    audit.check(Counter(str(row["tier"]).split("_")[0] for row in summaries.values()) == Counter({"A3": 12, "A2": 10, "A0": 1}),
                "independent raw analogy split is 12 A3 10 A2 1 A0")
    return pool, summaries


def validate_raw_analogy(audit: Audit, specs: Mapping[str, Mapping[str, str]], pool: Mapping[str, Mapping[str, object]], summaries: Mapping[str, Mapping[str, object]]) -> None:
    for surface in EXPECTED_ORDER:
        expected_axes = "NONE" if surface == "chorcholsal" else specs[surface]["functional_axes"]
        audit.check(summaries[surface]["tier"] == specs[surface]["analogy_tier"], "raw analogy tier " + surface)
        audit.check(summaries[surface]["consensus"] == expected_axes, "raw analogy consensus " + surface)
    audit.check(
        summaries["eses"]["minimum"] == 2 and summaries["eses"]["radius"] == 2
        and summaries["eses"]["neighbors"] == ("oeees", "oees", "shes")
        and summaries["eses"]["consensus"] == "PREPARATION",
        "eses raw old layer is exactly three distance-two PREPARATION neighbors",
    )
    audit.check(
        summaries["sheeoy"]["minimum"] == 1 and summaries["sheeoy"]["radius"] == 1
        and summaries["sheeoy"]["neighbors"] == ("sheedy", "sheeky", "sheeo", "sheeod", "sheety", "sheoy")
        and summaries["sheeoy"]["consensus"] == "MOIST|END_STAGE",
        "sheeoy raw old layer keeps its six distance-one neighbors",
    )
    audit.check(
        summaries["chorcholsal"] == {
            "minimum": "NA", "radius": 0, "neighbors": (), "closest": (),
            "consensus": "NONE", "rivals": "NONE", "support": "NONE",
            "nearest_glosses": "NONE", "functional_class": "MIXED_OR_OPEN_WHOLE",
            "tier": "A0_NO_CLEAN_NEIGHBOR",
        }, "chorcholsal raw analogy layer has no clean radius-two neighbor",
    )
    audit.check(pool["chol"]["core_tags"] >= {"DRY"}
                and pool["cheor"]["core_tags"] >= {"DRY", "PART", "MATERIAL"},
                "local frame wholes chol and cheor independently carry dry and material-part axes")


def validate_source_evidence(audit: Audit, specs: Mapping[str, Mapping[str, str]], summaries: Mapping[str, Mapping[str, object]]) -> None:
    supplement = unique(read_tsv(G780_SUPPLEMENT), "entry")
    audit.check(set(supplement) == {"eees", "sheeol"}, "later supplement is exactly eees and sheeol")
    audit.check(supplement["eees"]["preferred_gdt780_default_de"] == "Mengenfeld"
                and supplement["eees"]["functional_axis"] == "AMOUNT_OR_VALUE_FIELD",
                "later eees supplement is amount/value field")
    audit.check(supplement["sheeol"]["preferred_gdt780_default_de"] == "Endzustand"
                and supplement["sheeol"]["functional_axis"] == "END_STAGE",
                "later sheeol supplement is end stage")
    audit.check(levenshtein("eses", "eees") == 1 and "Mengenfeld" == specs["eses"]["alternate_1_de"],
                "eses later eees ED1 conflict stays rival not raw vote")
    audit.check(levenshtein("sheeoy", "sheeol") == 1
                and "END_STAGE" in str(summaries["sheeoy"]["consensus"]),
                "sheeol is a later ED1 reinforcement without changing sheeoy raw six-neighbor layer")

    g745 = [row for row in read_tsv(G745) if row["candidate_surface"] == "okalor"]
    audit.check(len(g745) == 1 and g745[0]["gdt745_card_id"] == "G745-C018", "one exact existing okalor card")
    row = g745[0]
    audit.check(row["analogy_confidence_level"] == specs["okalor"]["analogy_tier"]
                and row["analogy_consensus_axes"] == specs["okalor"]["functional_axes"]
                and row["reader_exact_occurrences"] == "2" and row["reader_exact_pages"] == "2"
                and row["analogy_neighbor_surfaces"].split("|")[0] == "otalor"
                and "COLD" in row["analogy_rival_axes"],
                "GDT745 okalor card preserves hot consensus and direct cold rival")

    external = unique(read_tsv(G748), "evidence_id")
    for evidence_id, surface in (("G748-E0313", "cheedaiin"), ("G748-E0391", "otlaiin")):
        row = external[evidence_id]
        audit.check(row["target_surface"] == surface and row["target_reader_exact"] == "1"
                    and row["best_predicted_axes"] == "END_STAGE"
                    and row["whole_form_bridge_tier"] == "B0_NO_WHOLE_FORM_BRIDGE"
                    and row["whole_form_bridge_weight"] == "0"
                    and row["known_wholes_within_edit1"] == row["known_wholes_within_edit2"] == "0",
                    "target-independent B0 END counterframe " + surface)
        audit.check(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0"
                    and row["component_export_credit"] == "0",
                    "external frame exports no identity " + surface)

    recurrence = [row for row in read_tsv(G762_NEIGHBORS)
                  if row["candidate_surface"] == "ol" and row["neighbor_surface"] in specs]
    audit.check(len(recurrence) == 23 and len(unique(recurrence, "neighbor_surface")) == 23,
                "GDT762 has one ol-neighbor recurrence row per cohort form")
    by_surface = unique(recurrence, "neighbor_surface")
    for surface, spec in specs.items():
        row = by_surface[surface]
        audit.check(int(row["global_reader_exact_occurrences"]) == int(spec["reader_exact_occurrences"])
                    and int(row["global_reader_exact_pages"]) == int(spec["reader_exact_pages"]),
                    "independent exact recurrence and page count " + surface)
        audit.check(row["relation_identity"] == "DIRECT_EXACT_COMPLETE_WHOLE_NEIGHBOR"
                    and row["component_export_credit"] == "0",
                    "recurrence is whole-only and exports no component " + surface)
    nulls = {row["surface"]: row for row in read_tsv(G762_NULLS)}
    for surface, spec in specs.items():
        if surface in nulls:
            audit.check(nulls[surface]["reader_exact_occurrences"] == spec["reader_exact_occurrences"]
                        and nulls[surface]["reader_exact_pages"] == spec["reader_exact_pages"]
                        and nulls[surface]["component_export_credit"] == "0",
                        "directed-null recurrence agrees where published " + surface)

    slot = [row for row in read_tsv(G775) if row["right_surface"] in specs]
    audit.check(len(slot) == 23 and len(unique(slot, "right_surface")) == 23,
                "GDT775 contains every cohort surface exactly once")
    audit.check(all(row["stable_direction"] == "UNINFORMATIVE" and row["slot_evidence_tier"] == "UNINFORMATIVE" for row in slot),
                "all target-slot surfaces were previously uninformative")
    support_fields = [field for field in slot[0] if field.endswith("_raw_edges") or field.endswith("_support_surfaces") or field.endswith("_support_folios")]
    audit.check(all(row[field] == "0" for row in slot for field in support_fields),
                "GDT775 target slot supplied zero semantic selection edges")


def reconstruct_parent(audit: Audit, specs: Mapping[str, Mapping[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], set[str]]:
    parent = read_tsv(PARENT)
    audit.check(len(parent) == 376 and len(unique(parent, "target_occurrence_id")) == 376,
                "parent has 376 unique rows")
    audit.check(Counter(row["gdt780_renderer_contextual"] for row in parent) == Counter({"1": 247, "0": 129}),
                "parent independently reconstructs 247 contextual 129 fallback")
    tokens: list[str] = []
    for row in parent:
        row_tokens = [] if row["gdt780_consumed_token_ids"] == "NONE" else row["gdt780_consumed_token_ids"].split("|")
        audit.check(len(row_tokens) == int(row["gdt780_consumed_token_count"]), "parent token arity " + row["target_occurrence_id"])
        tokens.extend(row_tokens)
    audit.check(len(tokens) == len(set(tokens)) == 207, "parent has 207 collision-free consumed tokens")
    result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit.check(result["renderer"] == {"gdt779_contextual": 245, "gdt779_fallbacks": 131, "gdt780_contextual": 247, "gdt780_fallbacks": 129}
                and result["consumption"]["total_unique_right_tokens"] == 207,
                "parent RESULT agrees on coverage and consumption")

    residual = read_tsv(PARENT_RESIDUAL)
    audit.check(len(residual) == 129, "parent residual has 129 rows")
    audit.check(Counter(row["residual_reason"] for row in residual) == Counter({
        "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT": 23,
        "V99_CARD_NONEXACT": 49,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
        "LINE_FINAL_NO_RIGHT": 37,
    }), "parent residual split 23/49/20/37")
    source_intake = read_tsv(PARENT_INTAKE)
    audit.check(len(source_intake) == 25, "parent intake has 25 rows")
    audit.check([row["right_surface"] for row in source_intake if row["selected_by_pure_rule"] == "1"] == ["eees", "sheeol"],
                "parent intake marks only eees and sheeol selected")
    cohort = [row for row in source_intake if row["right_surface"] not in {"eees", "sheeol"}]
    audit.check(len(cohort) == 23 and tuple(row["right_surface"] for row in cohort) == EXPECTED_ORDER,
                "GDT781 cohort is exact GDT780 intake minus eees and sheeol")
    audit.check(all(row["selected_by_pure_rule"] == "0" and row["right_reader_exact"] == "1"
                    and row["parent_residual_reason"] == "NO_V99R7_COMPLETE_WORD_CARD_READER_EXACT" for row in cohort),
                "all cohort rows are still-unselected reader-exact cardless wholes")

    selected = [row for row in parent if row["gdt780_renderer_contextual"] == "0"
                and row["right_reader_exact"] == "1" and row["right_surface"] in specs]
    audit.check(len(selected) == 23 and tuple(row["right_surface"] for row in selected) == EXPECTED_ORDER,
                "pure selector independently yields exact ordered 23")
    audit.check([row["target_occurrence_id"] for row in selected] == [row["target_occurrence_id"] for row in cohort],
                "selector cohort target IDs equal parent intake-minus-two IDs")
    audit.check(len({row["locus"] for row in selected}) == 23
                and len({row["page"] for row in selected}) == 23
                and len({row["physical_folio"] for row in selected}) == 20,
                "cohort has 23 loci 23 page labels 20 physical folios")
    for row in selected:
        line = row["written_line_eva"].split()
        audit.check(line[int(row["ordinal"]) - 1] == "ol"
                    and line[int(row["right_ordinal"]) - 1] == row["right_surface"]
                    and int(row["right_ordinal"]) == int(row["ordinal"]) + 1,
                    "literal adjacent ol plus complete whole " + row["right_surface"])
    local = next(row for row in selected if row["right_surface"] == "chorcholsal")
    audit.check(local["target_occurrence_id"] == "G769-T0488" and local["locus"] == "f88r.22"
                and local["written_line_eva"] == "ychey okaiin chol cheor ol chorcholsal"
                and local["ordinal"] == "5" and local["right_ordinal"] == "6",
                "chorcholsal enumerated target-local frame exact")
    known_local = [(row["right_surface"], row["gdt780_default_de"], row["gdt780_exact_whole"])
                   for row in parent if row["right_surface"] in {"chol", "cheor"} and row["gdt780_renderer_contextual"] == "1"]
    audit.check(("chol", "Zustand: trocken", "chol") in known_local
                and ("cheor", "trockener Teil", "cheor") in known_local,
                "parent independently supplies complete chol and cheor local-frame cards")
    return parent, residual, selected, set(tokens)


def validate_cohort_output(audit: Audit, specs: Mapping[str, Mapping[str, str]]) -> list[dict[str, str]]:
    source = [row for row in read_tsv(PARENT_INTAKE) if row["right_surface"] not in {"eees", "sheeol"}]
    rows = read_tsv(COHORT_OUT)
    audit.check(len(rows) == len(source) == 23, "published cohort has exactly 23 rows")
    audit.check([row["cohort_id"] for row in rows] == [f"G781-I{n:03d}" for n in range(1, 24)],
                "cohort IDs complete and ordered")
    for row, old in zip(rows, source):
        audit.check(
            row["parent_intake_id"] == old["intake_id"]
            and row["target_occurrence_id"] == old["target_occurrence_id"]
            and row["page"] == old["page"] and row["physical_folio"] == old["physical_folio"]
            and row["locus"] == old["locus"] and row["section"] == old["section"]
            and row["language"] == old["language"] and row["hand"] == old["hand"]
            and row["ol_ordinal"] == old["ol_ordinal"] and row["right_ordinal"] == old["right_ordinal"]
            and row["right_surface"] == old["right_surface"] and row["right_reader_exact"] == "1",
            "cohort row reconstructs parent intake " + row["cohort_id"],
        )
        audit.check(row["right_surface"] in specs and row["parent_gdt780_selected"] == "0"
                    and row["frozen_whole_23_member"] == "1" and row["selection_rule"] == SELECTION_RULE,
                    "cohort row is exact frozen unselected parent member " + row["cohort_id"])
    audit.check(zero_fields(rows, (
        "selection_uses_occurrence_id", "selection_uses_page_or_locus",
        "selection_uses_analogy_or_meaning", "selection_uses_frequency",
        "selection_uses_substring", "default_is_translation", "confirmed_lexeme",
        "component_export_credit",
    )), "cohort contains zero forbidden selector and claim flags")
    return rows


def validate_raw_relations_output(
    audit: Audit, pool: Mapping[str, Mapping[str, object]],
    summaries: Mapping[str, Mapping[str, object]],
) -> list[dict[str, str]]:
    rows = read_tsv(RAW_RELATIONS_OUT)
    audit.check(len(rows) == 135, "published raw analogy has 135 relations")
    audit.check([row["relation_id"] for row in rows] == [f"G781-A{n:04d}" for n in range(1, 136)],
                "raw analogy relation IDs complete and ordered")
    expected: list[tuple[str, str]] = []
    for surface in sorted(EXPECTED_ORDER):
        expected.extend((surface, neighbor) for neighbor in summaries[surface]["neighbors"])
    audit.check([(row["candidate_surface"], row["known_neighbor_surface"]) for row in rows] == expected,
                "raw relation candidate-neighbor sequence independently reconstructs")
    for row in rows:
        surface, neighbor = row["candidate_surface"], row["known_neighbor_surface"]
        raw, known = summaries[surface], pool[neighbor]
        distance = levenshtein(surface, neighbor)
        audit.check(
            row["whole_levenshtein_distance"] == str(distance)
            and row["within_raw_closest_layer"] == str(int(neighbor in raw["closest"]))
            and row["raw_selected_radius"] == str(raw["radius"])
            and distance <= int(row["raw_selected_radius"]),
            "whole Levenshtein relation geometry " + row["relation_id"],
        )
        audit.check(
            row["known_neighbor_reading_ids"] == known["reading_ids"]
            and row["known_neighbor_levels"] == known["levels"]
            and row["known_neighbor_max_score_not_probability"] == str(known["max_score"])
            and row["known_neighbor_occurrences"] == str(known["occurrences"])
            and row["known_neighbor_pages"] == str(known["pages"])
            and row["known_neighbor_core_axes"] == joined(known["core_tags"])
            and row["known_neighbor_union_axes"] == joined(known["union_tags"])
            and row["known_neighbor_best_gloss_de"] == known["best_gloss"]
            and row["known_neighbor_all_glosses_de"] == known["all_glosses"],
            "relation donor reconstructed solely from clean source pool " + row["relation_id"],
        )
        audit.check(
            row["candidate_raw_consensus_axes"] == raw["consensus"]
            and row["candidate_raw_rival_axes"] == raw["rivals"]
            and row["candidate_raw_analogy_tier"] == raw["tier"]
            and row["relation_scope"] == "COMPLETE_WHOLE_EDIT_ANALOGY_ONLY",
            "relation summary agrees with independent whole-only calculation " + row["relation_id"],
        )
    audit.check(zero_fields(rows, ("selector_credit", "literal_identity_credit", "component_export_credit")),
                "raw relations grant zero selector identity and component credit")
    audit.check("chorcholsal" not in {row["candidate_surface"] for row in rows},
                "A0 chorcholsal has no raw relation")
    return rows


def validate_evidence_output(
    audit: Audit, specs: Mapping[str, Mapping[str, str]],
    summaries: Mapping[str, Mapping[str, object]],
) -> list[dict[str, str]]:
    rows = read_tsv(EVIDENCE_OUT)
    audit.check(len(rows) == 23 and [row["surface"] for row in rows] == list(EXPECTED_ORDER),
                "evidence cards cover exact ordered deck")
    audit.check([row["card_id"] for row in rows] == [f"G781-C{n:03d}" for n in range(1, 24)],
                "evidence card IDs complete and ordered")
    direct = unique([row for row in read_tsv(G762_NEIGHBORS)
                     if row["candidate_surface"] == "ol" and row["neighbor_surface"] in specs], "neighbor_surface")
    nulls = {row["surface"]: row for row in read_tsv(G762_NULLS)}
    slots = unique([row for row in read_tsv(G775) if row["right_surface"] in specs], "right_surface")
    supplements = unique(read_tsv(G780_SUPPLEMENT), "entry")
    external = {row["target_surface"]: row for row in read_tsv(G748) if row["target_surface"] in specs}
    later_pairs: set[tuple[str, str]] = set()
    for row in rows:
        surface, spec, raw = row["surface"], specs[row["surface"]], summaries[row["surface"]]
        audit.check(
            row["preferred_gdt781_default_de"] == spec["default_de"]
            and row["alternate_1_de"] == spec["alternate_1_de"]
            and row["alternate_2_de"] == spec["alternate_2_de"]
            and row["confidence"] == spec["confidence"]
            and row["card_class"] == spec["card_class"]
            and row["renderer_scope"] == spec["renderer_scope"],
            "evidence card copies exact frozen wording and scope " + surface,
        )
        audit.check(
            row["raw_pool_reading_rows"] == "770" and row["raw_pool_wholes"] == "769"
            and row["raw_analogy_tier"] == raw["tier"]
            and row["raw_min_edit_distance"] == str(raw["minimum"])
            and row["raw_selected_radius"] == str(raw["radius"])
            and row["raw_neighbor_wholes"] == str(len(raw["neighbors"]))
            and row["raw_closest_neighbor_wholes"] == str(len(raw["closest"]))
            and row["raw_neighbor_surfaces"] == ("|".join(raw["neighbors"]) or "NONE")
            and row["raw_nearest_glosses_de"] == raw["nearest_glosses"]
            and row["raw_consensus_axes"] == raw["consensus"]
            and row["raw_rival_axes"] == raw["rivals"]
            and row["raw_axis_support"] == raw["support"]
            and row["raw_functional_class"] == raw["functional_class"],
            "evidence card raw analogy fully reconstructed " + surface,
        )
        later = [(entry, levenshtein(surface, entry), record) for entry, record in sorted(supplements.items())
                 if levenshtein(surface, entry) <= 2]
        later_pairs.update((surface, entry) for entry, _, _ in later)
        audit.check(
            row["later_supplement_surfaces"] == ("|".join(item[0] for item in later) or "NONE")
            and row["later_supplement_edit_distances"] == ("|".join(str(item[1]) for item in later) or "NONE")
            and row["later_supplement_defaults_de"] == (" || ".join(f"{item[0]}={item[2]['preferred_gdt780_default_de']}" for item in later) or "NONE")
            and row["later_supplement_functional_axes"] == (" || ".join(f"{item[0]}={item[2]['functional_axis']}" for item in later) or "NONE")
            and row["later_supplement_pool_vote_credit"] == "0",
            "later supplement is a separate zero-vote layer " + surface,
        )
        recurrent = direct[surface]
        audit.check(
            row["cache_occurrences"] == spec["cache_occurrences"]
            and row["reader_exact_occurrences"] == recurrent["global_reader_exact_occurrences"] == spec["reader_exact_occurrences"]
            and row["reader_exact_pages"] == recurrent["global_reader_exact_pages"] == spec["reader_exact_pages"]
            and row["gdt762_direct_ol_contacts"] == recurrent["direct_contacts"]
            and row["gdt762_direct_ol_contact_pages"] == recurrent["contact_pages"]
            and row["gdt762_pattern_null_row_present"] == str(int(surface in nulls))
            and row["gdt775_fallback_target_tokens"] == slots[surface]["fallback_target_tokens"] == "1"
            and row["gdt775_slot_evidence_tier"] == "UNINFORMATIVE",
            "evidence recurrence and null-presence reconstructed " + surface,
        )
        expected_external = "END_STAGE" if surface == "cheedaiin" else "NONE"
        expected_local = "END_STAGE" if surface == "otlaiin" else (spec["functional_axes"] if surface == "chorcholsal" else "NONE")
        audit.check(row["external_serial_axes"] == expected_external and row["target_local_axes"] == expected_local,
                    "external versus target-local layer separated " + surface)
        if surface in external:
            audit.check(row["serial_evidence_ids"] == external[surface]["evidence_id"]
                        and row["serial_whole_bridge_tiers"] == "B0_NO_WHOLE_FORM_BRIDGE",
                        "serial evidence row and no-bridge tier exact " + surface)
        else:
            audit.check(row["serial_evidence_ids"] == row["serial_whole_bridge_tiers"] == "NONE",
                        "no undeclared serial evidence " + surface)
        audit.check(row["working_functional_axes"] == spec["functional_axes"]
                    and row["existing_gdt745_card_id"] == ("G745-C018" if surface == "okalor" else "NONE")
                    and row["positive_evidence"] == spec["positive_evidence"]
                    and row["counterevidence"] == spec["counterevidence"]
                    and row["source_evidence"] == spec["source_evidence"],
                    "working card evidence provenance exact " + surface)
    audit.check(later_pairs == {
        ("sheeoy", "sheeol"), ("keeed", "eees"), ("okes", "eees"),
        ("eses", "eees"), ("sheoly", "sheeol"),
    }, "exact five later supplement relations")
    audit.check(sum(int(row["cache_occurrences"]) for row in rows) == 40
                and sum(int(row["reader_exact_occurrences"]) for row in rows) == 32
                and sum(int(row["reader_exact_occurrences"]) > 1 for row in rows) == 7
                and sum(int(row["reader_exact_occurrences"]) == 1 for row in rows) == 16,
                "evidence recurrence totals 40 cache 32 exact 7 recurrent 16 singleton")
    audit.check(all(row["replaceable"] == row["selected_by_exploratory_policy"] == "1"
                    and row["literal_identity"] == "OPEN" for row in rows)
                and zero_fields(rows, ("confirmed_lexeme", "confirmed_plaintext", "component_export_credit",
                                       "numeric_identity_confirmed", "specific_substance_confirmed", "default_is_translation")),
                "evidence cards remain replaceable and export no identities")
    return rows


def validate_atlas_and_precedence(
    audit: Audit, parent: Sequence[Mapping[str, str]], selected: Sequence[Mapping[str, str]],
    specs: Mapping[str, Mapping[str, str]], summaries: Mapping[str, Mapping[str, object]],
    parent_tokens: set[str],
) -> tuple[list[dict[str, str]], set[str]]:
    atlas = read_tsv(ATLAS_OUT)
    audit.check(len(atlas) == 23 and [row["target_occurrence_id"] for row in atlas] == [row["target_occurrence_id"] for row in selected],
                "atlas exactly follows independent selector")
    audit.check([row["span_id"] for row in atlas] == [f"G781-S{n:03d}" for n in range(1, 24)],
                "atlas span IDs complete and ordered")
    for row, old in zip(atlas, selected):
        surface, spec, raw = row["right_surface"], specs[row["right_surface"]], summaries[row["right_surface"]]
        audit.check(
            row["target_occurrence_id"] == old["target_occurrence_id"] and row["page"] == old["page"]
            and row["physical_folio"] == old["physical_folio"] and row["locus"] == old["locus"]
            and row["ol_ordinal"] == old["ordinal"] and row["right_ordinal"] == old["right_ordinal"]
            and row["right_surface"] == old["right_surface"] and row["written_span_eva"] == "ol " + surface
            and row["written_line_eva"] == old["written_line_eva"] and row["right_reader_exact"] == "1",
            "atlas geometry reconstructs parent " + surface,
        )
        audit.check(
            row["old_gdt780_branch"] == old["gdt780_branch"] and row["old_gdt780_default_de"] == old["gdt780_default_de"]
            and row["old_gdt780_contextual"] == "0" and row["selected_whole_default_de"] == spec["default_de"]
            and row["new_gdt781_default_de"] == spec["default_de"] and row["alternate_1_de"] == spec["alternate_1_de"]
            and row["alternate_2_de"] == spec["alternate_2_de"] and row["confidence"] == spec["confidence"]
            and row["analogy_tier"] == raw["tier"] and row["raw_analogy_consensus_axes"] == raw["consensus"]
            and row["working_functional_axes"] == spec["functional_axes"] and row["card_class"] == spec["card_class"]
            and row["scope_status"] == spec["renderer_scope"],
            "atlas card and separate raw/working axes exact " + surface,
        )
        audit.check(
            row["semantic_change_class"] == "EXPLORATORY_FALLBACK_REPLACEMENT"
            and row["fallback_replacement"] == row["display_changed"] == row["new_unique_consumption"] == "1"
            and row["inherited_consumed_token_ids"] == "NONE"
            and row["gdt781_consumed_token_id"] == row["locus"] + "@" + row["right_ordinal"]
            and row["selection_rule"] == SELECTION_RULE and row["exact_complete_whole_only"] == "1",
            "atlas exact complete-token fallback replacement " + surface,
        )
    new_tokens = {row["gdt781_consumed_token_id"] for row in atlas}
    audit.check(len(new_tokens) == 23 and not (new_tokens & parent_tokens),
                "23 new token consumptions are unique and disjoint from parent")
    audit.check(zero_fields(atlas, (
        "same_row_inherited_consumption_takeover", "cross_row_consumption_collision",
        "selection_uses_occurrence_id", "selection_uses_page_or_locus", "selection_uses_analogy_or_meaning",
        "selection_uses_frequency", "selection_uses_substring", "default_is_translation", "confirmed_lexeme",
        "confirmed_plaintext", "component_export_credit",
    )), "atlas has zero takeover collision forbidden selector and claim flags")

    precedence = read_tsv(PRECEDENCE_OUT)
    audit.check(len(precedence) == 23 and [row["target_occurrence_id"] for row in precedence] == [row["target_occurrence_id"] for row in atlas],
                "precedence audit covers exactly selected atlas")
    parent_by_id = unique(parent, "target_occurrence_id")
    atlas_by_id = unique(atlas, "target_occurrence_id")
    for n, row in enumerate(precedence, 1):
        old, span = parent_by_id[row["target_occurrence_id"]], atlas_by_id[row["target_occurrence_id"]]
        audit.check(row["precedence_id"] == f"G781-H{n:03d}" and row["right_surface"] == span["right_surface"]
                    and row["parent_gdt780_fallback"] == "1" and row["parent_gdt780_contextual"] == "0"
                    and row["frozen_whole_23_member"] == "1"
                    and row["precedence_disposition"] == "SELECTED_GDT781_EXPLORATORY_FALLBACK",
                    "precedence selects exact parent fallback " + row["precedence_id"])
        audit.check(row["old_gdt780_branch"] == old["gdt780_branch"]
                    and row["old_gdt780_default_de"] == old["gdt780_default_de"]
                    and row["old_gdt780_consumed_token_count"] == "0" and row["old_gdt780_consumed_token_ids"] == "NONE"
                    and row["new_gdt781_default_de"] == span["new_gdt781_default_de"]
                    and row["new_gdt781_contextual"] == "1" and row["new_gdt781_consumed_token_count"] == "1"
                    and row["new_gdt781_consumed_token_ids"] == span["gdt781_consumed_token_id"]
                    and row["selection_rule"] == SELECTION_RULE,
                    "precedence old/new state exact " + row["precedence_id"])
    audit.check(zero_fields(precedence, (
        "same_row_inherited_consumption_takeover", "cross_row_consumption_collision",
        "selection_uses_occurrence_id", "selection_uses_page_or_locus",
        "selection_uses_analogy_or_meaning", "selection_uses_substring", "component_export_credit",
    )), "precedence audit has zero takeover collision semantic selector or component")
    return atlas, new_tokens


def validate_renderer(
    audit: Audit, parent: Sequence[Mapping[str, str]], atlas: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    rows = read_tsv(RENDERER_OUT)
    audit.check(len(rows) == len(parent) == 376, "renderer has exactly 376 rows")
    audit.check([row["target_occurrence_id"] for row in rows] == [row["target_occurrence_id"] for row in parent],
                "renderer preserves complete parent order")
    parent_fields = tuple(parent[0])
    spans = unique(atlas, "target_occurrence_id")
    for old, row in zip(parent, rows):
        audit.check(all(row[field] == old[field] for field in parent_fields),
                    "renderer preserves all parent bytes by field " + row["target_occurrence_id"])
        span = spans.get(row["target_occurrence_id"])
        if span is None:
            audit.check(
                row["gdt781_branch"] == "INHERITED_GDT780"
                and row["gdt781_default_de"] == old["gdt780_default_de"]
                and row["gdt781_renderer_contextual"] == old["gdt780_renderer_contextual"]
                and row["gdt781_span_id"] == old["gdt780_span_id"]
                and row["gdt781_exact_whole"] == old["gdt780_exact_whole"]
                and row["gdt781_confidence"] == old["gdt780_confidence"]
                and row["gdt781_functional_axes"] == old["gdt780_functional_axis"]
                and row["gdt781_consumed_token_count"] == old["gdt780_consumed_token_count"]
                and row["gdt781_consumed_token_ids"] == old["gdt780_consumed_token_ids"],
                "nonselected active renderer state inherited " + row["target_occurrence_id"],
            )
            audit.check(row["gdt781_analogy_tier"] == "INHERITED_GDT780"
                        and row["gdt781_positive_evidence"] == row["gdt781_counterevidence"] == "INHERITED_GDT780"
                        and row["gdt781_dispatch_rule"] == row["gdt781_scope_status"] == row["gdt781_card_class"] == "INHERITED_GDT780",
                        "nonselected GDT781 metadata inherited " + row["target_occurrence_id"])
        else:
            audit.check(
                row["gdt781_branch"] == "GDT781_EXPLORATORY_EXACT_OL_PLUS_COMPLETE_WHOLE"
                and row["gdt781_default_de"] == span["new_gdt781_default_de"]
                and row["gdt781_renderer_contextual"] == "1" and row["gdt781_span_id"] == span["span_id"]
                and row["gdt781_exact_whole"] == span["right_surface"]
                and row["gdt781_confidence"] == span["confidence"]
                and row["gdt781_analogy_tier"] == span["analogy_tier"]
                and row["gdt781_functional_axes"] == span["working_functional_axes"]
                and row["gdt781_consumed_token_count"] == "1"
                and row["gdt781_consumed_token_ids"] == span["gdt781_consumed_token_id"]
                and row["gdt781_dispatch_rule"] == SELECTION_RULE
                and row["gdt781_scope_status"] == span["scope_status"]
                and row["gdt781_card_class"] == span["card_class"],
                "selected renderer state equals exact atlas card " + row["target_occurrence_id"],
            )
    audit.check(Counter(row["gdt781_renderer_contextual"] for row in rows) == Counter({"1": 270, "0": 106}),
                "renderer transition is 247 to 270 contextual and 129 to 106 fallback")
    audit.check(sum(row["gdt781_branch"] != "INHERITED_GDT780" for row in rows) == 23
                and sum(row["gdt781_branch"] == "INHERITED_GDT780" for row in rows) == 353,
                "renderer changes 23 and inherits 353 rows")
    audit.check(sum(int(row["gdt781_fallback_replacement"]) for row in rows) == 23
                and sum(int(row["gdt781_display_changed"]) for row in rows) == 23
                and sum(int(row["gdt781_new_unique_consumption"]) for row in rows) == 23,
                "renderer has exactly 23 replacement display and consumption deltas")
    owners: dict[str, str] = {}
    for row in rows:
        tokens = [] if row["gdt781_consumed_token_ids"] == "NONE" else row["gdt781_consumed_token_ids"].split("|")
        audit.check(len(tokens) == int(row["gdt781_consumed_token_count"]),
                    "renderer token arity " + row["target_occurrence_id"])
        for token in tokens:
            audit.check(token not in owners, "no cross-row token collision " + token)
            owners[token] = row["target_occurrence_id"]
    audit.check(len(owners) == 230, "renderer has 230 uniquely consumed tokens")
    audit.check(zero_fields(rows, ("gdt781_default_is_translation", "gdt781_confirmed_lexeme",
                                   "gdt781_confirmed_plaintext", "gdt781_component_export_credit")),
                "renderer exports no translation lexeme plaintext or component")
    return rows


def render_line(
    locus: str, written: str, rows_by_position: Mapping[tuple[str, int], Mapping[str, str]], prefix: str,
) -> str:
    rendered: list[str] = []
    consumed: set[int] = set()
    for ordinal, token in enumerate(written.split(), 1):
        if ordinal in consumed:
            continue
        dispatch = rows_by_position.get((locus, ordinal))
        if dispatch is None:
            rendered.append(token)
        elif dispatch[f"{prefix}_renderer_contextual"] == "1":
            rendered.append("⟦" + dispatch[f"{prefix}_default_de"] + "⟧")
            count = int(dispatch[f"{prefix}_consumed_token_count"])
            consumed.update(range(ordinal + 1, ordinal + count + 1))
        else:
            rendered.append(token)
    return " ".join(rendered)


def validate_passages(
    audit: Audit, parent: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, str]],
    atlas: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    rows = read_tsv(PASSAGES_OUT)
    ordered = sorted(atlas, key=lambda row: row["locus"])
    audit.check(len(rows) == 23 and [row["target_occurrence_id"] for row in rows] == [row["target_occurrence_id"] for row in ordered],
                "passage patches cover selected atlas in locus order")
    old_by_pos = {(row["locus"], int(row["ordinal"])): row for row in parent}
    new_by_pos = {(row["locus"], int(row["ordinal"])): row for row in renderer}
    for n, (row, span) in enumerate(zip(rows, ordered), 1):
        before = render_line(span["locus"], span["written_line_eva"], old_by_pos, "gdt780")
        after = render_line(span["locus"], span["written_line_eva"], new_by_pos, "gdt781")
        audit.check(
            row["passage_patch_id"] == f"G781-P{n:03d}" and row["span_id"] == span["span_id"]
            and row["target_occurrence_id"] == span["target_occurrence_id"]
            and row["locus"] == span["locus"] and row["right_surface"] == span["right_surface"]
            and row["right_token_id"] == span["gdt781_consumed_token_id"]
            and row["selected_whole_default_de"] == span["selected_whole_default_de"]
            and row["written_line_eva"] == span["written_line_eva"]
            and row["inherited_gdt780_patch_de"] == before
            and row["gdt781_practical_patch_de"] == after and before != after,
            "passage patch independently rendered " + row["passage_patch_id"],
        )
    special = [row for row in rows if row["right_surface"] == "chorcholsal"]
    audit.check(len(special) == 1 and special[0]["target_occurrence_id"] == "G769-T0488"
                and special[0]["locus"] == "f88r.22"
                and special[0]["working_field_list_de"] == "Trocknung bis zur Mittelstufe, dann Abschluss | Heißansatz, Grad III | trocken | trockener Teil | getrocknete Stoffzubereitung"
                and special[0]["working_field_list_source_values_de"] == "ychey=trockne hiervon bis zur Mittelstufe und schließe ab || okaiin=heißer Ansatz, Grad III || chol=trocken || cheor=trockener Teil || chorcholsal=getrocknete Stoffzubereitung"
                and special[0]["working_field_list_status"] == "WORKING_DISPLAY_NOT_PLAINTEXT",
                "chorcholsal local field list and source-value provenance exact")
    audit.check(all(row["working_field_list_status"] == "NA" for row in rows if row["right_surface"] != "chorcholsal")
                and zero_fields(rows, ("default_is_translation", "confirmed_plaintext", "component_export_credit")),
                "only enumerated field list is populated and no plaintext is claimed")
    return rows


def normalize_residual_reason(value: str) -> str:
    if value in {"V99_CARD_NONEXACT_FINAL44", "V99_CARD_NONEXACT_RAW_ONLY"}:
        return "V99_CARD_NONEXACT"
    return value


def validate_residual(
    audit: Audit, parent_residual: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, str]],
    specs: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    rows = read_tsv(RESIDUAL_OUT)
    fallback = [row for row in renderer if row["gdt781_renderer_contextual"] == "0"]
    source_by_id = unique(parent_residual, "target_occurrence_id")
    audit.check(len(rows) == len(fallback) == 106, "residual covers exactly 106 renderer fallbacks")
    audit.check([row["target_occurrence_id"] for row in rows] == [row["target_occurrence_id"] for row in fallback],
                "residual preserves fallback renderer order")
    for n, (row, current) in enumerate(zip(rows, fallback), 1):
        old = source_by_id[row["target_occurrence_id"]]
        audit.check(
            row["residual_id"] == f"G781-R{n:03d}" and row["parent_gdt780_residual_id"] == old["residual_id"]
            and row["page"] == current["page"] and row["physical_folio"] == current["physical_folio"]
            and row["locus"] == current["locus"] and row["ol_ordinal"] == current["ordinal"]
            and row["right_ordinal"] == current["right_ordinal"] and row["right_surface"] == current["right_surface"]
            and row["right_reader_exact"] == current["right_reader_exact"]
            and row["parent_residual_reason"] == old["residual_reason"]
            and row["residual_reason"] == normalize_residual_reason(old["residual_reason"])
            and row["gdt781_default_de"] == current["gdt781_default_de"],
            "residual row reconstructs parent reason " + row["residual_id"],
        )
    audit.check(Counter(row["residual_reason"] for row in rows) == Counter({
        "V99_CARD_NONEXACT": 49,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
        "LINE_FINAL_NO_RIGHT": 37,
    }), "residual split is exactly 0/49/20/37")
    audit.check(all(row["frozen_whole_23_member"] == "0" and row["right_surface"] not in specs for row in rows)
                and zero_fields(rows, ("component_export_credit",)),
                "no selected exact whole or component remains in residual")
    return rows


def validate_relation_packet(audit: Audit, atlas: Sequence[Mapping[str, str]]) -> None:
    packet = read_tsv(PACKET_OUT)
    crosswalk = read_tsv(CROSSWALK_OUT)
    audit.check(len(packet) == len(crosswalk) == len(atlas) == 23,
                "relation packet crosswalk and atlas each have 23 rows")
    expected_ids = [f"G781-E{n:03d}" for n in range(1, 24)]
    audit.check([row["edge_id"] for row in packet] == [row["edge_id"] for row in crosswalk] == expected_ids,
                "relation edge IDs complete ordered and crosswalked")
    for edge, cross, span in zip(packet, crosswalk, atlas):
        audit.check(
            edge["page"] == span["page"] and edge["physical_folio"] == span["physical_folio"]
            and edge["pivot_locus"] == span["locus"] + "@" + span["ol_ordinal"]
            and edge["target_locus"] == span["gdt781_consumed_token_id"]
            and edge["relation_type"] == "NEXT_TOKEN"
            and edge["direction_basis"] == "TRANSCRIPTION_ORDER_ONLY"
            and edge["ownership_basis"] == "NONVISUAL_TEXT_ADJACENCY",
            "relation edge reconstructs exact text adjacency " + edge["edge_id"],
        )
        audit.check(
            edge["geometry_only_selection"] == "FALSE" and edge["formal_access_state"] == "SEALED_NOT_ACCESSED"
            and edge["fold_assignment"] == "NONE" and edge["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION"
            and edge["source_manifest_id"] == "GDT780"
            and edge["page_crop_sha256"] == edge["pivot_crop_sha256"] == edge["target_crop_sha256"] == "NONE",
            "relation edge is explicitly nonvisual ineligible and unscored " + edge["edge_id"],
        )
        audit.check(
            cross["span_id"] == span["span_id"] and cross["target_occurrence_id"] == span["target_occurrence_id"]
            and cross["page"] == span["page"] and cross["locus"] == span["locus"]
            and cross["right_surface"] == span["right_surface"] and cross["written_span_eva"] == span["written_span_eva"]
            and cross["selection_rule"] == SELECTION_RULE and cross["score_eligible"] == "0"
            and cross["component_export_credit"] == "0",
            "relation crosswalk maps exact selected span " + edge["edge_id"],
        )
    stored = json.loads(EDGE_INTAKE_OUT.read_text(encoding="utf-8"))
    audit.check(stored == EXPECTED_EDGE_INTAKE, "stored edge intake is exact not-score-ready result")
    gate = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(PACKET_OUT)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    audit.check(gate.returncode == 0, "external edge checker exits successfully")
    try:
        observed = json.loads(gate.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError("external edge checker output is not JSON") from error
    audit.check(observed == EXPECTED_EDGE_INTAKE, "external edge checker reproduces stored intake")


def validate_result_and_report(audit: Audit) -> None:
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT781" and result["status"] == EXPECTED_STATUS,
                "RESULT experiment identity and exact PASS status")
    audit.check(result["source_locks"] == 14 and result["source_lock_sha256"] == sha256(LOCKS)
                and result["whole_23_specs_sha256"] == SPEC_SHA256,
                "RESULT records exact source and spec locks")
    audit.check(result["inherited_guard"] == parent_result["inherited_guard"],
                "RESULT inherits acquisition guard unchanged")
    audit.check(result["cohort"] == {
        "parent_cardless_intake": 25, "removed_parent_selected_forms": 2,
        "renderer_rows": 376, "selected_spans": 23, "selected_forms": 23,
        "loci": 23, "page_labels": 23, "physical_folios": 20,
    }, "RESULT cohort exact")
    audit.check(result["precedence"] == {
        "full_parent_deck_matches": 23, "reader_exact_parent_deck_matches": 23,
        "nonexact_parent_deck_matches": 0, "parent_fallback_deck_matches": 23,
        "protected_contextual_deck_matches": 0, "selected_fallback_matches": 23,
        "nonselected_parent_rows_unchanged": 353,
    }, "RESULT precedence exact")
    audit.check(result["changes"] == {
        "fallback_replacements": 23, "actual_display_changes": 23,
        "contextual_sharpenings": 0, "contextual_confirmations": 0, "passage_patches": 23,
    }, "RESULT changes exact")
    audit.check(result["renderer"] == {
        "gdt780_contextual": 247, "gdt781_contextual": 270,
        "gdt780_fallbacks": 129, "gdt781_fallbacks": 106,
    }, "RESULT renderer transition exact")
    audit.check(result["consumption"] == {
        "gdt780_unique_right_tokens": 207, "gdt781_selected_right_tokens": 23,
        "same_row_inherited_takeovers": 0, "new_unique_right_tokens": 23,
        "total_unique_right_tokens": 230, "cross_row_collisions": 0,
    }, "RESULT consumption transition exact")
    audit.check(result["whole_analogy"] == {
        "dictionary_rows": 1606, "clean_axis_reading_rows": 770, "clean_axis_whole_pool": 769,
        "raw_relation_rows": 135, "a3_cards": 12, "a2_cards": 10, "a0_cards": 1,
        "a0_surface": "chorcholsal", "a0_raw_consensus_axes": "NONE",
        "a0_scope": "EXACT_ENUMERATED_OL_CHORCHOLSAL_SPAN_ONLY",
        "later_supplement_relations": 5, "later_supplements_in_raw_pool": 0,
        "target_local_axes_in_raw_consensus": 0, "eses_raw_neighbor_wholes": 3,
        "eses_raw_consensus_axes": "PREPARATION", "sheeoy_raw_neighbor_wholes": 6,
        "sheeoy_raw_analogy_tier": "A3_DISTANCE1_MULTIWHOLE_CONSENSUS",
    }, "RESULT whole analogy layers exact")
    audit.check(result["recurrence"] == {
        "cache_occurrences": 40, "reader_exact_occurrences": 32,
        "reader_exact_recurrent_forms": 7, "reader_exact_singleton_forms": 16,
        "chsky_cache_occurrences": 3, "chsky_reader_exact_occurrences": 1,
    }, "RESULT recurrence exact")
    audit.check(result["serial_evidence"] == {
        "cheedaiin_external_axes": "END_STAGE",
        "cheedaiin_external_bridge_tier": "B0_NO_WHOLE_FORM_BRIDGE",
        "otlaiin_target_local_axes": "END_STAGE",
        "otlaiin_target_local_bridge_tier": "B0_NO_WHOLE_FORM_BRIDGE",
    }, "RESULT serial external/local distinction exact")
    audit.check(result["chorcholsal_field_list"] == {
        "locus": "f88r.22", "target_occurrence_id": "G769-T0488",
        "status": "WORKING_DISPLAY_NOT_PLAINTEXT",
    }, "RESULT chorcholsal target-local field list exact")
    audit.check(result["residual_fallback_rows"] == 106 and result["residual_partition"] == {
        "no_card_reader_exact": 0, "v99_card_nonexact": 49,
        "no_card_reader_nonexact": 20, "line_final_no_right": 37,
    }, "RESULT residual split exact")
    audit.check(result["relation_packet"] == EXPECTED_EDGE_INTAKE,
                "RESULT relation packet exact and not score-ready")
    audit.check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"]
                == result["numeric_identities"] == result["specific_substances"]
                == result["component_exports"] == 0,
                "RESULT exports no lexeme plaintext number substance or component")
    audit.check(result["new_pages"] == result["new_images"] == result["new_ocr"]
                == result["new_transcriptions"] == result["sealed_pages_accessed"] == 0,
                "RESULT records zero acquisition and sealed access")

    report = REPORT.read_text(encoding="utf-8")
    audit.check(EXPECTED_STATUS in report, "REPORT states exact PASS status")
    audit.check("**247→270**" in report and "**129→106**" in report and "**207→230**" in report
                and "**353** Rendererzeilen" in report, "REPORT states all renderer transitions")
    audit.check("770 zulässige Lesungszeilen" in report and "769 vollständige Ganzwörter" in report
                and "135 ausgewählte" in report and "**12 A3, 10 A2 und 1 A0**" in report,
                "REPORT states independently reconstructed analogy totals")
    audit.check("`eses` behält roh seine" in report and "`sheeoy` behält roh sechs" in report
                and "`chorcholsal` bleibt roh A0/NONE" in report,
                "REPORT preserves raw and supplement layers")
    audit.check("WORKING_DISPLAY_NOT_PLAINTEXT" in report and "kein entschlüsselter" in report
                and "0 reader-exaktes" not in report,
                "REPORT labels field list as working display not plaintext")
    audit.check("49 nicht-exakte" in report and "20 nicht-exakte" in report and "37 Zeilenenden" in report
                and "kein reader-exaktes" in report, "REPORT states complete residual partition")
    audit.check("`f84` und `f84r` blieben versiegelt" in report,
                "REPORT explicitly records both sealed pages untouched")


def validate_hygiene(audit: Audit) -> None:
    for path in REPLAY_OUTPUTS:
        if path.suffix != ".tsv":
            continue
        rows = read_tsv(path)
        audit.check(all(not any(SEALED_RE.search(value) for value in row.values()) for row in rows),
                    "sealed f84/f84r absent from " + path.name)
    audit.check(all(not SEALED_RE.search(relative) for relative in EXPECTED_LOCKS),
                "source lock set contains no sealed path")
    audit.check("EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY" in EVIDENCE_OUT.read_text(encoding="utf-8")
                and all(row["selection_uses_substring"] == "0" for row in read_tsv(COHORT_OUT)),
                "whole-only scope and zero substring selection explicit in outputs")


def byte_replay(audit: Audit, runner_hash_before: str) -> dict[str, str]:
    published = {str(path.relative_to(EXP)): sha256(path) for path in REPLAY_OUTPUTS}
    with tempfile.TemporaryDirectory(prefix="gdt781-validator-") as temporary:
        temp = Path(temporary)
        artifacts = temp / "artifacts"
        report = temp / "REPORT.md"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        replay = subprocess.run(
            [sys.executable, "-B", str(RUN), "--artifacts-dir", str(artifacts), "--report-path", str(report)],
            cwd=ROOT, env=environment, text=True, capture_output=True, check=False,
        )
        audit.check(replay.returncode == 0, "runner temp-directory replay exits successfully")
        if replay.returncode:
            raise AssertionError("runner replay failed:\n" + replay.stdout + "\n" + replay.stderr)
        for original in REPLAY_OUTPUTS:
            generated = report if original == REPORT else artifacts / original.name
            audit.check(generated.is_file(), "replay generated " + original.name)
            audit.check(generated.read_bytes() == original.read_bytes(), "byte replay exact for " + original.name)
    audit.check(sha256(RUN) == runner_hash_before, "runner hash stable across byte replay")
    return published


def main() -> int:
    missing = [path for path in (RUN, *REPLAY_OUTPUTS) if not path.is_file()]
    if missing:
        raise FileNotFoundError("runner outputs not ready: " + ", ".join(path.name for path in missing))
    audit = Audit()
    runner_hash = sha256(RUN)
    source_hashes = validate_source_locks(audit)
    specs = validate_specs(audit)
    validate_runner_ast(audit)
    pool, summaries = build_clean_pool(audit)
    validate_raw_analogy(audit, specs, pool, summaries)
    validate_source_evidence(audit, specs, summaries)
    parent, parent_residual, selected, parent_tokens = reconstruct_parent(audit, specs)
    validate_cohort_output(audit, specs)
    validate_raw_relations_output(audit, pool, summaries)
    validate_evidence_output(audit, specs, summaries)
    atlas, new_tokens = validate_atlas_and_precedence(
        audit, parent, selected, specs, summaries, parent_tokens,
    )
    renderer = validate_renderer(audit, parent, atlas)
    validate_passages(audit, parent, renderer, atlas)
    validate_residual(audit, parent_residual, renderer, specs)
    validate_relation_packet(audit, atlas)
    validate_result_and_report(audit)
    validate_hygiene(audit)
    output_hashes = byte_replay(audit, runner_hash)

    value = {
        "experiment_id": "GDT781", "status": "PASS",
        "validator_independence": "14_SOURCES_HASHED__GDT780_INTAKE_MINUS_TWO_RECONSTRUCTED__770_READING_769_WHOLE_POOL_REBUILT__EXACT_WHOLE_LEVENSHTEIN_REPLAYED__PURE_AST_GATED__ALL_376_ROWS_RECONSTRUCTED__EDGE_GATED__BYTE_REPLAYED",
        "checks_passed": audit.count,
        "source_hash_count": len(source_hashes), "source_hashes": source_hashes,
        "spec_sha256": sha256(SPECS), "runner_sha256": runner_hash,
        "runner_output_replay_count": len(REPLAY_OUTPUTS), "runner_output_sha256": output_hashes,
        "selection": {
            "parent_cardless_intake": 25, "removed_parent_selected_forms": 2,
            "selected_spans": 23, "selected_forms": 23, "selected_loci": 23,
            "selected_page_labels": 23, "selected_physical_folios": 20,
            "selection_uses_occurrence_id": False, "selection_uses_page_or_locus": False,
            "selection_uses_analogy_or_meaning": False, "selection_uses_frequency": False,
            "selection_uses_substrings": False,
        },
        "whole_analogy": {
            "clean_axis_reading_rows": 770, "clean_axis_whole_pool": 769,
            "raw_relation_rows": 135, "a3_cards": 12, "a2_cards": 10, "a0_cards": 1,
            "eses_raw_consensus_axes": "PREPARATION", "eses_raw_neighbors": 3,
            "sheeoy_raw_neighbors": 6, "chorcholsal_raw_consensus_axes": "NONE",
            "later_supplement_relations": 5, "later_supplements_in_raw_pool": 0,
        },
        "recurrence": {
            "cache_occurrences": 40, "reader_exact_occurrences": 32,
            "reader_exact_recurrent_forms": 7, "reader_exact_singleton_forms": 16,
            "chsky_cache_occurrences": 3, "chsky_reader_exact_occurrences": 1,
        },
        "renderer": {
            "contextual_before": 247, "contextual_after": 270,
            "fallback_before": 129, "fallback_after": 106,
            "consumed_before": 207, "new_consumed_tokens": sorted(new_tokens),
            "consumed_after": 230, "nonselected_rows_inherited": 353,
            "cross_row_collisions": 0,
        },
        "residual_partition": {
            "no_card_reader_exact": 0, "v99_card_nonexact": 49,
            "no_card_reader_nonexact": 20, "line_final_no_right": 37,
        },
        "relation_packet_gate": EXPECTED_EDGE_INTAKE,
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "numeric_identities": 0, "specific_substances": 0,
        "component_exports": 0, "sealed_pages_accessed": 0, "errors": [],
    }
    destination = ART / "VALIDATION.json"
    destination.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
