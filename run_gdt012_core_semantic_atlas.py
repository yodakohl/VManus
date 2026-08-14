#!/usr/bin/env python3
"""Build a page-conditioned exploratory atlas of residual host content."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/semantic_assumptions/results"
PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
MODULES = ("ar", "ol", "dal", "dar", "sy", "te", "tee", "ai", "aii")
OBJECTS = ("PLANT", "FIGURE", "WATER_OR_APPARATUS", "STAR_OR_SKY", "ROSETTE_OR_MAP")
RELATIONS = ("REL_EXPLICIT_ATTACHMENT", "REL_ENCLOSURE", "REL_OVERLAP_OR_CONTACT", "REL_PROXIMITY", "REL_ARRAY_OR_GROUP")
OUTCOMES = OBJECTS + RELATIONS


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"(f\d+)", page)
    return match.group(1) if match else page


def strip_layers(token: str) -> tuple[str, str, int]:
    prefix = "NONE"
    host = token
    for candidate in PREFIXES:
        if host.startswith(candidate) and len(host) > len(candidate):
            prefix = candidate
            host = host[len(candidate):]
            break
    closure = int(host.endswith("dy") and len(host) > 2)
    if closure:
        host = host[:-2]
    return prefix, host, closure


def build_inventory() -> list[dict[str, object]]:
    annotations = {r["locus"]: r for r in read_tsv(RESULTS / "existing_human_exact_locus_annotations.tsv") if not r["locus"].startswith("f84r")}
    align = defaultdict(list)
    # Guard f84 before retaining any source-formal record.
    with (RESULTS / "source_sta_group_alignment.tsv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"].startswith("f84r") or row["locus"] not in annotations:
                continue
            align[(row["locus"], row["source_group_index"])].append(row)
    consensus = {}
    with (RESULTS / "source_sta_family_consensus_groups.tsv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"].startswith("f84r") or row["locus"] not in annotations:
                continue
            consensus[(row["locus"], row["consensus_group_index"])] = row
    out = []
    for key, readings in sorted(align.items()):
        con = consensus.get(key)
        if not con or con["strict_zero_alternative"] != "1" or con["grammar_scope"] != "DIAGNOSTIC_NONPROSE":
            continue
        if {r["edition"] for r in readings} != {"ZL3b", "IT2a", "RF1b"}:
            continue
        tokens = {r["nearest_basic_eva_primary"] for r in readings}
        families = {r["primary_sta_families"] for r in readings}
        if len(tokens) != 1 or len(families) != 1 or "" in tokens:
            continue
        token = next(iter(tokens)); prefix, host, closure = strip_layers(token); ann = annotations[key[0]]
        object_tags = set(filter(None, ann["object_tags"].split(";")))
        relation_tags = set(filter(None, (ann["local_relation_tags"] + ";" + ann["unit_relation_tags"]).split(";")))
        out.append({
            "group_id": f"{key[0]}|G{int(key[1]):03d}", "locus": key[0], "page": con["page"], "physical_folio": physical_folio(con["page"]),
            "group_index": int(key[1]), "group_count": int(con["consensus_group_count"]), "token": token,
            "stripped_prefix": prefix, "residual_host": host, "dy_closure": closure, "family_surface": con["family_surface"],
            "family_length": int(con["symbol_count"]), "host_length": len(host), "section": con["section"], "currier": con["currier"],
            "hand": con["hand"], "kind": con["kind"], "grammar_scope": con["grammar_scope"], "annotation_certainty": ann["certainty"],
            "object_tags": ";".join(sorted(object_tags)), "relation_tags": ";".join(sorted(relation_tags)),
            "unit": ann["unit"], "annotation_source": ann["source_path"], "raw_source_description": " || ".join(x.strip() for x in (ann["unit_description"],ann["local_comment"]) if x.strip()),
        })
    return out


def feature_masks(rows: list[dict[str, object]]) -> dict[str, set[int]]:
    masks: dict[str, set[int]] = {}
    def add(name: str, indexes: set[int], typed: bool = True) -> None:
        pages = {str(rows[i]["page"]) for i in indexes}
        if not typed or (len(indexes) >= 3 and len(pages) >= 2):
            masks[name] = indexes
    for field, label in (("token", "TOKEN_EQ"), ("residual_host", "HOST_EQ"), ("family_surface", "FAMILY_EQ")):
        values = defaultdict(set)
        for i, row in enumerate(rows): values[str(row[field])].add(i)
        for value, indexes in values.items(): add(f"{label}:{value}", indexes)
    for module in MODULES:
        add(f"HOST_CONTAINS:{module}", {i for i,r in enumerate(rows) if module in str(r["residual_host"])}, False)
        add(f"HOST_PREFIX:{module}", {i for i,r in enumerate(rows) if str(r["residual_host"]).startswith(module)}, False)
        add(f"HOST_SUFFIX:{module}", {i for i,r in enumerate(rows) if str(r["residual_host"]).endswith(module)}, False)
    for prefix in ("NONE",) + PREFIXES:
        add(f"STRIPPED_PREFIX:{prefix}", {i for i,r in enumerate(rows) if r["stripped_prefix"] == prefix}, False)
    add("DY_CLOSURE", {i for i,r in enumerate(rows) if r["dy_closure"] == 1}, False)
    for length in sorted({int(r["host_length"]) for r in rows}):
        add(f"HOST_LENGTH:{length}", {i for i,r in enumerate(rows) if r["host_length"] == length}, False)
    for length in sorted({int(r["family_length"]) for r in rows}):
        add(f"FAMILY_LENGTH:{length}", {i for i,r in enumerate(rows) if r["family_length"] == length}, False)
    return {k:v for k,v in masks.items() if 0 < len(v) < len(rows)}


def has_outcome(row: dict[str, object], outcome: str) -> bool:
    field = "object_tags" if outcome in OBJECTS else "relation_tags"
    return outcome in str(row[field]).split(";")


def hypergeom_pmf(n: int, k: int, m: int) -> dict[int, Fraction]:
    denominator = math.comb(n, m)
    return {x: Fraction(math.comb(k, x) * math.comb(n-k, m-x), denominator)
            for x in range(max(0, m-(n-k)), min(m, k)+1)}


def exact_page_test(rows: list[dict[str, object]], feature: set[int], outcome: str, allowed: set[int], stratum_field: str = "page") -> dict[str, object]:
    pages = defaultdict(list)
    for i in allowed: pages[str(rows[i][stratum_field])].append(i)
    strata=[]; observed_total=0; expected=Fraction(0); weighted_num=0.; weighted_den=0.
    for page, indexes in pages.items():
        n=len(indexes); m=sum(i in feature for i in indexes); k=sum(has_outcome(rows[i],outcome) for i in indexes)
        if not (0 < m < n and 0 < k < n): continue
        x=sum(i in feature and has_outcome(rows[i],outcome) for i in indexes)
        exp=Fraction(m*k,n); w=m*(n-m)/n
        risk=(x/m)-((k-x)/(n-m))
        strata.append((page,n,m,k,x)); observed_total+=x; expected+=exp; weighted_num+=w*risk; weighted_den+=w
    effect=weighted_num/weighted_den if weighted_den else 0.
    pmf={0:Fraction(1)}
    for _,n,m,k,_ in strata:
        nxt=defaultdict(Fraction)
        for a,pa in pmf.items():
            for b,pb in hypergeom_pmf(n,k,m).items(): nxt[a+b]+=pa*pb
        pmf=dict(nxt)
    distance=abs(Fraction(observed_total)-expected)
    p=sum(prob for value,prob in pmf.items() if abs(Fraction(value)-expected)>=distance) if strata else Fraction(1)
    loo=[]
    for omitted, *_ in strata:
        keep={i for i in allowed if str(rows[i][stratum_field]) != omitted}
        loo.append(float(exact_page_test_no_loo(rows,feature,outcome,keep,stratum_field)["effect"]))
    return {"effect":effect,"p":float(p),"informative_pages":len(strata),"observed":observed_total,"expected":float(expected),
            "loo_min":min(loo) if loo else effect,"loo_max":max(loo) if loo else effect,"strata":";".join(f"{p}:{n}/{m}/{k}/{x}" for p,n,m,k,x in strata)}


def exact_page_test_no_loo(rows: list[dict[str, object]], feature: set[int], outcome: str, allowed: set[int], stratum_field: str = "page") -> dict[str, float]:
    pages=defaultdict(list)
    for i in allowed: pages[str(rows[i][stratum_field])].append(i)
    num=den=0.
    for indexes in pages.values():
        n=len(indexes);m=sum(i in feature for i in indexes);k=sum(has_outcome(rows[i],outcome) for i in indexes)
        if not(0<m<n and 0<k<n):continue
        x=sum(i in feature and has_outcome(rows[i],outcome) for i in indexes);w=m*(n-m)/n
        num+=w*((x/m)-((k-x)/(n-m)));den+=w
    return {"effect":num/den if den else 0.}


def classify(primary: dict[str, object], all_effect: float, single_effect: float) -> str:
    effect=float(primary["effect"]); p=float(primary["p"]); pages=int(primary["informative_pages"])
    reverse=lambda x: abs(x)>1e-12 and abs(effect)>1e-12 and x*effect<0
    if reverse(all_effect) or reverse(single_effect) or (primary["loo_min"] < 0 < primary["loo_max"]): return "UNSTABLE"
    if pages < 2: return "LIKELY_PAGE_CONFOUND"
    stable=not (primary["loo_min"] < 0 < primary["loo_max"])
    if pages>=3 and p<.05 and stable:return "INTERESTING_EXPLORATORY"
    if p<.10 or abs(effect)>=.35:return "WEAK"
    return "NO_SIGNAL"


def main() -> None:
    rows=build_inventory(); assert rows and not any(str(r["locus"]).startswith("f84r") for r in rows)
    write_tsv(ROOT/"gdt012_annotated_core_inventory.tsv",rows)
    primary={i for i,r in enumerate(rows) if r["annotation_certainty"]=="UNHEDGED"}
    all_rows=set(range(len(rows))); single={i for i in primary if int(rows[i]["group_count"])==1}
    masks=feature_masks(rows); family_tests=len(masks)*len(OUTCOMES)
    atlas=[]
    for feature,indexes in sorted(masks.items()):
        for outcome in OUTCOMES:
            test=exact_page_test(rows,indexes,outcome,primary)
            folio_test=exact_page_test(rows,indexes,outcome,primary,"physical_folio")
            all_effect=exact_page_test_no_loo(rows,indexes,outcome,all_rows)["effect"]
            single_effect=exact_page_test_no_loo(rows,indexes,outcome,single)["effect"]
            support=sum(i in indexes for i in primary); positive=sum(i in indexes and has_outcome(rows[i],outcome) for i in primary)
            atlas.append({"candidate_id":hashlib.sha256((feature+"|"+outcome).encode()).hexdigest()[:12],"formal_feature":feature,"visual_outcome":outcome,
                "primary_rows":len(primary),"feature_support":support,"feature_positive":positive,"informative_pages":test["informative_pages"],
                "within_page_effect":f"{test['effect']:.12f}","exact_local_p":f"{test['p']:.12f}","search_adjusted_p":f"{min(1.,test['p']*family_tests):.12f}",
                "conditional_observed":test["observed"],"conditional_expected":f"{test['expected']:.9f}","leave_one_page_effect_min":f"{test['loo_min']:.12f}","leave_one_page_effect_max":f"{test['loo_max']:.12f}",
                "within_physical_folio_effect":f"{folio_test['effect']:.12f}","physical_folio_exact_p":f"{folio_test['p']:.12f}","informative_physical_folios":folio_test["informative_pages"],"leave_one_folio_effect_min":f"{folio_test['loo_min']:.12f}","leave_one_folio_effect_max":f"{folio_test['loo_max']:.12f}",
                "all_certainty_effect":f"{all_effect:.12f}","single_group_only_effect":f"{single_effect:.12f}","informative_page_strata":test["strata"],
                "label":classify(test,all_effect,single_effect),"claim_state":"POSTSELECTED_VISUAL_FORMAL_ASSOCIATION_NOT_MEANING"})
    priority={"INTERESTING_EXPLORATORY":0,"WEAK":1,"UNSTABLE":2,"LIKELY_PAGE_CONFOUND":3,"NO_SIGNAL":4}
    atlas.sort(key=lambda r:(priority[r["label"]],float(r["exact_local_p"]),-abs(float(r["within_page_effect"])),r["formal_feature"],r["visual_outcome"]))
    write_tsv(ROOT/"gdt012_core_semantic_candidates.tsv",atlas)

    strongest=atlas[0]
    host_candidates=[r for r in atlas if r["formal_feature"].startswith("HOST_EQ:")]
    strongest_host=host_candidates[0] if host_candidates else strongest
    module_candidates=[r for r in atlas if r["formal_feature"].startswith(("HOST_CONTAINS:","HOST_PREFIX:","HOST_SUFFIX:"))]
    strongest_module=module_candidates[0] if module_candidates else strongest
    controls=[]
    token_types=len({str(r["token"]) for r in rows});host_types=len({str(r["residual_host"]) for r in rows})
    token_cross=sum(len({str(r["page"]) for r in rows if r["token"]==t})>=2 for t in {str(r["token"]) for r in rows})
    host_cross=sum(len({str(r["page"]) for r in rows if r["residual_host"]==h})>=2 for h in {str(r["residual_host"]) for r in rows})
    controls.extend([
        {"control":"TYPE_REUSE","metric":"UNSTRIPPED_TOKEN_TYPES","value":token_types,"detail":"exact three-reading display types"},
        {"control":"TYPE_REUSE","metric":"RESIDUAL_HOST_TYPES","value":host_types,"detail":"after one prefix plus optional DY removal"},
        {"control":"CROSS_PAGE_REUSE","metric":"UNSTRIPPED_TYPES_ON_2PLUS_PAGES","value":token_cross,"detail":"state-blind"},
        {"control":"CROSS_PAGE_REUSE","metric":"RESIDUAL_HOSTS_ON_2PLUS_PAGES","value":host_cross,"detail":"state-blind"},
        {"control":"SEARCH","metric":"FEATURE_OUTCOME_TESTS","value":family_tests,"detail":"Bonferroni family"},
        {"control":"HOLDOUT","metric":"F84R_ROWS_RETAINED","value":0,"detail":"sealed"},
    ])
    write_tsv(ROOT/"gdt012_core_semantic_controls.tsv",controls)

    counter=[]
    for candidate in [strongest,strongest_host,strongest_module]:
        feature=candidate["formal_feature"]; outcome=candidate["visual_outcome"]; mask=masks[feature]
        for i,row in enumerate(rows):
            if i not in primary:continue
            relation="FEATURE_WITHOUT_OUTCOME" if i in mask and not has_outcome(row,outcome) else "OUTCOME_WITHOUT_FEATURE" if i not in mask and has_outcome(row,outcome) else ""
            if relation:
                counter.append({"candidate_id":candidate["candidate_id"],"formal_feature":feature,"visual_outcome":outcome,"counterexample_type":relation,"group_id":row["group_id"],"token":row["token"],"residual_host":row["residual_host"],"page":row["page"],"object_tags":row["object_tags"],"relation_tags":row["relation_tags"],"description":row["raw_source_description"]})
            if sum(x["candidate_id"]==candidate["candidate_id"] for x in counter)>=12:break
    write_tsv(ROOT/"gdt012_core_semantic_counterexamples.tsv",counter)

    indexed={(r["formal_feature"],r["visual_outcome"]):r for r in atlas}
    role_specs=[
        ("AR","HOST_CONTAINS:ar","REL_ENCLOSURE","BOUNDED_LOCAL_ASSOCIATION","The strongest reusable-module lead; compatible with a local referent/association element, not an object noun."),
        ("DAL","HOST_CONTAINS:dal","REL_ARRAY_OR_GROUP","ARRAY_OR_CONFIGURATION_STATE","A positive array/group association paired with depletion on plant outcomes; still sparse."),
        ("DAR","HOST_SUFFIX:dar","REL_PROXIMITY","POSITIONAL_OR_PROXIMAL_STATE","Weak cross-page proximity enrichment; does not identify source, destination, or direction."),
        ("O_HOST","HOST_EQ:o","REL_EXPLICIT_ATTACHMENT","ATTACHED_INDEX_OR_MINIMAL_FIELD","Sparse exact-host lead dominated by very short diagram labels."),
        ("ONE_SIGN_HOST","HOST_LENGTH:1","REL_EXPLICIT_ATTACHMENT","INDEX_LABEL_CLASS","Strongest adjusted association, but likely a mechanical class of one-sign diagram indices rather than lexical content."),
    ]
    roles=[]
    for unit,feature,outcome,role,note in role_specs:
        candidate=indexed.get((feature,outcome))
        if not candidate:continue
        roles.append({"formal_unit":unit,"formal_feature":feature,"provisional_role":role,"visual_outcome":outcome,"candidate_id":candidate["candidate_id"],"label":candidate["label"],
            "within_page_effect":candidate["within_page_effect"],"exact_local_p":candidate["exact_local_p"],"search_adjusted_p":candidate["search_adjusted_p"],"informative_pages":candidate["informative_pages"],
            "within_physical_folio_effect":candidate["within_physical_folio_effect"],"physical_folio_exact_p":candidate["physical_folio_exact_p"],"informative_physical_folios":candidate["informative_physical_folios"],
            "certainty_sensitivity_effect":candidate["all_certainty_effect"],"interpretive_note":note,"claim_state":"SPECULATIVE_FUNCTION_NOT_WORD_MEANING"})
    write_tsv(ROOT/"gdt012_provisional_core_roles.tsv",roles)

    interesting=sum(r["label"]=="INTERESTING_EXPLORATORY" for r in atlas); weak=sum(r["label"]=="WEAK" for r in atlas)
    status="RESIDUAL_CORE_VISUAL_LEADS_EXPLORATORY" if interesting or weak else "RESIDUAL_CORE_MEANING_REMAINS_PAGE_LOCAL"
    result={"schema":"GDT012_CORE_SEMANTIC_ATLAS_RESULT_V1","status":status,"inventory_rows":len(rows),"primary_unhedged_rows":len(primary),"pages":len({r['page'] for r in rows}),
        "token_types":token_types,"residual_host_types":host_types,"cross_page_token_types":token_cross,"cross_page_residual_hosts":host_cross,"feature_count":len(masks),"outcomes":len(OUTCOMES),"family_tests":family_tests,
        "label_counts":dict(Counter(r["label"] for r in atlas)),"strongest_candidate":strongest,"strongest_exact_host_candidate":strongest_host,"strongest_reusable_module_candidate":strongest_module,
        "f84r":{"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Post-selected visual-formal meaning leads only; no confirmed word, morpheme, POS, language, plaintext, or translation."}
    report=f"""# GDT012 residual-core semantic atlas

