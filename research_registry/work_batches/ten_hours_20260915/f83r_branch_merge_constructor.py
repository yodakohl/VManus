#!/usr/bin/env python3
"""Source-free exploratory constructor for already exposed f83r paragraphs.

This is a deterministic semantic reduction hypothesis, not a decoder.  It
uses reusable surface parts, a finite context machine, and an explicit opaque
residual rule for forms that cannot be segmented by the declared inventory.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


P1 = {
    "f83r.25": "qokeedy qolchey qokeey qokedy chedy otal",
    "f83r.26": "otchey qokeey qoky tol shedy qokylddy",
    "f83r.27": "dain chedy qokeedy shckhedy shckhedy",
    "f83r.28": "saiin cheeky sheey qokedy shedy oldy",
    "f83r.29": "salchedy cheey qody kesd oldy",
    "f83r.30": "s okeedy qokeedy qoky saii",
}

# This is another already exposed complete report-owned paragraph used only as
# a prospective reduction check; no new transcription or image is read here.
P2 = {
    "f83r.9": "pchor checphedy qokedy lsheedy qokchdy r shedkedy qopshdy qopy",
    "f83r.10": "olkeey rchs cheeb ols aiin skal dain cthal s aiin chky lal sam",
    "f83r.11": "sor shedy qokaiin chkain shcthey qokedy okair sheedy lchedy lo",
    "f83r.12": "qockhol sheckhy otal qokeal sheckhdy al okedy qokedy qokal",
    "f83r.13": "salcheol tar shedy s altedy sair qokedy qedy lchcphedy ldar",
    "f83r.14": "qokchedy qokeedy shedy qokshedy dal lchedy qokaiin shcthy dal sy",
    "f83r.15": "saiin shedal shecthy chey tal shcthy dalchdy qotchedy lchedy",
    "f83r.16": "tchedy qokchdy cheedar chldaiin chedy qokain checthy chealror",
    "f83r.17": "dcheokedy lkeed shckhey ytaiin shechy schety",
}


# Components are semantic atoms, not English letters.  Longest-first matching
# makes every current P1 token deterministic without a whole-form dictionary.
ATOMS: Dict[str, str] = {
    "qok": "UPDATE",
    "qol": "RELATE",
    "chey": "LINK_FRAME",
    "che": "EFFECT",
    "ot": "GUARD",
    "sh": "PARTICIPANT",
    "ckh": "LIST_ITEM",
    "da": "ORDER",
    "sa": "REFERENCE",
    "qo": "STATE_REFERENCE",
    "kes": "NEGATE",
    "ol": "OWNER",
    "o": "RENEW",
    "ke": "MATERIAL",
    "t": "LOCATION",
    "s": "TOPIC",
    "e": "EXPLICIT_ARG",
    "l": "SCOPE",
    "ddy": "GUARDED_COMPLETE",
    "edy": "DECLARE_FRAME",
    "ey": "OUTCOME_FRAME",
    "y": "CONTINUE_FRAME",
    "dy": "COMPLETE_FRAME",
    "al": "TARGET_FRAME",
    "iin": "ATTRIBUTE_ARG",
    "aiin": "PARTICIPANT_ARG",
    "in": "ORDER_ARG",
    "ii": "CLOSE_FRAME",
    "ky": "DEGREE",
    "d": "NEGATIVE",
}

PREFERRED = sorted(ATOMS, key=lambda x: (-len(x), x))


@dataclass
class Context:
    next_register: int = 0
    next_participant: int = 0
    last_register: str = "u0"
    last_event: str = "ROOT"
    scope_depth: int = 0
    branch_count: int = 0
    residuals: Dict[str, str] = field(default_factory=dict)
    component_counts: Counter = field(default_factory=Counter)

    def register(self) -> str:
        value = f"u{self.next_register}"
        self.next_register += 1
        self.last_register = value
        return value

    def participant(self) -> str:
        value = f"p{self.next_participant}"
        self.next_participant += 1
        return value


def residual_class(token: str) -> str:
    """A lawful residual key, shared by exact residuals across paragraphs."""
    first = token[0] if token else "_"
    vowels = sum(ch in "aeiou" for ch in token)
    return f"R({first},{len(token) % 2},{vowels % 3})"


def segment(token: str) -> Tuple[List[Tuple[str, str]], str | None]:
    """Greedy declared-component segmentation with a finite residual fallback."""
    rest = token
    pieces: List[Tuple[str, str]] = []
    while rest:
        match = next((a for a in PREFERRED if rest.startswith(a)), None)
        if match is None:
            key = residual_class(token)
            return [(token, key)], key
        pieces.append((match, ATOMS[match]))
        rest = rest[len(match) :]
    return pieces, None


def reduce_token(token: str, ctx: Context) -> dict:
    pieces, residual = segment(token)
    for atom, role in pieces:
        ctx.component_counts[atom] += 1

    roles = [role for _, role in pieces]
    atoms = [atom for atom, _ in pieces]
    frame = next((r for r in reversed(roles) if r.endswith("FRAME") or r in {"NEGATIVE", "DEGREE", "ORDER_ARG", "ATTRIBUTE_ARG", "PARTICIPANT_ARG"}), "OPAQUE")
    root = roles[0]

    if residual:
        ctx.residuals.setdefault(residual, token)
        event = {"op": "RESIDUAL_ARGUMENT", "arg": residual, "frame": frame}
    elif root == "TOPIC":
        event = {"op": "OPEN_TOPIC", "arg": "topic0"}
    elif root == "UPDATE":
        target = ctx.register()
        op = "UPDATE"
        if "GUARDED_COMPLETE" in roles:
            op = "GUARDED_UPDATE"
        elif "CONTINUE_FRAME" in roles:
            op = "CONTINUE_UPDATE"
        event = {"op": op, "input": ctx.last_event, "output": target, "frame": frame}
    elif root == "EFFECT":
        event = {"op": "EFFECT", "target": ctx.last_register, "frame": frame}
    elif root == "LINK_FRAME":
        event = {"op": "LINK", "left": ctx.last_register, "frame": frame}
    elif root == "RELATE":
        event = {"op": "RELATE", "source": ctx.last_register, "frame": frame}
    elif root == "GUARD":
        ctx.scope_depth += 1
        event = {"op": "GUARD", "scope": ctx.scope_depth, "target": ctx.last_event, "frame": frame}
    elif root == "PARTICIPANT":
        event = {"op": "BIND", "participant": ctx.participant(), "frame": frame}
    elif root == "LIST_ITEM":
        event = {"op": "LIST_ITEM", "list": f"L{ctx.branch_count}", "ordinal": 1, "frame": frame}
    elif root == "ORDER":
        ctx.branch_count += 1
        event = {"op": "ORDER", "branch": ctx.branch_count, "frame": frame}
    elif root == "REFERENCE":
        event = {"op": "REFERENCE", "target": ctx.last_register, "frame": frame}
    elif root == "STATE_REFERENCE":
        event = {"op": "STATE_REFERENCE", "target": ctx.last_register, "frame": frame}
    elif root == "NEGATE":
        event = {"op": "NEGATE", "target": ctx.last_event, "frame": frame}
    elif root == "OWNER":
        event = {"op": "OWNER_REFERENCE", "target": ctx.last_register, "frame": frame}
    elif root == "RENEW":
        event = {"op": "RENEW", "target": ctx.last_register, "frame": frame}
    elif root == "LOCATION":
        event = {"op": "LOCATE", "target": ctx.last_register, "frame": frame}
    else:
        event = {"op": root, "target": ctx.last_register, "frame": frame}
    ctx.last_event = event["op"]
    return {"token": token, "parts": atoms, "roles": roles, "event": event, "residual": residual}


def reduce_passage(records: Dict[str, str]) -> dict:
    ctx = Context()
    lines = []
    for locus, text in records.items():
        groups = [reduce_token(t, ctx) for t in text.split()]
        lines.append({"locus": locus, "raw": text, "groups": groups})
    return {
        "lines": lines,
        "component_counts": dict(ctx.component_counts),
        "residuals": ctx.residuals,
        "register_count": ctx.next_register,
        "participant_count": ctx.next_participant,
        "branch_count": ctx.branch_count,
    }


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "p1"
    records = P2 if which == "p2" else P1
    print(json.dumps(reduce_passage(records), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
