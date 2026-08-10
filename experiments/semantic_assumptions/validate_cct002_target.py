#!/usr/bin/env python3
"""Production-free reconstruction of the CCT002 manuscript target."""
from __future__ import annotations
import csv,hashlib,json,os,re,tempfile
from pathlib import Path
from validate_cct002_synthetic_preflight import clean,evaluate
B=Path(__file__).resolve().parent;R=B/"results";FREEZE=B/"CCT002_TARGET_FREEZE.json";PANEL=R/"cho_che_canonical_transfer_masked_panel.tsv";SOURCE=R/"source_separator_transcription.tsv";TARGET=R/"cct002_target.json";TARGET_REPORT=R/"cct002_target.md";OUT=R/"cct002_target_validation.json";REPORT=R/"cct002_target_validation.md";SITE=re.compile(r"(ch|sh)([oe])")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def derive():
 rows=list(csv.DictReader(PANEL.open(),delimiter="\t"));src={x["source_group_id"]:x for x in csv.DictReader(SOURCE.open(),delimiter="\t")};out=[]
 for x in rows:
  y=src[x["source_group_id"]]
  if any(y[k]!=x[k] for k in ("edition","locus","page")) or y["clean_ascii_fragment_count"]!="1":raise AssertionError("join")
  s=y["clean_ascii_fragments"];q=list(SITE.finditer(s));assert len(q)==1 and q[0].group(1)==x["site_prefix"] and len(s)==int(x["ascii_length"]);i=q[0].end()-1;out.append({"event_id":x["source_group_id"],"edition":x["edition"],"leaf":x["physical_folio"],"side":x["side"],"state":int(x["page_state"]),"scope":x["grammar_scope"],"prefix":x["site_prefix"],"raw_type":s,"canonical_type":s[:i]+"X"+s[i+1:],"realization":s[i],"length":len(s),"site_index":i})
 assert len(out)==2223 and len({x["event_id"] for x in out})==2223;return out
def install(j,m):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix="cct002tv_",dir=R) as d:
  a,b=Path(d)/"j",Path(d)/"m";a.write_bytes(j);b.write_bytes(m);os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 freeze=json.loads(FREEZE.read_text());target=json.loads(TARGET.read_text());checks=0
 if freeze["status"]!="FROZEN_CCT002_TARGET_AND_VALIDATION_ABSENT":raise AssertionError("freeze")
 for n,h in freeze["files"].items():
  p=next((q for q in (B/n,R/n) if q.exists()),None)
  if p is None or sha(p)!=h:raise AssertionError("hash "+n)
  checks+=1
 if target["freeze_sha256"]!=sha(FREEZE) or target["target_rows"]!=2223 or target["individual_types_emitted"] or target["individual_templates_emitted"] or target["english_glosses"]:raise AssertionError("binding")
 checks+=6;events=derive();score=evaluate(events);checks+=clean.compare(score,target["score"],"score");g=score["gates"];core=("capacity","primary_state_excess","matched_merge_advantage","state_orbit_p","merger_null_p","reading_state_excess","leaf_support","loo_gain","concentration")
 if score["passes"]:decision="CONFIRM_USEFUL_GENERAL_CCT002_CANONICAL_TRANSFER"
 elif all(g[k] for k in core) and not all(g[k] for k in ("prose_state_excess","prose_support","diagnostic_state_excess","diagnostic_support","prefix_gain")):decision="NONCONFIRM_GENERAL_CCT002_DOMAIN_OR_PREFIX_LIMITED"
 else:decision="NONCONFIRM_CCT002_CANONICAL_TRANSFER"
 if decision!=target["decision"]:raise AssertionError("decision")
 if decision.startswith("CONFIRM_"):summary="All frozen state, merger, reading, folio, domain, prefix, deletion, and concentration gates pass."
 elif "DOMAIN_OR_PREFIX" in decision:summary="Core transfer gates pass but a frozen domain or prefix distribution gate fails, so the general claim is not confirmed."
 else:summary="One or more frozen core canonical-transfer gates fail."
 expected=f"# CCT002 canonical-transfer target\n\nStatus: **PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION**\n\nDecision: **{decision}**\n\n{summary} Exactly {len(events):,} frozen rows were joined; no individual type or template is emitted. Independent reconstruction is mandatory.\n"
 if TARGET_REPORT.read_text()!=expected:raise AssertionError("report")
 checks+=3;result={"experiment":"CCT002_TARGET_VALIDATION","status":"PASS_PRODUCTION_FREE_CCT002_TARGET_RECONSTRUCTION","checks_passed":checks,"target_sha256":sha(TARGET),"target_report_sha256":sha(TARGET_REPORT),"freeze_sha256":sha(FREEZE),"target_rows":len(events),"decision":decision,"score":score,"individual_types_emitted":0,"individual_templates_emitted":0,"english_glosses":0,"claim_ceiling":"At most validated formal canonical transfer; no word sound language cipher meaning plaintext or translation."};report=f"# CCT002 target validation\n\n**PASS**: production-free code rejoined all **{len(events):,}** rows and reconstructed every score, gate, decision, and report in **{checks:,}** checks. Final decision: **{decision}**.\n";install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode());print(json.dumps({"status":result["status"],"checks":checks,"decision":decision},sort_keys=True))
if __name__=="__main__":main()
