import csv,json,hashlib,re
from pathlib import Path
from collections import Counter
D=Path(__file__).parent;s=json.loads((D/'SPEC.json').read_text())
def read(p):return json.loads(Path(p).read_text())
def table(n,rows,cols):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rows)
for p,h in s['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
allowed=set(read(s['allow_source'])['allowed_selectors']);paras=read(s['paragraphs']);pindex={}
for ed,pp in paras.items():
 for p in pp:
  for line in p['lines']:pindex[ed,line['locus']]=p
roles={}
for branch,p in s['roles'].items():
 rr={}
 for r in csv.DictReader(Path(p).open(),delimiter='\t'):
  assert r['form'] not in rr or rr[r['form']]==r['role'];rr[r['form']]=r['role']
 roles[branch]=rr
features={r['form']:(r['axis'],r['value']) for r in read(s['feature_source'])['features'] if r['kind']=='STANDALONE'}
materials=set(read(s['material_source'])['material_roles']);candidates=read(s['candidate_source'])['candidates']
occ=[];patterns=[];pred=[];contexts=[];kept={};counts=Counter()
for src in s['sources']:
 data=read(src)
 for line in data['lines']:
  m=line['metadata'];ed=m['edition'];assert m['page'] in allowed and not m['page'].startswith('f84')
  counts[ed,'lines']+=1;counts[ed,'groups']+=len(line['groups'])
  gs=[dict(zip(data['group_columns'],g)) for g in line['groups']];words=[g['ivtff_group_raw'] for g in gs]
  hits=[i for i,w in enumerate(words) if w==s['target']]
  if not hits:continue
  leaf=int(re.match(r'f(\d+)',m['page'])[1]);partition='MOTIVATION' if leaf in s['motivation_leaves'] else 'OTHER_EXPOSED'
  p=pindex.get((ed,m['locus']));pid=p['id'] if p else 'NO_COMPLETE_PARAGRAPH'
  contexts.append(dict(source=src,metadata=m,groups=gs,paragraph=pid))
  if p:kept[ed,pid]=dict(edition=ed,**p)
  for i in hits:
   counts[ed,'hits']+=1;found=0
   for branch,rr in roles.items():
    for typ,indices in [('M_A_S',[i-1,i,i+1]),('A_M_S',[i,i+1,i+2])]:
     if min(indices)<0 or max(indices)>=len(gs):continue
     ww=[words[j] for j in indices];mi=0 if typ=='M_A_S' else 1
     if rr.get(ww[mi]) not in materials or rr.get(ww[2])!='STATE' or ww[2] not in features:continue
     seam=all(gs[a]['right_separator']==gs[b]['left_separator']=='DEFINITE_SPACE' and int(gs[b]['source_group_index'])==int(gs[a]['source_group_index'])+1 for a,b in zip(indices,indices[1:]))
     axis,value=features[ww[2]];key=branch+'|'+gs[i]['source_group_id']+'|'+typ
     r=dict(case=key,edition=ed,page=m['page'],leaf=leaf,partition=partition,paragraph=pid,locus=m['locus'],target_id=gs[i]['source_group_id'],branch=branch,pattern=typ,material=ww[mi],state_word=ww[2],axis=axis,value=value,definite=seam,raw_pattern=' '.join(ww))
     patterns.append(r);found+=1
     for name,(ca,cv) in candidates.items():
      for timing in ['O','I']:
       status='UNCERTAIN_SEAM' if not seam else 'NO_OUTPUT_TEST' if timing=='I' else 'UNKNOWN' if ca!=axis else 'MATCH' if cv==value else 'CONFLICT' if {cv,value} in ({'wet','dry'},{'cold','warm'},{'cold','hot'}) else 'DIFFERENT_NOT_OPPOSED'
       pred.append(dict(case=key,candidate=name,predicted_axis=ca,predicted_value=cv,timing=timing,status=status))
   occ.append(dict(edition=ed,page=m['page'],leaf=leaf,locus=m['locus'],source_id=gs[i]['source_group_id'],partition=partition,paragraph=pid,patterns=found,raw_line=' '.join(words)))
table('OCCURRENCES.tsv',occ,['edition','page','leaf','locus','source_id','partition','paragraph','patterns','raw_line'])
table('PATTERNS.tsv',patterns,['case','edition','page','leaf','partition','paragraph','locus','target_id','branch','pattern','material','state_word','axis','value','definite','raw_pattern'])
table('PREDICTIONS.tsv',pred,['case','candidate','predicted_axis','predicted_value','timing','status'])
(D/'CONTEXTS.json').write_text(json.dumps(dict(lines=contexts,paragraphs=list(kept.values())),ensure_ascii=False,separators=(',',':'))+'\n')
lines=['# W47 vollständige sheey-Kontexte','', 'Alle deutschen Rollen und Werte bleiben Annahmen. Vollständige Absätze, soweit GDT928 sie trägt; sonst ganze Quellzeilen.','']
for p in kept.values():
 lines+=['## '+p['edition']+' '+p['id'],'']+[l['locus']+' `'+ ' '.join(l['words'])+'`' for l in p['lines']]+['']
for l in contexts:
 if l['paragraph']=='NO_COMPLETE_PARAGRAPH':lines += [l['metadata']['edition']+' '+l['metadata']['locus']+' `'+ ' '.join(g['ivtff_group_raw'] for g in l['groups'])+'`']
(D/'CONTEXTS.md').write_text('\n'.join(lines)+'\n')
result={}
result['counts']={ed:{k:counts[ed,k] for k in ['lines','groups','hits']} for ed in ['ZL3b','IT2a','RF1b']}
result.update(distinct_source_lines=len({r['locus'] for r in occ}),reading_union_index_pairs=len({(r['locus'],r['source_id'].split('|')[-1]) for r in occ}),index_pairs_are_not_native_aligned=True,physical_leaves=sorted({r['leaf'] for r in occ}),patterns=len(patterns),safe_patterns=sum(r['definite'] for r in patterns),predictions=len(pred),complete_paragraphs=len(kept),status_counts=dict(Counter(r['status'] for r in pred)),independent_meaning_confirmations=0)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

summary=[dict(candidate=c,predicted_axis=a,predicted_value=v,motivation_cases=sum(x['partition']=='MOTIVATION' and x['definite'] for x in patterns),other_exposed_cases=sum(x['partition']=='OTHER_EXPOSED' and x['definite'] for x in patterns),decision='NO_ELIGIBLE_TEST' if not patterns else 'SEE_ALL_PREDICTIONS',independent_confirmations=0) for c,(a,v) in candidates.items()]
table('CANDIDATES.tsv',summary,['candidate','predicted_axis','predicted_value','motivation_cases','other_exposed_cases','decision','independent_confirmations'])
