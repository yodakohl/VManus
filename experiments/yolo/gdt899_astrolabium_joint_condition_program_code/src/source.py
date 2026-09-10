"""Read and compile the frozen source-only condition packet.

No target reader, source-text repair, optional atom, or predicate inference lives
here.  Each of the six header orders must be used globally by the caller.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROLES = ("location", "mercury", "companion")
HEADER_ORDERS = tuple(itertools.permutations(ROLES))


def compile_program(program: dict, header_order) -> tuple[str, ...]:
    order = tuple(header_order)
    if order not in HEADER_ORDERS:
        raise ValueError("header_order must permute the three global roles")
    return tuple(
        atom
        for sequence in (
            *(program["header_factors"][role] for role in order),
            program["after_header"],
            program["body_atoms"],
        )
        for atom in sequence
    )


def load_source(path) -> dict:
    packet = json.loads(Path(path).read_text(encoding="utf-8"))
    if packet.get("schema") != "GDT899_SOURCE_PROGRAMS_V1":
        raise ValueError("unsupported source packet schema")
    programs = packet.get("programs")
    if not isinstance(programs, list) or len(programs) != 24:
        raise ValueError("the complete two-register source requires24 blocks")
    expected_ids = {f"{register}{house:02}" for register in ("MS", "MJ")
                    for house in range(1, 13)}
    if {p["id"] for p in programs} != expected_ids:
        raise ValueError("missing or duplicated source block")
    if packet.get("header_orders") != [list(order) for order in HEADER_ORDERS]:
        raise ValueError("incomplete or altered header permutation family")
    seen = set()
    for program in programs:
        if set(program["header_factors"]) != set(ROLES):
            raise ValueError("incorrect header roles")
        if program["after_header"] != ["PARTILE"]:
            raise ValueError("the obligatory PARTILE atom changed")
        if program["body_atoms"] != [atom for event in program["events"]
                                      for atom in event["atoms"]]:
            raise ValueError("source trace and event provenance disagree")
        for sequence in (*program["header_factors"].values(),
                         program["after_header"], program["body_atoms"]):
            if not isinstance(sequence, list) or not sequence:
                raise ValueError("source factors and body must be nonempty")
            if any(not isinstance(a, str) or not a or a == "UNCERTAIN"
                   for a in sequence):
                raise ValueError("invalid source atom")
            seen.update(sequence)
    if sorted(seen) != packet.get("vocabulary"):
        raise ValueError("source vocabulary does not match programs")
    return packet


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("source_packet")
    args = parser.parse_args()
    source = load_source(args.source_packet)
    compiled = [compile_program(program, order)
                for order in HEADER_ORDERS for program in source["programs"]]
    print(json.dumps({"status": "SOURCE_STRUCTURE_PASS",
                      "programs": len(source["programs"]),
                      "header_orders": len(HEADER_ORDERS),
                      "compiled_programs": len(compiled),
                      "vocabulary": len(source["vocabulary"])}))
