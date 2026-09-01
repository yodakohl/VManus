#!/usr/bin/env python3
"""Build GDT709's exhaustive three-reader first-terminal-product census."""

from __future__ import annotations

import csv
import hashlib
import json
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
EXP = ROOT / "experiments/yolo/gdt709_v82_complete_first_terminal_product_census"
SRC, ART = EXP / "src", EXP / "artifacts"
STATUS = (
    "PASS_V82_42_WINDOWS_203_ITEMS__25_LEXICAL_FIRST_TERMINALS_"
    "22_OPERATOR_TERMINALS_9_EXPLORATORY_ENDPOINTS__0_NEW_EDGES__"
    "A048_HIGH_HOLD_ZERO_WORD_DELTA"
)
QUESTION = (
    "When every semantic item in all 42 delayed nominal windows is inspected without skipping, "
    "how many first terminal products survive a compound-aware lexical marker, an operational "
    "apothecary reading, and a complete manual patient/path reading?"
)
CLAIM = (
    "V82 exhausts all 42 delayed windows and all 203 semantic items. A reproducible broad marker "
    "finds 25 first terminal-material windows, an operational reader recognizes 22, and complete "
    "manual reading retains nine locally readable exploratory endpoints. Only the already admitted C019 and C021 "
    "remain edges. A048 is the strongest new exploratory hold, not a word value or graph edge. "
    "No earlier short hold is erased by a longer-path STOP."
)
NEXT_GAP = (
    "Apply one deterministic preterminal-reset gate to the 25 broad first hits: stop at the first "
    "material, operation or degree reset; require exact action material and degree recurrence plus "
    "productive licensing of the new terminal state. Use C021 as positive anchor, inherited C019 "
    "as the carrier-bundle special case, and A048 as the named negative/high-hold anchor."
)

G706 = ROOT / "experiments/yolo/gdt706_v79_second_nominal_item_result_census/artifacts"
ACTIONS = G706 / "V79_83_ACTION_DISPOSITIONS.tsv"
PAIRS = G706 / "V79_161_DELAYED_SEMANTIC_PAIR_UNIVERSE.tsv"
G708 = ROOT / "experiments/yolo/gdt708_v81_variable_batch_terminal_product/artifacts"
BASE_RESULT = G708 / "RESULT.json"
BASE_FILES = {
    "EDGE_MEMBERSHIP": G708 / "V81_20_EDGE_COMPONENT_MEMBERSHIP.tsv",
    "CONNECTED_COMPONENTS": G708 / "V81_14_CONNECTED_COMPONENTS.tsv",
    "POSITION_ROLES": G708 / "V81_45_COMPONENT_POSITION_ROLES.tsv",
    "TOKEN_OVERLAY": G708 / "V81_479_TOKEN_RELATION_OVERLAY.tsv",
    "LINE_OVERLAY": G708 / "V81_51_LINE_RELATION_OVERLAY.tsv",
    "BOUND_SPANS": G708 / "V81_3_BOUND_SPAN_FREEZE.tsv",
}
SPEC = SRC / "V82_42_FIRST_TERMINAL_SPECS.tsv"

UNIVERSE_OUT = ART / "V82_203_SEMANTIC_ITEM_UNIVERSE.tsv"
CENSUS_OUT = ART / "V82_42_FIRST_TERMINAL_WINDOW_CENSUS.tsv"
TERMINALS_OUT = ART / "V82_30_LEXICAL_TERMINAL_MATERIAL_FIELDS.tsv"
ENDPOINTS_OUT = ART / "V82_9_EXPLORATORY_ENDPOINTS.tsv"
READERS_OUT = ART / "V82_3_READER_FUNNEL.tsv"
FOCUS_OUT = ART / "V82_A048_FOCUS_HOLD.tsv"
PRESERVATION_OUT = ART / "V82_PRESERVATION_HASHES.tsv"
READER_OUT = ART / "GDT709_V82_COMPLETE_TERMINAL_READER.md"
RESULT_OUT = ART / "RESULT.json"

