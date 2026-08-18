#!/usr/bin/env python3
"""Independent reconstruction of the frozen GDT296 renderer atlas.

This validator deliberately does not import the production scorer.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESIGN = ROOT / "gdt296_design.json"
RESULT = ROOT / "gdt296_result.json"
ATLAS = ROOT / "gdt296_host_renderer_atlas.tsv"
FOLDS = ROOT / "gdt296_host_renderer_folds.tsv"
COUNTER = ROOT / "gdt296_counterexamples.tsv"
REPORT = ROOT / "GDT296_OPAQUE_HOST_RENDERER_ATLAS_REPORT.md"
OUT = ROOT / "gdt296_validation.json"
COMPONENTS = (
    "wrapper",
    "local_frame",
    "inner_d",
    "right_family",
    "dy_closure",
    "b3",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def content_hash(value: dict) -> str:
    copy = dict(value)
    copy.pop("content_sha256", None)
    return canonical_hash(copy)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def renderer(row: dict[str, str]) -> str:
    return "|".join(row[key] for key in COMPONENTS)


def empirical_entropy(counts: Counter[str]) -> float:
    total = sum(counts.values())
    return -sum(
        (count / total) * math.log2(count / total)
        for count in counts.values()
        if count
    )


def close(a: float, b: float, tolerance: float = 5e-12) -> bool:
    return abs(a - b) <= tolerance


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    design = json.loads(DESIGN.read_text())
    result = json.loads(RESULT.read_text())
    check("design_content_hash", design["content_sha256"] == content_hash(design))
    check("result_content_hash", result["content_sha256"] == content_hash(result))
    check("design_status", design["status"] == "FROZEN_BEFORE_GDT296_ATLAS_SCORING")
    check("result_status", result["status"] == "OPAQUE_HOST_RENDERER_ATLAS_BUILT")
    check("frozen_models", design["models"] == ["HOST_CANONICAL", "HOST_X_POSITION"])
    check("no_p_values", design["p_values"] == result["p_values"] == 0)
    check(
        "no_semantic_or_substring_search",
        design["semantic_assignments"]
        == result["semantic_assignments"]
        == design["host_substrings_mined"]
        == result["host_substrings_mined"]
        == 0,
    )
    check("f84_flags", all(value in (False, 0) for value in result["f84"].values()))

    for name, expected in result["inputs"].items():
        check(f"input_hash:{name}", sha256(ROOT / name) == expected)
    for name, expected in result["documents"].items():
        check(f"document_hash:{name}", sha256(ROOT / name) == expected)
    for name, expected in result["implementation"].items():
        check(f"implementation_hash:{name}", sha256(ROOT / name) == expected)
    for name, expected in result["outputs"].items():
        check(f"output_hash:{name}", sha256(ROOT / name) == expected)

    population = read_tsv(ROOT / "gdt296_population.tsv")
    source = read_tsv(ROOT / "gdt278_native_event_inventory.tsv")
    check(
        "source_contains_no_f84",
        not any(
            row["page"].startswith("f84") or row["locus"].startswith("f84")
            for row in source
        ),
    )
    events = [row for row in source if row["control_id"] == "VOYNICH_REFERENCE"]
    hosts = {row["page_host"] for row in population}
    check("population_host_count", len(hosts) == design["population"]["hosts"] == 59)
    selected = [row for row in events if row["page_host"] in hosts]
    check("population_event_count", len(selected) == design["population"]["events"] == 5715)
    for row in population:
        host_events = [x for x in events if x["page_host"] == row["page_host"]]
        check(
            f"population:{row['page_host']}",
            int(row["events"]) == len(host_events)
            and int(row["folios"])
            == len({x["physical_folio"] for x in host_events})
            and len(host_events) >= design["population"]["minimum_events"]
            and len({x["physical_folio"] for x in host_events})
            >= design["population"]["minimum_physical_folios"],
        )

    published_atlas = {row["page_host"]: row for row in read_tsv(ATLAS)}
    published_folds = {
        (row["page_host"], row["held_folio"]): row for row in read_tsv(FOLDS)
    }
    check("atlas_host_keys", set(published_atlas) == hosts)

    alphabet = sorted({renderer(row) for row in events})
    alphabet_rank = {value: index for index, value in enumerate(alphabet)}
    alpha = float(design["alpha"])
    prior = float(design["position_prior_mass"])
    rebuilt_counts: Counter[str] = Counter()
    rebuilt_top: list[dict[str, object]] = []
    expected_fold_keys: set[tuple[str, str]] = set()

    reconstructed_rows: list[dict[str, object]] = []
    for host in sorted(hosts):
        host_events = [row for row in events if row["page_host"] == host]
        folios = sorted({row["physical_folio"] for row in host_events})
        aggregate = Counter(renderer(row) for row in host_events)
        dominant = max(alphabet, key=lambda value: (aggregate[value], -alphabet_rank[value]))
        model_bits: Counter[str] = Counter()
        model_tops: Counter[str] = Counter()
        positive_folds = 0

        for held_folio in folios:
            training = [row for row in host_events if row["physical_folio"] != held_folio]
            testing = [row for row in host_events if row["physical_folio"] == held_folio]
            host_counts = Counter(renderer(row) for row in training)
            position_counts: dict[str, Counter[str]] = defaultdict(Counter)
            for row in training:
                position_counts[row["within_field_position"]][renderer(row)] += 1
            fold_bits: Counter[str] = Counter()
            fold_tops: Counter[str] = Counter()
            for row in testing:
                actual = renderer(row)
                host_probs = {
                    value: (host_counts[value] + alpha)
                    / (len(training) + alpha * len(alphabet))
                    for value in alphabet
                }
                local = position_counts[row["within_field_position"]]
                local_total = sum(local.values())
                position_probs = {
                    value: (local[value] + prior * host_probs[value])
                    / (local_total + prior)
                    for value in alphabet
                }
                for model, probabilities in (
                    ("HOST_CANONICAL", host_probs),
                    ("HOST_X_POSITION", position_probs),
                ):
                    ordering = sorted(
                        alphabet, key=lambda value: (-probabilities[value], alphabet_rank[value])
                    )
                    loss = -math.log2(probabilities[actual])
                    model_bits[model] += loss
                    fold_bits[model] += loss
                    model_tops[f"{model}_TOP1"] += int(actual == ordering[0])
                    model_tops[f"{model}_TOP3"] += int(actual in ordering[:3])
                    fold_tops[f"{model}_TOP1"] += int(actual == ordering[0])
                    fold_tops[f"{model}_TOP3"] += int(actual in ordering[:3])
            gain = fold_bits["HOST_CANONICAL"] - fold_bits["HOST_X_POSITION"]
            positive_folds += int(gain > 0)
            key = (host, held_folio)
            expected_fold_keys.add(key)
            row = published_folds[key]
            check(
                f"fold:{host}:{held_folio}",
                int(row["events"]) == len(testing)
                and close(float(row["host_bits"]), fold_bits["HOST_CANONICAL"])
                and close(float(row["position_bits"]), fold_bits["HOST_X_POSITION"])
                and close(float(row["position_gain_bits"]), gain)
                and int(row["host_top1"]) == fold_tops["HOST_CANONICAL_TOP1"]
                and int(row["host_top3"]) == fold_tops["HOST_CANONICAL_TOP3"]
                and int(row["position_top1"]) == fold_tops["HOST_X_POSITION_TOP1"]
                and int(row["position_top3"]) == fold_tops["HOST_X_POSITION_TOP3"],
            )

        n_events = len(host_events)
        host_top1 = model_tops["HOST_CANONICAL_TOP1"] / n_events
        position_top1 = model_tops["HOST_X_POSITION_TOP1"] / n_events
        entropy = empirical_entropy(aggregate)
        if (
            host_top1 >= design["labels"]["canonical"]["top1_min"]
            and entropy <= design["labels"]["canonical"]["entropy_max_bits"]
        ):
            classification = "CANONICAL_RENDERER_CANDIDATE"
        elif (
            position_top1 >= design["labels"]["position_conditioned"]["top1_min"]
            and position_top1 - host_top1
            >= design["labels"]["position_conditioned"]["top1_improvement_min"]
        ):
            classification = "POSITION_CONDITIONED_CANDIDATE"
        else:
            classification = "VARIABLE_RENDERER"

        position_dominants: dict[str, dict[str, object]] = {}
        for position in sorted({row["within_field_position"] for row in host_events}):
            counts = Counter(
                renderer(row)
                for row in host_events
                if row["within_field_position"] == position
            )
            position_dominant = max(
                alphabet, key=lambda value: (counts[value], -alphabet_rank[value])
            )
            total = sum(counts.values())
            position_dominants[position] = {
                "tuple": position_dominant,
                "events": total,
                "share": counts[position_dominant] / total,
            }

        expected = {
            "classification": classification,
            "events": n_events,
            "folios": len(folios),
            "sections": len({row["section"] for row in host_events}),
            "hands": len({row["hand"] for row in host_events}),
            "positions": len(position_dominants),
            "renderer_tuple_types": len(aggregate),
            "empirical_entropy_bits": entropy,
            "dominant_renderer_tuple": dominant,
            "dominant_share": aggregate[dominant] / n_events,
            "lofo_host_bits_per_event": model_bits["HOST_CANONICAL"] / n_events,
            "lofo_host_top1": host_top1,
            "lofo_host_top3": model_tops["HOST_CANONICAL_TOP3"] / n_events,
            "lofo_position_bits_per_event": model_bits["HOST_X_POSITION"] / n_events,
            "lofo_position_top1": position_top1,
            "lofo_position_top3": model_tops["HOST_X_POSITION_TOP3"] / n_events,
            "position_gain_bits_per_event": (
                model_bits["HOST_CANONICAL"] - model_bits["HOST_X_POSITION"]
            )
            / n_events,
            "positive_position_folds": positive_folds,
            "position_dominants_json": json.dumps(
                position_dominants, sort_keys=True, separators=(",", ":")
            ),
        }
        actual = published_atlas[host]
        exact_fields = (
            "classification",
            "events",
            "folios",
            "sections",
            "hands",
            "positions",
            "renderer_tuple_types",
            "dominant_renderer_tuple",
            "positive_position_folds",
            "position_dominants_json",
        )
        numeric_fields = (
            "empirical_entropy_bits",
            "dominant_share",
            "lofo_host_bits_per_event",
            "lofo_host_top1",
            "lofo_host_top3",
            "lofo_position_bits_per_event",
            "lofo_position_top1",
            "lofo_position_top3",
            "position_gain_bits_per_event",
        )
        check(
            f"atlas_exact:{host}",
            all(str(expected[field]) == actual[field] for field in exact_fields),
        )
        check(
            f"atlas_numeric:{host}",
            all(close(float(expected[field]), float(actual[field])) for field in numeric_fields),
        )
        rebuilt_counts[classification] += 1
        reconstructed_rows.append({"page_host": host, **expected})

    check("fold_key_set", set(published_folds) == expected_fold_keys)
    check("classification_counts", dict(rebuilt_counts) == result["classification_counts"])
    check("result_totals", result["hosts"] == len(hosts) and result["events"] == len(selected))

    ordering = {
        "CANONICAL_RENDERER_CANDIDATE": 0,
        "POSITION_CONDITIONED_CANDIDATE": 1,
        "VARIABLE_RENDERER": 2,
    }
    reconstructed_rows.sort(
        key=lambda row: (
            ordering[row["classification"]],
            -float(
                row["lofo_host_top1"]
                if row["classification"] == "CANONICAL_RENDERER_CANDIDATE"
                else row["lofo_position_top1"]
            ),
            float(row["empirical_entropy_bits"]),
            -int(row["events"]),
            row["page_host"],
        )
    )
    rebuilt_top = [row["page_host"] for row in reconstructed_rows[:20]]
    check(
        "top_candidate_order",
        rebuilt_top == [row["page_host"] for row in result["top_candidates"]],
    )

    report_text = REPORT.read_text()
    check("report_status", "OPAQUE_HOST_RENDERER_ATLAS_BUILT" in report_text)
    check("report_claim_ceiling", "cannot establish lexicality" in report_text)
    check("report_no_f84", "No host substring was mined" in report_text and "no f84 row" in report_text)
    check("counterexample_count", len(read_tsv(COUNTER)) == 15)

    check_categories = Counter(str(row["check"]).split(":", 1)[0] for row in checks)
    validation = {
        "schema": "GDT296_OPAQUE_HOST_RENDERER_ATLAS_VALIDATION_V1",
        "status": "PASS",
        "scope": "INDEPENDENT_NONIMPORTING_SOURCE_FOLD_SCORE_CLASSIFICATION_RECONSTRUCTION",
        "checks_total": len(checks),
        "checks_passed": sum(int(row["pass"]) for row in checks),
        "check_categories": dict(sorted(check_categories.items())),
        "failed_checks": [row for row in checks if not row["pass"]],
        "result_sha256": sha256(RESULT),
        "validator_sha256": sha256(Path(__file__)),
    }
    validation["content_sha256"] = content_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": validation["status"],
                "checks": validation["checks_total"],
                "hosts": len(hosts),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
