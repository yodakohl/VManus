#!/usr/bin/env python3
"""GDT074: fixed HPR3 enclosure predicates with target-section-excluded rates."""
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
METHOD = ROOT / "GDT074_SECTION_EXCLUDED_ENCLOSURE_CLASSES_METHOD.md"
REPORT = ROOT / "GDT074_SECTION_EXCLUDED_ENCLOSURE_CLASSES_REPORT.md"
TESTS = ROOT / "gdt074_section_excluded_enclosure_tests.tsv"
EXAMPLES = ROOT / "gdt074_enclosure_class_examples.tsv"
HOST_RATES = ROOT / "gdt074_section_excluded_host_rates.tsv"
VARIANTS = ROOT / "gdt074_variant_log.tsv"
RESULT = ROOT / "gdt074_result.json"

TARGET_SECTIONS = ("A", "Z")
PREDICATES = {
    "HCLASS_RAIIN_HIGH": ("R=aiin", 0.25),
    "HCLASS_FO_ACTIVE": ("F=O", 0.10),
}
AXIS = "REL_ENCLOSURE"


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


def effect(rows, predicate):
    feature = [row for row in rows if predicate(row)]
    nonfeature = [row for row in rows if not predicate(row)]
    feature_positive = sum(AXIS in row["tags"] for row in feature)
    nonfeature_positive = sum(AXIS in row["tags"] for row in nonfeature)
    pooled = feature_positive / len(feature) - nonfeature_positive / len(nonfeature) if feature and nonfeature else 0.0
    strata = defaultdict(list)
    for row in rows:
        strata[row["stratum"]].append(row)
    observed = expected = variance = 0.0
    informative = eligible = 0
    for selected in strata.values():
        nx = sum(predicate(row) for row in selected)
        ny = sum(AXIS in row["tags"] for row in selected)
        total = len(selected)
        if not (0 < nx < total and 0 < ny < total):
            continue
        overlap = sum(predicate(row) and AXIS in row["tags"] for row in selected)
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
        "axis_positive": sum(AXIS in row["tags"] for row in rows),
        "feature_loci": len(feature),
        "feature_positive": feature_positive,
        "feature_negative": len(feature) - feature_positive,
        "nonfeature_positive": nonfeature_positive,
        "pooled_risk_difference": pooled,
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
    events = [
        (row["section"], row["physical_folio"], row["page_host"], "R=" + row["right_family"], "F=" + row["local_frame"])
        for row in source
    ]
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
                "certainty": annotation["annotation_certainty"],
                "hosts": [row["page_host"] for row in groups],
                "tags": {value for value in (annotation["object_tags"] + ";" + annotation["relation_tags"]).split(";") if value and value != "LABEL"},
            }
        )
    test_rows = []
    example_rows = []
    rate_rows = []
    section_rows = {}
    for target_section in TARGET_SECTIONS:
        counts = defaultdict(Counter)
        totals = Counter()
        folios = defaultdict(set)
        for section, folio, page_host, right, frame in events:
            if section == target_section:
                continue
            counts[page_host].update((right, frame))
            totals[page_host] += 1
            folios[page_host].add(folio)
        profiles = {
            page_host: {key: value / totals[page_host] for key, value in values.items()}
            for page_host, values in counts.items()
            if len(folios[page_host]) >= 2
        }
        for page_host, rates in sorted(profiles.items()):
            rate_rows.append(
                {
                    "target_section": target_section,
                    "page_host": page_host,
                    "outside_section_occurrences": totals[page_host],
                    "outside_section_folios": len(folios[page_host]),
                    "rate_R_aiin": rates.get("R=aiin", 0.0),
                    "rate_F_O": rates.get("F=O", 0.0),
                }
            )
        rows = []
        for row in base:
            if row["section"] != target_section or not all(page_host in profiles for page_host in row["hosts"]):
                continue
            rates = Counter()
            for page_host in row["hosts"]:
                rates.update(profiles[page_host])
            rates = {key: value / len(row["hosts"]) for key, value in rates.items()}
            rows.append({**row, "rates": rates, "stratum": row["physical_folio"] + "|" + row["unit"]})
        section_rows[target_section] = rows
        for predicate_id, (coordinate, threshold) in PREDICATES.items():
            predicate = lambda row, c=coordinate, t=threshold: row["rates"].get(c, 0.0) >= t
            values = effect(rows, predicate)
            test_rows.append(
                {
                    "predicate_id": predicate_id,
                    "target_section": target_section,
                    "coordinate": coordinate,
                    "threshold": threshold,
                    **values,
                    "direction_positive": int(values["conditional_effect"] > 0),
                }
            )
            for row in rows:
                if predicate(row):
                    example_rows.append(
                        {
                            "predicate_id": predicate_id,
                            "target_section": target_section,
                            "locus": row["locus"],
                            "physical_folio": row["physical_folio"],
                            "unit": row["unit"],
                            "annotation_certainty": row["certainty"],
                            "host_count": len(row["hosts"]),
                            "page_hosts": ";".join(row["hosts"]),
                            "outside_section_rate": row["rates"].get(coordinate, 0.0),
                            "relation_enclosure": int(AXIS in row["tags"]),
                            "outcome": "POSITIVE_EXAMPLE" if AXIS in row["tags"] else "COUNTEREXAMPLE",
                        }
                    )
    combined = []
    for predicate_id, (coordinate, threshold) in PREDICATES.items():
        joined = []
        for target_section, rows in section_rows.items():
            for row in rows:
                joined.append({**row, "stratum": target_section + "|" + row["stratum"]})
        predicate = lambda row, c=coordinate, t=threshold: row["rates"].get(c, 0.0) >= t
        combined.append({"predicate_id": predicate_id, **effect(joined, predicate)})
    def clean(rows):
        return [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]
    write(TESTS, clean(test_rows), list(test_rows[0]))
    write(EXAMPLES, clean(example_rows), list(example_rows[0]))
    write(HOST_RATES, clean(rate_rows), list(rate_rows[0]))
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "Exact frozen R=aiin>=.25 and F=O>=.10 predicates; section-excluded host rates."},
        {"variant_id": "V01", "status": "FIXED_TARGETS", "description": "Only GDT073 enclosure-capable sections A and Z."},
        {"variant_id": "V02", "status": "POSTSELECTED_TRANSPORT", "description": "Predicate thresholds and archived relation axis arose in GDT069; not prospective confirmation."},
        {"variant_id": "V03", "status": "NOT_RUN", "description": "No alternate threshold, relation, parser, semantic class, gloss, or f84r."},
    ]
    write(VARIANTS, variants, list(variants[0]))
    directions = {
        predicate_id: sum(row["direction_positive"] for row in test_rows if row["predicate_id"] == predicate_id)
        for predicate_id in PREDICATES
    }
    status = "RAIIN_HIGH_ENCLOSURE_LEAD_SURVIVES_SECTION_EXCLUDED_RATE_TRANSPORT" if directions["HCLASS_RAIIN_HIGH"] == 2 and directions["HCLASS_FO_ACTIVE"] < 2 else "FROZEN_ENCLOSURE_CLASS_LEADS_DO_NOT_TRANSPORT"
    combined_by_id = {row["predicate_id"]: row for row in combined}
    report = f"""# GDT074 — section-excluded enclosure-class transport

## Outcome

**{status}**

`HCLASS_RAIIN_HIGH` retains a positive within-section conditional direction in
{directions['HCLASS_RAIIN_HIGH']}/2 target sections after every host's
`R=aiin` rate is rebuilt without that section.  Its combined stratified effect
is {combined_by_id['HCLASS_RAIIN_HIGH']['conditional_effect']:+.4f}; the A
effect is {next(row['conditional_effect'] for row in test_rows if row['predicate_id']=='HCLASS_RAIIN_HIGH' and row['target_section']=='A'):+.4f}
and the Z effect is {next(row['conditional_effect'] for row in test_rows if row['predicate_id']=='HCLASS_RAIIN_HIGH' and row['target_section']=='Z'):+.4f}.

`HCLASS_FO_ACTIVE` is positive in only
{directions['HCLASS_FO_ACTIVE']}/2 sections: it is strong in A but reverses in
Z.  It is therefore removed from the leading HPR3 content-class candidate.
Every high-class positive and counterexample locus is exported.

The surviving `R=aiin` class is a formal ecology association, not a decoded
unit or an enclosure meaning.  The threshold and archived relation axis were
selected before this audit, so this is transport evidence for prioritization,
not confirmation and not the prospective GDT072 test.  Its combined statistic
reproduces GDT069 because the same A/Z strata supplied that earlier result;
the new robustness fact is only that rebuilding rates without each complete
target section preserves the direction.  A has one informative stratum and Z
has two, with many explicit counterexamples.  No semantic class,
role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or
translation is assigned.  f84r was excluded and not opened, retained, queried,
joined, scored, or targeted.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT074_SECTION_EXCLUDED_ENCLOSURE_CLASSES_RESULT_V1",
        "status": status,
        "groups": len(source),
        "target_sections": list(TARGET_SECTIONS),
        "predicates": PREDICATES,
        "test_rows": len(test_rows),
        "direction_positive_sections": directions,
        "combined": combined_by_id,
        "leading_candidate": "HCLASS_RAIIN_HIGH",
        "downgraded_candidate": "HCLASS_FO_ACTIVE",
        "gdt069_overlap_disclosure": "The combined conditional statistic reproduces GDT069 because its informative strata were A/Z; GDT074 newly tests section-excluded formal-rate construction, not fresh outcome labels.",
        "selection_disclosure": "Both predicates and REL_ENCLOSURE are inherited from postselected GDT069; section exclusion applies to formal-rate construction, not original outcome selection.",
        "interpretation": "Section-excluded rate transport of fixed formal predicates only; the prospective GDT072 tests remain unrun.",
        "claim_ceiling": "No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
        "inputs": {SOURCE.name: sha(SOURCE), ANN.name: sha(ANN), PARSED.name: sha(PARSED), "gdt069_result.json": sha(ROOT / "gdt069_result.json"), "gdt071_result.json": sha(ROOT / "gdt071_result.json"), "gdt072_result.json": sha(ROOT / "gdt072_result.json"), "gdt073_result.json": sha(ROOT / "gdt073_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {TESTS.name: sha(TESTS), EXAMPLES.name: sha(EXAMPLES), HOST_RATES.name: sha(HOST_RATES), VARIANTS.name: sha(VARIANTS)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "directions": directions, "combined": combined_by_id}, sort_keys=True))


if __name__ == "__main__":
    main()
