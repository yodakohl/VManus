#!/usr/bin/env python3
"""Independent, fail-closed validation for GDT697.

This validator intentionally does not import or inspect the GDT697 renderer.
It reconstructs the seven allowed V70 windows from the preregistered TSV and
the frozen GDT696 relation layer, then checks every published projection.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
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
EXP = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords"
SRC = EXP / "src"
ART = EXP / "artifacts"
G696 = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries/artifacts"

STATUS = (
    "PASS_V70_7_EXACT_MICRORECORDS__9_EDGE_COVERAGE__"
    "1_SERIAL_CHAIN_1_SHARED_DESTINATION_REPEAT_5_SINGLE__"
    "ZERO_WORD_MEANING_DELTA"
)

SPEC = SRC / "V70_MICRORECORD_SPECS.tsv"
EDGE_SOURCE = G696 / "V69_9_LOCAL_ACTION_EDGES.tsv"
TOKEN_SOURCE = G696 / "V69_479_TOKEN_RELATION_OVERLAY.tsv"
LINE_SOURCE = G696 / "V69_51_LINE_RELATION_OVERLAY.tsv"
SPAN_SOURCE = G696 / "V69_3_BOUND_SPAN_FREEZE.tsv"
REFERENCE_SOURCE = G696 / "V69_27_REFERENCE_CENSUS.tsv"
RIVAL_SOURCE = G696 / "V69_17_RELATION_RIVALS.tsv"

MICRO_ARTIFACT = ART / "V70_7_EXACT_MICRORECORDS.tsv"
EDGE_ARTIFACT = ART / "V70_9_EDGE_WINDOW_COVERAGE.tsv"
WINDOW_TOKEN_ARTIFACT = ART / "V70_19_WINDOW_TOKEN_ROLES.tsv"
TOKEN_ARTIFACT = ART / "V70_479_TOKEN_FREEZE.tsv"
LINE_ARTIFACT = ART / "V70_51_LINE_MICRORECORD_OVERLAY.tsv"
SPAN_ARTIFACT = ART / "V70_3_BOUND_SPAN_FREEZE.tsv"
CENSUS_ARTIFACT = ART / "V70_TOPOLOGY_CENSUS.tsv"
READER_ARTIFACT = ART / "GDT697_V70_EXACT_MICRORECORD_READER.md"

EXPECTED_GENERATED = {
    "GDT697_V70_EXACT_MICRORECORD_READER.md",
    "README.md",
    "V70_3_BOUND_SPAN_FREEZE.tsv",
    "V70_7_EXACT_MICRORECORDS.tsv",
    "V70_9_EDGE_WINDOW_COVERAGE.tsv",
    "V70_19_WINDOW_TOKEN_ROLES.tsv",
    "V70_51_LINE_MICRORECORD_OVERLAY.tsv",
    "V70_479_TOKEN_FREEZE.tsv",
    "V70_TOPOLOGY_CENSUS.tsv",
}

SPEC_SHA256 = "1debb76d8d5589e5c740c4a86c426d8fe5996814ab52928c744616f19c56bd9f"

SPEC_FIELDS = [
    "microrecord_id",
    "locus",
    "window_start_ordinal",
    "window_end_ordinal",
    "edge_ids",
    "topology",
    "action_ordinals",
    "working_edge_ids",
    "expected_surfaces",
    "expected_glosses_de",
    "expected_role_trace",
    "microrecord_de",
    "left_boundary",
    "right_boundary",
    "outside_reference_ids",
    "outside_rival_ids",
    "boundary_note_de",
    "composition_basis",
    "forbidden_inference",
]

MICRO_FIELDS = [
    "microrecord_id",
    "locus",
    "window_start_ordinal",
    "window_end_ordinal",
    "window_token_count",
    "edge_ids",
    "edge_count",
    "topology",
    "action_ordinals",
    "action_count",
    "working_edge_ids",
    "strong_edge_ids",
    "support_profile",
    "expected_surfaces",
    "observed_surfaces",
    "expected_glosses_de",
    "observed_glosses_de",
    "expected_role_trace",
    "observed_role_trace",
    "v68_clause_ids",
    "microrecord_de",
    "left_boundary",
    "right_boundary",
    "left_neighbor_ordinal",
    "left_neighbor_surface",
    "right_neighbor_ordinal",
    "right_neighbor_surface",
    "outside_reference_ids",
    "outside_rival_ids",
    "boundary_note_de",
    "composition_basis",
    "forbidden_inference",
    "minimal_convex_hull",
    "edge_coverage_exact",
    "final_result_status",
    "v69_word_delta",
    "status",
]

EDGE_FIELDS = [
    "edge_id",
    "microrecord_id",
    "locus",
    "support_tier",
    "relation_class",
    "source_ordinals",
    "reference_ordinals",
    "target_action_ordinal",
    "right_participant_ordinals",
    "node_ordinals",
    "window_start_ordinal",
    "window_end_ordinal",
    "operation_rank",
    "topology",
    "edge_role_in_window",
    "shared_node_ordinals",
    "source_join_exact",
    "reference_join_exact",
    "target_join_exact",
    "covered_once",
    "v68_word_delta",
    "status",
]

WINDOW_TOKEN_FIELDS = [
    "page",
    "locus",
    "token_ordinal",
    "surface",
    "v69_token_gloss_de",
    "microrecord_id",
    "window_position",
    "window_size",
    "role_trace",
    "edge_ids",
    "source_edge_ids",
    "reference_edge_ids",
    "target_edge_ids",
    "right_participant_edge_ids",
    "is_action_target",
    "is_shared_node",
    "is_action_output_bridge",
    "is_window_start",
    "is_window_end",
    "v68_clause_id",
    "v68_clause_type",
    "v70_microrecord_de",
    "v69_word_delta",
    "status",
]

TOKEN_EXTRA_FIELDS = [
    "v70_microrecord_id",
    "v70_window_role_trace",
    "v70_window_position",
    "v70_window_size",
    "v70_microrecord_de",
    "v70_token_gloss_de",
    "v70_word_delta",
    "v70_status",
]

LINE_EXTRA_FIELDS = [
    "v70_microrecord_ids",
    "v70_microrecords_de",
    "v70_window_ordinals",
    "v70_topologies",
    "v70_support_profiles",
    "v70_named_intermediate_output_count",
    "v70_named_final_result_count",
    "v70_clause_translation_de",
    "v70_word_delta",
    "v70_status",
]

SPAN_EXTRA_FIELDS = [
    "v70_selected_gloss_de",
    "v70_byte_identical",
    "v70_microrecord_overlap",
    "v70_status",
]

CENSUS_FIELDS = ["dimension", "value", "count", "member_ids", "note"]

# These occurrence coordinates are duplicated deliberately.  A changed source
# TSV must not silently redefine what the validator considers GDT697.
EXPECTED_CORE = {
    "M001": {
        "locus": "f104v.2",
        "start": 4,
        "end": 6,
        "edges": ["C009"],
        "topology": "SINGLE_SUBSET_OPERATION",
        "actions": [6],
        "working": ["C009"],
        "outside_refs": ["R001"],
        "outside_rivals": [],
        "microrecord": "Kalter Ansatz, Grad III: davon drei Maße. Eines der drei Maße nehmen und erhitzen.",
    },
    "M002": {
        "locus": "f105v.1",
        "start": 3,
        "end": 4,
        "edges": ["C001"],
        "topology": "SINGLE_OBJECT_OPERATION",
        "actions": [4],
        "working": [],
        "outside_refs": ["R005"],
        "outside_rivals": ["H001"],
        "microrecord": "Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen.",
    },
    "M003": {
        "locus": "f113v.17",
        "start": 6,
        "end": 7,
        "edges": ["C002"],
        "topology": "SINGLE_SUBSET_OPERATION",
        "actions": [7],
        "working": [],
        "outside_refs": [],
        "outside_rivals": [],
        "microrecord": "Von den drei Portionen Krautdroge eine Portion bis zur letzten Stufe abkühlen.",
    },
    "M004": {
        "locus": "f75r.3",
        "start": 3,
        "end": 4,
        "edges": ["C003"],
        "topology": "SINGLE_OBJECT_OPERATION",
        "actions": [4],
        "working": [],
        "outside_refs": [],
        "outside_rivals": ["P005"],
        "microrecord": "Die vorstehende, bis zur Mittelstufe getrocknete Drogenportion anschließend nehmen.",
    },
    "M005": {
        "locus": "f77r.38",
        "start": 5,
        "end": 6,
        "edges": ["C005"],
        "topology": "SINGLE_OBJECT_OPERATION",
        "actions": [6],
        "working": [],
        "outside_refs": [],
        "outside_rivals": [],
        "microrecord": "Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum zugeben.",
    },
    "M006": {
        "locus": "f80v.35",
        "start": 3,
        "end": 6,
        "edges": ["C004", "C008"],
        "topology": "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT",
        "actions": [5, 6],
        "working": ["C008"],
        "outside_refs": [],
        "outside_rivals": [],
        "microrecord": "Dem Anteil I des heißen Holzansatzes Drogenstoff zugeben. Dem Anteil I des heißen Holzansatzes nochmals Drogenstoff zugeben.",
    },
    "M007": {
        "locus": "f86v6.25",
        "start": 2,
        "end": 5,
        "edges": ["C007", "C006"],
        "topology": "SERIAL_ACTION_OUTPUT_CHAIN",
        "actions": [4, 5],
        "working": ["C007"],
        "outside_refs": ["R023", "R025"],
        "outside_rivals": [],
        "microrecord": "Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. Den so abgemessenen Drogenanteil I auf Stufe III erhitzen.",
    },
}

EXPECTED_OPERATIONS = {
    "M001": Counter({"nehmen": 1, "erhitzen": 1}),
    "M002": Counter({"erhitzen": 1}),
    "M003": Counter({"abkühlen": 1}),
    "M004": Counter({"nehmen": 1}),
    "M005": Counter({"zugeben": 1}),
    "M006": Counter({"zugeben": 2}),
    "M007": Counter({"abmessen": 1, "erhitzen": 1}),
}

EXPECTED_EDGE_TIERS = {
    "C001": "A_STRONG_LICENSED",
    "C002": "A_STRONG_LICENSED",
    "C003": "A_STRONG_LICENSED",
    "C004": "A_STRONG_LICENSED",
    "C005": "A_STRONG_LICENSED",
    "C006": "A_MINUS_EXPLICIT_OUTPUT",
    "C007": "B_WORKING_LOCAL",
    "C008": "B_WORKING_LOCAL",
    "C009": "B_WORKING_LOCAL",
}

EXPECTED_PUBLISHED_TOPOLOGY = {
    "M001": "SINGLE_EDGE",
    "M002": "SINGLE_EDGE",
    "M003": "SINGLE_EDGE",
    "M004": "SINGLE_EDGE",
    "M005": "SINGLE_EDGE",
    "M006": "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT",
    "M007": "SERIAL_ACTION_OUTPUT_CHAIN",
}

EXPECTED_SUPPORT_PROFILE = {
    "M001": "B_ONLY",
    "M002": "A_ONLY",
    "M003": "A_ONLY",
    "M004": "A_ONLY",
    "M005": "A_ONLY",
    "M006": "A_PLUS_B",
    "M007": "A_MINUS_PLUS_B",
}

EXPECTED_EDGE_ROLE = {
    "C001": "SINGLE_OPERATION",
    "C002": "SINGLE_OPERATION",
    "C003": "SINGLE_OPERATION",
    "C004": "COMMON_DESTINATION_FIRST",
    "C005": "SINGLE_OPERATION",
    "C006": "SERIAL_CONSUMER",
    "C007": "SERIAL_PRODUCER",
    "C008": "COMMON_DESTINATION_REPEAT_WORKING",
    "C009": "SINGLE_OPERATION",
}

FORBIDDEN_LOCUS_RE = re.compile(r"^f84(?:r|v)?(?:\b|\.)", re.IGNORECASE)
FORBIDDEN_MICRORECORD_RE = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsgegenstand|Arbeitsmaterial|Arbeitsblock|"
    r"Materialblock|Werkstück|Arbeitsschritt|Arbeitszyklus|Arbeitsstelle|"
    r"Hauptstelle|Zielstelle|Quellstelle|Zielgefäß|Quellgefäß|Prozess|"
    r"Verfahren|ausführen|weiterleiten|Produkt|Endprodukt|Wasser|Wein|Öl|"
    r"Salz|Wurzel|Blatt|Frau|Krankheit|Heilung|Behälter|Gefäß|Kessel|"
    r"Topf|Mörser|Bad)\b",
    re.IGNORECASE,
)
INVENTED_RESULT_RE = re.compile(
    r"\b(?:ergibt|entsteht|erzeugt|herstellen|gewinnen|resultiert)\b",
    re.IGNORECASE,
)
OPERATION_RE = re.compile(
    r"\b(?:abmessen|abkühlen|abziehen|abschließen|einweichen|erhitzen|"
    r"nehmen|trocknen|umfüllen|zugeben)\b",
    re.IGNORECASE,
)


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, object]] = []

    def check(self, condition: bool, name: str) -> None:
        passed = bool(condition)
        self.checks.append({"check": name, "pass": int(passed)})
        if not passed:
            raise AssertionError(name)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(
    path: Path,
    *,
    exact_fields: Sequence[str] | None = None,
) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if not fields or len(fields) != len(set(fields)):
        raise AssertionError(f"invalid or duplicate TSV header: {path}")
    if exact_fields is not None and fields != list(exact_fields):
        raise AssertionError(f"unexpected TSV schema: {path}")
    for number, row in enumerate(rows, start=2):
        if None in row or set(row) != set(fields):
            raise AssertionError(f"malformed TSV row {number}: {path}")
        if any(value is None for value in row.values()):
            raise AssertionError(f"missing TSV field at row {number}: {path}")
    return fields, rows


def indexed(
    rows: Sequence[Mapping[str, str]],
    key_fields: Sequence[str],
    context: str,
) -> dict[tuple[str, ...], Mapping[str, str]]:
    result: dict[tuple[str, ...], Mapping[str, str]] = {}
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        if key in result:
            raise AssertionError(f"duplicate key {key!r}: {context}")
        result[key] = row
    return result


def integer(text: str, context: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]*", text):
        raise AssertionError(f"invalid positive integer {text!r}: {context}")
    return int(text)


def id_list(text: str) -> list[str]:
    return [] if text == "NONE" else text.split("|")


def ordinal_list(text: str, context: str) -> list[int]:
    if text == "NONE":
        return []
    values: list[int] = []
    for item in text.split("|"):
        match = re.fullmatch(r"([1-9][0-9]*)(?:-([1-9][0-9]*))?", item)
        if not match:
            raise AssertionError(f"invalid ordinal list {text!r}: {context}")
        start = int(match.group(1))
        end = int(match.group(2) or match.group(1))
        if end < start:
            raise AssertionError(f"descending ordinal range {item!r}: {context}")
        values.extend(range(start, end + 1))
    if len(values) != len(set(values)):
        raise AssertionError(f"duplicate ordinal in {text!r}: {context}")
    return values


def role_map(text: str, context: str) -> dict[int, str]:
    roles: dict[int, str] = {}
    for item in text.split("|"):
        match = re.fullmatch(r"([1-9][0-9]*):([A-Z][A-Z_]*)", item)
        if not match:
            raise AssertionError(f"invalid role item {item!r}: {context}")
        ordinal = int(match.group(1))
        if ordinal in roles:
            raise AssertionError(f"duplicate role ordinal {ordinal}: {context}")
        roles[ordinal] = match.group(2)
    return roles


def join_or_none(values: Iterable[str]) -> str:
    materialized = list(values)
    return "|".join(materialized) if materialized else "NONE"


def support_profile_for(edge_ids: Sequence[str]) -> str:
    tiers = Counter(EXPECTED_EDGE_TIERS[edge_id] for edge_id in edge_ids)
    profiles = {
        (("A_STRONG_LICENSED", 1),): "A_ONLY",
        (("B_WORKING_LOCAL", 1),): "B_ONLY",
        (("A_STRONG_LICENSED", 1), ("B_WORKING_LOCAL", 1)): "A_PLUS_B",
        (("A_MINUS_EXPLICIT_OUTPUT", 1), ("B_WORKING_LOCAL", 1)): "A_MINUS_PLUS_B",
    }
    key = tuple(sorted(tiers.items()))
    if key not in profiles:
        raise AssertionError(f"unsupported edge-tier profile: {dict(tiers)!r}")
    return profiles[key]


def no_forbidden_locus(rows: Iterable[Mapping[str, str]]) -> bool:
    return all(
        not FORBIDDEN_LOCUS_RE.match(row.get(field, ""))
        for row in rows
        for field in ("page", "locus")
        if row.get(field, "")
    )


def assert_projection(
    audit: Audit,
    source_fields: Sequence[str],
    source_rows: Sequence[Mapping[str, str]],
    published_fields: Sequence[str],
    published_rows: Sequence[Mapping[str, str]],
    name: str,
) -> None:
    audit.check(
        list(published_fields[: len(source_fields)]) == list(source_fields),
        f"{name} retains inherited columns first and in order",
    )
    audit.check(len(source_rows) == len(published_rows), f"{name} row count exact")
    audit.check(
        all(
            tuple(published[field] for field in source_fields)
            == tuple(source[field] for field in source_fields)
            for source, published in zip(source_rows, published_rows)
        ),
        f"{name} inherited projection byte-exact and ordered",
    )


def values_for_key(payload: object, key: str) -> list[object]:
    values: list[object] = []
    if isinstance(payload, dict):
        for current_key, value in payload.items():
            if current_key == key:
                values.append(value)
            values.extend(values_for_key(value, key))
    elif isinstance(payload, list):
        for value in payload:
            values.extend(values_for_key(value, key))
    return values


def require_metric(
    audit: Audit,
    payload: object,
    names: Sequence[str],
    expected: object,
    label: str,
) -> None:
    found = [value for name in names for value in values_for_key(payload, name)]
    audit.check(bool(found), f"RESULT publishes {label}")
    audit.check(all(value == expected for value in found), f"RESULT {label} exact")


def main() -> int:
    audit = Audit()

    # Fixed sources and their own published hashes.
    audit.check(sha256(SPEC) == SPEC_SHA256, "V70 preregistered specification hash exact")
    spec_fields, specs = read_tsv(SPEC, exact_fields=SPEC_FIELDS)
    edge_fields, edges = read_tsv(EDGE_SOURCE)
    token_fields, tokens = read_tsv(TOKEN_SOURCE)
    line_fields, lines = read_tsv(LINE_SOURCE)
    span_fields, spans = read_tsv(SPAN_SOURCE)
    _, references = read_tsv(REFERENCE_SOURCE)
    _, rivals = read_tsv(RIVAL_SOURCE)
    g696_result = json.loads((G696 / "RESULT.json").read_text(encoding="utf-8"))
    for path in (
        EDGE_SOURCE,
        TOKEN_SOURCE,
        LINE_SOURCE,
        SPAN_SOURCE,
        REFERENCE_SOURCE,
        RIVAL_SOURCE,
    ):
        audit.check(
            g696_result.get("files", {}).get(path.name) == sha256(path),
            f"GDT696 source hash remains sealed: {path.name}",
        )
    audit.check(len(edges) == 9, "GDT696 supplies exactly nine admitted edges")
    audit.check(len(tokens) == 479, "GDT696 supplies exactly 479 frozen tokens")
    audit.check(len(lines) == 51, "GDT696 supplies exactly 51 frozen lines")
    audit.check(len(spans) == 3, "GDT696 supplies exactly three frozen spans")
    audit.check(len(references) == 27, "GDT696 reference census remains complete at 27")
    audit.check(len(rivals) == 17, "GDT696 held-rival deck remains complete at 17")
    audit.check(
        no_forbidden_locus([*specs, *edges, *tokens, *lines, *spans, *references, *rivals]),
        "fixed inputs exclude f84/f84r",
    )

    edge_by_id = indexed(edges, ["edge_id"], "GDT696 edges")
    token_by_key = indexed(tokens, ["locus", "token_ordinal"], "GDT696 tokens")
    line_by_locus = indexed(lines, ["locus"], "GDT696 lines")
    reference_by_id = indexed(references, ["reference_id"], "GDT696 references")
    rival_by_id = indexed(rivals, ["rival_id"], "GDT696 rivals")

    audit.check(
        {key[0] for key in edge_by_id} == set(EXPECTED_EDGE_TIERS),
        "closed C001-C009 edge identity",
    )
    audit.check(
        {edge_id: edge_by_id[(edge_id,)]["support_tier"] for edge_id in EXPECTED_EDGE_TIERS}
        == EXPECTED_EDGE_TIERS,
        "five strong, one A-minus and three working tiers exact",
    )

    # Reconstruct all roles solely from the GDT696 edge coordinates.
    source_roles: dict[tuple[str, int], list[str]] = defaultdict(list)
    reference_roles: dict[tuple[str, int], list[str]] = defaultdict(list)
    target_roles: dict[tuple[str, int], list[str]] = defaultdict(list)
    right_roles: dict[tuple[str, int], list[str]] = defaultdict(list)
    edge_nodes: dict[str, set[int]] = {}
    edge_sources: dict[str, list[int]] = {}
    edge_references: dict[str, list[int]] = {}
    edge_right: dict[str, list[int]] = {}
    edge_target: dict[str, int] = {}
    for edge_id in sorted(EXPECTED_EDGE_TIERS):
        edge = edge_by_id[(edge_id,)]
        locus = edge["locus"]
        start = integer(edge["source_start_ordinal"], edge_id)
        end = integer(edge["source_end_ordinal"], edge_id)
        sources = list(range(start, end + 1))
        references_here = ordinal_list(edge["reference_ordinal"], edge_id)
        target = integer(edge["target_action_ordinal"], edge_id)
        right = ordinal_list(edge["right_participant_ordinals"], edge_id)
        roles = role_map(edge["left_role_map"], edge_id)
        audit.check(list(roles) == sources, f"{edge_id} exact left-role ordinal coverage")
        source_tokens = [token_by_key.get((locus, str(ordinal))) for ordinal in sources]
        audit.check(all(source_tokens), f"{edge_id} source ordinals exist in frozen V69")
        source_tokens = [token for token in source_tokens if token is not None]
        audit.check(
            [token["surface"] for token in source_tokens]
            == edge["expected_source_surfaces"].split("|"),
            f"{edge_id} source surfaces join exactly",
        )
        audit.check(
            [token["v69_token_gloss_de"] for token in source_tokens]
            == edge["expected_source_glosses_de"].split(" || "),
            f"{edge_id} source glosses join exactly",
        )
        target_token = token_by_key.get((locus, str(target)))
        audit.check(target_token is not None, f"{edge_id} target ordinal exists in frozen V69")
        assert target_token is not None
        audit.check(
            target_token["surface"] == edge["expected_target_surface"]
            and target_token["v69_token_gloss_de"] == edge["expected_target_gloss_de"]
            and target_token["v68_clause_type"] == "ACTION_CLAUSE"
            and target_token["v68_action_license"] == "GDT689_V62_ACTION_ORDINAL",
            f"{edge_id} target surface, gloss and action license exact",
        )
        if references_here:
            audit.check(len(references_here) == 1, f"{edge_id} has at most one written reference")
            reference_token = token_by_key.get((locus, str(references_here[0])))
            audit.check(reference_token is not None, f"{edge_id} reference ordinal exists in frozen V69")
            assert reference_token is not None
            audit.check(
                reference_token["surface"] == edge["expected_reference_surface"]
                and reference_token["v69_token_gloss_de"] == edge["expected_reference_gloss_de"],
                f"{edge_id} reference surface and gloss exact",
            )
        else:
            audit.check(
                edge["expected_reference_surface"]
                == edge["expected_reference_gloss_de"]
                == "NONE",
                f"{edge_id} has no invented reference token",
            )
        for ordinal in sources:
            source_roles[(locus, ordinal)].append(f"{roles[ordinal]}:{edge_id}")
        for ordinal in references_here:
            reference_roles[(locus, ordinal)].append(f"REFERENCE:{edge_id}")
        target_roles[(locus, target)].append(f"TARGET_ACTION:{edge_id}")
        for ordinal in right:
            right_roles[(locus, ordinal)].append(f"RIGHT_PARTICIPANT:{edge_id}")
        edge_sources[edge_id] = sources
        edge_references[edge_id] = references_here
        edge_target[edge_id] = target
        edge_right[edge_id] = right
        edge_nodes[edge_id] = set([*sources, *references_here, target, *right])

    # The source TSV itself is fixed, minimal and exhaustive.
    audit.check(len(specs) == 7, "exactly seven V70 microrecord specifications")
    spec_by_id = indexed(specs, ["microrecord_id"], "V70 specifications")
    audit.check(
        [row["microrecord_id"] for row in specs] == [f"M{number:03d}" for number in range(1, 8)],
        "closed ordered M001-M007 identity",
    )
    audit.check(set(key[0] for key in spec_by_id) == set(EXPECTED_CORE), "closed seven-window identity")

    edge_use: Counter[str] = Counter()
    window_positions: dict[tuple[str, int], str] = {}
    expected_window_roles: dict[tuple[str, int], str] = {}
    expected_window_edges: dict[tuple[str, int], list[str]] = {}
    expected_source_edges: dict[tuple[str, int], list[str]] = {}
    expected_reference_edges: dict[tuple[str, int], list[str]] = {}
    expected_target_edges: dict[tuple[str, int], list[str]] = {}
    expected_right_edges: dict[tuple[str, int], list[str]] = {}
    clause_positions: set[tuple[str, str]] = set()
    reference_positions: set[tuple[str, int]] = set()

    for spec in specs:
        micro_id = spec["microrecord_id"]
        expected = EXPECTED_CORE[micro_id]
        locus = spec["locus"]
        start = integer(spec["window_start_ordinal"], micro_id)
        end = integer(spec["window_end_ordinal"], micro_id)
        assigned_edges = id_list(spec["edge_ids"])
        actions = ordinal_list(spec["action_ordinals"], micro_id)
        working = id_list(spec["working_edge_ids"])
        audit.check(
            {
                "locus": locus,
                "start": start,
                "end": end,
                "edges": assigned_edges,
                "topology": spec["topology"],
                "actions": actions,
                "working": working,
                "outside_refs": id_list(spec["outside_reference_ids"]),
                "outside_rivals": id_list(spec["outside_rival_ids"]),
                "microrecord": spec["microrecord_de"],
            }
            == expected,
            f"{micro_id} fixed locus/window/topology/text contract",
        )
        audit.check(start <= end, f"{micro_id} nonempty window")
        audit.check(all((edge_id,) in edge_by_id for edge_id in assigned_edges), f"{micro_id} uses only admitted edges")
        audit.check(
            all(edge_by_id[(edge_id,)]["locus"] == locus for edge_id in assigned_edges),
            f"{micro_id} edges belong to its exact locus",
        )
        for edge_id in assigned_edges:
            edge_use[edge_id] += 1
        expected_actions = sorted(edge_target[edge_id] for edge_id in assigned_edges)
        audit.check(actions == expected_actions, f"{micro_id} exact written action ordinals")
        audit.check(
            working
            == [edge_id for edge_id in assigned_edges if EXPECTED_EDGE_TIERS[edge_id] == "B_WORKING_LOCAL"],
            f"{micro_id} working-edge IDs exact",
        )
        all_nodes = set().union(*(edge_nodes[edge_id] for edge_id in assigned_edges))
        audit.check(
            (start, end) == (min(all_nodes), max(all_nodes)),
            f"{micro_id} is the minimal convex hull of its admitted nodes",
        )
        audit.check(
            all(start <= ordinal <= end for ordinal in all_nodes),
            f"{micro_id} contains every and only bounded edge node",
        )

        observed_surfaces: list[str] = []
        observed_glosses: list[str] = []
        observed_role_segments: list[str] = []
        for position, ordinal in enumerate(range(start, end + 1), start=1):
            key = locus, ordinal
            audit.check(key not in window_positions, f"unique window position {locus}#{ordinal}")
            window_positions[key] = micro_id
            token = token_by_key.get((locus, str(ordinal)))
            audit.check(token is not None, f"{micro_id} token exists at ordinal {ordinal}")
            assert token is not None
            observed_surfaces.append(token["surface"])
            observed_glosses.append(token["v69_token_gloss_de"])
            clause_positions.add((locus, token["v68_clause_id"]))

            source_here = [
                edge_id for edge_id in assigned_edges
                if ordinal in edge_sources[edge_id]
            ]
            reference_here = [
                edge_id for edge_id in assigned_edges
                if ordinal in edge_references[edge_id]
            ]
            target_here = [
                edge_id for edge_id in assigned_edges
                if ordinal == edge_target[edge_id]
            ]
            right_here = [
                edge_id for edge_id in assigned_edges
                if ordinal in edge_right[edge_id]
            ]
            roles_here = [
                role
                for edge_id in source_here
                for role in source_roles[(locus, ordinal)]
                if role.endswith(f":{edge_id}")
            ]
            roles_here.extend(f"REFERENCE:{edge_id}" for edge_id in reference_here)
            roles_here.extend(f"TARGET_ACTION:{edge_id}" for edge_id in target_here)
            roles_here.extend(f"RIGHT_PARTICIPANT:{edge_id}" for edge_id in right_here)
            audit.check(bool(roles_here), f"{micro_id} ordinal {ordinal} has an admitted role")
            role_trace = "|".join(roles_here)
            observed_role_segments.append(role_trace)
            expected_window_roles[key] = role_trace
            expected_source_edges[key] = sorted(source_here)
            expected_reference_edges[key] = sorted(reference_here)
            expected_target_edges[key] = sorted(target_here)
            expected_right_edges[key] = sorted(right_here)
            expected_window_edges[key] = sorted(set([*source_here, *reference_here, *target_here, *right_here]))
            if reference_here:
                reference_positions.add(key)
            audit.check(
                token["v69_relation_roles"] == role_trace,
                f"{micro_id} ordinal {ordinal} role trace equals GDT696 overlay",
            )
            audit.check(
                token["v69_edge_ids"] == join_or_none(expected_window_edges[key]),
                f"{micro_id} ordinal {ordinal} edge membership equals GDT696",
            )

        audit.check(
            spec["expected_surfaces"] == "|".join(observed_surfaces),
            f"{micro_id} exact surface sequence",
        )
        audit.check(
            spec["expected_glosses_de"] == " || ".join(observed_glosses),
            f"{micro_id} exact V69 gloss sequence",
        )
        audit.check(
            spec["expected_role_trace"] == " || ".join(observed_role_segments),
            f"{micro_id} exact source/reference/target role trace",
        )

        outside_refs = id_list(spec["outside_reference_ids"])
        outside_rivals = id_list(spec["outside_rival_ids"])
        for reference_id in outside_refs:
            row = reference_by_id.get((reference_id,))
            audit.check(row is not None, f"{micro_id} outside reference {reference_id} exists")
            assert row is not None
            ordinal = integer(row["reference_ordinal"], reference_id)
            audit.check(row["locus"] == locus and not start <= ordinal <= end, f"{micro_id} {reference_id} truly remains outside")
            audit.check(row["linked_edge_ids"] == "NONE", f"{micro_id} {reference_id} is not an admitted inner edge")
        for rival_id in outside_rivals:
            row = rival_by_id.get((rival_id,))
            audit.check(row is not None, f"{micro_id} outside rival {rival_id} exists")
            assert row is not None
            target = integer(row["target_action_ordinal"], rival_id)
            audit.check(row["locus"] == locus and not start <= target <= end, f"{micro_id} {rival_id} target truly remains outside")
            audit.check(row["decision"] == "HELD_AS_RIVAL_NOT_ADMITTED", f"{micro_id} {rival_id} remains held")

        audit.check(
            not FORBIDDEN_MICRORECORD_RE.search(spec["microrecord_de"]),
            f"{micro_id} contains no generic filler or invented concrete noun",
        )
        audit.check(
            not INVENTED_RESULT_RE.search(spec["microrecord_de"]),
            f"{micro_id} contains no invented result claim",
        )
        operations = Counter(match.group(0).lower() for match in OPERATION_RE.finditer(spec["microrecord_de"]))
        audit.check(operations == EXPECTED_OPERATIONS[micro_id], f"{micro_id} contains only licensed written operations")

    audit.check(
        edge_use == Counter({edge_id: 1 for edge_id in EXPECTED_EDGE_TIERS}),
        "all and only nine admitted edges are used exactly once",
    )
    audit.check(len(window_positions) == 19, "seven minimal windows contain 19 unique token positions")
    audit.check(len({row["locus"] for row in specs}) == 7, "seven windows occupy seven distinct loci")
    audit.check(len(clause_positions) == 16, "windows touch exactly 16 distinct V68 clauses")
    audit.check(len(reference_positions) == 6, "windows contain exactly six written reference positions")
    audit.check(
        sum(len(expected_target_edges[key]) for key in expected_target_edges) == 9,
        "windows contain exactly nine action-target roles",
    )

    # No target from the held deck may have entered any window.
    held_targets = {
        (row["locus"], integer(row["target_action_ordinal"], row["rival_id"]))
        for row in rivals
    }
    audit.check(held_targets.isdisjoint(window_positions), "no held-rival target occurs inside a V70 window")

    # Two multi-edge topologies are checked as graphs, not labels alone.
    f80 = EXPECTED_CORE["M006"]
    audit.check(
        edge_sources["C004"] == edge_sources["C008"] == [3]
        and edge_target["C004"] == 5
        and edge_target["C008"] == 6
        and edge_references["C004"] == [4]
        and edge_references["C008"] == [],
        "f80v.35 is one exact shared-destination fanout with only the first written reference",
    )
    audit.check(
        (f80["start"], f80["end"]) == (3, 6),
        "f80v.35 fanout has the exact four-token convex hull",
    )
    f86 = EXPECTED_CORE["M007"]
    audit.check(
        edge_target["C007"] == 4
        and edge_sources["C006"] == [4]
        and edge_target["C006"] == 5,
        "f86v6.25 has the exact C007-to-C006 serial action-output bridge",
    )
    audit.check(
        source_roles[("f86v6.25", 2)] == ["OUTPUT_LABEL:C007"]
        and source_roles[("f86v6.25", 3)] == ["DONOR_SOURCE_SHARE:C007"]
        and (f86["start"], f86["end"]) == (2, 5),
        "f86v6.25 preserves one preposed output label and one true donor source",
    )
    final_outgoing_carries = 0
    for micro_id, expected in EXPECTED_CORE.items():
        ordered_edges = sorted(expected["edges"], key=lambda edge_id: edge_target[edge_id])
        final_edge = ordered_edges[-1]
        final_target = edge_target[final_edge]
        final_outgoing_carries += sum(
            final_target in edge_sources[edge_id]
            for edge_id in ordered_edges
            if edge_id != final_edge
        )
    audit.check(final_outgoing_carries == 0, "all seven windows have zero outgoing carry from the final action")

    # Published compact microrecords.
    _, published_micro = read_tsv(MICRO_ARTIFACT, exact_fields=MICRO_FIELDS)
    published_micro_by_id = indexed(published_micro, ["microrecord_id"], "published microrecords")
    audit.check(len(published_micro) == 7, "published deck has seven microrecords")
    audit.check(set(published_micro_by_id) == set(spec_by_id), "published deck covers M001-M007 exactly")
    for spec in specs:
        micro_id = spec["microrecord_id"]
        row = published_micro_by_id[(micro_id,)]
        expected = EXPECTED_CORE[micro_id]
        locus = expected["locus"]
        start, end = expected["start"], expected["end"]
        edges_here = expected["edges"]
        tokens_here = [token_by_key[(locus, str(ordinal))] for ordinal in range(start, end + 1)]
        inherited_spec_fields = [
            field for field in SPEC_FIELDS
            if field in MICRO_FIELDS and field != "topology"
        ]
        audit.check(
            all(row[field] == spec[field] for field in inherited_spec_fields),
            f"{micro_id} publishes its complete preregistered wording and boundaries",
        )
        strong_here = [edge_id for edge_id in edges_here if EXPECTED_EDGE_TIERS[edge_id] != "B_WORKING_LOCAL"]
        clauses_here = list(dict.fromkeys(token["v68_clause_id"] for token in tokens_here))
        left_key = (locus, str(start - 1))
        right_key = (locus, str(end + 1))
        left_neighbor = token_by_key.get(left_key)
        right_neighbor = token_by_key.get(right_key)
        audit.check(row["window_token_count"] == str(end - start + 1), f"{micro_id} published window size exact")
        audit.check(row["edge_count"] == str(len(edges_here)), f"{micro_id} published edge count exact")
        audit.check(row["action_count"] == str(len(expected["actions"])), f"{micro_id} published action count exact")
        audit.check(
            row["topology"] == EXPECTED_PUBLISHED_TOPOLOGY[micro_id],
            f"{micro_id} published topology family exact",
        )
        audit.check(row["strong_edge_ids"] == join_or_none(strong_here), f"{micro_id} strong/A-minus IDs remain distinct from working")
        audit.check(
            row["support_profile"]
            == EXPECTED_SUPPORT_PROFILE[micro_id]
            == support_profile_for(edges_here),
            f"{micro_id} support profile exact",
        )
        audit.check(row["observed_surfaces"] == spec["expected_surfaces"], f"{micro_id} observed surfaces equal frozen expectation")
        audit.check(row["observed_glosses_de"] == spec["expected_glosses_de"], f"{micro_id} observed glosses equal frozen expectation")
        audit.check(row["observed_role_trace"] == spec["expected_role_trace"], f"{micro_id} observed roles equal fixed trace")
        audit.check(row["v68_clause_ids"] == join_or_none(clauses_here), f"{micro_id} exact V68 clause coverage")
        audit.check(
            (row["left_neighbor_ordinal"], row["left_neighbor_surface"])
            == (
                str(start - 1) if left_neighbor else "NONE",
                left_neighbor["surface"] if left_neighbor else "NONE",
            ),
            f"{micro_id} left boundary neighbor exact",
        )
        audit.check(
            (row["right_neighbor_ordinal"], row["right_neighbor_surface"])
            == (
                str(end + 1) if right_neighbor else "NONE",
                right_neighbor["surface"] if right_neighbor else "NONE",
            ),
            f"{micro_id} right boundary neighbor exact",
        )
        audit.check(row["minimal_convex_hull"] == "1", f"{micro_id} published minimality certificate")
        audit.check(row["edge_coverage_exact"] == "1", f"{micro_id} published exact-edge certificate")
        audit.check(row["final_result_status"] == "UNNAMED_NO_OUTGOING_EDGE", f"{micro_id} refuses an invented final result")
        audit.check(row["v69_word_delta"] == "0", f"{micro_id} zero word delta")
        audit.check(
            row["status"] == "EXACT_OCCURRENCE_MICRORECORD__NO_NEW_EDGE_OR_WORD",
            f"{micro_id} occurrence-bound status exact",
        )
        audit.check(not FORBIDDEN_MICRORECORD_RE.search(row["microrecord_de"]), f"{micro_id} published wording has no generic filler")

    # One exact coverage row per admitted edge.
    _, published_edges = read_tsv(EDGE_ARTIFACT, exact_fields=EDGE_FIELDS)
    published_edge_by_id = indexed(published_edges, ["edge_id"], "published edge coverage")
    audit.check(len(published_edges) == 9 and set(published_edge_by_id) == set(edge_by_id), "published edge coverage is exactly C001-C009")
    edge_to_micro = {
        edge_id: micro_id
        for micro_id, expected in EXPECTED_CORE.items()
        for edge_id in expected["edges"]
    }
    for edge_id in sorted(EXPECTED_EDGE_TIERS):
        row = published_edge_by_id[(edge_id,)]
        source = edge_by_id[(edge_id,)]
        micro_id = edge_to_micro[edge_id]
        expected = EXPECTED_CORE[micro_id]
        all_nodes = sorted(edge_nodes[edge_id])
        ordered_actions = expected["actions"]
        shared = []
        if micro_id == "M006":
            shared = [3]
        elif micro_id == "M007":
            shared = [4]
        audit.check(row["microrecord_id"] == micro_id and row["locus"] == expected["locus"], f"{edge_id} exact window owner")
        audit.check(row["support_tier"] == source["support_tier"] == EXPECTED_EDGE_TIERS[edge_id], f"{edge_id} support tier exact")
        audit.check(row["relation_class"] == source["relation_class"], f"{edge_id} relation class exact")
        audit.check(row["source_ordinals"] == join_or_none(str(value) for value in edge_sources[edge_id]), f"{edge_id} source ordinals exact")
        audit.check(row["reference_ordinals"] == join_or_none(str(value) for value in edge_references[edge_id]), f"{edge_id} reference ordinals exact")
        audit.check(row["target_action_ordinal"] == str(edge_target[edge_id]), f"{edge_id} target ordinal exact")
        audit.check(row["right_participant_ordinals"] == join_or_none(str(value) for value in edge_right[edge_id]), f"{edge_id} right participants exact")
        audit.check(row["node_ordinals"] == "|".join(map(str, all_nodes)), f"{edge_id} complete node set exact")
        audit.check(
            (row["window_start_ordinal"], row["window_end_ordinal"])
            == (str(expected["start"]), str(expected["end"])),
            f"{edge_id} exact minimal window bounds",
        )
        audit.check(row["operation_rank"] == str(ordered_actions.index(edge_target[edge_id]) + 1), f"{edge_id} operation rank exact")
        audit.check(row["topology"] == EXPECTED_PUBLISHED_TOPOLOGY[micro_id], f"{edge_id} topology family exact")
        audit.check(row["edge_role_in_window"] == EXPECTED_EDGE_ROLE[edge_id], f"{edge_id} exact graph role")
        audit.check(row["shared_node_ordinals"] == join_or_none(map(str, shared)), f"{edge_id} shared-node trace exact")
        audit.check(
            (row["source_join_exact"], row["reference_join_exact"], row["target_join_exact"], row["covered_once"], row["v68_word_delta"])
            == ("1", "1", "1", "1", "0"),
            f"{edge_id} exact joins, one coverage and zero delta",
        )
        audit.check(
            row["status"] == "V69_EDGE_USED_ONCE_IN_MINIMAL_V70_WINDOW",
            f"{edge_id} exact coverage status",
        )
        audit.check(
            not any(key[0] in "\t".join(row.values()) for key in rival_by_id),
            f"{edge_id} contains no held-rival identity",
        )

    audit.check(
        published_edge_by_id[("C004",)]["edge_role_in_window"]
        != published_edge_by_id[("C008",)]["edge_role_in_window"],
        "f80v.35 distinguishes first referenced add from working repeat",
    )
    audit.check(
        published_edge_by_id[("C007",)]["edge_role_in_window"]
        != published_edge_by_id[("C006",)]["edge_role_in_window"],
        "f86v6.25 distinguishes serial producer from serial consumer",
    )

    # The compact 19-token window deck is reconstructed position by position.
    _, published_window_tokens = read_tsv(WINDOW_TOKEN_ARTIFACT, exact_fields=WINDOW_TOKEN_FIELDS)
    published_window_by_key = indexed(published_window_tokens, ["locus", "token_ordinal"], "published window tokens")
    audit.check(len(published_window_tokens) == 19, "published window deck has exactly 19 token rows")
    audit.check(
        set(published_window_by_key) == {(locus, str(ordinal)) for locus, ordinal in window_positions},
        "published window deck contains exactly the seven convex hulls",
    )
    action_target_count = 0
    shared_count = 0
    bridge_count = 0
    preposed_output_count = 0
    for locus, ordinal in sorted(window_positions):
        micro_id = window_positions[(locus, ordinal)]
        expected = EXPECTED_CORE[micro_id]
        row = published_window_by_key[(locus, str(ordinal))]
        source = token_by_key[(locus, str(ordinal))]
        position = ordinal - expected["start"] + 1
        size = expected["end"] - expected["start"] + 1
        sources_here = expected_source_edges[(locus, ordinal)]
        references_here = expected_reference_edges[(locus, ordinal)]
        targets_here = expected_target_edges[(locus, ordinal)]
        right_here = expected_right_edges[(locus, ordinal)]
        edges_here = expected_window_edges[(locus, ordinal)]
        is_shared = len(edges_here) > 1
        is_bridge = bool(sources_here and targets_here and any(
            source_roles[(locus, ordinal)][index].startswith("DONOR_ACTION_OUTPUT:")
            for index in range(len(source_roles[(locus, ordinal)]))
        ))
        audit.check(
            (row["page"], row["locus"], row["token_ordinal"], row["surface"], row["v69_token_gloss_de"])
            == (source["page"], locus, str(ordinal), source["surface"], source["v69_token_gloss_de"]),
            f"window token {locus}#{ordinal} frozen identity",
        )
        audit.check(row["microrecord_id"] == micro_id, f"window token {locus}#{ordinal} owner exact")
        audit.check((row["window_position"], row["window_size"]) == (str(position), str(size)), f"window token {locus}#{ordinal} position exact")
        audit.check(row["role_trace"] == expected_window_roles[(locus, ordinal)], f"window token {locus}#{ordinal} role exact")
        audit.check(row["edge_ids"] == join_or_none(edges_here), f"window token {locus}#{ordinal} edge IDs exact")
        audit.check(row["source_edge_ids"] == join_or_none(sources_here), f"window token {locus}#{ordinal} source IDs exact")
        audit.check(row["reference_edge_ids"] == join_or_none(references_here), f"window token {locus}#{ordinal} reference IDs exact")
        audit.check(row["target_edge_ids"] == join_or_none(targets_here), f"window token {locus}#{ordinal} target IDs exact")
        audit.check(row["right_participant_edge_ids"] == join_or_none(right_here), f"window token {locus}#{ordinal} right IDs exact")
        audit.check(row["is_action_target"] == str(int(bool(targets_here))), f"window token {locus}#{ordinal} action flag exact")
        audit.check(row["is_shared_node"] == str(int(is_shared)), f"window token {locus}#{ordinal} shared-node flag exact")
        audit.check(row["is_action_output_bridge"] == str(int(is_bridge)), f"window token {locus}#{ordinal} bridge flag exact")
        audit.check(row["is_window_start"] == str(int(ordinal == expected["start"])), f"window token {locus}#{ordinal} start flag exact")
        audit.check(row["is_window_end"] == str(int(ordinal == expected["end"])), f"window token {locus}#{ordinal} end flag exact")
        audit.check((row["v68_clause_id"], row["v68_clause_type"]) == (source["v68_clause_id"], source["v68_clause_type"]), f"window token {locus}#{ordinal} clause exact")
        audit.check(row["v70_microrecord_de"] == expected["microrecord"], f"window token {locus}#{ordinal} exact microrecord text")
        audit.check(
            row["v69_word_delta"] == "0"
            and row["status"] == "V69_TOKEN_AND_GLOSS_FROZEN__V70_WINDOW_ROLE_ONLY",
            f"window token {locus}#{ordinal} zero delta and exact status",
        )
        action_target_count += int(bool(targets_here))
        shared_count += int(is_shared)
        bridge_count += int(is_bridge)
        preposed_output_count += int("OUTPUT_LABEL:C007" in row["role_trace"])
    audit.check(action_target_count == 9, "19-token deck contains nine unique action targets")
    audit.check(shared_count == 2, "19-token deck has exactly two cross-edge shared nodes")
    audit.check(bridge_count == 1, "19-token deck has exactly one action-output bridge")
    audit.check(preposed_output_count == 1, "19-token deck has exactly one preposed output label")

    # Complete V69 freeze projections: 479 tokens, 51 lines and three spans.
    published_token_fields, published_tokens = read_tsv(
        TOKEN_ARTIFACT, exact_fields=[*token_fields, *TOKEN_EXTRA_FIELDS]
    )
    published_line_fields, published_lines = read_tsv(
        LINE_ARTIFACT, exact_fields=[*line_fields, *LINE_EXTRA_FIELDS]
    )
    published_span_fields, published_spans = read_tsv(
        SPAN_ARTIFACT, exact_fields=[*span_fields, *SPAN_EXTRA_FIELDS]
    )
    assert_projection(audit, token_fields, tokens, published_token_fields, published_tokens, "479-token V70 freeze")
    assert_projection(audit, line_fields, lines, published_line_fields, published_lines, "51-line V70 freeze")
    assert_projection(audit, span_fields, spans, published_span_fields, published_spans, "three-span V70 freeze")
    audit.check(no_forbidden_locus([*published_tokens, *published_lines, *published_spans]), "all complete V70 projections exclude f84/f84r")

    inside_token_rows = 0
    for source, row in zip(tokens, published_tokens):
        locus = source["locus"]
        ordinal = integer(source["token_ordinal"], f"token {locus}")
        micro_id = window_positions.get((locus, ordinal))
        if micro_id:
            expected = EXPECTED_CORE[micro_id]
            expected_extra = (
                micro_id,
                expected_window_roles[(locus, ordinal)],
                str(ordinal - expected["start"] + 1),
                str(expected["end"] - expected["start"] + 1),
                expected["microrecord"],
                source["v69_token_gloss_de"],
                "0",
            )
            inside_token_rows += 1
        else:
            expected_extra = (
                "NONE",
                "NONE",
                "NONE",
                "NONE",
                "NONE",
                source["v69_token_gloss_de"],
                "0",
            )
        audit.check(
            tuple(row[field] for field in TOKEN_EXTRA_FIELDS[:-1]) == expected_extra,
            f"complete token freeze exact {locus}#{ordinal}",
        )
        audit.check(
            row["v70_status"] == "V69_TOKEN_GLOSS_BYTE_IDENTICAL__SEPARATE_WINDOW_METADATA",
            f"complete token status exact {locus}#{ordinal}",
        )
    audit.check(inside_token_rows == 19, "complete 479-token freeze marks exactly 19 window positions")
    audit.check(
        all(row["v70_token_gloss_de"] == source["v69_token_gloss_de"] for source, row in zip(tokens, published_tokens)),
        "479/479 V70 token glosses are byte-identical to V69",
    )

    affected_lines = 0
    for source, row in zip(lines, published_lines):
        local = [spec for spec in specs if spec["locus"] == source["locus"]]
        if local:
            spec = local[0]
            micro_id = spec["microrecord_id"]
            expected = EXPECTED_CORE[micro_id]
            expected_extra = (
                micro_id,
                expected["microrecord"],
                f"{expected['start']}-{expected['end']}",
                EXPECTED_PUBLISHED_TOPOLOGY[micro_id],
                EXPECTED_SUPPORT_PROFILE[micro_id],
                "1" if micro_id == "M007" else "0",
                "0",
                source["v69_clause_translation_de"],
                "0",
            )
            affected_lines += 1
        else:
            expected_extra = (
                "NONE",
                "NONE",
                "NONE",
                "NONE",
                "NONE",
                "0",
                "0",
                source["v69_clause_translation_de"],
                "0",
            )
        audit.check(
            tuple(row[field] for field in LINE_EXTRA_FIELDS[:-1]) == expected_extra,
            f"complete line overlay exact {source['locus']}",
        )
        audit.check(
            row["v70_status"]
            == (
                "V69_LINE_BYTE_IDENTICAL__SEPARATE_EXACT_MICRORECORD"
                if local
                else "V69_LINE_BYTE_IDENTICAL__NO_MICRORECORD"
            ),
            f"complete line status exact {source['locus']}",
        )
    audit.check(affected_lines == 7, "complete 51-line overlay marks exactly seven loci")
    audit.check(
        all(row["v70_clause_translation_de"] == source["v69_clause_translation_de"] for source, row in zip(lines, published_lines)),
        "51/51 line translations are byte-identical to V69",
    )
    audit.check(
        sum(integer(row["v70_named_intermediate_output_count"], row["locus"]) for row in published_lines if row["v70_named_intermediate_output_count"] != "0") == 1,
        "line overlay has one named intermediate output",
    )
    audit.check(
        all(row["v70_named_final_result_count"] == "0" for row in published_lines),
        "line overlay invents zero named final results",
    )

    for source, row in zip(spans, published_spans):
        audit.check(
            tuple(row[field] for field in SPAN_EXTRA_FIELDS[:-1])
            == (source["v69_selected_gloss_de"], "1", "NONE"),
            f"bound span remains exact and outside windows {source['span_id']}",
        )
        audit.check(row["v70_status"] == "V69_BOUND_SPAN_BYTE_IDENTICAL", f"bound span status exact {source['span_id']}")

    # Census rows must be internally exact and expose every topology and tier.
    _, census = read_tsv(CENSUS_ARTIFACT, exact_fields=CENSUS_FIELDS)
    indexed(census, ["dimension", "value"], "topology census")
    audit.check(len(census) == 14, "topology census has the exact fourteen declared rows")
    audit.check(
        Counter(row["dimension"] for row in census)
        == Counter(
            {
                "TOPOLOGY": 3,
                "SUPPORT_PROFILE": 4,
                "EDGE_SUPPORT_TIER": 3,
                "RESULT_STATUS": 2,
                "BOUNDARY": 2,
            }
        ),
        "topology census dimensions are complete and closed",
    )
    for row in census:
        members = id_list(row["member_ids"])
        audit.check(row["count"] == str(len(members)), f"census count exact {row['dimension']}/{row['value']}")
        audit.check(bool(row["note"]), f"census note present {row['dimension']}/{row['value']}")
    required_census = {
        "SINGLE_EDGE": {"M001", "M002", "M003", "M004", "M005"},
        "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT": {"M006"},
        "SERIAL_ACTION_OUTPUT_CHAIN": {"M007"},
        "A_ONLY": {"M002", "M003", "M004", "M005"},
        "A_PLUS_B": {"M006"},
        "A_MINUS_PLUS_B": {"M007"},
        "B_ONLY": {"M001"},
        "A_STRONG_LICENSED": {"C001", "C002", "C003", "C004", "C005"},
        "A_MINUS_EXPLICIT_OUTPUT": {"C006"},
        "B_WORKING_LOCAL": {"C007", "C008", "C009"},
        "NAMED_INTERMEDIATE_OUTPUT": {"M007"},
        "NAMED_FINAL_RESULT": set(),
        "CLAUSE_ALIGNED_START": {"M007"},
        "TARGET_CLAUSE_ALIGNED_END": set(EXPECTED_CORE),
    }
    for value, members in required_census.items():
        matches = [row for row in census if row["value"] == value]
        audit.check(len(matches) == 1, f"census has one {value} row")
        audit.check(set(id_list(matches[0]["member_ids"])) == members, f"census {value} membership exact")

    # RESULT, reader, report and manifest make the compact release auditable.
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result.get("status") == STATUS, "RESULT status exact")
    audit.check(set(result.get("files", {})) == EXPECTED_GENERATED, "RESULT enumerates the exact compact artifact set")
    for name, digest in result["files"].items():
        path = ART / name
        audit.check(path.is_file(), f"RESULT artifact exists {name}")
        audit.check(sha256(path) == digest, f"RESULT artifact hash exact {name}")
    required_inputs = {
        str(SPEC.relative_to(ROOT)): sha256(SPEC),
        str((G696 / "RESULT.json").relative_to(ROOT)): sha256(G696 / "RESULT.json"),
        str(EDGE_SOURCE.relative_to(ROOT)): sha256(EDGE_SOURCE),
        str(TOKEN_SOURCE.relative_to(ROOT)): sha256(TOKEN_SOURCE),
        str(LINE_SOURCE.relative_to(ROOT)): sha256(LINE_SOURCE),
        str(SPAN_SOURCE.relative_to(ROOT)): sha256(SPAN_SOURCE),
        str(REFERENCE_SOURCE.relative_to(ROOT)): sha256(REFERENCE_SOURCE),
        str(RIVAL_SOURCE.relative_to(ROOT)): sha256(RIVAL_SOURCE),
    }
    audit.check(isinstance(result.get("inputs"), dict), "RESULT publishes an input hash map")
    audit.check(
        all(result["inputs"].get(path) == digest for path, digest in required_inputs.items()),
        "RESULT seals every material V70/GDT696 input",
    )
    audit.check(
        all(not Path(path).is_absolute() and "f84" not in path.lower() for path in result["inputs"]),
        "RESULT input paths are relative and exclude f84/f84r",
    )

    audit.check(
        result.get("basis")
        == {
            "bound_spans": 3,
            "f84_access": 0,
            "f84r_access": 0,
            "lines": 51,
            "new_pages": 0,
            "pages": 36,
            "token_positions": 479,
            "v69_admitted_edges": 9,
            "v69_held_rivals": 17,
            "v69_reference_positions": 27,
        },
        "RESULT fixed basis and forbidden-access counts exact",
    )
    audit.check(
        result.get("composition")
        == {
            "action_output_bridges": 1,
            "action_target_positions": 9,
            "adjacency_derived_edges": 0,
            "affected_loci": 7,
            "common_destination_fanouts": 1,
            "distinct_v68_clauses_touched": 16,
            "edges_covered_exactly_once": 9,
            "final_target_outgoing_carries": 0,
            "generic_nearest_donor_rules": 0,
            "held_rival_targets_inside_windows": 0,
            "microrecords": 7,
            "multi_edge_microrecords": 2,
            "named_final_results": 0,
            "named_intermediate_outputs": 1,
            "preposed_output_label_nodes": 1,
            "summed_per_edge_convex_hull_positions": 23,
            "window_token_positions": 19,
            "written_reference_positions": 6,
        },
        "RESULT complete 7/19/9 composition and zero-invention counts exact",
    )
    audit.check(
        result.get("topologies")
        == {
            "ORDERED_REPEATED_COMMON_DESTINATION_FANOUT": 1,
            "SERIAL_ACTION_OUTPUT_CHAIN": 1,
            "SINGLE_EDGE": 5,
        },
        "RESULT five single, one fanout and one serial topology exact",
    )
    audit.check(
        result.get("support_profiles")
        == {"A_MINUS_PLUS_B": 1, "A_ONLY": 4, "A_PLUS_B": 1, "B_ONLY": 1},
        "RESULT support-profile census exact",
    )
    audit.check(
        result.get("edge_support_tiers")
        == {"A_MINUS_EXPLICIT_OUTPUT": 1, "A_STRONG_LICENSED": 5, "B_WORKING_LOCAL": 3},
        "RESULT five strong, one A-minus and three working edge tiers exact",
    )
    audit.check(
        result.get("freeze")
        == {
            "bound_spans_byte_identical": 3,
            "changed_word_meanings": 0,
            "content_word_additions": 0,
            "content_word_deletions": 0,
            "content_word_reorders": 0,
            "line_translations_byte_identical": 51,
            "new_word_meanings": 0,
            "token_glosses_byte_identical": 479,
        },
        "RESULT complete 479/51/3 zero-word-delta freeze exact",
    )
    audit.check(
        result.get("boundaries")
        == {
            "clause_aligned_window_starts": 1,
            "nominal_tail_window_starts": 6,
            "target_clause_aligned_window_ends": 7,
        },
        "RESULT boundary census exact",
    )

    reader = READER_ARTIFACT.read_text(encoding="utf-8")
    audit.check(STATUS in reader, "human reader prints the exact status")
    for spec in specs:
        micro_id = spec["microrecord_id"]
        audit.check(micro_id in reader and spec["locus"] in reader, f"reader identifies {micro_id} and its locus")
        audit.check(spec["microrecord_de"] in reader, f"reader prints exact text for {micro_id}")
        audit.check(spec["boundary_note_de"] in reader, f"reader prints the unresolved boundary for {micro_id}")
        audit.check(spec["forbidden_inference"] in reader, f"reader prints the anti-smuggling warning for {micro_id}")
        for edge_id in id_list(spec["edge_ids"]):
            audit.check(edge_id in reader, f"reader exposes edge {edge_id}")
    audit.check(
        all(
            profile in reader
            for profile in ("A_ONLY", "A_PLUS_B", "A_MINUS_PLUS_B", "B_ONLY")
        ),
        "reader keeps strong, A-minus and working support profiles visible",
    )
    audit.check(
        "19" in reader and "479" in reader and "51" in reader and "3" in reader,
        "reader reports compact-window and complete-freeze coverage",
    )
    for line in lines:
        audit.check(
            f"`{line['locus']}`" in reader
            and line["v69_clause_translation_de"] in reader,
            f"reader carries the complete unchanged V69 line {line['locus']}",
        )
    audit.check(not re.search(r"\bf84r?\b", reader, re.IGNORECASE), "reader does not expose forbidden folio material")

    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    artifact_readme = (ART / "README.md").read_text(encoding="utf-8")
    audit.check(STATUS in report, "REPORT publishes exact result status")
    audit.check(
        all(name in artifact_readme for name in EXPECTED_GENERATED - {"README.md"}),
        "artifact README maps every generated artifact",
    )
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    audit.check(
        manifest.get("experiment_id") == "GDT697"
        and manifest.get("slug") == "v69_exact_relation_microrecords",
        "manifest experiment identity exact",
    )
    audit.check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest forbids f84/f84r")
    audit.check(manifest.get("status") == STATUS, "manifest status matches RESULT")
    audit.check(
        bool(result.get("claim_ceiling"))
        and manifest.get("claim_ceiling") == result.get("claim_ceiling"),
        "manifest and RESULT share a nonempty claim ceiling",
    )

    payload = {
        "status": "PASS",
        "checks": len(audit.checks),
        "failed": 0,
        "summary": {
            "microrecords": 7,
            "affected_loci": 7,
            "window_token_positions": 19,
            "admitted_edges_covered_once": 9,
            "single_edge_windows": 5,
            "multi_edge_windows": 2,
            "shared_destination_repeats": 1,
            "serial_action_output_chains": 1,
            "distinct_v68_clauses": 16,
            "action_targets": 9,
            "written_reference_positions": 6,
            "action_output_bridges": 1,
            "common_destination_nodes": 1,
            "preposed_output_labels": 1,
            "final_outgoing_carries": 0,
            "tokens_frozen": 479,
            "lines_frozen": 51,
            "spans_frozen": 3,
            "new_word_meanings": 0,
            "changed_word_meanings": 0,
        },
        "audit": audit.checks,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
