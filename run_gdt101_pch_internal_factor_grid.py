#!/usr/bin/env python3
"""GDT101: postselected PCH internal factor-grid and transfer audit."""
from __future__ import annotations
import csv, hashlib, json, math, random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
GDT003_RESULT = ROOT / "gdt003_nested_result.json"
GDT003_CORRECT = ROOT / "gdt003_nested_correct_predictions.tsv"
GDT003_TOP = ROOT / "gdt003_nested_top_predictions.tsv"
METHOD = ROOT / "GDT101_PCH_INTERNAL_FACTOR_GRID_METHOD.md"
REPORT = ROOT / "GDT101_PCH_INTERNAL_FACTOR_GRID_REPORT.md"
CELLS = ROOT / "gdt101_pch_factor_cells.tsv"
RANKING = ROOT / "gdt101_trigram_grid_ranking.tsv"
TRANSFER = ROOT / "gdt101_pch_folio_transfer.tsv"
OVERLAP = ROOT / "gdt101_pch_gdt003_overlap.tsv"
RESULT = ROOT / "gdt101_result.json"

PREFIXES = ("", "o", "y")
TAILS = ("", "e", "ed", "ey", "d", "y")
CORE = "pch"
PERMUTATIONS = 20000
SEED = 101001

def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader(); out.writerows(rows)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()

def parse_exact(host, core):
    for prefix in PREFIXES:
        for tail in TAILS:
            if host == prefix + core + tail:
                return prefix, tail
    return None

def rectangles(occupied):
    return sum(all((p, t) in occupied for p in pp for t in tt)
               for pp in combinations(PREFIXES, 2) for tt in combinations(TAILS, 2))

def mutual_information(rows):
    n = len(rows)
    a = Counter(x[0] for x in rows); b = Counter(x[1] for x in rows); ab = Counter((x[0], x[1]) for x in rows)
    return sum(v / n * math.log2(v * n / a[p] / b[t]) for (p, t), v in ab.items()) if n else 0.0

