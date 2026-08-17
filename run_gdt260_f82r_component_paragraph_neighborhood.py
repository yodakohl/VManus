#!/usr/bin/env python3
"""Search the fixed f82r.10 label components in its following paragraph."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
PROJ="gdt002_grammar_projection.tsv";COORD="gdt242_f82r_paragraph_coordinate.tsv";DOS="gdt239_f82r_label_dossier.tsv";ACCESS="gdt257_result.json"
OUTS=["gdt260_component_neighborhood.tsv","gdt260_component_controls.tsv","gdt260_counterexamples.tsv"]
DOCS=["GDT260_F82R_COMPONENT_PARAGRAPH_NEIGHBORHOOD_METHOD.md","GDT260_F82R_COMPONENT_PARAGRAPH_NEIGHBORHOOD_REPORT.md"]
EDS=["ZL3b","IT2a","RF1b"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with (R/p).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tail(m,k):
 return sum(math.comb(9,j)*math.comb(23,m-j) for j in range(k,min(9,m)+1))/math.comb(32,m) if m else 1.0
def main():
 d=[x for x in read(DOS) if x["locus"]=="f82r.10"];assert len(d)==1 and d[0]["ownership_evidence"]=="CONNECTED_COMPONENT" and "cross-shaped" in d[0]["human_local_comment"]
 p=read(PROJ);assert {x["page"] for x in p}=={"f80r","f82r"} and all(not x["page"].startswith("f84") for x in p)
 c={x["locus"]:x for x in read(COORD)};assert c["f82r.11"]["paragraph_id"]=="P2" and c["f82r.11"]["paragraph_line_ordinal"]=="1"
 rows=[];controls=[]
 for ed in EDS:
  target=sorted([x for x in p if x["edition"]==ed and x["locus"]=="f82r.10"],key=lambda x:int(x["source_group_index"]));full=sum((x["primary_sta_codes"].split() for x in target),[]);assert len(full)==7
  reps=[("LEFT_SPLIT_COMPONENT",full[:4]),("RIGHT_SPLIT_COMPONENT",full[4:]),("FULL_JOINED_LABEL",full)]
  prose=[x for x in p if x["edition"]==ed and x["page"]=="f82r" and x["kind"]=="P" and x["locus"] in c]
  byline=defaultdict(list)
  for x in prose:byline[x["locus"]].append(x)
  for name,t in reps:
   hit=defaultdict(list);exact=set();op=Counter()
   for loc,xs in byline.items():
    for x in xs:
     q=x["primary_sta_codes"].split();op[c[loc]["paragraph_id"]]+=max(0,len(q)-len(t)+1)
     for i in range(len(q)-len(t)+1):
      z=q[i:i+len(t)];dist=sum(a!=b for a,b in zip(t,z))
      if dist<=1:hit[loc].append(f'{x["ivtff_group_raw"]}@{i+1}:d{dist}')
      if dist==0:exact.add(loc)
   hist=Counter(c[x]["paragraph_id"] for x in hit);m=len(hit);k=hist["P2"];local=tail(m,k)
   p2loc=sorted([x for x in hit if c[x]["paragraph_id"]=="P2"],key=lambda z:int(z.split('.')[1]))
   rows.append({"edition":ed,"representation":name,"target_member_codes":" ".join(t),"target_length":len(t),"P1_hit_lines":hist["P1"],"P2_hit_lines":k,"P3_hit_lines":hist["P3"],"all_hit_lines":m,"exact_distance0_hit_lines":len(exact),"P2_hit_loci":";".join(x+"["+",".join(hit[x])+"]" for x in p2loc),"local_hypergeom_p":f"{local:.12f}","three_representation_bonferroni_p":f"{min(1,3*local):.12f}","P1_opportunity_windows":op["P1"],"P2_opportunity_windows":op["P2"],"P3_opportunity_windows":op["P3"],"semantic_value":"UNASSIGNED"})
  # Family-only control: line-level ACAB occurrence after concatenating groups.
  fam=Counter();loci=[]
  for loc,xs in byline.items():
   s="".join(x["primary_sta_families"] for x in sorted(xs,key=lambda z:int(z["source_group_index"])))
   if "ACAB" in s:fam[c[loc]["paragraph_id"]]+=1;loci.append(loc)
  controls.append({"edition":ed,"control":"LEFT_COMPONENT_FAMILY_ACAB_ANYWHERE_IN_LINE","P1_lines":fam["P1"],"P2_lines":fam["P2"],"P3_lines":fam["P3"],"all_lines":sum(fam.values()),"loci":";".join(sorted(loci,key=lambda z:int(z.split('.')[1]))),"result":"BROAD_ALL_PARAGRAPHS_NOT_P2_SPECIFIC"})
 write(OUTS[0],rows);write(OUTS[1],controls)
 left=[x for x in rows if x["representation"]=="LEFT_SPLIT_COMPONENT"]
 assert [(x["edition"],x["P2_hit_lines"],x["all_hit_lines"]) for x in left]==[("ZL3b",3,3),("IT2a",4,4),("RF1b",3,3)]
 counter=[
  {"counterexample":"NO_EXACT_MEMBER_COPY","value":"0 distance-zero prose lines for LEFT_SPLIT_COMPONENT in every reading","consequence":"lead requires a one-member neighborhood rather than exact code identity"},
  {"counterexample":"FULL_LABEL_NO_MATCH","value":"0 distance<=1 prose lines for FULL_JOINED_LABEL in every reading","consequence":"paragraph does not repeat the complete attached label"},
  {"counterexample":"RIGHT_COMPONENT_BROAD","value":"P2/all hit-lines ZL 5/13 IT 7/19 RF 3/10","consequence":"not every label component points to the following paragraph"},
  {"counterexample":"FAMILY_ACAB_BROAD","value":"P1=2 P2=3 P3=4 lines in every reading","consequence":"coarse family recurrence alone is not a component reference"},
  {"counterexample":"BOUNDARY_READING_SENSITIVE","value":"ZL3b joined; IT2a and RF1b split after member four","consequence":"component boundary is supported by two readings but is not invariant"},
  {"counterexample":"EXPOSED_ANALYTIC_CHOICE","value":"one-edit member windows and attached-label query devised after page exposure","consequence":"adjusted p covers three representations only and is hypothesis-generating"},]
 write(OUTS[2],counter)
 access=json.loads((R/ACCESS).read_text());assert access["access"]["pristine_access_seal"] is False
 result={"experiment":"GDT260_F82R_COMPONENT_PARAGRAPH_NEIGHBORHOOD","status":"F82R_ATTACHED_LABEL_LEFT_COMPONENT_NEIGHBORHOOD_CONCENTRATES_IN_FOLLOWING_PARAGRAPH_PROVISIONAL","externally_selected_label":"f82r.10","ownership_evidence":"CONNECTED_COMPONENT","following_paragraph":"P2","left_component_hits":{"ZL3b":"3/3","IT2a":"4/4","RF1b":"3/3"},"left_component_local_p":{x["edition"]:float(x["local_hypergeom_p"]) for x in left},"left_component_three_representation_adjusted_p":{x["edition"]:float(x["three_representation_bonferroni_p"]) for x in left},"exact_left_component_copies":0,"full_label_neighbor_hits":0,"family_control":"ACAB_P1_2_P2_3_P3_4_EVERY_READING","active_semantic_assignments":0,"interpretation":"The fine member-code neighborhood of the attached label's left split component is concentrated in the physically following paragraph, nominating a local component-address/topic family while remaining exposed and compatible with paragraph-local morphotactics.","next_prediction":"On a different source-bound attached label with a mechanically adjacent paragraph, freeze the label components before formal access and predict enrichment in that adjacent paragraph.","claim_ceiling":"Provisional attached-label adjacent-paragraph formal neighborhood only; no component name object process meaning word language plaintext or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False},"inputs":{x:sha(x) for x in [PROJ,COORD,DOS,ACCESS]},"outputs":{},"documents":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 for x in OUTS:result["outputs"][x]=sha(x)
 for x in DOCS:result["documents"][x]=sha(x)
 result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt260_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"hits":result["left_component_hits"]},sort_keys=True))
if __name__=="__main__":main()
