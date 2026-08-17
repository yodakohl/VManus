#!/usr/bin/env python3
"""Find all-reading exact label-group identities reused inside local prose."""
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
PROJ='gdt002_grammar_projection.tsv';VIS='gdt002_visual_inventory.tsv';PRED='gdt233_q13_label_predictions.tsv';C80='gdt244_f80r_paragraph_coordinate.tsv';C82='gdt242_f82r_paragraph_coordinate.tsv';CENS='gdt246_result.json'
OUTS=['gdt247_exact_label_prose_member_matches.tsv','gdt247_page_recurrence_context.tsv','gdt247_counterexamples.tsv'];DOCS=['GDT247_LABEL_PROSE_MEMBER_REUSE_METHOD.md','GDT247_LABEL_PROSE_MEMBER_REUSE_REPORT.md']
EDS=['ZL3b','IT2a','RF1b']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):
 with (R/p).open(encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,rows):
 with (R/p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sig(v):return tuple(v[e]['primary_sta_codes'] for e in EDS)
def main():
 src=[r for r in read(PROJ) if r['page'] in {'f80r','f82r'}];assert src and all(not r['page'].startswith('f84') for r in src)
 by=defaultdict(dict)
 for r in src:by[(r['page'],r['locus'],r['source_group_index'])][r['edition']]=r
 aligned={k:v for k,v in by.items() if set(v)==set(EDS)}
 visual={r['local_text_loci']:r for r in read(VIS) if r['local_text_loci']}
 pred={r['locus']:r for r in read(PRED) if r['page'] in {'f80r','f82r'}}
 coord={}
 for p in (C80,C82):
  for r in read(p):coord[r['locus']]=r
 matches=[];contexts=[]
 for page in ('f80r','f82r'):
  labs={k:v for k,v in aligned.items() if k[0]==page and next(iter(v.values()))['kind']=='L'}
  prose={k:v for k,v in aligned.items() if k[0]==page and next(iter(v.values()))['kind']=='P'}
  pc=Counter(sig(v) for v in prose.values())
  hitlabs=set()
  for lk,lv in labs.items():
   for pk,pv in prose.items():
    if sig(lv)!=sig(pv):continue
    hitlabs.add(lk);one=lv['ZL3b'];q=pv['ZL3b'];surfaces={e:lv[e]['ivtff_group_raw'] for e in EDS};ps={e:pv[e]['ivtff_group_raw'] for e in EDS}
    assert len(set(surfaces.values()))==1 and surfaces==ps
    loc=lk[1];ploc=pk[1];vv=visual[loc];pp=pred[loc];cc=coord[ploc]
    gi=int(pk[2]);gc=int(q['source_group_count']);pos='LINE_START' if gi==1 else ('LINE_END' if gi==gc else 'LINE_INTERNAL')
    matches.append({'page':page,'member_surface':surfaces['ZL3b'],'family_surface':one['primary_sta_families'],'label_locus':loc,'label_group_index':lk[2],'prose_locus':ploc,'prose_group_index':pk[2],'prose_group_count':gc,'prose_group_position':pos,'corrected_paragraph_id':cc['paragraph_id'],'paragraph_line_ordinal':cc['paragraph_line_ordinal'],'all_reading_member_identity':'EXACT_ZL3b_IT2a_RF1b','ownership_evidence':vv['ownership_evidence'],'neutral_visual_description':vv['neutral_description'],'transferred_label_prefix':pp['strict_prefix'],'transferred_label_residual':pp['strict_residual'],'semantic_value':'UNASSIGNED'})
  contexts.append({'page':page,'aligned_label_groups':len(labs),'aligned_prose_groups':len(prose),'unique_prose_member_vectors':len(pc),'label_groups_with_exact_prose_match':len(hitlabs),'label_match_fraction':f'{len(hitlabs)/len(labs):.9f}','prose_occurrences_belonging_to_recurrent_vector':sum(n for n in pc.values() if n>1),'prose_recurrent_occurrence_fraction':f'{sum(n for n in pc.values() if n>1)/len(prose):.9f}','comparability_note':'PROSE_RECURRENCE_IS_CONTEXT_ONLY_NOT_A_LABEL_NULL'})
 matches.sort(key=lambda r:(r['page'],int(r['label_locus'].split('.')[1]),int(r['prose_locus'].split('.')[1])))
 assert [(r['label_locus'],r['prose_locus'],r['member_surface']) for r in matches]==[('f80r.3','f80r.31','okaly'),('f80r.7','f80r.38','olky'),('f82r.36','f82r.6','okal')]
 write(OUTS[0],matches);write(OUTS[1],contexts)
 counter=[
 {'counterexample':'MINORITY_COVERAGE','value':'3/23 aligned label groups recur exactly in same-page prose','consequence':'not a general label dictionary or universal interface'},
 {'counterexample':'PROXIMITY_NOT_OWNERSHIP','value':'all three matching labels are PROXIMITY_ONLY','consequence':'no visible referent or object name is established'},
 {'counterexample':'RENDERER_NOT_EXCLUSIVE','value':'all three matches carry a transferred label prefix and two are consumed completely by it','consequence':'the prefix layer is enrichment/rendering propensity not a label-exclusive morpheme'},
 {'counterexample':'FAMILY_MATCH_EXCEEDS_MEMBER_MATCH','value':'GDT246 has three cross-scope families but only okaly/olky/okal survive exact all-reading member matching','consequence':'family recurrence alone overstates exact code identity'},
 {'counterexample':'NO_POSITIONAL_EQUIVALENCE','value':'all three prose matches are line-internal while labels are isolated groups','consequence':'reuse crosses display position but does not identify a shared record slot'},
 ]
 write(OUTS[2],counter)
 result={'experiment':'GDT247_LABEL_PROSE_MEMBER_REUSE','status':'MINORITY_EXACT_LABEL_TO_PROSE_CODE_INTERFACE_DESCRIPTIVE_NOT_SEMANTIC','aligned_label_groups':sum(int(x['aligned_label_groups']) for x in contexts),'aligned_prose_groups':sum(int(x['aligned_prose_groups']) for x in contexts),'exact_matches':len(matches),'matched_label_groups':len({x['label_locus'] for x in matches}),'member_surfaces':[x['member_surface'] for x in matches],'all_matches_line_internal':all(x['prose_group_position']=='LINE_INTERNAL' for x in matches),'all_matches_proximity_only':all(x['ownership_evidence']=='PROXIMITY_ONLY' for x in matches),'all_matches_label_prefix_positive':all(x['transferred_label_prefix']!='NONE' for x in matches),'interpretation':'A small minority of isolated graphical-label groups are byte/display-equivalent source-native units inside prose, consistent with labels selecting reusable prose-compatible code units rather than a wholly separate vocabulary.','active_semantic_assignments':0,'claim_ceiling':'Exact cross-scope member reuse only; no label ownership object role word language plaintext or translation.','f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{p:sha(p) for p in [PROJ,VIS,PRED,C80,C82,CENS]},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt247_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'matches':[(x['member_surface'],x['label_locus'],x['prose_locus']) for x in matches],'context':contexts},sort_keys=True))
if __name__=='__main__':main()
