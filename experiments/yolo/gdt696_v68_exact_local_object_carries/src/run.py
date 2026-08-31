#!/usr/bin/env python3
"""Build the V69 occurrence-bound relation overlay without changing V68 words."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt696_v68_exact_local_object_carries"
SRC = EXP / "src"
ART = EXP / "artifacts"
G695 = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization"
G676 = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer"

TOKENS = G695 / "artifacts/V68_479_TOKEN_FREEZE.tsv"
LINES = G695 / "artifacts/V68_51_LINE_CLAUSE_READER.tsv"
CLAUSES = G695 / "artifacts/V68_175_CLAUSE_REALIZATIONS.tsv"
SPANS = G695 / "artifacts/V68_3_BOUND_SPAN_FREEZE.tsv"
G695_RESULT = G695 / "artifacts/RESULT.json"
EDGE_SPECS = SRC / "V69_LOCAL_ACTION_EDGES.tsv"
REFERENCE_SPECS = SRC / "V69_REFERENCE_DECISIONS.tsv"
RIVAL_SPECS = SRC / "V69_RELATION_RIVALS.tsv"

STATUS = (
    "PASS_V69_6_STRONG_PLUS_3_WORKING_LOCAL_EDGES__"
    "27_REFERENCE_CENSUS__17_RIVALS_HELD__ZERO_WORD_DELTA"
)
CLAIM_CEILING = (
    "V69 is an occurrence-bound editorial relation overlay on the unchanged "
    "exploratory V68 German reader. It records six stronger and three working "
    "local source-to-action relations; it adds no Voynich word meaning and does "
    "not establish pronouns, case, syntax, plaintext, language, or procedure."
)
REFERENCE_RE = re.compile(
    r"\b(?:hiervon|hieraus|hierzu|hieran|vorstehende\w*|davon|dieses)\b",
    re.IGNORECASE,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.reader(handle, delimiter="\t"))
    require(bool(raw), f"empty TSV: {path}")
    width = len(raw[0])
    require(len(set(raw[0])) == width, f"duplicate TSV header: {path}")
    for number, row in enumerate(raw[1:], 2):
        require(len(row) == width, f"TSV width mismatch {path}:{number}: {len(row)} != {width}")
    return [dict(zip(raw[0], row)) for row in raw[1:]]


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def parse_ordinals(spec: str) -> list[int]:
    if spec == "NONE":
        return []
    out: list[int] = []
    for part in spec.split("|"):
        if "-" in part:
            left, right = (int(value) for value in part.split("-", 1))
            require(left <= right, f"reversed ordinal range: {spec}")
            out.extend(range(left, right + 1))
        else:
            out.append(int(part))
    require(len(out) == len(set(out)), f"duplicate ordinal in {spec}")
    return out


def split_expected(value: str, separator: str) -> list[str]:
    return [] if value == "NONE" else value.split(separator)


def parse_role_map(value: str) -> dict[int, str]:
    roles: dict[int, str] = {}
    for item in value.split("|"):
        ordinal_text, role = item.split(":", 1)
        ordinal = int(ordinal_text)
        require(ordinal not in roles, f"duplicate left-role ordinal: {value}")
        require(bool(re.fullmatch(r"[A-Z][A-Z_]*", role)), f"invalid left role: {role}")
        roles[ordinal] = role
    return roles


def md(value: str) -> str:
    return value.replace("|", "<br>").replace("\n", " ")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    token_rows = read_tsv(TOKENS)
    line_rows = read_tsv(LINES)
    clause_rows = read_tsv(CLAUSES)
    span_rows = read_tsv(SPANS)
    edge_specs = read_tsv(EDGE_SPECS)
    reference_specs = read_tsv(REFERENCE_SPECS)
    rival_specs = read_tsv(RIVAL_SPECS)

    require(len(token_rows) == 479, "V68 token count changed")
    require(len(line_rows) == 51, "V68 line count changed")
    require(len(clause_rows) == 175, "V68 clause count changed")
    require(len(span_rows) == 3, "V68 span count changed")
    require(all(row["byte_identical"] == "1" for row in token_rows), "V68 token freeze broken")
    require(all(row["v68_content_word_sequence_exact"] == "1" for row in line_rows), "V68 line freeze broken")
    require(all(row["v68_byte_identical"] == "1" for row in span_rows), "V68 span freeze broken")
    require(not any(row["locus"].lower().startswith("f84") for row in token_rows), "f84/f84r entered scope")
    require(len({row["locus"] for row in line_rows}) == 51, "duplicate V68 locus")

    g695_result = json.loads(G695_RESULT.read_text(encoding="utf-8"))
    require(g695_result["status"].startswith("PASS_V68_"), "GDT695 is not a passing V68 base")
    require(g695_result["basis"] == {
        "accepted_inherited_bindings": 10,
        "active_verb_occurrences": 115,
        "binding_inside_frozen_span": 1,
        "bound_spans": 3,
        "f84_access": 0,
        "f84r_access": 0,
        "lines": 51,
        "live_action_positions": 83,
        "new_colon_edges": 9,
        "new_pages": 0,
        "pages": 36,
        "right_bound_introducers": 4,
        "token_positions": 479,
    }, "unexpected GDT695 base")

    token_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in token_rows}
    require(len(token_by_key) == 479, "duplicate V68 token key")
    line_by_locus = {row["locus"]: row for row in line_rows}
    clauses_by_position: dict[tuple[str, int], dict[str, str]] = {}
    for row in clause_rows:
        for ordinal in range(int(row["start_ordinal"]), int(row["end_ordinal"]) + 1):
            key = (row["locus"], ordinal)
            require(key not in clauses_by_position, f"overlapping V68 clauses at {key}")
            clauses_by_position[key] = row
    require(len(clauses_by_position) == 479, "V68 clauses do not cover all tokens")

    syntax = read_tsv(G676 / "src/SYNTAX_TEMPLATES.tsv")
    t03 = [row for row in syntax if row["template_id"] == "GDT676-T03"]
    require(len(t03) == 1 and t03[0]["visible_pattern"] == "RESULT_OR_OBJECT QOL", "GDT676 T03 changed")
    scope = {row["locus"]: row for row in read_tsv(G676 / "artifacts/ACTION_SCOPE_AUDIT.tsv")}
    require(scope["f77r.38"]["gdt675_render_correction"] == "RENDER_CHCPHEY_AS_OBJECT_OF_QOL_AT_6", "f77r.38 license missing")
    require(scope["f80v.35"]["gdt675_render_correction"] == "RENDER_OLKAR_AS_NOMINAL_REFERENCE_OR_OBJECT_BEFORE_QOL_5_6", "f80v.35 license missing")

    expected_prior_needles = {
        ROOT / "experiments/yolo/gdt679_eight_three_hole_family_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv": ("f113v.17", "cthororaiin", "yteeeor", "f75r.3", "orchey", "qey"),
        ROOT / "experiments/yolo/gdt680_eight_four_hole_family_completion/artifacts/EIGHT_COMPLETED_LINES_V54.tsv": ("f86v6.25", "qodar", "ykaiin"),
        ROOT / "experiments/yolo/gdt681_six_five_hole_family_completion/artifacts/SIX_COMPLETED_LINES_V55.tsv": ("f104v.2", "ydaiin", "qokamdy"),
        ROOT / "experiments/yolo/gdt682_final_seven_hole_line_completion/artifacts/TARGET_EXACT_OCCURRENCE_AUDIT.tsv": ("f105v.1", "olpcheey", "ykaiin"),
    }
    for path, needles in expected_prior_needles.items():
        text = path.read_text(encoding="utf-8")
        require(all(needle in text for needle in needles), f"prior occurrence evidence changed: {path}")

    require(len(edge_specs) == 9, "edge deck must contain exactly 9 rows")
    require(len({row["edge_id"] for row in edge_specs}) == 9, "duplicate edge ID")
    require(Counter(row["support_tier"] for row in edge_specs) == Counter({
        "A_STRONG_LICENSED": 5,
        "A_MINUS_EXPLICIT_OUTPUT": 1,
        "B_WORKING_LOCAL": 3,
    }), "unexpected edge-tier census")
    require(len({row["relation_class"] for row in edge_specs}) == 9, "relation classes must remain occurrence-specific")

    edge_out: list[dict[str, object]] = []
    edge_by_id: dict[str, dict[str, str]] = {}
    token_roles: dict[tuple[str, int], list[str]] = defaultdict(list)
    token_edge_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    token_source_edge_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    token_target_edge_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    for spec in edge_specs:
        edge_id = spec["edge_id"]
        locus = spec["locus"]
        require(locus in line_by_locus and not locus.lower().startswith("f84"), f"bad edge locus: {locus}")
        start = int(spec["source_start_ordinal"])
        end = int(spec["source_end_ordinal"])
        source_ordinals = list(range(start, end + 1))
        left_roles = parse_role_map(spec["left_role_map"])
        require(list(left_roles) == source_ordinals, f"{edge_id} left-role map does not cover its exact source span")
        reference_ordinals = parse_ordinals(spec["reference_ordinal"])
        target = int(spec["target_action_ordinal"])
        right_ordinals = parse_ordinals(spec["right_participant_ordinals"])
        source_tokens = [token_by_key[(locus, ordinal)] for ordinal in source_ordinals]
        reference_tokens = [token_by_key[(locus, ordinal)] for ordinal in reference_ordinals]
        target_token = token_by_key[(locus, target)]
        right_tokens = [token_by_key[(locus, ordinal)] for ordinal in right_ordinals]
        require([row["surface"] for row in source_tokens] == split_expected(spec["expected_source_surfaces"], "|"), f"{edge_id} source surfaces changed")
        require([row["v68_token_gloss_de"] for row in source_tokens] == split_expected(spec["expected_source_glosses_de"], " || "), f"{edge_id} source glosses changed")
        require([row["surface"] for row in reference_tokens] == split_expected(spec["expected_reference_surface"], "|"), f"{edge_id} reference surface changed")
        require([row["v68_token_gloss_de"] for row in reference_tokens] == split_expected(spec["expected_reference_gloss_de"], " || "), f"{edge_id} reference gloss changed")
        require(target_token["surface"] == spec["expected_target_surface"], f"{edge_id} target surface changed")
        require(target_token["v68_token_gloss_de"] == spec["expected_target_gloss_de"], f"{edge_id} target gloss changed")
        target_clause = clauses_by_position[(locus, target)]
        require(target_clause["clause_type"] == "ACTION_CLAUSE", f"{edge_id} target is not an action clause")
        require(
            parse_ordinals(target_clause["action_ordinals"]) == [target],
            f"{edge_id} target clause does not contain exactly the nominated action ordinal",
        )
        require(target_token["v68_action_license"] == "GDT689_V62_ACTION_ORDINAL", f"{edge_id} lacks V62 action license")
        require(all(ordinal != target or ordinal in reference_ordinals for ordinal in source_ordinals), f"{edge_id} source consumes target")
        require(all((locus, ordinal) in token_by_key for ordinal in right_ordinals), f"{edge_id} right participant missing")
        source_clause_ids = "|".join(dict.fromkeys(row["v68_clause_id"] for row in source_tokens))
        row_out: dict[str, object] = dict(spec)
        row_out.update({
            "observed_source_clause_ids": source_clause_ids,
            "observed_target_clause_id": target_clause["clause_id"],
            "observed_target_clause_type": target_clause["clause_type"],
            "observed_right_surfaces": "|".join(row["surface"] for row in right_tokens) or "NONE",
            "source_join_exact": 1,
            "reference_join_exact": 1,
            "target_join_exact": 1,
            "v68_word_delta": 0,
            "edge_status": "ADMITTED_OCCURRENCE_BOUND_METADATA_EDGE",
        })
        edge_out.append(row_out)
        edge_by_id[edge_id] = spec
        for ordinal in source_ordinals:
            token_roles[(locus, ordinal)].append(f"{left_roles[ordinal]}:{edge_id}")
            token_edge_ids[(locus, ordinal)].add(edge_id)
            token_source_edge_ids[(locus, ordinal)].add(edge_id)
        for ordinal in reference_ordinals:
            token_roles[(locus, ordinal)].append(f"REFERENCE:{edge_id}")
            token_edge_ids[(locus, ordinal)].add(edge_id)
        token_roles[(locus, target)].append(f"TARGET_ACTION:{edge_id}")
        token_edge_ids[(locus, target)].add(edge_id)
        token_target_edge_ids[(locus, target)].add(edge_id)
        for ordinal in right_ordinals:
            token_roles[(locus, ordinal)].append(f"RIGHT_PARTICIPANT:{edge_id}")
            token_edge_ids[(locus, ordinal)].add(edge_id)

    detected_references = {
        (row["locus"], int(row["token_ordinal"])): row
        for row in token_rows
        if REFERENCE_RE.search(row["v68_token_gloss_de"])
    }
    require(len(detected_references) == 27, "V68 reference regex no longer yields 27 positions")
    require(len(reference_specs) == 27, "reference decision deck must contain 27 rows")
    require(len({row["reference_id"] for row in reference_specs}) == 27, "duplicate reference ID")
    expected_reference_counts = Counter({
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
    })
    require(Counter(row["decision"] for row in reference_specs) == expected_reference_counts, "reference category census changed")
    reference_keys = {(row["locus"], int(row["reference_ordinal"])) for row in reference_specs}
    require(reference_keys == set(detected_references), "reference deck does not exhaust the V68 reference positions")

    reference_out: list[dict[str, object]] = []
    token_reference_ids: dict[tuple[str, int], list[str]] = defaultdict(list)
    for spec in reference_specs:
        key = (spec["locus"], int(spec["reference_ordinal"]))
        observed = detected_references[key]
        require(observed["surface"] == spec["expected_surface"], f"{spec['reference_id']} surface changed")
        require(observed["v68_token_gloss_de"] == spec["expected_gloss_de"], f"{spec['reference_id']} gloss changed")
        linked = [] if spec["linked_edge_ids"] == "NONE" else spec["linked_edge_ids"].split("|")
        require(all(edge_id in edge_by_id for edge_id in linked), f"{spec['reference_id']} links unknown edge")
        if spec["decision"] == "ADMITTED_STRONG_EDGE":
            require(len(linked) == 1 and edge_by_id[linked[0]]["support_tier"] in {"A_STRONG_LICENSED", "A_MINUS_EXPLICIT_OUTPUT"}, f"{spec['reference_id']} strong link mismatch")
        elif spec["decision"] == "ADMITTED_WORKING_EDGE":
            require(len(linked) == 1 and edge_by_id[linked[0]]["support_tier"] == "B_WORKING_LOCAL", f"{spec['reference_id']} working link mismatch")
        else:
            require(not linked, f"{spec['reference_id']} non-admitted decision links an edge")
        if spec["decision"] == "UNRESOLVED_LINE_INITIAL":
            require(spec["reference_ordinal"] == "1" and spec["source_ordinals"] == "NONE", f"{spec['reference_id']} false line-initial hold")
        for edge_id in linked:
            edge = edge_by_id[edge_id]
            require(edge["locus"] == spec["locus"], f"{spec['reference_id']} cross-locus link")
            require(edge["reference_ordinal"] == spec["reference_ordinal"], f"{spec['reference_id']} edge/reference ordinal mismatch")
        source_ordinals = parse_ordinals(spec["source_ordinals"])
        target_ordinals = parse_ordinals(spec["target_ordinals"])
        require(all((spec["locus"], ordinal) in token_by_key for ordinal in source_ordinals + target_ordinals), f"{spec['reference_id']} source/target ordinal missing")
        reference_out.append({
            **spec,
            "observed_surface": observed["surface"],
            "observed_gloss_de": observed["v68_token_gloss_de"],
            "exact_v68_match": 1,
            "v69_resolution_scope": "OCCURRENCE_ONLY" if linked else "NO_NEW_OBJECT_EDGE",
        })
        token_reference_ids[key].append(spec["reference_id"])

    require(len(rival_specs) == 17, "rival deck must contain exactly 17 rows")
    require(Counter(row["rival_kind"] for row in rival_specs) == Counter({"EXPLICIT_REFERENCE_RIVAL": 7, "PROXIMITY_ONLY": 10}), "rival-kind census changed")
    require(len({row["rival_id"] for row in rival_specs}) == 17, "duplicate rival ID")
    require(not any("nearest" in row["rejection_reason"].lower() and "not" not in row["rejection_reason"].lower() for row in rival_specs), "generic nearest rule entered rival deck")
    rival_out: list[dict[str, object]] = []
    token_rival_ids: dict[tuple[str, int], list[str]] = defaultdict(list)
    admitted_signatures = {
        (row["locus"], tuple(range(int(row["source_start_ordinal"]), int(row["source_end_ordinal"]) + 1)), int(row["target_action_ordinal"]))
        for row in edge_specs
    }
    for spec in rival_specs:
        locus = spec["locus"]
        source_ordinals = parse_ordinals(spec["source_ordinals"])
        target = int(spec["target_action_ordinal"])
        sources = [token_by_key[(locus, ordinal)] for ordinal in source_ordinals]
        target_token = token_by_key[(locus, target)]
        require([row["surface"] for row in sources] == split_expected(spec["expected_source_surfaces"], "|"), f"{spec['rival_id']} source surface changed")
        require(target_token["surface"] == spec["expected_target_surface"], f"{spec['rival_id']} target surface changed")
        require(clauses_by_position[(locus, target)]["clause_type"] == "ACTION_CLAUSE", f"{spec['rival_id']} target is not action")
        require((locus, tuple(source_ordinals), target) not in admitted_signatures, f"{spec['rival_id']} duplicates admitted edge")
        rival_out.append({
            **spec,
            "observed_source_surfaces": "|".join(row["surface"] for row in sources),
            "observed_target_surface": target_token["surface"],
            "source_target_join_exact": 1,
            "decision": "HELD_AS_RIVAL_NOT_ADMITTED",
        })
        for ordinal in source_ordinals:
            token_rival_ids[(locus, ordinal)].append(spec["rival_id"])
        token_rival_ids[(locus, target)].append(spec["rival_id"])

    edge_fields = list(edge_specs[0]) + [
        "observed_source_clause_ids", "observed_target_clause_id", "observed_target_clause_type",
        "observed_right_surfaces", "source_join_exact", "reference_join_exact", "target_join_exact",
        "v68_word_delta", "edge_status",
    ]
    write_tsv(ART / "V69_9_LOCAL_ACTION_EDGES.tsv", edge_out, edge_fields)
    reference_fields = list(reference_specs[0]) + ["observed_surface", "observed_gloss_de", "exact_v68_match", "v69_resolution_scope"]
    write_tsv(ART / "V69_27_REFERENCE_CENSUS.tsv", reference_out, reference_fields)
    rival_fields = list(rival_specs[0]) + ["observed_source_surfaces", "observed_target_surface", "source_target_join_exact", "decision"]
    write_tsv(ART / "V69_17_RELATION_RIVALS.tsv", rival_out, rival_fields)

    token_out: list[dict[str, object]] = []
    for row in token_rows:
        key = (row["locus"], int(row["token_ordinal"]))
        token_out.append({
            **row,
            "v69_relation_roles": "|".join(token_roles[key]) or "NONE",
            "v69_edge_ids": "|".join(sorted(token_edge_ids[key])) or "NONE",
            "v69_source_edge_ids": "|".join(sorted(token_source_edge_ids[key])) or "NONE",
            "v69_reference_ids": "|".join(token_reference_ids[key]) or "NONE",
            "v69_target_edge_ids": "|".join(sorted(token_target_edge_ids[key])) or "NONE",
            "v69_rival_ids": "|".join(token_rival_ids[key]) or "NONE",
            "v69_token_gloss_de": row["v68_token_gloss_de"],
            "v69_word_delta": 0,
            "v69_status": "V68_WORDS_FROZEN__RELATION_METADATA_ONLY",
        })
    token_fields = list(token_rows[0]) + [
        "v69_relation_roles", "v69_edge_ids", "v69_source_edge_ids",
        "v69_reference_ids", "v69_target_edge_ids", "v69_rival_ids",
        "v69_token_gloss_de", "v69_word_delta", "v69_status",
    ]
    write_tsv(ART / "V69_479_TOKEN_RELATION_OVERLAY.tsv", token_out, token_fields)

    edges_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    refs_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    rivals_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in edge_specs:
        edges_by_locus[row["locus"]].append(row)
    for row in reference_specs:
        refs_by_locus[row["locus"]].append(row)
    for row in rival_specs:
        rivals_by_locus[row["locus"]].append(row)
    line_out: list[dict[str, object]] = []
    for row in line_rows:
        locus = row["locus"]
        local_edges = edges_by_locus[locus]
        annotations = " || ".join(f"{edge['edge_id']}: {edge['relation_explicit_de']}" for edge in local_edges) or "NONE"
        line_out.append({
            **row,
            "v69_clause_translation_de": row["v68_clause_translation_de"],
            "admitted_edge_ids": "|".join(edge["edge_id"] for edge in local_edges) or "NONE",
            "strong_edge_ids": "|".join(edge["edge_id"] for edge in local_edges if edge["support_tier"] != "B_WORKING_LOCAL") or "NONE",
            "working_edge_ids": "|".join(edge["edge_id"] for edge in local_edges if edge["support_tier"] == "B_WORKING_LOCAL") or "NONE",
            "reference_decisions": "|".join(f"{ref['reference_id']}:{ref['decision']}" for ref in refs_by_locus[locus]) or "NONE",
            "held_rival_ids": "|".join(rival["rival_id"] for rival in rivals_by_locus[locus]) or "NONE",
            "relation_annotations_de": annotations,
            "v69_word_delta": 0,
            "v69_status": "UNCHANGED_V68_TEXT_WITH_SEPARATE_OCCURRENCE_RELATIONS",
        })
    line_fields = list(line_rows[0]) + [
        "v69_clause_translation_de", "admitted_edge_ids", "strong_edge_ids",
        "working_edge_ids", "reference_decisions", "held_rival_ids",
        "relation_annotations_de", "v69_word_delta", "v69_status",
    ]
    write_tsv(ART / "V69_51_LINE_RELATION_OVERLAY.tsv", line_out, line_fields)

    span_out = [{**row, "v69_selected_gloss_de": row["v68_selected_gloss_de"], "v69_byte_identical": 1, "v69_relation_change": "NONE"} for row in span_rows]
    span_fields = list(span_rows[0]) + ["v69_selected_gloss_de", "v69_byte_identical", "v69_relation_change"]
    write_tsv(ART / "V69_3_BOUND_SPAN_FREEZE.tsv", span_out, span_fields)

    census_rows = [
        {
            "relation_class": relation_class,
            "edges": count,
            "edge_ids": "|".join(row["edge_id"] for row in edge_specs if row["relation_class"] == relation_class),
        }
        for relation_class, count in sorted(Counter(row["relation_class"] for row in edge_specs).items())
    ]
    write_tsv(ART / "V69_RELATION_CLASS_CENSUS.tsv", census_rows, ["relation_class", "edges", "edge_ids"])

    report_lines = [
        "# GDT696 — V69 local object/carry reader",
        "",
        f"Status: `{STATUS}`",
        "",
        "V69 leaves every V68 token gloss, line text and bound span unchanged. The new content is a finite occurrence-level relation layer: six stronger local edges and three explicitly working local edges. It is not a new dictionary.",
        "",
        "## Nine admitted local relations",
        "",
        "| ID | locus | tier | source → action | explicit practical relation |",
        "|---|---|---|---|---|",
    ]
    for row in edge_specs:
        relation = f"#{row['source_start_ordinal']}–#{row['source_end_ordinal']} `{row['expected_source_surfaces']}` → #{row['target_action_ordinal']} `{row['expected_target_surface']}`"
        report_lines.append(f"| {row['edge_id']} | {row['locus']} | {row['support_tier']} | {md(relation)} | {md(row['relation_explicit_de'])} |")
    report_lines.extend([
        "",
        "## Complete unchanged 51-line reader with relation notes",
        "",
        "The text after **V68** is byte-identical to GDT695. A relation note appears only at the seven affected loci; all other lines remain explicitly unlinked.",
        "",
    ])
    for row in line_out:
        report_lines.extend([
            f"### {row['locus']}",
            "",
            f"- Surface: `{row['zl3b_line']}`",
            f"- V68/V69 text: {row['v69_clause_translation_de']}",
            f"- Relation: {row['relation_annotations_de']}",
            f"- Reference decisions: `{row['reference_decisions']}`; held rivals: `{row['held_rival_ids']}`",
            "",
        ])
    report_lines.extend([
        "## Boundaries of the result",
        "",
        "All 27 visible German reference expressions are enumerated. Only six participate in a new admitted edge; seven object rivals, five line-initial references, two local rivals, three sequence-only connectors and four other nominal/process cases stay outside object carry. Seventeen tempting alternatives are printed as controls. No nearest-noun or nearest-material rule is introduced.",
        "",
        "The German relations are editorial working hypotheses tied to these exact occurrences. They do not make `y`, `qey`, `ykaiin`, or any substring a manuscript-wide pronoun, case marker, object marker, or word meaning.",
        "",
    ])
    reader_path = ART / "GDT696_V69_LOCAL_OBJECT_CARRY_READER.md"
    reader_path.write_text("\n".join(report_lines), encoding="utf-8")

    artifact_readme = ART / "README.md"
    artifact_readme.write_text(
        "# GDT696 artifacts\n\n"
        "- `V69_9_LOCAL_ACTION_EDGES.tsv`: finite admitted edge deck.\n"
        "- `V69_27_REFERENCE_CENSUS.tsv`: all reference-bearing V68 tokens.\n"
        "- `V69_17_RELATION_RIVALS.tsv`: seventeen held alternatives.\n"
        "- `V69_479_TOKEN_RELATION_OVERLAY.tsv`: complete frozen token overlay.\n"
        "- `V69_51_LINE_RELATION_OVERLAY.tsv`: complete unchanged line edition plus relation notes.\n"
        "- `V69_3_BOUND_SPAN_FREEZE.tsv`: byte-identical bound spans.\n"
        "- `V69_RELATION_CLASS_CENSUS.tsv`: exact nine-class edge census.\n"
        "- `GDT696_V69_LOCAL_OBJECT_CARRY_READER.md`: human-readable complete reader.\n",
        encoding="utf-8",
    )

    input_paths = [
        TOKENS, LINES, CLAUSES, SPANS, G695_RESULT,
        G676 / "src/SYNTAX_TEMPLATES.tsv",
        G676 / "artifacts/ACTION_SCOPE_AUDIT.tsv",
        *expected_prior_needles.keys(),
        ROOT / "experiments/yolo/gdt666_one_hundred_fifty_one_residual_family_completion/REPORT.md",
        ROOT / "experiments/yolo/gdt677_nine_one_hole_family_completion/REPORT.md",
        ROOT / "experiments/yolo/gdt678_seventeen_two_hole_family_completion/REPORT.md",
        EDGE_SPECS, REFERENCE_SPECS, RIVAL_SPECS, SRC / "run.py",
    ]
    output_paths = [
        ART / "V69_9_LOCAL_ACTION_EDGES.tsv",
        ART / "V69_27_REFERENCE_CENSUS.tsv",
        ART / "V69_17_RELATION_RIVALS.tsv",
        ART / "V69_479_TOKEN_RELATION_OVERLAY.tsv",
        ART / "V69_51_LINE_RELATION_OVERLAY.tsv",
        ART / "V69_3_BOUND_SPAN_FREEZE.tsv",
        ART / "V69_RELATION_CLASS_CENSUS.tsv",
        reader_path,
        artifact_readme,
    ]
    require(all(path.is_file() for path in input_paths), "declared input missing")
    result = {
        "status": STATUS,
        "question": "Can a finite deck of already licensed local source/object carries make V68 more concrete without changing any word, span, line, page, or unresolved deictic?",
        "claim_ceiling": CLAIM_CEILING,
        "basis": {
            "pages": 36,
            "lines": 51,
            "token_positions": 479,
            "v68_clauses": 175,
            "v68_action_clauses": 83,
            "v68_nominal_blocks": 92,
            "bound_spans": 3,
            "f84_access": 0,
            "f84r_access": 0,
            "new_pages": 0,
        },
        "relations": {
            "admitted_edges": 9,
            "admitted_total": 9,
            "strong_edges": 6,
            "strong_plus_explicit_output": 6,
            "working_edges": 3,
            "working_local": 3,
            "affected_loci": len({row["locus"] for row in edge_specs}),
            "reference_positions": 27,
            "reference_positions_exhausted": 27,
            "references_with_admitted_edge": 6,
            "held_rivals": 17,
            "held_relation_rivals": 17,
            "generic_nearest_donor_rules": 0,
        },
        "freeze": {
            "token_glosses_byte_identical": 479,
            "line_translations_byte_identical": 51,
            "bound_spans_byte_identical": 3,
            "content_word_additions": 0,
            "content_word_deletions": 0,
            "content_word_reorders": 0,
            "new_word_meanings": 0,
            "changed_word_meanings": 0,
        },
        "reference_decisions": dict(sorted(expected_reference_counts.items())),
        "edge_support_tiers": dict(sorted(Counter(row["support_tier"] for row in edge_specs).items())),
        "rival_kinds": dict(sorted(Counter(row["rival_kind"] for row in rival_specs).items())),
        "inputs": {rel(path): digest(path) for path in input_paths},
        "files": {path.name: digest(path) for path in output_paths},
        "next_gap": "Use only the nine occurrence-bound V69 edges to render exact source/action microclauses; do not generalize a deictic or proximity rule and do not change the 479-word deck.",
    }
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "relations": result["relations"], "freeze": result["freeze"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
