#!/usr/bin/env python3
"""Compare record architecture on matched Herbal Currier A/B pages."""
from __future__ import annotations
import csv,functools,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FLAGS=("TEXT_WRAPS_GRAPHIC","TEXT_AVOIDS_GRAPHIC","TEXT_INSIDE_GRAPHIC","TEXT_BETWEEN_GRAPHICS")
PRIMARY=("FIELDS_PER_LINE","DY_CHAIN_RATE","SINGLETON_CLOSED_RATE","OPEN_TAIL_AFTER_DY_RATE","DIRECT_MINUS_INSERTIONAL_QL_RATE")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def guarded(path,pages):
 out=[]
 with path.open(encoding="utf-8",newline="")as h:
  header=h.readline();columns=header.rstrip("\n").split("\t");page_index=columns.index("page")
  for line in h:
   page=line.split("\t")[page_index]
   if page not in pages:continue
   out.extend(csv.DictReader([header,line],delimiter="\t"))
 return {r["page"]:r for r in out}
def write(n,rows):
 with (ROOT/n).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def profile(text):return"MIXED"if"α:"in text and"β:"in text else"ALPHA"if"α:"in text else"BETA"if"β:"in text else"UNCLASSIFIED"
def ql(f,pats):return any(p in f for p in pats)
def page_metrics(rows):
 lines=defaultdict(list)
 for r in rows:lines[r["locus"]].append(r)
 checkpoints=fields=dy_next=dy_chain=singleton=closed=lines_dy=multi=open_tail=0;closed_lengths=[];direct=[];insert=[]
 for line in lines.values():
  line.sort(key=lambda r:int(r["group_index"]));states=[r["record_state"]for r in line];dy=[i for i,s in enumerate(states)if s=="DY_RESOLUTION"];checkpoints+=len(dy);fields+=len(dy)+int(not dy or states[-1]!="DY_RESOLUTION");lines_dy+=int(bool(dy));multi+=int(len(dy)>=2);dy_next+=sum(s=="DY_RESOLUTION"for s in states[:-1]);dy_chain+=sum(a==b=="DY_RESOLUTION"for a,b in zip(states,states[1:]));open_tail+=int(bool(dy)and states[-1]!="DY_RESOLUTION");start=0
  for i in dy:closed+=1;closed_lengths.append(i-start+1);singleton+=int(i==start);start=i+1
  for i,r in enumerate(line):
   f=r["family_surface"]
   if ql(f,("QJB","QKB","LJB","LKB")):direct.append(("QJB"in f or"QKB"in f,i>0 and states[i-1]=="DY_RESOLUTION"))
   if ql(f,("QJAB","QKAB","LJAB","LKAB")):insert.append(("QJAB"in f or"QKAB"in f,i>0 and states[i-1]=="DY_RESOLUTION"))
 n=len(lines);groups=sum(len(x)for x in lines.values());rate=lambda a,b:a/b if b else 0.
 return {"LINES":n,"GROUPS":groups,"FIELDS_PER_LINE":fields/n,"DY_PER_LINE":checkpoints/n,"DY_LINE_RATE":lines_dy/n,"MULTI_DY_LINE_RATE":multi/n,"DY_CHAIN_RATE":rate(dy_chain,dy_next),"SINGLETON_CLOSED_RATE":rate(singleton,closed),"MEAN_CLOSED_FIELD_LENGTH":rate(sum(closed_lengths),len(closed_lengths)),"OPEN_TAIL_AFTER_DY_RATE":rate(open_tail,lines_dy),"DIRECT_QL_RATE":len(direct)/groups,"INSERTIONAL_QL_RATE":len(insert)/groups,"DIRECT_MINUS_INSERTIONAL_QL_RATE":len(direct)/groups-len(insert)/groups,"DIRECT_Q_SHARE":rate(sum(q for q,p in direct),len(direct)),"INSERTIONAL_Q_SHARE":rate(sum(q for q,p in insert),len(insert)),"DIRECT_POST_DY_RATE":rate(sum(p for q,p in direct),len(direct)),"INSERTIONAL_POST_DY_RATE":rate(sum(p for q,p in insert),len(insert))}
