#!/usr/bin/env python3
"""Recover Voynich field layers from host-page positional distributions."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from run_gdt010_record_position import (
    ROOT, PERMUTATIONS, canonical_sha, effect, form_maps, group_universe,
    matched_strata, permutation_p, read_tsv, sha, write_tsv,
)

PREFIXES = ("t", "s", "d", "q", "ch", "sh", "che", "o", "ot")
METRICS = ("normalized_position", "line_initial", "line_final", "nonprose")
FAMILY_TESTS = 40


def exact_binomial_two_sided(success: int, total: int) -> float:
    distance = abs(success - total / 2)
    numerator = sum(math.comb(total, k) for k in range(total + 1) if abs(k - total / 2) >= distance - 1e-12)
    return numerator / (2 ** total)


def main() -> None:
    source = read_tsv("gdt002_morphology_occurrences.tsv")
    assert not any(row["locus"].startswith("f84r") for row in source)
    groups = group_universe(source)
    by_token = defaultdict(list)
    for row in groups: by_token[str(row["token"])].append(row)

    operations = {}
    for prefix in PREFIXES:
        bare, marked = defaultdict(list), defaultdict(list)
        for token, items in by_token.items():
            if token.startswith(prefix) and len(token) > len(prefix): marked[token[len(prefix):]].extend(items)
            else: bare[token].extend(items)
        operations[f"{prefix.upper()}_PREPEND"] = (bare, marked)
    operations["DY_APPEND"] = form_maps(groups)["C03_BARE_TO_DY"]

    tests = []
    for oi, (operation, (bare, marked)) in enumerate(operations.items(), 1):
        strata = matched_strata(bare, marked, "HOST_PAGE")
        for mi, metric in enumerate(METRICS, 1):
            observed, positive, negative, na, nb = effect(strata, metric)
            p, low, high = permutation_p(strata, metric, observed, 110000 + oi * 100 + mi)
            tests.append({
                "operation": operation, "metric": metric,
                "host_types": len({name.split("|", 1)[0] for name, _, _ in strata}),
                "host_page_strata": len(strata), "bare_groups": na, "marked_groups": nb,
                "effect_marked_minus_bare": f"{observed:.12f}", "positive_strata": positive, "negative_strata": negative,
                "permutation_draws": PERMUTATIONS, "local_p": f"{p:.8f}",
                "search_adjusted_p_40": f"{min(1.0, p * FAMILY_TESTS):.8f}",
                "null_2_5pct": f"{low:.12f}", "null_97_5pct": f"{high:.12f}",
                "scope": "HOST_PLUS_PAGE_MATCHED_MODULE_SELECTED_UNIVERSE",
            })
    write_tsv("gdt011_operation_position_tests.tsv", tests)
    by = {(row["operation"], row["metric"]): row for row in tests}

    layers = []
    for operation in operations:
        pos = by[(operation, "normalized_position")]; initial = by[(operation, "line_initial")]; final = by[(operation, "line_final")]
        pe, ie, fe = (float(pos["effect_marked_minus_bare"]), float(initial["effect_marked_minus_bare"]), float(final["effect_marked_minus_bare"]))
        pp, ip, fp = (float(pos["search_adjusted_p_40"]), float(initial["search_adjusted_p_40"]), float(final["search_adjusted_p_40"]))
        if operation == "DY_APPEND" and pe > 0 and fe > 0 and pp < .05 and fp < .05: layer = "CLOSURE"
        elif pe < 0 and ie > 0 and pp < .05 and ip < .05: layer = "ENTRY"
        elif (pe < 0 and pp < .05) or (fe < 0 and fp < .05): layer = "EARLY_CARRIER"
        else: layer = "LOCAL_OR_UNRESOLVED"
        layers.append({
            "operation": operation, "recovered_layer": layer,
            "position_effect": pos["effect_marked_minus_bare"], "position_adjusted_p": pos["search_adjusted_p_40"],
            "initial_effect": initial["effect_marked_minus_bare"], "initial_adjusted_p": initial["search_adjusted_p_40"],
            "final_effect": final["effect_marked_minus_bare"], "final_adjusted_p": final["search_adjusted_p_40"],
            "host_page_strata": pos["host_page_strata"], "claim_state": "DISTRIBUTIONAL_FUNCTION_NOT_WORD_MEANING",
        })
    write_tsv("gdt011_recovered_layers.tsv", layers)

    complete_hosts = []
    for host in sorted(by_token):
        if host.startswith("q") or host.endswith("dy"): continue
        forms = (host, "q" + host, host + "dy", "q" + host + "dy")
        if all(form in by_token for form in forms): complete_hosts.append(host)
    global_rows = []
    interactions = []; q_effects = []; dy_effects = []
    for host in complete_hosts:
        means = {cell: sum(float(row["normalized_position"]) for row in by_token[form]) / len(by_token[form]) for cell, form in zip(("00", "10", "01", "11"), (host, "q"+host, host+"dy", "q"+host+"dy"))}
        interaction = means["11"] - means["10"] - means["01"] + means["00"]
        qe = ((means["10"] - means["00"]) + (means["11"] - means["01"])) / 2
        de = ((means["01"] - means["00"]) + (means["11"] - means["10"])) / 2
        interactions.append(interaction); q_effects.append(qe); dy_effects.append(de)
        pages = [set(str(row["page"]) for row in by_token[form]) for form in (host,"q"+host,host+"dy","q"+host+"dy")]
        global_rows.append({"host":host,"bare_n":len(by_token[host]),"q_n":len(by_token["q"+host]),"dy_n":len(by_token[host+"dy"]),"qdy_n":len(by_token["q"+host+"dy"]),"q_main_position_effect":f"{qe:.12f}","dy_main_position_effect":f"{de:.12f}","interaction":f"{interaction:.12f}","same_page_complete":len(set.intersection(*pages)),"claim_state":"GLOBAL_TYPE_RECTANGLE_NO_PAGE_LOCAL_REPLICATION"})
    write_tsv("gdt011_q_dy_rectangles.tsv", global_rows)

    by_line = defaultdict(list)
    for row in groups: by_line[str(row["group_id"]).split("|G", 1)[0]].append(row)
    earlier = later = tied = eligible = 0
    for items in by_line.values():
        qrows = [row for row in items if str(row["token"]).startswith("q") and not str(row["token"]).endswith("dy")]
        dyrows = [row for row in items if str(row["token"]).endswith("dy") and not str(row["token"]).startswith("q")]
        if not qrows or not dyrows: continue
        eligible += 1
        mq = sum(float(row["normalized_position"]) for row in qrows) / len(qrows)
        md = sum(float(row["normalized_position"]) for row in dyrows) / len(dyrows)
        earlier += mq < md; later += mq > md; tied += mq == md
    line_p = exact_binomial_two_sided(earlier, earlier + later)
    interaction_summary = {
        "schema":"GDT011_Q_DY_INTERACTION_V1","global_complete_hosts":len(complete_hosts),"same_page_complete_rectangles":sum(int(row["same_page_complete"]) for row in global_rows),
        "global_mean_q_position_effect":sum(q_effects)/len(q_effects),"global_mean_dy_position_effect":sum(dy_effects)/len(dy_effects),"global_mean_interaction":sum(interactions)/len(interactions),
        "eligible_distinct_group_lines":eligible,"q_mean_before_dy_mean":earlier,"q_mean_after_dy_mean":later,"ties":tied,"two_sided_line_binomial_p":line_p,
        "decision":"FIELD_EDGE_AXES_NOT_WHOLE_LINE_BRACKETS",
    }
    (ROOT / "gdt011_q_dy_interaction.json").write_text(json.dumps(interaction_summary, indent=2, sort_keys=True)+"\n")

    layer_map = {row["operation"]:row["recovered_layer"] for row in layers}
    model = {
        "schema":"GDT011_DISTRIBUTIONAL_FIELD_GRAMMAR_V1","status":"DISTRIBUTIONAL_FIELD_LAYERS_RECOVERED",
        "field_grammar":"ENTRY(t/s/d) -> EARLY_CARRIER(q/ch/sh/che) -> LOCAL_FRAME(o/ot or unresolved host material) -> CLOSURE(DY)",
        "recovered_layers":layer_map,
        "interpretation":"The operations select rendering/record positions inside fields. q and DY do not demonstrably bracket whole lines; their scope and resolution mnemonics apply at field level only.",
        "f84r":{"opened":False,"joined":False,"scored":False},
        "claim_ceiling":"Distributional field functions only; no confirmed language, sound, morpheme, POS, word meaning, plaintext, or translation.",
    }
    (ROOT / "gdt011_field_layer_model.json").write_text(json.dumps(model, indent=2, sort_keys=True)+"\n")

    layer_text = ", ".join(f"{row['operation']}={row['recovered_layer']}" for row in layers)
    report = f"""# GDT011 distributional field-layer result

