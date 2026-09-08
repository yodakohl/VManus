#!/usr/bin/env python3
"""One guarded raw local-record bridge census; no semantic scoring."""
import csv, hashlib, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file() and (p/'.git').exists())
BASE=Path(__file__).resolve().parents[1]
SPEC=BASE/'src/SPEC.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x,compact=False):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=None if compact else 2,separators=(',',':') if compact else None)+'\n')
def bad(x): return x=='UNCERTAIN_SMALL_SPACE' or x.startswith('DRAWING_')
def clear(g): return g['clean_ascii_fragment_count']=='1' and g['ivtff_group_raw']==g['clean_ascii_fragments'] and bool(re.fullmatch('[a-z]+',g['ivtff_group_raw']))
def clean_window(gs): return bool(gs) and all(clear(g) for g in gs) and all(not bad(a['right_separator']) and not bad(b['left_separator']) for a,b in zip(gs,gs[1:]))
def leaf(x):
 m=re.match(r'^(f\d+)[rv]',x);assert m,x;return m.group(1)
def source(s):
 assert s['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'} and len(set(s['selectors']))==35
 assert not any(p.startswith('f84') for p in s['selectors'])
 assert sha(ROOT/s['roster']['path'])==s['roster']['sha256']
 result={};receipts=[]
 for d in s['sources']:
  assert sha(ROOT/d['path'])==d['sha256']
  cmd=[str(ROOT/'vmanus-exp'),'query-tsv',d['path'],'--selector',d['selector']]
  for p in s['selectors']:cmd+=['--allow',p]
  cmd+=['--columns',','.join(d['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
  out=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
  stats=[json.loads(t[12:]) for t in out.stderr.splitlines() if t.startswith('GUARD_STATS ')]
  assert len(stats)==1
  cache=BASE/'runtime'/f"{d['name']}.tsv";cache.parent.mkdir(exist_ok=True);cache.write_text(out.stdout)
  rows=list(csv.DictReader(out.stdout.splitlines(),delimiter='\t'));assert all(r[d['selector']] in s['selectors'] for r in rows)
  result[d['name']]=rows
  receipts.append({'name':d['name'],'source':d['path'],'source_sha256':d['sha256'],'projection_sha256':sha(cache),'rows':len(rows),'selector':d['selector'],'allow_values':s['selectors'],'columns':d['columns'],'guard_stats':stats[0]})
 return result,receipts

def group_source(lines,atlas,s):
 meta={x['locus']:x for x in lines};assert len(meta)==len(lines)==s['expected_metadata_loci']
 assert set(x['source_selector'] for x in lines)==set(s['selectors'])
 groups=defaultdict(list);seen=set()
 for g in atlas:
  assert g['page'] in s['selectors'] and not g['page'].startswith('f84')
  assert g['source_group_id'] not in seen;seen.add(g['source_group_id'])
  if g['edition'] in s['editions']:groups[g['edition'],g['locus']].append(g)
 for (e,loc),gs in groups.items():
  gs.sort(key=lambda g:int(g['source_group_index']));n=len(gs)
  assert [int(g['source_group_index']) for g in gs]==list(range(1,n+1)),(e,loc)
  assert all(int(g['source_group_count'])==n for g in gs),(e,loc)
  assert len({g['source_row_index'] for g in gs})==1
  if loc in meta:assert all(g['page']==meta[loc]['source_selector'] for g in gs)
 missing={e:[loc for loc,m in meta.items() if int(m['token_count'])>0 and not groups.get((e,loc))] for e in s['editions']}
 assert not missing[s['editions'][0]],'Incomplete primary metadata/raw coverage'
 return meta,groups,missing

def calculate(lines,atlas,s):
 meta,groups,missing=group_source(lines,atlas,s);candidates=[];bridges=[];views={}
 for e in s['editions']:
  patterns=defaultdict(list);local=[]
  for loc,m in meta.items():
   if m['line_kind']!=s['local_kind']:continue
   gs=groups.get((e,loc),[]);eligible=len(gs)>=2 and clean_window(gs)
   c={'edition':e,'local_locus':loc,'selector':m['source_selector'],'page_key':m['physical_page'],'raw_group_count':len(gs),'groups':[g['ivtff_group_raw'] for g in gs],'eligible':eligible,'reason':'ELIGIBLE' if eligible else 'MISSING_RAW' if not gs else 'SINGLE_GROUP' if len(gs)<2 else 'RAW_GROUP_OR_INTERNAL_SEPARATOR'}
   local.append(c);candidates.append(c)
   if eligible:patterns[tuple(c['groups'])].append(c)
  lengths=sorted({len(p) for p in patterns});opps={str(n):{'raw_windows':0,'eligible_windows':0} for n in lengths};hits=[]
  for loc,m in meta.items():
   if m['line_kind']!=s['running_kind']:continue
   gs=groups.get((e,loc),[])
   for n in lengths:
    opps[str(n)]['raw_windows']+=max(0,len(gs)-n+1)
    for i in range(len(gs)-n+1):
     window=gs[i:i+n]
     if not clean_window(window):continue
     opps[str(n)]['eligible_windows']+=1;seq=tuple(g['ivtff_group_raw'] for g in window)
     for c in patterns.get(seq,[]):
      hits.append({'edition':e,'local_locus':c['local_locus'],'local_selector':c['selector'],'running_locus':loc,'running_selector':m['source_selector'],'local_page_key':c['page_key'],'running_page_key':m['physical_page'],'same_page_key':c['page_key']==m['physical_page'],'start_group':i+1,'group_length':n,'running_group_count':len(gs),'groups':list(seq),'running_raw_kind':gs[0]['kind'],'same_selector':c['selector']==m['source_selector'],'same_physical_leaf':leaf(c['selector'])==leaf(m['source_selector'])})
  bridges+=hits
  views[e]={'local_records':len(local),'eligible_local_records':sum(x['eligible'] for x in local),'eligible_distinct_patterns':len(patterns),'running_records':sum(m['line_kind']==s['running_kind'] for m in meta.values()),'missing_nonempty_raw_loci':missing[e],'running_opportunities_by_length':opps,'bridge_references':len(hits),'matched_local_records':len({h['local_locus'] for h in hits}),'matched_distinct_patterns':len({tuple(h['groups']) for h in hits}),'unique_running_windows':len({(h['running_locus'],h['start_group'],h['group_length']) for h in hits}),'same_page_key_references':sum(h['same_page_key'] for h in hits),'same_selector_references':sum(h['same_selector'] for h in hits),'other_physical_leaf_references':sum(not h['same_physical_leaf'] for h in hits),'running_raw_kinds':dict(Counter(h['running_raw_kind'] for h in hits))}
 def key(h):return (h['local_locus'],h['running_locus'],h['start_group'],h['group_length'],h['running_group_count'])
 maps={e:{key(h):h for h in bridges if h['edition']==e} for e in s['editions']};common=set.intersection(*(set(m) for m in maps.values()));concordant=[]
 for k in sorted(common):
  hs=[maps[e][k] for e in s['editions']]
  concordant.append({'local_locus':k[0],'running_locus':k[1],'start_group':k[2],'group_length':k[3],'running_group_count':k[4],'literal_same_candidate':len({tuple(h['groups']) for h in hs})==1,'reading_groups':{e:maps[e][k]['groups'] for e in s['editions']}})
 result={'experiment_id':s['experiment_id'],'status':'COMPLETE_EXPLORATORY_AVAILABILITY_CENSUS','metadata_records':len(meta),'raw_loci_outside_metadata':{e:sorted(loc for ee,loc in groups if ee==e and loc not in meta) for e in s['editions']},'metadata_line_kinds':dict(Counter(m['line_kind'] for m in meta.values())),'views':views,'same_index_three_reading_bridges':concordant,'focal_records':[c for c in candidates if c['local_locus']==s['focal_locus']],'focal_bridges':[h for h in bridges if h['local_locus']==s['focal_locus']],'claim_ceiling':'Raw local-record/running-window identity only; inherited kinds are not semantic units, three readings are one manuscript, no null significance or translation.'}
 return result,sorted(candidates,key=lambda c:(c['edition'],c['local_locus'])),sorted(bridges,key=lambda h:(h['edition'],key(h)))

def main():
 s=json.loads(SPEC.read_text());data,receipt=source(s);result,candidates,bridges=calculate(data['LINES'],data['ATLAS'],s)
 write(BASE/'artifacts/SOURCE_RECEIPTS.json',receipt);write(BASE/'artifacts/RESULT.json',result);write(BASE/'artifacts/CANDIDATES.json',candidates,True);write(BASE/'artifacts/BRIDGES.json',bridges,True)
 print(json.dumps({'views':{e:{k:v for k,v in x.items() if k not in ['running_opportunities_by_length','missing_nonempty_raw_loci']} for e,x in result['views'].items()},'same_index_three_reading_bridges':len(result['same_index_three_reading_bridges'])}))
if __name__=='__main__':main()
