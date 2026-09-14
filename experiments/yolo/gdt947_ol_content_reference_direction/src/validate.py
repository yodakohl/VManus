#!/usr/bin/env python3
"""Independent raw-source reconstruction of every frozen direction obligation."""
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def tab(n):
 with (E/'artifacts'/n).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 lock=read(E/'PREREG_LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 m=read(E/'src/MODEL.json');allow=set(read(R/m['allow_source'])['allowed_selectors'])
 assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
 source={};lines={}
 for p in m['sources']:
  d=read(R/p)
  for l in d['lines']:
   meta=l['metadata'];assert meta['page'] in allow
   rr=[meta|dict(zip(d['group_columns'],g)) for g in l['groups']]
   k=(meta['edition'],meta['locus']);assert k not in lines;lines[k]=rr
   for r in rr:
    sid=r['source_group_id'];assert sid not in source;source[sid]=r
 paragraphs=read(R/m['paragraph_source']);by_group={};pcount={}
 for ed,pp in paragraphs.items():
  pcount[ed]=len(pp)
  for p in pp:
   assert p['page'] in allow and p['lines'][0]['start'] and p['lines'][-1]['end']
   ns=[int(l['locus'].rsplit('.',1)[1]) for l in p['lines']]
   assert all(b==a+1 for a,b in zip(ns,ns[1:]))
   flat=[]
   for l in p['lines']:
    rr=lines[ed,l['locus']]
    assert l['words']==[r['ivtff_group_raw'] for r in rr]
    assert l['source_ids']==[r['source_group_id'] for r in rr]
    assert l['start']==(rr[0]['paragraph_start']=='1') and l['end']==(rr[0]['paragraph_end']=='1')
    flat.extend(rr)
   assert len(flat)==p['groups']
   for i,r in enumerate(flat):
    sid=r['source_group_id'];assert sid not in by_group;by_group[sid]=(p,flat,i)
 words=m['primary_forms']|m['family_diagnostics'];bound=set(m['definite_boundaries'])
 def definite(r):return r['left_separator'] in bound and r['right_separator'] in bound
 expected={sid:r for sid,r in source.items() if r['ivtff_group_raw'] in words}
 occ=tab('OCCURRENCES.tsv');assert len(occ)==len(expected) and {r['source_group_id'] for r in occ}==set(expected)
 for x in occ:
  r=expected[x['source_group_id']]
  for k in ['edition','page','locus','left_separator','right_separator']:assert x[k]==r[k],(x,k)
  assert x['form']==r['ivtff_group_raw'] and x['core']==words[x['form']]
  assert int(x['physical_leaf'])==int(re.match(r'f(\d+)',r['page'])[1])
  pid=by_group[x['source_group_id']][0]['id'] if x['source_group_id'] in by_group else ''
  assert x['paragraph_id']==pid
 cases=tab('CASES.tsv');observed={(c['source_group_id'],c['direction']):c for c in cases}
 assert len(cases)==len(observed)==2*len(expected)
 assert set(observed)=={(sid,d) for sid in expected for d in m['directions']}
 totals=Counter();strong=[]
 for sid,r in expected.items():
  for direction in m['directions']:
   c=observed[sid,direction];anchors=[];uncertain=[]
   if sid not in by_group:status='NO_PARAGRAPH_CAPACITY'
   elif not definite(r):status='TARGET_BOUNDARY_UNCERTAIN'
   else:
    p,flat,i=by_group[sid];side=flat[:i] if direction=='BACK' else flat[i+1:]
    anchors=[z['source_group_id'] for z in side if z['ivtff_group_raw']==words[r['ivtff_group_raw']] and definite(z)]
    uncertain=[z['source_group_id'] for z in side if re.fullmatch('[a-z]+',z['ivtff_group_raw']) is None or not definite(z)]
    status='WRITTEN_ANCHOR_PRESENT' if anchors else 'UNRESOLVED_SOURCE' if uncertain else 'MISSING_WRITTEN_ANCHOR'
   assert c['status']==status,(sid,direction,c['status'],status)
   assert c['anchor_ids']== '|'.join(anchors),(sid,direction,'anchors')
   assert c['uncertainty_ids']== '|'.join(uncertain),(sid,direction,'uncertainty')
   totals[status]+=1
   if status=='MISSING_WRITTEN_ANCHOR':strong.append((sid,direction))
 # Independently verify preserved whole source lines and paragraph coverage.
 target_loci={r['locus'] for r in expected.values()}
 sc=read(E/'artifacts/SOURCE_CONTEXT.json')
 wanted={f'{ed}|{locus}':rr for (ed,locus),rr in lines.items() if locus in target_loci}
 assert set(sc)==set(wanted)
 for key,rr in wanted.items():assert sc[key]['groups']==rr,key
 pc=read(E/'artifacts/PARAGRAPH_CONTEXT.json')
 want_p={(r['edition'],by_group[sid][0]['id']) for sid,r in expected.items() if sid in by_group}
 assert {(p['edition'],p['paragraph_id']) for p in pc}==want_p
 for p in pc:
  for line in p['lines']:assert line['groups']==lines[p['edition'],line['locus']]
 for s in tab('SUMMARY.tsv'):
  rr=[c for c in cases if all(c[k]==s[k] for k in ['form','edition','direction','exposure'])]
  ct=Counter(c['status'] for c in rr)
  assert int(s['occurrence_count'])==len(rr)
  for state in ['NO_PARAGRAPH_CAPACITY','TARGET_BOUNDARY_UNCERTAIN','WRITTEN_ANCHOR_PRESENT','UNRESOLVED_SOURCE','MISSING_WRITTEN_ANCHOR']:
   assert int(s[state.lower()])==ct[state]
  if ct['MISSING_WRITTEN_ANCHOR']:assert s['decision']=='REJECT_MISSING_WRITTEN_ANCHOR'
 cd=tab('CANDIDATE_DECISIONS.tsv')
 assert len(cd)==6 and {(d['candidate'],d['direction']) for d in cd}=={(f,d) for f in list(m['primary_forms'])+['JOINT_PRIMARY'] for d in m['directions']}
 for d in cd:
  forms=set(m['primary_forms']) if d['candidate']=='JOINT_PRIMARY' else {d['candidate']}
  cc=[c for c in cases if c['form'] in forms and c['direction']==d['direction']]
  ct=Counter(c['status'] for c in cc)
  assert int(d['occurrence_count'])==len(cc) and d['meaning_confirmed']=='FALSE'
  for state in ['NO_PARAGRAPH_CAPACITY','TARGET_BOUNDARY_UNCERTAIN','WRITTEN_ANCHOR_PRESENT','UNRESOLVED_SOURCE','MISSING_WRITTEN_ANCHOR']:
   assert int(d[state.lower()])==ct[state]
  if ct['MISSING_WRITTEN_ANCHOR']:assert d['decision']=='REJECT_MISSING_WRITTEN_ANCHOR'
 result=read(E/'artifacts/RESULT.json')
 assert result['confirmed_words']==result['independent_meaning_tests']==0 and result['significance_claim'] is False
 from run import build
 saved={p.name:p.read_bytes() for p in (E/'artifacts').iterdir() if p.is_file()}
 built=build()
 assert saved=={p.name:p.read_bytes() for p in (E/'artifacts').iterdir() if p.is_file()},'build replay must not mutate artifacts'
 if isinstance(built,dict):
  for name,value in built.items():
   if isinstance(value,str):assert (E/'artifacts'/name).read_text()==value,name
 from present import build as present
 assert (E/'artifacts/CANDIDATES.md').read_text()==present()
 result={'experiment':'GDT947','status':'PASS','source_groups':len(source),'own_complete_paragraphs':pcount,'exact_occurrences':len(expected),'direction_cases':len(cases),'case_statuses':dict(totals),'strict_missing_anchor_cases':len(strong),'checks':['all preregistration/model/input hashes','179-selector safe snapshot boundaries and source uniqueness','own-reader complete paragraph boundaries/contiguity and every raw source ID','every exact target occurrence, including no-capacity RF and non-paragraph hits','independent reconstruction of every directional status and full anchor/uncertainty ID lists','whole target lines including alternate-reader nonmatches, full target paragraphs','summary contradictions cannot be masked by missing source cases','deterministic read-only artifact replay'],'meaning_validation':False,'independent_meaning_tests':0,'significance_claim':False}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
