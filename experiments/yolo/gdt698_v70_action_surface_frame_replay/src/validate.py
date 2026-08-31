#!/usr/bin/env python3
"""Independent fail-closed validation for GDT698.

The GDT698 builder is deliberately neither imported nor inspected here.  This
validator reconstructs every target-aligned replay directly from the fixed V71
template deck and the published GDT697 freezes.  An action surface, clause
shape, or neighbouring nominal is never sufficient: both the complete surface
sequence and its exact participant-role trace must match.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt698_v70_action_surface_frame_replay"
SRC = EXP / "src"
ART = EXP / "artifacts"
G697 = ROOT / "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts"

STATUS = (
    "PASS_V71_6_SURFACES_10_OCCURRENCES__9_EXISTING_MATCHES_"
    "1_UNBOUND_HELD__0_CROSS_REPLAYS__ZERO_WORD_DELTA"
)
QUESTION = (
    "Do any unbound occurrences of the six V70 action surfaces reproduce an "
    "already observed exact contiguous participant frame?"
)
CLAIM_CEILING = (
    "V71 exhausts the exact occurrences of the six action surfaces used by V70 "
    "and replays only nine already observed contiguous participant frames. All "
    "nine matches are self-source matches; the sole unbound qol remains held. "
    "No relation, microrecord, word meaning, or page is added."
)

SPEC = SRC / "V71_EXACT_TARGET_FRAME_TEMPLATES.tsv"
G697_RESULT = G697 / "RESULT.json"
G697_TOKENS = G697 / "V70_479_TOKEN_FREEZE.tsv"
G697_LINES = G697 / "V70_51_LINE_MICRORECORD_OVERLAY.tsv"
G697_SPANS = G697 / "V70_3_BOUND_SPAN_FREEZE.tsv"
G697_MICRORECORDS = G697 / "V70_7_EXACT_MICRORECORDS.tsv"
G697_EDGES = G697 / "V70_9_EDGE_WINDOW_COVERAGE.tsv"

TEMPLATE_ARTIFACT = ART / "V71_9_EXACT_TARGET_FRAME_TEMPLATES.tsv"
OCCURRENCE_ARTIFACT = ART / "V71_10_ACTION_SURFACE_OCCURRENCES.tsv"
CONTRAST_ARTIFACT = ART / "V71_3_UNBOUND_QOL_TEMPLATE_CONTRASTS.tsv"
CENSUS_ARTIFACT = ART / "V71_6_ACTION_SURFACE_CENSUS.tsv"
TOKEN_ARTIFACT = ART / "V71_479_TOKEN_FREEZE.tsv"
LINE_ARTIFACT = ART / "V71_51_LINE_FREEZE.tsv"
SPAN_ARTIFACT = ART / "V71_3_BOUND_SPAN_FREEZE.tsv"
READER_ARTIFACT = ART / "GDT698_V71_ACTION_SURFACE_FRAME_REPLAY_READER.md"

SPEC_SHA256 = "debf5a334eb44b5ba2dad654087457b82a82fa77897a4f6e652e109b2d8a8bb9"
RUN_DECLARED_SHA256 = "6c8af2073cc0e0f401e74a8273ca14e8c87b4733e5bdc20e4b0545a205d4a525"

G697_INPUT_HASHES = {
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/RESULT.json":
        "0d85be4ad35b1643eb619040f9da7a081fdd8839db73a68f3b2909fb2901bcaf",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_3_BOUND_SPAN_FREEZE.tsv":
        "1c5ec3a1838a84cdfc9fc80a3d51943dcfb279e368bdcb12fb8bead076ee171a",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_479_TOKEN_FREEZE.tsv":
        "c35a98d970dd0f4696fb9944325aa1f6fc038d219f6946b7834acc5889811238",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_51_LINE_MICRORECORD_OVERLAY.tsv":
        "6058271ccfe9b99a834e213c7cf01ae2938dcbd8c6939c61a087f0dfdc55833e",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_7_EXACT_MICRORECORDS.tsv":
        "c4b8b8e87e729b70da6f43115f666297b441035cebb210bdc7d37e59e52bcdcc",
    "experiments/yolo/gdt697_v69_exact_relation_microrecords/artifacts/V70_9_EDGE_WINDOW_COVERAGE.tsv":
        "02be802b569c39354f5bff77786cc2143e8d9e344bae09d4c8d14562f37a6aac",
}

RUN_RELATIVE = "experiments/yolo/gdt698_v70_action_surface_frame_replay/src/run.py"
SPEC_RELATIVE = "experiments/yolo/gdt698_v70_action_surface_frame_replay/src/V71_EXACT_TARGET_FRAME_TEMPLATES.tsv"
EXPECTED_RESULT_INPUTS = {
    **G697_INPUT_HASHES,
    SPEC_RELATIVE: SPEC_SHA256,
    RUN_RELATIVE: RUN_DECLARED_SHA256,
}

EXPECTED_GENERATED = {
    "GDT698_V71_ACTION_SURFACE_FRAME_REPLAY_READER.md",
    "README.md",
    "V71_10_ACTION_SURFACE_OCCURRENCES.tsv",
    "V71_3_BOUND_SPAN_FREEZE.tsv",
    "V71_3_UNBOUND_QOL_TEMPLATE_CONTRASTS.tsv",
    "V71_479_TOKEN_FREEZE.tsv",
    "V71_51_LINE_FREEZE.tsv",
    "V71_6_ACTION_SURFACE_CENSUS.tsv",
    "V71_9_EXACT_TARGET_FRAME_TEMPLATES.tsv",
}

EXPECTED_MANIFEST_OUTPUTS = {
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/README.md",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/METHOD.md",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/REPORT.md",
    SPEC_RELATIVE,
    RUN_RELATIVE,
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/src/validate.py",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/GDT698_V71_ACTION_SURFACE_FRAME_REPLAY_READER.md",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/README.md",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/RESULT.json",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_10_ACTION_SURFACE_OCCURRENCES.tsv",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_3_BOUND_SPAN_FREEZE.tsv",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_3_UNBOUND_QOL_TEMPLATE_CONTRASTS.tsv",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_479_TOKEN_FREEZE.tsv",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_51_LINE_FREEZE.tsv",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_6_ACTION_SURFACE_CENSUS.tsv",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/V71_9_EXACT_TARGET_FRAME_TEMPLATES.tsv",
    "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/VALIDATION.json",
}

SPEC_FIELDS = [
    "template_id", "source_edge_id", "microrecord_id", "action_surface",
    "target_offset", "window_surfaces", "window_glosses_de",
    "window_role_trace", "participant_frame_de", "topology", "replay_gate",
    "forbidden_shortcut",
]

TEMPLATE_FIELDS = [
    *SPEC_FIELDS,
    "source_locus", "source_target_ordinal", "window_start_ordinal",
    "window_end_ordinal", "window_length", "observed_surfaces",
    "observed_glosses_de", "observed_role_trace", "source_match_exact",
    "total_exact_hits", "self_source_hits", "cross_occurrence_hits", "status",
]

OCCURRENCE_FIELDS = [
    "occurrence_id", "page", "locus", "token_ordinal", "action_surface",
    "v70_token_gloss_de", "v68_clause_id", "v68_clause_type",
    "eligible_template_ids", "exact_match_template_ids", "exact_match_edge_ids",
    "inherited_target_edge_ids", "already_bound", "unbound_candidate",
    "context_start_ordinal", "context_end_ordinal", "context_surfaces",
    "context_glosses_de", "context_roles", "decision", "new_edge_count",
    "new_microrecord_count", "note",
]

CONTRAST_FIELDS = [
    "candidate_locus", "candidate_ordinal", "candidate_surface", "template_id",
    "source_edge_id", "expected_window_surfaces", "observed_aligned_surfaces",
    "expected_participant_frame_de", "observed_aligned_roles", "mismatch_offsets",
    "mismatch_count", "surface_frame_exact", "decision", "reason_de",
]

CENSUS_FIELDS = [
    "action_surface", "occurrence_count", "already_bound_count", "unbound_count",
    "template_count", "exact_template_hits", "self_source_hits",
    "cross_occurrence_hits", "new_candidate_hits",
    "participant_frame_multiplicity", "frame_determinacy", "decision",
]

TOKEN_EXTRA_FIELDS = [
    "v71_action_surface_scan", "v71_action_occurrence_id",
    "v71_exact_frame_match_ids", "v71_frame_decision", "v71_token_gloss_de",
    "v71_word_delta", "v71_status",
]
LINE_EXTRA_FIELDS = [
    "v71_action_occurrence_ids", "v71_existing_frame_match_count",
    "v71_unbound_action_count", "v71_new_frame_replay_count",
    "v71_clause_translation_de", "v71_word_delta", "v71_status",
]
SPAN_EXTRA_FIELDS = [
    "v71_selected_gloss_de", "v71_byte_identical", "v71_frame_replay_change",
    "v71_status",
]

# Duplicated intentionally: neither a changed template deck nor a changed
# generated table may silently redefine the independent validator's targets.
EXPECTED_TEMPLATES = {
    "T001": ("C001", "M002", "f105v.1", 4, "ykaiin"),
    "T002": ("C002", "M003", "f113v.17", 7, "yteeeor"),
    "T003": ("C003", "M004", "f75r.3", 4, "qey"),
    "T004": ("C004", "M006", "f80v.35", 5, "qol"),
    "T005": ("C005", "M005", "f77r.38", 6, "qol"),
    "T006": ("C006", "M007", "f86v6.25", 5, "ykaiin"),
    "T007": ("C007", "M007", "f86v6.25", 4, "qodar"),
    "T008": ("C008", "M006", "f80v.35", 6, "qol"),
    "T009": ("C009", "M001", "f104v.2", 6, "qokamdy"),
}

EXPECTED_OCCURRENCES = [
    ("A001", "f104v.2", 6, "qokamdy", "T009", "C009"),
    ("A002", "f105v.1", 4, "ykaiin", "T001", "C001"),
    ("A003", "f113v.17", 7, "yteeeor", "T002", "C002"),
    ("A004", "f75r.3", 4, "qey", "T003", "C003"),
    ("A005", "f77r.38", 6, "qol", "T005", "C005"),
    ("A006", "f77r.38", 9, "qol", "NONE", "NONE"),
    ("A007", "f80v.35", 5, "qol", "T004", "C004"),
    ("A008", "f80v.35", 6, "qol", "T008", "C008"),
    ("A009", "f86v6.25", 4, "qodar", "T007", "C007"),
    ("A010", "f86v6.25", 5, "ykaiin", "T006", "C006"),
]

EXPECTED_SURFACE_COUNTS = {
    "qokamdy": 1,
    "ykaiin": 2,
    "yteeeor": 1,
    "qey": 1,
    "qol": 4,
    "qodar": 1,
}

CONTRAST_MISMATCHES = {"T004": [0, 1], "T005": [0], "T008": [0, 1, 2]}
CONTRAST_REASONS = {
    "T004": "Der geschriebene Zielanteil und der Hierzu-Verweis fehlen; ltaiin|shedy ist kein olkar|y-Rahmen.",
    "T005": "Unmittelbar vor #9 steht der Feuchtzustand shedy, nicht das zugelassene Zugabeobjekt chcphey.",
    "T008": "Die zwei qol sind durch ltaiin|shedy und eine neue Nominalklausel getrennt; der gemeinsame olkar-Zielrahmen fehlt.",
}

FORBIDDEN_LOCUS_RE = re.compile(r"^f84(?:r|v)?(?:\b|\.)", re.IGNORECASE)
HEX_RE = re.compile(r"[0-9a-f]{64}")


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
            raise AssertionError(f"missing TSV value at row {number}: {path}")
    return fields, rows


def indexed(
    rows: Sequence[Mapping[str, str]],
    fields: Sequence[str],
    context: str,
) -> dict[tuple[str, ...], Mapping[str, str]]:
    result: dict[tuple[str, ...], Mapping[str, str]] = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        if key in result:
            raise AssertionError(f"duplicate key {key!r}: {context}")
        result[key] = row
    return result


def positive_integer(text: str, context: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]*", text):
        raise AssertionError(f"invalid positive integer {text!r}: {context}")
    return int(text)


def nonnegative_integer(text: str, context: str) -> int:
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)", text):
        raise AssertionError(f"invalid nonnegative integer {text!r}: {context}")
    return int(text)


def ids(text: str) -> list[str]:
    return [] if text == "NONE" else text.split("|")


def joined(values: Sequence[str]) -> str:
    return "|".join(values) if values else "NONE"


def split_trace(text: str) -> list[str]:
    return text.split(" || ")


def no_forbidden_locus(rows: Sequence[Mapping[str, str]]) -> bool:
    for row in rows:
        for field in ("locus", "source_locus", "candidate_locus"):
            value = row.get(field, "")
            if value and FORBIDDEN_LOCUS_RE.match(value):
                return False
    return True


def assert_projection(
    audit: Audit,
    source_fields: Sequence[str],
    source_rows: Sequence[Mapping[str, str]],
    output_fields: Sequence[str],
    output_rows: Sequence[Mapping[str, str]],
    label: str,
) -> None:
    audit.check(list(output_fields[: len(source_fields)]) == list(source_fields), f"{label} preserves source schema prefix")
    audit.check(len(source_rows) == len(output_rows), f"{label} preserves row count")
    for number, (source, output) in enumerate(zip(source_rows, output_rows), start=1):
        audit.check(
            all(output[field] == source[field] for field in source_fields),
            f"{label} source row byte-equivalent {number}",
        )


def aligned_rows(
    token_by_key: Mapping[tuple[str, str], Mapping[str, str]],
    locus: str,
    target: int,
    length: int,
) -> list[Mapping[str, str]]:
    start = target - length + 1
    if start < 1:
        return []
    result: list[Mapping[str, str]] = []
    for ordinal in range(start, target + 1):
        row = token_by_key.get((locus, str(ordinal)))
        if row is None:
            return []
        result.append(row)
    return result


def exact_frame_match(template: Mapping[str, str], aligned: Sequence[Mapping[str, str]]) -> bool:
    if not aligned:
        return False
    surfaces = "|".join(row["surface"] for row in aligned)
    roles = " || ".join(row["v70_window_role_trace"] for row in aligned)
    return surfaces == template["window_surfaces"] and roles == template["window_role_trace"]


def main() -> int:
    audit = Audit()

    # Fixed decks.  The builder itself is intentionally not opened or hashed.
    audit.check(sha256(SPEC) == SPEC_SHA256, "fixed V71 template source hash exact")
    for relative, expected in G697_INPUT_HASHES.items():
        audit.check(sha256(ROOT / relative) == expected, f"sealed GDT697 input hash exact {Path(relative).name}")

    spec_fields, templates = read_tsv(SPEC, exact_fields=SPEC_FIELDS)
    token_fields, tokens = read_tsv(G697_TOKENS)
    line_fields, lines = read_tsv(G697_LINES)
    span_fields, spans = read_tsv(G697_SPANS)
    _, microrecords = read_tsv(G697_MICRORECORDS)
    _, edges = read_tsv(G697_EDGES)
    g697_result = json.loads(G697_RESULT.read_text(encoding="utf-8"))

    audit.check(len(templates) == 9, "template source contains exactly nine rows")
    audit.check(len(tokens) == 479, "GDT697 supplies exactly 479 tokens")
    audit.check(len(lines) == 51, "GDT697 supplies exactly 51 lines")
    audit.check(len(spans) == 3, "GDT697 supplies exactly three bound spans")
    audit.check(len(microrecords) == 7, "GDT697 supplies exactly seven microrecords")
    audit.check(len(edges) == 9, "GDT697 supplies exactly nine covered edges")
    audit.check(
        g697_result.get("status", "").startswith("PASS_V70_7_EXACT_MICRORECORDS"),
        "GDT697 source result remains the passing V70 release",
    )
    for source in (G697_TOKENS, G697_LINES, G697_SPANS, G697_MICRORECORDS, G697_EDGES):
        audit.check(
            g697_result.get("files", {}).get(source.name) == sha256(source),
            f"GDT697 RESULT seals {source.name}",
        )
    audit.check(no_forbidden_locus([*templates, *tokens, *lines, *spans, *microrecords, *edges]), "all fixed decks exclude f84/f84r loci")

    template_by_id = indexed(templates, ["template_id"], "template source")
    edge_by_id = indexed(edges, ["edge_id"], "GDT697 edge coverage")
    micro_by_id = indexed(microrecords, ["microrecord_id"], "GDT697 microrecords")
    token_by_key = indexed(tokens, ["locus", "token_ordinal"], "GDT697 tokens")
    indexed(lines, ["locus"], "GDT697 lines")

    audit.check(set(key[0] for key in template_by_id) == set(EXPECTED_TEMPLATES), "template IDs are exactly T001-T009")
    audit.check(
        Counter(row["source_edge_id"] for row in templates) == Counter({f"C{number:03d}": 1 for number in range(1, 10)}),
        "templates cover C001-C009 exactly once",
    )

    action_surfaces = {row["action_surface"] for row in templates}
    audit.check(action_surfaces == set(EXPECTED_SURFACE_COUNTS), "template deck exposes exactly six fixed action surfaces")
    audit.check(
        Counter(row["action_surface"] for row in templates)
        == Counter({"qokamdy": 1, "ykaiin": 2, "yteeeor": 1, "qey": 1, "qol": 3, "qodar": 1}),
        "template multiplicity is ykaiin two, qol three, all others one",
    )

    template_source: dict[str, tuple[str, int]] = {}
    for template_id in sorted(EXPECTED_TEMPLATES):
        row = template_by_id[(template_id,)]
        edge_id, micro_id, locus, target, surface = EXPECTED_TEMPLATES[template_id]
        audit.check(
            (row["source_edge_id"], row["microrecord_id"], row["action_surface"])
            == (edge_id, micro_id, surface),
            f"{template_id} fixed edge, owner and action surface",
        )
        edge = edge_by_id[(edge_id,)]
        micro = micro_by_id[(micro_id,)]
        audit.check(
            (edge["microrecord_id"], edge["locus"], positive_integer(edge["target_action_ordinal"], edge_id))
            == (micro_id, locus, target),
            f"{template_id} joins exact GDT697 target coordinate",
        )
        audit.check(row["topology"] == edge["topology"] == micro["topology"], f"{template_id} topology exact")
        audit.check(row["replay_gate"] == "EXACT_CONTIGUOUS_SURFACE_HULL_ENDING_AT_TARGET", f"{template_id} exact replay gate")
        audit.check(
            row["forbidden_shortcut"] == "Action surface alone, clause shape, or nearest left noun is not a frame match.",
            f"{template_id} forbids surface, shape and proximity shortcuts",
        )
        surfaces = row["window_surfaces"].split("|")
        glosses = split_trace(row["window_glosses_de"])
        roles = split_trace(row["window_role_trace"])
        offset = nonnegative_integer(row["target_offset"], template_id)
        audit.check(len(surfaces) == len(glosses) == len(roles), f"{template_id} parallel frame widths exact")
        audit.check(offset == len(surfaces) - 1 and surfaces[-1] == surface, f"{template_id} is target-aligned at its final token")
        start = target - offset
        aligned = aligned_rows(token_by_key, locus, target, len(surfaces))
        audit.check(bool(aligned), f"{template_id} complete source hull exists")
        audit.check("|".join(token["surface"] for token in aligned) == row["window_surfaces"], f"{template_id} source surfaces exact")
        audit.check(" || ".join(token["v70_token_gloss_de"] for token in aligned) == row["window_glosses_de"], f"{template_id} source glosses exact")
        audit.check(" || ".join(token["v70_window_role_trace"] for token in aligned) == row["window_role_trace"], f"{template_id} source participant roles exact")
        audit.check(start == target - len(surfaces) + 1, f"{template_id} minimal aligned start exact")
        audit.check(edge_id in ids(token_by_key[(locus, str(target))]["v69_target_edge_ids"]), f"{template_id} target inherits its exact edge")
        audit.check(bool(row["participant_frame_de"]), f"{template_id} participant-frame description present")
        template_source[template_id] = (locus, target)

    # Exhaustive exact-surface occurrence scan in source token order.
    action_tokens = [row for row in tokens if row["surface"] in action_surfaces]
    audit.check(len(action_tokens) == 10, "six action surfaces have exactly ten V70 occurrences")
    audit.check(Counter(row["surface"] for row in action_tokens) == Counter(EXPECTED_SURFACE_COUNTS), "exact six-surface occurrence counts")
    audit.check(all(row["v68_clause_type"] == "ACTION_CLAUSE" for row in action_tokens), "all ten scanned positions are V68 action clauses")
    observed_coordinates = [(row["locus"], int(row["token_ordinal"]), row["surface"]) for row in action_tokens]
    audit.check(
        observed_coordinates == [(locus, ordinal, surface) for _, locus, ordinal, surface, _, _ in EXPECTED_OCCURRENCES],
        "ten action occurrences have the fixed coordinates and source order",
    )

    eligible_templates: dict[str, list[str]] = defaultdict(list)
    for row in templates:
        eligible_templates[row["action_surface"]].append(row["template_id"])

    hits_by_template: dict[str, list[tuple[str, int]]] = defaultdict(list)
    matches_by_occurrence: dict[tuple[str, int], list[str]] = defaultdict(list)
    for template in templates:
        template_id = template["template_id"]
        length = len(template["window_surfaces"].split("|"))
        for occurrence in action_tokens:
            if occurrence["surface"] != template["action_surface"]:
                continue
            locus = occurrence["locus"]
            target = positive_integer(occurrence["token_ordinal"], f"{locus} target")
            aligned = aligned_rows(token_by_key, locus, target, length)
            if exact_frame_match(template, aligned):
                hits_by_template[template_id].append((locus, target))
                matches_by_occurrence[(locus, target)].append(template_id)

    for template_id in sorted(EXPECTED_TEMPLATES):
        audit.check(hits_by_template[template_id] == [template_source[template_id]], f"{template_id} has exactly one self-source hit")
    audit.check(sum(len(value) for value in hits_by_template.values()) == 9, "nine exact target-aligned template hits")
    audit.check(sum(template_source[template_id] in hits for template_id, hits in hits_by_template.items()) == 9, "nine self-source hits")
    audit.check(
        sum(sum(hit != template_source[template_id] for hit in hits) for template_id, hits in hits_by_template.items()) == 0,
        "zero cross-occurrence frame hits",
    )

    # Published template replay rows are rebuilt, not trusted.
    _, published_templates = read_tsv(TEMPLATE_ARTIFACT, exact_fields=TEMPLATE_FIELDS)
    published_template_by_id = indexed(published_templates, ["template_id"], "published templates")
    audit.check(len(published_templates) == 9 and set(published_template_by_id) == set(template_by_id), "published template deck is exactly T001-T009")
    for template in templates:
        template_id = template["template_id"]
        row = published_template_by_id[(template_id,)]
        edge_id, _, locus, target, _ = EXPECTED_TEMPLATES[template_id]
        length = len(template["window_surfaces"].split("|"))
        start = target - int(template["target_offset"])
        expected_extra = {
            "source_locus": locus,
            "source_target_ordinal": str(target),
            "window_start_ordinal": str(start),
            "window_end_ordinal": str(target),
            "window_length": str(length),
            "observed_surfaces": template["window_surfaces"],
            "observed_glosses_de": template["window_glosses_de"],
            "observed_role_trace": template["window_role_trace"],
            "source_match_exact": "1",
            "total_exact_hits": "1",
            "self_source_hits": "1",
            "cross_occurrence_hits": "0",
            "status": "SOURCE_REPLAY_ONLY__NO_CROSS_OCCURRENCE_TRANSFER",
        }
        audit.check(all(row[field] == template[field] for field in SPEC_FIELDS), f"{template_id} publishes exact fixed specification")
        audit.check(all(row[field] == value for field, value in expected_extra.items()), f"{template_id} publishes exact independent replay counts")
        audit.check(row["source_edge_id"] == edge_id, f"{template_id} source edge unchanged")

    # Ten occurrence rows, including the sole open qol.
    _, published_occurrences = read_tsv(OCCURRENCE_ARTIFACT, exact_fields=OCCURRENCE_FIELDS)
    occurrence_by_id = indexed(published_occurrences, ["occurrence_id"], "published occurrences")
    audit.check(len(published_occurrences) == 10, "published occurrence inventory has ten rows")
    expected_occurrence_ids = {row[0] for row in EXPECTED_OCCURRENCES}
    audit.check({key[0] for key in occurrence_by_id} == expected_occurrence_ids, "published occurrence IDs are A001-A010")

    occurrence_id_by_key: dict[tuple[str, int], str] = {}
    for expected, source in zip(EXPECTED_OCCURRENCES, action_tokens):
        occurrence_id, locus, ordinal, surface, match_id, edge_id = expected
        row = occurrence_by_id[(occurrence_id,)]
        occurrence_id_by_key[(locus, ordinal)] = occurrence_id
        eligible = eligible_templates[surface]
        exact_matches = matches_by_occurrence[(locus, ordinal)]
        exact_edges = [template_by_id[(template_id,)]["source_edge_id"] for template_id in exact_matches]
        inherited = ids(source["v69_target_edge_ids"])
        bound = bool(inherited)
        context_start = max(1, ordinal - 3)
        context = [token_by_key[(locus, str(value))] for value in range(context_start, ordinal + 1)]
        decision = "ALREADY_ADMITTED_EXACT_SELF_REPLAY" if bound else "UNBOUND_NO_EXACT_PARTICIPANT_FRAME"
        note = (
            "Exact template match is the template's own GDT697 source occurrence; it adds no transfer."
            if bound
            else "Only a coarse nominal-block plus qol clause shape repeats; none of the three exact qol surface frames matches."
        )
        expected_row = {
            "occurrence_id": occurrence_id,
            "page": source["page"],
            "locus": locus,
            "token_ordinal": str(ordinal),
            "action_surface": surface,
            "v70_token_gloss_de": source["v70_token_gloss_de"],
            "v68_clause_id": source["v68_clause_id"],
            "v68_clause_type": source["v68_clause_type"],
            "eligible_template_ids": joined(eligible),
            "exact_match_template_ids": joined(exact_matches),
            "exact_match_edge_ids": joined(exact_edges),
            "inherited_target_edge_ids": joined(inherited),
            "already_bound": str(int(bound)),
            "unbound_candidate": str(int(not bound)),
            "context_start_ordinal": str(context_start),
            "context_end_ordinal": str(ordinal),
            "context_surfaces": "|".join(token["surface"] for token in context),
            "context_glosses_de": " || ".join(token["v70_token_gloss_de"] for token in context),
            "context_roles": " || ".join(token["v70_window_role_trace"] for token in context),
            "decision": decision,
            "new_edge_count": "0",
            "new_microrecord_count": "0",
            "note": note,
        }
        audit.check(all(row[field] == value for field, value in expected_row.items()), f"{occurrence_id} complete exact occurrence reconstruction")
        audit.check(match_id == joined(exact_matches) and edge_id == joined(exact_edges), f"{occurrence_id} fixed expected replay decision")

    bound_occurrences = [row for row in action_tokens if row["v69_target_edge_ids"] != "NONE"]
    unbound_occurrences = [row for row in action_tokens if row["v69_target_edge_ids"] == "NONE"]
    audit.check(len(bound_occurrences) == 9, "nine scanned occurrences are already admitted targets")
    audit.check(len(unbound_occurrences) == 1, "exactly one scanned occurrence is unbound")
    unbound = unbound_occurrences[0]
    audit.check(
        (unbound["locus"], unbound["token_ordinal"], unbound["surface"])
        == ("f77r.38", "9", "qol"),
        "sole unbound target is f77r.38#9 qol",
    )
    audit.check(matches_by_occurrence[("f77r.38", 9)] == [], "unbound qol has zero exact frame matches")

    # The three qol contrasts are aligned independently at the open target.
    _, contrasts = read_tsv(CONTRAST_ARTIFACT, exact_fields=CONTRAST_FIELDS)
    contrast_by_template = indexed(contrasts, ["template_id"], "qol contrasts")
    audit.check({key[0] for key in contrast_by_template} == {"T004", "T005", "T008"}, "unbound qol is contrasted with exactly three admitted qol templates")
    exact_role_contrasts = 0
    for template_id in ("T004", "T005", "T008"):
        template = template_by_id[(template_id,)]
        row = contrast_by_template[(template_id,)]
        length = len(template["window_surfaces"].split("|"))
        aligned = aligned_rows(token_by_key, "f77r.38", 9, length)
        observed_surfaces = [token["surface"] for token in aligned]
        expected_surfaces = template["window_surfaces"].split("|")
        observed_roles = " || ".join(token["v70_window_role_trace"] for token in aligned)
        mismatches = [index for index, (expected, observed) in enumerate(zip(expected_surfaces, observed_surfaces)) if expected != observed]
        exact_role = observed_roles == template["window_role_trace"]
        exact_role_contrasts += int(exact_role)
        expected_row = {
            "candidate_locus": "f77r.38",
            "candidate_ordinal": "9",
            "candidate_surface": "qol",
            "template_id": template_id,
            "source_edge_id": template["source_edge_id"],
            "expected_window_surfaces": template["window_surfaces"],
            "observed_aligned_surfaces": "|".join(observed_surfaces),
            "expected_participant_frame_de": template["participant_frame_de"],
            "observed_aligned_roles": observed_roles,
            "mismatch_offsets": "|".join(map(str, mismatches)),
            "mismatch_count": str(len(mismatches)),
            "surface_frame_exact": "0",
            "decision": "HOLD_NO_EXACT_FRAME_REPLAY",
            "reason_de": CONTRAST_REASONS[template_id],
        }
        audit.check(mismatches == CONTRAST_MISMATCHES[template_id], f"{template_id} exact unbound mismatch offsets and count")
        audit.check(not exact_role, f"{template_id} has no exact participant-role match at f77r.38#9")
        audit.check(all(row[field] == value for field, value in expected_row.items()), f"{template_id} published unbound contrast exact")
    audit.check(exact_role_contrasts == 0, "zero of three unbound qol contrasts matches its participant roles")

    # Six-row surface census.
    _, census = read_tsv(CENSUS_ARTIFACT, exact_fields=CENSUS_FIELDS)
    census_by_surface = indexed(census, ["action_surface"], "surface census")
    surface_order = list(dict.fromkeys(row["surface"] for row in action_tokens))
    audit.check([row["action_surface"] for row in census] == surface_order, "surface census follows first occurrence order")
    audit.check(set(key[0] for key in census_by_surface) == set(EXPECTED_SURFACE_COUNTS), "surface census covers exactly six surfaces")
    for surface in surface_order:
        row = census_by_surface[(surface,)]
        occurrences_here = [token for token in action_tokens if token["surface"] == surface]
        templates_here = eligible_templates[surface]
        exact_hits = sum(len(hits_by_template[template_id]) for template_id in templates_here)
        self_hits = sum(template_source[template_id] in hits_by_template[template_id] for template_id in templates_here)
        cross_hits = exact_hits - self_hits
        bound_here = sum(token["v69_target_edge_ids"] != "NONE" for token in occurrences_here)
        multiple = len(templates_here) > 1
        expected_row = {
            "action_surface": surface,
            "occurrence_count": str(len(occurrences_here)),
            "already_bound_count": str(bound_here),
            "unbound_count": str(len(occurrences_here) - bound_here),
            "template_count": str(len(templates_here)),
            "exact_template_hits": str(exact_hits),
            "self_source_hits": str(self_hits),
            "cross_occurrence_hits": str(cross_hits),
            "new_candidate_hits": "0",
            "participant_frame_multiplicity": str(len(templates_here)),
            "frame_determinacy": "MULTIPLE_ADMITTED_PARTICIPANT_FRAMES" if multiple else "SINGLE_OBSERVED_FRAME",
            "decision": "SURFACE_DOES_NOT_DETERMINE_PARTICIPANT_FRAME" if multiple else "NO_CROSS_OCCURRENCE_TRANSFER_TEST_AVAILABLE",
        }
        audit.check(all(row[field] == value for field, value in expected_row.items()), f"surface census exact {surface}")
    audit.check(census_by_surface[("ykaiin",)]["participant_frame_multiplicity"] == "2", "ykaiin retains two participant frames")
    audit.check(census_by_surface[("qol",)]["participant_frame_multiplicity"] == "3", "qol retains three participant frames")

    # Complete 479/51/3 projections remain byte-identical to V70.
    token_output_fields, token_output = read_tsv(TOKEN_ARTIFACT, exact_fields=[*token_fields, *TOKEN_EXTRA_FIELDS])
    line_output_fields, line_output = read_tsv(LINE_ARTIFACT, exact_fields=[*line_fields, *LINE_EXTRA_FIELDS])
    span_output_fields, span_output = read_tsv(SPAN_ARTIFACT, exact_fields=[*span_fields, *SPAN_EXTRA_FIELDS])
    assert_projection(audit, token_fields, tokens, token_output_fields, token_output, "479-token V71 freeze")
    assert_projection(audit, line_fields, lines, line_output_fields, line_output, "51-line V71 freeze")
    assert_projection(audit, span_fields, spans, span_output_fields, span_output, "three-span V71 freeze")

    for source, row in zip(tokens, token_output):
        locus = source["locus"]
        ordinal = positive_integer(source["token_ordinal"], f"token {locus}")
        occurrence_id = occurrence_id_by_key.get((locus, ordinal))
        if occurrence_id:
            matches = matches_by_occurrence[(locus, ordinal)]
            decision = "ALREADY_ADMITTED_EXACT_SELF_REPLAY" if source["v69_target_edge_ids"] != "NONE" else "UNBOUND_NO_EXACT_PARTICIPANT_FRAME"
            expected = ("1", occurrence_id, joined(matches), decision)
        else:
            expected = ("0", "NONE", "NONE", "NOT_IN_ACTION_SURFACE_SCAN")
        audit.check(
            tuple(row[field] for field in TOKEN_EXTRA_FIELDS[:4]) == expected,
            f"V71 scan metadata exact {locus}#{ordinal}",
        )
        audit.check(row["v71_token_gloss_de"] == source["v70_token_gloss_de"], f"V71 token gloss byte-identical {locus}#{ordinal}")
        audit.check(
            row["v71_word_delta"] == "0"
            and row["v71_status"] == "V70_TOKEN_GLOSS_BYTE_IDENTICAL__FRAME_REPLAY_METADATA_ONLY",
            f"V71 token zero delta and status exact {locus}#{ordinal}",
        )

    action_by_locus: dict[str, list[tuple[str, Mapping[str, str]]]] = defaultdict(list)
    for expected, source in zip(EXPECTED_OCCURRENCES, action_tokens):
        action_by_locus[source["locus"]].append((expected[0], source))
    for source, row in zip(lines, line_output):
        local = action_by_locus.get(source["locus"], [])
        exact_count = sum(bool(matches_by_occurrence[(token["locus"], int(token["token_ordinal"]))]) for _, token in local)
        unbound_count = sum(token["v69_target_edge_ids"] == "NONE" for _, token in local)
        audit.check(
            (
                row["v71_action_occurrence_ids"],
                row["v71_existing_frame_match_count"],
                row["v71_unbound_action_count"],
                row["v71_new_frame_replay_count"],
            )
            == (joined([occurrence_id for occurrence_id, _ in local]), str(exact_count), str(unbound_count), "0"),
            f"V71 line scan counts exact {source['locus']}",
        )
        audit.check(row["v71_clause_translation_de"] == source["v70_clause_translation_de"], f"V71 line text byte-identical {source['locus']}")
        audit.check(
            row["v71_word_delta"] == "0"
            and row["v71_status"] == "V70_LINE_BYTE_IDENTICAL__ACTION_FRAME_SCAN_ONLY",
            f"V71 line zero delta and status exact {source['locus']}",
        )

    for source, row in zip(spans, span_output):
        audit.check(
            (
                row["v71_selected_gloss_de"], row["v71_byte_identical"],
                row["v71_frame_replay_change"], row["v71_status"],
            )
            == (source["v70_selected_gloss_de"], "1", "NONE", "V70_BOUND_SPAN_BYTE_IDENTICAL"),
            f"V71 bound span byte-identical {source['span_id']}",
        )
    audit.check(no_forbidden_locus([*token_output, *line_output, *span_output]), "all complete V71 projections exclude f84/f84r loci")

    # Compact machine result and all non-cyclic artifact hashes.
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result.get("status") == STATUS, "RESULT status exact")
    audit.check(result.get("question") == QUESTION, "RESULT question exact")
    audit.check(result.get("claim_ceiling") == CLAIM_CEILING, "RESULT claim ceiling exact")
    audit.check(set(result.get("files", {})) == EXPECTED_GENERATED, "RESULT enumerates exact generated artifact set")
    for name, digest in result["files"].items():
        path = ART / name
        audit.check(path.is_file(), f"RESULT artifact exists {name}")
        audit.check(sha256(path) == digest, f"RESULT artifact hash exact {name}")
    result_inputs = result.get("inputs", {})
    audit.check(result_inputs == EXPECTED_RESULT_INPUTS, "RESULT publishes exactly the sealed input paths and hashes")
    declared_run_hash = result_inputs.get(RUN_RELATIVE, "")
    audit.check(
        bool(HEX_RE.fullmatch(declared_run_hash)),
        "RESULT publishes a syntactically valid builder hash without validator access to builder source",
    )
    for relative, digest in EXPECTED_RESULT_INPUTS.items():
        if relative == RUN_RELATIVE:
            audit.check(digest == RUN_DECLARED_SHA256, "builder hash equals the externally supplied digest without opening builder source")
        else:
            audit.check(sha256(ROOT / relative) == digest, f"RESULT input hash matches actual {Path(relative).name}")

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
            "v70_edges": 9,
            "v70_microrecords": 7,
        },
        "RESULT fixed scope and forbidden-access counts exact",
    )
    audit.check(
        result.get("scan")
        == {
            "action_surface_occurrences": 10,
            "action_surface_types": 6,
            "already_bound_target_occurrences": 9,
            "cross_occurrence_template_hits": 0,
            "exact_frame_templates": 9,
            "exact_template_hits": 9,
            "new_candidate_hits": 0,
            "new_edges": 0,
            "new_microrecords": 0,
            "repeated_action_surface_types": 2,
            "repeated_surface_occurrences": 6,
            "self_source_template_hits": 9,
            "shape_only_false_friends": 1,
            "single_occurrence_surface_types": 4,
            "surface_types_with_multiple_participant_frames": 2,
            "unbound_target_occurrences": 1,
        },
        "RESULT complete 6/10/9/1/0 replay census exact",
    )
    audit.check(result.get("surface_counts") == EXPECTED_SURFACE_COUNTS, "RESULT six surface counts exact")
    audit.check(
        result.get("unbound_decision")
        == {
            "decision": "HOLD_NO_EXACT_FRAME_REPLAY",
            "eligible_qol_frames": 3,
            "exact_matches": 0,
            "locus": "f77r.38",
            "ordinal": 9,
            "surface": "qol",
        },
        "RESULT sole unbound qol decision exact",
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
        "RESULT 479/51/3 zero-word-delta freeze exact",
    )

    # Human reader must expose the negative transfer result and every contrast.
    reader = READER_ARTIFACT.read_text(encoding="utf-8")
    audit.check(STATUS in reader, "reader prints exact status")
    for occurrence_id, locus, ordinal, surface, match_id, _ in EXPECTED_OCCURRENCES:
        audit.check(occurrence_id in reader and f"{locus}#{ordinal}" in reader and f"`{surface}`" in reader, f"reader identifies {occurrence_id} exactly")
        audit.check(f"`{match_id}`" in reader, f"reader prints exact frame decision for {occurrence_id}")
    for template_id in ("T004", "T005", "T008"):
        edge_id = EXPECTED_TEMPLATES[template_id][0]
        audit.check(edge_id in reader and CONTRAST_REASONS[template_id] in reader, f"reader exposes {template_id} unbound contrast")
        audit.check(f"> {len(CONTRAST_MISMATCHES[template_id])} <" not in reader, f"reader mismatch count is not hidden in malformed prose for {template_id}")
    audit.check("0 exakte Cross-Occurrence-Replays" in reader, "reader states zero cross-occurrence replay")
    audit.check("0 neue Mikrorecords oder Kanten" in reader, "reader states zero new microrecords and edges")
    audit.check("`ykaiin` besitzt zwei" in reader and "`qol` drei" in reader, "reader preserves ykaiin-two and qol-three frame multiplicity")
    audit.check("479 Token, 51 Zeilen und 3 gebundene Spannen" in reader, "reader reports complete freeze")
    audit.check("[Teilnehmerbindung offen:]" in reader, "reader visibly marks the sole unbound action")
    audit.check(not re.search(r"\bf84r?\b", reader, re.IGNORECASE), "reader exposes no forbidden folio material")

    # Manifest identity, dependency graph, hashes and sealed-data contract.
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    audit.check(
        manifest.get("experiment_id") == "GDT698"
        and manifest.get("slug") == "v70_action_surface_frame_replay",
        "manifest experiment identity exact",
    )
    audit.check(manifest.get("status") == STATUS, "manifest status matches RESULT")
    audit.check(manifest.get("question") == QUESTION, "manifest question matches RESULT")
    audit.check(manifest.get("claim_ceiling") == CLAIM_CEILING, "manifest claim ceiling matches RESULT")
    audit.check(manifest.get("dependencies") == ["GDT697"], "manifest has only GDT697 dependency")
    audit.check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest forbids f84/f84r")
    audit.check(
        manifest.get("commands")
        == {
            "run": RUN_RELATIVE.replace("src/run.py", "src/run.py").replace("experiments/yolo/", "python3 experiments/yolo/"),
            "validate": "python3 experiments/yolo/gdt698_v70_action_surface_frame_replay/src/validate.py",
        },
        "manifest commands exact",
    )
    audit.check(
        manifest.get("artifact_policy", {}).get("max_inline_bytes") == 5_000_000
        and bool(manifest.get("artifact_policy", {}).get("large_artifact_justification")),
        "manifest justifies complete freeze artifacts",
    )
    audit.check(
        manifest.get("validation")
        == {
            "artifact": "experiments/yolo/gdt698_v70_action_surface_frame_replay/artifacts/VALIDATION.json",
            "status": "PASS",
        },
        "manifest validation contract exact",
    )

    manifest_inputs = manifest.get("inputs", [])
    audit.check(isinstance(manifest_inputs, list), "manifest inputs are a list")
    input_map = {entry.get("path"): entry for entry in manifest_inputs}
    audit.check(set(input_map) == set(G697_INPUT_HASHES), "manifest lists exactly six external GDT697 inputs")
    for relative, expected_hash in G697_INPUT_HASHES.items():
        entry = input_map[relative]
        audit.check(entry.get("sha256") == expected_hash == sha256(ROOT / relative), f"manifest input hash exact {Path(relative).name}")
        audit.check(bool(entry.get("role")), f"manifest input role present {Path(relative).name}")

    manifest_outputs = manifest.get("outputs", [])
    audit.check(isinstance(manifest_outputs, list), "manifest outputs are a list")
    output_map = {entry.get("path"): entry for entry in manifest_outputs}
    audit.check(set(output_map) == EXPECTED_MANIFEST_OUTPUTS, "manifest lists exact reproducible GDT698 output tree")
    for relative in sorted(EXPECTED_MANIFEST_OUTPUTS):
        entry = output_map[relative]
        digest = entry.get("sha256", "")
        audit.check(bool(HEX_RE.fullmatch(digest)), f"manifest output hash syntax exact {Path(relative).name}")
        audit.check(bool(entry.get("role")), f"manifest output role present {Path(relative).name}")
        if relative == RUN_RELATIVE:
            audit.check(digest == declared_run_hash, "manifest preserves RESULT-declared builder hash without reading builder source")
        elif relative.endswith("/VALIDATION.json"):
            # The file is rewritten below; avoiding a self-referential digest is
            # intentional.  Repository-wide manifest checks bind it afterward.
            pass
        else:
            path = ROOT / relative
            audit.check(path.is_file(), f"manifest output exists {relative}")
            audit.check(sha256(path) == digest, f"manifest output hash exact {relative}")
    audit.check(
        all(not Path(path).is_absolute() and "f84" not in path.lower() for path in [*input_map, *output_map]),
        "manifest paths are relative and exclude f84/f84r",
    )

    payload = {
        "status": "PASS",
        "checks": len(audit.checks),
        "failed": 0,
        "summary": {
            "exact_frame_templates": 9,
            "action_surface_types": 6,
            "action_surface_occurrences": 10,
            "already_bound_occurrences": 9,
            "unbound_occurrences": 1,
            "self_source_hits": 9,
            "cross_occurrence_hits": 0,
            "new_candidate_hits": 0,
            "unbound_qol_contrasts": 3,
            "unbound_qol_surface_mismatches": 6,
            "unbound_qol_role_frame_matches": 0,
            "ykaiin_participant_frames": 2,
            "qol_participant_frames": 3,
            "tokens_frozen": 479,
            "lines_frozen": 51,
            "spans_frozen": 3,
            "new_edges": 0,
            "new_microrecords": 0,
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
