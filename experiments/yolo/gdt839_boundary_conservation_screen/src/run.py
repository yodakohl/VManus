import argparse,hashlib,importlib.util,itertools,json,re
from collections import defaultdict,Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
p=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py'
s=importlib.util.spec_from_file_location('base829',p);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
def dump(x):return json.dumps(x,sort_keys=True,indent=2)+'\n'
def main():
 a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');a=a.parse_args()
 for name,value in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value,name
 spec=json.loads((E/'src/SPEC.json').read_text());rows,guard=h.query(spec);recs=h.records(rows);segments,stats=h.scaffold(recs)
 out=[];counts=Counter()
 for segment in segments:
  for r in segment:
   gs=r['groups']
   for i,(left,right) in enumerate(zip(gs,gs[1:])):
    counts['adjacent_pairs']+=1
    if left['right_separator']!='DEFINITE_SPACE':continue
    counts['certain_pairs']+=1
    words=[left['ivtff_group_raw'],right['ivtff_group_raw']]
    aa=[[x[0] for x in h.atoms(w)] for w in words]
    if min(map(len,aa))<spec['min_group_atoms'] or sum(map(len,aa))<spec['min_joined_atoms']:continue
    counts['size_eligible']+=1
    ok=True
    for ed in ['IT2a','RF1b']:
     other=recs.get((ed,r['locus']))
     if other is None or len(other['groups'])!=len(gs):ok=False;break
     pair=other['groups'][i:i+2]
     if [g['ivtff_group_raw'] for g in pair]!=words or pair[0]['right_separator']!='DEFINITE_SPACE':ok=False;break
    if not ok:continue
    out.append(dict(id=left['source_group_id'],page=r['page'],leaf=re.match(r'f(\d+)',r['page'])[1],locus=r['locus'],index=i+1,words=words,atoms=aa[0]+aa[1],split=len(aa[0])))
 buckets=defaultdict(list)
 for x in out:buckets[tuple(x['atoms'])].append(x)
 pairs=[]
 for group in buckets.values():
  for x,y in itertools.combinations(group,2):
   if x['leaf']!=y['leaf'] and 1<=abs(x['split']-y['split'])<=spec['max_shift_atoms']:pairs.append(sorted([x['id'],y['id']]))
 pairs.sort();result=dict(status='CANDIDATE_CAPACITY' if pairs else 'CAPACITY_STOP',counts=dict(counts),eligible_occurrences=len(out),qualifying_pairs=len(pairs),joined_families=len({tuple(x['atoms']) for x in out if any(x['id'] in p for p in pairs)}),guard=guard,scaffold=stats)
 for name,obj in [('OCCURRENCES.json',out),('PAIRS.json',pairs),('RESULT.json',result)]:
  path=E/'artifacts'/name;data=dump(obj)
  if a.check:assert path.read_text()==data,name
  else:path.write_text(data)
 print(dump({k:v for k,v in result.items() if k!='guard'}))
if __name__=='__main__':main()
