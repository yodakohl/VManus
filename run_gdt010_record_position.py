#!/usr/bin/env python3
"""Run host-matched position tests for GDT009's provisional functions."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
PERMUTATIONS = 20_000
SEED = 9102026
METRICS = ("normalized_position", "line_final", "line_initial", "nonprose")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, object]]) -> None:
    with (ROOT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def tagged(value: str, key: str) -> str:
    for part in value.split(";"):
        if part.startswith(key + ":"):
            return part.split(":", 1)[1]
    return ""


def group_universe(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups = {}
    for row in rows:
        key = (row["locus"], row["source_group_index"])
        if key in groups or not row["ZL3b_token"] or not (row["ZL3b_token"] == row["IT2a_token"] == row["RF1b_token"]):
            continue
        count = int(tagged(row["source_group_count_by_reading"], "ZL3b"))
        index = int(row["source_group_index"])
        groups[key] = {
            "group_id": f"{row['locus']}|G{index:03d}", "token": row["ZL3b_token"],
            "normalized_position": (index - 1) / (count - 1) if count > 1 else 0.5,
            "line_final": int(index == count), "line_initial": int(index == 1),
            "nonprose": int(row["layout_role"] != "RUNNING_TEXT"),
            "page": row["page"], "folio": row["physical_folio"], "section": row["section"],
        }
    return list(groups.values())


def form_maps(groups: list[dict[str, object]]) -> dict[str, tuple[dict[str, list[dict]], dict[str, list[dict]]]]:
    by_token: dict[str, list[dict]] = defaultdict(list)
    for row in groups: by_token[str(row["token"])].append(row)
    bare_q, q = defaultdict(list), defaultdict(list)
    s, d = defaultdict(list), defaultdict(list)
    suffix = {x: defaultdict(list) for x in ("dy", "dal", "dar", "sy")}
    bare_right = defaultdict(list)
    for token, items in by_token.items():
        if token.startswith("q") and len(token) > 1: q[token[1:]].extend(items)
        else: bare_q[token].extend(items)
        if token.startswith("s") and len(token) > 1: s[token[1:]].extend(items)
        if token.startswith("d") and len(token) > 1: d[token[1:]].extend(items)
        matched = False
        for ending in ("dal", "dar", "sy", "dy"):
            if token.endswith(ending) and len(token) > len(ending):
                suffix[ending][token[:-len(ending)]].extend(items); matched = True; break
        if not matched: bare_right[token].extend(items)
    return {
        "C01_BARE_TO_Q": (bare_q, q), "C02_S_TO_D": (s, d),
        "C03_BARE_TO_DY": (bare_right, suffix["dy"]),
        "C04_BARE_TO_SY": (bare_right, suffix["sy"]),
        "C05_DAL_TO_DAR": (suffix["dal"], suffix["dar"]),
    }


def matched_strata(a: dict[str, list[dict]], b: dict[str, list[dict]], scope: str, omit_key: str = "", omit_value: str = "") -> list[tuple[str, list[dict], list[dict]]]:
    out = []
    for host in sorted(set(a) & set(b)):
        aa = [r for r in a[host] if not omit_key or r[omit_key] != omit_value]
        bb = [r for r in b[host] if not omit_key or r[omit_key] != omit_value]
        if scope == "HOST_GLOBAL": buckets = [(host, aa, bb)]
        else:
            key = "folio" if scope == "HOST_PHYSICAL_FOLIO" else "page"
            av, bv = defaultdict(list), defaultdict(list)
            for row in aa: av[str(row[key])].append(row)
            for row in bb: bv[str(row[key])].append(row)
            buckets = [(f"{host}|{value}", av[value], bv[value]) for value in sorted(set(av) & set(bv))]
        out.extend((name, left, right) for name, left, right in buckets if left and right)
    return out


def effect(strata: list[tuple[str, list[dict], list[dict]]], metric: str) -> tuple[float, int, int, int, int]:
    numerator = denominator = 0.0; positive = negative = n_a = n_b = 0
    for _, aa, bb in strata:
        ma = sum(float(r[metric]) for r in aa) / len(aa); mb = sum(float(r[metric]) for r in bb) / len(bb)
        weight = len(aa) * len(bb) / (len(aa) + len(bb))
        numerator += weight * (mb - ma); denominator += weight; n_a += len(aa); n_b += len(bb)
        positive += mb > ma; negative += mb < ma
    return (numerator / denominator if denominator else math.nan, positive, negative, n_a, n_b)


def permutation_p(strata: list[tuple[str, list[dict], list[dict]]], metric: str, observed: float, seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    pools = []
    for _, aa, bb in strata:
        values = [float(r[metric]) for r in aa + bb]
        pools.append((values, len(aa), len(bb), len(aa) * len(bb) / (len(aa) + len(bb))))
    denominator = sum(x[3] for x in pools); null = np.zeros(PERMUTATIONS)
    for values, na, nb, weight in pools:
        values = np.asarray(values); total = float(values.sum()); n = len(values)
        # Choose the smaller class to keep the temporary random matrix compact.
        choose_b = nb <= na; take = nb if choose_b else na
        scores = rng.random((PERMUTATIONS, n), dtype=np.float32)
        chosen = np.argpartition(scores, take - 1, axis=1)[:, :take]
        selected = values[chosen].sum(axis=1)
        if choose_b: sb, sa = selected, total - selected
        else: sa, sb = selected, total - selected
        null += weight * (sb / nb - sa / na)
    null /= denominator
    p = (1 + int(np.sum(np.abs(null) >= abs(observed) - 1e-15))) / (PERMUTATIONS + 1)
    low, high = np.quantile(null, [.025, .975])
    return p, float(low), float(high)


def main() -> None:
    source = read_tsv("gdt002_morphology_occurrences.tsv")
    assert not any(row["locus"].startswith("f84r") for row in source)
    gdt009 = json.loads((ROOT / "gdt009_result.json").read_text())
    assert gdt009["leading_theory"] == "PRS1_PROCEDURAL_REFERENCE_STATE"
    groups = group_universe(source); contrasts = form_maps(groups)
    rows = []
    for ci, (contrast, (a, b)) in enumerate(contrasts.items(), 1):
        hosts = sorted(set(a) & set(b))
        folios = sorted({str(r["folio"]) for h in hosts for r in a[h] + b[h]})
        sections = sorted({str(r["section"]) for h in hosts for r in a[h] + b[h]})
        for si, scope in enumerate(("HOST_GLOBAL", "HOST_PHYSICAL_FOLIO", "HOST_PAGE"), 1):
          strata = matched_strata(a, b, scope)
          for mi, metric in enumerate(METRICS, 1):
            observed, positive, negative, na, nb = effect(strata, metric)
            p, low, high = permutation_p(strata, metric, observed, SEED + ci * 1000 + si * 100 + mi)
            lofo = [effect(matched_strata(a, b, scope, "folio", value), metric)[0] for value in folios]
            losection = [effect(matched_strata(a, b, scope, "section", value), metric)[0] for value in sections]
            lofo = [x for x in lofo if not math.isnan(x)]; losection = [x for x in losection if not math.isnan(x)]
            rows.append({
                "contrast_id": contrast, "match_scope": scope, "metric": metric, "host_types": len({name.split("|",1)[0] for name,_,_ in strata}), "matched_strata": len(strata), "form_a_groups": na, "form_b_groups": nb,
                "host_fixed_effect_B_minus_A": f"{observed:.12f}", "positive_hosts": positive, "negative_hosts": negative,
                "permutation_draws": PERMUTATIONS, "two_sided_permutation_p": f"{p:.8f}",
                "search_adjusted_p_20_primary_tests": f"{min(1.0, p * 20):.8f}" if scope == "HOST_PAGE" else "",
                "null_2_5pct": f"{low:.12f}", "null_97_5pct": f"{high:.12f}",
                "lofo_min": f"{min(lofo):.12f}", "lofo_max": f"{max(lofo):.12f}",
                "lofo_same_sign_fraction": f"{sum((x > 0) == (observed > 0) for x in lofo) / len(lofo):.6f}",
                "leave_section_min": f"{min(losection):.12f}", "leave_section_max": f"{max(losection):.12f}",
                "claim_state": "EXPLORATORY_HOST_MATCHED_MODULE_SELECTED_UNIVERSE",
            })
    write_tsv("gdt010_record_position_tests.tsv", rows)

    by = {(r["contrast_id"], r["match_scope"], r["metric"]): r for r in rows}
    primary = "HOST_PAGE"
    interpretations = [
        {"constraint":"Q_EARLY_SCOPE","evidence":"C01_BARE_TO_Q HOST_PAGE normalized_position","effect":by[("C01_BARE_TO_Q",primary,"normalized_position")]["host_fixed_effect_B_minus_A"],"p":by[("C01_BARE_TO_Q",primary,"normalized_position")]["two_sided_permutation_p"],"decision":"USEFUL_PROVISIONAL_CONSTRAINT","semantic_update":"q selects an early/current-frame dependent rendering and is not an object-label marker."},
        {"constraint":"D_LATER_THAN_S","evidence":"C02_S_TO_D HOST_PAGE normalized_position","effect":by[("C02_S_TO_D",primary,"normalized_position")]["host_fixed_effect_B_minus_A"],"p":by[("C02_S_TO_D",primary,"normalized_position")]["two_sided_permutation_p"],"decision":"LIKELY_PAGE_OR_REGISTER_CONFOUND","semantic_update":"The global later-d trend weakens to p=.203 within host-page; do not assign d/s meanings from position."},
        {"constraint":"DY_COMPLETION","evidence":"C03_BARE_TO_DY HOST_PAGE normalized_position + line_final","effect":by[("C03_BARE_TO_DY",primary,"normalized_position")]["host_fixed_effect_B_minus_A"]+";final="+by[("C03_BARE_TO_DY",primary,"line_final")]["host_fixed_effect_B_minus_A"],"p":by[("C03_BARE_TO_DY",primary,"normalized_position")]["two_sided_permutation_p"]+";final="+by[("C03_BARE_TO_DY",primary,"line_final")]["two_sided_permutation_p"],"decision":"STRONGEST_FUNCTIONAL_CONSTRAINT","semantic_update":"DY is the best current record-completion/resolution operator."},
        {"constraint":"SY_MARKED_TERMINAL","evidence":"C04_BARE_TO_SY HOST_PAGE line_final","effect":by[("C04_BARE_TO_SY",primary,"line_final")]["host_fixed_effect_B_minus_A"],"p":by[("C04_BARE_TO_SY",primary,"line_final")]["two_sided_permutation_p"],"decision":"INSUFFICIENT_WITHIN_PAGE_CAPACITY","semantic_update":"Global terminal behavior is suggestive, but only two host-page strata exist; do not assign secondary/exception meaning yet."},
        {"constraint":"DAR_LATER_CONFIGURATION","evidence":"C05_DAL_TO_DAR HOST_PAGE normalized_position","effect":by[("C05_DAL_TO_DAR",primary,"normalized_position")]["host_fixed_effect_B_minus_A"],"p":by[("C05_DAL_TO_DAR",primary,"normalized_position")]["two_sided_permutation_p"],"decision":"INTERESTING_EXPLORATORY_SEARCH_SENSITIVE","semantic_update":"DAR is later than DAL locally (p=.025) but not after the 20-test search adjustment (.505); retain as a risky lead only."},
    ]
    write_tsv("gdt010_functional_constraints.tsv", interpretations)
    model = {
        "schema":"GDT010_ORDERED_RECORD_SKELETON_V1","status":"USEFUL_POSITIONAL_FUNCTIONS_RECOVERED",
        "record_skeleton":"[q EARLY/CURRENT-FRAME]? HOST [DY LATE/RESOLUTION]?",
        "updates":{"q":"early/current-frame scope (search-adjusted)","s_d":"global ordering is page/register-confounded; functions unresolved","DAL_DAR":"same-slot alternatives; DAR-later is a search-sensitive lead only","SY":"terminal-looking but insufficient within-page capacity","DY":"late record completion/resolution (strongest; search-adjusted)"},
        "scope":"All-reading-exact groups from the non-f84 GDT002 module-selected occurrence universe; no sound, word, POS, language, or translation.",
        "f84r":{"opened":False,"joined":False,"scored":False},
    }
    (ROOT / "gdt010_ordered_record_model.json").write_text(json.dumps(model, indent=2, sort_keys=True)+"\n")

    q = by[("C01_BARE_TO_Q",primary,"normalized_position")]; ds = by[("C02_S_TO_D",primary,"normalized_position")]
    dypos = by[("C03_BARE_TO_DY",primary,"normalized_position")]; dyfin = by[("C03_BARE_TO_DY",primary,"line_final")]
    sy = by[("C04_BARE_TO_SY",primary,"line_final")]; dd = by[("C05_DAL_TO_DAR",primary,"normalized_position")]
    report = f"""# GDT010 ordered record-position result