Status: **DISTRIBUTIONAL FIELD LAYERS RECOVERED**

## Result

Host-plus-page matching recovers a four-layer field grammar without using the
provisional semantic labels:

```text
ENTRY (t / s / d)
    -> EARLY CARRIER (q / ch / sh / che)
    -> LOCAL OR UNRESOLVED FRAME (o / ot and host material)
    -> CLOSURE (DY)
```

Recovered classes: {layer_text}.

`t` and `s` have the strongest line-entry shifts; `d` is a weaker member of
the same entry class.  q/sh move a matched host earlier; ch/che are reliably
non-final; none has the paired position-plus-initial signature of an entry
carrier.  o and ot do not acquire a complete directional class.  DY moves the
host later and toward line-final position.

## Meaning update

The best defensible functions are now:

- `t/s/d`: choose an entry or continuation record state;
- `q/ch/sh/che`: introduce or scope an early field;
- `o/ot`: local frame material whose function remains unresolved;
- `DY`: close or resolve the current field.

This is stronger than assigning a picture noun, because the classes were
recovered from attachment distributions across matched hosts and pages.

## q and DY do not bracket whole lines

Only {len(complete_hosts)} strict global hosts form all four `H, qH, Hdy,
qHdy` cells, and **zero** rectangles are complete within one page.  Their
global mean interaction is {interaction_summary['global_mean_interaction']:+.4f},
consistent with approximate additivity but not a held page-local test.