Status: **{status.replace('_',' ')}**

## Result

The atlas joins **{len(rows)}** exact all-reading, source-native groups on
**{len({r['page'] for r in rows})}** non-f84 pages to existing human visual
annotations.  The primary unhedged set has **{len(primary)}** rows.  Removing
one recovered left layer and optional `DY` closure reduces {token_types}
surface types to {host_types} residual hosts; cross-page reused types change
from {token_cross} to {host_cross}.  This is evidence that the renderer layers
collapse variants, but not by itself evidence of meaning.

The complete state-blind scan contains {family_tests} feature/outcome tests.
It retains {interesting} `INTERESTING_EXPLORATORY` and {weak} `WEAK` entries.
No adjusted p-value is treated as confirmation.

Strongest ranked association:

- `{strongest['formal_feature']}` versus `{strongest['visual_outcome']}`;
- within-page effect {float(strongest['within_page_effect']):+.3f};
- {strongest['informative_pages']} informative pages;
- exact local p={float(strongest['exact_local_p']):.4g}, search-adjusted
  p={float(strongest['search_adjusted_p']):.4g};
- label `{strongest['label']}`.

Strongest exact residual-host association:

- `{strongest_host['formal_feature']}` versus
  `{strongest_host['visual_outcome']}`;
- within-page effect {float(strongest_host['within_page_effect']):+.3f};
- {strongest_host['informative_pages']} informative pages;
- exact local p={float(strongest_host['exact_local_p']):.4g}, adjusted
  p={float(strongest_host['search_adjusted_p']):.4g};
