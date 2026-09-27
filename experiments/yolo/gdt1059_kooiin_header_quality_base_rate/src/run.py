#!/usr/bin/env python3
"""Replay GDT623's fixed page-head rule on every admitted Herbal-A head."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from math import comb
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = ROOT / "experiments/yolo/gdt1059_kooiin_header_quality_base_rate"
OLDER = ROOT / "experiments/yolo/gdt623_temperament_orientation_frequency/src/run.py"


def load_predecessor():
    spec = importlib.util.spec_from_file_location("gdt623_fixed", OLDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    old = load_predecessor()
    pages = old.safe_pages()
    tokens, guard = old.guarded_tokens(pages)
    by_page = defaultdict(list)
    for row in tokens:
        by_page[row["page"]].append(row)
    heads = {}
    for row in tokens:
        if row["section"] == "H" and row["language"] == "A" and row["token_index"] == "1" and row["code"].startswith("@"):
            heads.setdefault(row["page"], row)

    rows = []
    for page, head in sorted(heads.items()):
        contact, family = old.first_quality(head, by_page, 3)
        rows.append({
            "page": page,
            "head_locus": head["locus"],
            "head_surface": head["eva"],
            "contact_locus": contact["locus"] if contact else "NONE",
            "contact_surface": contact["eva"] if contact else "NONE",
            "family": family,
            "kooiin_exact": int(head["eva"] == "kooiin"),
        })
    assert {r["page"] for r in rows if r["kooiin_exact"]} == {"f2v", "f29v"}
    assert all(r["family"] == "TCH" for r in rows if r["kooiin_exact"])
    assert not any(r["page"].startswith("f84") or r["page"] == "f1r" for r in rows)

    fields = ("page", "head_locus", "head_surface", "contact_locus", "contact_surface", "family", "kooiin_exact")
    out = HERE / "artifacts/HEAD_CONTACTS.tsv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    pools = {}
    for name, excluded in (("all_heads", set()), ("exclude_exact", {"f2v", "f29v"}), ("exclude_exact_and_sibling", {"f2v", "f29v", "f3v"})):
        pool = [row for row in rows if row["page"] not in excluded]
        counts = Counter(row["family"] for row in pool)
        n = len(pool)
        contacted = n - counts["NONE"]
        pair_n = comb(n, 2) if n > 1 else 0
        pools[name] = {
            "heads": n,
            "families": {family: counts[family] for family in ("KCH", "KSH", "TCH", "TSH", "NONE")},
            "tch_share_all_heads": counts["TCH"] / n if n else None,
            "tch_share_contacted": counts["TCH"] / contacted if contacted else None,
            "tch_pair_fraction_all_heads": comb(counts["TCH"], 2) / pair_n if pair_n else None,
            "same_nonempty_family_pair_fraction_all_heads": sum(comb(counts[family], 2) for family in ("KCH", "KSH", "TCH", "TSH")) / pair_n if pair_n else None,
        }
    result = {
        "experiment": "GDT1059",
        "status": "DESCRIPTIVE_CAPACITY_ONLY",
        "guard": guard,
        "token_count": len(tokens),
        "selected_exact": [r for r in rows if r["kooiin_exact"]],
        "pools": pools,
        "claim_ceiling": "No p-value, temperature direction, rootstock meaning, or confirmed translation. Post-hoc selected heads; page dependence and missing independent ownership remain.",
    }
    (HERE / "artifacts/RESULT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"head_count": len(rows), "pools": pools}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