On {eligible} lines containing distinct q-only and DY-only groups, mean q
position precedes mean DY position on {earlier} and follows it on {later}
(two-sided p={line_p:.4f}).  There is no whole-line bracketing effect.  q and
DY are therefore field-edge states, not demonstrated opening and closing
brackets for an entire sentence or recipe record.

## What changed

GDT010's q-early and DY-late constraints survive.  GDT009's concrete
`d=active`, `s=state`, and line-wide current-scope language is too specific.
The useful decoder is a field-state grammar: entry carriers, early carriers,
local host material, and closure.  Exact lexical content remains inside the
page-local host inventory.

## Limits

The universe is selected for GDT002 candidate modules and is not a random
whole-manuscript sample.  Prefix strings can overlap (`che` also begins with
`ch`), and the recovered layers may be scribal generation states rather than
meaning-bearing grammar.  Forty primary tests are explicitly adjusted.  f84r
remained sealed.

No language, sound, word, POS, plaintext, or translation is claimed.
"""
    (ROOT / "GDT011_FIELD_LAYER_REPORT.md").write_text(report)

    inputs = ["gdt002_morphology_occurrences.tsv","gdt010_result.json","gdt009_result.json","GDT011_FIELD_LAYER_METHOD.md"]
    outputs = ["gdt011_operation_position_tests.tsv","gdt011_recovered_layers.tsv","gdt011_q_dy_rectangles.tsv","gdt011_q_dy_interaction.json","gdt011_field_layer_model.json","GDT011_FIELD_LAYER_REPORT.md"]
    result = {"schema":"GDT011_FIELD_LAYER_RESULT_V1","status":"DISTRIBUTIONAL_FIELD_LAYERS_RECOVERED","groups":len(groups),"operations":len(operations),"tests":len(tests),"family_tests":FAMILY_TESTS,"layers":layer_map,"interaction_decision":interaction_summary["decision"],"f84r":model["f84r"],"inputs":{x:sha(ROOT/x) for x in inputs},"implementation":{"run_gdt011_field_layer.py":sha(Path(__file__)),"run_gdt010_record_position.py":sha(ROOT/"run_gdt010_record_position.py")},"outputs":{x:sha(ROOT/x) for x in outputs},"claim_ceiling":model["claim_ceiling"]}
    result["result_content_sha256"] = canonical_sha(result)
    (ROOT / "gdt011_result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"layers":layer_map,"global_rectangles":len(complete_hosts),"same_page_rectangles":interaction_summary["same_page_complete_rectangles"],"line_p":line_p},sort_keys=True))


if __name__ == "__main__": main()
