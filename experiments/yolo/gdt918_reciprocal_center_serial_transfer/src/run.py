import argparse,collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def dump(n,d):(E/'artifacts'/n).write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n')
def read(n):return json.loads((E/'artifacts'/n).read_text())
def intake(ed,phase):
 parent=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer';s=json.loads((parent/'src/SPEC.json').read_text());d=json.loads((parent/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text());out=[]
 for row in d['lines']:
  m=row['metadata'];assert m['page'] in s['partitions'][phase] and not m['page'].startswith('f84')
  if m['kind']=='P':out.append((m,[dict(zip(d['group_columns'],g)) for g in row['groups']]))
 return out

def census(rows):
 triples=[];serial=[];den=collections.Counter(lines=len(rows),raw_triples=0,eligible_triples=0,distinct_triples=0,raw_fives=0,eligible_fives=0,serial_fives=0)
 def event(m,gs):return dict(page=m['page'],leaf=int(re.match(r'f(\d+)',m['page'])[1]),locus=m['locus'],start_index=int(gs[0]['source_group_index']),words=[g['ivtff_group_raw'] for g in gs],source_ids=[g['source_group_id'] for g in gs])
 def valid(gs):return all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs) and all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
 for m,gs in rows:
  for n,tag in [(3,'triples'),(5,'fives')]:
   for i in range(len(gs)-n+1):
    den['raw_'+tag]+=1;part=gs[i:i+n]
    if not valid(part):continue
    den['eligible_'+tag]+=1;w=[g['ivtff_group_raw'] for g in part]
    if n==3 and len(set(w))==3:triples.append(event(m,part));den['distinct_triples']+=1
    if n==5 and w[1]==w[3] and len({w[0],w[2],w[4],w[1]})==4:serial.append(event(m,part));den['serial_fives']+=1
 return dict(denominators=dict(den),triples=triples,serial=serial)

def reciprocal(triples):
 by=collections.defaultdict(lambda:collections.defaultdict(list))
 for t in triples:
  a,x,b=t['words'];by[(x,*sorted([a,b]))][0 if a<b else 1].append(t)
 out=[]
 for (x,a,b),v in sorted(by.items()):
  left=v.get(0,[]);right=v.get(1,[])
  if left and right and any(t['leaf']!=u['leaf'] for t in left for u in right):out.append(dict(center=x,endpoints=[a,b],forward=left,reverse=right,leaves=sorted({t['leaf'] for ts in v.values() for t in ts})))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['discovery','evaluation']);args=ap.parse_args();lock=json.loads((E/'PREREG_LOCK.json').read_text());assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in lock['files'].items())
 if args.phase=='discovery':
  allc={}
  for ed in ['ZL3b','IT2a','RF1b']:
   c=census(intake(ed,'DISCOVERY'));rp=reciprocal(c['triples']);by=collections.defaultdict(list)
   for q in rp:by[q['center']].append(q)
   candidates=[]
   for x,qs in sorted(by.items()):
    leaves=sorted({l for q in qs for l in q['leaves']})
    if len(qs)>=2 and len(leaves)>=3:candidates.append(dict(center=x,reciprocal_pairs=qs,leaves=leaves))
   d=dict(denominators=c['denominators'],reciprocal_pairs=rp,candidates=candidates);dump(f'DISCOVERY_{ed}.json',d);allc[ed]=dict(denominators=c['denominators'],reciprocal_pairs=len(rp),candidates=[v['center'] for v in candidates])
  candidates=read('DISCOVERY_ZL3b.json')['candidates'];dump('CANDIDATES.json',candidates);dump('PREDICTIONS.json',[dict(center=v['center'],carrier='A X B X C',constraint='all3endpointsdistinctandnotX',partition='evenphysicalleaves',expected='atleastoneeligiblecomplete5groupwitness',claim='availability_only_not_meaning') for v in candidates]);dump('DISCOVERY_RESULT.json',allc);print(json.dumps(allc));return
 freeze=json.loads((E/'DISCOVERY_LOCK.json').read_text());assert all(hashlib.sha256((E/p).read_bytes()).hexdigest()==h for p,h in freeze['files'].items());candidates=read('CANDIDATES.json');assert candidates,'no candidates: evaluation prohibited';centers=[v['center'] for v in candidates];out={}
 for ed in ['ZL3b','IT2a','RF1b']:
  c=census(intake(ed,'EVALUATION'));rp=reciprocal(c['triples']);cards=[]
  for x in centers:
   ss=[t for t in c['serial'] if t['words'][1]==x];tt=[t for t in c['triples'] if t['words'][1]==x];rr=[q for q in rp if q['center']==x];cards.append(dict(center=x,serial=ss,serial_leaves=sorted({t['leaf'] for t in ss}),triples=tt,reciprocal_pairs=rr,predicted_construction_available=bool(ss)))
  d=dict(denominators=c['denominators'],candidates=cards);dump(f'EVALUATION_{ed}.json',d);out[ed]=dict(denominators=c['denominators'],candidates=[dict(center=v['center'],serial=len(v['serial']),serial_leaves=v['serial_leaves'],triples=len(v['triples']),reciprocal_pairs=len(v['reciprocal_pairs']),predicted_construction_available=v['predicted_construction_available']) for v in cards])
 result=dict(status='COMPLETE_STRUCTURAL_WITNESS_AVAILABILITY',nominees=centers,readings=out,meaning_claims=0,significance_claim=False,source_exposed=True);dump('RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
