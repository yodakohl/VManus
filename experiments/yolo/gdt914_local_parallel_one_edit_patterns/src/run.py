#!/usr/bin/env python3
import collections,csv,hashlib,json,re
from functools import lru_cache
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
PAIRINGS={'ADJACENT':((0,1),(2,3)),'PARALLEL':((0,2),(1,3)),'CROSSED':((0,3),(1,2))}
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(name,x):(E/'artifacts'/name).write_text(enc(x))
@lru_cache(None)
def edits(a,b):
 out=set()
 if a==b or abs(len(a)-len(b))>1:return out
 if len(a)==len(b):
  sites=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
  if len(sites)==1:
   i=sites[0]
   out.update([('SUB',a[i],b[i],'L',i),('SUB',a[i],b[i],'R',len(a)-i-1)])
 elif len(b)==len(a)+1:
  for i in range(len(b)):
   if b[:i]+b[i+1:]==a:out.update([('INS','',b[i],'L',i),('INS','',b[i],'R',len(a)-i)])
 else:
  for i in range(len(a)):
   if a[:i]+a[i+1:]==b:out.update([('DEL',a[i],'','L',i),('DEL',a[i],'','R',len(b)-i)])
 return out

def main():
 spec=json.loads((E/'src/SPEC.json').read_text());allhits=[];den={};full=[]
 for ed,source in spec['sources'].items():
  raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256'];data=json.loads(raw);counts=collections.Counter(candidate=0,definite_plain=0,four_distinct=0,ADJACENT=0,PARALLEL=0,CROSSED=0)
  for line in data['lines']:
   m=line['metadata'];assert m['edition']==ed and m['page'] in spec['allowed_selectors'] and not m['page'].startswith('f84');gs=[dict(zip(data['group_columns'],g)) for g in line['groups']];linehit=False
   for start in range(len(gs)-3):
    counts['candidate']+=1;seg=gs[start:start+4];words=[g['ivtff_group_raw'] for g in seg]
    if not all(re.fullmatch('[a-z]+',w) for w in words):continue
    if not all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(seg,seg[1:])):continue
    counts['definite_plain']+=1
    if len(set(words))<4:continue
    counts['four_distinct']+=1
    for pairing,((a,b),(c,d)) in PAIRINGS.items():
     signatures=edits(words[a],words[b]) & edits(words[c],words[d])
     if not signatures:continue
     counts[pairing]+=1;linehit=True
     allhits.append(dict(edition=ed,locus=m['locus'],page=m['page'],folio=re.match(r'f[0-9]+',m['page']).group(),start_index=int(seg[0]['source_group_index']),source_ids=[g['source_group_id'] for g in seg],words=words,pairing=pairing,signatures=[list(s) for s in sorted(signatures)]))
   if linehit:full.append(dict(edition=ed,metadata=m,group_columns=data['group_columns'],groups=line['groups']))
  den[ed]=dict(counts)
 allhits.sort(key=lambda h:(h['edition'],h['locus'],h['start_index'],h['pairing']))
 by=collections.defaultdict(dict)
 for h in allhits:
  key=(h['locus'],h['start_index'],tuple(h['words']),h['pairing']);by[key][h['edition']]=h
 consensus=[]
 for key,readings in sorted(by.items()):
  if set(readings)!=set(spec['sources']):continue
  common=set.intersection(*(set(tuple(s) for s in h['signatures']) for h in readings.values()))
  if common:
   h=readings['ZL3b'];consensus.append({k:v for k,v in h.items() if k not in ('edition','source_ids','signatures')}|dict(signatures=[list(s) for s in sorted(common)],source_ids_by_reading={ed:v['source_ids'] for ed,v in readings.items()}))
 rules=collections.defaultdict(list)
 for h in consensus:
  for sig in h['signatures']:rules[(h['pairing'],tuple(sig))].append(h)
 aggregate=[]
 for (pairing,sig),hits in rules.items():
  ((a,b),(c,d))=PAIRINGS[pairing];leaves=sorted({h['folio'] for h in hits},key=lambda f:int(f[1:]));bases=sorted({(h['words'][a],h['words'][c]) for h in hits})
  aggregate.append(dict(pairing=pairing,signature=list(sig),folios=leaves,base_pairs=[list(x) for x in bases],occurrences=len(hits),nomination=len(leaves)>=3 and len(bases)>=2))
 aggregate.sort(key=lambda r:(-len(r['folios']),-len(r['base_pairs']),-r['occurrences'],r['pairing'],r['signature']))
 result=dict(status='COMPLETE_LOCAL_EDIT_DISCOVERY_NO_SEMANTIC_TEST',denominators=den,hit_rows=len(allhits),concordant_window_pairings=len(consensus),concordant_physical_leaves=sorted({h['folio'] for h in consensus},key=lambda f:int(f[1:])),signature_rows=len(aggregate),nominated_signature_rows=sum(r['nomination'] for r in aggregate),meaning_claims=0,significance='NOT_TESTED_NO_SEARCH_NULL')
 save('HITS.json',allhits);save('FULL_HIT_LINES.json',full);save('CONSENSUS.json',consensus);save('RULES.json',aggregate);save('RESULT.json',result)
 with (E/'artifacts/PATTERNS.tsv').open('w') as f:
  writer=csv.writer(f,delimiter='\t',lineterminator='\n');writer.writerow(['locus','page','start_index','pairing','words','shared_edit_signatures'])
  for h in consensus:writer.writerow([h['locus'],h['page'],h['start_index'],h['pairing'],' '.join(h['words']),json.dumps(h['signatures'],separators=(',',':'))])
 print(json.dumps(result));print(json.dumps({'top_rules':aggregate[:10],'first_concordant':consensus[:8]}))
if __name__=='__main__':main()
