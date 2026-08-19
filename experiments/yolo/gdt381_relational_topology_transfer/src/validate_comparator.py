#!/usr/bin/env python3
"""Validate GDT381 comparator topology outputs without importing the scorer."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt381_relational_topology_transfer"
ART = BASE / "artifacts"
G378 = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def content(obj: dict) -> str:
    clone = dict(obj); clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def read(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks=[]
    def check(name, ok):
        checks.append({"check":name,"pass":bool(ok)})
        if not ok: raise AssertionError(name)
    design=json.loads((ART/"gdt381_comparator_topology_freeze.json").read_text()); result=json.loads((ART/"gdt381_comparator_result.json").read_text()); signature=json.loads((ART/"gdt381_topology_signature_freeze.json").read_text())
    clusters=read(ART/"gdt381_clustering_summary.tsv"); classes=read(ART/"gdt381_latent_class_summary.tsv"); features=read(ART/"gdt381_topology_feature_manifest.tsv"); folds=read(ART/"gdt381_comparator_fold_scores.tsv"); summary=read(ART/"gdt381_comparator_family_summary.tsv"); capacity=read(ART/"gdt381_null_capacity.tsv"); null=read(ART/"gdt381_comparator_null.tsv.gz"); obs=read(G378/"gdt378_comparator_observation_layer.tsv.gz")
    check("result_content_hash",result["content_hash"]==content(result));check("signature_content_hash",signature["content_hash"]==content(signature));check("five_summary",len(summary)==5);check("five_capacity",len(capacity)==5)
    check("feature_identity_free",all(r["class_label_invariant"]=="1" and r["exact_identity_value_used"]=="0" for r in features));check("null_worlds",len(null)==design["null"]["worlds"]==2048)
    obs_domains=Counter(r["domain"] for r in obs); obs_types=Counter()
    for domain in obs_domains: obs_types[domain]=len({r["opaque_form_id"] for r in obs if r["domain"]==domain})
    for row in clusters:
        inertias={int(k):float(v) for k,v in json.loads(row["candidate_inertias_json"]).items()}; i1=float(row["k1_inertia"]); maxk=max(inertias); denominator=max(i1-inertias[maxk],1e-9); expected=maxk
        for k in sorted(inertias):
            if (i1-inertias[k])/denominator>=.80: expected=k;break
        check("k_rule_"+row["domain"],expected==int(row["selected_k"]))
        drows=[r for r in classes if r["domain"]==row["domain"]]
        check("class_count_"+row["domain"],len(drows)==expected)
        check("token_total_"+row["domain"],sum(int(r["token_count"]) for r in drows)==obs_domains[row["domain"]])
        check("type_total_"+row["domain"],sum(int(r["type_count"]) for r in drows)==obs_types[row["domain"]])
        check("unaligned_"+row["domain"],row["cross_domain_alignment"]=="0" and all(r["cross_domain_alignment"]=="0" for r in drows))
    check("fold_counts",Counter(r["anonymous_topology"] for r in folds)==Counter({"CMP_TOPOLOGY_01":5,"CMP_TOPOLOGY_02":5,"CMP_TOPOLOGY_03":5,"CMP_TOPOLOGY_04":4,"CMP_TOPOLOGY_05":4}))
    maxima=[float(r["world_max"]) for r in null]; eligible=[]
    for row in summary:
        family=row["anonymous_topology"]; fr=[r for r in folds if r["anonymous_topology"]==family]; floor=sorted((float(r["auc_full"]) for r in fr),reverse=True)[2]
        check("floor_"+family,math.isclose(floor,float(row["transfer_auc_floor"]),abs_tol=5e-10));check("gain_n_"+family,sum(float(r["gain_full_vs_nuisance_bits"])>0 for r in fr)==int(row["positive_gain_vs_nuisance_domains"]));check("gain_t_"+family,sum(float(r["gain_full_vs_trivial_bits"])>0 for r in fr)==int(row["positive_gain_vs_trivial_domains"]));check("gain_r_"+family,sum(float(r["gain_reduced_vs_nuisance_bits"])>0 for r in fr)==int(row["positive_reduced_gain_domains"]))
        expected=(1+sum(v>=floor for v in maxima))/(1+len(maxima));check("maxp_"+family,math.isclose(expected,float(row["max_family_p"]),abs_tol=5e-10))
        passes=floor>=.62 and int(row["positive_gain_vs_nuisance_domains"])>=3 and int(row["positive_gain_vs_trivial_domains"])>=3 and float(row["pceec2_auc"])>=.60 and float(row["pceec2_gain_vs_nuisance_bits"])>0 and float(row["pceec2_gain_vs_trivial_bits"])>0 and bool(row["procedural_domains_passing"]) and float(row["max_family_p"])<=.05 and int(row["positive_reduced_gain_domains"])>=3
        check("gate_"+family,passes==(row["voynich_mapping_eligible"]=="1"))
        if passes: eligible.append(family)
    check("eligible_exact",eligible==["CMP_TOPOLOGY_04"]==signature["eligible_anonymous_topologies"]==result["eligible_anonymous_topologies"])
    check("all_mobile",all(r["status"]=="MOBILE" and int(r["mobile_strata"])>0 for r in capacity));check("target_unread",not result["voynich_target_scored"] and result["voynich_rows_read"]==0 and not signature["voynich_target_scored"]);check("f84_false",all(v is False for v in result["f84"].values()) and all(v is False for v in signature["f84"].values()))
    for section in ["inputs","outputs","implementation"]:
        for path,digest in result[section].items():check(section+"_"+path.replace("/","_"),sha(ROOT/path)==digest)
    out={"schema":"GDT381_COMPARATOR_VALIDATION_V1","status":"PASS","scope":"OUTPUT_HASHES_CLUSTER_COUNT_AND_K_RULE_METRIC_GATE_NULL_ACCOUNTING_NO_KMEANS_OR_MODEL_REFIT","checks_passed":len(checks),"checks_total":len(checks),"checks":checks,"result_hash":sha(ART/"gdt381_comparator_result.json"),"f84":{"opened":False,"parsed":False,"retained":False,"scored":False}};out["content_hash"]=content(out);(ART/"gdt381_comparator_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")


if __name__=="__main__":main()
