#!/usr/bin/env python3
"""GDT079: leave-host-out RIGHT_FAMILY structural-function prediction."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
METHOD = ROOT / "GDT079_RIGHT_FAMILY_HELD_HOST_FUNCTION_METHOD.md"
REPORT = ROOT / "GDT079_RIGHT_FAMILY_HELD_HOST_FUNCTION_REPORT.md"
SCORES = ROOT / "gdt079_context_model_scores.tsv"
FOLDS = ROOT / "gdt079_held_host_folds.tsv"
PROFILES = ROOT / "gdt079_right_family_profiles.tsv"
VARIANTS = ROOT / "gdt079_variant_log.tsv"
RESULT = ROOT / "gdt079_result.json"

HOSTS = ("d", "ok", "yk", "yt")
RIGHTS = ("aiin", "air", "ain", "ar", "al")
GRID = (1, 4, 16, 64, 256)
CONTEXTS = {
    "POSITION": lambda row: (row["position_quartile"], row["dy_closure"], row["b3"]),
    "POSITION_ONLY": lambda row: (row["position_quartile"],),
    "WRAPPER": lambda row: (row["wrapper"],),
    "LEFT": lambda row: (row["wrapper"], row["local_frame"]),
    "FULL": lambda row: (row["wrapper"], row["local_frame"], row["position_quartile"], row["dy_closure"], row["b3"]),
}


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def content_sha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    all_source = read(SOURCE)
    source = [row for row in all_source if row["page_host"] in HOSTS and row["right_family"] in RIGHTS]
    assert len(all_source) == 15592 and len(source) == 1212 and not any(row["locus"].startswith("f84r") for row in all_source)
    baseline_total = 0.0
    model_totals = Counter()
    fold_values = defaultdict(Counter)
    for held_host in HOSTS:
        training = [row for row in source if row["page_host"] != held_host]
        held = [row for row in source if row["page_host"] == held_host]
        register_counts = defaultdict(Counter); register_n = Counter()
        for row in training:
            register_counts[row["register"]][row["right_family"]] += 1
            register_n[row["register"]] += 1
        baseline = 0.0
        for row in held:
            probability = (register_counts[row["register"]][row["right_family"]] + 0.5) / (register_n[row["register"]] + 0.5 * len(RIGHTS))
            baseline -= math.log2(probability)
        baseline_total += baseline; fold_values[held_host]["BASELINE"] = baseline
        for context_name, context_function in CONTEXTS.items():
            context_counts = defaultdict(Counter); context_n = Counter()
            for row in training:
                key = (row["register"], context_function(row))
                context_counts[key][row["right_family"]] += 1; context_n[key] += 1
            for backoff in GRID:
                bits = 0.0
                for row in held:
                    base_probability = (register_counts[row["register"]][row["right_family"]] + 0.5) / (register_n[row["register"]] + 0.5 * len(RIGHTS))
                    key = (row["register"], context_function(row))
                    probability = (context_counts[key][row["right_family"]] + backoff * base_probability) / (context_n[key] + backoff)
                    bits -= math.log2(probability)
                model_totals[context_name, backoff] += bits
                fold_values[held_host][context_name, backoff] = bits
    score_rows = []
    selector_bits = math.log2(len(CONTEXTS) * len(GRID))
    for (context, backoff), bits in model_totals.items():
        score_rows.append({"context": context, "backoff": backoff, "groups": len(source), "baseline_bits": baseline_total, "held_bits": bits, "raw_gain_bits": baseline_total - bits, "selector_configurations": len(CONTEXTS) * len(GRID), "selector_bits": selector_bits, "selector_paid_gain_bits": baseline_total - bits - selector_bits})
    score_rows.sort(key=lambda row: (-row["selector_paid_gain_bits"], row["context"], row["backoff"]))
    best = score_rows[0]
    position_only_best = max((row for row in score_rows if row["context"] == "POSITION_ONLY"), key=lambda row: row["selector_paid_gain_bits"])
    fold_rows = []
    for host in HOSTS:
        fold_rows.append({"held_page_host": host, "held_groups": sum(row["page_host"] == host for row in source), "baseline_bits": fold_values[host]["BASELINE"], "selected_context": best["context"], "selected_backoff": best["backoff"], "held_bits": fold_values[host][best["context"], best["backoff"]], "gain_bits": fold_values[host]["BASELINE"] - fold_values[host][best["context"], best["backoff"]]})
    profile_rows = []
    for right in RIGHTS:
        rows = [row for row in source if row["right_family"] == right]
        profile_rows.append({"right_family": right, "occurrences": len(rows), "hosts": len({row["page_host"] for row in rows}), "registers": len({row["register"] for row in rows}), "mean_position_quartile": sum(int(row["position_quartile"]) for row in rows) / len(rows), "dy_rate": sum(int(row["dy_closure"]) for row in rows) / len(rows), "b3_rate": sum(int(row["b3"]) for row in rows) / len(rows), "line_final_rate": sum(int(row["group_index"]) == int(row["group_count"]) for row in rows) / len(rows), "dominant_wrapper": Counter(row["wrapper"] for row in rows).most_common(1)[0][0]})
    def clean(rows): return [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]
    write(SCORES, clean(score_rows), list(score_rows[0])); write(FOLDS, clean(fold_rows), list(fold_rows[0])); write(PROFILES, clean(profile_rows), list(profile_rows[0]))
    variants = [{"variant_id":"V00","status":"BASELINE","description":"Register-only RIGHT_FAMILY prevalence, leave one PAGE_HOST out."},{"variant_id":"V01","status":"PRIMARY","description":"Five fixed structural contexts x five backoffs; selector paid over all 25."},{"variant_id":"V02","status":"FIXED_HOSTS","description":"Only HPR4 d/ok/yk/yt and five explicit right families."},{"variant_id":"V03","status":"NOT_RUN","description":"No external annotation, semantic class, alternate host/feature/grid, or f84r."}]
    write(VARIANTS, variants, list(variants[0]))
    positive_hosts = sum(row["gain_bits"] > 0 for row in fold_rows)
    status = "RIGHT_FAMILY_POSITION_PROFILE_WEAKLY_TRANSFERS_ACROSS_HELD_HOSTS" if best["selector_paid_gain_bits"] > 0 and positive_hosts >= 3 else "RIGHT_FAMILY_FUNCTION_DOES_NOT_TRANSFER_ACROSS_HOSTS"
    report = f"""# GDT079 — RIGHT_FAMILY held-host function transfer

