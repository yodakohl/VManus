#!/usr/bin/env python3
"""All unknown overlapping-pair assignments via exact endpoint equalities."""
import argparse,csv,hashlib,io,json,re,subprocess
from collections import Counter,defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(x): return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def write(name,x,check):
 p=E/'artifacts'/name; data=encoded(x)
 if check: assert p.read_text()==data,name
 else: p.write_text(data)
def select(spec):
 p=ROOT/spec['source_lines']; assert sha(p)==spec['source_lines_sha256']
 lines=json.loads(p.read_text()); assert sorted(x['locus'] for x in lines)==spec['allowed_loci']
 argv=['./vmanus-exp','query-tsv',spec['sta_atlas'],'--selector','locus']
 for locus in spec['allowed_loci']:
  assert not locus.lower().startswith('f84'); argv+=['--allow',locus]
 argv+=['--columns',','.join(spec['sta_columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
 out=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,check=True).stdout
 rows=list(csv.DictReader(io.StringIO(out),delimiter='\t')); assert rows
 index={r['source_group_id']:r for r in rows}; assert len(index)==len(rows)
 groups=[]; excluded=Counter()
 for line in sorted(lines,key=lambda x:x['locus']):
  readers={r['edition']:r for r in line['readings']}; assert set(readers)==set(spec['editions'])
  ref=readers['ZL3b']['groups']
  if any(r['groups']!=ref for r in readers.values()): excluded['line_group_boundary_disagreement']+=1; continue
  for k,raw in enumerate(ref):
   assert re.fullmatch('[a-z]+',raw)
   ids={ed:r['source_group_ids'][k] for ed,r in readers.items()}
   boundaries={ed:(r['internal_separators'][k-1] if k else 'LINE_START',r['internal_separators'][k] if k<len(ref)-1 else 'LINE_END') for ed,r in readers.items()}
   if any(left not in ('DEFINITE_SPACE','LINE_START') or right not in ('DEFINITE_SPACE','LINE_END') for left,right in boundaries.values()):
    excluded['group_uncertain_outer_boundary']+=1; continue
   sr=[]
   for ed,sid in ids.items():
    assert sid in index,('missing_sta_group',sid)
    a=index[sid]; left,right=boundaries[ed]
    assert (a['edition'],a['locus'],int(a['source_group_index']),int(a['source_group_count']),a['left_separator'],a['right_separator'])==(ed,line['locus'],k+1,len(ref),left,right),sid
    codes=a['primary_sta_codes'].split(); assert len(codes)==int(a['primary_sta_symbol_count']) and codes,sid
    sr.append((codes,int(a['alternative_site_count'])))
   sta=None
   if any(n for codes,n in sr): excluded['sta_group_marked_alternative']+=1
   elif not all(codes==sr[0][0] for codes,n in sr): excluded['sta_group_member_disagreement']+=1
   else: sta=sr[0][0]
   groups.append(dict(id=line['locus']+'#'+str(k+1),locus=line['locus'],page=line['page'],group_index=k+1,raw=raw,source_group_ids=ids,sta=sta))
 return groups,dict(sorted(excluded.items())),dict(argv=argv,sha256=hashlib.sha256(out.encode()).hexdigest())
def graph(groups,panel):
 seqs=[(g,list(g['raw']) if panel=='literal_eva' else g['sta']) for g in groups if panel=='literal_eva' or g['sta'] is not None]
 alphabet=sorted({c for g,s in seqs for c in s}); nodes=sorted(prefix+c for c in alphabet for prefix in ('L:','R:'))
 parent={n:n for n in nodes}
 def find(a):
  while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
  return a
 witnesses={}; occurrences=0
 for g,s in seqs:
  for pos,(a,b) in enumerate(zip(s,s[1:])):
   occurrences+=1; witnesses.setdefault((a,b),dict(pair=[a,b],group_id=g['id'],position=pos))
 forest=[]
 for (a,b),witness in sorted(witnesses.items()):
  x,y=find('R:'+a),find('L:'+b)
  if x!=y: parent[max(x,y)]=min(x,y); forest.append(witness)
 buckets=defaultdict(list)
 for n in nodes: buckets[find(n)].append(n)
 components=sorted((sorted(v) for v in buckets.values()),key=lambda v:v[0]); labels={n:i for i,v in enumerate(components) for n in v}
 pairs={c:[labels['L:'+c],labels['R:'+c]] for c in alphabet}; collision=defaultdict(list)
 for c,pair in pairs.items(): collision[tuple(pair)].append(c)
 forced=sorted((v for v in collision.values() if len(v)>1),key=lambda v:v[0])
 underlying={tuple([pairs[s[0]][0]]+[pairs[c][1] for c in s]) for g,s in seqs}
 status='INJECTIVE_OVERLAPPING_PAIR_MODEL_EXCLUDED' if forced else 'EXACT_OVERLAPPING_PAIR_MODEL_COMPATIBLE'
 return dict(alphabet=alphabet,groups=len(seqs),occurrences=occurrences,pair_types=len(witnesses),components=components,symbol_pairs=pairs,forest=forest,forced_collision_classes=forced,underlying_distinct_sequences=len(underlying),status=status)
def selftest():
 def panel(words): return graph([dict(id=str(i),raw=w) for i,w in enumerate(words)],'literal_eva')
 a=panel(['ab','bc']); assert a['status']=='EXACT_OVERLAPPING_PAIR_MODEL_COMPATIBLE'
 b=panel(['aa','ab','ba','bb']); assert len(b['components'])==1 and b['forced_collision_classes']==[['a','b']]
 c=panel(['a','b']); assert len(c['components'])==4 and not c['forced_collision_classes']
 return ['noncollapsing_chain','forced_homophony','isolated_singletons']
def main():
 p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); args=p.parse_args()
 for path,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items(): assert sha(ROOT/path)==h,path
 spec=json.loads((E/'src/SPEC.json').read_text()); groups,excluded,guard=select(spec)
 result=dict(experiment_id='GDT883',status='EXACT_OVERLAPPING_PAIR_CONSTRAINTS_COMPLETED',source_lines_sha256=spec['source_lines_sha256'],source_sta_sha256=sha(ROOT/spec['sta_atlas']),guard=guard,exclusions=excluded,panels={panel:graph(groups,panel) for panel in spec['panels']},selftests=selftest())
 write('SELECTED_GROUPS.json',groups,args.check); write('RESULT.json',result,args.check)
 print(json.dumps(dict(status=result['status'],groups=len(groups),panels={p:{k:v for k,v in r.items() if k in ('groups','occurrences','pair_types','status','underlying_distinct_sequences')}|dict(alphabet=len(r['alphabet']),components=len(r['components']),collision_classes=len(r['forced_collision_classes'])) for p,r in result['panels'].items()}),sort_keys=True))
if __name__=='__main__': main()