COMPLETION_STEMS = ("fertig", "vollständig", "abgeschlossen")
MATERIAL_HEADS = (
    "ansatz", "arzneikompositum", "auszug", "charge", "droge", "gut", "holz",
    "masse", "mazerat", "portion", "pulver", "zubereitung",
)

SPEC_FIELDS = [
    "action_case_id", "path_class", "best_endpoint_ranks", "explicit_terminal_rank",
    "strict_decision", "exploratory_decision", "first_blocker_rank", "first_blocker_class",
    "practical_reading_de", "decision_reason_de", "portable_default",
]
UNIVERSE_FIELDS = [
    "semantic_item_id", "action_case_id", "page", "locus", "action_ordinal",
    "action_surface", "action_gloss_de", "rank", "ordinal", "surface", "gloss_de",
    "completion_stems", "material_heads", "lexical_terminal_material",
    "first_lexical_terminal", "later_lexical_terminal_blocked", "operator_terminal",
    "manual_endpoint_member", "path_class", "strict_decision", "exploratory_decision",
    "word_delta", "status",
]
CENSUS_FIELDS = [
    "action_case_id", "page", "locus", "action_ordinal", "action_surface", "action_gloss_de",
    "semantic_item_count", "item_ranks", "item_ordinals", "item_surfaces", "item_glosses_de",
    "lexical_first_terminal_rank", "lexical_first_terminal_ordinal",
    "lexical_first_terminal_surface", "lexical_first_terminal_gloss_de",
    "lexical_terminal_field_count", "later_lexical_terminal_ranks_blocked",
    "operator_terminal_rank", "operator_terminal_ordinal", "operator_terminal_surface",
    "operator_terminal_gloss_de", "operator_matches_lexical_first", "path_class", "best_endpoint_ranks",
    "best_endpoint_ordinals", "best_endpoint_surfaces", "best_endpoint_glosses_de",
    "strict_decision", "exploratory_decision", "first_blocker_rank", "first_blocker_ordinal",
    "first_blocker_surface", "first_blocker_gloss_de", "first_blocker_class",
    "blocker_inside_selected_endpoint",
    "practical_reading_de", "decision_reason_de", "prior_shorter_holds_preserved",
    "portable_default", "new_relation_edge", "word_delta", "status",
]
TERMINAL_FIELDS = [
    "terminal_field_id", "action_case_id", "page", "locus", "rank", "ordinal", "surface",
    "gloss_de", "completion_stems", "material_heads", "first_in_window",
    "blocked_by_earlier_terminal", "operator_terminal", "manual_endpoint_member",
    "path_class", "strict_decision", "exploratory_decision", "new_relation_edge", "status",
]
ENDPOINT_FIELDS = [
    "endpoint_id", "action_case_id", "page", "locus", "action_ordinal", "action_surface",
    "action_gloss_de", "selected_ranks", "selected_ordinals", "selected_surfaces",
    "selected_glosses_de", "strict_decision", "exploratory_decision", "relation_edge_id",
    "practical_reading_de", "decision_reason_de", "blocker_inside_selected_endpoint",
    "portable_default", "status",
]
READER_FIELDS = [
    "reader_id", "reader_background", "selection_rule", "selected_windows", "selected_case_ids",
    "exclusion_rule", "interpretive_role", "status",
]
FOCUS_FIELDS = [
    "action_case_id", "locus", "action_ordinal", "action_surface", "action_gloss_de",
    "attribute_ordinal", "attribute_surface", "attribute_gloss_de", "terminal_ordinal",
    "terminal_surface", "terminal_gloss_de", "working_reading_de", "why_attractive_de",
    "why_not_edge_de", "next_test", "decision", "surface_default_licensed", "word_delta", "status",
]
PRESERVATION_FIELDS = [
    "artifact_class", "source_path", "row_count", "sha256", "preservation", "status",
]


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    assert fields and len(fields) == len(set(fields)), path
    assert all(None not in row and set(row) == set(fields) for row in rows), path
    return fields, rows


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def pipe(values: Sequence[object]) -> str:
    clean = [str(value) for value in values if value not in (None, "", "NONE")]
    return "|".join(clean) if clean else "NONE"


