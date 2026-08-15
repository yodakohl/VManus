#!/usr/bin/env python3
"""GDT075: discover formal behavior predicates in one section, test another."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
ANN = ROOT / "gdt012_annotated_core_inventory.tsv"
PARSED = ROOT / "gdt059_hpr2_external_inventory.tsv"
METHOD = ROOT / "GDT075_NESTED_SECTION_PREDICATE_TRANSFER_METHOD.md"
REPORT = ROOT / "GDT075_NESTED_SECTION_PREDICATE_TRANSFER_REPORT.md"
FOLDS = ROOT / "gdt075_nested_section_folds.tsv"
RANKINGS = ROOT / "gdt075_candidate_rankings.tsv"
VARIANTS = ROOT / "gdt075_variant_log.tsv"
RESULT = ROOT / "gdt075_result.json"

THRESHOLDS = (0.10, 0.25, 0.50, 0.75)
AXIS = "REL_ENCLOSURE"
FOLD_SPECS = (("A", "Z"), ("Z", "A"))
FIXED_SUBLEAD = "RATE:R=aiin>=0.25"


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def effect(rows, feature):
    strata = defaultdict(list)
    for row in rows:
        strata[row["stratum"]].append(row)
    observed = expected = variance = 0.0
    informative = eligible = 0
    for selected in strata.values():
        nx = sum(feature in row["features"] for row in selected)
        ny = sum(AXIS in row["tags"] for row in selected)
        total = len(selected)
        if not (0 < nx < total and 0 < ny < total):
            continue
        overlap = sum(feature in row["features"] and AXIS in row["tags"] for row in selected)
        expectation = nx * ny / total
        var = nx * (ny / total) * (1 - ny / total) * (total - nx) / (total - 1)
        observed += overlap
        expected += expectation
        variance += var
        informative += 1
        eligible += nx
    conditional = (observed - expected) / eligible if eligible else 0.0
    z = (observed - expected) / math.sqrt(variance) if variance else 0.0
    return {
        "loci": len(rows),
        "feature_loci": sum(feature in row["features"] for row in rows),
        "feature_folios": len({row["physical_folio"] for row in rows if feature in row["features"]}),
        "axis_positive": sum(AXIS in row["tags"] for row in rows),
        "informative_strata": informative,
        "eligible_feature_loci": eligible,
        "conditional_effect": conditional,
        "conditional_z": z,
        "local_two_sided_p": math.erfc(abs(z) / math.sqrt(2)) if variance else 1.0,
    }


def main():
    source = read(SOURCE)
    annotations = read(ANN)
    parsed = read(PARSED)
    assert len(source) == 15592 and len(annotations) == len(parsed) == 671
    assert not any(row["locus"].startswith("f84r") for row in source + parsed)
    by_line = defaultdict(list)
    for row in source:
        by_line[row["locus"]].append(row)
    events = []
    for line in by_line.values():
        line.sort(key=lambda row: int(row["group_index"]))
        for index, row in enumerate(line):
            previous = line[index - 1] if index else None
            following = line[index + 1] if index + 1 < len(line) else None
            tokens = [
                "W=" + row["wrapper"], "D=" + row["inner_d"],
                "F=" + row["local_frame"], "R=" + row["right_family"],
                "DY=" + row["dy_closure"], "B3=" + row["b3"],
                "P=" + row["position_quartile"],
                "PW=" + (previous["wrapper"] if previous else "BOS"),
                "PF=" + (previous["local_frame"] if previous else "BOS"),
                "PDY=" + (previous["dy_closure"] if previous else "BOS"),
                "NW=" + (following["wrapper"] if following else "EOS"),
                "NF=" + (following["local_frame"] if following else "EOS"),
                "NDY=" + (following["dy_closure"] if following else "EOS"),
            ]
            events.append((row["section"], row["physical_folio"], row["page_host"], tokens))
    annotation_map = {(row["locus"], row["group_index"]): row for row in annotations}
    by_locus = defaultdict(list)
    for row in parsed:
        by_locus[row["locus"]].append(row)
    base = []
    for locus, groups in sorted(by_locus.items()):
        groups.sort(key=lambda row: int(row["group_index"]))
        annotation = annotation_map[locus, groups[0]["group_index"]]
        base.append(
            {
                "locus": locus,
                "section": groups[0]["section"],
                "physical_folio": groups[0]["physical_folio"],
                "unit": annotation["unit"],
                "hosts": [row["page_host"] for row in groups],
                "tags": {value for value in (annotation["object_tags"] + ";" + annotation["relation_tags"]).split(";") if value and value != "LABEL"},
            }
        )
    fold_rows = []
    ranking_rows = []
    fold_payload = []
    for training_section, held_section in FOLD_SPECS:
        counts = defaultdict(Counter)
        totals = Counter()
        folios = defaultdict(set)
        for section, folio, page_host, tokens in events:
            if section == held_section:
                continue
            counts[page_host].update(tokens)
            totals[page_host] += 1
            folios[page_host].add(folio)
        profiles = {
            page_host: {key: value / totals[page_host] for key, value in values.items()}
            for page_host, values in counts.items()
            if len(folios[page_host]) >= 2
        }
        rows = []
        for row in base:
            if row["section"] not in {training_section, held_section} or not all(host in profiles for host in row["hosts"]):
                continue
            rates = Counter()
            for host in row["hosts"]:
                rates.update(profiles[host])
            rates = {key: value / len(row["hosts"]) for key, value in rates.items()}
            features = {f"RATE:{key}>={threshold:.2f}" for key, value in rates.items() for threshold in THRESHOLDS if value >= threshold}
            rows.append({**row, "features": features, "stratum": row["physical_folio"] + "|" + row["unit"]})
        training = [row for row in rows if row["section"] == training_section]
        held = [row for row in rows if row["section"] == held_section]
        library = sorted(set().union(*(row["features"] for row in rows)))
        candidates = []
        for feature in library:
            train_effect = effect(training, feature)
            held_effect = effect(held, feature)
            if not (
                5 <= train_effect["feature_loci"] <= len(training) - 5
                and 3 <= held_effect["feature_loci"] <= len(held) - 3
                and train_effect["feature_folios"] >= 2
                and held_effect["feature_folios"] >= 2
                and train_effect["informative_strata"] >= 1
                and held_effect["informative_strata"] >= 1
            ):
                continue
            candidates.append((feature, train_effect, held_effect))
        candidates.sort(key=lambda item: (-item[1]["conditional_z"], -item[1]["conditional_effect"], item[0]))
        for rank, (feature, train_effect, held_effect) in enumerate(candidates, 1):
            ranking_rows.append(
                {
                    "training_section": training_section,
                    "held_section": held_section,
                    "training_rank": rank,
                    "candidate": feature,
                    **{"training_" + key: value for key, value in train_effect.items()},
                    **{"held_" + key: value for key, value in held_effect.items()},
                    "held_direction_positive": int(held_effect["conditional_effect"] > 0),
                    "candidate_role": "SELECTED_TOP" if rank == 1 else "FIXED_RAIIN_SUBLEAD" if feature == FIXED_SUBLEAD else "LIBRARY_MEMBER",
                }
            )
        selected = candidates[0]
        raiin_rank, raiin = next((rank, item) for rank, item in enumerate(candidates, 1) if item[0] == FIXED_SUBLEAD)
        fold_row = {
            "training_section": training_section,
            "held_section": held_section,
            "training_loci": len(training),
            "held_loci": len(held),
            "eligible_candidates": len(candidates),
            "selected_candidate": selected[0],
            "selected_training_effect": selected[1]["conditional_effect"],
            "selected_training_z": selected[1]["conditional_z"],
            "selected_held_effect": selected[2]["conditional_effect"],
            "selected_held_z": selected[2]["conditional_z"],
            "selected_transfers_positive": int(selected[2]["conditional_effect"] > 0),
            "raiin_training_rank": raiin_rank,
            "raiin_training_effect": raiin[1]["conditional_effect"],
            "raiin_held_effect": raiin[2]["conditional_effect"],
            "raiin_transfers_positive": int(raiin[2]["conditional_effect"] > 0),
        }
        fold_rows.append(fold_row)
        fold_payload.append(fold_row)
    shared = set(row["candidate"] for row in ranking_rows if row["training_section"] == "A") & set(row["candidate"] for row in ranking_rows if row["training_section"] == "Z")
    stability = []
    for candidate in shared:
        a = next(row for row in ranking_rows if row["training_section"] == "A" and row["candidate"] == candidate)
        z = next(row for row in ranking_rows if row["training_section"] == "Z" and row["candidate"] == candidate)
        stability.append((min(float(a["training_conditional_z"]), float(z["training_conditional_z"])), candidate))
    stability.sort(reverse=True)
    raiin_stability_rank = next(index for index, (_, candidate) in enumerate(stability, 1) if candidate == FIXED_SUBLEAD)
    def clean(rows):
        return [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]
    write(FOLDS, clean(fold_rows), list(fold_rows[0]))
    write(RANKINGS, clean(ranking_rows), list(ranking_rows[0]))
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "Nested A-to-Z and Z-to-A discovery using fixed GDT069 threshold library."},
        {"variant_id": "V01", "status": "FIXED_SUBLEAD", "description": "Report pre-existing R=aiin>=.25 rank and held effect without substituting it for selected top."},
        {"variant_id": "V02", "status": "CAPACITY", "description": "Training/held support, folio, nonfeature, and informative-stratum gates fixed in method."},
        {"variant_id": "V03", "status": "NOT_RUN", "description": "No alternate axis, threshold, semantic class, gloss, parser, or f84r."},
    ]
    write(VARIANTS, variants, list(variants[0]))
    selected_positive = sum(row["selected_transfers_positive"] for row in fold_rows)
    raiin_positive = sum(row["raiin_transfers_positive"] for row in fold_rows)
    status = "TOP_DISCOVERED_BEHAVIOR_PREDICATES_FAIL_CROSS_SECTION_TRANSFER_RAIIN_SUBLEAD_STABLE" if selected_positive == 0 and raiin_positive == 2 else "NESTED_SECTION_PREDICATE_TRANSFER_MIXED"
    report = f"""# GDT075 — nested section-held predicate discovery

