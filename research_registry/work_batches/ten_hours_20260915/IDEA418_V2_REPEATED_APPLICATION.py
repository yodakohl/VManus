#!/usr/bin/env python3
"""Deterministic V2 state trace for the raw IDEA418 f80v.7-.13 hypothesis.

This is a bounded worked constructor over the already exposed W56 excerpt.
The content hypothesis is deliberately concrete but provisional: ``qokchdy``
is FILTER (apply the same separation/filtering operation to the current
material), ``qoty`` is the condition CLEAR_ENOUGH, and ``qokal`` is a receiver
or treatment target. Unknown groups are retained as observations; they are
not silently used as operators, closures, or filler.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


PARAGRAPH = {
    "f80v.7": "polshol tchey qokol shedy qotshey saly kchey stolpchy",
    "f80v.8": "olteedy qokaiin shedy qokain sheol qokchdy qokchdy qoty dy",
    "f80v.9": "tchdy qol tol tal taldain chckhy qokal dol checthy qokal ly",
    "f80v.10": "sol sheey qokaiin shcthy dolshedy qokal shecthy qotainol",
    "f80v.11": "tol sheedy qokar olky rorcheey sheckhy qotain chedy rol",
    "f80v.12": "ycheol kain shey qokain chedy qokol olkain sh{cthh}y l",
    "f80v.13": "lor ar ol olor chey koldy",
}


@dataclass
class State:
    current_item: str | None = None
    current_state: str | None = None
    condition: str | None = None
    next_item: int = 0
    next_state: int = 0
    next_target: int = 0
    target_in_line: str | None = None
    input_in_line: str | None = None
    traces: list[dict[str, Any]] = field(default_factory=list)
    unknowns: list[dict[str, Any]] = field(default_factory=list)
    operations: list[dict[str, Any]] = field(default_factory=list)
    targets: list[dict[str, Any]] = field(default_factory=list)
    conditions: list[dict[str, Any]] = field(default_factory=list)

    def new_state(self) -> str:
        out = f"S{self.next_state}"
        self.next_state += 1
        return out

    def new_target(self, locus: str) -> str:
        out = f"T{self.next_target}"
        self.next_target += 1
        self.target_in_line = out
        self.targets.append({"id": out, "locus": locus})
        return out


def reduce_paragraph() -> dict[str, Any]:
    state = State()
    for locus, raw in PARAGRAPH.items():
        # The report-owned line boundary scopes target-frame identity. This is
        # an input boundary, not a claimed sentence or semantic reset.
        state.target_in_line = None
        groups = raw.split()
        line_trace = []
        for index, token in enumerate(groups, start=1):
            event: dict[str, Any]
            if token == "qokaiin":
                state.current_item = f"I{state.next_item}"
                state.next_item += 1
                # A newly written input supersedes the active material state;
                # this is an explicit typed-input rule, not a line reset.
                state.current_state = None
                state.input_in_line = state.current_item
                event = {"op": "INPUT_ITEM", "item": state.current_item}
            elif token == "qokain":
                if state.input_in_line is not None:
                    source = state.input_in_line
                    state.current_item = f"O{state.next_item}"
                    state.next_item += 1
                    event = {"op": "OUTPUT_ITEM", "item": state.current_item, "from": source}
                else:
                    state.current_item = f"O{state.next_item}"
                    state.next_item += 1
                    event = {"op": "OUTPUT_ITEM", "item": state.current_item, "from": "UNBOUND_PRIOR"}
            elif token == "qokchdy":
                if state.current_item is None:
                    event = {"op": "INVALID_OPERATION", "reason": "no_current_item"}
                else:
                    # A second FILTER consumes the prior filtered state. If
                    # no state exists yet it consumes the current item.
                    before = state.current_state or state.current_item
                    after = state.new_state()
                    state.current_state = after
                    event = {
                        "op": "APPLY_OP",
                        "operator": "FILTER",
                        "surface": "qokchdy",
                        "input": before,
                        "output": after,
                    }
                    state.operations.append({
                        "locus": locus,
                        "surface": "qokchdy",
                        "operator": "FILTER",
                        "input": before,
                        "output": after,
                        "condition": None,
                    })
            elif token == "qoty":
                target = state.current_state or state.current_item
                event = {"op": "CONDITION", "condition": "CLEAR_ENOUGH", "target": target, "surface": "qoty"}
                state.condition = "CLEAR_ENOUGH"
                state.conditions.append({"locus": locus, "target": target, "condition": "CLEAR_ENOUGH"})
                if state.operations:
                    state.operations[-1]["condition"] = "CLEAR_ENOUGH"
            elif token == "qokal":
                if state.target_in_line is None:
                    target = state.new_target(locus)
                    event = {
                        "op": "TARGET_NEW",
                        "target": target,
                        "target_kind": "RECEIVER_VESSEL",
                        "subject": state.current_state or state.current_item,
                        "surface": "qokal",
                    }
                else:
                    target = state.target_in_line
                    event = {
                        "op": "TARGET_REASSERT",
                        "target": target,
                        "target_kind": "RECEIVER_VESSEL",
                        "subject": state.current_state or state.current_item,
                        "surface": "qokal",
                    }
            else:
                event = {"op": "UNKNOWN_GROUP", "surface": token}
                state.unknowns.append({"locus": locus, "group": index, "surface": token})
            row = {"locus": locus, "group": index, "surface": token, "event": event}
            line_trace.append(row)
            state.traces.append(row)
        # Explicit input boundary for target frames only; item/state and the
        # operation trace are not silently reset here.
        state.target_in_line = None
        state.input_in_line = None

    return {
        "paragraph_scope": list(PARAGRAPH),
        "operation_occurrences": state.operations,
        "target_occurrences": state.targets,
        "condition_occurrences": state.conditions,
        "unknown_group_count": len(state.unknowns),
        "unknown_groups": state.unknowns,
        "trace": state.traces,
        "final_state": {
            "current_item": state.current_item,
            "current_state": state.current_state,
            "condition": state.condition,
            "next_item": state.next_item,
            "next_state": state.next_state,
            "next_target": state.next_target,
        },
    }


def independent_entry_rival() -> dict[str, Any]:
    # Same observed forms, but every qokchdy starts a fresh operation and every
    # qokal occurrence allocates a fresh target, including f80v.9's repeat.
    op_inputs = ["O0", "O1"]
    targets = ["T0", "T1", "T2"]
    return {"operations": [{"operator": "qokchdy", "input": x, "output": f"R{i}"} for i, x in enumerate(op_inputs)], "targets": targets}


if __name__ == "__main__":
    print(json.dumps({"constructor": reduce_paragraph(), "independent_entry_rival": independent_entry_rival()}, indent=2))
