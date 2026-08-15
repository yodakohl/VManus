#!/usr/bin/env python3
"""GDT127: enumerate exact Q20 compiler field templates and host substitutions."""
from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import run_gdt114_q20_record_template_linkage as g

ROOT = Path(__file__).resolve().parent
METHOD = ROOT / "GDT127_Q20_CONTRASTIVE_FIELD_ATLAS_METHOD.md"
REPORT = ROOT / "GDT127_Q20_CONTRASTIVE_FIELD_ATLAS_REPORT.md"
FIELDS = ROOT / "gdt127_q20_field_inventory.tsv"
TEMPLATES = ROOT / "gdt127_q20_field_templates.tsv"
SUBS = ROOT / "gdt127_q20_field_substitutions.tsv"
NULL = ROOT / "gdt127_q20_field_null.tsv"
VISUAL = ROOT / "gdt127_q20_field_visual_leads.tsv"
COUNTER = ROOT / "gdt127_q20_field_counterexamples.tsv"
RESULT = ROOT / "gdt127_result.json"
STAR = ROOT / "experiments/semantic_assumptions/star_morphology_entry/source_panel.tsv"
WORLDS = 4096


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def write(path, rows):
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cell(group):
    return (group["wrapper"], group["frame"], group["right"], group["inner_d"], group["dy"], group["b3"])


def extract_fields():
    output = []
    for record in g.load_records():
        lines = [record["open_locus"]] + record["body_line_loci"].split("|")
        groups = record["open"] + record["body"]
        for line_scope, locus in enumerate(lines):
            current = []
            field_index = 0
            for group in [item for item in groups if item["locus"] == locus]:
                current.append(group)
                if group["dy"]:
                    field_index += 1
                    output.append((record, locus, line_scope, field_index, current))
                    current = []
            if current:
                field_index += 1
                output.append((record, locus, line_scope, field_index, current))
    assert not any(row[0]["page"].startswith("f84r") for row in output)
    return output


def skeleton(groups):
    return tuple(cell(group) for group in groups)


def field_key(record, locus, field_index):
    return f"{record['edition']}|{locus}|F{field_index:02d}"


def null_stat(fields, pair_indices, hosts):
    exact = one = 0
    for left, right in pair_indices:
        left_hosts = [hosts[group["global_id"]] for group in fields[left][4]]
        right_hosts = [hosts[group["global_id"]] for group in fields[right][4]]
        distance = sum(a != b for a, b in zip(left_hosts, right_hosts))
        exact += distance == 0
        one += distance == 1
    return exact, one