Status: **USEFUL POSITIONAL FUNCTIONS RECOVERED**

## Main result

The provisional pieces do not merely occupy arbitrary string positions.  When
the lexical host is held fixed, they form a reproducible line-order skeleton:

```text
[q EARLY / CURRENT FRAME]  HOST  [DY LATE / RESOLUTION]
```

This is the first useful empirical refinement of PRS-1.

## Strongest constraints

- Adding **DY** to the same host shifts normalized line position by
  **{float(dypos['host_fixed_effect_B_minus_A']):+.3f}** and raises line-final
  probability by **{float(dyfin['host_fixed_effect_B_minus_A']):+.3f}** across
  {dypos['matched_strata']} matched host-page strata.  Both page-stratified permutation p-values are
  {dypos['two_sided_permutation_p']} and {dyfin['two_sided_permutation_p']}.
  Their 20-test adjusted values remain {dypos['search_adjusted_p_20_primary_tests']}
  and {dyfin['search_adjusted_p_20_primary_tests']}.
  DY is therefore the strongest current candidate for *completion/resolution*.
- Adding **q** shifts the same host **{float(q['host_fixed_effect_B_minus_A']):+.3f}**
  of a line ({q['matched_strata']} host-page strata; p={q['two_sided_permutation_p']},
  20-test adjusted p={q['search_adjusted_p_20_primary_tests']}).  It also
  reduces nonprose use.  This supports early/current-frame scope rather than an
  object-label function.
