#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path

def find_root(p):
 for x in (p,*p.parents):
  if (x/"AGENTS.md").is_file() and (x/".git").exists():return x
 raise RuntimeError("repository root not found")
ROOT=find_root(Path(__file__).resolve());BASE=ROOT/"experiments/yolo/gdt386_independent_relation_edge_capacity";ART=BASE/"artifacts"
P169=ROOT/"gdt169_external_referent_candidates.tsv";P351=ROOT/"experiments/yolo/gdt351_remaining_referent_label_capacity/artifacts/gdt351_capacity.tsv";P360=ROOT/"experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv";P337=ROOT/"experiments/yolo/gdt337_external_homologue_census/artifacts/gdt337_candidate_correspondences.tsv";Q20=ROOT/"q20ob001_source_panel.tsv";P385=ROOT/"experiments/yolo/gdt385_corema_parent_link_consequence/artifacts/gdt385_result.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rr,fields=None):
 fields=fields or list(rr[0])
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rr)
def content(d):q=dict(d);q.pop("content_hash",None);return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def folio(page):
 m=re.match(r"^(f\d+)",page);assert m,page;return m.group(1)

def main():
 a169=rows(P169);a351=rows(P351);a360=rows(P360);a337=rows(P337)
 # Q20 payload columns are deliberately not retained or parsed.
 with Q20.open(encoding="utf-8",newline="") as f:
  rd=csv.DictReader(f,delimiter="\t");need=["unit_id","page","physical_folio","edition","open_locus","body_line_loci"];assert all(x in rd.fieldnames for x in need);q20=[{k:r[k] for k in need} for r in rd]
 assert all(not (r["source_page"].startswith("f84") or r["target_page"].startswith("f84")) for r in a169)
 assert all(not (r["source_page"].startswith("f84") or r["target_page"].startswith("f84")) for r in a351)
 assert all(not r["page"].startswith("f84") for r in a360)
 assert all("f84" not in r["voynich_target"].lower() for r in a337)
 assert all(not r["page"].startswith("f84") for r in q20)
 q_units={r["unit_id"] for r in q20};q_folios={r["physical_folio"] for r in q20};assert len(q_units)==170 and len(q_folios)==8 and Counter(r["edition"] for r in q20)=={"ZL3b":170,"IT2a":170,"RF1b":170}
 relch={"HUMAN_REL_ATTACHMENT","HUMAN_REL_CONTACT","HUMAN_REL_ENCLOSURE","HUMAN_REL_ARRAY_GROUP"};local=[r for r in a360 if r["channel"] in relch];local_folios={r["physical_folio"] for r in local};local_loci={r["locus"] for r in local}
 owned=[r for r in a169 if r["local_ownership_tier"]=="PUBLISHED_SINGULAR_OR_PROVISIONAL"]
 candidates=[
  {"family_id":"EDGE01_EXPLICIT_EDITOR_PARENT","source":"complete cached relation corpus","capacity_basis":"COMPLETE_SOURCE_FAMILY","raw_observations":0,"physical_folios":0,"exact_pivot":0,"exact_target":0,"direction_fixed":0,"singular_ownership":0,"external_to_grammar":1,"prior_route":"GDT384;GDT385","status":"NO_SOURCE_ROWS","reason":"No cached Voynich annotation supplies an editor/author antecedent or parent-record target."},
  {"family_id":"EDGE02_CROSS_PAGE_REFERENT","source":str(P169.relative_to(ROOT)),"capacity_basis":"COMPLETE_SOURCE_FAMILY","raw_observations":len(a169),"physical_folios":len({r["source_physical_folio"] for r in a169}|{r["target_physical_folio"] for r in a169}),"exact_pivot":len(a169),"exact_target":len(owned),"direction_fixed":0,"singular_ownership":len(owned),"external_to_grammar":1,"prior_route":"GDT151;GDT152;GDT169;GDT351","status":"NO_SINGULAR_ORDERED_RECORD_EDGE","reason":"Human same/similar drawing pairs are not ordered parent links; only five have singular/provisional target inscriptions and the remaining four upgrades all failed."},
  {"family_id":"EDGE03_LOCAL_OBJECT_RELATION","source":str(P360.relative_to(ROOT)),"capacity_basis":"COMPLETE_SOURCE_FAMILY","raw_observations":len(local),"physical_folios":len(local_folios),"exact_pivot":len(local_loci),"exact_target":0,"direction_fixed":0,"singular_ownership":0,"external_to_grammar":1,"prior_route":"GDT002;GDT360","status":"LOCAL_SPATIAL_RELATION_NO_TARGET_ID","reason":"Attachment/contact/enclosure/group tags are local text-to-object states; the inventory has no independent target-locus or parent identifier."},
  {"family_id":"EDGE04_Q20_STAR_RECORD","source":str(Q20.relative_to(ROOT)),"capacity_basis":"UNIQUE_PHYSICAL_RECORDS_NOT_READINGS","raw_observations":len(q_units),"physical_folios":len(q_folios),"exact_pivot":len(q_units),"exact_target":0,"direction_fixed":0,"singular_ownership":len(q_units),"external_to_grammar":0,"prior_route":"Q20OB001;GDT114-131","status":"RECORD_BOUNDARY_NOT_INTER_RECORD_EDGE","reason":"Stars define 170 records, but no star or record points to another record; OPEN-to-BODY membership is the source hierarchy itself."},
  {"family_id":"EDGE05_EXTERNAL_DIAGRAM_HOMOLOGUE","source":str(P337.relative_to(ROOT)),"capacity_basis":"BEST_SINGLE_CANDIDATE_UPPER_BOUND_NOT_POOLED","raw_observations":len(a337),"physical_folios":max(int(r["voynich_physical_folios"]) for r in a337),"exact_pivot":0,"exact_target":0,"direction_fixed":0,"singular_ownership":0,"external_to_grammar":1,"prior_route":"GDT337;GDT354-359","status":"ZERO_VIABLE_ENDPOINTS","reason":"All eleven external correspondences fail target phase, ownership, or independent-folio transfer."},
  {"family_id":"EDGE06_REMAINING_REFERENT_UPGRADE","source":str(P351.relative_to(ROOT)),"capacity_basis":"COMPLETE_SOURCE_FAMILY","raw_observations":len(a351),"physical_folios":len({folio(r["source_page"]) for r in a351}|{folio(r["target_page"]) for r in a351}),"exact_pivot":len(a351),"exact_target":0,"direction_fixed":0,"singular_ownership":0,"external_to_grammar":1,"prior_route":"GDT351","status":"ZERO_NEW_OWNED_TARGETS","reason":"Three targets have no separate label and one is proximity-only."},
  {"family_id":"EDGE07_INTERNAL_RESUME_REPEAT","source":"not opened; definition-only control","capacity_basis":"DEFINITION_ONLY_NOT_ENUMERATED","raw_observations":"NOT_ENUMERATED","physical_folios":"NOT_ENUMERATED","exact_pivot":"NA","exact_target":"NA","direction_fixed":1,"singular_ownership":"NA","external_to_grammar":0,"prior_route":"GDT060;GDT111;GDT126;GDT165;GDT374;GDT379-381","status":"UNIDENTIFIABLE_SOURCE_DEFINED","reason":"A target defined by tuple recurrence, field return, line reset, DY/B3, or placement is reconstructed from the same grammar licensed as predictor."},
 ]
 for r in candidates:r["passes_all_gates"]=0
 write(ART/"gdt386_candidate_edge_families.tsv",candidates)
 write(ART/"gdt386_viable_endpoint_freeze.tsv",[],["endpoint_id","source_family","pivot_id","target_id","physical_folio","relation_provenance","status"])
 dedup=[
  {"route":"cross-page repeated referent invariance","prior":"GDT151;GDT152;GDT169;GDT351","genuinely_new":0,"decision":"CLOSED_NO_OWNED_ORDERED_EDGE"},
  {"route":"local attachment/contact/enclosure","prior":"GDT002;GDT110;GDT360","genuinely_new":0,"decision":"CLOSED_LOCAL_SPATIAL_STATE"},
  {"route":"record resume/repeat/anaphora from recurrence","prior":"GDT060;GDT111;GDT126;GDT165;GDT374;GDT379-381","genuinely_new":0,"decision":"CLOSED_SOURCE_DEFINED_OUTCOME"},
  {"route":"external diagram slot relation","prior":"GDT337;GDT354-359","genuinely_new":0,"decision":"CLOSED_ZERO_PHASE_OR_HELD_CAPACITY"},
  {"route":"Q20 OPEN/BODY parent relation","prior":"Q20OB001;GDT114-131","genuinely_new":0,"decision":"NOT_AN_INTER_RECORD_EDGE"},
 ];write(ART/"gdt386_closed_route_dedup.tsv",dedup)
 outputs=[ART/"gdt386_candidate_edge_families.tsv",ART/"gdt386_viable_endpoint_freeze.tsv",ART/"gdt386_closed_route_dedup.tsv"]
 result={"schema":"GDT386_RESULT_V1","status":"NO_INDEPENDENT_TARGET_RELATION_EDGE_AVAILABLE","candidate_families":len(candidates),"families_passing":0,"viable_endpoints":0,"counts":{"cross_page_referent_pairs":len(a169),"singular_or_provisional_referent_targets":len(owned),"remaining_referent_upgrades":len(a351),"local_relation_cases":len(local),"local_relation_unique_loci":len(local_loci),"q20_records":len(q_units),"q20_physical_folios":len(q_folios),"external_homologue_candidates":len(a337),"external_homologue_viable":sum(r["viable"]=="YES" for r in a337)},"voynich_formal_rows_read":0,"voynich_text_identities_read":0,"target_score_run":False,"semantic_state":"UNASSIGNED","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [P169,P351,P360,P337,Q20,P385]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in outputs},"implementation":{str((BASE/p).relative_to(ROOT)):sha(BASE/p) for p in ["src/run.py","src/validate.py"]},"claim_ceiling":"INDEPENDENT_RELATION_EDGE_CAPACITY_ONLY"};result["content_hash"]=content(result);(ART/"gdt386_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"counts":result["counts"]},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