def main():
    fields = extract_fields()
    global_id = 0
    for _, _, _, _, groups in fields:
        for group in groups:
            group["global_id"] = global_id
            global_id += 1
    field_rows = []
    by_edition_skeleton = defaultdict(list)
    location = {}
    for index, (record, locus, line_scope, field_index, groups) in enumerate(fields):
        skel = skeleton(groups)
        template_id = csha(skel)[:16]
        hosts = tuple(group["page_host"] for group in groups)
        tokens = tuple(group["token"] for group in groups)
        fid = field_key(record, locus, field_index)
        location[(record["edition"], locus, field_index)] = index
        by_edition_skeleton[(record["edition"], skel)].append(index)
        field_rows.append({
            "field_id": fid, "edition": record["edition"], "page": record["page"],
            "physical_folio": record["physical_folio"], "star_ordinal": record["star_ordinal"],
            "record_scope": "OPEN" if line_scope == 0 else "BODY", "locus": locus,
            "line_depth": line_scope, "field_index": field_index, "field_group_count": len(groups),
            "group_tokens": "|".join(tokens), "page_hosts": "|".join(hosts),
            "compiler_skeleton": json.dumps(skel, separators=(",", ":")), "template_id": template_id,
            "ends_dy": groups[-1]["dy"], "ends_b3": groups[-1]["b3"],
        })
    primary_indices = [i for i, row in enumerate(fields) if row[0]["edition"] == "ZL3b"]
    primary_templates = []
    eligible_skeletons = set()
    for (edition, skel), indices in by_edition_skeleton.items():
        if edition != "ZL3b":
            continue
        folios = {fields[i][0]["physical_folio"] for i in indices}
        fills = Counter(tuple(group["page_host"] for group in fields[i][4]) for i in indices)
        if len(indices) >= 4 and len(folios) >= 2 and len(fills) >= 2:
            eligible_skeletons.add(skel)
            examples = [f"{fields[i][1]}:F{fields[i][3]}" for i in indices[:5]]
            primary_templates.append({
                "template_id": csha(skel)[:16], "field_group_count": len(skel),
                "occurrences": len(indices), "physical_folios": len(folios), "distinct_host_fills": len(fills),
                "compiler_skeleton": json.dumps(skel, separators=(",", ":")),
                "top_host_fills": ";".join(f"{'|'.join(fill)}:{count}" for fill, count in fills.most_common(8)),
                "example_fields": "|".join(examples),
            })
    substitution_counter = Counter()
    substitution_examples = {}
    pair_indices = []
    for skel in {key[1] for key in by_edition_skeleton if key[0] == "ZL3b" and len(key[1]) >= 2}:
        indices = by_edition_skeleton[("ZL3b", skel)]
        for offset, left in enumerate(indices):
            for right in indices[offset + 1:]:
                if fields[left][0]["physical_folio"] == fields[right][0]["physical_folio"]:
                    continue
                pair_indices.append((left, right))
                left_hosts = tuple(group["page_host"] for group in fields[left][4])
                right_hosts = tuple(group["page_host"] for group in fields[right][4])
                differences = [i for i, (a, b) in enumerate(zip(left_hosts, right_hosts)) if a != b]
                if len(differences) != 1:
                    continue
                position = differences[0]
                host_a, host_b = sorted((left_hosts[position], right_hosts[position]))
                key = (skel, position, host_a, host_b)
                substitution_counter[key] += 1
                substitution_examples.setdefault(key, (left, right, left_hosts, right_hosts))
    substitution_rows = []
    for (skel, position, host_a, host_b), support in sorted(substitution_counter.items(), key=lambda item: (-item[1], item[0][1], item[0][2], item[0][3])):
        left, right, left_hosts, right_hosts = substitution_examples[(skel, position, host_a, host_b)]
        left_record, right_record = fields[left][0], fields[right][0]
        stable = True
        for edition in g.EDITIONS:
            li = location.get((edition, fields[left][1], fields[left][3]))
            ri = location.get((edition, fields[right][1], fields[right][3]))
            if li is None or ri is None:
                stable = False
                continue
            stable &= skeleton(fields[li][4]) == skel and skeleton(fields[ri][4]) == skel
        substitution_rows.append({
            "substitution_id": csha((skel, position, host_a, host_b))[:16],
            "template_id": csha(skel)[:16], "field_group_count": len(skel),
            "changed_position_1based": position + 1, "host_a": host_a, "host_b": host_b,
            "cross_folio_pair_support": support, "left_host_sequence": "|".join(left_hosts),
            "right_host_sequence": "|".join(right_hosts),
            "left_page": left_record["page"], "left_star_ordinal": left_record["star_ordinal"],
            "left_locus": fields[left][1], "left_field_index": fields[left][3],
            "right_page": right_record["page"], "right_star_ordinal": right_record["star_ordinal"],
            "right_locus": fields[right][1], "right_field_index": fields[right][3],
            "compiler_skeleton": json.dumps(skel, separators=(",", ":")),
            "skeleton_stable_all_readings": int(stable), "claim_state": "CONTRASTIVE_FORMAL_SLOT_NO_MEANING",
        })
    observed_hosts = {group["global_id"]: group["page_host"] for _, _, _, _, groups in fields for group in groups}
    observed_exact, observed_one = null_stat(fields, pair_indices, observed_hosts)
    null_rows = []
    rng = random.Random(g.seed("GDT127", "FIELD_NULL"))
    for mode in ("PAGE_CELL_LENGTH", "PAGE_CELL_LENGTH_EDGE"):
        strata = defaultdict(list)
        for record, _, _, _, groups in fields:
            if record["edition"] != "ZL3b":
                continue
            for group in groups:
                key = (record["page"], cell(group), min(len(group["page_host"]), 6))
                if mode.endswith("EDGE"):
                    key += (group["page_host"][-1:] or "",)
                strata[key].append(group["global_id"])
        exact_world, one_world = [], []
        for _ in range(WORLDS):
            permuted = dict(observed_hosts)
            for ids in strata.values():
                if len(ids) > 1:
                    values = [permuted[i] for i in ids]
                    rng.shuffle(values)
                    for index, value in zip(ids, values):
                        permuted[index] = value
            exact, one = null_stat(fields, pair_indices, permuted)
            exact_world.append(exact)
            one_world.append(one)
        null_rows.append({
            "null_model": mode, "worlds": WORLDS, "multi_group_cross_folio_template_pairs": len(pair_indices),
            "movable_groups": sum(len(ids) for ids in strata.values() if len(ids) > 1),
            "observed_exact_fill_pairs": observed_exact, "null_exact_mean": float(np.mean(exact_world)),
            "exact_inclusive_p": (1 + sum(value >= observed_exact for value in exact_world)) / (WORLDS + 1),
            "observed_one_slot_pairs": observed_one, "null_one_mean": float(np.mean(one_world)),
            "null_one_q95": float(np.quantile(one_world, .95)),
            "one_slot_inclusive_p": (1 + sum(value >= observed_one for value in one_world)) / (WORLDS + 1),
        })
    star = {(row["page"], int(row["star_ordinal"])): row for row in csv.DictReader(STAR.open(), delimiter="\t")}
    visual_rows = []
    lead_loci = {"f104v.21", "f105r.17", "f112v.30", "f115v.29"}
    lead_skeleton = (("NONE", "NONE", "NONE", 0, 0, 0), ("sh", "NONE", "NONE", 0, 1, 0))
    for index in primary_indices:
        record, locus, _, field_index, groups = fields[index]
        if locus not in lead_loci or skeleton(groups) != lead_skeleton:
            continue
        prop = star[(record["page"], record["star_ordinal"])]
        visual_rows.append({
            "page": record["page"], "physical_folio": record["physical_folio"],
            "star_ordinal": record["star_ordinal"], "field_locus": locus, "field_index": field_index,
            "field_tokens": "|".join(group["token"] for group in groups),
            "page_hosts": "|".join(group["page_host"] for group in groups),
            "compiler_skeleton": json.dumps(skeleton(groups), separators=(",", ":")),
            "rays": prop["rays"], "tail": prop["tail"], "color": prop["color"],
            "overlay_state": "POSTSELECTED_EXPLORATORY_VISUAL_OVERLAY",
        })
    counterexamples = [
        {"counterexample": "ONE_SLOT_FORMULAS_NOT_ABOVE_MATCHED_NULL", "detail": f"observed={observed_one};edge_matched_p={null_rows[1]['one_slot_inclusive_p']:.6f}"},
        {"counterexample": "MOST_ELIGIBLE_TEMPLATES_ARE_SINGLE_GROUP_RENDERER_CELLS", "detail": f"single_group={sum(int(row['field_group_count']) == 1 for row in primary_templates)}/{len(primary_templates)}"},
        {"counterexample": "VISUAL_OVERLAY_HAS_ONLY_FOUR_POSTSELECTED_RECORDS", "detail": "No visual meaning can be inferred."},
    ]
    status = "Q20_CONTRASTIVE_FIELD_SLOTS_PRESENT_NOT_ENRICHED"
    write(FIELDS, field_rows)
    write(TEMPLATES, primary_templates)
    write(SUBS, substitution_rows)
    write(NULL, [{key: f"{value:.12f}" if isinstance(value, float) else value for key, value in row.items()} for row in null_rows])
    write(VISUAL, visual_rows)
    write(COUNTER, counterexamples)
    strongest = next(row for row in substitution_rows if {row["host_a"], row["host_b"]} == {"polor", "yshor"})
    report = f'''# GDT127 — Q20 contrastive field-template atlas

Status: **{status}**

The primary inventory contains {sum(row['edition'] == 'ZL3b' for row in field_rows)}
fields and {len(primary_templates)} eligible recurrent compiler templates.
There are {len(substitution_rows)} distinct cross-folio, exact-template,
one-host substitution types ({observed_one} occurrence pairs).

## Strongest concrete formula

The exact two-group field `polor sheedy` occurs at f112v.30 and f115v.29.
The same skeleton and fixed second group occurs as `yshor sheedy` at f104v.21.
All three readings preserve the skeleton. Thus the formal parse is:

```
[bare PAGE_HOST = polor | yshor] [sh + PAGE_HOST ee + DY]
```

This is a real aligned variable slot. The fixed second group behaves like a
compiler closer in this analysis; neither host receives a meaning.

The postselected four-record visual overlay is deliberately retained: the two
`polor sheedy` records are 7-ray/1-tail, `yshor sheedy` is 8-ray/1-tail, and
`okeeddl sheokedy` is 8-ray/2-tail. This is a risky local-codebook lead, not a
confirmed star description.

## Null

Observed exact-fill/one-slot cross-folio pairs are {observed_exact}/{observed_one}.
The page+cell+length null gives p={null_rows[0]['exact_inclusive_p']:.4f}/
{null_rows[0]['one_slot_inclusive_p']:.4f}; retaining final host edge gives
p={null_rows[1]['exact_inclusive_p']:.4f}/{null_rows[1]['one_slot_inclusive_p']:.4f}.
The slot count is therefore not unusually high under matched page-local
compiler statistics. The observed formulas remain useful exemplars, but their
abundance does not establish a codebook or semantic system.

No star, ray, tail, role, word, morpheme, POS, sound, language, plaintext,
meaning, or translation is assigned. f84r remained entirely sealed.
'''
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT127_Q20_CONTRASTIVE_FIELD_ATLAS_RESULT_V1", "status": status,
        "primary_fields": sum(row["edition"] == "ZL3b" for row in field_rows),
        "eligible_templates": len(primary_templates), "one_slot_substitution_types": len(substitution_rows),
        "observed_exact_fill_pairs": observed_exact, "observed_one_slot_pairs": observed_one,
        "strongest_formula": strongest, "nulls": null_rows,
        "interpretation": "Exact compiler-field skeletons provide aligned host substitutions, but their count is not above matched page-local nulls.",
        "claim_ceiling": "Formal contrastive slots and postselected visual lead only; no star, ray, tail, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "predicted")},
        "inputs": {"gdt126_result.json": sha(ROOT / "gdt126_result.json"), "q20ob001_source_panel.tsv": sha(ROOT / "q20ob001_source_panel.tsv"), str(STAR.relative_to(ROOT)): sha(STAR)},
        "implementation": {Path(__file__).name: sha(Path(__file__)), "run_gdt114_q20_record_template_linkage.py": sha(ROOT / "run_gdt114_q20_record_template_linkage.py")},
        "outputs": {path.name: sha(path) for path in (FIELDS, TEMPLATES, SUBS, NULL, VISUAL, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "templates": len(primary_templates), "substitutions": len(substitution_rows), "exact": observed_exact, "one": observed_one, "nulls": null_rows}, sort_keys=True))


if __name__ == "__main__":
    main()
