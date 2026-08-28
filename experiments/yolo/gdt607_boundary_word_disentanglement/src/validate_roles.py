#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


SRC = Path(__file__).resolve().parent
HERE = SRC.parent
ROOT = find_repo_root(HERE)
SOURCE = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"
OUT = HERE / "artifacts/role_attack"
TARGETS = ("ol", "y", "C", "d", "o")
LANGUAGES = ("latin", "old_italian", "middle_high_german")
EXPECTED_INPUTS = {
    "guarded_rows.tsv": "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9",
    "unit_sequences.json": "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf",
    "complete_mappings.tsv": "005ddec8e5b67763c9ccfd1d3244e44c1e68d8c0c6c46a2c7d7edcc36fa4aabe",
    "category_stability_all_configs_latin.tsv": "2a43d309b78392781ab9111c00dcead82424d648ad820fd02f1479dbb33e7997",
    "category_stability_all_configs_old_italian.tsv": "069023255a729b0918f7298ca5482f9bfa6fa1815541098f801db7ddc4704169",
    "category_stability_all_configs_middle_high_german.tsv": "998a6f093584f26321bc4e4ef2f88171ff245383eecb786adde7fe98733e81b5",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def average_ranks(values):
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1] == ordered[i][1]:
            j += 1
        rank = (i + 1 + j) / 2
        for k in range(i, j):
            ranks[ordered[k][0]] = rank
        i = j
    return ranks


