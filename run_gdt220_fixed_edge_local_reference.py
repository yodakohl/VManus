#!/usr/bin/env python3
"""GDT220: audit the fixed GDT217 edge overlaps against human local assemblies."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
MANIFEST = R / "gdt220_local_assembly_manifest.tsv"
OVERLAPS = R / "gdt217_exact_overlaps.tsv"
LABELS = R / "gdt012_annotated_core_inventory.tsv"
GROUPS = R / "gdt016_group_state_inventory.tsv"
GDT217 = R / "gdt217_result.json"
METHOD = R / "GDT220_FIXED_EDGE_LOCAL_REFERENCE_METHOD.md"
REPORT = R / "GDT220_FIXED_EDGE_LOCAL_REFERENCE_REPORT.md"
ATLAS = R / "gdt220_local_reference_atlas.tsv"
CONTENT = R / "gdt220_f83_content_diagnostic.tsv"
COUNTER = R / "gdt220_counterexamples.tsv"
RESULT = R / "gdt220_result.json"


def read(path: Path):
    with path.open(encoding="utf8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def write(path: Path, rows):
    with path.open("w", encoding="utf8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def main():
    manifest = read(MANIFEST)
    overlaps = read(OVERLAPS)
    assert len(manifest) == len(overlaps) == 7
    keys = ("representation", "page", "physical_folio", "shared_key", "label_loci",
            "paragraph_initial_loci", "label_occurrences", "paragraph_occurrences")
    assert {tuple(r[k] for k in keys) for r in manifest} == {tuple(r[k] for k in keys) for r in overlaps}
    assert not any(r["page"].startswith("f84") for r in manifest)

    labels = {}
    for row in read(LABELS):
        if row["page"].startswith("f84"):
            raise AssertionError("GDT012 must remain f84-free")
        labels[row["locus"]] = row
    selected = {x for row in manifest for x in row["label_loci"].split(",")}
    assert selected <= labels.keys()

    relation_counts = Counter(row["visual_relation_state"] for row in manifest)
    same_parent = [row for row in manifest if row["visual_relation_state"] == "SAME_CATALOGUE_PARENT_FIGURE_ADJACENT"]
    explicit_different = [row for row in manifest if row["visual_relation_state"].startswith("EXPLICIT_DIFFERENT")]
    assert len(same_parent) == 1 and same_parent[0]["page"] == "f83r" and len(explicit_different) == 2

    paragraph_rows = defaultdict(list)
    with GROUPS.open(encoding="utf8", newline="") as h:
        for row in csv.DictReader(h, delimiter="\t"):
            if row["page"].startswith("f84"):
                continue
            if row["locus"] in {"f83r.52", "f83r.53", "f83r.54", "f83r.55"}:
                paragraph_rows[row["locus"]].append(row)
    assert set(paragraph_rows) == {"f83r.52", "f83r.53", "f83r.54", "f83r.55"}
    flat = [r for locus in sorted(paragraph_rows) for r in paragraph_rows[locus]]
    exact_arolsy = sum(r["residual_host"] == "arolsy" for r in flat)
    exact_ol = sum(r["residual_host"] == "ol" for r in flat)
    ar_al_states = sum(r["record_state"] in {"AR_REFERENCE", "AL_STATE", "OT_AR_LOCAL", "OT_AL_LOCAL"} for r in flat)
    complete_lines = sum(len(rows) == int(rows[0]["group_count"]) for rows in paragraph_rows.values())
    content_rows = []
    for locus in sorted(paragraph_rows, key=lambda x: int(x.split(".")[-1])):
        rows = sorted(paragraph_rows[locus], key=lambda x: int(x["group_index"]))
        content_rows.append({
            "paragraph_locus": locus,
            "observed_groups": len(rows),
            "declared_group_count": rows[0]["group_count"],
            "complete_hpr2_coverage": int(len(rows) == int(rows[0]["group_count"])),
            "residual_hosts": "|".join(r["residual_host"] for r in rows),
            "record_states": "|".join(r["record_state"] for r in rows),
            "exact_arolsy_hosts": sum(r["residual_host"] == "arolsy" for r in rows),
            "exact_ol_hosts": sum(r["residual_host"] == "ol" for r in rows),
        })
    write(CONTENT, content_rows)

    # Three strict label keys occupy top-left, top-right, lower-right.  Count
    # the exact six reassignments placing CA at the lower position.
    label_keys = ("AB", "AG", "CA")
    worlds = list(itertools.permutations(label_keys))
    local_hits = [int(world[2] == "CA") for world in worlds]
    observed_local_hit = 1
    local_p = sum(x >= observed_local_hit for x in local_hits) / len(local_hits)
    assert local_p == 1 / 3

    atlas = []
    for row in manifest:
        rr = dict(row)
        rr["same_parent_reference_candidate"] = int(row["visual_relation_state"] == "SAME_CATALOGUE_PARENT_FIGURE_ADJACENT")
        rr["explicit_counterexample"] = int(row["visual_relation_state"].startswith("EXPLICIT_DIFFERENT"))
        rr["interpretation"] = ("LOCAL_REFERENCE_CANDIDATE" if rr["same_parent_reference_candidate"] else
                                "COUNTEREXAMPLE" if rr["explicit_counterexample"] else "OWNERSHIP_UNRESOLVED")
        atlas.append(rr)
    write(ATLAS, atlas)

    counter = [
        {"counterexample": "DIFFERENT_VISUAL_UNIT_MATCHES", "count": len(explicit_different),
         "detail": "f75v matches top-pond label to lower-pond prose; f99v KA matches row-1 label to bottom prose."},
        {"counterexample": "SINGLE_SAME_PARENT_FOLIO", "count": len(same_parent),
         "detail": "Only f83 supplies an independently co-localized overlap; the two-folio decision gate fails."},
        {"counterexample": "F83_LOCAL_NULL", "count": f"{sum(local_hits)}_OF_{len(local_hits)}",
         "detail": f"The same-parent CA placement has an exact descriptive reassignment tail of {local_p:.12g}."},
        {"counterexample": "NO_EXACT_CONTENT_HOST_REUSE", "count": exact_arolsy,
         "detail": "The adjacent f83r.52-55 HPR2 rows contain no exact arolsy residual host."},
        {"counterexample": "F83_SECOND_LOWER_LABEL_UNAVAILABLE", "count": 1,
         "detail": "f83r.50 is reading-unstable and had no strict eligible GDT217 family key."},
        {"counterexample": "INCOMPLETE_HPR2_LINE_COVERAGE", "count": 4 - complete_lines,
         "detail": "Only complete observed rows are interpreted; missing groups cannot be treated as absences."},
    ]
    write(COUNTER, counter)

    established = len({r["physical_folio"] for r in same_parent}) >= 2 and not explicit_different
    status = "FIXED_EDGE_LOCAL_REFERENCE_ESTABLISHED" if established else "FIXED_EDGE_LOCAL_REFERENCE_NOT_ESTABLISHED_F83_CANDIDATE_ONLY"
    REPORT.write_text(f"""# GDT220 — fixed-edge local reference audit

