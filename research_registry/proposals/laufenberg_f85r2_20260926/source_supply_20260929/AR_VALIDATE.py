#!/usr/bin/env python3
"""Reproduce AR input identity/scope and whole-page occurrence obligations.

This checks literal data, never source Latin, semantic fits or independence.
Run from repository root; no mixed transcription source is opened.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main():
    receipt = json.loads((D / "AR_PACKET_RECEIPT.json").read_text())
    source = ROOT / receipt["source"]
    assert sha(source) == receipt["source_sha256"]
    for name, expected in receipt["sha256"].items():
        assert sha(D / name) == expected, name
    rows = read_tsv(source)
    assert len(rows) == 473
    assert all(r["locus"].startswith("f85r2.") for r in rows)
    assert Counter(r["edition"] for r in rows) == {"ZL3b": 156, "IT2a": 157, "RF1b": 160}
    packet = read_tsv(D / "AR_W_PACKET.tsv")
    assert packet == [r for r in rows if r["block"] == "W"]
    assert Counter(r["edition"] for r in packet) == {"ZL3b": 36, "IT2a": 35, "RF1b": 37}
    forms = sorted({r["ivtff_group_raw"] for r in packet if r["edition"] == "ZL3b"})
    assert forms == receipt["profile_forms"] and len(forms) == 29
    batches = json.loads((D / "AR_W_PROFILES.json").read_text())["batches"]
    assert sorted(p["form"] for b in batches for p in b["profiles"]) == forms
    for batch in batches:
        inputs = batch["source_receipt"]["inputs"]
        assert inputs["selector_count"] == len(inputs["selectors"]) == 179
        assert all(not s.startswith("f84") and s != "f116v" for s in inputs["selectors"])
        assert inputs["reader_policy"] == "alternate readings, never pooled"
    obligations = []
    for form in forms:
        for edition in ("ZL3b", "IT2a", "RF1b"):
            hits = [r for r in rows if r["edition"] == edition and r["ivtff_group_raw"] == form]
            obligations.append({"form": form, "edition": edition,
                "W_count": sum(r["block"] == "W" for r in hits),
                "outside_W_count": sum(r["block"] != "W" for r in hits),
                "outside_W_ids": "|".join(r["source_group_id"] for r in hits if r["block"] != "W")})
    with (D / "AR_OCCURRENCE_OBLIGATIONS.tsv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(obligations[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(obligations)
    frozen = {
        "AR_AUTHOR.md": "e1388725f820b4f4ff2a64b35ef3a9e2c048a94a0af8a443f05634f853f7a465",
        "AR_AUTHOR.json": "c947a24b97c729e2a3beabe875263013f8c206e9c13832fddf1e9261f284e4b1",
    }
    for name, expected in frozen.items():
        assert sha(D / name) == expected, name
    author = json.loads((D / "AR_AUTHOR.json").read_text())
    entries = {e["form"]: e for e in author["entries"]}
    assert len(entries) == 8
    # Preserve the original's erroneous 65-character hash; record, never silently fix it.
    wrong_hash = author["target"]["projection_sha256"]
    actual_hash = receipt["sha256"]["AR_W_PACKET.tsv"]
    assert wrong_hash == actual_hash + "a"
    bindings = []
    for r in rows:
        form = r["ivtff_group_raw"]
        if form not in entries:
            continue
        line = [s for s in rows if s["edition"] == r["edition"] and s["locus"] == r["locus"]]
        i = next(i for i, s in enumerate(line) if s["source_group_id"] == r["source_group_id"])
        left = line[i-1]["ivtff_group_raw"] if i else "LINE_START"
        right = line[i+1]["ivtff_group_raw"] if i+1 < len(line) else "LINE_END"
        applicable = "atomic guess only; surrounding construction unassigned"
        if form == "shedy" and left in ("ar", "or"):
            applicable = "rule2 participant/greater fragment; not a complete clause"
        elif form == "qokshey":
            suffix = [s["ivtff_group_raw"] for s in line[i+1:i+4]]
            if suffix == ["qose?y", "or", "aiin"]:
                applicable = "rule3 guessed counterpart-water fragment"
            else:
                applicable = "rule3 not bound: alternate raw groups unassigned"
        bindings.append({**r, "frozen_N1": entries[form]["N1"], "frozen_N2": entries[form]["N2"],
                         "previous_raw": left, "next_raw": right, "literal_rule_application": applicable})
    with (D / "AR_FIXED_BINDINGS.tsv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(bindings[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(bindings)
    print(json.dumps({"status": "PASS", "rows": 473, "W": 108, "outside_W": 365,
        "profile_forms": 29, "obligation_rows": len(obligations),
        "fixed_value_rows": len(bindings), "W_fixed_value_rows": sum(r["block"] == "W" for r in bindings),
        "outside_W_fixed_value_rows": sum(r["block"] != "W" for r in bindings),
        "W_lexical_coverage_by_reader": dict(Counter(r["edition"] for r in bindings if r["block"] == "W")),
        "preserved_metadata_error": "frozen author projection hash has one extra trailing a",
        "scope": "identity, exact projection and literal frozen-value obligations only; no semantic validation"}))


if __name__ == "__main__":
    main()
