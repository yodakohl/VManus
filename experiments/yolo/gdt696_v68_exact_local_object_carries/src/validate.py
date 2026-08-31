#!/usr/bin/env python3
"""Independent, fail-closed validation for GDT696.

The validator intentionally does not import the renderer.  It reconstructs
every admitted and held relation from the frozen GDT695 tables and checks the
published GDT696 tables as a separate projection of those inputs.
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
EXP = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries"
SRC = EXP / "src"
ART = EXP / "artifacts"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization/artifacts"
G676 = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer"

STATUS = (
    "PASS_V69_6_STRONG_PLUS_3_WORKING_LOCAL_EDGES__"
    "27_REFERENCE_CENSUS__17_RIVALS_HELD__ZERO_WORD_DELTA"
)

EDGE_SOURCE = SRC / "V69_LOCAL_ACTION_EDGES.tsv"
REFERENCE_SOURCE = SRC / "V69_REFERENCE_DECISIONS.tsv"
RIVAL_SOURCE = SRC / "V69_RELATION_RIVALS.tsv"

EDGE_ARTIFACT = ART / "V69_9_LOCAL_ACTION_EDGES.tsv"
REFERENCE_ARTIFACT = ART / "V69_27_REFERENCE_CENSUS.tsv"
RIVAL_ARTIFACT = ART / "V69_17_RELATION_RIVALS.tsv"
TOKEN_ARTIFACT = ART / "V69_479_TOKEN_RELATION_OVERLAY.tsv"
LINE_ARTIFACT = ART / "V69_51_LINE_RELATION_OVERLAY.tsv"
SPAN_ARTIFACT = ART / "V69_3_BOUND_SPAN_FREEZE.tsv"
CLASS_ARTIFACT = ART / "V69_RELATION_CLASS_CENSUS.tsv"
READER_ARTIFACT = ART / "GDT696_V69_LOCAL_OBJECT_CARRY_READER.md"

EXPECTED_GENERATED = {
    "GDT696_V69_LOCAL_OBJECT_CARRY_READER.md",
    "README.md",
    "V69_17_RELATION_RIVALS.tsv",
    "V69_27_REFERENCE_CENSUS.tsv",
    "V69_3_BOUND_SPAN_FREEZE.tsv",
    "V69_479_TOKEN_RELATION_OVERLAY.tsv",
    "V69_51_LINE_RELATION_OVERLAY.tsv",
    "V69_9_LOCAL_ACTION_EDGES.tsv",
    "V69_RELATION_CLASS_CENSUS.tsv",
}

EDGE_FIELDS = [
    "edge_id",
    "locus",
    "source_start_ordinal",
    "source_end_ordinal",
    "left_role_map",
    "reference_ordinal",
    "target_action_ordinal",
    "right_participant_ordinals",
    "relation_class",
    "support_tier",
    "expected_source_surfaces",
    "expected_reference_surface",
    "expected_target_surface",
    "expected_source_glosses_de",
    "expected_reference_gloss_de",
    "expected_target_gloss_de",
    "relation_explicit_de",
    "license_basis",
    "rival_control",
]
REFERENCE_FIELDS = [
    "reference_id",
    "locus",
    "reference_ordinal",
    "expected_surface",
    "expected_gloss_de",
    "decision",
    "linked_edge_ids",
    "source_ordinals",
    "target_ordinals",
    "scope_class",
    "provenance",
    "note",
]
RIVAL_FIELDS = [
    "rival_id",
    "rival_kind",
    "locus",
    "source_ordinals",
    "target_action_ordinal",
    "expected_source_surfaces",
    "expected_target_surface",
    "plausible_reading_de",
    "rejection_reason",
]

# The closed deck is deliberately occurrence-bound.  Hard-coding its topology
# prevents a modified source TSV from silently defining a different experiment.
EXPECTED_EDGE_CORE = {
    "C001": ("f105v.1", 3, 3, 4, 4, "WRITTEN_MATERIAL_OBJECT", "A_STRONG_LICENSED"),
    "C002": ("f113v.17", 6, 6, 7, 7, "PORTION_SUBSET_CARRY", "A_STRONG_LICENSED"),
    "C003": ("f75r.3", 3, 3, 4, 4, "EXPLICIT_PRECEDING_PORTION", "A_STRONG_LICENSED"),
    "C004": ("f80v.35", 3, 3, 4, 5, "WRITTEN_DESTINATION_REFERENCE", "A_STRONG_LICENSED"),
    "C005": ("f77r.38", 5, 5, None, 6, "LEFT_WRITTEN_OBJECT", "A_STRONG_LICENSED"),
    "C006": ("f86v6.25", 4, 4, 5, 5, "MEASURED_SHARE_OUTPUT_CARRY", "A_MINUS_EXPLICIT_OUTPUT"),
    "C007": ("f86v6.25", 2, 3, None, 4, "OUTPUT_LABEL_PLUS_SOURCE_TO_MEASURE", "B_WORKING_LOCAL"),
    "C008": ("f80v.35", 3, 3, None, 6, "REPEATED_QOL_DESTINATION_CARRY", "B_WORKING_LOCAL"),
    "C009": ("f104v.2", 4, 5, 5, 6, "MEASURE_SUBSET_CARRY", "B_WORKING_LOCAL"),
}

EXPECTED_LEFT_ROLE_MAPS = {
    "C001": {3: "DONOR_MATERIAL"},
    "C002": {6: "DONOR_PORTION_POOL"},
    "C003": {3: "DONOR_PRECEDING_PORTION"},
    "C004": {3: "DESTINATION"},
    "C005": {5: "ADDED_OBJECT"},
    "C006": {4: "DONOR_ACTION_OUTPUT"},
    "C007": {2: "OUTPUT_LABEL", 3: "DONOR_SOURCE_SHARE"},
    "C008": {3: "DESTINATION"},
    "C009": {4: "PREPARATION_HEAD", 5: "DONOR_MEASURE_POOL"},
}

EXPECTED_REFERENCE_DECISIONS = {
    "R001": "UNRESOLVED_LINE_INITIAL",
    "R002": "ADMITTED_WORKING_EDGE",
    "R003": "STRUCTURAL_SEQUENCE_ONLY",
    "R004": "ADMITTED_STRONG_EDGE",
    "R005": "HOLD_OBJECT_RIVAL",
    "R006": "PROCESS_SCOPE_ONLY",
    "R007": "ADMITTED_STRONG_EDGE",
    "R008": "UNRESOLVED_LINE_INITIAL",
    "R009": "STRUCTURAL_SEQUENCE_ONLY",
    "R010": "UNRESOLVED_LOCAL_RIVAL",
    "R011": "UNRESOLVED_LOCAL_RIVAL",
    "R012": "HOLD_OBJECT_RIVAL",
    "R013": "HOLD_OBJECT_RIVAL",
    "R014": "UNRESOLVED_LINE_INITIAL",
    "R015": "ADMITTED_STRONG_EDGE",
    "R016": "HOLD_OBJECT_RIVAL",
    "R017": "HOLD_OBJECT_RIVAL",
    "R018": "ADMITTED_STRONG_EDGE",
    "R019": "STRUCTURAL_SEQUENCE_ONLY",
    "R020": "HOLD_OBJECT_RIVAL",
    "R021": "HOLD_OBJECT_RIVAL",
    "R022": "UNRESOLVED_LINE_INITIAL",
    "R023": "UNRESOLVED_LINE_INITIAL",
    "R024": "ADMITTED_STRONG_EDGE",
    "R025": "SELF_CONTAINED_INTRATOKEN",
    "R026": "INHERITED_NOMINAL_BINDING",
    "R027": "EXACT_NOMINAL_REFERENCE",
}

EXPECTED_REFERENCE_CENSUS = Counter(
    {
        "ADMITTED_STRONG_EDGE": 5,
        "ADMITTED_WORKING_EDGE": 1,
        "HOLD_OBJECT_RIVAL": 7,
        "UNRESOLVED_LINE_INITIAL": 5,
        "UNRESOLVED_LOCAL_RIVAL": 2,
        "STRUCTURAL_SEQUENCE_ONLY": 3,
        "PROCESS_SCOPE_ONLY": 1,
        "SELF_CONTAINED_INTRATOKEN": 1,
        "INHERITED_NOMINAL_BINDING": 1,
        "EXACT_NOMINAL_REFERENCE": 1,
    }
)

REFERENCE_RE = re.compile(
    r"\b(?:hiervon|hieraus|hierzu|hieran|vorstehende\w*|davon|dieses)\b",
    re.IGNORECASE,
)
FORBIDDEN_LOCUS_RE = re.compile(r"^f84(?:r|v)?(?:\b|\.)", re.IGNORECASE)


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


def integer(text: str, context: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]*", text):
        raise AssertionError(f"invalid positive ordinal {text!r}: {context}")
    return int(text)


def ordinal_spec(text: str, context: str) -> list[int]:
    """Expand a source/reference specification without guessing direction."""

    if text == "NONE":
        return []
    values: list[int] = []
    for component in text.split("|"):
        if re.fullmatch(r"[1-9][0-9]*", component):
            values.append(int(component))
            continue
        match = re.fullmatch(r"([1-9][0-9]*)-([1-9][0-9]*)", component)
        if not match:
            raise AssertionError(f"invalid ordinal specification {text!r}: {context}")
        start, end = map(int, match.groups())
        if end < start:
            raise AssertionError(f"descending ordinal range {text!r}: {context}")
        values.extend(range(start, end + 1))
    if len(values) != len(set(values)):
        raise AssertionError(f"duplicate ordinal in {text!r}: {context}")
    return values


def role_map(text: str, context: str) -> dict[int, str]:
    roles: dict[int, str] = {}
    if not text:
        raise AssertionError(f"empty left-role map: {context}")
    for item in text.split("|"):
        match = re.fullmatch(r"([1-9][0-9]*):([A-Z][A-Z_]*)", item)
        if not match:
            raise AssertionError(f"invalid left-role map item {item!r}: {context}")
        ordinal, role = int(match.group(1)), match.group(2)
        if ordinal in roles:
            raise AssertionError(f"duplicate left-role ordinal {ordinal}: {context}")
        roles[ordinal] = role
    return roles


def split_parallel(text: str, separator: str, expected: int, context: str) -> list[str]:
    values = text.split(separator)
    if len(values) != expected or any(value == "" for value in values):
        raise AssertionError(f"parallel field length mismatch: {context}")
    return values


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


def assert_projection(
    audit: Audit,
    inherited_fields: Sequence[str],
    inherited_rows: Sequence[Mapping[str, str]],
    overlay_fields: Sequence[str],
    overlay_rows: Sequence[Mapping[str, str]],
    name: str,
) -> None:
    audit.check(all(field in overlay_fields for field in inherited_fields), f"{name} carries every inherited column")
    audit.check(len(inherited_rows) == len(overlay_rows), f"{name} row count")
    audit.check(
        all(
            tuple(overlay[field] for field in inherited_fields)
            == tuple(source[field] for field in inherited_fields)
            for source, overlay in zip(inherited_rows, overlay_rows)
        ),
        f"{name} inherited projection byte-exact",
    )


def assert_source_projection(
    audit: Audit,
    fields: Sequence[str],
    source: Sequence[Mapping[str, str]],
    published_fields: Sequence[str],
    published: Sequence[Mapping[str, str]],
    name: str,
) -> None:
    audit.check(all(field in published_fields for field in fields), f"{name} carries complete source contract")
    audit.check(len(source) == len(published), f"{name} row count")
    audit.check(
        [tuple(row[field] for field in fields) for row in published]
        == [tuple(row[field] for field in fields) for row in source],
        f"{name} source projection exact and ordered",
    )


def values_for_key(payload: object, key: str) -> list[object]:
    found: list[object] = []
    if isinstance(payload, dict):
        for current_key, value in payload.items():
            if current_key == key:
                found.append(value)
            found.extend(values_for_key(value, key))
    elif isinstance(payload, list):
        for value in payload:
            found.extend(values_for_key(value, key))
    return found


def no_forbidden_locus(rows: Iterable[Mapping[str, str]]) -> bool:
    for row in rows:
        for field in ("page", "locus"):
            value = row.get(field, "")
            if value and FORBIDDEN_LOCUS_RE.match(value):
                return False
    return True


def main() -> int:
    audit = Audit()

    edge_fields, edge_specs = read_tsv(EDGE_SOURCE, exact_fields=EDGE_FIELDS)
    reference_fields, reference_specs = read_tsv(REFERENCE_SOURCE, exact_fields=REFERENCE_FIELDS)
    rival_fields, rival_specs = read_tsv(RIVAL_SOURCE, exact_fields=RIVAL_FIELDS)

    token_fields, tokens = read_tsv(G695 / "V68_479_TOKEN_FREEZE.tsv")
    line_fields, lines = read_tsv(G695 / "V68_51_LINE_CLAUSE_READER.tsv")
    span_fields, spans = read_tsv(G695 / "V68_3_BOUND_SPAN_FREEZE.tsv")
    _, clauses = read_tsv(G695 / "V68_175_CLAUSE_REALIZATIONS.tsv")
    token_by_key = indexed(tokens, ["locus", "token_ordinal"], "GDT695 tokens")

    audit.check(len(tokens) == 479, "GDT695 has 479 frozen token rows")
    audit.check(len(lines) == 51, "GDT695 has 51 frozen line rows")
    audit.check(len(spans) == 3, "GDT695 has three frozen span rows")
    audit.check(no_forbidden_locus([*tokens, *lines, *spans]), "GDT695 projection excludes f84/f84r")
    audit.check(no_forbidden_locus([*edge_specs, *reference_specs, *rival_specs]), "all GDT696 source decks exclude f84/f84r")

    clauses_by_position: dict[tuple[str, int], list[Mapping[str, str]]] = defaultdict(list)
    for clause in clauses:
        start = integer(clause["start_ordinal"], f"clause {clause['locus']}")
        end = integer(clause["end_ordinal"], f"clause {clause['locus']}")
        for ordinal in range(start, end + 1):
            clauses_by_position[(clause["locus"], ordinal)].append(clause)

    # Independently join all nine source, reference and target positions to V68.
    audit.check(len(edge_specs) == 9, "exactly nine admitted edge specifications")
    edge_by_id = indexed(edge_specs, ["edge_id"], "edge source")
    audit.check(set(key[0] for key in edge_by_id) == set(EXPECTED_EDGE_CORE), "closed C001-C009 edge identity")
    for edge_id, expected in EXPECTED_EDGE_CORE.items():
        row = edge_by_id[(edge_id,)]
        reference = None if row["reference_ordinal"] == "NONE" else integer(row["reference_ordinal"], edge_id)
        observed = (
            row["locus"],
            integer(row["source_start_ordinal"], edge_id),
            integer(row["source_end_ordinal"], edge_id),
            reference,
            integer(row["target_action_ordinal"], edge_id),
            row["relation_class"],
            row["support_tier"],
        )
        audit.check(observed == expected, f"{edge_id} closed topology and tier")
        source_ordinals = list(range(observed[1], observed[2] + 1))
        left_roles = role_map(row["left_role_map"], edge_id)
        audit.check(
            list(left_roles) == source_ordinals,
            f"{edge_id} left-role map covers its exact source span in order",
        )
        audit.check(
            left_roles == EXPECTED_LEFT_ROLE_MAPS[edge_id],
            f"{edge_id} left participant roles exact",
        )
        source_rows = [token_by_key.get((row["locus"], str(ordinal))) for ordinal in source_ordinals]
        audit.check(all(source_rows), f"{edge_id} source ordinals exist")
        source_rows = [source for source in source_rows if source is not None]
        audit.check(
            [source["surface"] for source in source_rows]
            == split_parallel(row["expected_source_surfaces"], "|", len(source_rows), f"{edge_id} source surfaces"),
            f"{edge_id} source surfaces join exactly",
        )
        audit.check(
            [source["v68_token_gloss_de"] for source in source_rows]
            == split_parallel(row["expected_source_glosses_de"], " || ", len(source_rows), f"{edge_id} source glosses"),
            f"{edge_id} source glosses join exactly",
        )
        target_key = row["locus"], row["target_action_ordinal"]
        target_clause_key = row["locus"], observed[4]
        target = token_by_key.get(target_key)
        audit.check(target is not None, f"{edge_id} target ordinal exists")
        assert target is not None
        audit.check(target["surface"] == row["expected_target_surface"], f"{edge_id} target surface joins exactly")
        audit.check(target["v68_token_gloss_de"] == row["expected_target_gloss_de"], f"{edge_id} target gloss joins exactly")
        audit.check(
            target["v68_clause_type"] == "ACTION_CLAUSE"
            and target["v68_action_license"] == "GDT689_V62_ACTION_ORDINAL",
            f"{edge_id} target is a licensed written action",
        )
        target_clauses = clauses_by_position[target_clause_key]
        audit.check(len(target_clauses) == 1, f"{edge_id} target belongs to one V68 clause")
        audit.check(target_clauses[0]["clause_type"] == "ACTION_CLAUSE", f"{edge_id} target clause type")
        audit.check(
            ordinal_spec(target_clauses[0]["action_ordinals"], f"{edge_id} action clause")
            == [observed[4]],
            f"{edge_id} target clause has exactly its written action ordinal",
        )
        if reference is None:
            audit.check(
                row["expected_reference_surface"] == row["expected_reference_gloss_de"] == "NONE",
                f"{edge_id} has no invented reference card",
            )
        else:
            reference_token = token_by_key.get((row["locus"], str(reference)))
            audit.check(reference_token is not None, f"{edge_id} reference ordinal exists")
            assert reference_token is not None
            audit.check(reference_token["surface"] == row["expected_reference_surface"], f"{edge_id} reference surface joins exactly")
            audit.check(reference_token["v68_token_gloss_de"] == row["expected_reference_gloss_de"], f"{edge_id} reference gloss joins exactly")
        audit.check(row["right_participant_ordinals"] == "NONE", f"{edge_id} has no hidden right participant")

    audit.check(
        Counter(row["support_tier"] for row in edge_specs)
        == Counter({"A_STRONG_LICENSED": 5, "A_MINUS_EXPLICIT_OUTPUT": 1, "B_WORKING_LOCAL": 3}),
        "edge tier census is exactly 5 strong plus 1 A-minus plus 3 working",
    )
    audit.check(
        len({(row["locus"], row["target_action_ordinal"]) for row in edge_specs}) == 9,
        "nine admitted edges have nine exact target occurrences",
    )

    # Find every written reference expression directly in the frozen glosses.
    found_reference_positions = {
        (row["locus"], row["token_ordinal"])
        for row in tokens
        if REFERENCE_RE.search(row["v68_token_gloss_de"])
    }
    audit.check(len(found_reference_positions) == 27, "independent V68 scan finds exactly 27 reference-bearing positions")
    audit.check(len(reference_specs) == 27, "source deck contains exactly 27 reference decisions")
    reference_by_id = indexed(reference_specs, ["reference_id"], "reference decisions")
    reference_by_position = indexed(reference_specs, ["locus", "reference_ordinal"], "reference positions")
    audit.check(
        {key[0] for key in reference_by_id} == set(EXPECTED_REFERENCE_DECISIONS),
        "closed R001-R027 reference identity",
    )
    audit.check(
        {key: row["decision"] for key, row in reference_by_id.items()}
        == {(reference_id,): decision for reference_id, decision in EXPECTED_REFERENCE_DECISIONS.items()},
        "all 27 reference decisions retain their fixed categories",
    )
    audit.check(
        set(reference_by_position) == found_reference_positions,
        "reference census equals independent V68 lexical scan",
    )
    audit.check(
        Counter(row["decision"] for row in reference_specs) == EXPECTED_REFERENCE_CENSUS,
        "reference decision-category census 5/1/7/5/2/3/1/1/1 exact",
    )
    linked_reference_edges: set[str] = set()
    for row in reference_specs:
        key = row["locus"], row["reference_ordinal"]
        token = token_by_key[key]
        audit.check(token["surface"] == row["expected_surface"], f"{row['reference_id']} surface joins V68")
        audit.check(token["v68_token_gloss_de"] == row["expected_gloss_de"], f"{row['reference_id']} gloss joins V68")
        source_ordinals = ordinal_spec(row["source_ordinals"], f"{row['reference_id']} source")
        target_ordinals = ordinal_spec(row["target_ordinals"], f"{row['reference_id']} target")
        audit.check(
            all((row["locus"], str(ordinal)) in token_by_key for ordinal in source_ordinals + target_ordinals),
            f"{row['reference_id']} stated ordinals exist",
        )
        if row["linked_edge_ids"] != "NONE":
            linked = row["linked_edge_ids"].split("|")
            audit.check(len(linked) == 1 and linked[0] in EXPECTED_EDGE_CORE, f"{row['reference_id']} links one admitted edge")
            edge = edge_by_id[(linked[0],)]
            expected_sources = list(
                range(integer(edge["source_start_ordinal"], linked[0]), integer(edge["source_end_ordinal"], linked[0]) + 1)
            )
            audit.check(source_ordinals == expected_sources, f"{row['reference_id']} source ordinals equal linked edge")
            audit.check(target_ordinals == [integer(edge["target_action_ordinal"], linked[0])], f"{row['reference_id']} target equals linked edge")
            audit.check(integer(row["reference_ordinal"], row["reference_id"]) == integer(edge["reference_ordinal"], linked[0]), f"{row['reference_id']} reference equals linked edge")
            linked_reference_edges.add(linked[0])
    audit.check(
        linked_reference_edges == {"C001", "C002", "C003", "C004", "C006", "C009"},
        "exactly six admitted edges use written reference positions",
    )

    # Rival positions are real V68 joins but never become admitted edges.
    audit.check(len(rival_specs) == 17, "exactly 17 held rival specifications")
    rival_by_id = indexed(rival_specs, ["rival_id"], "relation rivals")
    audit.check(
        {key[0] for key in rival_by_id} == {f"H{number:03d}" for number in range(1, 8)} | {f"P{number:03d}" for number in range(1, 11)},
        "closed H001-H007 plus P001-P010 rival identity",
    )
    audit.check(
        Counter(row["rival_kind"] for row in rival_specs)
        == Counter({"EXPLICIT_REFERENCE_RIVAL": 7, "PROXIMITY_ONLY": 10}),
        "seven explicit-reference and ten proximity-only rivals",
    )
    admitted_targets = {(row["locus"], row["target_action_ordinal"]) for row in edge_specs}
    rival_targets: set[tuple[str, str]] = set()
    for row in rival_specs:
        source_ordinals = ordinal_spec(row["source_ordinals"], f"{row['rival_id']} source")
        source_rows = [token_by_key.get((row["locus"], str(ordinal))) for ordinal in source_ordinals]
        audit.check(all(source_rows), f"{row['rival_id']} source ordinals exist")
        source_rows = [source for source in source_rows if source is not None]
        audit.check(
            [source["surface"] for source in source_rows]
            == split_parallel(row["expected_source_surfaces"], "|", len(source_rows), f"{row['rival_id']} source surfaces"),
            f"{row['rival_id']} source surfaces join V68",
        )
        target_key = row["locus"], row["target_action_ordinal"]
        target_clause_key = row["locus"], integer(row["target_action_ordinal"], row["rival_id"])
        target = token_by_key.get(target_key)
        audit.check(target is not None, f"{row['rival_id']} target exists")
        assert target is not None
        audit.check(target["surface"] == row["expected_target_surface"], f"{row['rival_id']} target surface joins V68")
        audit.check(
            target["v68_clause_type"] == "ACTION_CLAUSE"
            and target["v68_action_license"] == "GDT689_V62_ACTION_ORDINAL",
            f"{row['rival_id']} target is a written action",
        )
        target_clauses = clauses_by_position[target_clause_key]
        audit.check(
            len(target_clauses) == 1
            and target_clauses[0]["clause_type"] == "ACTION_CLAUSE"
            and ordinal_spec(target_clauses[0]["action_ordinals"], row["rival_id"])
            == [integer(row["target_action_ordinal"], row["rival_id"])],
            f"{row['rival_id']} maps to exactly one written-action clause",
        )
        audit.check(target_key not in admitted_targets, f"{row['rival_id']} remains outside admitted target deck")
        rival_targets.add(target_key)
    audit.check(len(rival_targets) == 17, "all 17 rivals are occurrence-distinct")

    # Bind the only two older GDT676 occurrence-level QOL licenses exactly.
    _, syntax = read_tsv(G676 / "src/SYNTAX_TEMPLATES.tsv")
    syntax_by_id = indexed(syntax, ["template_id"], "GDT676 syntax templates")
    t03 = syntax_by_id.get(("GDT676-T03",))
    audit.check(t03 is not None, "GDT676 syntax template T03 exists")
    assert t03 is not None
    audit.check(t03["visible_pattern"] == "RESULT_OR_OBJECT QOL", "GDT676 T03 visible pattern exact")
    audit.check(
        t03["renderer_rule"]
        == "QOL is the add action and the left item is its object; fused QOL+SHEEDY contains one add action plus one finished moist object.",
        "GDT676 T03 renderer rule exact",
    )
    _, scope = read_tsv(G676 / "artifacts/ACTION_SCOPE_AUDIT.tsv")
    scope_by_locus = indexed(scope, ["locus"], "GDT676 action scope")
    audit.check(
        (
            scope_by_locus[("f77r.38",)]["action_ordinals"],
            scope_by_locus[("f77r.38",)]["gdt675_render_correction"],
        )
        == ("3:qoeedy|6:qol|9:qol", "RENDER_CHCPHEY_AS_OBJECT_OF_QOL_AT_6"),
        "GDT676 f77r.38 object-of-qol license exact",
    )
    audit.check(
        (
            scope_by_locus[("f80v.35",)]["action_ordinals"],
            scope_by_locus[("f80v.35",)]["gdt675_render_correction"],
        )
        == ("5:qol|6:qol", "RENDER_OLKAR_AS_NOMINAL_REFERENCE_OR_OBJECT_BEFORE_QOL_5_6"),
        "GDT676 f80v.35 two-qol license exact",
    )

    # Published overlays must be lossless projections of GDT695 and exact
    # materializations of the three closed source decks.
    edge_extra_fields = [
        "observed_source_clause_ids",
        "observed_target_clause_id",
        "observed_target_clause_type",
        "observed_right_surfaces",
        "source_join_exact",
        "reference_join_exact",
        "target_join_exact",
        "v68_word_delta",
        "edge_status",
    ]
    reference_extra_fields = [
        "observed_surface",
        "observed_gloss_de",
        "exact_v68_match",
        "v69_resolution_scope",
    ]
    rival_extra_fields = [
        "observed_source_surfaces",
        "observed_target_surface",
        "source_target_join_exact",
        "decision",
    ]
    token_extra_fields = [
        "v69_relation_roles",
        "v69_edge_ids",
        "v69_source_edge_ids",
        "v69_reference_ids",
        "v69_target_edge_ids",
        "v69_rival_ids",
        "v69_token_gloss_de",
        "v69_word_delta",
        "v69_status",
    ]
    line_projection_fields = line_fields
    line_extra_fields = [
        "v69_clause_translation_de",
        "admitted_edge_ids",
        "strong_edge_ids",
        "working_edge_ids",
        "reference_decisions",
        "held_rival_ids",
        "relation_annotations_de",
        "v69_word_delta",
        "v69_status",
    ]
    span_extra_fields = ["v69_selected_gloss_de", "v69_byte_identical", "v69_relation_change"]

    published_edge_fields, published_edges = read_tsv(
        EDGE_ARTIFACT, exact_fields=[*edge_fields, *edge_extra_fields]
    )
    published_reference_fields, published_references = read_tsv(
        REFERENCE_ARTIFACT, exact_fields=[*reference_fields, *reference_extra_fields]
    )
    published_rival_fields, published_rivals = read_tsv(
        RIVAL_ARTIFACT, exact_fields=[*rival_fields, *rival_extra_fields]
    )
    published_token_fields, published_tokens = read_tsv(
        TOKEN_ARTIFACT, exact_fields=[*token_fields, *token_extra_fields]
    )
    published_line_fields, published_lines = read_tsv(
        LINE_ARTIFACT, exact_fields=[*line_projection_fields, *line_extra_fields]
    )
    published_span_fields, published_spans = read_tsv(
        SPAN_ARTIFACT, exact_fields=[*span_fields, *span_extra_fields]
    )
    class_fields, class_census = read_tsv(
        CLASS_ARTIFACT, exact_fields=["relation_class", "edges", "edge_ids"]
    )

    assert_source_projection(audit, edge_fields, edge_specs, published_edge_fields, published_edges, "published edge deck")
    assert_source_projection(audit, reference_fields, reference_specs, published_reference_fields, published_references, "published reference census")
    assert_source_projection(audit, rival_fields, rival_specs, published_rival_fields, published_rivals, "published rival deck")
    assert_projection(audit, token_fields, tokens, published_token_fields, published_tokens, "479-token overlay")
    assert_projection(audit, line_projection_fields, lines, published_line_fields, published_lines, "51-line translation overlay")
    assert_projection(audit, span_fields, spans, published_span_fields, published_spans, "three-span freeze")
    audit.check(
        no_forbidden_locus(
            [
                *published_edges,
                *published_references,
                *published_rivals,
                *published_tokens,
                *published_lines,
                *published_spans,
            ]
        ),
        "all published row artifacts exclude f84/f84r",
    )

    for source, published in zip(edge_specs, published_edges):
        source_ordinals = range(
            integer(source["source_start_ordinal"], source["edge_id"]),
            integer(source["source_end_ordinal"], source["edge_id"]) + 1,
        )
        source_clause_ids = "|".join(
            dict.fromkeys(
                token_by_key[(source["locus"], str(ordinal))]["v68_clause_id"]
                for ordinal in source_ordinals
            )
        )
        target_ordinal = integer(source["target_action_ordinal"], source["edge_id"])
        target_clause = clauses_by_position[(source["locus"], target_ordinal)][0]
        audit.check(
            tuple(published[field] for field in edge_extra_fields)
            == (
                source_clause_ids,
                target_clause["clause_id"],
                "ACTION_CLAUSE",
                "NONE",
                "1",
                "1",
                "1",
                "0",
                "ADMITTED_OCCURRENCE_BOUND_METADATA_EDGE",
            ),
            f"{source['edge_id']} published join certificate exact",
        )

    for source, published in zip(reference_specs, published_references):
        observed = token_by_key[(source["locus"], source["reference_ordinal"])]
        scope = "OCCURRENCE_ONLY" if source["linked_edge_ids"] != "NONE" else "NO_NEW_OBJECT_EDGE"
        audit.check(
            tuple(published[field] for field in reference_extra_fields)
            == (observed["surface"], observed["v68_token_gloss_de"], "1", scope),
            f"{source['reference_id']} published decision certificate exact",
        )

    for source, published in zip(rival_specs, published_rivals):
        ordinals = ordinal_spec(source["source_ordinals"], source["rival_id"])
        observed_sources = "|".join(
            token_by_key[(source["locus"], str(ordinal))]["surface"] for ordinal in ordinals
        )
        observed_target = token_by_key[
            (source["locus"], source["target_action_ordinal"])
        ]["surface"]
        audit.check(
            tuple(published[field] for field in rival_extra_fields)
            == (
                observed_sources,
                observed_target,
                "1",
                "HELD_AS_RIVAL_NOT_ADMITTED",
            ),
            f"{source['rival_id']} published hold certificate exact",
        )

    # Rebuild every relation-ID and role annotation without consulting run.py.
    expected_roles: dict[tuple[str, str], list[str]] = defaultdict(list)
    expected_edge_ids: dict[tuple[str, str], set[str]] = defaultdict(set)
    expected_source_edge_ids: dict[tuple[str, str], set[str]] = defaultdict(set)
    expected_reference_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
    expected_target_edge_ids: dict[tuple[str, str], set[str]] = defaultdict(set)
    expected_rival_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
    for edge in edge_specs:
        edge_id = edge["edge_id"]
        locus = edge["locus"]
        source_ordinals = range(
            integer(edge["source_start_ordinal"], edge_id),
            integer(edge["source_end_ordinal"], edge_id) + 1,
        )
        reference_ordinals = ordinal_spec(edge["reference_ordinal"], edge_id)
        target_ordinal = integer(edge["target_action_ordinal"], edge_id)
        right_ordinals = ordinal_spec(edge["right_participant_ordinals"], edge_id)
        left_roles = role_map(edge["left_role_map"], edge_id)
        for ordinal in source_ordinals:
            key = locus, str(ordinal)
            expected_roles[key].append(f"{left_roles[ordinal]}:{edge_id}")
            expected_edge_ids[key].add(edge_id)
            expected_source_edge_ids[key].add(edge_id)
        for ordinal in reference_ordinals:
            key = locus, str(ordinal)
            expected_roles[key].append(f"REFERENCE:{edge_id}")
            expected_edge_ids[key].add(edge_id)
        target_key = locus, str(target_ordinal)
        expected_roles[target_key].append(f"TARGET_ACTION:{edge_id}")
        expected_edge_ids[target_key].add(edge_id)
        expected_target_edge_ids[target_key].add(edge_id)
        for ordinal in right_ordinals:
            key = locus, str(ordinal)
            expected_roles[key].append(f"RIGHT_PARTICIPANT:{edge_id}")
            expected_edge_ids[key].add(edge_id)
    for reference in reference_specs:
        expected_reference_ids[(reference["locus"], reference["reference_ordinal"])].append(
            reference["reference_id"]
        )
    for rival in rival_specs:
        locus = rival["locus"]
        for ordinal in ordinal_spec(rival["source_ordinals"], rival["rival_id"]):
            expected_rival_ids[(locus, str(ordinal))].append(rival["rival_id"])
        expected_rival_ids[(locus, rival["target_action_ordinal"])].append(rival["rival_id"])

    for source, published in zip(tokens, published_tokens):
        key = source["locus"], source["token_ordinal"]
        audit.check(
            tuple(published[field] for field in token_extra_fields)
            == (
                "|".join(expected_roles[key]) or "NONE",
                "|".join(sorted(expected_edge_ids[key])) or "NONE",
                "|".join(sorted(expected_source_edge_ids[key])) or "NONE",
                "|".join(expected_reference_ids[key]) or "NONE",
                "|".join(sorted(expected_target_edge_ids[key])) or "NONE",
                "|".join(expected_rival_ids[key]) or "NONE",
                source["v68_token_gloss_de"],
                "0",
                "V68_WORDS_FROZEN__RELATION_METADATA_ONLY",
            ),
            f"token relation overlay exact {key[0]}#{key[1]}",
        )
    audit.check(
        {
            value
            for row in published_tokens
            for value in ([] if row["v69_edge_ids"] == "NONE" else row["v69_edge_ids"].split("|"))
        }
        == set(EXPECTED_EDGE_CORE),
        "token overlay exposes exactly C001-C009",
    )
    audit.check(
        {
            value
            for row in published_tokens
            for value in ([] if row["v69_reference_ids"] == "NONE" else row["v69_reference_ids"].split("|"))
        }
        == set(EXPECTED_REFERENCE_DECISIONS),
        "token overlay exposes exactly R001-R027",
    )
    audit.check(
        {
            value
            for row in published_tokens
            for value in ([] if row["v69_rival_ids"] == "NONE" else row["v69_rival_ids"].split("|"))
        }
        == {key[0] for key in rival_by_id},
        "token overlay exposes all and only 17 held rivals",
    )
    c007_output_label = next(
        row for row in published_tokens
        if row["locus"] == "f86v6.25" and row["token_ordinal"] == "2"
    )
    c007_donor = next(
        row for row in published_tokens
        if row["locus"] == "f86v6.25" and row["token_ordinal"] == "3"
    )
    audit.check(
        c007_output_label["v69_relation_roles"] == "OUTPUT_LABEL:C007"
        and "DONOR" not in c007_output_label["v69_relation_roles"],
        "C007 ordinal 2 is an output label and not a donor",
    )
    audit.check(
        c007_donor["v69_relation_roles"] == "DONOR_SOURCE_SHARE:C007",
        "C007 ordinal 3 is the exact donor source share",
    )

    edges_by_locus: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    references_by_locus: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    rivals_by_locus: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in edge_specs:
        edges_by_locus[row["locus"]].append(row)
    for row in reference_specs:
        references_by_locus[row["locus"]].append(row)
    for row in rival_specs:
        rivals_by_locus[row["locus"]].append(row)
    for source, published in zip(lines, published_lines):
        local_edges = edges_by_locus[source["locus"]]
        expected_extra = (
            source["v68_clause_translation_de"],
            "|".join(row["edge_id"] for row in local_edges) or "NONE",
            "|".join(row["edge_id"] for row in local_edges if row["support_tier"] != "B_WORKING_LOCAL") or "NONE",
            "|".join(row["edge_id"] for row in local_edges if row["support_tier"] == "B_WORKING_LOCAL") or "NONE",
            "|".join(f"{row['reference_id']}:{row['decision']}" for row in references_by_locus[source["locus"]]) or "NONE",
            "|".join(row["rival_id"] for row in rivals_by_locus[source["locus"]]) or "NONE",
            " || ".join(f"{row['edge_id']}: {row['relation_explicit_de']}" for row in local_edges) or "NONE",
            "0",
            "UNCHANGED_V68_TEXT_WITH_SEPARATE_OCCURRENCE_RELATIONS",
        )
        audit.check(
            tuple(published[field] for field in line_extra_fields) == expected_extra,
            f"line relation overlay exact {source['locus']}",
        )
    audit.check(
        sum(row["admitted_edge_ids"] != "NONE" for row in published_lines) == 7,
        "exactly seven lines carry the nine occurrence-bound edges",
    )

    for source, published in zip(spans, published_spans):
        audit.check(
            tuple(published[field] for field in span_extra_fields)
            == (source["v68_selected_gloss_de"], "1", "NONE"),
            f"bound span remains byte-identical {source['span_id']}",
        )

    expected_census = [
        {
            "relation_class": relation_class,
            "edges": str(count),
            "edge_ids": "|".join(
                row["edge_id"] for row in edge_specs if row["relation_class"] == relation_class
            ),
        }
        for relation_class, count in sorted(
            Counter(row["relation_class"] for row in edge_specs).items()
        )
    ]
    audit.check(class_fields == ["relation_class", "edges", "edge_ids"], "relation census schema exact")
    audit.check(class_census == expected_census and len(class_census) == 9, "complete nine-class relation census reconstructed exactly")

    # Compact result, hashes, human reader and top-level report integrity.
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result.get("status") == STATUS, "RESULT status exact")
    audit.check(set(result.get("files", {})) == EXPECTED_GENERATED, "RESULT enumerates the complete compact artifact set")
    for name, digest in result["files"].items():
        path = ART / name
        audit.check(path.is_file(), f"artifact exists {name}")
        audit.check(sha256(path) == digest, f"artifact hash exact {name}")
    audit.check(isinstance(result.get("inputs"), dict) and len(result["inputs"]) >= 8, "RESULT seals its material inputs")
    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        audit.check(path.is_file() and sha256(path) == digest, f"input hash exact {relative}")

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
            "v68_action_clauses": 83,
            "v68_clauses": 175,
            "v68_nominal_blocks": 92,
        },
        "RESULT basis exact",
    )
    audit.check(
        result.get("relations")
        == {
            "admitted_edges": 9,
            "admitted_total": 9,
            "affected_loci": 7,
            "generic_nearest_donor_rules": 0,
            "held_relation_rivals": 17,
            "held_rivals": 17,
            "reference_positions": 27,
            "reference_positions_exhausted": 27,
            "references_with_admitted_edge": 6,
            "strong_edges": 6,
            "strong_plus_explicit_output": 6,
            "working_edges": 3,
            "working_local": 3,
        },
        "RESULT relation counts and zero generic-nearest rule exact",
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
        "RESULT zero-word-delta freeze exact",
    )
    audit.check(
        result.get("edge_support_tiers")
        == {"A_MINUS_EXPLICIT_OUTPUT": 1, "A_STRONG_LICENSED": 5, "B_WORKING_LOCAL": 3},
        "RESULT edge tiers exact",
    )
    audit.check(result.get("reference_decisions") == dict(EXPECTED_REFERENCE_CENSUS), "RESULT reference census exact")
    audit.check(
        result.get("rival_kinds") == {"EXPLICIT_REFERENCE_RIVAL": 7, "PROXIMITY_ONLY": 10},
        "RESULT rival census exact",
    )

    reader = READER_ARTIFACT.read_text(encoding="utf-8")
    report = (EXP / "REPORT.md").read_text(encoding="utf-8")
    artifact_readme = (ART / "README.md").read_text(encoding="utf-8")
    for edge in edge_specs:
        audit.check(edge["edge_id"] in reader and edge["relation_explicit_de"] in reader, f"human reader prints {edge['edge_id']} and exact explicit reading")
    for rival in rival_specs:
        audit.check(rival["rival_id"] in reader, f"human reader retains rival {rival['rival_id']}")
    audit.check(STATUS in report, "REPORT publishes exact result status")
    audit.check(
        "no “nearest material” fallback" in report
        and "No nearest-noun or nearest-material rule is introduced." in reader,
        "reports explicitly reject a generic nearest-donor rule",
    )
    audit.check(
        all(name in artifact_readme for name in EXPECTED_GENERATED - {"README.md"}),
        "artifact README maps every generated artifact",
    )

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    audit.check(manifest.get("experiment_id") == "GDT696" and manifest.get("slug") == "v68_exact_local_object_carries", "manifest experiment identity")
    audit.check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest forbids f84 and f84r")
    audit.check(manifest.get("status") == STATUS, "manifest status matches RESULT")
    audit.check(manifest.get("claim_ceiling") == result.get("claim_ceiling") and bool(result.get("claim_ceiling")), "manifest and RESULT claim ceiling exact")

    payload = {
        "status": "PASS",
        "checks": len(audit.checks),
        "failed": 0,
        "summary": {
            "tokens_frozen": 479,
            "lines_frozen": 51,
            "spans_frozen": 3,
            "admitted_edges": 9,
            "strong_or_a_minus_edges": 6,
            "working_edges": 3,
            "reference_positions": 27,
            "held_rivals": 17,
            "new_word_meanings": 0,
            "changed_word_meanings": 0,
            "new_pages": 0,
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