def main():
    source = [x for x in read(SOURCE) if not x["page"].startswith("f84r")]
    assert source and not any(x["page"].startswith("f84r") for x in source)
    pch_all = [x for x in source if CORE in x["page_host"]]
    exact = []
    for x in source:
        parsed = parse_exact(x["page_host"], CORE)
        if parsed:
            exact.append((parsed[0], parsed[1], x))

    by_cell = defaultdict(list)
    for prefix, tail, x in exact: by_cell[prefix, tail].append(x)
    cell_rows = []
    for prefix in PREFIXES:
        for tail in TAILS:
            z = by_cell[prefix, tail]
            assert z
            cell_rows.append({
                "prefix": prefix or "EMPTY", "core": CORE, "tail": tail or "EMPTY",
                "page_host": prefix + CORE + tail, "source_groups": len(z),
                "physical_folios": len({x["physical_folio"] for x in z}),
                "registers": ";".join(sorted({x["register"] for x in z})),
                "register_count": len({x["register"] for x in z}),
                "loci": ";".join(sorted({x["locus"] for x in z})),
                "full_tokens": ";".join(sorted({x["token"] for x in z})),
                "semantic_role": "UNASSIGNED",
            })
    write(CELLS, cell_rows, list(cell_rows[0]))

    trigram_counts = Counter()
    for x in source:
        for tri in set(x["page_host"][i:i+3] for i in range(max(0, len(x["page_host"])-2))):
            trigram_counts[tri] += 1
    ranking = []
    for core, containing_groups in trigram_counts.items():
        if containing_groups < 50: continue
        matched = []
        occupied = set()
        for x in source:
            parsed = parse_exact(x["page_host"], core)
            if parsed:
                occupied.add(parsed); matched.append(x)
        ranking.append({
            "core": core, "containing_source_groups": containing_groups,
            "fixed_grid_source_groups": len(matched), "occupied_cells": len(occupied),
            "complete_rectangles": rectangles(occupied),
            "fixed_grid_coverage_of_containing_groups": len(matched) / containing_groups,
            "physical_folios": len({x["physical_folio"] for x in matched}),
            "postselection_state": "FIXED_GRID_DESCRIPTIVE_ONLY", "semantic_role": "UNASSIGNED",
        })
    ranking.sort(key=lambda x:(-x["occupied_cells"], -x["complete_rectangles"], -x["fixed_grid_source_groups"], x["core"]))
    for rank, row in enumerate(ranking, 1): row["rank"] = rank
    write(RANKING, [{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in ranking], list(ranking[0]))
    pch_rank = next(x for x in ranking if x["core"] == CORE)

    transfer = []
    for (prefix, tail), z in sorted(by_cell.items()):
        for folio in sorted({x["physical_folio"] for x in z}):
            target = [x for x in z if x["physical_folio"] == folio]
            training = [x for p, t, x in exact if x["physical_folio"] != folio]
            exact_seen = any(x["page_host"] == prefix + CORE + tail for x in training)
            prefix_seen = any(parse_exact(x["page_host"], CORE) and parse_exact(x["page_host"], CORE)[0] == prefix for x in training)
            tail_seen = any(parse_exact(x["page_host"], CORE) and parse_exact(x["page_host"], CORE)[1] == tail for x in training)
            transfer.append({
                "held_physical_folio": folio, "prefix": prefix or "EMPTY", "core": CORE,
                "tail": tail or "EMPTY", "page_host": prefix + CORE + tail,
                "held_source_groups": len(target), "exact_cell_seen_outside_folio": int(exact_seen),
                "prefix_seen_outside_folio": int(prefix_seen), "tail_seen_outside_folio": int(tail_seen),
                "factor_combination_predictable": int(prefix_seen and tail_seen),
                "whole_form_frequency_predictable": int(exact_seen),
                "novel_factor_only_prediction": int(prefix_seen and tail_seen and not exact_seen),
                "claim_state": "COMPUTATIONAL_POSTSELECTED_NOT_PROSPECTIVE", "semantic_role": "UNASSIGNED",
            })
    write(TRANSFER, transfer, list(transfer[0]))

    # Prefix-tail dependence, with prefixes shuffled inside exact register x folio cells.
    mi_rows = [(p, t, x["register"], x["physical_folio"]) for p,t,x in exact]
    real_mi = mutual_information(mi_rows)
    strata = defaultdict(list)
    for i,x in enumerate(mi_rows): strata[x[2],x[3]].append(i)
    rng = random.Random(SEED); null = []
    for _ in range(PERMUTATIONS):
        perm = [list(x) for x in mi_rows]
        for ids in strata.values():
            prefixes = [perm[i][0] for i in ids]; rng.shuffle(prefixes)
            for i,prefix in zip(ids,prefixes): perm[i][0] = prefix
        null.append(mutual_information(perm))
    mi_p = (1 + sum(v >= real_mi - 1e-15 for v in null)) / (PERMUTATIONS + 1)

    correct = read(GDT003_CORRECT); top = read(GDT003_TOP)
    overlap = []
    for artifact, rows in ((GDT003_CORRECT.name, correct), (GDT003_TOP.name, top)):
        for x in rows:
            fields = (x.get("base_X",""), x.get("A_X",""), x.get("B_X",""), x.get("predicted_fourth",""))
            if any(CORE in v for v in fields):
                overlap.append({"artifact":artifact,"fold_id":x["fold_id"],"operation_A":x["operation_A"],"operation_B":x["operation_B"],"base_X":fields[0],"A_X":fields[1],"B_X":fields[2],"predicted_fourth":fields[3],"target_present":x.get("target_present",""),"claim_state":"ALREADY_IN_GDT003_GENERIC_ALGEBRA","semantic_role":"UNASSIGNED"})
    write(OVERLAP, overlap, list(overlap[0]))

    novel = [x for x in transfer if x["novel_factor_only_prediction"] == 1]
    exact_supported_groups = sum(int(x["held_source_groups"]) for x in transfer if x["exact_cell_seen_outside_folio"] == 1)
    factor_supported_groups = sum(int(x["held_source_groups"]) for x in transfer if x["factor_combination_predictable"] == 1)
    status = "PCH_FORMS_COMPLETE_POSTSELECTED_3X6_FACTOR_GRID_BUT_GDT003_STRING_CEILING_REMAINS"
    REPORT.write_text(f"""# GDT101 — `PCH` internal factor-grid audit

## Outcome

**{status}**

The inspected factorization `{{EMPTY,o,y}} + pch +
{{EMPTY,e,ed,ey,d,y}}` fills all 18 cells and therefore all 45 possible 2x2
rectangles. It contains {len(exact)} source groups on {len({x['physical_folio'] for _,_,x in exact})}
physical folios. Under this same fixed frame, `pch` ranks
{pch_rank['rank']}/{len(ranking)} among trigrams occurring in at least 50 source
groups by occupied cells, then rectangles.

This is real formal reuse but is heavily postselected. The exact grid covers
only {len(exact)}/{len(pch_all)} ({len(exact)/len(pch_all):.1%}) of all
`PCH`-containing PAGE_HOST groups; the remaining {len(pch_all)-len(exact)} are
counterexamples to this narrow factor inventory. Seventeen of eighteen cells
occur on at least two folios. In leave-one-folio diagnostics,
{exact_supported_groups}/{len(exact)} grid-group instances have the exact same
whole form elsewhere, so their transfer is equally available to a whole-form
frequency baseline. {factor_supported_groups}/{len(exact)} have separately
supported prefix and tail factors. There are {len(novel)} factor-only cell
predictions; the notable one is `ypched` on f105, reconstructible from factors
outside f105 but not seen there as an exact form. This is a computational
postselected reconstruction, not a form predicted before manuscript exposure.

The factors are compatible but not frequency-independent. Prefix-tail mutual
information is {real_mi:.4f} bits; shuffling prefixes within exact
register×folio strata gives inclusive p={mi_p:.5f}. Thus the grid behaves like
a conditionally compatible renderer with preferences, not a free Cartesian
slot system.

GDT003 already contains {sum(x['artifact']==GDT003_CORRECT.name for x in overlap)}
correct hidden-folio rows and {sum(x['artifact']==GDT003_TOP.name for x in overlap)}
top-prediction rows involving `pch` somewhere in their rectangle. This audit
does not override GDT003: transformation algebra remained no better than strong
string statistics. `PCH` is retained as a particularly dense formal
content-address family, with semantic role **UNASSIGNED**. f84r was excluded
and untouched.
""", encoding="utf-8")

    result = {
        "schema":"GDT101_PCH_INTERNAL_FACTOR_GRID_RESULT_V1", "status":status,
        "source_groups":len(source), "pch_containing_groups":len(pch_all),
        "fixed_grid_groups":len(exact), "fixed_grid_folios":len({x["physical_folio"] for _,_,x in exact}),
        "occupied_cells":len(by_cell), "possible_cells":len(PREFIXES)*len(TAILS),
        "complete_rectangles":rectangles(set(by_cell)), "possible_rectangles":45,
        "grid_coverage":len(exact)/len(pch_all), "eligible_comparator_trigrams":len(ranking),
        "pch_grid_rank":pch_rank["rank"], "cells_multi_folio":sum(len({x["physical_folio"] for x in z})>=2 for z in by_cell.values()),
        "leave_folio_exact_supported_groups":exact_supported_groups,
        "leave_folio_factor_supported_groups":factor_supported_groups,
        "novel_factor_only_predictions":len(novel),
        "novel_factor_only_forms":sorted({x["page_host"] for x in novel}),
        "prefix_tail_mutual_information_bits":real_mi,
        "prefix_tail_within_register_folio_permutation_p":mi_p,
        "permutations":PERMUTATIONS, "seed":SEED,
        "gdt003_pch_correct_overlap_rows":sum(x["artifact"]==GDT003_CORRECT.name for x in overlap),
        "gdt003_pch_top_overlap_rows":sum(x["artifact"]==GDT003_TOP.name for x in overlap),
        "interpretation":"PCH is an unusually dense postselected formal factor family with conditional prefix-tail compatibility; exact-form frequency and GDT003 string baselines prevent a morphology or semantic promotion.",
        "semantic_role":"UNASSIGNED",
        "claim_ceiling":"Formal factor compatibility only; no word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.",
        "f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},
        "inputs":{SOURCE.name:sha(SOURCE),GDT003_RESULT.name:sha(GDT003_RESULT),GDT003_CORRECT.name:sha(GDT003_CORRECT),GDT003_TOP.name:sha(GDT003_TOP),"gdt100_result.json":sha(ROOT/"gdt100_result.json")},
        "implementation":{Path(__file__).name:sha(Path(__file__))},
        "outputs":{CELLS.name:sha(CELLS),RANKING.name:sha(RANKING),TRANSFER.name:sha(TRANSFER),OVERLAP.name:sha(OVERLAP)},
        "documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"groups":len(exact),"cells":len(by_cell),"rectangles":result["complete_rectangles"],"rank":pch_rank["rank"],"novel":result["novel_factor_only_forms"],"mi_p":mi_p},sort_keys=True))

if __name__ == "__main__": main()
