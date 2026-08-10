#!/usr/bin/env python3
"""One-shot CCT002 target under the marginal-preserving merger null."""
from __future__ import annotations
import csv,hashlib,json,os,re,tempfile
from pathlib import Path
from cct002_core import compact_score,score_world
B=Path(__file__).resolve().parent;R=B/"results";FREEZE=B/"CCT002_TARGET_FREEZE.json";PANEL=R/"cho_che_canonical_transfer_masked_panel.tsv";SOURCE=R/"source_separator_transcription.tsv";OUT=R/"cct002_target.json";REPORT=R/"cct002_target.md";VOUT=R/"cct002_target_validation.json";VREPORT=R/"cct002_target_validation.md";SITE=re.compile(r"(ch|sh)([oe])")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def absence():return {p.name:not p.exists() for p in (OUT,REPORT,VOUT,VREPORT)}
def derive():
 rows=list(csv.DictReader(PANEL.open(),delimiter="\t"));src={}
 for x in csv.DictReader(SOURCE.open(),delimiter="\t"):
  if x["source_group_id"] in src:raise RuntimeError("duplicate source")
  src[x["source_group_id"]]=x
 events=[]
 for x in rows:
  y=src[x["source_group_id"]]
  if any(y[k]!=x[k] for k in ("edition","locus","page")) or y["clean_ascii_fragment_count"]!="1":raise RuntimeError("join")
  s=y["clean_ascii_fragments"];q=list(SITE.finditer(s))
  if len(q)!=1 or q[0].group(1)!=x["site_prefix"] or len(s)!=int(x["ascii_length"]):raise RuntimeError("site")
  i=q[0].end()-1;events.append({"event_id":x["source_group_id"],"edition":x["edition"],"leaf":x["physical_folio"],"side":x["side"],"state":int(x["page_state"]),"scope":x["grammar_scope"],"prefix":x["site_prefix"],"raw_type":s,"canonical_type":s[:i]+"X"+s[i+1:],"realization":s[i],"length":len(s),"site_index":i})
 if len(events)!=2223 or len({x["event_id"] for x in events})!=2223:raise RuntimeError("rows")
 return events
def install(j,m):
 if not all(absence().values()):raise FileExistsError
 with tempfile.TemporaryDirectory(prefix="cct002t_",dir=R) as d:
  a,b=Path(d)/"j",Path(d)/"m";a.write_bytes(j);b.write_bytes(m)
  if not all(absence().values()):raise FileExistsError
  os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 freeze=json.loads(FREEZE.read_text());paths={p.name:p for p in (B/"CCT002_TARGET_METHOD.md",B/"CCT002_SYNTHETIC_PREFLIGHT_SPEC.md",B/"cct002_core.py",B/"run_cct002_target.py",B/"validate_cct002_target.py",PANEL,SOURCE,R/"cct002_marginal_merger_capacity_validation.json",R/"cct002_synthetic_preflight.json",R/"cct002_synthetic_preflight_validation.json")}
 if freeze.get("status")!="FROZEN_CCT002_TARGET_AND_VALIDATION_ABSENT" or set(paths)!=set(freeze.get("files",{})) or set(freeze["files"])!=set(freeze.get("required_files",[])):raise SystemExit("freeze")
 for n,p in paths.items():
  if sha(p)!=freeze["files"][n]:raise SystemExit("hash "+n)
 if absence()!=freeze["output_absence"] or not all(absence().values()):raise SystemExit("absence")
 events=derive();score=compact_score(score_world(events));g=score["gates"];core=("capacity","primary_state_excess","matched_merge_advantage","state_orbit_p","merger_null_p","reading_state_excess","leaf_support","loo_gain","concentration")
 if score["passes"]:decision="CONFIRM_USEFUL_GENERAL_CCT002_CANONICAL_TRANSFER"
 elif all(g[k] for k in core) and not all(g[k] for k in ("prose_state_excess","prose_support","diagnostic_state_excess","diagnostic_support","prefix_gain")):decision="NONCONFIRM_GENERAL_CCT002_DOMAIN_OR_PREFIX_LIMITED"
 else:decision="NONCONFIRM_CCT002_CANONICAL_TRANSFER"
 result={"experiment":"CCT002_CANONICAL_TRANSFER_TARGET","status":"PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION","decision":decision,"freeze_sha256":sha(FREEZE),"inputs":{n:sha(p) for n,p in paths.items()},"target_rows":len(events),"score":score,"individual_types_emitted":0,"individual_templates_emitted":0,"english_glosses":0,"claim_ceiling":"At most useful formal canonical transfer under a marginal-preserving null; no word sound language cipher meaning plaintext or translation."}
 if decision.startswith("CONFIRM_"):summary="All frozen state, merger, reading, folio, domain, prefix, deletion, and concentration gates pass."
 elif "DOMAIN_OR_PREFIX" in decision:summary="Core transfer gates pass but a frozen domain or prefix distribution gate fails, so the general claim is not confirmed."
 else:summary="One or more frozen core canonical-transfer gates fail."
 report=f"# CCT002 canonical-transfer target\n\nStatus: **PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION**\n\nDecision: **{decision}**\n\n{summary} Exactly {len(events):,} frozen rows were joined; no individual type or template is emitted. Independent reconstruction is mandatory.\n";install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode());print(json.dumps({"status":result["status"],"decision":decision,"target_rows":len(events),"capacity":score["capacity"],"primary_gain":score["primary_gain"],"primary_state_excess":score["primary_state_excess"],"state_orbit_p":score["state_orbit_p"],"merge_null_p":score["merge_null_p"],"gates":g},sort_keys=True))
if __name__=="__main__":main()