## Outcome

**{status}**

The A-only discovery selects `{fold_rows[0]['selected_candidate']}` from
{fold_rows[0]['eligible_candidates']} eligible predicates, but its held-Z
effect is {fold_rows[0]['selected_held_effect']:+.4f}.  The Z-only discovery
selects `{fold_rows[1]['selected_candidate']}` from
{fold_rows[1]['eligible_candidates']} predicates, but its held-A effect is
{fold_rows[1]['selected_held_effect']:+.4f}.  Thus the actually selected top
predicate transfers positively in {selected_positive}/2 directions.

The pre-existing `R=aiin>=.25` predicate ranks
{fold_rows[0]['raiin_training_rank']}/{fold_rows[0]['eligible_candidates']} in A
and {fold_rows[1]['raiin_training_rank']}/{fold_rows[1]['eligible_candidates']}
in Z.  It transfers positively in {raiin_positive}/2 directions and ranks
{raiin_stability_rank}/{len(stability)} by minimum A/Z training z among the
shared capacity-qualified library.  This makes it a comparatively stable
sublead, but it was not independently rediscovered as the top rule.

The result narrows, rather than confirms, HPR3: unconstrained single-section
discovery overfits section-specific behavior coordinates; one frozen
right-family ecology class is directionally stable but remains postselected.
All candidates and counterdirections are exported.  No semantic class, role,
gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation
is assigned.  f84r was excluded and not opened, retained, queried, joined,
scored, or targeted.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT075_NESTED_SECTION_PREDICATE_TRANSFER_RESULT_V1",
        "status": status,
        "folds": fold_payload,
        "selected_positive_transfers": selected_positive,
        "raiin_positive_transfers": raiin_positive,
        "shared_capacity_candidates": len(stability),
        "raiin_cross_section_stability_rank": raiin_stability_rank,
        "interpretation": "Single-section discovery selects nontransferring top predicates; the fixed R=aiin sublead remains positive but is not independently top-ranked.",
        "claim_ceiling": "No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
        "inputs": {SOURCE.name: sha(SOURCE), ANN.name: sha(ANN), PARSED.name: sha(PARSED), "gdt069_result.json": sha(ROOT / "gdt069_result.json"), "gdt072_result.json": sha(ROOT / "gdt072_result.json"), "gdt074_result.json": sha(ROOT / "gdt074_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {FOLDS.name: sha(FOLDS), RANKINGS.name: sha(RANKINGS), VARIANTS.name: sha(VARIANTS)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "folds": fold_rows, "raiin_stability_rank": raiin_stability_rank, "shared": len(stability)}, sort_keys=True))


if __name__ == "__main__":
    main()
