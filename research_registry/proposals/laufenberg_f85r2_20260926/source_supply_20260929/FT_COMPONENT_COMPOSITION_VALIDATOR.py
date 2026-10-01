#!/usr/bin/env python3
"""Finite frozen-A table audit. Not a manuscript parser or semantic confirmation.

Checks hand-specified operation classes against already authored row deltas.
No source expansion, lexical inference, repairs, or author writes occur.
Run from anywhere; the inputs and completed audit are beside this script.
"""
import collections
import copy
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
BOUND = {
    "FT_AUTHOR_COMPONENT.json": "088e54f9865d77b6f4e461a522e750fd241111f40530feb37e24f35b1c890afc",
    "FT_AUTHOR_COMPONENT.md": "10e318acad59fd74acce9527e1d1f7fdca56086f2064f08b28829192b878f0db",
    "FT_COMPONENT_DERIVATION.tsv": "0c5154cb966e89d31b178f706295d68990d6c31909d21ec72b63728804173c33",
    "FT_SOURCE_PACKET.json": "31de602d3d3a6b1c58caf5563159a3f757fe05995971f9319b769c4bbb95fa26",
}
BRANCH = set("SIDE INTERIOR FINE_BRANCH WALL_BRANCH NEIGHBOR_BRANCH CIRCULATION_BRANCH INFERIOR_BRANCH SIBLING".split())
NOMINAL = set("MOIST CONDENSATE THIN_FLUID DISCHARGED_FLUID SECRETION".split())
EVENT = set("TRANSIT RETAIN OUTFLOW UNIFORM_TRANSIT INFLOW RETURN REJOIN EXCHANGE ACCUMULATE BRANCH_COLLECTION".split())
CPROP = set("C_NARROW C_OPEN C_FINE_TERMINALS C_SMOOTH C_RESISTANT C_LATERAL_APERTURE C_SMALL_OUTLET C_CONTRACTED".split())
FPROP = set("FLUID_PRESSURED FLUID_EASING FLUID_REST FLUID_OUTLET_STABLE FLUID_CONTINUOUS FLUID_DECLINING FLUID_BEGINNING FLUID_WEAK FLUID_REDUCED FLUID_INTERMITTENT FLUID_MULTISTREAM FLUID_FREE FLUID_STABLE".split())
RELATION = set("ENCLOSES FLUID_LOWER WALL_FILM FLOW_LIMIT".split())