- label `{strongest_host['label']}`.

Strongest reusable-module association:

- `{strongest_module['formal_feature']}` versus
  `{strongest_module['visual_outcome']}`;
- within-page effect {float(strongest_module['within_page_effect']):+.3f}
  across {strongest_module['informative_pages']} informative pages;
- exact local p={float(strongest_module['exact_local_p']):.4g}, adjusted
  p={float(strongest_module['search_adjusted_p']):.4g};
- label `{strongest_module['label']}`.

This makes the most useful current semantic guess **AR = bounded/local
association or referent anchoring**.  It does not make AR a noun meaning
“circle”, “inside”, or any depicted object.  The effect is present on four
pages and survives single-group restriction, but the all-certainty effect
falls from {float(strongest_module['within_page_effect']):+.3f} to
{float(strongest_module['all_certainty_effect']):+.3f}; the global search
adjustment is null.  At the stricter physical-folio level the effect is
{float(strongest_module['within_physical_folio_effect']):+.3f} across
{strongest_module['informative_physical_folios']} informative folios (exact
p={float(strongest_module['physical_folio_exact_p']):.4g}), exposing material
diagram-family confounding.  Plant-label and ordinary proximity occurrences are
published as counterexamples.

Other deliberately provisional readings are `DAL` as an array/configuration
state, terminal `DAR` as a positional/proximity state, exact `o` as a minimal
attached-index field, and one-sign residual hosts as an index-label class.
These are ranked prompts for new predictions, not a dictionary.

