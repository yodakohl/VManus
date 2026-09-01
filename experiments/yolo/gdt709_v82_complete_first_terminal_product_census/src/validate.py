#!/usr/bin/env python3
"""Independent GDT709 validator; deliberately does not import run.py."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt709_v82_complete_first_terminal_product_census"
SRC, ART = EXP / "src", EXP / "artifacts"
VALIDATION = ART / "VALIDATION.json"
STATUS = (
    "PASS_V82_42_WINDOWS_203_ITEMS__25_LEXICAL_FIRST_TERMINALS_"
    "22_OPERATOR_TERMINALS_9_EXPLORATORY_ENDPOINTS__0_NEW_EDGES__"
    "A048_HIGH_HOLD_ZERO_WORD_DELTA"
)
G706 = ROOT / "experiments/yolo/gdt706_v79_second_nominal_item_result_census/artifacts"
G708 = ROOT / "experiments/yolo/gdt708_v81_variable_batch_terminal_product/artifacts"
COMPLETION = ("fertig", "vollständig", "abgeschlossen")
MATERIAL = (
    "ansatz", "arzneikompositum", "auszug", "charge", "droge", "gut", "holz",
    "masse", "mazerat", "portion", "pulver", "zubereitung",
)
EXPECTED_LEXICAL = {
    "A003", "A004", "A005", "A006", "A009", "A012", "A014", "A015", "A017",
    "A024", "A027", "A028", "A029", "A032", "A036", "A041", "A043", "A047",
    "A048", "A053", "A063", "A067", "A073", "A074", "A077",
}
EXPECTED_OPERATOR = EXPECTED_LEXICAL - {"A004", "A015", "A053"}
EXPECTED_COHERENT = {"A005", "A012", "A014", "A024", "A041", "A043", "A048", "A073", "A077"}


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def require(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.checks += 1
        if actual != expected:
            raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def read_tsv(path: Path, audit: Audit) -> tuple[list[str], list[dict[str, str]]]:
    audit.require(path.is_file(), f"missing TSV {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields, rows = list(reader.fieldnames or []), list(reader)
    audit.require(bool(fields), f"empty header {path}")
    audit.equal(len(fields), len(set(fields)), f"unique header {path}")
    for number, row in enumerate(rows, 2):
        audit.require(None not in row, f"extra cells {path}:{number}")
        audit.equal(set(row), set(fields), f"row schema {path}:{number}")
    return fields, rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(rows: list[dict[str, str]], label: str, **wanted: str) -> dict[str, str]:
    hits = [row for row in rows if all(row.get(field) == value for field, value in wanted.items())]
    if len(hits) != 1:
        raise AssertionError(f"{label}: expected one, got {len(hits)} for {wanted}")
    return hits[0]


def validate() -> dict[str, Any]:
    a = Audit()
    paths = {
        "spec": SRC / "V82_42_FIRST_TERMINAL_SPECS.tsv",
        "actions": G706 / "V79_83_ACTION_DISPOSITIONS.tsv",
        "pairs": G706 / "V79_161_DELAYED_SEMANTIC_PAIR_UNIVERSE.tsv",
        "universe": ART / "V82_203_SEMANTIC_ITEM_UNIVERSE.tsv",
        "census": ART / "V82_42_FIRST_TERMINAL_WINDOW_CENSUS.tsv",
        "terminals": ART / "V82_30_LEXICAL_TERMINAL_MATERIAL_FIELDS.tsv",
        "endpoints": ART / "V82_9_EXPLORATORY_ENDPOINTS.tsv",
        "readers": ART / "V82_3_READER_FUNNEL.tsv",
        "focus": ART / "V82_A048_FOCUS_HOLD.tsv",
        "preservation": ART / "V82_PRESERVATION_HASHES.tsv",
    }
    loaded = {name: read_tsv(path, a)[1] for name, path in paths.items()}
    spec, actions_all, pairs = loaded["spec"], loaded["actions"], loaded["pairs"]
    universe, census = loaded["universe"], loaded["census"]
    terminals, endpoints = loaded["terminals"], loaded["endpoints"]
    readers, focus, preservation = loaded["readers"], loaded["focus"], loaded["preservation"]
    actions = [row for row in actions_all if row["disposition"] == "DELAYED_NOMINAL_WINDOW"]

    a.equal((len(spec), len(actions), len(pairs)), (42, 42, 161), "source population")
    a.equal((len(universe), len(census), len(terminals), len(endpoints)), (203, 42, 30, 9), "output population")
    a.equal((len(readers), len(focus), len(preservation)), (3, 1, 6), "compact artifact population")
    a.equal(len({row["action_case_id"] for row in spec}), 42, "unique spec cases")
    a.equal({row["action_case_id"] for row in actions}, {row["action_case_id"] for row in spec}, "source/spec cases")
    a.equal([row["semantic_item_id"] for row in universe], [f"T{i:03d}" for i in range(1, 204)], "universe IDs")

    action_by_id = {row["action_case_id"]: row for row in actions}
    source_items: dict[str, list[tuple[int, int, str, str]]] = defaultdict(list)
    for row in actions:
        source_items[row["action_case_id"]].append((
            1, int(row["right_first_ordinal"]), row["right_first_surface"], row["right_first_gloss_de"]
        ))
    for row in pairs:
        source_items[row["action_case_id"]].append((
            int(row["target_rank"]), int(row["target_ordinal"]), row["target_surface"], row["target_gloss_de"]
        ))
    a.equal(sum(len(items) for items in source_items.values()), 203, "source semantic items")

    output_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in universe:
        output_by_id[row["action_case_id"]].append(row)
        a.equal(row["status"], STATUS, f"universe status {row['semantic_item_id']}")
        a.equal((row["word_delta"], row["page"].startswith("f84"), row["locus"].startswith("f84")),
                ("0", False, False), f"universe scope {row['semantic_item_id']}")

    recomputed_first: dict[str, int] = {}
    recomputed_terminals = 0
    recomputed_completion = 0
    nonmaterial_controls: list[tuple[str, int]] = []
    for action_id, source in source_items.items():
        source.sort()
        a.equal([item[0] for item in source], list(range(1, len(source) + 1)), f"rank continuity {action_id}")
        a.equal([item[1] for item in source], sorted(item[1] for item in source), f"ordinal order {action_id}")
        a.equal(len(source), int(action_by_id[action_id]["nominal_semantic_item_count"]), f"item count {action_id}")
        observed = sorted(output_by_id[action_id], key=lambda row: int(row["rank"]))
        a.equal([(int(r["rank"]), int(r["ordinal"]), r["surface"], r["gloss_de"]) for r in observed], source,
                f"universe source parity {action_id}")
        hits = []
        for row in observed:
            gloss = row["gloss_de"].lower()
            completion = [stem for stem in COMPLETION if stem in gloss]
            material = [head for head in MATERIAL if head in gloss]
            expected_terminal = int(bool(completion and material))
            recomputed_completion += int(bool(completion))
            recomputed_terminals += expected_terminal
            a.equal(row["completion_stems"], "|".join(completion) if completion else "NONE", f"completion marker {action_id} r{row['rank']}")
            a.equal(row["material_heads"], "|".join(material) if material else "NONE", f"material marker {action_id} r{row['rank']}")
            a.equal(int(row["lexical_terminal_material"]), expected_terminal, f"terminal marker {action_id} r{row['rank']}")
            if completion and not material:
                nonmaterial_controls.append((action_id, int(row["rank"])))
            if expected_terminal:
                hits.append(int(row["rank"]))
        if hits:
            recomputed_first[action_id] = min(hits)
        for row in observed:
            rank = int(row["rank"])
            a.equal(int(row["first_lexical_terminal"]), int(rank == recomputed_first.get(action_id)), f"first marker {action_id} r{rank}")
            a.equal(int(row["later_lexical_terminal_blocked"]), int(bool(hits) and rank in hits[1:]), f"later block {action_id} r{rank}")

    a.equal((recomputed_completion, recomputed_terminals), (32, 30), "completion and terminal totals")
    a.equal(set(recomputed_first), EXPECTED_LEXICAL, "25 lexical windows")
    a.equal(Counter(recomputed_first.values()), Counter({2: 9, 1: 5, 4: 4, 3: 3, 8: 2, 6: 1, 9: 1}), "first rank distribution")
    a.equal(nonmaterial_controls, [("A038", 2), ("A070", 6)], "hard nonmaterial controls")
    a.equal(sum(int(row["later_lexical_terminal_blocked"]) for row in universe), 5, "five later hits")
    a.equal({row["action_case_id"] for row in census if row["operator_terminal_rank"] != "NONE"}, EXPECTED_OPERATOR, "22 operator windows")
    a.equal({row["action_case_id"] for row in endpoints}, EXPECTED_COHERENT, "nine coherent windows")

    a.equal(Counter(row["path_class"] for row in census), Counter({
        "LOCALLY_READABLE_PRODUCT_ENDPOINT": 9, "EARLIER_COMPLETION_BLOCKS_LONGER": 7,
        "RESET_OR_BREAK_BEFORE_ATTRACTION": 12, "NO_COHERENT_PRODUCT_PATH": 13,
        "COHERENT_NONFINISHED_RESULT_STATE": 1,
    }), "path partition")
    a.equal(Counter(row["strict_decision"] for row in census), Counter({
        "STOP": 34, "HOLD": 6, "ADMIT_EXISTING_C019": 1, "ADMIT_EXISTING_C021": 1,
    }), "strict decisions")
    a.equal(sum(int(row["new_relation_edge"]) for row in census), 0, "zero new edges")
    a.equal(sum(int(row["operator_matches_lexical_first"]) for row in census), 21, "21 same-field operator hits")
    a.equal([row["action_case_id"] for row in census if row["operator_terminal_rank"] != "NONE" and row["operator_matches_lexical_first"] == "0"], ["A047"], "A047 later-field operator exception")
    a.require(all(row["prior_shorter_holds_preserved"] == "1" for row in census), "shorter holds preserved")
    a.require(all(row["portable_default"] == "NO" and row["word_delta"] == "0" for row in census), "zero portable/word delta")

    a048 = one(census, "A048 census", action_case_id="A048")
    a.equal((a048["locus"], a048["lexical_first_terminal_rank"], a048["operator_terminal_rank"],
             a048["best_endpoint_ranks"], a048["strict_decision"], a048["exploratory_decision"]),
            ("f77r.38", "2", "2", "1|2", "STOP", "HIGH_HOLD_NEW_FOCUS"), "A048 decisions")
    a.equal((a048["item_surfaces"], a048["best_endpoint_ordinals"]), ("qokaiin|chcphey", "4|5"), "A048 items")
    a.require("Endportion" in a048["practical_reading_de"] and "Arzneikompositum" in a048["practical_reading_de"], "A048 concrete reading")
    a.equal(sum(int(row["blocker_inside_selected_endpoint"]) for row in endpoints), 4, "four endpoint-terminal mismatches")
    a.equal({row["action_case_id"] for row in endpoints if row["blocker_inside_selected_endpoint"] == "1"}, {"A005", "A014", "A041", "A048"}, "endpoint-terminal mismatch cases")
    a.equal((focus[0]["decision"], focus[0]["surface_default_licensed"], focus[0]["word_delta"]),
            ("HIGH_HOLD_NO_EDGE", "NO", "0"), "A048 focus ceiling")
    a.equal(one(census, "C019", action_case_id="A077")["strict_decision"], "ADMIT_EXISTING_C019", "C019 replay")
    a.equal(one(census, "C021", action_case_id="A012")["strict_decision"], "ADMIT_EXISTING_C021", "C021 replay")
    a.equal((one(census, "C020", action_case_id="A083")["path_class"],
             one(census, "C020", action_case_id="A083")["operator_terminal_rank"]),
            ("COHERENT_NONFINISHED_RESULT_STATE", "NONE"), "C020 nonterminal preservation")

    a.equal([int(row["selected_windows"]) for row in readers], [25, 22, 9], "reader funnel counts")
    for row, expected in zip(readers, (EXPECTED_LEXICAL, EXPECTED_OPERATOR, EXPECTED_COHERENT)):
        a.equal(set(row["selected_case_ids"].split("|")), expected, f"reader cases {row['reader_id']}")

    base_expected = {
        "EDGE_MEMBERSHIP": (G708 / "V81_20_EDGE_COMPONENT_MEMBERSHIP.tsv", 20),
        "CONNECTED_COMPONENTS": (G708 / "V81_14_CONNECTED_COMPONENTS.tsv", 14),
        "POSITION_ROLES": (G708 / "V81_45_COMPONENT_POSITION_ROLES.tsv", 45),
        "TOKEN_OVERLAY": (G708 / "V81_479_TOKEN_RELATION_OVERLAY.tsv", 479),
        "LINE_OVERLAY": (G708 / "V81_51_LINE_RELATION_OVERLAY.tsv", 51),
        "BOUND_SPANS": (G708 / "V81_3_BOUND_SPAN_FREEZE.tsv", 3),
    }
    for row in preservation:
        path, count = base_expected[row["artifact_class"]]
        a.equal((row["source_path"], int(row["row_count"]), row["sha256"], row["preservation"]),
                (str(path.relative_to(ROOT)), count, sha256(path), "BYTE_SOURCE_UNCHANGED_NO_V82_DELTA"),
                f"preservation {row['artifact_class']}")

    token_rows = read_tsv(G708 / "V81_479_TOKEN_RELATION_OVERLAY.tsv", a)[1]
    a.equal(sum(row["surface"] == "qoeedy" for row in token_rows), 1, "qoeedy singleton")
    a.require(all(not row["page"].startswith("f84") for row in token_rows), "base token f84-free")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    a.equal(result["status"], STATUS, "result status")
    a.equal((result["basis"]["delayed_windows"], result["basis"]["semantic_items"],
             result["basis"]["lexical_first_terminal_windows"], result["basis"]["operator_terminal_windows"],
             result["basis"]["exploratory_endpoint_windows"], result["basis"]["new_relation_edges"]),
            (42, 203, 25, 22, 9, 0), "result core counts")
    a.equal((result["graph"]["relation_edges"], result["graph"]["connected_components"],
             result["graph"]["edge_nodes"], result["graph"]["delta"]), (20, 14, 37, 0), "result graph")
    a.equal((result["basis"]["f84_access"], result["basis"]["f84r_access"], result["basis"]["new_words"]), (0, 0, 0), "result scope")
    a.equal(result["provenance"]["actions_sha256"], sha256(paths["actions"]), "action provenance")
    a.equal(result["provenance"]["pairs_sha256"], sha256(paths["pairs"]), "pair provenance")
    a.equal(result["provenance"]["spec_sha256"], sha256(paths["spec"]), "spec provenance")

    reader_text = (ART / "GDT709_V82_COMPLETE_TERMINAL_READER.md").read_text(encoding="utf-8")
    for action_id in sorted(EXPECTED_COHERENT):
        a.require(f"**{action_id} /" in reader_text, f"reader endpoint {action_id}")
    a.require("Endportion hinzugeben" in reader_text and "A048 focus" in reader_text, "reader A048")
    for doc in (EXP / "README.md", EXP / "METHOD.md", EXP / "REPORT.md", ART / "README.md"):
        text = doc.read_text(encoding="utf-8")
        a.require("TODO" not in text and "REGISTERED_UNSCORED" not in text, f"finished doc {doc.name}")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    a.equal((manifest["experiment_id"], manifest["status"], manifest["sealed_data"]),
            ("GDT709", STATUS, {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}), "manifest identity")
    for entry in manifest["inputs"] + manifest["outputs"]:
        path = ROOT / entry["path"]
        a.require(path.is_file(), f"manifest file {entry['path']}")
        a.equal(sha256(path), entry["sha256"], f"manifest hash {entry['path']}")

    return {
        "status": STATUS, "checks": a.checks, "delayed_windows": len(census),
        "semantic_items": len(universe), "lexical_terminal_material_fields": len(terminals),
        "lexical_first_terminal_windows": len(EXPECTED_LEXICAL),
        "operator_terminal_windows": len(EXPECTED_OPERATOR),
        "exploratory_endpoint_windows": len(endpoints), "new_relation_edges": 0,
        "relation_edges_preserved": 20, "components_preserved": 14,
        "token_glosses_preserved": 479, "line_translations_preserved": 51,
        "bound_spans_preserved": 3, "new_word_meanings": 0, "f84_access": 0, "f84r_access": 0,
    }


def main() -> int:
    result = validate()
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