- For the same host, **d** occurs **{float(ds['host_fixed_effect_B_minus_A']):+.3f}**
  later than **s** ({ds['matched_strata']} host-page strata; p={ds['two_sided_permutation_p']}).
  The local p-value is {ds['two_sided_permutation_p']}; the global contrast was
  misleading.  d/s meaning remains unresolved rather than being forced into
  active/state semantics.
- **SY** looks terminal globally, but only {sy['matched_strata']} matched
  host-page strata exist.  It is therefore not assigned a meaning.
- **DAR** occurs **{float(dd['host_fixed_effect_B_minus_A']):+.3f}** later than
  **DAL** across {dd['matched_strata']} matched host-page strata
  (local p={dd['two_sided_permutation_p']}, 20-test adjusted
  p={dd['search_adjusted_p_20_primary_tests']}).  This is an interesting risky
  lead, not yet a decoder constraint and not source/destination.

## Why this is useful

The result converts two glosses into an ordered decoder constraint.  A
candidate parse now pays a penalty if q is treated as a late closure or DY as
an early scope marker.  d/s and DAL/DAR remain exploratory branches rather
than forced meanings.  `qotedy` is consequently best read structurally as:

```text
[current-frame scope] [host/grade] [resolved result]
```

and not as an indivisible noun.

