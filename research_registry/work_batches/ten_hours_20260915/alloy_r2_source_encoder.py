#!/usr/bin/env python3
"""Prospective R2 source-only spelling alternative; no unknown-text input."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import string

D = Path(__file__).resolve().parent
R1_HASH = "5048251b43b1c3ba996e3a23a235ce3c865ceea00a2328de1cef68a4578d93e6"
S0_CODE_HASH = "bc04278d040217de9b7d97bd08943429374f97c3a36d02d38001f54e900f5ce3"
PAYLOAD = list("0123456789ABC") + ["NUM", "QREF", "RREF", "MIXED", "HOLE"]
CONTEXTS = {"GRADES": [(0, 0)]}
CONTEXTS.update({h: [(1, 0)] for h in ["TARGET", "TOTAL", "FIRST", "ALTERNATIVELY"]})
CONTEXTS.update({h: [(e, m) for e in [0, 1] for m in [0, 1]]
                 for h in ["SETQ", "ASSERTQ", "ASSERTWEIGHTS"]})
CONTEXTS.update({h: [(0, 0), (1, 0)] for h in ["SETR", "YIELD"]})
CONTEXTS.update({h: [(1, 0), (1, 1)]
                 for h in ["ADD", "SUB", "MUL", "DIV", "PORTION", "SCALE", "REPEAT_FILL"]})
CONTEXTS.update({h: [(1, 0)] for h in ["MASS", "FINE", "GRADE", "MIX"]})
Q_HEADS = {"ADD", "SUB", "MUL", "DIV", "MASS", "FINE", "GRADE"}
R_HEADS = {"PORTION", "MIX", "SCALE", "REPEAT_FILL"}


def label(head, entry, mixed):
    return f"{head}@{entry}{mixed}"


def transform(groups):
    out = []
    previous = None
    for group in groups:
        head = group[1]
        payload = group[2:-1]
        entry = int(previous is not None and previous not in {"FIRST", "ALTERNATIVELY"})
        mixed = int("MIXED" in payload)
        kind = "Q" if head in Q_HEADS else "R" if head in R_HEADS else "S"
        assert group[0] == f"ENTRY{entry}"
        assert group[-1] == f"AGREE_{kind}{mixed}"
        assert (entry, mixed) in CONTEXTS[head]
        assert all(atom in PAYLOAD for atom in payload)
        out.append([label(head, entry, mixed), *payload])
        previous = head
    return out


def build():
    source = D.parents[1] / "proposals/raw_alloy_r1_compositional_group_code.json"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == R1_HASH
    r1 = json.loads(source.read_text())["design"]
    code = D / "alloy_finite_grammar.py"
    assert hashlib.sha256(code.read_bytes()).hexdigest() == S0_CODE_HASH
    spec = importlib.util.spec_from_file_location("owned_s0_for_r2", code)
    s0 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s0)
    allomorphs = [label(h, e, m) for h, contexts in CONTEXTS.items() for e, m in contexts]
    atoms = PAYLOAD + allomorphs
    assert len(PAYLOAD) == 18 and len(allomorphs) == 39
    assert len(atoms) == len(set(atoms)) == 57
    accounts = {}
    for name, original in r1["source_example_streams"].items():
        item = copy.deepcopy(original)
        item["groups"] = transform(original["groups"])
        assert len(item["groups"]) == original["generated_group_count"]
        assert all(new[1:] == old[2:-1] for new, old in zip(item["groups"], original["groups"]))
        assert s0.evaluate(item["complete_semantic_account"]) == item["semantic_outputs"]
        accounts[name] = item
    # A legal code existence witness, assigned before any target inspection.
    witness = dict(zip(["GRADES@00", "TARGET@10", "TOTAL@10", "FIRST@10"], "abcd"))
    available = iter(a + b for a in string.ascii_lowercase[4:] for b in string.ascii_lowercase)
    witness.update({atom: next(available) for atom in atoms if atom not in witness})
    words = list(witness.values())
    assert len(words) == len(set(words)) == 57
    assert not any(a != b and b.startswith(a) for a in words for b in words)
    example = accounts["two_source_alternatives"]["groups"]
    first_four = ["".join(witness[a] for a in g) for g in example[:4]]
    assert len({g[0] for g in first_four}) == 4 and len(first_four[3]) == 1
    generated = accounts["new_grades_4_6_10_total12"]["groups"]
    fine = next(g for g in generated if g[0] == "FINE@10")
    yield_group = next(g for g in generated if g[0] == "YIELD@10")
    assert fine[1:] == yield_group[1:] == ["RREF", "1"]
    entry = r1["entry_context_check"]
    # Context witness groups are transformed with their explicitly certified contexts.
    entry_pair = [[label("SETR", e, 0), *entry[k][2:-1]]
                  for e, k in [(0, "entry_group"), (1, "later_group")]]
    return {"status": "PROSPECTIVE_SOURCE_ONLY_NO_TARGET_INPUT_OR_FIT",
            "payload_atoms": PAYLOAD, "operator_contexts": CONTEXTS,
            "allomorph_atoms": allomorphs, "atoms": atoms,
            "accounts": accounts,
            "code_existence_witness": {"dictionary": witness,
                "first_four_source_groups": first_four,
                "distinct_initials_in_first_four": 4,
                "first_marker_group_length": 1,
                "prefix_free": True, "purpose": "Logical contrast only; no target fit"},
            "shared_payload_witness": {"fine_group": fine, "yield_group": yield_group,
                "identical_tail": ["RREF", "1"]},
            "entry_context_witness": entry_pair,
            "arithmetic_rival_inherited_unchanged": r1["source_only_rival_check"],
            "r1_proposal_sha256": R1_HASH, "s0_code_sha256": S0_CODE_HASH}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
