#!/usr/bin/env python3
"""Independent integrity checks for the frozen comparator corpus."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORPORA = ROOT / "gdt003_structural_fingerprint_corpora.json.gz"
MANIFEST = ROOT / "gdt003_structural_fingerprint_corpus_manifest.tsv"
PROVENANCE = ROOT / "gdt003_structural_fingerprint_source_provenance.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[tuple[str, bool]] = []
    with gzip.open(CORPORA, "rt", encoding="utf-8") as handle:
        corpus = json.load(handle)
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        manifest = list(csv.DictReader(handle, delimiter="\t"))
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    records = corpus["records"]
    counts = Counter(row["corpus_id"] for row in records)
    folds: dict[str, Counter[str]] = defaultdict(Counter)
    for row in records:
        folds[row["corpus_id"]][row["fold_id"]] += 1

    checks.append(("schema", corpus["schema"] == "GDT003_STRUCTURAL_FINGERPRINT_CORPORA_V1"))
    checks.append(("provenance_corpus_hash", provenance["corpora_sha256"] == sha(CORPORA)))
    checks.append(("provenance_manifest_hash", provenance["manifest_sha256"] == sha(MANIFEST)))
    checks.append(("unique_manifest_ids", len(manifest) == len({row["corpus_id"] for row in manifest})))
    checks.append(("record_fields", all(set(row) == {"corpus_id", "fold_id", "unit_id", "occurrence_index", "form", "sample_rank"} for row in records)))
    checks.append(("forms_nonempty", all(row["form"] and " " not in row["form"] for row in records)))
    for row in manifest:
        corpus_id = row["corpus_id"]
        checks.append((f"count_{corpus_id}", counts[corpus_id] == int(row["sampled_tokens"])))
        checks.append((f"fold_count_{corpus_id}", len(folds[corpus_id]) == int(row["folds"])))
        if row["capacity_state"] == "MATCHED_12000":
            checks.append((f"matched_{corpus_id}", counts[corpus_id] == 12000 and set(folds[corpus_id].values()) == {1000}))
    checks.append(("voynich_matched", counts["VOYNICH_MATCHED"] == 12000))
    checks.append(("middle_armenian_not_padded", counts["MIDDLE_ARMENIAN_UD"] == 0))
    checks.append(("old_georgian_disclosed_low_capacity", counts["OLD_GEORGIAN_UD"] == 6093))
    checks.append(("no_f84_string", all("f84r" not in str(value) for row in records for value in row.values())))
    checks.append(("no_phoneme_or_translation_fields", not any({"phoneme", "lemma", "translation", "gloss"} & set(row) for row in records)))
    failures = [name for name, passed in checks if not passed]
    result = {"status": "PASS" if not failures else "FAIL", "checks": len(checks), "failures": failures, "corpora_sha256": sha(CORPORA), "manifest_sha256": sha(MANIFEST)}
    print(json.dumps(result, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
