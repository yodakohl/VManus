#!/usr/bin/env python3
"""Independent, nonimporting validation of GDT027 retained results."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt027_result.json"
VALIDATION = ROOT / "gdt027_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def classify(family: str) -> str:
    if "QJB" in family or "QKB" in family:
        return "Q"
    if "LJB" in family or "LKB" in family:
        return "L"
    return "OTHER"


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    n, row, col = a + b + c + d, a + b, a + c
    lo, hi = max(0, row - (n - col)), min(row, col)

    def log_probability(x: int) -> float:
        return (
            math.lgamma(col + 1)
            - math.lgamma(x + 1)
            - math.lgamma(col - x + 1)
            + math.lgamma(n - col + 1)
            - math.lgamma(row - x + 1)
            - math.lgamma(n - col - row + x + 1)
            - math.lgamma(n + 1)
            + math.lgamma(row + 1)
            + math.lgamma(n - row + 1)
        )

    observed = log_probability(a)
    selected = [log_probability(x) for x in range(lo, hi + 1) if log_probability(x) <= observed + 1e-12]
    peak = max(selected)
    return min(1.0, math.exp(peak) * sum(math.exp(x - peak) for x in selected))


def hypergeom(n: int, k: int, m: int) -> np.ndarray:
    out = np.zeros(min(k, m) + 1)
    denominator = math.comb(n, m)
    for x in range(max(0, m - (n - k)), min(m, k) + 1):
        out[x] = math.comb(k, x) * math.comb(n - k, m - x) / denominator
    return out


def conditional(
    keys: set[tuple[str, int]],
    q_keys: set[tuple[str, int]],
    context: dict[tuple[str, int], dict[str, object]],
    level: str,
) -> tuple[float, float, int]:
    strata: dict[tuple[object, ...], list[tuple[bool, int]]] = defaultdict(list)
    for key in keys:
        x = context[key]
        geography = x["page"] if level == "PAGE" else x["physical_folio"] if level == "FOLIO" else x["section"]
        strata[(geography, x["state"], x["position_bin"])].append((key in q_keys, int(x["post_dy"])))
    observed = 0
    expected = numerator = denominator = 0.0
    informative = 0
    law = np.array([1.0])
    for values in strata.values():
        n = len(values)
        m = sum(q for q, _ in values)
        k = sum(y for _, y in values)
        if not (0 < m < n and 0 < k < n):
            continue
        informative += 1
        overlap = sum(q and y for q, y in values)
        observed += overlap
        expected += m * k / n
        weight = m * (n - m) / n
        numerator += weight * (overlap / m - (k - overlap) / (n - m))
        denominator += weight
        law = np.convolve(law, hypergeom(n, k, m))
    effect = numerator / denominator if denominator else 0.0
    p = 1.0
    if denominator:
        distance = abs(observed - expected)
        p = min(1.0, float(law[np.abs(np.arange(len(law)) - expected) >= distance - 1e-12].sum()))
    return effect, p, informative


def close(left: object, right: object) -> bool:
    return abs(float(left) - float(right)) < 7e-12


def main() -> None:
    checks: list[tuple[str, bool]] = []
    result = json.loads(RESULT.read_text())
    content = dict(result)
    digest = content.pop("result_content_sha256")
    checks.extend(
        [
            ("schema", result["schema"] == "GDT027_Q_L_RIGHT_EDGE_PORTABILITY_RESULT_V1"),
            ("content_hash", digest == csha(content)),
            ("status", result["status"] == "Q_L_HISTORY_BIT_RIGHT_EDGE_PORTABILITY_PROVISIONAL_LOW_CAPACITY"),
        ]
    )
    for section in ("inputs", "implementation", "outputs"):
        for name, digest in result[section].items():
            checks.append((f"hash:{section}:{name}", sha(ROOT / name) == digest))

    inventory = read("gdt016_group_state_inventory.tsv")
    checks.extend(
        [
            ("inventory_count", len(inventory) == result["inventory_groups"] == 15592),
            ("inventory_f84r_free", not any(row["locus"].startswith("f84r") for row in inventory)),
        ]
    )
    lines: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inventory:
        lines[row["locus"]].append(row)

    lookup: dict[tuple[str, int], dict[str, str]] = {}
    previous: dict[tuple[str, int], dict[str, str] | None] = {}
    context: dict[tuple[str, int], dict[str, object]] = {}
    all_keys: set[tuple[str, int]] = set()
    q_keys: set[tuple[str, int]] = set()
    for locus, line in lines.items():
        line.sort(key=lambda row: int(row["group_index"]))
        for i, row in enumerate(line):
            branch = classify(row["family_surface"])
            if row["currier"] != "B" or branch == "OTHER":
                continue
            count = int(row["group_count"])
            coordinate = (int(row["group_index"]) - 1) / (count - 1) if count > 1 else 0.5
            key = (locus, int(row["group_index"]))
            all_keys.add(key)
            lookup[key] = row
            previous[key] = line[i - 1] if i else None
            if branch == "Q":
                q_keys.add(key)
            context[key] = {
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "section": row["section"],
                "state": row["record_state"],
                "position_bin": min(3, int(coordinate * 4)),
                "post_dy": int(i > 0 and line[i - 1]["record_state"] == "DY_RESOLUTION"),
            }

    partitions: list[tuple[str, set[tuple[str, int]]]] = [
        ("ALL", set(all_keys)),
        ("DY", {key for key in all_keys if lookup[key]["record_state"] == "DY_RESOLUTION"}),
        ("NON_DY", {key for key in all_keys if lookup[key]["record_state"] != "DY_RESOLUTION"}),
    ]
    for state in sorted({lookup[key]["record_state"] for key in all_keys}):
        partitions.append((state, {key for key in all_keys if lookup[key]["record_state"] == state}))

    stored = {row["partition"]: row for row in read("gdt027_right_edge_portability_tests.tsv")}
    checks.append(("partition_names", set(stored) == {name for name, _ in partitions}))
    for name, keys in partitions:
        row = stored[name]
        positive = q_keys & keys
        negative = keys - positive
        q_post = sum(int(context[key]["post_dy"]) for key in positive)
        l_post = sum(int(context[key]["post_dy"]) for key in negative)
        q_not, l_not = len(positive) - q_post, len(negative) - l_post
        raw_p = fisher_two_sided(q_post, q_not, l_post, l_not) if positive and negative else 1.0
        odds = q_post * l_not / (q_not * l_post) if q_not and l_post else math.inf if q_post and l_not else 0.0
        exact = (
            int(row["groups"]) == len(keys)
            and int(row["q_groups"]) == len(positive)
            and int(row["l_groups"]) == len(negative)
            and [int(row[x]) for x in ("q_postdy", "q_not_postdy", "l_postdy", "l_not_postdy")]
            == [q_post, q_not, l_post, l_not]
            and close(row["raw_fisher_p"], raw_p)
            and (close(row["raw_odds_ratio"], odds) if math.isfinite(odds) else row["raw_odds_ratio"] == "inf")
        )
        checks.append((f"partition_counts:{name}", exact))
        for level in ("PAGE", "FOLIO", "SECTION"):
            effect, p, informative = conditional(keys, positive, context, level)
            checks.append(
                (
                    f"conditional:{name}:{level}",
                    close(row[f"{level.lower()}_effect"], effect)
                    and close(row[f"{level.lower()}_exact_p"], p)
                    and int(row[f"{level.lower()}_informative_strata"]) == informative,
                )
            )

    examples = read("gdt027_non_dy_postcheckpoint_examples.tsv")
    expected_examples = []
    for key in sorted(all_keys):
        row = lookup[key]
        if row["record_state"] == "DY_RESOLUTION" or not context[key]["post_dy"]:
            continue
        prior = previous[key]
        assert prior is not None
        expected_examples.append(
            {
                "locus": key[0],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "group_index": str(key[1]),
                "branch": classify(row["family_surface"]),
                "current_state": row["record_state"],
                "previous_dy_token": prior["token"],
                "current_token": row["token"],
                "current_family": row["family_surface"],
                "claim_state": "NON_DY_POST_CHECKPOINT_EXAMPLE_NOT_MEANING",
            }
        )
    checks.extend(
        [
            ("examples_exact", examples == expected_examples),
            ("result_counts", len(all_keys) == result["ql_groups"] == 1633 and len(stored) == result["partitions"] == 11 and len(examples) == result["examples"] == 63),
            (
                "non_dy_snapshot",
                all(
                    str(result["non_dy"][key]) == value
                    for key, value in stored["NON_DY"].items()
                    if key not in {
                        "page_effect",
                        "page_exact_p",
                        "folio_effect",
                        "folio_exact_p",
                        "section_effect",
                        "section_exact_p",
                    }
                )
                and all(
                    close(result["non_dy"][key], stored["NON_DY"][key])
                    for key in (
                        "page_effect",
                        "page_exact_p",
                        "folio_effect",
                        "folio_exact_p",
                        "section_effect",
                        "section_exact_p",
                    )
                ),
            ),
            ("f84r_flags", result["f84r"] == {"input_contains_rows": False, "opened": False, "retained": False, "joined": False, "scored": False}),
        ]
    )
    report = " ".join((ROOT / "GDT027_Q_L_RIGHT_EDGE_PORTABILITY_REPORT.md").read_text().lower().split())
    ledger = (ROOT / "GDT002_YOLO_LEDGER.tsv").read_text()
    checks.extend(
        [
            ("claim_ceiling", all(term in report for term in ("primary page-matched", "provisional", "not a confirmed independent slot", "f84r was not opened", "no role"))),
            ("ledger", ledger.count("GDT027_CKPT001") == 1),
        ]
    )

    failures = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT027_Q_L_RIGHT_EDGE_PORTABILITY_VALIDATION_V1",
        "status": "PASS" if not failures else "FAIL",
        "checks": len(checks),
        "failures": failures,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent reconstruction of every Q/L partition, raw Fisher tests, page/folio/section conditional exact tests, all 63 examples, hashes, f84r exclusion, ledger, and claim ceiling.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps(validation, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
