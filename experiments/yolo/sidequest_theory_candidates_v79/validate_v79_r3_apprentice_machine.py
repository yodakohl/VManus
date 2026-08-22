#!/usr/bin/env python3
"""Validate the frozen V79 R3 apprentice machine and all traces."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

FREEZE = HERE / "V79_R3_EDGE_COPY_RULE_FREEZE.json"
MANUAL = HERE / "V79_R3_MACHINE_MANUAL.tsv"
TRACES = HERE / "V79_R3_FORWARD_BACKWARD_TRACES.tsv"
TRANSITIONS = HERE / "V79_R3_19_TRANSITION_AUDIT.tsv"
ERRORS = HERE / "V79_R3_ERROR_AUDIT.tsv"
SUMMARY = HERE / "V79_R3_BUILD_SUMMARY.json"
REPORT = HERE / "V79_R3_TECHNICAL_APPRENTICE_REPORT.md"
VALIDATION = HERE / "V79_R3_VALIDATION.json"

V78_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V78_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_116_STATEMENTS.tsv"
V75_LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
V75_GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"

TRACE_RECORDS = ["H2", "H4", "B2"]
TRACE_RECORD_COUNTS = {"H2": 24, "H4": 18, "B2": 62}
ET_ID = "dcda95c81a5460feb191"
PER_ID = "b5fcea1eaed06b2f2291"
ALLOWED_PAGES = {"f10r", "f55v", "f82r", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    manual = read_tsv(MANUAL)
    traces = read_tsv(TRACES)
    transitions = read_tsv(TRANSITIONS)
    errors = read_tsv(ERRORS)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    events = read_tsv(V78_EVENTS)
    statements = read_tsv(V78_STATEMENTS)
    loci = read_tsv(V75_LOCI)
    groups = read_tsv(V75_GROUPS)

    check("freeze status", freeze["freeze_status"] == "FROZEN_BEFORE_TRANSITION_ROW_SCORING")
    check("freeze covers all 19 transitions", freeze["scope"] == "ALL_19_STATEMENT_INTERNAL_PHYSICAL_LINE_TRANSITIONS_IN_V78_SELECTED_PROSE")
    check("freeze bars exceptions", freeze["no_exceptions"] == "NO_LOCUS_PAGE_CARD_WORD_OR_REGISTER_SPECIFIC_EXCEPTION_ALLOWED")
    check("freeze has four content conditions", all(f"condition_{index}" in freeze["rule"] for index in range(1, 5)))
    check("freeze seals f84/f84r", freeze["seals"] == {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"})

    check("manual has 16 rules", len(manual) == 16, len(manual))
    check("manual order exact", [row["rule_order"] for row in manual] == [f"{index:02d}" for index in range(1, 17)])
    operations = {row["operation"] for row in manual}
    for operation in [
        "RESET_RECORD", "OPEN_STATEMENT", "SET_OR_RESET_OWNER", "BUFFER_EDGE_CARD",
        "COLLAPSE_ANTICIPATORY_COPY", "RELEASE_BOTH", "EMIT_ET_QUESTIONED",
        "EMIT_PER_QUESTIONED", "EMIT_FORMAL_CHANNEL", "EMIT_OPAQUE_VALUE",
        "LOOKUP_CONTEXT_EXPANSION", "MASK_CONTEXT_EXPANSION", "SET_F69_LEFT_NAMESPACE",
        "LOOKUP_UNORDERED_SLOT", "VERIFY_ROUNDTRIP",
    ]:
        check(f"manual operation present: {operation}", operation in operations)
    check("manual rows complete", all(all(value != "" for value in row.values()) for row in manual))

    check("transition rows exactly 19", len(transitions) == 19, len(transitions))
    check("transition IDs exact", [row["transition_id"] for row in transitions] == [f"LT{index:02d}" for index in range(1, 20)])
    check("all transition rows same statement", all(row["same_statement"] == "YES" for row in transitions))
    check("all transition rows cross loci", all(row["from_locus"] != row["to_locus"] for row in transitions))
    check("all transition rows no locus exception", all(row["locus_specific_exception"] == "NO" for row in transitions))
    check("all line-final events NONCLOSE", all(row["line_final_terminal_status"] == "NONCLOSE" for row in transitions))
    check("one same-card transition", sum(row["same_exact_card"] == "YES" for row in transitions) == 1)
    check("15 same-owner transitions", sum(row["same_visible_owner"] == "YES" for row in transitions) == 15)
    check("classification TP1 TN18", Counter(row["classification"] for row in transitions) == {"TP": 1, "TN": 18})
    check("zero FP/FN", all(row["classification"] not in {"FP", "FN"} for row in transitions))
    positives = [row for row in transitions if row["rule_prediction"] == "ANTICIPATORY_MARGIN_COPY"]
    check("one predicted copy", len(positives) == 1, len(positives))
    check("copy pair exact E180/E181", positives[0]["line_final_event"] == "E180" and positives[0]["line_initial_event"] == "E181")
    check("copy pair exact PER card", positives[0]["line_final_exact_card"] == PER_ID and positives[0]["line_initial_exact_card"] == PER_ID)
    check("copy pair one source token", positives[0]["source_tokens_after_rule"] == "1")
    check("all negatives retain two tokens", all(row["source_tokens_after_rule"] == "2" for row in transitions if row["rule_prediction"] == "NO_COPY"))

    # Recompute the complete opportunity set from central V78.
    event_by_serial = {row["event_serial"]: row for row in events}
    rebuilt: list[tuple[str, str, str]] = []
    for statement in statements:
        serials = statement["event_serials"].split("|")
        for left, right in zip(serials, serials[1:]):
            if event_by_serial[left]["locus"] != event_by_serial[right]["locus"]:
                rebuilt.append((statement["statement_id"], f"E{int(left):03d}", f"E{int(right):03d}"))
    published = [(row["statement_id"], row["line_final_event"], row["line_initial_event"]) for row in transitions]
    check("transition opportunity reconstruction exact", rebuilt == published, len(rebuilt))

    check("trace rows exactly 264", len(traces) == 264, len(traces))
    check("trace IDs unique", len({row["trace_id"] for row in traces}) == 264)
    check("trace pages fixed", {row["page"] for row in traces} == ALLOWED_PAGES, sorted({row["page"] for row in traces}))
    check("no f84 trace page", all(not row["page"].startswith("f84") for row in traces))
    check("all traces exact roundtrip", all(row["exact_roundtrip"] == "YES" for row in traces))
    check("all traces without-master semantic no", all(row["semantic_recovery_without_master"] == "NO" for row in traces))
    check("all traces with-master marked lookup only", all(row["semantic_recovery_with_master"] == "LOOKUP_ONLY__YES" for row in traces))
    check("all trace cells populated", all(all(value != "" for value in row.values()) for row in traces))

    trace_counts = Counter((row["trace_family"], row["direction"]) for row in traces)
    check("prose forward 104", trace_counts[("PROSE", "FORWARD")] == 104)
    check("prose backward 104", trace_counts[("PROSE", "BACKWARD")] == 104)
    check("Astro forward 28", trace_counts[("ASTRO_DIRECT_SLOT", "FORWARD")] == 28)
    check("Astro backward 28", trace_counts[("ASTRO_DIRECT_SLOT", "BACKWARD")] == 28)

    selected_events = [row for row in events if row["record_unit_id"] in TRACE_RECORDS]
    source_event_ids = {row["event_id"] for row in selected_events}
    for record_id, count in TRACE_RECORD_COUNTS.items():
        forward = [row for row in traces if row["trace_family"] == "PROSE" and row["direction"] == "FORWARD" and row["unit_id"] == record_id]
        backward = [row for row in traces if row["trace_family"] == "PROSE" and row["direction"] == "BACKWARD" and row["unit_id"] == record_id]
        check(f"{record_id} forward count", len(forward) == count, len(forward))
        check(f"{record_id} backward count", len(backward) == count, len(backward))
        check(f"{record_id} forward item coverage", {row["item_id"] for row in forward} == {row["event_id"] for row in selected_events if row["record_unit_id"] == record_id})
        check(f"{record_id} backward item coverage", {row["item_id"] for row in backward} == {row["event_id"] for row in selected_events if row["record_unit_id"] == record_id})

    prose_forward = [row for row in traces if row["trace_family"] == "PROSE" and row["direction"] == "FORWARD"]
    prose_backward = [row for row in traces if row["trace_family"] == "PROSE" and row["direction"] == "BACKWARD"]
    check("prose forward item set exact", {row["item_id"] for row in prose_forward} == source_event_ids)
    check("prose backward item set exact", {row["item_id"] for row in prose_backward} == source_event_ids)
    source_card_by_event = {row["event_id"]: row["joint_tuple_id"] for row in selected_events}
    check("forward exact card reconstruction", all(row["reconstructed_exact_visible"] == source_card_by_event[row["item_id"]] for row in prose_forward))
    check("backward exact card reconstruction", all(row["reconstructed_exact_visible"] == source_card_by_event[row["item_id"]] for row in prose_backward))

    forward_by_item = {row["item_id"]: row for row in prose_forward}
    backward_by_item = {row["item_id"]: row for row in prose_backward}
    check("E180 forward buffered", "BUFFER_EDGE_CARD__NO_SOURCE_EMIT" in forward_by_item["E180"]["machine_action"] and forward_by_item["E180"]["formal_output"] == "NO_SOURCE_TOKEN__ANTICIPATORY_MARGIN_COPY")
    check("E181 forward read once", "MATCH_BUFFER__EMIT_ONCE__CLEAR" in forward_by_item["E181"]["machine_action"])
    check("E180 backward anticipation", backward_by_item["E180"]["machine_action"].startswith("RENDER_ANTICIPATORY_EDGE_COPY_FROM_NEXT_TOKEN"))
    check("E181 backward main token", backward_by_item["E181"]["machine_action"].startswith("RENDER_MAIN_SOURCE_TOKEN_AT_LINE_ENTRY"))

    reset_ids = {"E189", "E198", "E203", "E212"}
    check("B2 forward reset IDs exact", {row["item_id"] for row in prose_forward if "SET_OR_RESET_OWNER" in row["machine_action"] and row["item_id"] in reset_ids} == reset_ids)
    check("B2 backward reset IDs exact", all("RENDER_OWNER_RESET_BOUNDARY" in backward_by_item[item]["machine_action"] for item in reset_ids))
    check("E180/E181 same owner", forward_by_item["E180"]["local_owner"] == forward_by_item["E181"]["local_owner"])

    allowed_forward_tokens = {
        "[EXEMPLARWERT UNBEKANNT]",
        "[FORMAL:VORGABEPARAMETER?; KEIN WORT]",
        "[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN WORT]",
        "ET? (UND/AUCH?)",
        "PER? (DURCH/GEMÄSS?)",
        "NO_SOURCE_TOKEN__ANTICIPATORY_MARGIN_COPY",
    }
    check("no new prose token category", {row["formal_output"] for row in prose_forward} <= allowed_forward_tokens)
    check("trace ET exact card only", all(source_card_by_event[row["item_id"]] == ET_ID for row in prose_forward if row["formal_output"] == "ET? (UND/AUCH?)"))
    check("trace PER exact card only", all(source_card_by_event[row["item_id"]] == PER_ID for row in prose_forward if row["formal_output"] == "PER? (DURCH/GEMÄSS?)"))

    f69_source = [row for row in loci if row["page"] == "f69v" and row["locus"] in {f"f69v.{n}" for n in range(4, 32)}]
    f69_groups = [row for row in groups if row["page"] == "f69v" and row["locus"] in {f"f69v.{n}" for n in range(4, 32)}]
    astro_forward = [row for row in traces if row["trace_family"] == "ASTRO_DIRECT_SLOT" and row["direction"] == "FORWARD"]
    astro_backward = [row for row in traces if row["trace_family"] == "ASTRO_DIRECT_SLOT" and row["direction"] == "BACKWARD"]
    check("f69 source loci 28", len(f69_source) == 28)
    check("f69 source groups 33", len(f69_groups) == 33)
    check("Astro item IDs L01..L28", {row["item_id"] for row in astro_forward} == {f"L{n:02d}" for n in range(1, 29)})
    check("Astro namespace exact", all(row["field_or_namespace"] == "F69_LEFT_WHEEL_NS" for row in astro_forward + astro_backward))
    check("Astro no traversal forward", all(row["machine_action"] == "DIRECT_LOCAL_ADDRESS__COPY_OPAQUE_GROUPS__NO_TRAVERSAL" for row in astro_forward))
    check("Astro formal groups reconstructed both ways", sum(len(row["reconstructed_exact_visible"].split("|")) for row in astro_forward) == 33 and sum(len(row["reconstructed_exact_visible"].split("|")) for row in astro_backward) == 33)
    check("Astro no-master values unknown", all("CELESTIAL_VALUE_UNKNOWN" in row["without_master_output"] for row in astro_forward + astro_backward))

    check("error audit rows 13", len(errors) == 13, len(errors))
    error_by_id = {row["audit_id"]: row for row in errors}
    check("error audit IDs exact", set(error_by_id) == {f"A{n:02d}" for n in range(1, 14)})
    check("edge metric exact", error_by_id["A01"]["metric"] == "TP=1;FP=0;FN=0;TN=18;precision=1.000;recall=1.000;specificity=1.000")
    check("prose formal both master modes pass", error_by_id["A02"]["result"] == "PASS" and error_by_id["A03"]["result"] == "PASS")
    check("prose semantics without master fail", error_by_id["A05"]["successes"] == "0" and error_by_id["A05"]["failures"] == "103")
    check("Astro formal both master modes pass", error_by_id["A08"]["result"] == "PASS" and error_by_id["A09"]["result"] == "PASS")
    check("Astro semantics without master fail", error_by_id["A11"]["successes"] == "0" and error_by_id["A11"]["failures"] == "28")
    check("ET formal rival tied", error_by_id["A12"]["result"] == "TIE__NO_SEMANTIC_DISCRIMINATION")
    check("PER formal rival retained", error_by_id["A13"]["result"] == "WORD_ROUTE_MECHANICALLY_REPAIRED__FORMAL_RIVAL_SIMPLER_OR_TIED")

    check("summary built", summary["status"] == "BUILT")
    check("summary trace rows", summary["trace_rows"] == 264)
    check("summary TP/FP/FN/TN", summary["line_transition_audit"] == {
        "opportunities": 19, "TP": 1, "FP": 0, "FN": 0, "TN": 18,
        "predicted_copy_pairs": ["E180->E181"],
    })
    check("summary formal roundtrip both 137/137", summary["roundtrip"]["formal_with_master"].startswith("137/137") and summary["roundtrip"]["formal_without_master"].startswith("137/137"))
    check("summary no-master semantics zero", summary["roundtrip"]["prose_semantic_without_master"] == "0/103" and summary["roundtrip"]["astro_semantic_without_master"] == "0/28")
    check("summary word rivals exact", summary["word_rivals"] == {
        "ET": "ET?_AND_SILENT_LINK_SLOT_TIED",
        "PER": "EDGE_COPY_REPAIR_PASSES_MECHANICALLY__ENTRY_RESET_SIMPLER_OR_TIED",
    })
    check("summary seals", summary["seals"] == {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"})
    check("freeze hash current", summary["freeze_sha256"] == sha256(FREEZE))
    check("output hashes current", all(summary["output_sha256"][path.name] == sha256(path) for path in [MANUAL, TRACES, TRANSITIONS, ERRORS]))

    report_text = REPORT.read_text(encoding="utf-8")
    check("report exists and substantial", len(report_text) > 7000, len(report_text))
    check("report gives 19-transition confusion matrix", all(token in report_text for token in ["| TP | 1 |", "| FP | 0 |", "| FN | 0 |", "| TN | 18 |"]))
    check("report separates formal/semantic recovery", "formale Rekonstruktion 137/137" in report_text and "konkrete Prosa-Sachwerte 0/103" in report_text)
    check("report retains interpretation ceiling", "keine Übersetzung" in report_text and "kein wissenschaftlicher Nachweis" in report_text)

    passed = sum(item["pass"] for item in checks)
    failed = [item for item in checks if not item["pass"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "passed": passed,
        "total": len(checks),
        "failed": failed,
        "counts": {
            "manual_rules": len(manual), "trace_rows": len(traces), "transition_rows": len(transitions),
            "error_audit_rows": len(errors), "prose_visible_events": len(selected_events),
            "Astro_loci": len(f69_source), "Astro_groups": len(f69_groups),
        },
        "transition_confusion": dict(Counter(row["classification"] for row in transitions)),
        "roundtrip": summary["roundtrip"],
        "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']} {passed}/{len(checks)}")
    if failed:
        for item in failed:
            print(f"FAIL: {item['name']} :: {item['detail']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
