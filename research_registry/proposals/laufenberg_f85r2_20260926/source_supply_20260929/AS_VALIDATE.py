#!/usr/bin/env python3
"""Replay AS literal obligations and check its manually authored graph.

Not a decoder, grammar learner, source collator or semantic confirmation.
Only owned three-page projections are read; no mixed raw TSV is opened.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main():
    assert sha(D / "AS_AUTHOR.json") == "14a8806d042f51113d3228e7c37b4884e38108cbbc04a8f2c3ce502d9ad69a83"
    assert sha(D / "AS_AUTHOR.md") == "7b70d2329950e889aac060e8e3cfe2eb5cacea0dc9ee83c6d2b4b0ce47badd6b"
    author = json.loads((D / "AS_AUTHOR.json").read_text())
    for name, expected in author["hashes"].items():
        assert sha(D / name) == expected, name
    registration = json.loads((D / "AS_REGISTRATION.json").read_text())
    assert sha(D / "F_TARGET_RAW.tsv") == registration["target_projection_sha256"]
    raw = rows(D / "F_TARGET_RAW.tsv")
    assert len(raw) == 891
    assert Counter(r["edition"] for r in raw) == {"ZL3b": 303, "IT2a": 296, "RF1b": 292}
    assert {r["page"] for r in raw} == {"f22r", "f32r", "f42v"}
    unit = rows(D / "AS_PARAGRAPH.tsv")
    loci = {"f22r.4", "f22r.5", "f22r.6"}
    assert unit == [r for r in raw if r["locus"] in loci]
    assert Counter(r["edition"] for r in unit) == {"ZL3b": 22, "IT2a": 22, "RF1b": 21}
    lexicon = {r["form"]: r for r in author["lexicon"]}
    assert len(lexicon) == 21 and len(author["rules"]) == 9
    assert set(lexicon) == {r["ivtff_group_raw"] for r in unit}
    profiles = json.loads((D / "AS_PROFILES.json").read_text())["batches"]
    assert {p["form"] for b in profiles for p in b["profiles"]} == set(lexicon)
    for batch in profiles:
        inputs = batch["source_receipt"]["inputs"]
        assert inputs["selector_count"] == len(inputs["selectors"]) == 179
        assert all(not p.startswith("f84") and p != "f116v" for p in inputs["selectors"])
    token_table = rows(D / "AS_TOKEN_TABLE.tsv")
    assert len(token_table) == len(unit)
    for source, token in zip(unit, token_table):
        assert all(token[k] == v for k, v in source.items())
        entry = lexicon[source["ivtff_group_raw"]]
        assert token["C0_value"] == entry["value"] and token["C0_type"] == entry["type"]
    lines = defaultdict(list)
    for row in raw:
        lines[(row["edition"], row["locus"])].append(row)
    expected = []
    for row in raw:
        if row["ivtff_group_raw"] not in lexicon:
            continue
        line = lines[(row["edition"], row["locus"])]
        i = next(i for i, r in enumerate(line) if r["source_group_id"] == row["source_group_id"])
        entry = lexicon[row["ivtff_group_raw"]]
        expected.append({**row, "C0_value": entry["value"], "C0_type": entry["type"],
            "previous_raw": line[i-1]["ivtff_group_raw"] if i else "LINE_START",
            "next_raw": line[i+1]["ivtff_group_raw"] if i+1 < len(line) else "LINE_END",
            "first_unit": str(row["locus"] in loci).lower()})
    assert rows(D / "AS_FIXED_BINDINGS.tsv") == expected
    graph = author["program"]
    ids = [graph[k]["id"] for k in ("material", "container", "wearer", "authority")]
    head = graph["location"]["head"]["id"]
    assert len(set(ids + [head])) == 5
    assert graph["binding"] == {"predicate": "qokchy", "material": "W", "container": "B"}
    assert graph["placement"]["object"] == "B" and graph["placement"]["wearer"] == "P"
    sites = graph["placement"]["site"]
    assert sites["operator"] == "oky" and [s["kind"] for s in sites["alternatives"]] == ["neck", "arm"]
    assert graph["indication"]["kind"] == "quartan_fever" and graph["indication"]["affected_person"] == "P"
    assert graph["authority"]["kind"] == "Dioscorides"
    print(json.dumps({"status": "PASS", "scope": "frozen identities, exact literal projections/values and internal hand-authored graph only",
        "rows": 891, "first_unit_rows": 65, "assigned_rows": len(expected),
        "assigned_rows_elsewhere": sum(r["first_unit"] == "false" for r in expected),
        "unknown_rows": len(raw)-len(expected), "independent_meaning_confirmation": 0,
        "grammar_derivation_or_source_meaning_validated": False}))


if __name__ == "__main__":
    main()