def main():
    for filename, expected in BOUND.items():
        assert hashlib.sha256((BASE / filename).read_bytes()).hexdigest() == expected, filename
    author = json.loads((BASE / "FT_AUTHOR_COMPONENT.json").read_text())
    packet = json.loads((BASE / "FT_SOURCE_PACKET.json").read_text())
    audit = json.loads((BASE / "FT_COMPONENT_COMPOSITION_AUDIT.json").read_text())
    dictionary = {d["form"]: d for d in author["lexical_dictionary"]}
    lower = [r for r in author["group_ledger"] if r["page"] == "f83r"]
    units = collections.defaultdict(list)
    for row in lower:
        units[row["unit_id"], row["edition"]].append(row)
    results = {}
    for (unit, reader), rows in units.items():
        assertions, events, previous = [], [], None
        for row in rows:
            d = dictionary[row["raw"]]
            checks = {"exact_dictionary": row["definition"] == row["raw"] and row["segments"] == d["segments"],
                      "segments_concat": "".join(d["segments"]) == row["raw"]}
            if row["kind"] != "P":
                checks["finite_nominal"] = d["operations"] == "CAPTION" and row["status"] == "C0_NOMINAL_CAPTION" and row["state_after"]["namedComponent"] in row["referents"]
                results[row["source_group_id"]] = checks
                continue
            before, after, delta = row["state_before"], row["state_after"], row["state_delta"]
            component, fluid = before["currentComponent"], before["currentFluid"]
            want_c, want_f, pending = component, fluid, copy.deepcopy(before["pendingConsumer"])
            made_c, made_f = iter(delta["introduced_components"]), iter(delta["introduced_fluids"])
            want_events, want_assertions = [], []
            operations = d["operations"].split()
            checks["same_record_continuity"] = previous is None or previous["state_after"] == before
            if previous is None:
                entry = author["record_initial_environment"][unit]
                checks["paid_initial_environment"] = before["currentComponent"] == entry["current_component"] and before["currentFluid"] is None and not before["eventIds"] and not before["pendingConsumer"] and before["availableComponentParents"] == {k: v["parent"] for k, v in entry["component_details"].items()}
            for operation in operations:
                if operation == "ROOT":
                    want_c = before["entryComponent"]
                elif operation == "DISTAL":
                    want_c = "C51"
                    checks["explicit_distal_bridge"] = "C51" in before["availableComponentParents"] and before["availableComponentParents"]["C51"] == "C45"
                elif operation in BRANCH:
                    made = next(made_c, None)
                    obj = delta["introduced_components"].get(made, {})
                    parent = before["availableComponentParents"].get(want_c) if operation == "SIBLING" else want_c
                    checks["fresh_component_parent"] = bool(made and made not in before["availableComponentParents"] and obj.get("parent") == parent and obj.get("kind") == operation and parent in before["availableComponentParents"])
                    want_c = made
                elif operation in NOMINAL:
                    made = next(made_f, None)
                    obj = delta["introduced_fluids"].get(made, {})
                    checks["fresh_fluid"] = bool(made and made not in before["availableFluidKinds"] and obj.get("kind") == operation)
                    want_f = made
                    if operation == "SECRETION" and pending:
                        checks["immediate_pending_consumer"] = previous is not None and previous["raw"] == "qokchdy" and pending.get("component") == want_c
                        want_events.append(("Transit", [want_c, want_f]))
                        pending = None
                elif operation == "PENDING_TRANSIT":
                    checks["component_for_pending"] = want_c in before["availableComponentParents"]
                    # Independently check the exact G3 frozen construction below.
                    pending = after["pendingConsumer"]
                    checks["pending_declared"] = bool(pending)
                    assert pending == {"component": want_c, "consumer_source": row["source_group_id"], "required_next": "SECRETION"}
                elif operation == "PARENT":
                    want_c = before["availableComponentParents"].get(want_c)
                    checks["explicit_parent"] = want_c is not None
                elif operation == "REF":
                    pass
                elif operation in EVENT:
                    parent = before["availableComponentParents"].get(want_c) or delta["introduced_components"].get(want_c, {}).get("parent")
                    args, kind = [want_c, want_f], operation
                    if operation in {"RETURN", "REJOIN", "EXCHANGE"}:
                        args = [want_c, parent, want_f]
                        checks["event_explicit_parent"] = parent in before["availableComponentParents"]
                    if operation == "BRANCH_COLLECTION":
                        kind = "BranchCollection"
                        checks["terminal_relation_precondition"] = any(a["predicate"] == "CommunicatesWithTerminalPassages" and a["arguments"] == [want_c] for a in assertions)
                    checks["event_explicit_fluid"] = want_f is not None
                    want_events.append((kind, args))
                    if operation == "REJOIN":
                        want_c = parent
                elif operation == "COMMUNICATES":
                    want_assertions.append(("CommunicatesWithTerminalPassages", [want_c]))
                elif operation == "APERTURE_REL":
                    want_assertions.append(("HasSmallAperture", [want_c]))
                elif operation in CPROP:
                    want_assertions.append((operation, [want_c]))
                elif operation in FPROP:
                    checks["property_explicit_fluid"] = want_f is not None
                    want_assertions.append((operation, [want_f]))
                elif operation in RELATION:
                    checks["relation_explicit_fluid"] = want_f is not None
                    want_assertions.append((operation, [want_c, want_f]))
                else:
                    raise AssertionError("Unreviewed operation: " + operation)
            if "FLUID_EASING" in operations:
                checks["easing_preconditions"] = any(a["predicate"] == "FLUID_PRESSURED" and a["arguments"] == [fluid] for a in assertions) and any(e["kind"] == "OUTFLOW" and e["arguments"][-1] == fluid for e in events)
            if row["raw"] == "chckhal":
                checks["contracted_precondition"] = any(a["predicate"] == "C_CONTRACTED" and a["arguments"] == [component] for a in assertions)
            if row["raw"] == "qolkain":
                checks["thin_precondition"] = before["availableFluidKinds"].get(fluid) == "THIN_FLUID"
            if "FLUID_STABLE" in operations:
                checks["stable_retention_precondition"] = "RETAIN" in operations or bool(previous and previous["raw"] == "r" and previous["state_after"]["currentFluid"] == fluid and previous["state_after"]["currentComponent"] == component)
            checks["ordered_register_effect"] = want_c == after["currentComponent"] and want_f == after["currentFluid"] and pending == after["pendingConsumer"]
            checks["event_kind_arguments_count"] = want_events == [(e["kind"], e["arguments"]) for e in delta["events_added"]]
            checks["assertion_kind_arguments_count"] = want_assertions == [(a["predicate"], a["arguments"]) for a in delta["assertions_added"]]
            checks["additive_registers"] = after["availableComponentParents"] == {**before["availableComponentParents"], **{k: v["parent"] for k, v in delta["introduced_components"].items()}} and after["availableFluidKinds"] == {**before["availableFluidKinds"], **{k: v["kind"] for k, v in delta["introduced_fluids"].items()}} and after["eventIds"] == before["eventIds"] + [e["id"] for e in delta["events_added"]] and after["assertionCount"] == before["assertionCount"] + len(delta["assertions_added"])
            checks["no_extra_introductions"] = next(made_c, None) is None and next(made_f, None) is None
            assertions.extend(delta["assertions_added"])
            events.extend(delta["events_added"])
            previous = row
            results[row["source_group_id"]] = checks
        if rows[0]["kind"] == "P":
            cov = next(c for c in author["coverage"] if c["unit_id"] == unit and c["reader"] == reader)
            assert cov["final_state"]["events"] == events and cov["final_state"]["assertions"] == assertions
    stored = {r["source_group_id"]: r["checks"] for r in audit["lower_group_checks"]}
    assert results == stored and all(all(v.values()) for v in results.values())
    for cov in author["coverage"]:
        if not cov["unit_id"].startswith("F83") or "final_state" not in cov:
            continue
        rows = units[cov["unit_id"], cov["reader"]]
        components = copy.deepcopy(author["record_initial_environment"][cov["unit_id"]]["component_details"])
        fluids, events, assertions = {}, [], []
        for row in rows:
            delta = row["state_delta"]
            components.update(delta["introduced_components"])
            fluids.update(delta["introduced_fluids"])
            events.extend(delta["events_added"])
            assertions.extend(delta["assertions_added"])
        final = cov["final_state"]
        assert components == final["components"] and fluids == final["fluids"]
        assert events == final["events"] and assertions == final["assertions"]
        assert all(rows[-1]["state_after"][k] == final[k] for k in ["entryComponent", "currentComponent", "currentFluid", "pendingConsumer"])
        assert final["pendingConsumer"] is None and len(rows) == cov["total"]
        assert len({e["id"] for e in events}) == len(events)
    source = {g["source_group_id"]: g for c in packet["contexts"] for g in c["groups"]}
    assert len(source) == len(author["group_ledger"]) == 655
    for row in author["group_ledger"]:
        assert row["edition"] == row["source_group_id"].split("|")[0]
        assert all(row[k] == v for k, v in source[row["source_group_id"]].items() if k != "unit_position")
        if row["kind"] == "P":
            assert row["position_in_unit"] == source[row["source_group_id"]]["unit_position"]
    for context in packet["contexts"]:
        assert [g["source_group_id"] for g in context["groups"]] == [r["source_group_id"] for r in author["group_ledger"] if r["unit_id"] == context["unit_id"] and r["edition"] == context["edition"]]
    with (BASE / "FT_COMPONENT_DERIVATION.tsv").open() as handle:
        table = list(csv.DictReader(handle, delimiter="\t"))
    assert len(table) == 655
    for row, tsv in zip(author["group_ledger"], table):
        assert all(tsv[k] == str(row.get(k) or "") for k in "source_group_id unit_id edition locus raw left_separator right_separator status contribution definition".split())
    count = sum(len(v) for v in results.values())
    assert len(results) == 376 and count == audit["check_count"] == 3285
    print(json.dumps({"status": "FROZEN_TABLE_COMPATIBILITY_PASS", "lower_rows": 376, "routine_row_checks": count, "source_groups": 655, "meanings_selected": False, "confirmed_words": 0}))


if __name__ == "__main__":
    main()
