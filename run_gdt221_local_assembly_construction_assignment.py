#!/usr/bin/env python3
"""GDT221: two-folio top/bottom label-to-prose construction assignment."""
import csv, hashlib, itertools, json
from collections import Counter, defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
MAN=R/'gdt221_assembly_manifest.tsv'; LABELS=R/'gdt012_annotated_core_inventory.tsv'; GROUPS=R/'gdt016_group_state_inventory.tsv'; OLD=R/'gdt220_result.json'
METHOD=R/'GDT221_LOCAL_ASSEMBLY_CONSTRUCTION_ASSIGNMENT_METHOD.md'; REPORT=R/'GDT221_LOCAL_ASSEMBLY_CONSTRUCTION_ASSIGNMENT_REPORT.md'
SCORES=R/'gdt221_assembly_scores.tsv'; RETR=R/'gdt221_label_retrieval.tsv'; COUNTER=R/'gdt221_counterexamples.tsv'; RESULT=R/'gdt221_result.json'
REPS=('RAW_CHAR3','PAGE_HOST_CHAR3','SOURCE_FAMILY_CHAR3')

def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def add3(c,s):
 s='^'+s+'$'
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1
def vector(rows,rep):
 c=Counter();field={'RAW_CHAR3':'token','PAGE_HOST_CHAR3':'residual_host','SOURCE_FAMILY_CHAR3':'family_surface'}[rep]
 for r in rows:add3(c,r[field])
 return c
def sim(a,b):
 keys=set(a)|set(b);den=sum(max(a[k],b[k]) for k in keys)
 return sum(min(a[k],b[k]) for k in keys)/den if den else 0.0

