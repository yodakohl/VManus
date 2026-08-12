#!/usr/bin/env python3
"""Independent reconstruction of the LTG001 capacity artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
RESULT = RESULTS / "ltg001_latent_channel_capacity.json"
TABLE = RESULTS / "ltg001_latent_channel_capacity.tsv"
REPORT = RESULTS / "ltg001_latent_channel_capacity_report.md"
VALIDATION = RESULTS / "ltg001_latent_channel_capacity_validation.json"


def folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.IGNORECASE)
    if match is None:
        raise AssertionError(page)
    return match.group(1).lower()


def fold(value: str) -> int:
    return int.from_bytes(hashlib.sha256(("LTG001_FOLD_V1|" + value).encode()).digest()[:4], "big") % 5


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    source = list(csv.DictReader(GROUPS.open(encoding="utf-8", newline=""), delimiter="\t"))
    positions = disagreements = 0
    disagreement_folios = set()
    dominant_deleted_folios = set()
    currier = Counter()
    folds = Counter()
    triplet_count = Counter()
    triplet_folios = defaultdict(set)
    events = []
    contexts = defaultdict(list)
    per_family = defaultdict(Counter)
    family_folios = defaultdict(set)
    ambiguous_folios = defaultdict(set)
    for row in source:
        if row["strict_zero_alternative"] != "1":
            continue
        pf = folio(row["page"])
        codes = [row[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        assert all(len(values) == len(row["family_surface"]) for values in codes)
        for fam, z, i, r in zip(row["family_surface"], *codes):
            assert z[0] == i[0] == r[0] == fam
            positions += 1
            per_family[fam]["positions"] += 1
            obs = {"ZL": z[1:], "IT": i[1:], "RF": r[1:]}
            if len(set(obs.values())) > 1:
                disagreements += 1
                per_family[fam]["disagreements"] += 1
                family_folios[fam].add(pf)
                disagreement_folios.add(pf)
                currier[row["currier"] or "BLANK"] += 1
                folds[fold(pf)] += 1
                key = (fam, z, i, r)
                triplet_count[key] += 1
                triplet_folios[key].add(pf)
                if (z, i, r) != ("B1", "B1", "Ba"):
                    dominant_deleted_folios.add(pf)
            for target, left, right in (("ZL", "IT", "RF"), ("IT", "ZL", "RF"), ("RF", "ZL", "IT")):
                if obs[left] == obs[right]:
                    continue
                event = (pf, target, fam, obs[left], obs[right])
                events.append(event)
                per_family[fam]["ambiguous_events"] += 1
                ambiguous_folios[fam].add(pf)
                contexts[event[1:]].append(pf)
    supported = Counter()
    for pf, target, fam, left, right in events:
        if sum(other != pf for other in contexts[(target, fam, left, right)]) >= 5:
            supported[fam] += 1
    table = list(csv.DictReader(TABLE.open(encoding="utf-8", newline=""), delimiter="\t"))
    assert [row["family"] for row in table] == sorted(per_family)
    checks = 0
    for row in table:
        fam = row["family"]
        triplets = [key for key in triplet_count if key[0] == fam]
        expected = {
            "positions": per_family[fam]["positions"],
            "disagreements": per_family[fam]["disagreements"],
            "disagreement_folios": len(family_folios[fam]),
            "triplet_types": len(triplets),
            "triplet_types_three_folios": sum(len(triplet_folios[key]) >= 3 for key in triplets),
            "ambiguous_events": per_family[fam]["ambiguous_events"],
            "ambiguous_folios": len(ambiguous_folios[fam]),
            "loo_supported_ambiguous_events": supported[fam],
        }
        for key, value in expected.items():
            assert int(row[key]) == value
            checks += 1
    counts = result["counts"]
    assert positions == counts["strict_positions"] == 95451; checks += 1
    assert disagreements == counts["disagreement_positions"] == 3535; checks += 1
    assert len(events) == counts["ambiguous_prediction_events"]; checks += 1
    assert sum(supported.values()) == counts["loo_supported_ambiguous_events"]; checks += 1
    assert len(disagreement_folios) == counts["disagreement_folios"]; checks += 1
    assert triplet_count[("B", "B1", "B1", "Ba")] == counts["dominant_B1_B1_Ba_positions"]; checks += 1
    assert len(dominant_deleted_folios) == counts["dominant_policy_deleted_folios"]; checks += 1
    assert {str(k): folds[k] for k in range(5)} == result["fold_disagreements"]; checks += 1
    assert dict(sorted(currier.items())) == result["by_currier_disagreements"]; checks += 1
    assert all(result["gates"].values()); checks += 1
    assert result["status"] == "PASS_IDENTIFIABLE_CROSS_FOLIO_CHANNEL"; checks += 1
    assert result["outputs"][TABLE.name] == sha(TABLE); checks += 1
    assert REPORT.read_text(encoding="utf-8").startswith("# LTG001 latent transcription-channel capacity\n"); checks += 1
    validation = {"status": "PASS_INDEPENDENT_LTG001_CAPACITY_RECONSTRUCTION", "checks": checks}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