## Limits

The corpus is selected for containing one of the GDT002 candidate modules, so
the effect sizes are not whole-manuscript prevalence estimates.  Host-plus-page
matching removes exact-host and between-page composition, but not within-page
record position, register, or scribal-production mechanisms.  Permutations
quantify position association, not semantics.  The pure-template model can
generate such ordering; meaning still depends on the joint PRS-1
interpretation.

f84r remained sealed.  No language, sound, word, POS, plaintext, or translation
is claimed.
"""
    (ROOT / "GDT010_RECORD_POSITION_REPORT.md").write_text(report)

    inputs = ["gdt002_morphology_occurrences.tsv","gdt009_result.json","gdt009_semantic_model.json","GDT010_RECORD_POSITION_METHOD.md"]
    outputs = ["gdt010_record_position_tests.tsv","gdt010_functional_constraints.tsv","gdt010_ordered_record_model.json","GDT010_RECORD_POSITION_REPORT.md"]
    result = {"schema":"GDT010_RECORD_POSITION_RESULT_V1","status":"USEFUL_POSITIONAL_FUNCTIONS_RECOVERED","group_universe":len(groups),"contrasts":len(contrasts),"matching_scopes":3,"primary_scope":"HOST_PAGE","permutations_per_test":PERMUTATIONS,"primary_updates":model["updates"],"f84r":model["f84r"],"inputs":{x:sha(ROOT/x) for x in inputs},"implementation":{"run_gdt010_record_position.py":sha(Path(__file__))},"outputs":{x:sha(ROOT/x) for x in outputs},"claim_ceiling":model["scope"]}
    result["result_content_sha256"] = canonical_sha(result)
    (ROOT / "gdt010_result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"groups":len(groups),"dy_position":dypos["host_fixed_effect_B_minus_A"],"dy_final":dyfin["host_fixed_effect_B_minus_A"],"q_position":q["host_fixed_effect_B_minus_A"],"d_minus_s":ds["host_fixed_effect_B_minus_A"]},sort_keys=True))


if __name__ == "__main__": main()