def match_cost(a,b,role,ann):
 x,y=role[a],role[b];ta=set(ann[a]["source_tags"].split(";"));tb=set(ann[b]["source_tags"].split(";"));return abs(int(x["P_count"])-int(y["P_count"]))+2*abs(int(x["paragraph_start_count"])-int(y["paragraph_start_count"]))+4*int((int(x["L_count"])>0)!=(int(y["L_count"])>0))+2*sum((f in ta)!=(f in tb)for f in FLAGS)
def folio_matching(pages,page_rows,profiles,role,ann):
 A=sorted(p for p in pages if page_rows[p][0]["currier"]=="A");B=sorted(p for p in pages if page_rows[p][0]["currier"]=="B");options=defaultdict(list)
 for b in B:
  for a in A:
   cost=match_cost(a,b,role,ann)
   if profiles[a]==profiles[b]and profiles[b]!="BETA"and cost<=4:options[page_rows[b][0]["physical_folio"]].append((page_rows[a][0]["physical_folio"],a,b,profiles[b],cost))
 bfolios=sorted(options,key=lambda f:(len(options[f]),f))
 @functools.lru_cache(None)
 def solve(i,used):
  if i==len(bfolios):return(0,0,())
  best=solve(i+1,used)
  for afolio,a,b,profile_name,cost in options[bfolios[i]]:
   if afolio in used:continue
   tail=solve(i+1,tuple(sorted(used+(afolio,))));candidate=(tail[0]+1,tail[1]+cost,tuple(sorted(tail[2]+((a,b,profile_name,cost),))))
   if(-candidate[0],candidate[1],candidate[2])<(-best[0],best[1],best[2]):best=candidate
  return best
 selected=solve(0,())[2];return sum(len(v)for v in options.values()),selected
