#!/usr/bin/env python3
"""Independent guarded source, native interval and fixed-obligation validation."""
import csv,hashlib,io,json,subprocess
from collections import Counter,defaultdict
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in BASE.parents if (p/'AGENTS.md').is_file())
def get(p):return json.loads((BASE/p).read_text())
lock=get('PREREG_LOCK.json')
for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
m=get('src/MODEL.json');packet=get('artifacts/RETAINED_SOURCE.json');rs=packet['projected_rows']
cmd=[str(ROOT/'vmanus-exp'),'query-tsv','experiments/semantic_assumptions/results/source_separator_transcription.tsv','--selector','page','--columns',','.join(rs[0])]
for page in m['pages']:cmd+=['--allow',page]
source=list(csv.DictReader(io.StringIO(subprocess.check_output(cmd,cwd=ROOT,text=True)),delimiter='\t'))
assert source==rs and len(source)==2312
assert len({r['source_group_id'] for r in rs})==len(rs)
pages=defaultdict(list)
for r in source:
 assert r['page'] in m['pages'] and not r['page'].startswith('f84')
 if r['kind']=='P':pages[r['edition'],r['page']].append(r)
intervals={};where={}
for (e,page),groups in pages.items():
 groups.sort(key=lambda r:(int(r['source_row_index']),int(r['source_group_index'])))
 starts=[i for i,r in enumerate(groups) if r['paragraph_start']=='1' and r['source_group_index']=='1']
 ends=[i for i,r in enumerate(groups) if r['paragraph_end']=='1' and r['source_group_index']==r['source_group_count']]
 for end in ends:
  eligible=[i for i in starts if i<=end]
  if not eligible:continue
  start=max(eligible);span=groups[start:end+1]
  loci=list(dict.fromkeys(r['locus'] for r in span));ns=[int(l.rsplit('.',1)[1]) for l in loci]
  if ns!=list(range(ns[0],ns[-1]+1)):continue
  uid=e+'|'+page+'|'+loci[0]+'-'+loci[-1];intervals[uid]=span
  for i,r in enumerate(span):assert r['source_group_id'] not in where;where[r['source_group_id']]=(uid,i)
cases=list(csv.DictReader((BASE/'artifacts/CANDIDATE_CASES.tsv').open(),delimiter='\t'))
occ=list(csv.DictReader((BASE/'artifacts/OCCURRENCES.tsv').open(),delimiter='\t'))
matches=[r for r in source if r['kind']=='P' and r['ivtff_group_raw'] in m['selectors']]
assert len(matches)==42 and len(occ)==42 and len(cases)==84
assert Counter(r['source_group_id'] for r in matches)==Counter(r['source_group_id'] for r in occ)
byid={r['source_group_id']:r for r in matches}
assert len({(c['source_group_id'],c['candidate']) for c in cases})==len(cases)
for c in cases:
 r=byid[c['source_group_id']];b=where.get(r['source_group_id'])
 rule=m['candidates'][c['candidate']];need=rule['free_s_right'] if r['ivtff_group_raw']=='s' else rule['derived_right']
 assert int(c['required_right'])==need
 if b:
  uid,i=b;right=intervals[uid][i+1:i+1+need]
  assert c['unit_id']==uid and int(c['unit_position'])==i+1
  assert int(c['available_right'])==len(intervals[uid])-i-1
  expect='CAPACITY_COMPATIBLE' if len(right)==need else 'CONTRADICTION'
 else:
  right=[];expect='NOT_TESTABLE';assert not c['unit_id']
 assert c['outcome']==expect
 assert c['right_ids']=='|'.join(x['source_group_id'] for x in right)
 assert c['right_raw']=='|'.join(x['ivtff_group_raw'] for x in right)
assert {u['id'] for u in packet['matched_native_units']}=={where[r['source_group_id']][0] for r in matches if r['source_group_id'] in where}
for u in packet['matched_native_units']:
 assert u['groups']==intervals[u['id']]
 assert [r for line in u['lines'] for r in line]==u['groups']
result=get('artifacts/RESULT.json')
assert result['native_units_by_reader']=={e:sum(uid.startswith(e+'|') for uid in intervals) for e in m['editions']}
assert result['occurrences_by_reader']=={e:sum(r['edition']==e for r in matches) for e in m['editions']}
for cid in m['candidates']:
 cc=[c for c in cases if c['candidate']==cid];bad=[c for c in cc if c['outcome']=='CONTRADICTION']
 assert result['candidates'][cid]['by_reader']=={e:dict(Counter(c['outcome'] for c in cc if c['edition']==e)) for e in m['editions']}
 assert result['candidates'][cid]['decision']==('REJECT_FIXED_PACKAGE' if bad else 'NO_SURFACE_REFUTATION_MEANING_UNSELECTED')
bad=[c for c in cases if c['outcome']=='CONTRADICTION']
assert len(bad)==2 and {c['locus'] for c in bad}=={'f29v.12'} and {c['candidate'] for c in bad}=={'SOURCE_HEAD'}
assert all(c['right_raw']=='y' and c['available_right']=='1' for c in bad)
assert result['confirmed_words']==result['independent_confirmation_leaves']==0 and not result['significance_claim']
receipt={'status':'PASS_FIXED_SOURCE_AND_CAPACITY_ONLY','source_groups':len(source),'occurrences':len(matches),'candidate_rows':len(cases),'contradiction_physical_loci':['f29v.12'],'rf_native_units':0,'meaning_validated':False,'run_imported':False}
(BASE/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
