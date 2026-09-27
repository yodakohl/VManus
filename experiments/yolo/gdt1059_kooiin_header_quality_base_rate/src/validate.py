#!/usr/bin/env python3
"""Independent arithmetic and scope checks for GDT1059's saved projection."""

import csv
import json
from collections import Counter
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


def main() -> int:
    result = json.loads((HERE / "artifacts/RESULT.json").read_text(encoding="utf-8"))
    with (HERE / "artifacts/HEAD_CONTACTS.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == len({r["page"] for r in rows})
    assert not any(r["page"].startswith("f84") or r["page"] == "f1r" for r in rows)
    exact = [r for r in rows if r["head_surface"] == "kooiin"]
    assert {r["page"] for r in exact} == {"f2v", "f29v"}
    assert all(r["family"] == "TCH" and r["kooiin_exact"] == "1" for r in exact)
    checks = 4
    for name, excluded in (("all_heads", set()), ("exclude_exact", {"f2v", "f29v"}), ("exclude_exact_and_sibling", {"f2v", "f29v", "f3v"})):
        pool = [r for r in rows if r["page"] not in excluded]
        counts = Counter(r["family"] for r in pool)
        saved = result["pools"][name]
        assert saved["heads"] == len(pool)
        assert saved["families"] == {f: counts[f] for f in ("KCH", "KSH", "TCH", "TSH", "NONE")}
        denom = comb(len(pool), 2)
        contact = len(pool) - counts["NONE"]
        assert abs(saved["tch_share_all_heads"] - counts["TCH"] / len(pool)) < 1e-12
        assert abs(saved["tch_share_contacted"] - counts["TCH"] / contact) < 1e-12
        assert abs(saved["tch_pair_fraction_all_heads"] - comb(counts["TCH"], 2) / denom) < 1e-12
        assert abs(saved["same_nonempty_family_pair_fraction_all_heads"] - sum(comb(counts[f], 2) for f in ("KCH", "KSH", "TCH", "TSH")) / denom) < 1e-12
        checks += 6
    output = {"experiment": "GDT1059", "status": "PASS", "checks": checks, "rows": len(rows)}
    (HERE / "artifacts/VALIDATION.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
