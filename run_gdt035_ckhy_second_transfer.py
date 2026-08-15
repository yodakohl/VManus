#!/usr/bin/env python3
"""Run the corrected frozen GDT035 exact-form query."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;TARGET="f101v";ALLOWED={"ckhy","chckhy","checkhy","shckhy"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def target_groups():
 path=ROOT/"experiments/semantic_assumptions/results/source_sta_group_alignment.tsv";groups=defaultdict(list)
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();cols=header.rstrip("\n").split("\t");li=cols.index("locus")
  for line in h:
   raw=line.rstrip("\n").split("\t")
   if not raw[li].startswith(TARGET+"."):continue
   r=next(csv.DictReader([header,line],delimiter="\t"));groups[(r["locus"],r["source_group_index"])].append(r)
 return groups
def main():
 v1=json.loads((ROOT/"gdt035_ckhy_second_transfer_prediction.json").read_text());v2=json.loads((ROOT/"gdt035_ckhy_second_transfer_prediction_v2.json").read_text());assert v1["target"]["page"]==TARGET and v2["status"]=="FROZEN_AFTER_CAPACITY_CORRECTION_BEFORE_SOURCE_GROUP_QUERY"
 groups=target_groups();assert len(groups)==233;hits=[]
 for key,rows in sorted(groups.items()):
  forms={r["nearest_basic_eva_primary"]for r in rows};editions={r["edition"]for r in rows}
  if editions=={"ZL3b","IT2a","RF1b"}and len(forms)==1 and next(iter(forms))in ALLOWED:hits.append((key,next(iter(forms)),rows))
 assert not hits;status="FAIL_SECOND_SEMANTIC_GLOSS_REJECTED"
 summary=[{"page":TARGET,"physical_source_groups":len(groups),"allowed_surface_forms":"|".join(sorted(ALLOWED)),"exact_all_reading_ckhy_groups":0,"v1_query_status":"UNSCORABLE_TARGET_OUTSIDE_INVENTORY","v2_query_status":status,"alternative_host_or_meaning_search":"NOT_PERFORMED","formal_ckhy_core_status":"UNCHANGED","claim_state":"SEMANTIC_GLOSS_FAILURE_ONLY"}]
 with (ROOT/"gdt035_ckhy_second_transfer_query.tsv").open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=list(summary[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(summary)
 report=f"""# GDT035 second CKHY semantic transfer

Status: **{status.replace('_',' ')}**

The target f101v and positive CKHY prediction were frozen from visible geometry in public commit `6fc23b0`. The v1 query then proved unscorable because GDT016 contains no f101v rows of any host. This was registered as a capacity defect rather than a miss. Public correction commit `b3dfab3` retained the same page, geometry, gloss, binary outcome, and four exact forms while freezing the complete source-native group table before its f101v content was opened.

The corrected reveal contains 233 physical f101v source groups. **Zero** have unanimous ZL3b/IT2a/RF1b rendering as `ckhy`, `chckhy`, `checkhy`, or `shckhy`. No fuzzy form, family neighbor, alternative page, nearby host, component reassignment, or replacement meaning was inspected or admitted.

Under the frozen decision rule, the second prospective prediction fails and the exact semantic gloss **CKHY = parallel/fused leaf-or-stalk configuration descriptor is rejected**. GDT034's first-page hit remains a historical hit, but it does not transfer to the second comparable botanical geometry and is compatible with CKHY's substantial background occurrence.

This result does not weaken CKHY as a recurrent formal residual host and does not modify the parser. It rejects only the tested visual meaning. No word, morpheme, POS, sound, language, plaintext, translation, authorship, or origin is established. f84r was not opened, retained, queried, joined, or scored.
""";(ROOT/"GDT035_CKHY_SECOND_TRANSFER_REPORT.md").write_text(report)
 outputs=("gdt035_ckhy_second_transfer_query.tsv","GDT035_CKHY_SECOND_TRANSFER_REPORT.md");inputs=("GDT035_CKHY_SECOND_TRANSFER_METHOD.md","GDT035_CKHY_SECOND_TRANSFER_CAPACITY_CORRECTION.md","gdt035_ckhy_second_transfer_prediction.json","gdt035_ckhy_second_transfer_prediction_v2.json","gdt033_result.json","gdt034_result.json")
 result={"schema":"GDT035_CKHY_SECOND_TRANSFER_RESULT_V1","status":status,"freeze":{"visual_prediction_commit":"6fc23b0","capacity_correction_commit":"b3dfab3","v1_prediction_sha256":sha(ROOT/"gdt035_ckhy_second_transfer_prediction.json"),"v2_prediction_sha256":sha(ROOT/"gdt035_ckhy_second_transfer_prediction_v2.json")},"capacity_correction":{"v1_gdt016_target_rows":0,"v1_status":"UNSCORABLE_TARGET_OUTSIDE_INVENTORY","source_group_content_opened_before_v2_freeze":False,"same_target_gloss_forms_and_binary_rule":True},"target":{"page":TARGET,"physical_source_groups":len(groups),"exact_all_reading_allowed_form_groups":0,"allowed_surface_forms":sorted(ALLOWED)},"semantic_gloss":{"gloss":"PARALLEL_OR_FUSED_LEAF_OR_STALK_CONFIGURATION_DESCRIPTOR","outcome":"REJECTED_ON_SECOND_PROSPECTIVE_TRANSFER","alternative_meaning_search_performed":False,"parser_modified":False,"formal_core_status_modified":False},"interpretation":"The exact visual gloss failed its second prospective transfer; GDT034's one-page hit does not establish this meaning.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"claim_ceiling":"Rejection of one CKHY visual gloss only; CKHY remains a formal host and no alternative meaning, word, morpheme, POS, sound, language, plaintext, translation, authorship, or origin follows.","inputs":{n:sha(ROOT/n)for n in inputs},"guarded_target_alignment":{"retained_page":TARGET,"retained_physical_groups":len(groups),"retained_rows":sum(len(x)for x in groups.values()),"canonical_sha256":csha([r for k in sorted(groups)for r in sorted(groups[k],key=lambda x:x["edition"])]),"f84r_rows_retained":0},"implementation":{"run_gdt035_ckhy_second_transfer.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}}
 result["result_content_sha256"]=csha(result);(ROOT/"gdt035_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"physical_groups":len(groups),"hits":0},sort_keys=True))
if __name__=="__main__":main()
