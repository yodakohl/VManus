#!/usr/bin/env python3
"""Frozen B source/dictionary/barrier bookkeeping only; no semantic parser."""
import collections
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
BOUND = {
    "FT_AUTHOR_PROCEDURE.md": "f5613ed300f601892c771688dce67a9815b1a6f1b7a9c051a3e493ff120aa559",
    "FT_AUTHOR_PROCEDURE.json": "207ea6274ecbc085124465b78702d3a392d354597fa5d7fe8e42f659fcb2b05d",
    "FT_PROCEDURE_DERIVATION.tsv": "ea13755baccbf63152e3016817d00b1625a84732134947500d4f12ebca4c0e18",
    "FT_SOURCE_PACKET.json": "31de602d3d3a6b1c58caf5563159a3f757fe05995971f9319b769c4bbb95fa26",
}


def main():
    for name, expected in BOUND.items():
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == expected, name
    author = json.loads((BASE / "FT_AUTHOR_PROCEDURE.json").read_text())
    packet = json.loads((BASE / "FT_SOURCE_PACKET.json").read_text())
    with (BASE / "FT_PROCEDURE_DERIVATION.tsv").open() as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    dictionary = {d["whole_form"]: d for d in author["semantic_whole_definitions"]}
    assert len(dictionary) == 93 and len(author["rules"]) == 16
    assert len(author["assumptions_and_prices"]) == 26
    assert len(author["main_constructions"]) == 20 and len(author["embedded_constructions"]) == 7
    source = {g["source_group_id"]: g for c in packet["contexts"] for g in c["groups"]}
    assert len(rows) == len(source) == len({r["source_group_id"] for r in rows}) == 655
    fields = {"raw_group": "ivtff_group_raw", **{k: k for k in "edition locus source_group_index left_separator right_separator paragraph_start paragraph_end unit_position".split()}}
    groups = collections.defaultdict(list)
    for row in rows:
        original = source[row["source_group_id"]]
        assert row["edition"] == row["source_group_id"].split("|")[0]
        assert all(row[k] == str(original[v]) for k, v in fields.items())
        groups[row["unit_id"], row["edition"]].append(row)
        d = dictionary.get(row["raw_group"])
        if d:
            assert row["definition_id"] == d["definition_id"] and row["semantic_type"] == d["type"]
            assert row["contribution"] == d["meaning_C0"] and row["required_arguments"] == d["required_arguments_or_registers"]
        else:
            assert row["status"] == "UNKNOWN" and not row["definition_id"]
        if row["status"] in {"UNKNOWN", "KNOWN_BUT_BLOCKED"}:
            assert row["missing_dependency"]
            assert all(not row[k] for k in ["actual_binding_refs_C0", "individual_effect_C0", "manual_trace_checkpoint", "construction_checkpoint_emitted_here"])
        else:
            assert row["actual_binding_refs_C0"] and row["individual_effect_C0"]
    metadata_gaps = []
    for context in packet["contexts"]:
        unit = groups[context["unit_id"], context["edition"]]
        assert [r["source_group_id"] for r in unit] == [g["source_group_id"] for g in context["groups"]]
        blocked = False
        for row in unit:
            if row["status"] in {"UNKNOWN", "KNOWN_BUT_BLOCKED"}:
                blocked = True
            if blocked:
                assert row["status"] in {"UNKNOWN", "KNOWN_BUT_BLOCKED"}
        cov = next(c for c in author["coverage"] if c["unit_id"] == context["unit_id"] and c["edition"] == context["edition"])
        assert cov["literal_groups"] == len(unit)
        assert cov["connected_manual_account"] == (not blocked)
        if blocked and cov["first_gap_or_dependency"] is None:
            metadata_gaps.append(next(r["source_group_id"] for r in unit if r["status"] in {"UNKNOWN", "KNOWN_BUT_BLOCKED"}))
    primary = [r for r in rows if r["edition"] == "IT2a" and r["unit_id"].startswith("F83")]
    assert len(primary) == 123 and sum(r["status"] == "C0_TYPED_CONTRIBUTION" for r in primary) == 119
    assert sum(r["status"] == "C0_CAPTION_CONTRIBUTION" for r in primary) == 4
    templates = author["main_constructions"] + author["embedded_constructions"]
    for template in templates:
        matched = [r for r in primary if r["construction_id"] == template["construction_id"]]
        emitted = [r for r in matched if r["construction_checkpoint_emitted_here"]]
        assert len(emitted) == 1 and emitted[0] == matched[-1]
        assert emitted[0]["manual_trace_checkpoint"] == template["state_checkpoint"]
    assert dict(collections.Counter(r["status"] for r in rows)) == author["row_status_counts"]
    assert metadata_gaps == ["RF1b|f83r.50|G001"]
    print(json.dumps({"status": "SOURCE_DICTIONARY_BARRIER_BOOKKEEPING_PASS", "source_rows": 655,
                      "primary_IT_prose": 119, "primary_IT_captions": 4, "once_only_IT_checkpoints": 27,
                      "semantic_parser_validated": False, "meanings_selected": False,
                      "coverage_metadata_missing_gap": metadata_gaps}))


if __name__ == "__main__":
    main()