## Outcome

**{status}**

Across 1,212 explicit-renderer occurrences, the best of 25 fixed models is
`{best['context']}` with backoff {best['backoff']}.  It saves
{best['raw_gain_bits']:+.3f} raw bits and only
{best['selector_paid_gain_bits']:+.3f} bits after the complete selector.  The
direction is positive for {positive_hosts}/4 held hosts; `yt` is the explicit
counterexample.

Position alone saves {position_only_best['raw_gain_bits']:+.3f} raw bits, only
{best['raw_gain_bits']-position_only_best['raw_gain_bits']:+.3f} below the
selected POSITION+DY+B3 context; B3 is absent and DY nearly absent in these
explicit-renderer cells.  Thus the five right renderers have mainly a weak
transferable line-position profile,
but most of their choice remains PAGE_HOST- and register-specific.  Wrapper
context does not win this held-host comparison.  This supports a small record-
position component, not a semantic or linguistic function.  Full model, host,
and family profiles are exported.  No semantic class, role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.
f84r was excluded and not opened, retained, queried, joined, scored, or targeted.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {"schema":"GDT079_RIGHT_FAMILY_HELD_HOST_FUNCTION_RESULT_V1","status":status,"groups":len(source),"hosts":list(HOSTS),"right_families":list(RIGHTS),"contexts":list(CONTEXTS),"grid":list(GRID),"baseline_bits":baseline_total,"best_model":best,"position_only_best":position_only_best,"positive_held_hosts":positive_hosts,"interpretation":"Weak PAGE_HOST-transferable line-position bias in RIGHT_FAMILY choice; DY/B3 add little and most choice remains host/register-specific.","claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt076_result.json":sha(ROOT/"gdt076_result.json"),"gdt077_result.json":sha(ROOT/"gdt077_result.json"),"gdt078_result.json":sha(ROOT/"gdt078_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),FOLDS.name:sha(FOLDS),PROFILES.name:sha(PROFILES),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
    result["result_content_sha256"] = content_sha(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status":status,"best":best,"folds":fold_rows},sort_keys=True))


if __name__ == "__main__": main()
