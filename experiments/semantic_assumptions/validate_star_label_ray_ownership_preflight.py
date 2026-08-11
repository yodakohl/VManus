#!/usr/bin/env python3
"""Independent metadata reconstruction of the star-label ownership stop."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "results/existing_human_exact_locus_annotations.tsv"
RESULT = BASE / "results/star_label_ray_ownership_preflight.json"
REPORT = BASE / "results/star_label_ray_ownership_preflight_report.md"
OUT = BASE / "results/star_label_ray_ownership_preflight_validation.json"
OUT_MD = BASE / "results/star_label_ray_ownership_preflight_validation.md"
PATTERN = re.compile(r"\b(?:five|six|seven|eight|nine|\d+) points?\b", re.I)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    checks=[]
    def check(name: str, value: bool) -> None:
        checks.append({"name":name,"pass":bool(value)})
        if not value: raise SystemExit(name)
    check("source_hash", sha(SOURCE)=="79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61")
    with SOURCE.open(encoding="utf-8",newline="") as h:
        rows=[r for r in csv.DictReader(h,delimiter="\t") if PATTERN.search(r["local_comment"]) and "LABEL" in r["object_tags"].split(";")]
    counts=Counter(r["page"] for r in rows)
    check("candidate_census",len(rows)==63 and counts==Counter({"f68r1":29,"f68r2":24,"f70v1":10}))
    strong=Counter()
    for r in rows:
        if r["certainty"]=="UNHEDGED" and r["relation_scope"]=="EXACT_LOCAL_COMMENT" and "REL_EXPLICIT_ATTACHMENT" in r["local_relation_tags"].split(";"):
            strong["f68" if r["page"].startswith("f68") else "f70"]+=1
    check("strong_counts",strong==Counter({"f68":47}))
    f70=[r for r in rows if r["page"]=="f70v1"]
    check("f70_metadata_stop",len(f70)==10 and all(r["certainty"]=="HEDGED" and r["relation_scope"]=="OBJECT_CONTEXT_ONLY" for r in f70))
    result=json.loads(RESULT.read_text(encoding="utf-8"))
    check("stop_status",result["status"]=="STOP_UNSCORED_NO_SECOND_FOLIO_SINGULAR_OWNERSHIP")
    check("ownership_gate_failed",result["gates"]["at_least_eight_strong_singular_attachments_per_folio"] is False)
    check("native_connector_gate_failed",result["gates"]["native_f70_has_no_author_visible_singular_connector"] is False)
    check("zero_target_access",result["counts"]["label_surfaces_opened"]==0 and result["counts"]["formal_features_constructed"]==0 and result["counts"]["associations_scored"]==0)
    check("report_status",result["status"] in REPORT.read_text(encoding="utf-8"))
    out={"experiment":"DIRECT_STAR_LABEL_RAY_OWNERSHIP_PREFLIGHT_VALIDATION","status":"PASS_INDEPENDENT_METADATA_RECONSTRUCTION","validated_status":result["status"],"check_count":len(checks),"checks":checks,"source_result_sha256":sha(RESULT),"source_report_sha256":sha(REPORT),"claim_ceiling":result["claim_ceiling"]}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    OUT_MD.write_text("# Direct star-label ray-count ownership validation\n\nStatus: **PASS_INDEPENDENT_METADATA_RECONSTRUCTION** (9 checks).\n\nThe 63-row census, one-folio strong-ownership support, f70 hedge state, and zero-target-access stop reconstruct exactly. The native visual observation remains a source-bound machine-authored judgment, not a human annotation.\n\nClaim ceiling: "+result["claim_ceiling"]+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
