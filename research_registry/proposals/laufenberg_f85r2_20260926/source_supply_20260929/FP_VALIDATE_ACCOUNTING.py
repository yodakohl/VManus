#!/usr/bin/env python3
"""Source/accounting validation only; neither a parser nor a meaning test."""
import csv
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
EXPECTED = {
    "FM_TARGET.json": "55713ecdd6df28c7cddb8f02bf93ccc26134a599ec90919d9bf4513020be9199",
    "FO_AUTHOR.json": "0a28d6f096b560fe7d70302ff8bfc55e0e78c31ee77529a386f3ed630de58b09",
    "FP_WHOLE_AUTHOR.json": "5750753c45f8de14ac8ac13a31ff4beeb5deb98a652a8342f1f2fb0ce295f393",
    "FP_WHOLE_CHECK_CONTRACT.json": "714f168147f99e1da7cd23a5c6ce13453d253fde0df1ded27ba294e5be638adf",
}
for name, expected in EXPECTED.items():
    assert hashlib.sha256((D / name).read_bytes()).hexdigest() == expected, name
target = json.loads((D / "FM_TARGET.json").read_text())
author = json.loads((D / "FP_WHOLE_AUTHOR.json").read_text())
assert author["base_FM_TARGET_sha256"] == EXPECTED["FM_TARGET.json"]
assert author["base_FO_AUTHOR_sha256"] == EXPECTED["FO_AUTHOR.json"]
contexts = target["contexts"]
assert [(c["context"], len(c["groups"])) for c in contexts] == [("f85r1.1-6", 60), ("f80v.30-37", 69)]
assert len(author["rows"]) == 69
assert len({r["ID"] for r in author["rows"]}) == 69
for group, row in zip(contexts[1]["groups"], author["rows"]):
    assert row["position"] == group["position"]
    assert row["ID"] == group["source_group_id"]
    assert row["raw"] == group["ivtff_group_raw"]
    assert "".join(row["segments"]) == row["raw"]
assert [r["position"] for r in author["rows"] if r["status"] == "UNBOUND"] == list(range(63,70))
assert all(r["state"] is None for r in author["rows"][62:])
columns = ["context", "position", "source_group_id", "raw", "left_separator", "right_separator", "segments", "candidate_contribution", "typed_input", "typed_output", "author_status", "independent_meaning_status"]
with (D / "FP_CANDIDATE_TABLE.tsv").open("w", newline="") as out:
    writer = csv.DictWriter(out, fieldnames=columns, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for context in contexts:
        for group in context["groups"]:
            row = author["rows"][group["position"]-1] if context["context"] == "f80v.30-37" else None
            writer.writerow({
                "context": context["context"], "position": group["position"],
                "source_group_id": group["source_group_id"], "raw": group["ivtff_group_raw"],
                "left_separator": group["left_separator"], "right_separator": group["right_separator"],
                "segments": json.dumps(row["segments"], ensure_ascii=False) if row else "UNBOUND_OUTSIDE_NEW_VERSION",
                "candidate_contribution": row["contribution"] if row else "No FP derivation",
                "typed_input": row["typed_input"] if row else "UNBOUND",
                "typed_output": row["typed_output"] if row else "UNBOUND",
                "author_status": row["status"] if row else "UNBOUND_OUTSIDE_NEW_VERSION",
                "independent_meaning_status": "NOT_CONFIRMED",
            })
result = {"status": "SOURCE_ACCOUNTING_PASS_ONLY", "hashes": EXPECTED,
          "source_groups": 129, "f80_authored_rows": 69, "candidate_prefix_annotations": 62,
          "f80_unbound": 7, "other_context_unbound": 60, "total_unbound": 67,
          "raw_ids_and_segments_exact": True, "source_separators_preserved_in_table": True,
          "grammar_execution_tested": False, "meaning_tested": False,
          "complete_contexts": 0, "confirmed_words": 0}
(D / "FP_ACCOUNTING.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
print(json.dumps(result, ensure_ascii=False))
