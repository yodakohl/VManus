#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
def root(p):
 for x in (p,*p.parents):
  if (x/"AGENTS.md").is_file() and (x/".git").exists():return x
 raise RuntimeError
ROOT=root(Path(__file__).resolve());BASE=ROOT/"experiments/yolo/gdt386_independent_relation_edge_capacity";ART=BASE/"artifacts"
P169=ROOT/"gdt169_external_referent_candidates.tsv";P351=ROOT/"experiments/yolo/gdt351_remaining_referent_label_capacity/artifacts/gdt351_capacity.tsv";P360=ROOT/"experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv";P337=ROOT/"experiments/yolo/gdt337_external_homologue_census/artifacts/gdt337_candidate_correspondences.tsv";Q20=ROOT/"q20ob001_source_panel.tsv";P385=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_result.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rr(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def folio(page):
 m=re.match(r"^(f\d+)",page);assert m,page;return m.group(1)
c=[]
def ck(n,x):c.append(n);assert x,n
r=json.loads((ART/"gdt386_result.json").read_text());q=dict(r);h=q.pop("content_hash");ck("content",h==hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest())
for p,h in r["inputs"].items():ck("input:"+p,sha(ROOT/p)==h)
for p,h in r["outputs"].items():ck("output:"+p,sha(ROOT/p)==h)
for p,h in r["implementation"].items():ck("implementation:"+p,sha(ROOT/p)==h)
fam=rr(ART/"gdt386_candidate_edge_families.tsv");viable=rr(ART/"gdt386_viable_endpoint_freeze.tsv");dedup=rr(ART/"gdt386_closed_route_dedup.tsv")
# Independently rebuild the score-blind source census without importing the producer.
a169=rr(P169);a351=rr(P351);a360=rr(P360);a337=rr(P337)
with Q20.open(encoding="utf-8",newline="") as f:
 rd=csv.DictReader(f,delimiter="\t");need=["unit_id","page","physical_folio","edition","open_locus","body_line_loci"];ck("q20_required_schema",all(x in rd.fieldnames for x in need));q20=[{k:x[k] for k in need} for x in rd]
relch={"HUMAN_REL_ATTACHMENT","HUMAN_REL_CONTACT","HUMAN_REL_ENCLOSURE","HUMAN_REL_ARRAY_GROUP"};local=[x for x in a360 if x["channel"] in relch];owned=[x for x in a169 if x["local_ownership_tier"]=="PUBLISHED_SINGULAR_OR_PROVISIONAL"]
qu={x["unit_id"] for x in q20};qf={x["physical_folio"] for x in q20}
ck("all_inputs_f84_free",all(not (x["source_page"].startswith("f84") or x["target_page"].startswith("f84")) for x in a169+a351) and all(not x["page"].startswith("f84") for x in a360+q20) and all("f84" not in x["voynich_target"].lower() for x in a337))
ck("q20_alternate_readings_not_samples",len(qu)==170 and len(qf)==8 and Counter(x["edition"] for x in q20)=={"ZL3b":170,"IT2a":170,"RF1b":170})
rebuilt={"cross_page_referent_pairs":len(a169),"singular_or_provisional_referent_targets":len(owned),"remaining_referent_upgrades":len(a351),"local_relation_cases":len(local),"local_relation_unique_loci":len({x["locus"] for x in local}),"q20_records":len(qu),"q20_physical_folios":len(qf),"external_homologue_candidates":len(a337),"external_homologue_viable":sum(x["viable"]=="YES" for x in a337)}
ck("source_counts_rebuilt",r["counts"]==rebuilt)
by={x["family_id"]:x for x in fam}
ck("family_ids",set(by)=={f"EDGE{i:02d}_{n}" for i,n in [(1,"EXPLICIT_EDITOR_PARENT"),(2,"CROSS_PAGE_REFERENT"),(3,"LOCAL_OBJECT_RELATION"),(4,"Q20_STAR_RECORD"),(5,"EXTERNAL_DIAGRAM_HOMOLOGUE"),(6,"REMAINING_REFERENT_UPGRADE"),(7,"INTERNAL_RESUME_REPEAT")]})
ck("referent_family_rebuilt",int(by["EDGE02_CROSS_PAGE_REFERENT"]["raw_observations"])==len(a169) and int(by["EDGE02_CROSS_PAGE_REFERENT"]["exact_target"])==len(owned) and int(by["EDGE02_CROSS_PAGE_REFERENT"]["physical_folios"])==len({x["source_physical_folio"] for x in a169}|{x["target_physical_folio"] for x in a169}))
ck("local_relation_family_rebuilt",int(by["EDGE03_LOCAL_OBJECT_RELATION"]["raw_observations"])==len(local) and int(by["EDGE03_LOCAL_OBJECT_RELATION"]["exact_pivot"])==len({x["locus"] for x in local}) and int(by["EDGE03_LOCAL_OBJECT_RELATION"]["physical_folios"])==len({x["physical_folio"] for x in local}))
ck("q20_family_rebuilt",int(by["EDGE04_Q20_STAR_RECORD"]["raw_observations"])==len(qu) and int(by["EDGE04_Q20_STAR_RECORD"]["physical_folios"])==len(qf))
ck("homologue_family_rebuilt",int(by["EDGE05_EXTERNAL_DIAGRAM_HOMOLOGUE"]["raw_observations"])==len(a337) and int(by["EDGE05_EXTERNAL_DIAGRAM_HOMOLOGUE"]["physical_folios"])==max(int(x["voynich_physical_folios"]) for x in a337) and sum(x["viable"]=="YES" for x in a337)==0)
ck("upgrade_family_rebuilt",int(by["EDGE06_REMAINING_REFERENT_UPGRADE"]["raw_observations"])==len(a351) and int(by["EDGE06_REMAINING_REFERENT_UPGRADE"]["physical_folios"])==len({folio(x["source_page"]) for x in a351}|{folio(x["target_page"]) for x in a351}) and all(x["singular_owned_locus"]=="NONE" for x in a351))
ck("gdt385_bound_status",json.loads(P385.read_text())["status"]=="COMPARATOR_PARENT_LINK_INSTRUMENT_FAILED_STOP_BEFORE_VOYNICH")
ck("seven_families",len(fam)==7);ck("no_family_pass",all(x["passes_all_gates"]=="0" for x in fam));ck("empty_freeze",not viable);ck("dedup",len(dedup)==5 and all(x["genuinely_new"]=="0" for x in dedup));ck("decision",r["status"]=="NO_INDEPENDENT_TARGET_RELATION_EDGE_AVAILABLE" and r["families_passing"]==0 and r["viable_endpoints"]==0);ck("no_score",r["voynich_formal_rows_read"]==0 and r["voynich_text_identities_read"]==0 and r["target_score_run"] is False);ck("f84",not any(r["f84"].values()))
out={"schema":"GDT386_VALIDATION_V1","status":"PASS","checks_passed":len(c),"checks_total":len(c),"checks":c,"result_hash":sha(ART/"gdt386_result.json")};(ART/"gdt386_validation.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(c)}/{len(c)}");raise SystemExit(0)
