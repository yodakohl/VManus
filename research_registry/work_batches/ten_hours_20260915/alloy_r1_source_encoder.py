#!/usr/bin/env python3
"""Encode owned S0 source ASTs into abstract R1 groups; no unknown-text input."""
from collections import Counter
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

D = Path(__file__).resolve().parent
S0_JSON_HASH = "b852e2ec8e191bebdc904d1274a79174b5fa08bb3cd24980128286895dbab109"
S0_CODE_HASH = "bc04278d040217de9b7d97bd08943429374f97c3a36d02d38001f54e900f5ce3"
EXTRA_ATOMS = ["HOLE", "ENTRY0", "ENTRY1", "AGREE_Q0", "AGREE_Q1",
               "AGREE_R0", "AGREE_R1", "AGREE_S0", "AGREE_S1"]
Q_HEADS = {"ADD", "SUB", "MUL", "DIV", "MASS", "FINE", "GRADE"}
R_HEADS = {"PORTION", "MIX", "SCALE", "REPEAT_FILL"}


def atomic(x):
    return isinstance(x, str) or x[0] in {"num", "qref", "rref", "mixed"}


def atom_spelling(x):
    if isinstance(x, str):
        assert x in "ABC" and len(x) == 1
        return [x]
    op, *args = x
    if op in {"num", "qref", "rref"}:
        return [op.upper(), *str(args[0])]
    assert op == "mixed" and all(a[0] == "num" for a in args)
    return ["MIXED"] + [z for a in args for z in atom_spelling(a)]


def prefix_atoms(x):
    """S0 semantic atoms, before R1's grouping and agreement components."""
    if atomic(x):
        return atom_spelling(x)
    op, *args = x
    out = [op.upper()]
    if op in {"setq", "setr"}:
        out.extend(str(args.pop(0)))
    return out + [z for a in args for z in prefix_atoms(a)]


def node_cores(x):
    assert not atomic(x)
    op, *args = x
    core = [op.upper()]
    if op in {"setq", "setr"}:
        core.extend(str(args.pop(0)))
    children = []
    for arg in args:
        if atomic(arg):
            core.extend(atom_spelling(arg))
        else:
            core.append("HOLE")
            children.append(arg)
    out = [core]
    for child in children:
        out.extend(node_cores(child))
    return out


def account_nodes(a):
    grades = [z for kind, grade in zip("ABC", a["grades"]) for z in [kind, grade]]
    out = [["grades", *grades], ["target", a["target"]], ["total", a["mass"]]]
    for i, branch in enumerate(a["branches"]):
        out.append(["first" if i == 0 else "alternatively"])
        out.extend(branch)
    return out


def encode(a):
    nodes = account_nodes(a)
    cores = [core for node in nodes for core in node_cores(node)]
    source_atoms = [atom for node in nodes for atom in prefix_atoms(node)]
    retained_atoms = [atom for core in cores for atom in core if atom != "HOLE"]
    assert Counter(source_atoms) == Counter(retained_atoms)
    groups = []
    previous = None
    for core in cores:
        head = core[0]
        entry = 0 if previous is None or previous in {"FIRST", "ALTERNATIVELY"} else 1
        kind = "Q" if head in Q_HEADS else "R" if head in R_HEADS else "S"
        mixed = int("MIXED" in core)
        groups.append([f"ENTRY{entry}", *core, f"AGREE_{kind}{mixed}"])
        previous = head
    return {"groups": groups, "generated_group_count": len(groups),
            "source_semantic_atom_count": len(source_atoms),
            "all_semantic_atom_multiplicities_preserved": True,
            "hole_count": sum(core.count("HOLE") for core in cores)}


def build():
    source = D / "ALLOY_FINITE_GRAMMAR.json"
    code = D / "alloy_finite_grammar.py"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == S0_JSON_HASH
    assert hashlib.sha256(code.read_bytes()).hexdigest() == S0_CODE_HASH
    data = json.loads(source.read_text())
    spec = importlib.util.spec_from_file_location("owned_s0", code)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    atoms = data["renderer"]["atoms"] + EXTRA_ATOMS
    assert len(atoms) == len(set(atoms)) == 47
    examples = dict(data["examples"])
    n = lambda value: ["num", str(value)]
    r = lambda index: ["rref", index]
    portion = lambda kind, amount: ["portion", kind, n(amount)]
    examples["new_grades_4_6_10_total12"] = {
        "grades": [n(4), n(6), n(10)], "target": n(8), "mass": n(12),
        "branches": [[
            ["setr", 0, ["mix", portion("A", 2), portion("B", 3)]],
            ["assertq", ["grade", r(0)], ["mixed", n(5), n(1), n(5)]],
            ["setr", 1, ["mix", r(0), portion("C", 7)]],
            ["assertweights", r(1), n(2), n(3), n(7)],
            ["assertq", ["fine", r(1)], n(96)],
            ["yield", r(1)]
        ]]
    }
    accounts = {}
    for name, account in examples.items():
        result = encode(account)
        result["complete_semantic_account"] = account
        result["semantic_outputs"] = module.evaluate(account)
        assert all(atom in atoms for group in result["groups"] for atom in group)
        accounts[name] = result
    wrong = copy.deepcopy(data["examples"]["new_4_4_12"])
    wrong["branches"][0][1][2][2][1] = "A"
    wrong["branches"][0][2] = ["assertweights", r(1), n(16), n(4), n(0)]
    wrong_groups = encode(wrong)
    try:
        module.evaluate(wrong)
    except AssertionError:
        semantic_rejection = True
    else:
        raise AssertionError("Wrong-fineness fixture unexpectedly passed")
    later = copy.deepcopy(data["examples"]["new_4_4_12"])
    later["branches"][0].insert(0, ["setq", 0, n(4)])
    later["branches"][0][1][2][1][2] = ["qref", 0]
    assert module.evaluate(later) == accounts["new_4_4_12"]["semantic_outputs"]
    original_set = next(g for g in accounts["new_4_4_12"]["groups"]
                        if g[1:3] == ["SETR", "0"])
    later_set = next(g for g in encode(later)["groups"] if g[1:3] == ["SETR", "0"])
    assert original_set[1:] == later_set[1:]
    assert original_set[0] == "ENTRY0" and later_set[0] == "ENTRY1"
    return {"status": "SOURCE_ONLY_SYMBOLIC_ENCODING_NO_TARGET_FIT",
            "atoms": atoms, "accounts": accounts,
            "rival_check": {"typed_recipe_encoded": True,
                            "generated_groups": wrong_groups["generated_group_count"],
                            "written_header_arithmetic_rejected": semantic_rejection,
                            "weights": [16, 4, 0], "mass": 20, "fine": 64},
            "entry_context_check": {"both_complete_accounts_semantically_valid": True,
                                    "entry_group": original_set,
                                    "later_group": later_set,
                                    "extra_definition_is_used": True},
            "s0_json_sha256": S0_JSON_HASH, "s0_code_sha256": S0_CODE_HASH}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
