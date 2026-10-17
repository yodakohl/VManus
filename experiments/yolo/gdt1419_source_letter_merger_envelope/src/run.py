#!/usr/bin/env python3
"""Necessary forward letter-merger word/graph envelope, never a decoded reading."""
import gzip,hashlib,itertools,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def setsha(xs):return hashlib.sha256(json.dumps(sorted(xs),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def compatible(word,units):
 if len(word)!=len(units):return False
 key={}
 for letter,unit in zip(word,units):
  if letter in key and key[letter]!=unit:return False
  key[letter]=unit
 return True

def records(s):
 recipes=read(ROOT/s['recipe_path']);deot=read(ROOT/s['deot_path']);other=read(ROOT/s['other_path']);out={}
 for name in s['source_names']:
  if name in recipes:out[name]=[r['words'] for r in recipes[name]]
  elif name=='deot':out[name]=[r['words'] for r in deot['source_sections']]
  else:
   rows=other[name]['PRIMARY']['units'];assert len(rows)==8000
   blocks={}
   for r in rows:blocks.setdefault(r['sentence_index'],[]).append(r['unit'])
   out[name]=list(blocks.values())
 return out

def reachability(options,edges):
 reachable=[];successors={}
 for a,b in edges:successors.setdefault(a,set()).add(b)
 for i,opts in enumerate(options):
  reached=set(opts) if not i else {b for a in reachable[-1] for b in successors.get(a,()) if b in opts}
  reachable.append(reached)
 return reachable

def controls():
 n=0
 for length in range(1,5):
  for word in map(''.join,itertools.product('ab',repeat=length)):
   for units in itertools.product('XY',repeat=length):
    expected=any(tuple(dict(zip('ab',values))[c] for c in word)==units for values in itertools.product('XY',repeat=2))
    assert compatible(word,units)==expected;n+=1
 assert n==340 and compatible('ab','XX') and not compatible('aa','XY')
 assert [len(x) for x in reachability([{'ab'},{'bc'},{'ca'}],{('ab','bc'),('ca','ab')})]==[1,1,0]
 assert compatible('ab','XY') and compatible('ac','ZX')
 assert not any(''.join(dict(zip('abc',values))[c] for c in 'ab')=='XY' and ''.join(dict(zip('abc',values))[c] for c in 'ac')=='ZX' for values in itertools.product('XYZ',repeat=3))
 return {'status':'PASS','single_word_complete_function_cases':n,'merging_allowed_splitting_forbidden':True,'no_cross_record_edge':True,'envelope_can_pass_without_global_key':True}

def main():
 lock=read(E/'LOCK.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 s=read(E/'src/SPEC.json');gate=controls();native=read(ROOT/s['native_path']);groups=[]
 rx=re.compile('|'.join(re.escape(u) for u in sorted(s['signs'],key=lambda u:(-len(u),u))))
 for line in native['lines']:
  for g in line['groups']:
   units=rx.findall(g[2]);assert ''.join(units)==g[2]
   groups.append({'id':g[0],'raw':g[2],'units':units})
 assert len(groups)==77 and [u for g in groups for u in g['units']]==native['stream']
 assert [g['units'] for g in groups]==native['original_units']
 cases=[]
 for name,rs in records(s).items():
  W={w for r in rs for w in r};edges={p for r in rs for p in zip(r,r[1:])};bylen={n:{w for w in W if len(w)==n} for n in {len(g['units']) for g in groups}}
  options=[{w for w in bylen[len(g['units'])] if compatible(w,g['units'])} for g in groups]
  reached=reachability(options,edges)
  def failure(sets):
   pos=next((i for i,x in enumerate(sets) if not x),None)
   return None if pos is None else dict(position=pos+1,**groups[pos])
  row={'source':name,'word_types':len(W),'source_records':len(rs),'source_tokens':sum(map(len,rs)),'source_edges':len(edges),'candidate_counts':list(map(len,options)),'candidate_sha256':list(map(setsha,options)),'reachable_counts':list(map(len,reached)),'reachable_sha256':list(map(setsha,reached)),'first_empty_candidate':failure(options),'first_empty_path':failure(reached),'status':'RELAXED_PATH_EXISTS_NO_KEY_ESTABLISHED' if reached[-1] else 'EXCLUDED_BY_NECESSARY_ENVELOPE'}
  cases.append(row);print(json.dumps({'source':name,'status':row['status'],'first_empty_candidate':row['first_empty_candidate'],'first_empty_path':row['first_empty_path']}),flush=True)
 result={'experiment_id':'GDT1419','status':'NECESSARY_FORWARD_MERGER_ENVELOPE','groups':groups,'cases':cases,'source_free_controls':gate,'lock_sha256':sha(E/'LOCK.json'),'claim_ceiling':s['decision']}
 p=E/'artifacts/RESULT.json';data=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if p.exists():assert p.read_text()==data
 else:p.write_text(data)
if __name__=='__main__':main()
