"""Metadata-only diagnosis after the original reader stopped before fitting."""
import csv,json
from collections import defaultdict,Counter
from run import ROOT,E,ALLOW,ATLAS,RAW,FRAMECOLS,query,number
pages=[r['page'] for r in csv.DictReader((ROOT/ALLOW).open(),delimiter='\t')]
frames,g1=query(ATLAS,'page',pages,FRAMECOLS)
rows,g2=query(RAW,'page',pages,'edition,locus,page,kind,source_group_index,paragraph_start,paragraph_end')
lines=defaultdict(dict)
for r in rows:
 if r['source_group_index']=='1':lines[r['edition'],r['page']][r['locus']]=r
issues=[];markers=Counter()
for f in frames:
 lo,hi=int(f['start_line_number']),int(f['end_line_number'])
 selected={e:sorted((r for l,r in lines[e,f['page']].items() if lo<=number(l)<=hi),key=lambda r:number(r['locus'])) for e in ['ZL3b','IT2a','RF1b']}
 zl=selected['ZL3b'];reasons=[]
 if len(zl)!=int(f['source_line_count']):reasons.append('ZL_ALL_KIND_COUNT_MISMATCH')
 if not zl or zl[0]['locus']!=f['start_locus'] or zl[-1]['locus']!=f['end_locus']:reasons.append('ZL_ENDPOINT_MISMATCH')
 if zl and (zl[0]['paragraph_start']!='1' or zl[-1]['paragraph_end']!='1'):reasons.append('ZL_BOUNDARY_MISMATCH')
 if any(r['kind']!='P' for r in zl):reasons.append('MIXED_NON_P')
 for e,rs in selected.items():
  markers[e+':start']+=sum(r['paragraph_start']=='1' for r in rs)
  markers[e+':end']+=sum(r['paragraph_end']=='1' for r in rs)
  extra=set(r['locus'] for r in rs)-set(r['locus'] for r in zl)
  if extra:reasons.append(e+':EXTRA_LOCUS')
 if reasons:issues.append(dict(paragraph_id=f['paragraph_id'],page=f['page'],reasons=reasons,rows=selected))
result=dict(status='METADATA_DIAGNOSIS_NO_FIT',original_prereg_commit='e56225bd',frame_count=len(frames),guards=[g1,g2],marker_counts=dict(markers),issue_counts=dict(Counter(r for x in issues for r in x['reasons'])),issues=issues)
(E/'artifacts/METADATA_AUDIT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['guards','issues']},sort_keys=True))
