#!/usr/bin/env python3
"""Production-free reconstruction of the frozen CCT001 target."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

# This is the independently validated clean implementation, not the target
# runner or production scoring core.
from validate_cho_che_canonical_transfer_synthetic_preflight import compare, evaluate

B=Path(__file__).resolve().parent; R=B/"results"; FREEZE=B/"CCT001_TARGET_FREEZE.json"; PANEL=R/"cho_che_canonical_transfer_masked_panel.tsv"; SOURCE=R/"source_separator_transcription.tsv"; TARGET=R/"cho_che_canonical_transfer_target.json"; TARGET_REPORT=R/"cho_che_canonical_transfer_target.md"; OUT=R/"cho_che_canonical_transfer_target_validation.json"; REPORT=R/"cho_che_canonical_transfer_target_validation.md"; SITE=re.compile(r"(ch|sh)([oe])")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def derive():
 rows=list(csv.DictReader(PANEL.open(),delimiter="\t")); src={}
 for x in csv.DictReader(SOURCE.open(),delimiter="\t"):
  if x["source_group_id"] in src: raise AssertionError("duplicate source")
  src[x["source_group_id"]]=x
 out=[]
 for x in rows:
  y=src[x["source_group_id"]]
  if any(y[k]!=x[k] for k in ("edition","locus","page")) or y["clean_ascii_fragment_count"]!="1": raise AssertionError("join")
  s=y["clean_ascii_fragments"]; q=list(SITE.finditer(s))
  if len(q)!=1 or q[0].group(1)!=x["site_prefix"] or len(s)!=int(x["ascii_length"]): raise AssertionError("site")
  i=q[0].end()-1; c=s[:i]+"X"+s[i+1:]
  out.append({"event_id":x["source_group_id"],"edition":x["edition"],"leaf":x["physical_folio"],"side":x["side"],"state":int(x["page_state"]),"scope":x["grammar_scope"],"prefix":x["site_prefix"],"raw_type":s,"canonical_type":c,"realization":s[i],"length":len(s),"site_index":i})
 if len(out)!=2223 or len({x["event_id"] for x in out})!=2223: raise AssertionError("rows")
 return out
def install(j,m):
 if OUT.exists() or REPORT.exists(): raise FileExistsError
 with tempfile.TemporaryDirectory(prefix="cct001tv_",dir=R) as d:
  a,b=Path(d)/"j",Path(d)/"m";a.write_bytes(j);b.write_bytes(m);os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 freeze=json.loads(FREEZE.read_text()); target=json.loads(TARGET.read_text()); checks=0
 if freeze["status"]!="FROZEN_CCT001_TARGET_AND_VALIDATION_ABSENT":raise AssertionError("freeze")
 for name,h in freeze["files"].items():
  p=next((q for q in (B/name,R/name) if q.exists()),None)
  if p is None or sha(p)!=h:raise AssertionError("hash "+name)
  checks+=1
 if target["freeze_sha256"]!=sha(FREEZE) or target["target_rows"]!=2223 or target["individual_types_emitted"] or target["individual_templates_emitted"] or target["english_glosses"]:raise AssertionError("target binding")
 checks+=6; events=derive(); score=evaluate(events); checks+=compare(score,target["score"],"score")
 core=("capacity","primary_state_excess","matched_merge_advantage","state_orbit_p","merger_null_p","reading_state_excess","leaf_support","loo_gain","concentration"); g=score.get("gates",{})
 if score.get("status")=="STOP_INSUFFICIENT_COLLISION_CAPACITY":decision="STOP_INSUFFICIENT_CANONICAL_COLLISION_CAPACITY"
 elif score["passes"]:decision="CONFIRM_USEFUL_GENERAL_CANONICAL_TRANSFER"
 elif all(g.get(k,False) for k in core) and not all(g.get(k,False) for k in ("prose_state_excess","prose_support","diagnostic_state_excess","diagnostic_support","prefix_gain")):decision="NONCONFIRM_GENERAL_CANONICAL_TRANSFER_DOMAIN_OR_PREFIX_LIMITED"
 else:decision="NONCONFIRM_CANONICAL_TRANSFER"
 if decision!=target["decision"]:raise AssertionError("decision")
 if decision=="CONFIRM_USEFUL_GENERAL_CANONICAL_TRANSFER":summary="All registered capacity, state-excess, complexity-matched merger, reading, folio, domain, prefix, deletion, and concentration gates pass."
 elif decision=="NONCONFIRM_GENERAL_CANONICAL_TRANSFER_DOMAIN_OR_PREFIX_LIMITED":summary="Core transfer gates pass, but the preregistered domain or prefix distribution gates fail; the general collapse is not confirmed."
 elif decision=="STOP_INSUFFICIENT_CANONICAL_COLLISION_CAPACITY":summary="The frozen collision-pair capacity gate fails, so no target score is interpreted."
 else:summary="The frozen canonical-transfer representation fails one or more core registered gates."
 expected_report=f"# CCT001 `cho/che` canonical-transfer target\n\nStatus: **PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION**  \nDecision: **{decision}**\n\n{summary} The run joined exactly {len(events):,} frozen target rows and emitted no individual type or template. Independent reconstruction is mandatory.\n"
 if TARGET_REPORT.read_text()!=expected_report:raise AssertionError("report")
 checks+=3; result={"experiment":"CCT001_CHO_CHE_CANONICAL_TRANSFER_TARGET_VALIDATION","status":"PASS_PRODUCTION_FREE_TARGET_RECONSTRUCTION","checks_passed":checks,"target_sha256":sha(TARGET),"target_report_sha256":sha(TARGET_REPORT),"freeze_sha256":sha(FREEZE),"target_rows":len(events),"decision":decision,"score":score,"individual_types_emitted":0,"individual_templates_emitted":0,"english_glosses":0,"claim_ceiling":"At most validated useful formal canonical transfer; no word sound phonology language cipher plaintext meaning or translation."}; report=f"# CCT001 target validation\n\n**PASS**: production-free code rejoined all **{len(events):,}** rows and reconstructed the complete score, gates, decision, and report in **{checks:,}** checks. Final decision: **{decision}**. No individual type or template is emitted.\n";install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode());print(json.dumps({"status":result["status"],"checks":checks,"decision":decision},sort_keys=True))
if __name__=="__main__":main()
