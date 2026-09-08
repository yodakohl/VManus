#!/usr/bin/env python3
"""Independent direct label-by-running-window enumeration and analytic fixture."""
import argparse,csv,hashlib,importlib.util,json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1]
R=next(p for p in B.parents if (p/'AGENTS.md').is_file() and (p/'.git').exists())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def word(g):
 x=g['ivtff_group_raw'];return g['clean_ascii_fragment_count']=='1' and x==g['clean_ascii_fragments'] and x.isascii() and x.isalpha() and x.islower()
def valid(gs):
 if not gs or not all(word(g) for g in gs):return False
 for k in range(1,len(gs)):
  for x in [gs[k-1]['right_separator'],gs[k]['left_separator']]:
   if x=='UNCERTAIN_SMALL_SPACE' or x[:8]=='DRAWING_':return False
 return True
def leaf(p):return re.fullmatch(r'(f\d+)[rv]\d*',p).group(1)
def audit(lines,atlas,s,result,candidates,bridges):
 meta={m['locus']:m for m in lines};assert len(meta)==len(lines)==s['expected_metadata_loci']
 assert {m['source_selector'] for m in lines}==set(s['selectors'])
 gr={};ids=set()
 for row in atlas:
  assert row['page'] in s['selectors'] and not row['page'].startswith('f84');assert row['source_group_id'] not in ids;ids.add(row['source_group_id'])
  if row['edition'] in s['editions']:gr.setdefault((row['edition'],row['locus']),[]).append(row)
 for (e,loc),gs in gr.items():
  gs.sort(key=lambda x:int(x['source_group_index']));assert {int(x['source_group_count']) for x in gs}=={len(gs)}
  assert [int(x['source_group_index']) for x in gs]==list(range(1,len(gs)+1));assert len({x['source_row_index'] for x in gs})==1
  if loc in meta:assert {x['page'] for x in gs}=={meta[loc]['source_selector']}
 expected_candidates=[];expected_hits=[]
 for e in s['editions']:
  for loc,m in meta.items():
   if m['line_kind']!=s['local_kind']:continue
   gs=gr.get((e,loc),[]);ok=len(gs)>=2 and valid(gs)
   expected_candidates.append(dict(edition=e,local_locus=loc,selector=m['source_selector'],page_key=m['physical_page'],raw_group_count=len(gs),groups=[x['ivtff_group_raw'] for x in gs],eligible=ok,reason='ELIGIBLE' if ok else 'MISSING_RAW' if not gs else 'SINGLE_GROUP' if len(gs)<2 else 'RAW_GROUP_OR_INTERNAL_SEPARATOR'))
   if not ok:continue
   pattern=[x['ivtff_group_raw'] for x in gs];n=len(gs)
   for target,tm in meta.items():
    if tm['line_kind']!=s['running_kind']:continue
    run=gr.get((e,target),[])
    for start in range(0,len(run)-n+1):
     window=run[start:start+n]
     if [x['ivtff_group_raw'] for x in window]!=pattern or not valid(window):continue
     expected_hits.append(dict(edition=e,local_locus=loc,local_selector=m['source_selector'],running_locus=target,running_selector=tm['source_selector'],local_page_key=m['physical_page'],running_page_key=tm['physical_page'],same_page_key=m['physical_page']==tm['physical_page'],start_group=start+1,group_length=n,running_group_count=len(run),groups=pattern,running_raw_kind=run[0]['kind'],same_selector=m['source_selector']==tm['source_selector'],same_physical_leaf=leaf(m['source_selector'])==leaf(tm['source_selector'])))
 def canonical(x):return json.dumps(x,sort_keys=True)
 assert sorted(map(canonical,candidates))==sorted(map(canonical,expected_candidates))
 assert sorted(map(canonical,bridges))==sorted(map(canonical,expected_hits))
 assert result['metadata_records']==len(meta) and result['metadata_line_kinds']==dict(Counter(m['line_kind'] for m in lines))
 for e in s['editions']:
  local=[x for x in expected_candidates if x['edition']==e];eligible=[x for x in local if x['eligible']];hits=[x for x in expected_hits if x['edition']==e]
  missing=sorted(loc for loc,m in meta.items() if int(m['token_count'])>0 and (e,loc) not in gr)
  if e==s['editions'][0]:assert not missing
  assert sorted(result['views'][e]['missing_nonempty_raw_loci'])==missing
  assert result['raw_loci_outside_metadata'][e]==sorted(loc for ee,loc in gr if ee==e and loc not in meta)
  v=result['views'][e]
  checks={'local_records':len(local),'eligible_local_records':len(eligible),'eligible_distinct_patterns':len({tuple(c['groups']) for c in eligible}),'running_records':sum(m['line_kind']==s['running_kind'] for m in lines),'bridge_references':len(hits),'matched_local_records':len({h['local_locus'] for h in hits}),'matched_distinct_patterns':len({tuple(h['groups']) for h in hits}),'unique_running_windows':len({(h['running_locus'],h['start_group'],h['group_length']) for h in hits}),'same_page_key_references':sum(h['same_page_key'] for h in hits),'same_selector_references':sum(h['same_selector'] for h in hits),'other_physical_leaf_references':sum(not h['same_physical_leaf'] for h in hits),'running_raw_kinds':dict(Counter(h['running_raw_kind'] for h in hits))}
  for k,x in checks.items():assert v[k]==x,(e,k)
  lengths={len(c['groups']) for c in eligible};assert set(v['running_opportunities_by_length'])=={str(n) for n in lengths}
  for n in lengths:
   raw=good=0
   for loc,m in meta.items():
    if m['line_kind']!=s['running_kind']:continue
    gs=gr.get((e,loc),[]);raw+=max(0,len(gs)-n+1);good+=sum(valid(gs[j:j+n]) for j in range(len(gs)-n+1))
   assert v['running_opportunities_by_length'][str(n)]=={'raw_windows':raw,'eligible_windows':good}
 def key(h):return (h['local_locus'],h['running_locus'],h['start_group'],h['group_length'],h['running_group_count'])
 lookup={e:{key(h):h for h in expected_hits if h['edition']==e} for e in s['editions']}
 common=[]
 for k,h in lookup[s['editions'][0]].items():
  if not all(k in lookup[e] for e in s['editions']):continue
  patterns={e:lookup[e][k]['groups'] for e in s['editions']}
  common.append(dict(local_locus=k[0],running_locus=k[1],start_group=k[2],group_length=k[3],running_group_count=k[4],literal_same_candidate=len({tuple(x) for x in patterns.values()})==1,reading_groups=patterns))
 assert sorted(map(canonical,common))==sorted(map(canonical,result['same_index_three_reading_bridges']))
 assert sorted(map(canonical,result['focal_records']))==sorted(canonical(c) for c in expected_candidates if c['local_locus']==s['focal_locus'])
 assert sorted(map(canonical,result['focal_bridges']))==sorted(canonical(h) for h in expected_hits if h['local_locus']==s['focal_locus'])
 return {'local_records_checked':len(expected_candidates),'bridges_checked':len(expected_hits),'same_index_bridges_checked':len(common)}

