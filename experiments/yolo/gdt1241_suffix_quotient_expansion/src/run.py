"""Frozen reverse-unit wrapper; no native parsing or source census."""
import gzip, hashlib, importlib.util, itertools, json, sys
from datetime import datetime, timezone
from pathlib import Path
D=Path(__file__).resolve().parents[1]
ROOT=D.parents[2]
A=D/'artifacts'
ENGINE=ROOT/'experiments/yolo/gdt1234_prefix_quotient_code_capacity/src/engine.py'
loader=importlib.util.spec_from_file_location('old1234engine',ENGINE)
engine=importlib.util.module_from_spec(loader);loader.loader.exec_module(engine)
CACHE=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
OLD=ROOT/'experiments/yolo/gdt1240_prefix_expansion_fourth_power/artifacts'

def now():return datetime.now(timezone.utc).isoformat()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def closure(words):
 d=engine.derive([tuple(reversed(w)) for w in words],seconds=120)
 assert d['status']=='COMPLETE',d['status']
 nodes=[{'word':list(reversed(n['word'])),'parents':n['parents']} for n in d['nodes']]
 return nodes,d['rounds']
def fixture():
 def member(w,codes):
  ok={0}
  for i in range(len(w)):
   if i in ok:
    for c in codes:
     if w[i:i+len(c)]==c:ok.add(i+len(c))
  return len(w) in ok
 tables=0
 seq=[w for n in range(1,4) for w in itertools.product('ab',repeat=n)]
 for k in (1,2,3):
  for codes in itertools.combinations(seq,k):
   if any(a!=b and len(a)<=len(b) and b[-len(a):]==a for a in codes for b in codes):continue
   words={sum(p,()) for n in (1,2,3) for p in itertools.product(codes,repeat=n)}
   nodes,_=closure(words)
   assert all(member(tuple(n['word']),codes) for n in nodes)
   tables+=1
 out={tuple(n['word']) for n in closure([('a',),('a','b')])[0]}
 assert out=={('a',),('a','b')}
 out={tuple(n['word']) for n in closure([('a',),('b','a')])[0]}
 assert ('b',) in out
 out={tuple(n['word']) for n in closure([('a',),('ch','a')])[0]}
 assert ('ch',) in out and ('h','c') not in out
 return {'status':'PASS','suffix_free_tables':tables,'wrong_side_and_unit_cases':3}
def main():
 if '--fixtures' in sys.argv:print(json.dumps(fixture()));return
 assert not (A/'RESULT.json').exists(),'Frozen result exists; do not overwrite'
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress(CACHE.read_bytes()))
 old=json.loads((OLD/'RESULT.json').read_text())
 assert json.loads((OLD/'VALIDATION.json').read_text())['status']=='PASS'
 assert all(s['factorizations']==0 for s in old['sources'].values())
 summaries={};proofs={}
 for reader,rows in sorted(data.items()):
  byword={}
  for row in rows:
   assert not row['page'].startswith('f84')
   byword.setdefault(tuple(row['units']),[]).append(row)
  nodes,rounds=closure(byword)
  known={tuple(n['word']):i for i,n in enumerate(nodes)}
  used=sorted({x for w in byword for x in w})
  forced=sorted(w[0] for w in known if len(w)==1)
  needed=set()
  def visit(i):
   if i in needed:return
   needed.add(i)
   if nodes[i]['parents']:
    for p in nodes[i]['parents']:visit(p)
  for g in forced:visit(known[(g,)])
  proof=[]
  for i in sorted(needed):
   n=dict(nodes[i]);n['id']=i
   if n['parents'] is None:
    sources=byword[tuple(n['word'])]
    n['source_ids']=sorted(row['id'] for row in sources)
    n['frequency']=len(sources);n['pages']=sorted({row['page'] for row in sources})
   proof.append(n)
  witness=byword.get(tuple('keeees'),[])
  power=all(g in forced for g in ('k','e','s')) and bool(witness)
  summary={'whole_tokens':len(rows),'whole_types':len(byword),'closure_types':len(known),'rounds':rounds,
   'used_units':used,'forced_singletons':forced,'not_forced':sorted(set(used)-set(forced)),
   'code_status':'ALL_USED_CODES_SINGLETON' if used==forced else 'PARTIAL_SINGLETON_OBLIGATIONS',
   'keeees_ids':sorted(row['id'] for row in witness),'keeees_pages':sorted({row['page'] for row in witness}),
   'fourth_power_obligation':power,
   'source_contracts':{s:'EXCLUDED_BY_FROZEN1240' if power else 'NO_EXCLUSION_FROM_THIS_TEST' for s in old['sources']}}
  summaries[reader]=summary;proofs[reader]={'forced_nodes':{g:known[(g,)] for g in forced},'nodes':proof}
  payload=json.dumps({'reader':reader,'nodes':nodes},separators=(',',':')).encode()
  (A/f'CLOSURE_{reader}.json.gz').write_bytes(gzip.compress(payload,mtime=0))
 write(A/'PROOFS.json',proofs)
 result={'experiment':'GDT1241','status':'ALL_READINGS_SINGLETON_ONLY' if all(x['code_status']=='ALL_USED_CODES_SINGLETON' for x in summaries.values()) else 'PARTIAL_SINGLETON_OBLIGATIONS',
 'source_status':'ALL_READINGS_FIVE_SOURCE_CONTRACTS_EXCLUDED' if all(x['fourth_power_obligation'] for x in summaries.values()) else 'SEE_READER_SPECIFIC_CONSEQUENCES',
 'readers':summaries,'source_census':'No new census; frozen GDT1240 results reused',
 'limits':['Exact working units and complete whole-group contract','First-discovered proofs may depend on rare native forms','No meaning or source-language rejection']}
 write(A/'RESULT.json',result)
 write(A/'RUN_RECEIPT.json',{'completed_utc':now(),'registration_sha256':hashlib.sha256((A/'REGISTRATION_LOCK.json').read_bytes()).hexdigest(),'status':'COMPLETE'})
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