def ranks(value: str) -> list[int]:
    return [] if value == "NONE" else [int(part) for part in value.split("|")]


def manifest_entry(path: Path, role: str) -> dict[str, str]:
    return {"path": rel(path), "role": role, "sha256": sha256(path)}


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    spec_fields, specs = read_tsv(SPEC)
    _, action_rows = read_tsv(ACTIONS)
    _, pair_rows = read_tsv(PAIRS)
    assert spec_fields == SPEC_FIELDS and len(specs) == 42
    assert len({row["action_case_id"] for row in specs}) == 42
    assert all(row["portable_default"] == "NO" for row in specs)

    actions = [row for row in action_rows if row["disposition"] == "DELAYED_NOMINAL_WINDOW"]
    assert len(actions) == 42
    action_by_id = {row["action_case_id"]: row for row in actions}
    spec_by_id = {row["action_case_id"]: row for row in specs}
    assert set(action_by_id) == set(spec_by_id)
    pairs_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in pair_rows:
        pairs_by_id[row["action_case_id"]].append(row)
    assert len(pair_rows) == 161

    items_by_id: dict[str, list[dict[str, object]]] = {}
    all_items: list[dict[str, object]] = []
    for action in actions:
        action_id = action["action_case_id"]
        items: list[dict[str, object]] = [{
            "rank": 1, "ordinal": int(action["right_first_ordinal"]),
            "surface": action["right_first_surface"], "gloss_de": action["right_first_gloss_de"],
        }]
        for pair in sorted(pairs_by_id[action_id], key=lambda row: int(row["target_rank"])):
            items.append({
                "rank": int(pair["target_rank"]), "ordinal": int(pair["target_ordinal"]),
                "surface": pair["target_surface"], "gloss_de": pair["target_gloss_de"],
            })
        assert [item["rank"] for item in items] == list(range(1, len(items) + 1))
        assert [item["ordinal"] for item in items] == sorted(item["ordinal"] for item in items)
        assert len(items) == int(action["nominal_semantic_item_count"])
        for item in items:
            gloss = str(item["gloss_de"]).lower()
            item["completion_stems"] = pipe([stem for stem in COMPLETION_STEMS if stem in gloss])
            item["material_heads"] = pipe([head for head in MATERIAL_HEADS if head in gloss])
            item["lexical_terminal_material"] = int(
                item["completion_stems"] != "NONE" and item["material_heads"] != "NONE"
            )
        items_by_id[action_id] = items
        all_items.extend(items)
    assert len(all_items) == 203

    census_rows: list[dict[str, object]] = []
    universe_rows: list[dict[str, object]] = []
    terminal_rows: list[dict[str, object]] = []
    endpoint_rows: list[dict[str, object]] = []
    for action in actions:
        action_id = action["action_case_id"]
        spec = spec_by_id[action_id]
        items = items_by_id[action_id]
        by_rank = {int(item["rank"]): item for item in items}
        lexical = [item for item in items if item["lexical_terminal_material"]]
        first_lexical = lexical[0] if lexical else None
        operator_rank = None if spec["explicit_terminal_rank"] == "NONE" else int(spec["explicit_terminal_rank"])
        operator = by_rank.get(operator_rank) if operator_rank is not None else None
        selected_ranks = ranks(spec["best_endpoint_ranks"])
        selected = [by_rank[rank] for rank in selected_ranks]
        blocker_rank = None if spec["first_blocker_rank"] == "NONE" else int(spec["first_blocker_rank"])
        blocker = by_rank.get(blocker_rank) if blocker_rank is not None else None
        assert operator_rank is None or operator is not None
        assert blocker_rank is None or blocker is not None

        for item in items:
            first_flag = int(first_lexical is item)
            later_blocked = int(bool(item["lexical_terminal_material"]) and first_lexical is not item)
            universe_rows.append({
                "semantic_item_id": f"T{len(universe_rows) + 1:03d}", "action_case_id": action_id,
                "page": action["page"], "locus": action["locus"],
                "action_ordinal": action["action_ordinal"], "action_surface": action["action_surface"],
                "action_gloss_de": action["action_gloss_de"], "rank": item["rank"],
                "ordinal": item["ordinal"], "surface": item["surface"], "gloss_de": item["gloss_de"],
                "completion_stems": item["completion_stems"], "material_heads": item["material_heads"],
                "lexical_terminal_material": item["lexical_terminal_material"],
                "first_lexical_terminal": first_flag,
                "later_lexical_terminal_blocked": later_blocked,
                "operator_terminal": int(operator is item),
                "manual_endpoint_member": int(int(item["rank"]) in selected_ranks),
                "path_class": spec["path_class"], "strict_decision": spec["strict_decision"],
                "exploratory_decision": spec["exploratory_decision"], "word_delta": 0, "status": STATUS,
            })
            if item["lexical_terminal_material"]:
                terminal_rows.append({
                    "terminal_field_id": f"TM{len(terminal_rows) + 1:03d}",
                    "action_case_id": action_id, "page": action["page"], "locus": action["locus"],
                    "rank": item["rank"], "ordinal": item["ordinal"], "surface": item["surface"],
                    "gloss_de": item["gloss_de"], "completion_stems": item["completion_stems"],
                    "material_heads": item["material_heads"], "first_in_window": first_flag,
                    "blocked_by_earlier_terminal": later_blocked, "operator_terminal": int(operator is item),
                    "manual_endpoint_member": int(int(item["rank"]) in selected_ranks),
                    "path_class": spec["path_class"], "strict_decision": spec["strict_decision"],
                    "exploratory_decision": spec["exploratory_decision"], "new_relation_edge": 0,
                    "status": STATUS,
                })

        census_rows.append({
            "action_case_id": action_id, "page": action["page"], "locus": action["locus"],
            "action_ordinal": action["action_ordinal"], "action_surface": action["action_surface"],
            "action_gloss_de": action["action_gloss_de"], "semantic_item_count": len(items),
            "item_ranks": pipe([item["rank"] for item in items]),
            "item_ordinals": pipe([item["ordinal"] for item in items]),
            "item_surfaces": pipe([item["surface"] for item in items]),
            "item_glosses_de": pipe([item["gloss_de"] for item in items]),
            "lexical_first_terminal_rank": first_lexical["rank"] if first_lexical else "NONE",
            "lexical_first_terminal_ordinal": first_lexical["ordinal"] if first_lexical else "NONE",
            "lexical_first_terminal_surface": first_lexical["surface"] if first_lexical else "NONE",
            "lexical_first_terminal_gloss_de": first_lexical["gloss_de"] if first_lexical else "NONE",
            "lexical_terminal_field_count": len(lexical),
            "later_lexical_terminal_ranks_blocked": pipe([item["rank"] for item in lexical[1:]]),
            "operator_terminal_rank": operator["rank"] if operator else "NONE",
            "operator_terminal_ordinal": operator["ordinal"] if operator else "NONE",
            "operator_terminal_surface": operator["surface"] if operator else "NONE",
            "operator_terminal_gloss_de": operator["gloss_de"] if operator else "NONE",
            "operator_matches_lexical_first": int(operator is not None and operator is first_lexical),
            "path_class": spec["path_class"], "best_endpoint_ranks": spec["best_endpoint_ranks"],
            "best_endpoint_ordinals": pipe([item["ordinal"] for item in selected]),
            "best_endpoint_surfaces": pipe([item["surface"] for item in selected]),
            "best_endpoint_glosses_de": pipe([item["gloss_de"] for item in selected]),
            "strict_decision": spec["strict_decision"], "exploratory_decision": spec["exploratory_decision"],
            "first_blocker_rank": blocker["rank"] if blocker else "NONE",
            "first_blocker_ordinal": blocker["ordinal"] if blocker else "NONE",
            "first_blocker_surface": blocker["surface"] if blocker else "NONE",
            "first_blocker_gloss_de": blocker["gloss_de"] if blocker else "NONE",
            "first_blocker_class": spec["first_blocker_class"],
            "blocker_inside_selected_endpoint": int(blocker_rank is not None and blocker_rank in selected_ranks),
            "practical_reading_de": spec["practical_reading_de"],
            "decision_reason_de": spec["decision_reason_de"],
            "prior_shorter_holds_preserved": 1, "portable_default": spec["portable_default"],
            "new_relation_edge": 0, "word_delta": 0, "status": STATUS,
        })
        if spec["path_class"] == "LOCALLY_READABLE_PRODUCT_ENDPOINT":
            relation = {"A012": "C021", "A077": "C019"}.get(action_id, "NONE")
            endpoint_rows.append({
                "endpoint_id": f"EP{len(endpoint_rows) + 1:02d}", "action_case_id": action_id,
                "page": action["page"], "locus": action["locus"],
                "action_ordinal": action["action_ordinal"], "action_surface": action["action_surface"],
                "action_gloss_de": action["action_gloss_de"],
                "selected_ranks": spec["best_endpoint_ranks"],
                "selected_ordinals": pipe([item["ordinal"] for item in selected]),
                "selected_surfaces": pipe([item["surface"] for item in selected]),
                "selected_glosses_de": pipe([item["gloss_de"] for item in selected]),
                "strict_decision": spec["strict_decision"],
                "exploratory_decision": spec["exploratory_decision"], "relation_edge_id": relation,
                "practical_reading_de": spec["practical_reading_de"],
                "decision_reason_de": spec["decision_reason_de"],
                "blocker_inside_selected_endpoint": int(blocker_rank is not None and blocker_rank in selected_ranks),
                "portable_default": spec["portable_default"], "status": STATUS,
            })

    assert len(universe_rows) == 203
    assert Counter(row["lexical_terminal_material"] for row in universe_rows) == {0: 173, 1: 30}
    assert Counter(row["first_lexical_terminal"] for row in universe_rows) == {0: 178, 1: 25}
    assert Counter(row["later_lexical_terminal_blocked"] for row in universe_rows) == {0: 198, 1: 5}
    assert sum(row["operator_terminal"] for row in universe_rows) == 22
    assert len(census_rows) == 42 and len(terminal_rows) == 30 and len(endpoint_rows) == 9
    assert Counter(row["path_class"] for row in census_rows) == {
        "LOCALLY_READABLE_PRODUCT_ENDPOINT": 9, "EARLIER_COMPLETION_BLOCKS_LONGER": 7,
        "RESET_OR_BREAK_BEFORE_ATTRACTION": 12, "NO_COHERENT_PRODUCT_PATH": 13,
        "COHERENT_NONFINISHED_RESULT_STATE": 1,
    }
    assert Counter(row["strict_decision"] for row in census_rows) == {
        "ADMIT_EXISTING_C019": 1, "ADMIT_EXISTING_C021": 1, "HOLD": 6, "STOP": 34,
    }
    assert sum(int(row["operator_matches_lexical_first"]) for row in census_rows) == 21
    assert sum(int(row["blocker_inside_selected_endpoint"]) for row in endpoint_rows) == 4

    first_case_ids = [row["action_case_id"] for row in census_rows if row["lexical_first_terminal_rank"] != "NONE"]
    operator_case_ids = [row["action_case_id"] for row in census_rows if row["operator_terminal_rank"] != "NONE"]
    coherent_case_ids = [row["action_case_id"] for row in endpoint_rows]
    reader_rows = [
        {"reader_id": "R1_COMPOUND_MARKER", "reader_background": "reproducible compound-aware gloss marker",
         "selection_rule": "completion stem plus material-head substring; keep the first hit per window",
         "selected_windows": len(first_case_ids), "selected_case_ids": pipe(first_case_ids),
         "exclusion_rule": "state-only and quantity-only completion; every later completion in a hit window",
         "interpretive_role": "high-throughput candidate generator, never an edge decider", "status": STATUS},
        {"reader_id": "R2_APOTHECARY_FLOW", "reader_background": "historically plausible workshop-flow reader",
         "selection_rule": "explicit finished material or terminal stage in the local operational reading",
         "selected_windows": len(operator_case_ids), "selected_case_ids": pipe(operator_case_ids),
         "exclusion_rule": "mere completed heating/quantity and nonterminal process values",
         "interpretive_role": "window-level operation-aware recognition; 21 same-field first hits plus later-field A047", "status": STATUS},
        {"reader_id": "R3_COMPLETE_PATH", "reader_background": "manual patient/material/degree path reader",
         "selection_rule": "a locally readable shortest endpoint; unresolved operation/degree mismatch may occur in its terminal field",
         "selected_windows": len(coherent_case_ids), "selected_case_ids": pipe(coherent_case_ids),
         "exclusion_rule": "earlier completion blocks longer path; any reset blocks later attraction",
         "interpretive_role": "exploratory practical endpoint set, not nine blocker-free paths", "status": STATUS},
    ]

    a048 = next(row for row in census_rows if row["action_case_id"] == "A048")
    a048_items = items_by_id["A048"]
    focus_rows = [{
        "action_case_id": "A048", "locus": a048["locus"], "action_ordinal": a048["action_ordinal"],
        "action_surface": a048["action_surface"], "action_gloss_de": a048["action_gloss_de"],
        "attribute_ordinal": a048_items[0]["ordinal"], "attribute_surface": a048_items[0]["surface"],
        "attribute_gloss_de": a048_items[0]["gloss_de"],
        "terminal_ordinal": a048_items[1]["ordinal"], "terminal_surface": a048_items[1]["surface"],
        "terminal_gloss_de": a048_items[1]["gloss_de"], "working_reading_de": a048["practical_reading_de"],
        "why_attractive_de": "Kurzer vollständiger Zweierpfad; heiß III steht vor einem materialtragenden Abschlusswert; der Nominalblock endet dort.",
        "why_not_edge_de": "Hinzunehmen lizenziert weder Trocknung noch Abschluss; III wechselt zur Mittelstufe; qoeedy ist im 479-Token-Freeze ein Singleton.",
        "next_test": "PRETERMINAL_RESET_GATE_WITH_A048_NEGATIVE_ANCHOR",
        "decision": "HIGH_HOLD_NO_EDGE", "surface_default_licensed": "NO", "word_delta": 0,
        "status": STATUS,
    }]

    base_counts = {"EDGE_MEMBERSHIP": 20, "CONNECTED_COMPONENTS": 14, "POSITION_ROLES": 45,
                   "TOKEN_OVERLAY": 479, "LINE_OVERLAY": 51, "BOUND_SPANS": 3}
    preservation_rows = []
    for artifact_class, path in BASE_FILES.items():
        _, rows = read_tsv(path)
        assert len(rows) == base_counts[artifact_class]
        preservation_rows.append({
            "artifact_class": artifact_class, "source_path": rel(path), "row_count": len(rows),
            "sha256": sha256(path), "preservation": "BYTE_SOURCE_UNCHANGED_NO_V82_DELTA", "status": STATUS,
        })

    write_tsv(UNIVERSE_OUT, universe_rows, UNIVERSE_FIELDS)
    write_tsv(CENSUS_OUT, census_rows, CENSUS_FIELDS)
    write_tsv(TERMINALS_OUT, terminal_rows, TERMINAL_FIELDS)
    write_tsv(ENDPOINTS_OUT, endpoint_rows, ENDPOINT_FIELDS)
    write_tsv(READERS_OUT, reader_rows, READER_FIELDS)
    write_tsv(FOCUS_OUT, focus_rows, FOCUS_FIELDS)
    write_tsv(PRESERVATION_OUT, preservation_rows, PRESERVATION_FIELDS)

    reader_lines = [
        "# GDT709 V82 complete terminal reader", "", f"Status: `{STATUS}`", "", "## The funnel", "",
        "All 42 delayed windows and all 203 semantic items are present. The three readers are nested at window level:", "",
        "- broad compound marker: 25 first terminal-material windows;",
        "- operation-aware reader: 22 explicit terminal windows;",
        "- complete manual patient/path reader: nine locally readable exploratory endpoints;",
        "- admitted relation edges: only inherited C019 and C021.", "",
        "The broad marker also finds 30 terminal-material fields: five later fields are blocked by an earlier completion and cannot rescue a path. The 22-reader set is nested only at window level: 21 select the same first field, while A047's operational terminal is later than its first lexical completion and remains STOP.", "",
        "Four of the nine readable endpoints (A005, A014, A041, A048) carry their first unresolved mismatch in the terminal field itself. They are exploratory endpoints, not blocker-free causal paths.", "",
        "## Nine locally readable exploratory endpoints", "",
    ]
    for row in endpoint_rows:
        label = row["relation_edge_id"] if row["relation_edge_id"] != "NONE" else row["exploratory_decision"]
        reader_lines.append(f"- **{row['action_case_id']} / {row['locus']} / {label}:** {row['practical_reading_de']}")
    reader_lines.extend([
        "", "## A048 focus", "",
        "> Endportion hinzugeben; danach heiß, Grad III; mögliches terminales Produkt: abgeschlossenes, bis zur Mittelstufe getrocknetes Arzneikompositum.", "",
        "This is the strongest new practical reading because the two-item block is short, material-bearing and terminal. It remains a high hold because addition alone does not explain drying or closure, III changes to the middle degree, and the action surface is a singleton in the frozen 479-token reader.", "",
        "Long-path STOP decisions do not erase earlier short holds, C020, C019 or C021.", "",
    ])
    READER_OUT.write_text("\n".join(reader_lines), encoding="utf-8")

    base_result = json.loads(BASE_RESULT.read_text(encoding="utf-8"))
    path_counts = Counter(row["path_class"] for row in census_rows)
    strict_counts = Counter(row["strict_decision"] for row in census_rows)
    result = {
        "experiment_id": "GDT709", "status": STATUS, "question": QUESTION,
        "claim_ceiling": CLAIM, "next_gap": NEXT_GAP,
        "basis": {
            "delayed_windows": 42, "raw_nominal_positions": 205, "semantic_items": 203,
            "terminal_period_controls": 2, "completion_marked_fields": 32,
            "nonmaterial_completion_controls": 2, "lexical_terminal_material_fields": 30,
            "lexical_first_terminal_windows": 25, "later_terminal_fields_blocked": 5,
            "operator_terminal_windows": 22, "operator_same_first_field_windows": 21,
            "operator_later_field_exceptions": 1, "exploratory_endpoint_windows": 9,
            "exploratory_endpoints_with_terminal_mismatch": 4,
            "existing_edge_replays": 2, "new_relation_edges": 0, "new_components": 0,
            "new_words": 0, "new_pages": 0, "f84_access": 0, "f84r_access": 0,
            "strict_decisions": dict(sorted(strict_counts.items())),
            "path_classes": dict(sorted(path_counts.items())),
            "pages_inherited": base_result["basis"]["pages"],
            "token_positions_inherited": base_result["basis"]["token_positions"],
            "lines_inherited": base_result["basis"]["lines"], "bound_spans_inherited": 3,
        },
        "graph": {
            "relation_edges": base_result["basis"]["relation_edges_after"],
            "connected_components": base_result["basis"]["connected_components"],
            "edge_nodes": base_result["basis"]["edge_nodes"],
            "edge_node_incidences": base_result["basis"]["edge_node_incidences"],
            "minimal_hull_positions": base_result["basis"]["minimal_hull_positions"],
            "render_positions": base_result["basis"]["render_positions"],
            "shared_edge_nodes": base_result["basis"]["shared_edge_nodes"],
            "hull_only_positions": base_result["basis"]["hull_only_positions"],
            "render_only_structural_positions": base_result["basis"]["render_only_structural_positions"],
            "structural_closure_positions": base_result["basis"]["structural_closure_positions"],
            "delta": 0,
        },
        "reader_funnel": {"R1_COMPOUND_MARKER": first_case_ids,
                          "R2_APOTHECARY_FLOW": operator_case_ids,
                          "R3_COMPLETE_PATH": coherent_case_ids},
        "focus": {"case": "A048", "decision": "HIGH_HOLD_NO_EDGE",
                  "reading_de": a048["practical_reading_de"]},
        "provenance": {"actions_sha256": sha256(ACTIONS), "pairs_sha256": sha256(PAIRS),
                       "spec_sha256": sha256(SPEC), "base_result_sha256": sha256(BASE_RESULT)},
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    static_outputs = [(EXP / "METHOD.md", "three-reader exhaustive method and claim ceiling"),
                      (EXP / "README.md", "experiment entry point and concise funnel"),
                      (EXP / "REPORT.md", "primary interpretation and next route"),
                      (ART / "README.md", "artifact map")]
    generated_outputs = [(SRC / "validate.py", "independent source reconstruction scope and preservation validator"),
                         (READER_OUT, "complete practical reader and A048 focus"),
                         (RESULT_OUT, "machine counts graph preservation and next gap"),
                         (UNIVERSE_OUT, "all 203 semantic items with three-reader annotations"),
                         (CENSUS_OUT, "complete 42-window no-skip census"),
                         (TERMINALS_OUT, "all 30 broad terminal-material fields"),
                         (ENDPOINTS_OUT, "nine locally readable exploratory endpoints"),
                         (READERS_OUT, "three independent selection rules and populations"),
                         (FOCUS_OUT, "single A048 high-hold card"),
                         (PRESERVATION_OUT, "byte-source preservation hashes for the V81 graph and reader")]
    if (ART / "VALIDATION.json").is_file():
        generated_outputs.append((ART / "VALIDATION.json", "independent audit result"))
    assert all(path.is_file() for path, _ in static_outputs + generated_outputs)
    manifest = {
        "schema_version": 1, "experiment_id": "GDT709",
        "slug": "v82_complete_first_terminal_product_census",
        "title": "V82 complete first terminal product census", "created": "2026-09-01",
        "updated": "2026-09-01", "status": STATUS, "question": QUESTION,
        "claim_ceiling": CLAIM, "dependencies": ["GDT706", "GDT708"],
        "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "artifact_policy": {"max_inline_bytes": 5000000,
                            "large_artifact_justification": "The complete 203-item universe is small and proves that no delayed item was skipped."},
        "commands": {"run": "python3 experiments/yolo/gdt709_v82_complete_first_terminal_product_census/src/run.py",
                     "validate": "python3 experiments/yolo/gdt709_v82_complete_first_terminal_product_census/src/validate.py"},
        "inputs": [manifest_entry(ACTIONS, "42-window action source and first semantic item"),
                   manifest_entry(PAIRS, "all 161 rank-two-and-later semantic items"),
                   manifest_entry(BASE_RESULT, "authoritative V81 graph and preservation counts"),
                   manifest_entry(SPEC, "manual 42-window operational and coherent-path matrix"),
                   manifest_entry(SRC / "run.py", "deterministic three-reader census builder")],
        "outputs": [manifest_entry(path, role) for path, role in static_outputs + generated_outputs],
        "validation": {"status": "PASS" if (ART / "VALIDATION.json").is_file() else "NOT_RUN",
                       "artifact": rel(ART / "VALIDATION.json") if (ART / "VALIDATION.json").is_file() else None},
    }
    (EXP / "experiment.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(STATUS)
    print(json.dumps(result["basis"], ensure_ascii=False, sort_keys=True))
    print(NEXT_GAP)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