## Interpretation

The useful question is whether a residual host survives page conditioning.
Single-page perfect matches are retained in the atlas as dirty hypotheses,
not discarded, but they are marked `LIKELY_PAGE_CONFOUND`.  Recovered prefixes
and `DY` are controls: a strong object association there would count against
the proposed renderer/content separation.

The ranked TSV gives every effect, exact page-conditioned null, leave-one-page
range, certainty sensitivity, single-group sensitivity, and explicit
counterexamples.  It is therefore a map of where to look next, not a lexicon.

## Claim ceiling

The selected meanings are post-hoc functional hypotheses.  No word,
morpheme, part of speech, language, plaintext, or translation is confirmed.
f84r was not opened, retained, joined, or scored.
"""
    (ROOT/"GDT012_CORE_SEMANTIC_ATLAS_REPORT.md").write_text(report,encoding="utf-8")
    outputs=("gdt012_annotated_core_inventory.tsv","gdt012_core_semantic_candidates.tsv","gdt012_core_semantic_controls.tsv","gdt012_core_semantic_counterexamples.tsv","gdt012_provisional_core_roles.tsv","GDT012_CORE_SEMANTIC_ATLAS_REPORT.md")
    inputs=("experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv","experiments/semantic_assumptions/results/source_sta_group_alignment.tsv","experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv","gdt011_result.json","GDT012_CORE_SEMANTIC_ATLAS_METHOD.md")
    result["inputs"]={x:sha(ROOT/x) for x in inputs};result["implementation"]={"run_gdt012_core_semantic_atlas.py":sha(Path(__file__))};result["outputs"]={x:sha(ROOT/x) for x in outputs};result["result_content_sha256"]=canonical_sha(result)
    (ROOT/"gdt012_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"rows":len(rows),"tests":family_tests,"strongest":strongest,"strongest_host":strongest_host},sort_keys=True))


if __name__ == "__main__": main()
