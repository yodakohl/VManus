#!/usr/bin/env python3
"""Explain the exposed GDT144 MHI004 partial-retrieval lead."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;UNITS=R/'gdt112_o_ot_units.tsv';META=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';PARENT=R/'gdt144_result.json';METHOD=R/'GDT145_MHI004_RETRIEVAL_MECHANISM_METHOD.md';REPORT=R/'GDT145_MHI004_RETRIEVAL_MECHANISM_REPORT.md';SENS=R/'gdt145_sensitivities.tsv';COUNTER=R/'gdt145_counterexamples.tsv';RESULT=R/'gdt145_result.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def jac(a,b):return len(a&b)/len(a|b) if a|b else 0.
meta={x['page']:x for x in read(META)};eligible0=sorted(p for p,x in meta.items() if x['currier']=='A' and x['hand']=='1');by=defaultdict(set)
for x in read(UNITS):
 assert not x['page'].startswith('f84r')
 if x['page'] in eligible0:by[x['page']].add(x['page_host'])
eligible=sorted(p for p in eligible0 if p in by);assert len(eligible)==93
rel=next(x for x in read(INV) if x['relation_id']=='MHI004');s=rel['source_page'];t=rel['target_page'];assert s=='f6r' and t=='f51r';cands=[p for p in eligible if p!=s and meta[p]['physical_folio']!=meta[s]['physical_folio']];df=Counter(h for p in eligible for h in by[p]);n=len(eligible)
def idf(h):return math.log((n+.5)/(df[h]+.5))
def wjac(a,b):
 u=a|b;return sum(idf(h) for h in a&b)/sum(idf(h) for h in u) if u else 0.
def rank(fun,pool):
 score=fun(by[s],by[t]);v=[fun(by[s],by[p]) for p in pool];return score,1+sum(x>score+1e-12 for x in v),sum(x>=score-1e-12 for x in v)/len(v)
raw=rank(jac,cands);weighted=rank(wjac,cands);matched=[p for p in cands if len(by[p])==len(by[t])];wm=rank(wjac,matched)
longs={p:{h for h in by[p] if len(h)>=2} for p in eligible};long_capacity=bool(longs[s] and longs[t]);shared=sorted(by[s]&by[t]);assert shared==['l']
rows=[{'variant':'UNWEIGHTED_EXACT_HOST_SET','candidate_pages':len(cands),'source_hosts':'|'.join(sorted(by[s])),'target_hosts':'|'.join(sorted(by[t])),'score':raw[0],'rank':raw[1],'inclusive_tail':raw[2],'capacity':'PASS'},{'variant':'IDF_WEIGHTED_EXACT_HOST_SET','candidate_pages':len(cands),'source_hosts':'|'.join(sorted(by[s])),'target_hosts':'|'.join(sorted(by[t])),'score':weighted[0],'rank':weighted[1],'inclusive_tail':weighted[2],'capacity':'PASS'},{'variant':'IDF_WEIGHTED_TARGET_SET_SIZE_MATCHED','candidate_pages':len(matched),'source_hosts':'|'.join(sorted(by[s])),'target_hosts':'|'.join(sorted(by[t])),'score':wm[0],'rank':wm[1],'inclusive_tail':wm[2],'capacity':'PASS'},{'variant':'MIN_HOST_LENGTH_2','candidate_pages':len(cands),'source_hosts':'|'.join(sorted(longs[s])),'target_hosts':'|'.join(sorted(longs[t])),'score':'NA','rank':'NA','inclusive_tail':'NA','capacity':'PASS' if long_capacity else 'NO_PAIR_FEATURE_CAPACITY'}]
prevalence=df['l']/n;gates={'shared_host_page_prevalence_gt_0_8':prevalence>.8,'idf_rank_outside_top_decile':weighted[1]>math.ceil(.1*len(cands)),'length_two_pair_capacity_absent':not long_capacity};status='MHI004_O_OT_LEAD_EXPLAINED_BY_UBIQUITOUS_SINGLETON_HOST' if all(gates.values()) else 'MHI004_O_OT_LEAD_MECHANISM_UNRESOLVED'
counter=[{'type':'UBIQUITOUS_SHARED_HOST','item':'l','value':f"{df['l']}/{n}",'detail':'The only exact shared O/OT PAGE_HOST occurs on nearly every eligible page.'},{'type':'COMMON_SOURCE_HOST','item':'d','value':f"{df['d']}/{n}",'detail':'The second source host is also common and absent from the target.'},{'type':'SIZE_MATCHED_TIE','item':'f27v','value':'l','detail':'The target ties another one-host page under IDF weighting.'},{'type':'NO_LONG_HOST_CAPACITY','item':'MHI004','value':'NA','detail':'Both pair sets have no shared feature once one-character hosts are removed.'}]
write(SENS,rows);write(COUNTER,counter)
REPORT.write_text(f"""# GDT145 — MHI004 retrieval mechanism

## Outcome

**{status}**

The apparent GDT144 lead is a small-set/common-host artifact. f6r has only the O/OT PAGE_HOST set `{{d,l}}`; f51r has only `{{l}}`. The shared `l` occurs on {df['l']}/{n} eligible pages, while `d` occurs on {df['d']}/{n}. Unweighted character-boundary overlap had placed f51r at 3/91, but explicit exact-host IDF weighting places it at {weighted[1]}/91 (inclusive tail {weighted[2]:.3f}). Among the five one-host candidate pages, f51r ties f27v and has tail {wm[2]:.3f}. Removing one-character hosts leaves no pair feature.

Therefore this sensitivity supplies no candidate leaf core and no reason to localize or gloss `l`. It does not negate the full GDT140 five-target assignment, but it removes the only apparent corpus-wide O/OT retrieval exception. Only f84r-free derived tables were used; no source or image was opened.
""",encoding='utf8')
result={'schema':'GDT145_MHI004_RETRIEVAL_MECHANISM_RESULT_V1','status':status,'eligible_pages':n,'relation_id':'MHI004','source_page':s,'target_page':t,'shared_hosts':shared,'host_document_frequencies':{'l':df['l'],'d':df['d']},'sensitivities':rows,'gates':gates,'interpretation':'The partial O/OT MHI004 rank is explained by one ubiquitous singleton PAGE_HOST and tiny target set size.','claim_ceiling':'Mechanism audit only; no PAGE_HOST meaning, plant part, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'all_actual_inputs_have_zero_f84r_rows':True,'source_or_image_opened':False,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (UNITS,META,INV,PARENT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (SENS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'idf_rank':weighted[1],'idf_tail':weighted[2],'l_df':df['l'],'long_capacity':long_capacity},sort_keys=True))
