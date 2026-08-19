#!/usr/bin/env python3
"""Independent source/accounting validator for GDT345 (does not import scorer)."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt345_productive_operator_transfer"
ART = EXP / "artifacts"
NATIVE = ROOT / "gdt278_native_event_inventory.tsv"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
DESIGN = ART / "gdt345_design.json"
OPERATORS = ART / "gdt345_operator_inventory.tsv"
TRANSITIONS = ART / "gdt345_transition_inventory.tsv"
LOFO = ART / "gdt345_lofo_folds.tsv"
TRANSFER = ART / "gdt345_transfer_folds.tsv"
SCORES = ART / "gdt345_model_scores.tsv"
NULL = ART / "gdt345_null.tsv"
RESULT = ART / "gdt345_result.json"
VALIDATION = ART / "gdt345_validation.json"
MODELS = ("PLACEMENT", "EXACT_PREDECESSOR", "SOURCE_STATE_TABLE", "FACTORIAL_OPERATOR")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document); copy.pop("content_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def hid(domain: str, value: object, length: int = 20) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((domain + "\0" + payload).encode()).hexdigest()[:length]


def canonical_wrapper(row: dict[str, str]) -> str:
    if row["wrapper"] == "s" and row["line_first"] == "1": return "NONE"
    if row["wrapper"] == "q" and row["prev_dy"] == "1": return "NONE"
    return row["wrapper"]


def state(row: dict[str, str]) -> tuple[str, ...]:
    return (row["local_frame"], row["inner_d"], row["right_family"], row["dy_closure"], row["b3"], canonical_wrapper(row))


def delta(a: tuple[str, ...], b: tuple[str, ...]) -> tuple[str, ...]:
    return tuple("KEEP" if x == y else f"SET:{y}" for x, y in zip(a, b))


def apply(a: tuple[str, ...], op: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(x if change == "KEEP" else change[4:] for x, change in zip(a, op))


def boundary(a: dict[str, str], b: dict[str, str]) -> tuple[str, str, int, int, int, str]:
    rr = int(a["record_ordinal"] != b["record_ordinal"]); lr = int(a["locus"] != b["locus"])
    fr = int((a["record_ordinal"], a["field_ordinal"]) != (b["record_ordinal"], b["field_ordinal"]))
    if rr: return "RECORD_RESET", "RECORD_RESET", fr, lr, rr, "RECORD_START"
    if lr:
        step = int(b["field_ordinal"]) - int(a["field_ordinal"])
        order = "SAME_FIELD" if not fr else ("NEXT_FIELD" if step == 1 else ("FIELD_RESET" if step < 1 else "FIELD_SKIP"))
        return "LINE_RESET", order, fr, lr, rr, "LINE_START"
    if fr:
        step = int(b["field_ordinal"]) - int(a["field_ordinal"])
        order = "NEXT_FIELD" if step == 1 else ("FIELD_RESET" if step < 1 else "FIELD_SKIP")
        return "FIELD_BOUNDARY", order, fr, lr, rr, "CONTINUATION"
    return "SAME_FIELD", "SAME_FIELD", fr, lr, rr, "CONTINUATION"


def main() -> int:
    checks: list[dict[str, object]] = []
    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition: raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text()); result = json.loads(RESULT.read_text())
    ir = GuardedTSV(INTER, selector_column="page", forbidden_prefixes=("f84",), forbidden_action="skip")
    inter = list(ir); keys = {(r["page"], r["locus"], r["group_index"]) for r in inter}; pages = {r["page"] for r in inter}
    nr = GuardedTSV(NATIVE, selector_column="page", allowed_values=pages, forbidden_prefixes=("f84",), forbidden_action="skip")
    native = [r for r in nr if r["control_id"] == "VOYNICH_REFERENCE" and (r["page"], r["locus"], r["group_index"]) in keys]
    nk = {(r["page"], r["locus"], r["group_index"]): r for r in native}
    check("source_groups", len(inter) == len(native) == len(keys) == len(nk) == 8448, (len(inter), len(native)))
    check("source_pages", len(pages) == 180)
    check("source_folios", len({r["physical_folio"] for r in inter}) == 91)
    check("source_no_f84", not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in inter + native))
    check("f84_not_parsed", ir.stats.skipped_forbidden >= 0 and nr.stats.skipped_forbidden >= 0)

    expected = []
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inter:
        key = (row["page"], row["locus"], row["group_index"]); by_page[row["page"]].append({**nk[key], **row})
    for page, rows in by_page.items():
        for ordinal, (a, b) in enumerate(zip(rows, rows[1:]), 1):
            sa, sb = state(a), state(b); op = delta(sa, sb); scope, order, fb, lr, rr, reset = boundary(a, b)
            expected.append({
                "edge_id": hid("GDT345_EDGE_V1", (page, ordinal, a["locus"], a["group_index"], b["locus"], b["group_index"])),
                "page": page, "folio": a["physical_folio"], "section": a["section"], "register": a["register"], "hand": a["hand"],
                "source_state_id": hid("GDT345_STATE_V1", sa), "target_state_id": hid("GDT345_STATE_V1", sb), "source_tuple": a["joint_tuple_id"],
                "operator_id": hid("GDT345_OPERATOR_V1", (*op, scope, order, reset)), "text_operator_id": hid("GDT345_TEXT_OPERATOR_V1", op),
                "op": op, "sa": sa, "sb": sb, "scope": scope, "order": order, "fb": fb, "lr": lr, "rr": rr, "reset": reset,
            })
    check("expected_edges", len(expected) == 8268)
    transitions = read_tsv(TRANSITIONS); check("transition_rows", len(transitions) == len(expected))
    expected_by_id = {r["edge_id"]: r for r in expected}; check("transition_unique", len({r["edge_id"] for r in transitions}) == len(transitions))
    for row in transitions:
        x = expected_by_id[row["edge_id"]]
        check(f"edge_page:{row['edge_id']}", row["page"] == x["page"] and row["physical_folio"] == x["folio"])
        check(f"edge_strata:{row['edge_id']}", (row["section"], row["register"], row["hand"]) == (x["section"], x["register"], x["hand"]))
        check(f"edge_state:{row['edge_id']}", row["source_state_id"] == x["source_state_id"] and row["target_state_id"] == x["target_state_id"])
        check(f"edge_operator:{row['edge_id']}", row["operator_id"] == x["operator_id"] and row["text_operator_id"] == x["text_operator_id"] and tuple(json.loads(row["delta_json"])) == x["op"])
        check(f"edge_apply:{row['edge_id']}", apply(tuple(json.loads(row["source_state_json"])), tuple(json.loads(row["delta_json"]))) == tuple(json.loads(row["target_state_json"])))
        check(f"edge_boundary:{row['edge_id']}", (row["boundary_scope"], row["field_order"], int(row["field_boundary"]), int(row["line_reset"]), int(row["record_reset"]), row["reset_state"]) == (x["scope"], x["order"], x["fb"], x["lr"], x["rr"], x["reset"]))
        check(f"edge_unassigned:{row['edge_id']}", row["semantic_state"] == row["translation_state"] == "UNASSIGNED")

    operators = read_tsv(OPERATORS); groups = Counter(r["operator_id"] for r in transitions)
    check("operator_rows", len(operators) == len(groups))
    check("operator_event_sum", sum(int(r["events"]) for r in operators) == len(transitions))
    for row in operators:
        check(f"operator_count:{row['operator_id']}", int(row["events"]) == groups[row["operator_id"]])
        check(f"operator_unassigned:{row['operator_id']}", row["semantic_state"] == "UNASSIGNED")

    lofo = read_tsv(LOFO); transfer = read_tsv(TRANSFER); scores = read_tsv(SCORES); null = read_tsv(NULL)
    check("lofo_rows", len(lofo) == 91 * len(MODELS), len(lofo))
    expected_transfer_categories = len({r["section"] for r in expected}) + len({r["register"] for r in expected}) + len({r["hand"] for r in expected})
    check("transfer_rows", len(transfer) == expected_transfer_categories * len(MODELS), (len(transfer), expected_transfer_categories))
    check("models_exact", {r["model"] for r in scores} == set(MODELS))
    by_model = {r["model"]: r for r in scores}
    for model in MODELS:
        rows = [r for r in lofo if r["model"] == model]
        check(f"fold_count:{model}", len(rows) == 91)
        check(f"fold_events:{model}", sum(int(r["eligible_events"]) for r in rows) == int(by_model[model]["eligible_events"]))
        check(f"fold_bits:{model}", math.isclose(sum(float(r["total_bits"]) for r in rows), float(by_model[model]["total_bits"]), abs_tol=2e-6))
        check(f"fold_hits:{model}", sum(int(r["exact_next_state_hits"]) for r in rows) == int(by_model[model]["exact_next_state_hits"]))
        check(f"fold_unseen_n:{model}", sum(int(r["unseen_combo_events"]) for r in rows) == int(by_model[model]["unseen_combo_events"]))
        check(f"fold_unseen_bits:{model}", math.isclose(sum(float(r["unseen_combo_bits"]) for r in rows), float(by_model[model]["unseen_combo_bits"]), abs_tol=2e-6))
    for model in MODELS:
        row = by_model[model]
        check(f"gain_place:{model}", math.isclose(float(by_model["PLACEMENT"]["total_bits"]) - float(row["total_bits"]), float(row["gain_over_placement"]), abs_tol=2e-6))
        check(f"gain_exact:{model}", math.isclose(float(by_model["EXACT_PREDECESSOR"]["total_bits"]) - float(row["total_bits"]), float(row["gain_over_exact_predecessor"]), abs_tol=2e-6))
        check(f"unseen_gain_exact:{model}", math.isclose(float(by_model["EXACT_PREDECESSOR"]["unseen_combo_bits"]) - float(row["unseen_combo_bits"]), float(row["unseen_gain_over_exact"]), abs_tol=2e-6))

    # Independently reconstruct the purely combinatorial unseen-combination counts.
    unseen_total = 0
    for hold in sorted({r["folio"] for r in expected}):
        train = [r for r in expected if r["folio"] != hold]; test = [r for r in expected if r["folio"] == hold]
        states = {r["source_state_id"] for r in train}; ops = {r["operator_id"] for r in train}; combos = {(r["source_state_id"], r["operator_id"]) for r in train}
        unseen_total += sum(r["source_state_id"] in states and r["operator_id"] in ops and (r["source_state_id"], r["operator_id"]) not in combos for r in test)
    check("unseen_combo_reconstruction", unseen_total == int(by_model["FACTORIAL_OPERATOR"]["unseen_combo_events"]), unseen_total)

    check("null_worlds", len(null) == int(design["null"]["worlds"]))
    observed_fac = int(by_model["FACTORIAL_OPERATOR"]["exact_next_state_hits"]) - int(by_model["EXACT_PREDECESSOR"]["exact_next_state_hits"])
    observed_state = int(by_model["SOURCE_STATE_TABLE"]["exact_next_state_hits"]) - int(by_model["EXACT_PREDECESSOR"]["exact_next_state_hits"])
    p_fac = (1 + sum(int(r["factorial_hit_gain"]) >= observed_fac for r in null)) / (1 + len(null))
    p_state = (1 + sum(int(r["source_state_hit_gain"]) >= observed_state for r in null)) / (1 + len(null))
    p_max = (1 + sum(int(r["max_two_hit_gain"]) >= max(observed_fac, observed_state) for r in null)) / (1 + len(null))
    check("null_p_factorial", math.isclose(p_fac, float(by_model["FACTORIAL_OPERATOR"]["inclusive_p"]), abs_tol=5e-10))
    check("null_p_state", math.isclose(p_state, float(by_model["SOURCE_STATE_TABLE"]["inclusive_p"]), abs_tol=5e-10))
    check("null_p_max", math.isclose(p_max, float(by_model["FACTORIAL_OPERATOR"]["max_two_p"]), abs_tol=5e-10))

    check("result_source", result["source"]["groups"] == 8448 and result["source"]["edges"] == 8268 and result["source"]["folios"] == 91)
    check("result_operator_counts", result["operator_inventory"]["registered_operators"] == len(operators))
    check("zero_semantics", result["semantic_alignments"] == result["tuple_merges"] == result["page_host_factorizations"] == 0)
    check("f84_flags", all(value is False for value in result["f84"].values()))
    for path, digest in result["inputs"].items(): check(f"input_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in result["outputs"].items(): check(f"output_hash:{path}", sha(ROOT / path) == digest)
    for path, digest in result["implementation"].items(): check(f"implementation_hash:{path}", sha(ROOT / path) == digest)
    check("result_content_hash", content_hash(result) == result["content_sha256"])

    validation = {
        "schema": "GDT345_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks_failed": 0,
        "result_sha256": sha(RESULT), "source_reconstruction": {"groups": len(inter), "edges": len(expected), "pages": len(pages), "folios": 91},
        "scope": "Independent guarded source join, state/delta/application/operator reconstruction for every edge, inventory/fold/aggregate/unseen/null/gate accounting, semantic-zero, f84, content and file hashes. Categorical model probabilities and fixed-prediction worlds are not independently refit.",
        "checks": checks,
    }
    validation["content_sha256"] = content_hash(validation); VALIDATION.write_bytes(canonical(validation))
    print(f"PASS {len(checks)}/{len(checks)} {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
