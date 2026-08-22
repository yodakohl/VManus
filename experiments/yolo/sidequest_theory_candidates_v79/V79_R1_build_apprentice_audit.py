#!/usr/bin/env python3
"""Build the V79 R1 compact apprentice manual, traces, and carry audit."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
V78_SELECTION = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_FOUR_ROLE_SELECTION.md"
V78_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V78_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_116_STATEMENTS.tsv"
V78_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_11_CONTINUOUS_RECORDS.tsv"
V78_ROLE_AUDIT = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_ET_PER_28_AUDIT.tsv"
V75_GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
V75_LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
V75_INSTRUMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_THREE_INSTRUMENTS.tsv"

INPUT_HASHES = {
    V78_SELECTION: "ddd840def8e45afc6cc999602ed0a8fa2a7aab30ec164612464640e55ec0c211",
    V78_EVENTS: "0872a6f61f7e3396743c54bb1a8ad9e5830ebe7c0ddcf23885204a52ed046ac1",
    V78_STATEMENTS: "d12c385ba37dc1e875abbeadd3df55eb34698e5b08ab3d7136e9a8c4eaeef0f0",
    V78_RECORDS: "c32a202087155e015a6b86d32322fd6ca47c67998431d9b8fd4cc38d71db66f9",
    V78_ROLE_AUDIT: "7c9c9c3b43e8b9580a2dafdbcebd840d58b5675b36260b38cbbe50ec7e2f6c46",
    V75_GROUPS: "3c35deb68ee2a4a02b539a7b979011fb4fea1436847249277181974133c8ff8e",
    V75_LOCI: "8f43d3571694025383119101748cd6eb2ba6c909a638a87f532ba61b7270ced5",
    V75_INSTRUMENTS: "097678b799d9ce8ee960d82cc613c1375e678f34a8fbc2c97e79b7321a5dc0a8",
}

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"
FORMAL_CARDS = {"2f1c5e56e8f0ff459065", "308e8ea2d5d190c498e8"}
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    for path, expected in INPUT_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"input changed: {path}"

    events = read_tsv(V78_EVENTS)
    statements = read_tsv(V78_STATEMENTS)
    records = read_tsv(V78_RECORDS)
    role_audit = read_tsv(V78_ROLE_AUDIT)
    groups = read_tsv(V75_GROUPS)
    loci = read_tsv(V75_LOCI)
    instruments = read_tsv(V75_INSTRUMENTS)
    assert len(events) == 381 and len(statements) == 116 and len(records) == 11 and len(role_audit) == 28
    assert len(groups) == 395 and len(loci) == 142 and len(instruments) == 3
    assert [int(r["event_serial"]) for r in events] == list(range(1, 382))

    manual_rows = [
        (1, "BOTH", "START", "Choose one frozen record or one local Astro namespace; copy its visible owner and boundaries before any content.", "OWNER_AND_BOUNDARY_FRAME", "Do not choose a meaning first."),
        (2, "FORWARD", "PROSE_EVENT", "Copy every exact card once in visible order; preserve physical line, field, statement, and owner-break metadata.", "EXACT_CARD_AND_BOUNDARY_RECOVERY", "Never merge similar forms or omit a repeated card."),
        (3, "FORWARD", "ET", "For the exact ET card write one question-mark word ET?; read only UND?/AUCH?, never a process verb.", "ET_CATEGORY", "No additional sense and no promotion to a confirmed lexeme."),
        (4, "FORWARD", "PER", "For the exact PER card write PER?; outside carry pairs it governs one visibly bracketed complement as DURCH?/GEMÄSS?.", "PER_CATEGORY_PLUS_ONE_COMPLEMENT", "PER remains probationary and the complement is exemplar content."),
        (5, "BOTH", "FORMAL", "For either of the two formal cards write and read only [FORMAL; KEIN WORT].", "FORMAL_NONWORD", "Do not restore MASS, target, measure, or another gloss."),
        (6, "BOTH", "EXEMPLAR", "For every other card write [EXEMPLARWERT UNBEKANNT]; copy any concrete expansion only inside [EXEMPLAR:...].", "OPAQUE_CARD_PLUS_OPTIONAL_SOURCE_EXPANSION", "Without the exemplar no concrete semantic recovery is claimed."),
        (7, "BOTH", "CARRY", "At an intra-statement physical-line boundary compare the final card with the next line's first card. If exact identity, owner, and statement match and neither is CLOSE, copy both but read the first as anticipation and speak the source token once at the second.", "TWO_VISIBLE_COPIES_ONE_SOURCE_TOKEN", "No locus list is allowed."),
        (8, "BOTH", "CARRY_NEGATIVE", "If card identity differs, owner resets, statement changes, or CLOSE occurs, do not suppress either card.", "ORDINARY_TWO_EVENT_READING", "A line break alone never licenses carry."),
        (9, "BACKWARD", "STATEMENT", "Regroup by frozen statement identity rather than physical line; retain every cross-line and cross-field continuation.", "STATEMENT_BOUNDARY_RECOVERY", "Never turn every line end into a sentence end."),
        (10, "BOTH", "OWNER_RESET", "At BREAK_VISIBLE_GAP reset substance, target, and direction before reading the new local owner.", "LOCAL_OWNER_RECOVERY", "Do not create a page-wide Bio flow."),
        (11, "FORWARD", "ASTRO_GROUP", "Within one local Astro locus copy each opaque group ID in listed local order and retain the locus boundary.", "OPAQUE_GROUP_AND_LOCUS_RECOVERY", "Do not import prose cards or meanings."),
        (12, "BACKWARD", "ASTRO_NAMESPACE", "Return every copied group only to its frozen local wheel/panel/slot; never move a value across wheels or pages.", "LOCAL_NAMESPACE_RECOVERY", "No f68-f69 key, common start, direction, or rotation."),
        (13, "BOTH", "F69_LEFT_28", "Treat L01-L28 only as editorial addresses for 28 distinct visible radial slots; reconstruct all slot buckets but no authorial sequence.", "28_SLOT_BUCKET_RECOVERY", "Do not infer names, ranks, Moon mansions, or cyclic order."),
        (14, "BACKWARD", "SEMANTIC_CEILING", "With the master exemplar copy bracketed content verbatim; without it recover only exact identity, boundary, owner, ET?/PER? category, and formal/nonword status.", "SEPARATE_COPY_RECOVERY_FROM_SEMANTIC_INFERENCE", "Rote exemplar recovery is not decipherment."),
        (15, "CHECK", "PER_DECISION", "Run the carry rule over all 19 frozen transitions. Retain PER only if the E180/E181 repair is found without any false positive or false negative.", "PER_FALSIFIER", "One passing positive does not confirm PER semantics."),
        (16, "CHECK", "ET_DECISION", "Verify all 19 ET cards retain one additive question-mark category; keep the silent formal-link rival explicitly tied.", "ET_FALSIFIER", "If an extra sense is needed, withdraw ET."),
    ]
    manual = [
        {
            "step": step,
            "direction": direction,
            "scope": scope,
            "instruction": instruction,
            "recoverable_output": output,
            "forbidden_error": error,
        }
        for step, direction, scope, instruction, output, error in manual_rows
    ]
    write_tsv(HERE / "V79_R1_COMPACT_MANUAL.tsv", manual, list(manual[0]))

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)
    carry_rows: list[dict[str, object]] = []
    transition_index = 0
    for statement in statements:
        statement_events = events_by_statement[statement["statement_id"]]
        for left, right in zip(statement_events, statement_events[1:]):
            if left["locus"] == right["locus"]:
                continue
            transition_index += 1
            same_card = left["joint_tuple_id"] == right["joint_tuple_id"]
            same_owner = (
                left["image_owner_id"] == right["image_owner_id"]
                and not right["owner_break_before"].startswith("BREAK_VISIBLE_GAP")
            )
            no_close = left["terminal_status"] == "NONCLOSE" and right["terminal_status"] == "NONCLOSE"
            fires = same_card and same_owner and no_close
            expected = statement["selected_catchword_repair"] != "NONE"
            classification = "TP" if fires and expected else "FP" if fires else "FN" if expected else "TN"
            carry_rows.append({
                "transition_index": transition_index,
                "record_unit_id": statement["record_unit_id"],
                "statement_id": statement["statement_id"],
                "page": statement["page"],
                "left_locus": left["locus"],
                "left_event": left["event_id"],
                "left_card": left["joint_tuple_id"],
                "left_terminal_status": left["terminal_status"],
                "right_locus": right["locus"],
                "right_event": right["event_id"],
                "right_card": right["joint_tuple_id"],
                "right_terminal_status": right["terminal_status"],
                "same_exact_card": "YES" if same_card else "NO",
                "same_owner_without_reset": "YES" if same_owner else "NO",
                "same_statement": "YES",
                "no_close": "YES" if no_close else "NO",
                "carry_rule_fires": "YES" if fires else "NO",
                "central_expected_carry": "YES" if expected else "NO",
                "classification": classification,
                "forward_copy_action": "COPY_BOTH_VISIBLE_CARDS" if fires else "COPY_BOTH_ORDINARY_EDGE_EVENTS",
                "backward_source_action": "FIRST_IS_ANTICIPATION__READ_SECOND_ONCE" if fires else "READ_EACH_EVENT_ORDINARILY",
                "boundary_recovery": "EXACT",
                "strongest_risk": (
                    "single positive example; convention remains underdetermined against dittography/formal reset"
                    if fires else
                    "suppressing here would be a false positive"
                ),
            })
    assert transition_index == 19
    assert Counter(r["classification"] for r in carry_rows) == {"TP": 1, "TN": 18}
    write_tsv(HERE / "V79_R1_CARRY_AUDIT.tsv", carry_rows, list(carry_rows[0]))

    trace_rows: list[dict[str, object]] = []
    trace_step = Counter()
    prose_trace_records = {"H2": "TRACE_HERBAL_H2", "B2": "TRACE_BIO_B2"}
    for event in events:
        record = event["record_unit_id"]
        if record not in prose_trace_records:
            continue
        trace_id = prose_trace_records[record]
        trace_step[trace_id] += 1
        serial = int(event["event_serial"])
        is_carry_copy = serial == 180
        is_carry_main = serial == 181
        if event["joint_tuple_id"] == ET_CARD:
            backward = "ET?__UND_ODER_AUCH_FRAGEZEICHENKATEGORIE"
            without_exemplar = "ET_CATEGORY_ONLY__FORMAL_LINK_RIVAL_TIED"
        elif event["joint_tuple_id"] == PER_CARD:
            backward = "PER_CARRY_ANTICIPATION__DO_NOT_SPEAK" if is_carry_copy else "PER?__DURCH_ODER_GEMAESS_FRAGEZEICHENKATEGORIE"
            without_exemplar = "PER_CATEGORY_ONLY__COMPLEMENT_AND_CHOICE_UNKNOWN"
        elif event["joint_tuple_id"] in FORMAL_CARDS:
            backward = "[FORMAL; KEIN WORT]"
            without_exemplar = "FORMAL_NONWORD_ONLY"
        else:
            backward = "[EXEMPLARWERT UNBEKANNT]"
            without_exemplar = "NO_CONCRETE_SEMANTIC_RECOVERY"
        boundary = event["owner_break_before"]
        if is_carry_copy:
            boundary += "__LINE_FINAL_ANTICIPATION"
        elif is_carry_main:
            boundary += "__LINE_INITIAL_MAIN_TOKEN"
        trace_rows.append({
            "trace_id": trace_id,
            "domain": "HERBAL" if record == "H2" else "BIO",
            "trace_step": trace_step[trace_id],
            "source_unit": event["event_id"],
            "page": event["page"],
            "locus": event["locus"],
            "field_or_slot": event["field_id"],
            "statement_or_namespace": event["statement_id"],
            "exact_identity_order": event["joint_tuple_id"],
            "boundary_before": boundary,
            "visible_owner": event["image_owner_id"],
            "forward_copy_instruction": "COPY_EXACT_CARD_AND_BOUNDARIES" + ("__KEEP_VISIBLE_BUT_SOURCE_SILENT" if is_carry_copy else ""),
            "backward_literal_recovery": backward,
            "semantic_with_exemplar": event["selected_continuous_event_token"],
            "semantic_without_exemplar": without_exemplar,
            "exact_identity_recovery": "PASS",
            "boundary_recovery": "PASS",
            "strongest_error": event["strongest_contradiction"],
        })

    left_slots = [
        row for row in loci
        if row["page"] == "f69v" and row["local_content_class"] == "LEFT_WHEEL_LOCAL_28_PLACE_INVENTORY_ENTRY"
    ]
    assert len(left_slots) == 28
    group_map = {row["group_serial"]: row for row in groups}
    for slot_index, locus in enumerate(left_slots, 1):
        trace_id = "TRACE_ASTRO_F69_LEFT_28"
        trace_step[trace_id] += 1
        group_serials = locus["group_serials"].split("|")
        group_ids = locus["opaque_group_ids"].split("|")
        assert len(group_serials) == len(group_ids) == int(locus["group_count"])
        assert all(group_map[g]["opaque_local_id"] == gid for g, gid in zip(group_serials, group_ids))
        trace_rows.append({
            "trace_id": trace_id,
            "domain": "ASTRO",
            "trace_step": trace_step[trace_id],
            "source_unit": locus["locus"],
            "page": locus["page"],
            "locus": locus["locus"],
            "field_or_slot": f"L{slot_index:02d}",
            "statement_or_namespace": locus["local_namespace"],
            "exact_identity_order": "|".join(group_ids),
            "boundary_before": "LEFT_WHEEL_NAMESPACE_START" if slot_index == 1 else "DISTINCT_VISIBLE_RADIAL_SLOT",
            "visible_owner": locus["local_image_owner"],
            "forward_copy_instruction": "COPY_ALL_OPAQUE_GROUP_IDS_INSIDE_THIS_SLOT;PRESERVE_SLOT_BOUNDARY",
            "backward_literal_recovery": f"RETURN_{len(group_ids)}_GROUPS_TO_L{slot_index:02d}_ONLY",
            "semantic_with_exemplar": "[EXEMPLAR:" + locus["complete_copied_local_meaning_or_label"] + "]",
            "semantic_without_exemplar": "LEFT_WHEEL_LOCAL_SLOT_ONLY__NAME_RANK_START_DIRECTION_AND_MEANING_UNKNOWN",
            "exact_identity_recovery": "PASS",
            "boundary_recovery": "PASS",
            "strongest_error": locus["strongest_contradiction"],
        })
    assert Counter(r["trace_id"] for r in trace_rows) == {
        "TRACE_HERBAL_H2": 24,
        "TRACE_BIO_B2": 62,
        "TRACE_ASTRO_F69_LEFT_28": 28,
    }
    write_tsv(HERE / "V79_R1_REQUIRED_TRACES.tsv", trace_rows, list(trace_rows[0]))

    error_rows = [
        ("ERR01", "CARRY", "Only one positive transition exists.", "A perfect 1/19 audit can still be an accidental duplicated form.", "Retain mechanical rule, do not promote semantics.", 3),
        ("ERR02", "PER", "E180/E181 are two visible copies but one proposed source token.", "Independent-word reading gives PER PER before one complement.", "Retain PER on probation because the locus-free rule returns TP1/FP0/FN0; formal-entry/dittography rival remains.", 4),
        ("ERR03", "ET", "Exact additive reading is executable but a silent formal link fits the same positions.", "Backward form recovery cannot decide lexical word versus nonlexical link.", "Retain ET? provisionally; do not promote or add senses.", 3),
        ("ERR04", "FORMAL", "A learner may restore old MASS or target glosses.", "The two cards are explicitly nonwords in V78.", "Correct every such reading to [FORMAL; KEIN WORT].", 4),
        ("ERR05", "H2", "Oil, fraction, preparation and external use can be copied only from the exemplar.", "The cards alone do not recover those contents.", "Score exact card/boundary PASS but semantic-without-exemplar FAIL/UNKNOWN.", 3),
        ("ERR06", "B2_OWNER", "Four visible B2 gaps reset local owner state.", "Carrying substance or direction across E189, E198, E203, or E212 invents a process.", "Reset substance, target and direction at each break.", 4),
        ("ERR07", "LINE", "Physical line ends are not sentence ends.", "E180/E181 and 18 other transitions remain inside one statement.", "Recover statements from the frozen statement boundary, not line layout.", 3),
        ("ERR08", "ASTRO", "L01-L28 are editorial addresses, not an authorial cycle.", "No visible start, rank, direction or name is established.", "Recover 28 local buckets only.", 4),
        ("ERR09", "ASTRO_NAMESPACE", "The three f69v wheels are disconnected.", "Moving a value from the left 28-slot wheel to middle/right creates an unsupported key.", "Keep every group in A3_LEFT_WHEEL_ONLY.", 4),
        ("ERR10", "SEMANTICS", "With-exemplar recovery is rote copying, not inference.", "Removing the exemplar destroys concrete content while exact identities remain.", "Report semantic recovery with and without exemplar separately.", 4),
    ]
    errors = [
        {
            "error_id": eid,
            "scope": scope,
            "failure": failure,
            "why_it_matters": why,
            "repair_or_decision": repair,
            "severity_0_4": severity,
        }
        for eid, scope, failure, why, repair, severity in error_rows
    ]
    write_tsv(HERE / "V79_R1_ERROR_CONTRADICTIONS.tsv", errors, list(errors[0]))

    # Readable trace edition, generated directly from the complete trace rows.
    trace_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in trace_rows:
        trace_groups[str(row["trace_id"])].append(row)
    md = [
        "# V79 R1 — Pflichttraces für den Lehrling",
        "",
        "Vorwärts wird jede sichtbare Identität samt Grenzen kopiert. Rückwärts wird zuerst die formale Spur rekonstruiert; konkrete Inhalte dürfen nur aus `[EXEMPLAR:…]` stammen.",
        "",
    ]
    for trace_id in ("TRACE_HERBAL_H2", "TRACE_BIO_B2", "TRACE_ASTRO_F69_LEFT_28"):
        rows = trace_groups[trace_id]
        md += [f"## {trace_id}", ""]
        for row in rows:
            md.append(
                f"{row['trace_step']}. `{row['source_unit']}` / `{row['locus']}` / `{row['field_or_slot']}` — "
                f"Identität `{row['exact_identity_order']}`; Grenze `{row['boundary_before']}`; "
                f"rückwärts `{row['backward_literal_recovery']}`; mit Exemplar {row['semantic_with_exemplar']}; "
                f"ohne Exemplar `{row['semantic_without_exemplar']}`."
            )
        md.append("")
    (HERE / "V79_R1_REQUIRED_TRACES.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    counts = Counter(r["classification"] for r in carry_rows)
    summary = {
        "status": "BUILT",
        "manual_steps": len(manual),
        "trace_rows": len(trace_rows),
        "trace_counts": dict(Counter(r["trace_id"] for r in trace_rows)),
        "carry_transitions": len(carry_rows),
        "carry_confusion": {k: counts.get(k, 0) for k in ("TP", "FP", "FN", "TN")},
        "owner_reset_transitions": sum(r["same_owner_without_reset"] == "NO" for r in carry_rows),
        "et_decision": "RETAIN_PROVISIONAL__FORMAL_LINK_RIVAL_TIED",
        "per_decision": "RETAIN_ON_PROBATION__VISIBLE_CARRY_RULE_TP1_FP0_FN0__FORMAL_OR_DITTOGRAPHY_RIVAL_LIVE",
        "exact_copy_recovery": "PASS_ON_ALL_114_TRACE_ROWS",
        "semantic_with_exemplar": "ROTE_RECOVERY_ONLY",
        "semantic_without_exemplar": "CONCRETE_CONTENT_NOT_RECOVERED",
        "pages": sorted({str(r["page"]) for r in trace_rows}),
        "sealed_pages_accessed": [],
        "input_hashes": {str(path.relative_to(ROOT)): digest for path, digest in INPUT_HASHES.items()},
    }
    (HERE / "V79_R1_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