## Outcome

**{status}**

The seven exact GDT217 page/key cells do not become seven references when
checked against the existing human catalogue.  Only **1/7** is independently
co-localized: f83r.51 (`darolsy`) is the lower label near the right structure
of the southwest figure, and f83r.52 starts the text block below that same
figure.  Their fixed source-family key is `CA` and the loci are consecutive.

Two cells are explicit counterexamples.  f75v links a top-pond label key to a
lower-pond paragraph key; f99v's `KA` cell links a row-1 plant label to the
bottom text block.  The remaining four cells have only page-level overlap or
mix labels from several visual units with prose lacking an exact owner.

The f83 local permutation diagnostic is also small: placing the observed `CA`
label key in the lower strict-label position occurs in **2/6** reassignments
(`p={local_p:.4f}`).  The other lower label, f83r.50, lacks a strict eligible
family value.  In the available HPR2 rows of f83r.52--55, exact host `arolsy`
occurs **{exact_arolsy}** times.  Exact `ol` occurs **{exact_ol}** times and
AR/AL-like states occur **{ar_al_states}** times, but those are common
construction material, not a recovered content address.  HPR2 coverage is
complete for only **{complete_lines}/4** lines, so missing groups are not
negative evidence.

## Consequence

Retain f83r.51→f83r.52 as the strongest *candidate* diagram-label/text-block
bridge currently visible in the fixed edge atlas.  Do not promote it to a
key system, and do not assign `darolsy`, `arolsy`, `CA`, `ol`, or any component
a meaning.  The GDT217 aggregate remains an exploratory boundary association,
now weakened as a literal reference mechanism by two explicit different-unit
matches and the absence of a second same-parent folio.

No number, index, word, morpheme, sound, language, plaintext, meaning, or
translation follows.  f84r and every f84 row were excluded and not accessed.
""", encoding="utf8")

    result = {
        "schema": "GDT220_FIXED_EDGE_LOCAL_REFERENCE_RESULT_V1",
        "status": status,
        "overlap_cells": 7,
        "same_parent_cells": len(same_parent),
        "same_parent_folios": len({r["physical_folio"] for r in same_parent}),
        "explicit_different_cells": len(explicit_different),
        "unresolved_cells": 7 - len(same_parent) - len(explicit_different),
        "f83": {"label_locus": "f83r.51", "paragraph_locus": "f83r.52", "key": "CA",
                 "local_worlds": len(worlds), "inclusive_p": local_p,
                 "exact_arolsy_host_hits": exact_arolsy, "exact_ol_host_hits": exact_ol,
                 "ar_al_state_hits": ar_al_states, "complete_hpr2_lines": complete_lines},
        "interpretation": "One co-local f83 candidate survives, but the fixed edge does not establish a label-to-prose reference system.",
        "claim_ceiling": "Post-hoc fixed-edge local-assembly audit only; no key value, word, sound, language, plaintext, meaning, or translation.",
        "f84": {"accessed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {p.name: sha(p) for p in (MANIFEST, OVERLAPS, LABELS, GROUPS, GDT217)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {p.name: sha(p) for p in (ATLAS, CONTENT, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "same_parent": len(same_parent), "explicit_different": len(explicit_different), "f83_p": local_p}, sort_keys=True))


if __name__ == "__main__":
    main()