def fixture(module):
 s=dict(experiment_id='SYNTHETIC',editions=['ZL3b','IT2a','RF1b'],selectors=['f1r','f2r','f3r'],expected_metadata_loci=6,local_kind='LOCAL_LABEL_OR_MARKER',running_kind='RUNNING_PROSE',focal_locus='f1r.1')
 layout=[('f1r.1','L',2),('f1r.2','L',2),('f1r.3','L',1),('f1r.4','L',2),('f2r.1','P',5),('f3r.1','P',2)]
 lines=[dict(locus=loc,source_selector=loc.split('.')[0],physical_page=loc.split('.')[0],line_kind=s['local_kind'] if k=='L' else s['running_kind'],token_count=str(n)) for loc,k,n in layout];atlas=[]
 for e in s['editions']:
  second='cc' if e=='IT2a' else 'bb'
  for row,(loc,k,n) in enumerate(layout):
   vals=['aa',second] if n==2 else ['aa'] if n==1 else ['aa',second,'zz','aa',second]
   if loc=='f1r.4':vals=['aa','bb!']
   if loc=='f3r.1' and e=='IT2a':vals=['aa','zz']
   for j,v in enumerate(vals):
    atlas.append(dict(source_group_id=f'{e}:{loc}:{j}',edition=e,locus=loc,page=loc.split('.')[0],kind=k,source_row_index=str(row),source_group_index=str(j+1),source_group_count=str(n),left_separator='SPACE',right_separator='DRAWING_GAP' if loc=='f2r.1' and j==3 else 'SPACE',ivtff_group_raw=v,clean_ascii_fragments=v.replace('!',''),clean_ascii_fragment_count='1'))
 result,cs,hs=module.calculate(lines,atlas,s);audit(lines,atlas,s,result,cs,hs)
 assert [result['views'][e]['bridge_references'] for e in s['editions']]==[4,2,4]
 assert all(result['views'][e]['running_opportunities_by_length']['2']=={'raw_windows':5,'eligible_windows':4} for e in s['editions'])
 assert len(result['same_index_three_reading_bridges'])==2 and not any(x['literal_same_candidate'] for x in result['same_index_three_reading_bridges'])
 return {'status':'PASS','expected_bridge_references':[4,2,4],'same_index_bridges':2,'literal_same_bridges':0,'raw_windows':5,'eligible_windows':4}

def main():
 p=argparse.ArgumentParser();p.add_argument('--synthetic-only',action='store_true');a=p.parse_args()
 spec=importlib.util.spec_from_file_location('g874_builder',B/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 synthetic=fixture(mod)
 if a.synthetic_only:print(json.dumps(synthetic));return
 s=json.loads((B/'src/SPEC.json').read_text());receipt=json.loads((B/'artifacts/SOURCE_RECEIPTS.json').read_text());data={}
 for d in s['sources']:
  row=next(x for x in receipt if x['name']==d['name']);path=B/'runtime'/f"{d['name']}.tsv"
  assert row['source']==d['path'] and row['source_sha256']==d['sha256']==digest(R/d['path'])
  assert row['projection_sha256']==digest(path) and row['allow_values']==s['selectors'] and row['columns']==d['columns'] and row['selector']==d['selector']
  with path.open() as f:data[d['name']]=list(csv.DictReader(f,delimiter='\t'))
  assert len(data[d['name']])==row['rows']
 result=json.loads((B/'artifacts/RESULT.json').read_text());cs=json.loads((B/'artifacts/CANDIDATES.json').read_text());hs=json.loads((B/'artifacts/BRIDGES.json').read_text())
 checks=audit(data['LINES'],data['ATLAS'],s,result,cs,hs)
 out=dict(status='PASS',scope='Independent label/window enumeration, coverage, component counts and coordinate joins; no semantic validation.',synthetic=synthetic,checks=checks,input_hashes={str(x.relative_to(B)):digest(x) for x in [B/'src/run.py',B/'src/validate.py',B/'src/SPEC.json',B/'artifacts/RESULT.json',B/'artifacts/CANDIDATES.json',B/'artifacts/BRIDGES.json']})
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
