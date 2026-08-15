#!/usr/bin/env python3
"""Score the frozen one-page GDT034 CKHY semantic prediction."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PRED=ROOT/"gdt034_ckhy_semantic_hypothesis_prediction.json"
TARGET="f14r";HOST="ckhy";ALLOWED={"ckhy","chckhy","checkhy","shckhy"}
def read(name):
 with (ROOT/name).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def write_tsv(name,rows):
 with (ROOT/name).open("w",encoding="utf-8",newline="")as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def guarded_alignment(locus,index):
 out=[];path=ROOT/"experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();cols=header.rstrip("\n").split("\t");li=cols.index("locus");gi=cols.index("source_group_index")
  for line in h:
   raw=line.rstrip("\n").split("\t")
   if raw[li]!=locus or int(raw[gi])!=index:continue
   out.append(next(csv.DictReader([header,line],delimiter="\t")))
 return out
def main():
 prediction=json.loads(PRED.read_text());assert prediction["status"]=="FROZEN_BEFORE_CKHY_QUERY"and prediction["target"]["page"]==TARGET
 assert sha(ROOT/"gdt033_result.json")==prediction["parent"]["result_sha256"]
 inventory=read("gdt016_group_state_inventory.tsv");assert len(inventory)==15592 and not any(r["page"]=="f84r"for r in inventory)
 herbal_a=[r for r in inventory if r["section"]=="H"and r["currier"]=="A"];a_pages=sorted({r["page"]for r in herbal_a});assert len(a_pages)==95
 host_rows=[r for r in herbal_a if r["residual_host"]==HOST];host_pages=sorted({r["page"]for r in host_rows});target=[r for r in host_rows if r["page"]==TARGET]
 assert len(target)==1 and target[0]["token"]in ALLOWED
 r=target[0];align=guarded_alignment(r["locus"],int(r["group_index"]));assert {x["edition"]for x in align}=={"ZL3b","IT2a","RF1b"}
 occurrence=[]
 for x in sorted(align,key=lambda z:z["edition"]):
  occurrence.append({"page":r["page"],"physical_folio":r["physical_folio"],"locus":r["locus"],"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"stripped_prefix":r["stripped_prefix"],"residual_host":r["residual_host"],"dy_closure":r["dy_closure"],"record_state":r["record_state"],"edition":x["edition"],"sta_group_raw":x["sta_group_raw"],"primary_sta_families":x["primary_sta_families"],"alternative_site_count":x["alternative_site_count"],"claim_state":"FROZEN_PAGE_LEVEL_HIT_NOT_COMPONENT_OWNERSHIP"})
 write_tsv("gdt034_ckhy_target_occurrences.tsv",occurrence)
 status="PASS_SEMANTIC_GLOSS_PROVISIONAL_TRANSFER"
 report=f"""# GDT034 CKHY semantic-hypothesis transfer

Status: **{status.replace('_',' ')}**

The public pre-reveal prediction commit `6b75f1c` selected f14r from visible geometry and predicted at least one exact CKHY residual host. The frozen query returned exactly one: **`chckhy`**, f14r.7 group 3/3, prefix `ch`, residual host `ckhy`, record state `CARRIER_STATE`, with no DY closure. ZL3b, IT2a, and RF1b all give the same KUA family and `chckhy` rendering with zero alternative sites. They are alternate readings, not three hits.

This is a real prospective page-level hit for the provisional `parallel/fused leaf-or-stalk configuration descriptor` gloss. It is not strong confirmation. CKHY occurs 17 times on 17 of 95 Herbal-A pages; excluding f14r, the reference prevalence is 16/94 ({16/94:.3f}). A single successful prediction therefore has substantial background probability. No inscription is authorially connected to a particular leaf or stalk, so the hit cannot localize CKHY's referent within the drawing.

The test did not search another target, fuzzy CKHY match, neighboring host, alternate visual feature, or alternative CKHY meaning. A miss would have rejected only the gloss; the observed hit leaves CKHY's independent formal-core status unchanged. The correct next scientific use is to preserve this exact gloss and seek a second prospectively selected comparable page or explicit owned label—not to broaden the meaning.

Conclusion: **one-page provisional semantic transfer succeeded, with high residual chance and no component ownership**. No word, morpheme, POS, sound, language, plaintext, translation, authorship, or origin is established. f84r was not opened, retained, queried, joined, or scored.
"""
 (ROOT/"GDT034_CKHY_SEMANTIC_HYPOTHESIS_REPORT.md").write_text(report)
 outputs=("gdt034_ckhy_target_occurrences.tsv","GDT034_CKHY_SEMANTIC_HYPOTHESIS_REPORT.md")
 result={"schema":"GDT034_CKHY_SEMANTIC_HYPOTHESIS_RESULT_V1","status":status,"freeze":{"commit":"6b75f1c","prediction_sha256":sha(PRED),"method_sha256":sha(ROOT/"GDT034_CKHY_SEMANTIC_HYPOTHESIS_METHOD.md"),"target_ckhy_query_after_freeze":True},"target":{"page":TARGET,"exact_host_occurrences":len(target),"tokens":[r["token"]for r in target],"loci":[r["locus"]for r in target],"group_positions":[f"{r['group_index']}/{r['group_count']}"for r in target],"record_states":[r["record_state"]for r in target],"dy_closures":[int(r["dy_closure"])for r in target],"all_three_readings_exact_family_agreement":len({x["primary_sta_families"]for x in align})==1,"all_three_readings_exact_rendering_agreement":len({x["nearest_basic_eva_primary"]for x in align})==1,"alternative_sites":sum(int(x["alternative_site_count"])for x in align)},"reference":{"herbal_a_pages":len(a_pages),"ckhy_occurrences":len(host_rows),"ckhy_pages":len(host_pages),"inclusive_page_prevalence":len(host_pages)/len(a_pages),"leave_target_page_prevalence":16/94,"single_hit_background_probability_context":"HIGH_ENOUGH_TO_PRECLUDE_CONFIRMATION"},"semantic_gloss":{"gloss":"PARALLEL_OR_FUSED_LEAF_OR_STALK_CONFIGURATION_DESCRIPTOR","outcome":"PROVISIONAL_ONE_PAGE_TRANSFER_HIT_NOT_CONFIRMED_MEANING","alternative_meaning_search_performed":False,"parser_modified":False,"formal_core_status_modified":False},"f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"claim_ceiling":"One prospective page-level semantic-gloss hit with about 17 percent Herbal-A background prevalence and no component ownership; no word, morpheme, POS, sound, language, plaintext, translation, authorship, or origin.","inputs":{"gdt016_group_state_inventory.tsv":sha(ROOT/"gdt016_group_state_inventory.tsv"),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt033_result.json":sha(ROOT/"gdt033_result.json"),"gdt034_ckhy_semantic_hypothesis_prediction.json":sha(PRED),"GDT034_CKHY_SEMANTIC_HYPOTHESIS_METHOD.md":sha(ROOT/"GDT034_CKHY_SEMANTIC_HYPOTHESIS_METHOD.md")},"guarded_source_alignment":{"retained_rows":len(align),"editions":sorted(x["edition"]for x in align),"canonical_sha256":csha(align),"f84r_rows_retained":0},"implementation":{"run_gdt034_ckhy_semantic_hypothesis.py":sha(Path(__file__))},"outputs":{name:sha(ROOT/name)for name in outputs}}
 result["result_content_sha256"]=csha(result);(ROOT/"gdt034_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"target_rows":len(target),"token":target[0]["token"],"reference_pages":f"{len(host_pages)}/{len(a_pages)}"},sort_keys=True))
if __name__=="__main__":main()
