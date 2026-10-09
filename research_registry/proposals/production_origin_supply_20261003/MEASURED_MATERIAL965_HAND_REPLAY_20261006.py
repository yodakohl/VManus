#!/usr/bin/env python3
"""Small post-manual lesson replay. No manuscript input or source encoder."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(name):
    return json.loads((HERE / name).read_text())


def sha(name):
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


raw_name = "HUMAN_MEASURED_MATERIAL_LIST_RAW_20261006.json"
challenge_name = "HUMAN_MEASURED_MATERIAL965_CHALLENGE_20261006.json"
expected_name = "HUMAN_MEASURED_MATERIAL965_HELD_EXPECTATION_20261006.json"
readback_name = "HUMAN_MEASURED_MATERIAL965_ROOT_READBACK_20261006.json"
raw = read(raw_name)["design"]
challenge = read(challenge_name)
expected = read(expected_name)
manual = read(readback_name)
for name, digest in challenge["contract_files_and_sha256"].items():
    assert sha(name) == digest, name
assert sha(challenge_name) == manual["challenge_sha256"]
assert sha(expected_name) == challenge["held_expectation_sha256"]
assert sha(expected_name) == manual["held_expectation_sha256"]

alphabet = set(raw["working_units"])
names = raw["literal_names"]
selectors = names["selectors_in_order"]
ordinary = names["ordinary_letters"]
rare = names["rare_characters_in_order"]
assert len(alphabet) == 22
assert len(selectors) == 21 and "q" not in selectors
assert len(ordinary) == 21 and len(rare) == 74
assert set(ordinary) | set(rare) == {chr(i) for i in range(32, 127)}
assert len(set(ordinary) | set(rare)) == 95


def name_decode(word):
    assert word[:3] == ["r", "r", "d"] and word[-2:] == ["q", "q"]
    payload = word[3:-2]
    assert payload
    answer = []
    i = 0
    while i < len(payload):
        if payload[i] != "q":
            answer.append(ordinary[selectors.index(payload[i])])
            i += 1
        else:
            assert i + 2 < len(payload)
            j = 21 * selectors.index(payload[i + 1]) + selectors.index(payload[i + 2])
            assert j < 74
            answer.append(rare[j])
            i += 3
    return "".join(answer)


for i, ch in enumerate(ordinary):
    assert name_decode(["r", "r", "d", selectors[i], "q", "q"]) == ch
for i, ch in enumerate(rare):
    payload = ["q", selectors[i // 21], selectors[i % 21]]
    assert name_decode(["r", "r", "d"] + payload + ["q", "q"]) == ch

controls = {
    ("r", "r", "a"): "ADD", ("r", "r", "i"): "MIX",
    ("r", "r", "n"): "FORBID", ("r", "r", "y"): "END",
    ("r", "r", "l"): "IF_EMPTY", ("r", "r", "k"): "END_IF",
    ("r", "r", "p"): "END_MESSAGE",
}
roots = {("f", "p", "t"): "water stock", ("t", "p", "f"): "leaf stock",
         ("p", "t", "f"): "oil stock"}


def material_decode(word):
    remainder = list(word)
    history = []
    while tuple(remainder[-3:]) in {("r", "r", "o"), ("r", "r", "e")}:
        history.append("DRIED" if remainder[-1] == "o" else "GROUND")
        remainder = remainder[:-3]
    assert remainder and all(remainder[i:i + 2] != ["r", "r"] for i in range(len(remainder)))
    base = roots[tuple(remainder)]
    assert not history or base == "leaf stock"
    return {"base": base, "history": list(reversed(history))}


words = [w for row in challenge["physical_rows"] for w in row]
assert all(w and set(w) <= alphabet for w in words)
assert all(w != ["r", "r", "ch"] for w in words), "This narrow replay has no split word."
tree, stack = [], []
current = tree
i = 0
while i < len(words):
    op = controls[tuple(words[i])]
    i += 1
    if op == "END_MESSAGE":
        assert not stack and i == len(words)
        current.append({"op": op})
        break
    if op == "END_IF":
        assert len(stack) == 1 and current
        current = stack.pop()
        continue
    assert op in {"ADD", "MIX", "FORBID", "IF_EMPTY"}
    vessel = name_decode(words[i])
    i += 1
    node = {"op": op, "vessel": vessel}
    current.append(node)
    if op == "IF_EMPTY":
        assert not stack
        node["body"] = []
        stack.append(current)
        current = node["body"]
        continue
    materials = []
    while tuple(words[i]) not in controls:
        materials.append(material_decode(words[i]))
        i += 1
    assert controls[tuple(words[i])] == "END"
    i += 1
    assert (op == "MIX" and not materials) or (op != "MIX" and materials)
    if op != "MIX":
        node["portions" if op == "ADD" else "materials"] = materials
assert tree and tree[-1] == {"op": "END_MESSAGE"}


def projected_source(value):
    if isinstance(value, list):
        return [projected_source(v) for v in value]
    if isinstance(value, dict):
        return {k: projected_source(v) for k, v in value.items() if k not in {"scope", "evaluate"}}
    return value


assert tree == projected_source(expected["source_message"])
assert [x["name"] for x in manual["name_decoding"]] == ["Bela", "Ivo"]


def count_message(groups):
    by_role = {role: {"groups": 0, "units": 0} for role in ("controls", "vessel_names", "materials")}
    for w in groups:
        role = "controls" if tuple(w) in controls else "vessel_names" if w[:3] == ["r", "r", "d"] else "materials"
        by_role[role]["groups"] += 1
        by_role[role]["units"] += len(w)
    c = by_role["controls"]["groups"]
    v = by_role["vessel_names"]["groups"]
    m = by_role["materials"]["groups"]
    assert c == 2 * v + 1  # One complete message; neither lesson has continuation.
    assert 2 * len(groups) == 2 * m + 3 * c - 1
    return {"physical_groups": len(groups), "working_units": sum(map(len, groups)), "roles": by_role}


# The exposed lesson's compact strings are parsed against its stated22-unit alphabet.
# Reject ambiguous parses instead of treating roman characters as working drawings.
def unit_parse(text):
    parses = [[]]
    positions = {0: parses}
    for pos in range(len(text)):
        for prefix in positions.get(pos, []):
            for unit in alphabet:
                if text.startswith(unit, pos):
                    positions.setdefault(pos + len(unit), []).append(prefix + [unit])
    found = positions.get(len(text), [])
    assert len(found) == 1, (text, len(found))
    return found[0]


exposed = [unit_parse(w) for row in raw["complete_exposed_hand_message"]["written_words_by_instruction"] for w in row]
result = {
    "status": "PASS_NARROW_POST_MANUAL_SOURCE_HELD_LESSON_REPLAY",
    "input_hashes": {str((HERE / name).relative_to(ROOT)): sha(name) for name in
                     [raw_name, challenge_name, expected_name, readback_name] + list(challenge["contract_files_and_sha256"])[1:]},
    "checks": ["All95 literal characters have unique table readback", "Challenge contract/source/readback hashes match",
               "Physical rows preserve the one cross-row ADD", "Full parsed instruction tree matches the previously held source",
               "Exact quantities and ordered preparation tails match", "Control/name/material count identity holds for both complete lessons"],
    "manual_scope_checks": "Root separately compared every prohibition/guard distinction with the held source. This small replay checks the tree, not a general execution engine.",
    "decoded_instruction_tree": tree,
    "exposed_lesson_counts": count_message(exposed),
    "source_held_challenge_counts": count_message(words),
    "limitations": "Only invented lessons. No manuscript data, native meaning, source corpus, gap measurement, global statistical fit or general encoder. Root had already frozen the manual readback before this replay was written."
}
out = HERE / "MEASURED_MATERIAL965_HAND_REPLAY_RESULT_20261006.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": result["status"], "exposed": result["exposed_lesson_counts"], "challenge": result["source_held_challenge_counts"]}, ensure_ascii=False))
