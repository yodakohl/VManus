#!/usr/bin/env python3
"""Independent integrity validator for GDT229."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> None:
    checks: list[tuple[str, bool]] = []
    result = json.loads((ROOT / "gdt229_result.json").read_text())
    lattice = read("gdt229_q13_semantic_role_lattice.tsv")
    summaries = read("gdt229_q13_record_role_summaries.tsv")
    worlds = read("gdt229_candidate_worlds.tsv")
    inter = read("gdt227_q13_abstract_interlinear.tsv")
    checks += [("fields_701", len(lattice) == len(inter) == 701), ("records_33", len(summaries) == 33), ("worlds_4", len(worlds) == 4)]
    ikeys = {(r["page"], r["record_id"], r["field_ordinal"], r["locus"], r["source_tokens"], r["page_hosts"]) for r in inter}
    lkeys = {(r["page"], r["record_id"], r["field_ordinal"], r["locus"], r["source_tokens"], r["page_hosts"]) for r in lattice}
    checks.append(("interlinear_exact_join", ikeys == lkeys))
    checks.append(("no_f84", all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in lattice)))
    checks.append(("all_hypothesis_only", all(r["claim_state"] == "LATENT_ROLE_HYPOTHESIS_ONLY_NO_GLOSS" for r in lattice)))
    checks.append(("world_roles_none", all(r["semantic_claim"] == "NONE" for r in worlds)))
    lead_counts = Counter(r["leading_latent_document_role"] for r in lattice)
    checks.append(("lead_counts", dict(sorted(lead_counts.items())) == result["leading_role_counts"]))
    checks.append(("field_result_count", result["fields"] == len(lattice)))
    checks.append(("record_result_count", result["records"] == len(summaries)))
    for kind in ("inputs", "outputs", "documents", "implementation"):
        for name, digest in result[kind].items():
            checks.append((f"hash:{name}", sha(name) == digest))
    clean = dict(result); stored = clean.pop("content_hash")
    canonical = hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    checks.append(("content_hash", stored == canonical))
    checks += [(f"f84_{k}_false", v is False) for k, v in result["f84"].items()]
    failed = [name for name, ok in checks if not ok]
    validation = {"experiment": result["experiment"], "status": "PASS" if not failed else "FAIL", "checks_passed": sum(ok for _, ok in checks), "checks_total": len(checks), "failed": failed, "result_sha256": sha("gdt229_result.json")}
    (ROOT / "gdt229_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("FAIL " + ",".join(failed))
    print(f"PASS {validation['checks_passed']}/{validation['checks_total']}")


if __name__ == "__main__":
    main()