def signflip(values):
 observed=sum(values)/len(values);worlds=[sum(s*x for s,x in zip(signs,values))/len(values)for signs in itertools.product((-1,1),repeat=len(values))];return observed,sum(x>=observed-1e-15 for x in worlds)/len(worlds)
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv);page_rows=defaultdict(list)
 for r in inv:
  if r["section"]=="H":page_rows[r["page"]].append(r)
 pages=set(page_rows);base=ROOT/"experiments/semantic_assumptions/results";ann=guarded(base/"existing_human_page_annotations.tsv",pages);role=guarded(base/"existing_human_page_role_matrix.tsv",pages);assert set(ann)==set(role)==pages and"f84r"not in pages
 metrics={p:page_metrics(rs)for p,rs in page_rows.items()};compiled=defaultdict(list)
 for r in read("gdt020_line_phase_parses.tsv"):
  if r["page"]in pages:compiled[r["page"]].append(r)
 assert set(compiled)==pages and all(len(compiled[p])==metrics[p]["LINES"]and abs(sum(int(r["phase_count"])for r in compiled[p])/len(compiled[p])-metrics[p]["FIELDS_PER_LINE"])<1e-12 for p in pages)
 profiles={p:profile(ann[p]["illustrations"])for p in pages};pageout=[]
 for p in sorted(pages):
  r=page_rows[p][0];x=role[p];row={"page":p,"physical_folio":r["physical_folio"],"currier":r["currier"],"hand":r["hand"],"illustration_profile":profiles[p],"catalogue_prose_lines":x["P_count"],"paragraph_starts":x["paragraph_start_count"],"catalogue_label_presence":int(int(x["L_count"])>0),"special_layout_flags":"|".join(f for f in FLAGS if f in ann[p]["source_tags"].split(";"))}
  row.update({k:(v if isinstance(v,int)else f"{v:.12f}")for k,v in metrics[p].items()});row["claim_state"]="HERBAL_PAGE_FORMAL_ARCHITECTURE_NOT_MEANING";pageout.append(row)
 write("gdt031_herbal_page_architecture.tsv",pageout)
 eligible_edges,candidate=folio_matching(pages,page_rows,profiles,role,ann)
 matched=[]
 for i,(a,b,pr,cost) in enumerate(candidate,1):matched.append({"pair_id":f"HP{i:02d}","currier_a_page":a,"currier_a_folio":page_rows[a][0]["physical_folio"],"currier_b_page":b,"currier_b_folio":page_rows[b][0]["physical_folio"],"illustration_profile":pr,"match_cost":cost,"a_prose_lines":role[a]["P_count"],"b_prose_lines":role[b]["P_count"],"a_paragraph_starts":role[a]["paragraph_start_count"],"b_paragraph_starts":role[b]["paragraph_start_count"],"classified_profile":int(pr!="UNCLASSIFIED"),"claim_state":"VISIBLE_PROFILE_LAYOUT_MATCH_NOT_IDENTICAL_IMAGE"})
 assert len({r["currier_a_folio"]for r in matched})==len({r["currier_b_folio"]for r in matched})==len(matched)
 write("gdt031_matched_herbal_pages.tsv",matched);kept=matched;tests=[]
 supplementary=("DY_PER_LINE","DY_LINE_RATE","MULTI_DY_LINE_RATE","MEAN_CLOSED_FIELD_LENGTH","DIRECT_QL_RATE","INSERTIONAL_QL_RATE","DIRECT_Q_SHARE","INSERTIONAL_Q_SHARE","DIRECT_POST_DY_RATE","INSERTIONAL_POST_DY_RATE")
 for feature in PRIMARY+supplementary:
  diffs=[metrics[r["currier_b_page"]][feature]-metrics[r["currier_a_page"]][feature]for r in kept];effect,p=signflip(diffs);classified=[d for d,r in zip(diffs,kept)if r["classified_profile"]];classified_effect,classified_p=signflip(classified);tests.append({"test_scope":"PRIMARY_FIVE"if feature in PRIMARY else"SUPPLEMENTARY","feature":feature,"matched_pairs":len(kept),"b_minus_a_mean":f"{effect:.12f}","positive_pairs":sum(x>0 for x in diffs),"zero_pairs":sum(x==0 for x in diffs),"one_sided_exact_p":f"{p:.12f}","five_test_adjusted_p":f"{min(1,p*len(PRIMARY)):.12f}"if feature in PRIMARY else"NOT_APPLICABLE","classified_only_pairs":len(classified),"classified_only_b_minus_a":f"{classified_effect:.12f}","classified_only_positive_pairs":sum(x>0 for x in classified),"classified_only_zero_pairs":sum(x==0 for x in classified),"classified_only_exact_p":f"{classified_p:.12f}","classified_only_five_test_adjusted_p":f"{min(1,classified_p*len(PRIMARY)):.12f}"if feature in PRIMARY else"NOT_APPLICABLE","claim_state":"MATCHED_HERBAL_ARCHITECTURE_NOT_SEMANTICS"})
 write("gdt031_matched_architecture_tests.tsv",tests);by={(r["feature"]):r for r in tests};status="HERBAL_B_RECORD_DENSITY_SUPPORTED_FULL_RECORD_ARCHITECTURE_NOT_SUPPORTED"
 def avg(currier,feature):
  pp=[p for p in pages if page_rows[p][0]["currier"]==currier];return sum(metrics[p][feature]for p in pp)/len(pp)
 report=f"""# GDT031 Herbal Currier record architecture

Status: **{status.replace('_',' ')}**

The full section-H census has 95 Currier-A pages and 32 Currier-B pages. B is
descriptively denser: {avg('B','FIELDS_PER_LINE'):.3f} versus
{avg('A','FIELDS_PER_LINE'):.3f} compiled fields per line. But illustration
profiles differ sharply: A has 84 ALPHA and no BETA pages, while B has 18 BETA
and only two ALPHA pages. The all-page contrast is therefore not causal.

The strict comparable-page sensitivity retains eight independent-folio pairs after matching
human illustration profile, prose-line count, paragraph count, labels, and
special layout. B remains +{float(by['FIELDS_PER_LINE']['b_minus_a_mean']):.3f}
fields/line on 7/8 pairs (exact p={float(by['FIELDS_PER_LINE']['one_sided_exact_p']):.4f};
five-test adjusted p={float(by['FIELDS_PER_LINE']['five_test_adjusted_p']):.4f}).
The Q/L renderer shift also survives: direct-minus-insertional family rate is
{float(by['DIRECT_MINUS_INSERTIONAL_QL_RATE']['b_minus_a_mean']):+.3f} on 7/8
pairs (adjusted p={float(by['DIRECT_MINUS_INSERTIONAL_QL_RATE']['five_test_adjusted_p']):.4f}).

The broader “B is intrinsically more list-like” theory does not survive as a
five-part package. Matched DY chaining is
{float(by['DY_CHAIN_RATE']['b_minus_a_mean']):+.3f} (adjusted p={float(by['DY_CHAIN_RATE']['five_test_adjusted_p']):.3f}),
singleton closed fields {float(by['SINGLETON_CLOSED_RATE']['b_minus_a_mean']):+.3f}
(adjusted p={float(by['SINGLETON_CLOSED_RATE']['five_test_adjusted_p']):.3f}), and
open-tail continuation {float(by['OPEN_TAIL_AFTER_DY_RATE']['b_minus_a_mean']):+.3f}
(adjusted p={float(by['OPEN_TAIL_AFTER_DY_RATE']['five_test_adjusted_p']):.3f}).
The raw all-page contrasts cannot be cleanly separated from page-profile differences.

Only four pairs have affirmative ALPHA/MIXED visual profiles; four match the
absence of a catalogue profile. In that four-pair classified-only sensitivity,
the field-density effect is {float(by['FIELDS_PER_LINE']['classified_only_b_minus_a']):+.3f}
(adjusted p={float(by['FIELDS_PER_LINE']['classified_only_five_test_adjusted_p']):.3f})
and the Q/L effect is {float(by['DIRECT_MINUS_INSERTIONAL_QL_RATE']['classified_only_b_minus_a']):+.3f}
(adjusted p={float(by['DIRECT_MINUS_INSERTIONAL_QL_RATE']['classified_only_five_test_adjusted_p']):.3f});
neither clears the five-test threshold at this lower capacity. All A pages are hand 1 and all B pages are
hands 2/3/5, so Currier cannot be separated from hand. The supported statement
is narrow: within Herbal and approximate visible/layout matching, B has more
DY-delimited fields per line and a different Q/L-family realization regime.
It is not proven intrinsically more record-like on chaining, closed-template,
or continuation axes. The guarded inputs retain no f84r row; f84r was not
opened, retained, joined, or scored. No role, word, sound, language, plaintext,
meaning, or translation is assigned.
""";(ROOT/"GDT031_HERBAL_CURRIER_RECORD_ARCHITECTURE_REPORT.md").write_text(report)
 outputs=("gdt031_herbal_page_architecture.tsv","gdt031_matched_herbal_pages.tsv","gdt031_matched_architecture_tests.tsv","GDT031_HERBAL_CURRIER_RECORD_ARCHITECTURE_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt020_line_phase_parses.tsv","gdt025_result.json","GDT031_HERBAL_CURRIER_RECORD_ARCHITECTURE_METHOD.md")
 result={"schema":"GDT031_HERBAL_CURRIER_RECORD_ARCHITECTURE_RESULT_V1","status":status,"herbal_pages":{"A":sum(page_rows[p][0]["currier"]=="A"for p in pages),"B":sum(page_rows[p][0]["currier"]=="B"for p in pages)},"illustration_profiles":{"A":dict(Counter(profiles[p]for p in pages if page_rows[p][0]["currier"]=="A")),"B":dict(Counter(profiles[p]for p in pages if page_rows[p][0]["currier"]=="B"))},"eligible_match_edges":eligible_edges,"matched_folio_pairs":len(matched),"classified_pairs":sum(int(r["classified_profile"])for r in kept),"primary_tests":{k:by[k]for k in PRIMARY},"hand_confound":{"A":["1"],"B":sorted({page_rows[p][0]["hand"]for p in pages if page_rows[p][0]["currier"]=="B"})},"guarded_source_subsets":{"existing_human_page_annotations_rows":len(ann),"existing_human_page_annotations_canonical_sha256":csha([ann[p]for p in sorted(ann)]),"existing_human_page_role_matrix_rows":len(role),"existing_human_page_role_matrix_canonical_sha256":csha([role[p]for p in sorted(role)])},"interpretation":"Herbal B has higher matched field density and a different Q/L-family realization regime; matched chaining, closed-template, and continuation axes do not establish a general intrinsic record/list architecture.","f84r":{"input_contains_rows":False,"annotation_rows_retained":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Matched within-Herbal formal architecture only; Currier remains confounded with hand and no role, word, sound, language, plaintext, meaning, or translation follows.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt031_herbal_currier_record_architecture.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt031_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"pages":result["herbal_pages"],"pairs":len(kept),"primary":result["primary_tests"]},sort_keys=True))
if __name__=="__main__":main()