def correlation(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    dx = [v - mx for v in x]
    dy = [v - my for v in y]
    denom = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    return sum(a * b for a, b in zip(dx, dy)) / denom


def spearman(x, y):
    return correlation(average_ranks(x), average_ranks(y))


checks = []
failures = []


def check(name, condition, detail):
    entry = {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}
    checks.append(entry)
    if not condition:
        failures.append(entry)


def close(a, b, tolerance=1e-9):
    return abs(float(a) - float(b)) <= tolerance


def main():
    observed_inputs = {name: sha(SOURCE / name) for name in EXPECTED_INPUTS}
    for name, expected in EXPECTED_INPUTS.items():
        check(f"input hash: {name}", observed_inputs[name] == expected, observed_inputs[name])

    guarded = read_tsv(SOURCE / "guarded_rows.tsv")
    check("guarded row count", len(guarded) == 4165, len(guarded))
    check(
        "sealed selectors absent from guarded rows",
        not any(r["page"].lower().startswith("f84") or r["physical_folio"].lower().startswith("f84") for r in guarded),
        "f84/f84r prefix absent",
    )
    exact_pages = sorted({(r["page"], r["physical_folio"], r["split"]) for r in guarded})
    check("exact allowed page count", len(exact_pages) == 180, len(exact_pages))
    check("physical folio count", len({r["physical_folio"] for r in guarded}) == 91, len({r["physical_folio"] for r in guarded}))
    check("train physical folio count", len({r["physical_folio"] for r in guarded if r["split"] == "train"}) == 68, "68")
    check("held physical folio count", len({r["physical_folio"] for r in guarded if r["split"] == "held"}) == 23, "23")

    page_table = read_tsv(OUT / "guarded_page_selection.tsv")
    table_pages = sorted((r["page"], r["physical_folio"], r["split"]) for r in page_table)
    check("page selector table exactly matches guarded rows", table_pages == exact_pages, len(table_pages))
    check(
        "page selector table hash",
        sha(OUT / "guarded_page_selection.tsv") == "44094942f412ae956f9a793fc2b447233251c79f61700f06689fb61c78e1312c",
        sha(OUT / "guarded_page_selection.tsv"),
    )

    sequences = json.loads((SOURCE / "unit_sequences.json").read_text())
    check("unit inventory count", len(sequences["inventory"]) == 98, len(sequences["inventory"]))
    check("train hard chunk count", len(sequences["sequences"]["train"]) == 20336, len(sequences["sequences"]["train"]))
    check("held hard chunk count", len(sequences["sequences"]["held"]) == 9838, len(sequences["sequences"]["held"]))
    train_events = sum(len(r["units"]) for r in sequences["sequences"]["train"])
    held_events = sum(len(r["units"]) for r in sequences["sequences"]["held"])
    check("train unit events", train_events == 43335, train_events)
    check("held unit events", held_events == 21679, held_events)
    train_units = {u for r in sequences["sequences"]["train"] for u in r["units"]}
    held_units = {u for r in sequences["sequences"]["held"] for u in r["units"]}
    check("train observed unit types", len(train_units) == 98, len(train_units))
    check("held observed unit types", len(held_units) == 97, len(held_units))
    check("zero held-only units", not (held_units - train_units), sorted(held_units - train_units))

    # Independently reconstruct paragraph, line, chunk, and neighbour events.
    meta = {}
    active = {}
    page_counter = Counter()
    paragraph_loci = defaultdict(list)
    for row in guarded:
        page = row["page"]
        starts = "<%>" in row["ivtff_raw"][:32]
        ends = "<$>" in row["ivtff_raw"]
        if starts or page not in active:
            page_counter[page] += 1
            active[page] = f"{page}:p{page_counter[page]}"
        pid = active[page]
        paragraph_loci[pid].append(row["locus"])
        meta[row["locus"]] = {"pid": pid, "starts": starts, "ends": ends}
        if ends:
            active.pop(page, None)
    for pid, loci in paragraph_loci.items():
        for index, locus in enumerate(loci):
            meta[locus]["paragraph_line_index"] = index
            meta[locus]["paragraph_line_count"] = len(loci)
    check("raw guarded paragraph-group count", len(paragraph_loci) == 727, len(paragraph_loci))
    event_loci = {
        record["locus"]
        for split in ("train", "held")
        for record in sequences["sequences"][split]
    }
    event_paragraphs = {meta[locus]["pid"] for locus in event_loci}
    check("paragraphs with reconstructed unit events", len(event_paragraphs) == 725, len(event_paragraphs))

    stats = defaultdict(Counter)
    unit_folios = defaultdict(set)
    all_frequency = Counter()
    for split in ("train", "held"):
        grouped = defaultdict(list)
        for record in sequences["sequences"][split]:
            grouped[record["locus"]].append(record)
        for locus, chunks in grouped.items():
            chunks.sort(key=lambda r: int(r["chunk_index"]))
            line_units = sum(len(r["units"]) for r in chunks)
            offset = 0
            for chunk in chunks:
                units = chunk["units"]
                for index, unit in enumerate(units):
                    row = stats[split, unit]
                    row["n"] += 1
                    all_frequency[unit] += 1
                    unit_folios[split, unit].add(chunk["physical_folio"])
                    row["standalone"] += len(units) == 1
                    row["chunk_initial"] += index == 0
                    row["chunk_final"] += index == len(units) - 1
                    line_index = offset + index
                    row["line_initial"] += line_index == 0
                    row["line_final"] += line_index == line_units - 1
                    pmeta = meta[locus]
                    row["paragraph_initial"] += pmeta["paragraph_line_index"] == 0 and line_index == 0
                    row["paragraph_final"] += (
                        pmeta["paragraph_line_index"] == pmeta["paragraph_line_count"] - 1
                        and line_index == line_units - 1
                    )
                    row["target_neighbor"] += (
                        (index > 0 and units[index - 1] in TARGETS)
                        or (index + 1 < len(units) and units[index + 1] in TARGETS)
                    )
                offset += len(units)

    expected_n = {
        ("train", "ol"): 1825, ("held", "ol"): 712,
        ("train", "y"): 1554, ("held", "y"): 554,
        ("train", "C"): 1445, ("held", "C"): 711,
        ("train", "d"): 1144, ("held", "d"): 597,
        ("train", "o"): 1126, ("held", "o"): 609,
    }
    for key, expected in expected_n.items():
        check(f"target count {key[0]}:{key[1]}", stats[key]["n"] == expected, stats[key]["n"])
    check("all targets occur on every held folio", all(len(unit_folios["held", u]) == 23 for u in TARGETS), {u: len(unit_folios["held", u]) for u in TARGETS})

    expected_rates = {
        ("held", "C", "chunk_initial"): 0.6933895921237694,
        ("held", "C", "chunk_final"): 0.005625879043600563,
        ("train", "d", "line_initial"): 0.20804195804195805,
        ("held", "d", "line_initial"): 0.17587939698492464,
        ("train", "y", "chunk_final"): 0.711068211068211,
        ("held", "y", "chunk_final"): 0.6389891696750902,
        ("train", "y", "paragraph_final"): 0.029601029601029602,
        ("held", "y", "paragraph_final"): 0.04151624548736462,
        ("train", "ol", "standalone"): 0.12054794520547946,
        ("held", "ol", "standalone"): 0.14325842696629212,
        ("train", "o", "chunk_initial"): 0.33570159857904086,
        ("held", "o", "chunk_initial"): 0.31198686371100165,
        ("train", "o", "chunk_final"): 0.23268206039076378,
        ("held", "o", "chunk_final"): 0.2988505747126437,
    }
    for (split, unit, metric), expected in expected_rates.items():
        observed = stats[split, unit][metric] / stats[split, unit]["n"]
        check(f"independent structural rate {split}:{unit}:{metric}", close(observed, expected, 1e-12), observed)

    mapping = read_tsv(SOURCE / "complete_mappings.tsv")
    check("complete mappings count", len(mapping) == 48 * 98, len(mapping))
    direct_trace = {}
    for language in LANGUAGES:
        for unit in TARGETS:
            subset = [r for r in mapping if r["language"] == language and r["unit"] == unit]
            real_primary = [r for r in subset if r["model_kind"] == "real" and r["config"].startswith("primary_")]
            real_all = [r for r in subset if r["model_kind"] == "real"]
            destroyed = [r for r in subset if r["model_kind"] == "destroyed" and r["config"].startswith("primary_")]
            direct_trace[language, unit] = (
                len(real_primary), sum(r["category"] == "W" for r in real_primary),
                len(real_all), sum(r["category"] == "W" for r in real_all),
                len(destroyed), sum(r["category"] == "W" for r in destroyed),
            )
            check(f"real primary W stability {language}:{unit}", direct_trace[language, unit][:2] == (6, 6), direct_trace[language, unit][:2])
    expected_real_all = {
        "latin": {"ol": 12, "y": 12, "C": 11, "d": 11, "o": 12},
        "old_italian": {u: 12 for u in TARGETS},
        "middle_high_german": {"ol": 12, "y": 12, "C": 11, "d": 11, "o": 12},
    }
    expected_destroyed = {
        "latin": {"ol": 4, "y": 4, "C": 1, "d": 3, "o": 0},
        "old_italian": {"ol": 4, "y": 3, "C": 4, "d": 3, "o": 4},
        "middle_high_german": {"ol": 4, "y": 4, "C": 0, "d": 3, "o": 0},
    }
    for language in LANGUAGES:
        for unit in TARGETS:
            trace = direct_trace[language, unit]
            check(f"all-real W count {language}:{unit}", trace[2:] and trace[2:4] == (12, expected_real_all[language][unit]), trace[2:4])
            check(f"destroyed W count {language}:{unit}", trace[4:] == (4, expected_destroyed[language][unit]), trace[4:])

    real_w = defaultdict(list)
    destroyed_w = defaultdict(list)
    for row in mapping:
        bucket = real_w if row["model_kind"] == "real" else destroyed_w
        bucket[row["unit"]].append(row["category"] == "W")
    w_fraction = {u: sum(real_w[u]) / len(real_w[u]) for u in sequences["inventory"]}
    rho_frequency = spearman([math.log(all_frequency[u]) for u in sequences["inventory"]], [w_fraction[u] for u in sequences["inventory"]])
    check("independent W-frequency Spearman", close(rho_frequency, 0.7306479018009955, 1e-12), rho_frequency)
    for unit, expected in {"ar": 34/36, "s": 33/36, "or": 31/36, "k": 31/36}.items():
        check(f"non-target W counterexample {unit}", close(w_fraction[unit], expected, 1e-12), w_fraction[unit])

    qok_family = ("qokaI", "qokaN", "qokEdy", "qokedy", "qokEy")
    qok_expected = {"qokaI": 0.9890909090909091, "qokaN": 0.9809160305343512,
                    "qokEdy": 0.9829931972789115, "qokedy": 0.9838056680161943,
                    "qokEy": 0.9717314487632509}
    for unit in qok_family:
        pooled_n = stats["train", unit]["n"] + stats["held", unit]["n"]
        pooled_only = stats["train", unit]["standalone"] + stats["held", unit]["standalone"]
        standalone = pooled_only / pooled_n
        check(f"independent standalone counterclass rate {unit}", close(standalone, qok_expected[unit], 1e-12), standalone)
        check(f"standalone counterclass real W zero {unit}", w_fraction[unit] == 0, w_fraction[unit])

    result = json.loads((OUT / "RESULT.json").read_text())
    check("result sealed-data declaration", result["f84_f84r"] == "FORBIDDEN_AND_ABSENT", result["f84_f84r"])
    check("result target event count", result["target_occurrences"] == 10277, result["target_occurrences"])
    check("result target train/held counts", result["target_occurrences_by_split"] == {"train": 7094, "held": 3183}, result["target_occurrences_by_split"])
    classifier = result["classifier"]
    check("held balanced identity accuracy", close(classifier["held_balanced_accuracy"], 0.6456134129410045, 1e-12), classifier["held_balanced_accuracy"])
    check("conditional permutation construction", classifier["conditional_permutations"] == 200 and classifier["permutation_strata"] == "section x hand x chunk_pos", {k: classifier[k] for k in ("conditional_permutations", "permutation_strata")})
    check("conditional permutation p-value", close(classifier["balanced_accuracy_empirical_p_ge"], 1/201, 1e-15), classifier["balanced_accuracy_empirical_p_ge"])
    check("local-neighbour ablation dominates", classifier["ablations"]["local_neighbors"]["held_balanced_accuracy"] > classifier["held_balanced_accuracy"], classifier["ablations"]["local_neighbors"]["held_balanced_accuracy"])
    check("metadata ablation non-predictive", classifier["ablations"]["metadata"]["held_balanced_accuracy"] < 0.25 and classifier["ablations"]["metadata"]["held_gain_over_train_prior_bits_per_event"] < 0, classifier["ablations"]["metadata"])
    aucs = [r["auc_a_over_b"] for r in classifier["pairwise_auc"]]
    check("ten held pairwise AUCs", len(aucs) == 10, len(aucs))
    check("minimum held pairwise AUC", min(aucs) >= 0.8501, min(aucs))
    check("W-frequency result agrees", close(result["architecture_correlations"]["occurrences"]["spearman"], rho_frequency, 1e-12), result["architecture_correlations"]["occurrences"]["spearman"])
    check("W-standalone correlation negative", result["architecture_correlations"]["standalone_rate"]["spearman"] < 0, result["architecture_correlations"]["standalone_rate"]["spearman"])

    target_occurrences = read_tsv(OUT / "target_occurrences.tsv")
    check("target occurrence table length", len(target_occurrences) == 10277, len(target_occurrences))
    check("target occurrence units exact", {r["unit"] for r in target_occurrences} == set(TARGETS), sorted({r["unit"] for r in target_occurrences}))
    check("target occurrence selector safety", not any(r["page"].lower().startswith("f84") for r in target_occurrences), "safe")

    role_rows = read_tsv(OUT / "default_role_table.tsv")
    expected_roles = {
        "C": "strict_hard_chunk_opener_or_local_head",
        "d": "chunk_and_physical_line_head_carrier",
        "y": "chunk_line_and_paragraph_closure_carrier",
        "ol": "boundary_and_occasional_standalone_carrier",
        "o": "flexible_bidirectional_connector",
    }
    check("default role table unit set", {r["unit"] for r in role_rows} == set(TARGETS), sorted(r["unit"] for r in role_rows))
    check("default structural roles exact", {r["unit"]: r["stable_default_structural_role"] for r in role_rows} == expected_roles, {r["unit"]: r["stable_default_structural_role"] for r in role_rows})
    hypothesis_rows = read_tsv(OUT / "role_hypothesis_tests.tsv")
    decision_by_hypothesis = {r["hypothesis"]: r["decision"] for r in hypothesis_rows}
    check("shared-role rejection recorded", decision_by_hypothesis.get("single_exchangeable_whole_word_role") == "reject", decision_by_hypothesis.get("single_exchangeable_whole_word_role"))
    check("architecture alternative recorded", decision_by_hypothesis.get("architecture_frequency_bucket") == "supported", decision_by_hypothesis.get("architecture_frequency_bucket"))
    counter_rows = read_tsv(OUT / "standalone_counterclass.tsv")
    check("standalone counterclass units exact", {r["unit"] for r in counter_rows} == set(qok_family), sorted(r["unit"] for r in counter_rows))

    manifest = json.loads((OUT / "ARTIFACT_MANIFEST.json").read_text())
    check("analysis source hash sealed", manifest["analysis_source_sha256"] == sha(SRC / "context_role_attack.py"), manifest["analysis_source_sha256"])
    for name, expected in manifest["outputs"].items():
        check(f"analysis output hash: {name}", sha(OUT / name) == expected, sha(OUT / name))

    report = (OUT / "REPORT.md").read_text()
    for phrase in (
        "MULTIPLE_STABLE_FORMAL_SUBROLES__NO_SHARED_SEMANTIC_DEFAULT",
        "hard-chunk/physical-line head carrier",
        "recipe/formula-closure-like",
        "flexible bidirectional connector",
        "0.7306",
        "qokaN",
        "no internal distributional statistic here identifies any default word meaning",
    ):
        check(f"report claim present: {phrase}", phrase in report, phrase)

    # Re-read source pins after every analysis/output check to catch late drift.
    final_inputs = {name: sha(SOURCE / name) for name in EXPECTED_INPUTS}
    check("source inputs unchanged during validation", final_inputs == observed_inputs == EXPECTED_INPUTS, final_inputs)

    supplemental = (
        "PREREGISTRATION.md", "REPORT.md", "default_role_table.tsv",
        "role_hypothesis_tests.tsv", "standalone_counterclass.tsv",
    )
    validation = {
        "schema": "gdt606-role-attack-validation-v1",
        "status": "FAIL" if failures else "PASS",
        "checks_passed": sum(r["status"] == "PASS" for r in checks),
        "checks_failed": len(failures),
        "checks": checks,
        "input_hashes": observed_inputs,
        "analysis_manifest_sha256": sha(OUT / "ARTIFACT_MANIFEST.json"),
        "supplemental_artifact_hashes": {
            **{name: sha(OUT / name) for name in supplemental},
            "src/context_role_attack.py": sha(SRC / "context_role_attack.py"),
            "src/validate_roles.py": sha(SRC / "validate_roles.py"),
        },
        "decision": "MULTIPLE_STABLE_FORMAL_SUBROLES__NO_SHARED_SEMANTIC_DEFAULT",
        "claim_ceiling": "formal distributional defaults only; no word meaning, sound, language, or plaintext",
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": validation["status"],
        "checks_passed": validation["checks_passed"],
        "checks_failed": validation["checks_failed"],
        "validation_sha256": sha(OUT / "VALIDATION.json"),
    }, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