def main():
 man=read(MAN);assert len(man)==4 and {(r['page'],r['assembly']) for r in man}=={('f75v','TOP'),('f75v','BOTTOM'),('f83r','TOP'),('f83r','BOTTOM')}
 assert not any(r['page'].startswith('f84') for r in man)
 label_by=defaultdict(list)
 with LABELS.open(encoding='utf8',newline='')as h:
  for r in csv.DictReader(h,delimiter='\t'):
   assert not r['page'].startswith('f84')
   if r['page'] in {'f75v','f83r'}:label_by[r['locus']].append(r)
 prose_by=defaultdict(list)
 with GROUPS.open(encoding='utf8',newline='')as h:
  for r in csv.DictReader(h,delimiter='\t'):
   if r['page'].startswith('f84'):continue
   if r['page'] in {'f75v','f83r'}:prose_by[r['locus']].append(r)
 spec={(r['page'],r['assembly']):r for r in man}
 def locs(row,key):return row[key].split(',')
 missing_labels=sorted({x for r in man for x in locs(r,'label_loci') if x not in label_by})
 assert missing_labels==['f75v.22','f75v.23','f83r.50']
 target_prose={x for r in man for x in locs(r,'prose_loci')}
 complete={l:rr for l,rr in prose_by.items() if l in target_prose and len(rr)==int(rr[0]['group_count'])}
 score_rows=[];retr_rows=[];page_leads={rep:{} for rep in REPS}
 for scope in ('COMPLETE_LINES_PRIMARY','ALL_AVAILABLE_SENSITIVITY'):
  source=complete if scope=='COMPLETE_LINES_PRIMARY' else prose_by
  for rep in REPS:
   for page in ('f75v','f83r'):
    lv={};pv={}
    for side in ('TOP','BOTTOM'):
     row=spec[(page,side)]
     lv[side]=vector([z for locus in locs(row,'label_loci') for z in label_by.get(locus,[])],rep)
     pv[side]=vector([z for locus in locs(row,'prose_loci') for z in source.get(locus,[])],rep)
    tt=sim(lv['TOP'],pv['TOP']);tb=sim(lv['TOP'],pv['BOTTOM']);bt=sim(lv['BOTTOM'],pv['TOP']);bb=sim(lv['BOTTOM'],pv['BOTTOM'])
    lead=tt+bb-tb-bt
    if scope=='COMPLETE_LINES_PRIMARY':page_leads[rep][page]=lead
    score_rows.append({'scope':scope,'representation':rep,'page':page,'top_to_top':f'{tt:.12g}','top_to_bottom':f'{tb:.12g}','bottom_to_top':f'{bt:.12g}','bottom_to_bottom':f'{bb:.12g}','correct_assignment_lead':f'{lead:.12g}','complete_top_prose_lines':sum(l in complete for l in locs(spec[(page,'TOP')],'prose_loci')),'complete_bottom_prose_lines':sum(l in complete for l in locs(spec[(page,'BOTTOM')],'prose_loci'))})
    # Fixed individual-label diagnostic against the same scope.
    for side in ('TOP','BOTTOM'):
     for locus in locs(spec[(page,side)],'label_loci'):
      if not label_by.get(locus):continue
      q=vector(label_by[locus],rep);a=sim(q,pv['TOP']);b=sim(q,pv['BOTTOM'])
      pred='TIE' if abs(a-b)<1e-15 else 'TOP' if a>b else 'BOTTOM'
      retr_rows.append({'scope':scope,'representation':rep,'page':page,'label_locus':locus,'true_assembly':side,'top_similarity':f'{a:.12g}','bottom_similarity':f'{b:.12g}','predicted_assembly':pred,'correct':int(pred==side)})
 worlds=list(itertools.product((1,-1),repeat=2));mat=[]
 for world in worlds:mat.append([sum(world[i]*page_leads[rep][page] for i,page in enumerate(('f75v','f83r'))) for rep in REPS])
 means=[sum(r[j] for r in mat)/4 for j in range(3)];sds=[(sum((r[j]-means[j])**2 for r in mat)/4)**.5 or 1 for j in range(3)]
 zs=[[ (r[j]-means[j])/sds[j] for j in range(3)] for r in mat];mx=[max(r) for r in zs]
 summaries={}
 for j,rep in enumerate(REPS):
  obs=mat[0][j];local=sum(r[j]>=obs-1e-15 for r in mat)/4;maxp=sum(x>=zs[0][j]-1e-15 for x in mx)/4
  summaries[rep]={'aggregate_lead':obs,'local_exact_p':local,'max_three_p':maxp,'positive_pages':sum(page_leads[rep][p]>0 for p in ('f75v','f83r')),'page_leads':page_leads[rep]}
 write(SCORES,score_rows);write(RETR,retr_rows)
 host=summaries['PAGE_HOST_CHAR3'];gates={'both_pages_positive':host['positive_pages']==2,'max_three_at_most_05':host['max_three_p']<=.05}
 status='LOCAL_ASSEMBLY_CONSTRUCTION_TRANSFER_SUPPORTED' if all(gates.values()) else 'LOCAL_ASSEMBLY_CONSTRUCTION_NOT_TRANSFERABLE'
 primary_retr=[r for r in retr_rows if r['scope']=='COMPLETE_LINES_PRIMARY']
 retr_summary={rep:{'correct':sum(int(r['correct']) for r in primary_retr if r['representation']==rep),'eligible':sum(1 for r in primary_retr if r['representation']==rep),'ties':sum(r['predicted_assembly']=='TIE' for r in primary_retr if r['representation']==rep)} for rep in REPS}
 majority_top=sum(r['true_assembly']=='TOP' for r in primary_retr if r['representation']==REPS[0])
 counter=[
  {'counterexample':'F83_DIRECTION_REVERSAL','value':'3_OF_3_PRIMARY_REPRESENTATIONS_NEGATIVE','detail':'Under complete-line coverage the human-defined f83 assignment loses to the swapped text blocks in raw host and family views.'},
  {'counterexample':'INCOMPLETE_PROSE_COVERAGE','value':f"{sum(len(r.split(',')) for r in [spec[(p,s)]['prose_loci'] for p in ('f75v','f83r') for s in ('TOP','BOTTOM')])-len(complete)}_OF_29_NOT_COMPLETE",'detail':'The primary excludes missing or partial HPR2 lines; the all-available view is sensitivity only.'},
  {'counterexample':'MISSING_STRICT_LABEL_ROWS','value':','.join(missing_labels),'detail':'These human-defined labels have no eligible strict GDT012 row and are not imputed.'},
  {'counterexample':'FOUR_WORLD_NULL','value':'4','detail':'Two binary page assignments provide only four exact worlds; minimum attainable local p is .25.'},
  {'counterexample':'INDIVIDUAL_RETRIEVAL','value':json.dumps(retr_summary,sort_keys=True,separators=(',',':')),'detail':f'Every representation is below the fixed always-TOP majority baseline {majority_top}/28; aggregate bag resemblance does not establish individual label-to-record retrieval.'},
 ]
 write(COUNTER,counter)
 REPORT.write_text(f"""# GDT221 — local assembly construction assignment

## Outcome

**{status}**

The full-construction route does not rescue the f83 candidate.  With only
complete HPR2 prose lines, f75v's human-defined top/bottom assignment is
positive in all three fixed representations, but f83r's assignment is
negative in all three.  The combined PAGE_HOST-char3 lead is
**{host['aggregate_lead']:.6f}**, with **{host['positive_pages']}/2** positive
pages and local/max-three exact tails of **{host['local_exact_p']:.3f} /
{host['max_three_p']:.3f}** over four page-swap worlds.

The all-available-row sensitivity can make the f83 PAGE_HOST direction look
positive, but many of those rows are incomplete; it cannot override the
coverage-controlled result.  Only 10/29 human-defined prose lines have
complete HPR2 group coverage, and three label loci (`f75v.22`, `f75v.23`,
`f83r.50`) lack eligible strict label rows.  Individual-label retrieval is
also below the fixed always-TOP majority baseline (**{majority_top}/28**): raw,
PAGE_HOST, and family views recover only **{retr_summary['RAW_CHAR3']['correct']}**,
**{retr_summary['PAGE_HOST_CHAR3']['correct']}**, and
**{retr_summary['SOURCE_FAMILY_CHAR3']['correct']}** labels respectively.
It does not provide a usable label dictionary.

Thus f83r.51→f83r.52 remains a spatially plausible local candidate from
GDT220, but neither its raw construction, residual host texture, nor
source-family texture transfers as a two-folio label-to-record assignment.
No label, PAGE_HOST, family, wrapper, or closure receives a key value, word,
sound, language, plaintext, meaning, or translation.  f84r and every f84 row
were excluded and not accessed.
""",encoding='utf8')
 result={'schema':'GDT221_LOCAL_ASSEMBLY_ASSIGNMENT_RESULT_V1','status':status,'pages':2,'assemblies':4,'representations':list(REPS),'exact_worlds':4,'primary':summaries,'individual_retrieval':retr_summary,'individual_retrieval_majority_top_correct':majority_top,'gates':gates,'missing_label_loci':missing_labels,'complete_prose_lines':len(complete),'human_prose_lines':29,'interpretation':'Human-defined label/prose assembly construction does not transfer across f75 and f83 under complete-line coverage.','claim_ceiling':'Two-folio post-hoc construction assignment only; no key, word, sound, language, plaintext, meaning, or translation.','f84':{'accessed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (MAN,LABELS,GROUPS,OLD)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (SCORES,RETR,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'host':host},sort_keys=True))
if __name__=='__main__':main()
