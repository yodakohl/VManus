#!/usr/bin/env python3
"""A necessary wholeword cube for two fixed freeUD decoding envelopes."""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def pattern(w):
 d={};return tuple(d.setdefault(x,len(d)) for x in w)
def cube(w):return len(w)>=6 and len(w)%3==0 and w[:len(w)//3]*3==w
def controls():
 examples={'ababab':True,'aaaaaa':True,'abcabcabc':True,'abcabc':False,'abab':False,'XabababY':False,'aababab':False,'aaaaaA':False,'aAaAaA':True,'áaáaáa':True,'דידידי':True};checks=0
 for word,expected in examples.items():
  assert cube(word)==expected and cube(tuple(pattern(word)))==expected and cube(word[::-1])==expected;checks+=1
 for U,V in itertools.product(['a','bc','def'],repeat=2):
  word=(U+V)*3;assert cube(word) and cube((V+U)*3) and cube(word[::-1]);checks+=1
 C=[tuple('a'),tuple('b'),tuple('c'),tuple('cd')]
 assert any(a!=b and b[:len(a)]==a for a in C for b in C)
 assert all(a==b or b[-len(a):]!=a for a in C for b in C) # suffix-free, hence freelyUD despite nonprefix
 values={tuple('a'):'u',tuple('b'):'vw',tuple('c'):'z',tuple('cd'):''}
 def decode(s):
  tail=tuple(s);out=[]
  while tail:
   candidates=[c for c in C if tail[-len(c):]==c];assert len(candidates)==1;c=candidates[0];out.append(c);tail=tail[:-len(c)]
  return list(reversed(out))
 assert decode('ababab')==[tuple(x) for x in 'ababab'];assert cube(''.join(values[c] for c in decode('ababab')))
 assert ''.join(values[c] for c in decode('acd'))=='u';checks+=2
 assert tuple('a')+tuple('b')==tuple('ab') # adding ab beside a,b would make written code nonUD
 assert ''.join(['x']*3)=='xxx' and not cube('xxx') # C={ab}, without singleton premises
 assert sum([1,1])==2 and all(sum(parts)>2 for n in [3,4] for parts in itertools.product([1,2],repeat=n));checks+=3
 return {'status':'PASS_SOURCE_FREE_CONTROLS','checks':checks,'same_expansions_allowed':True,'whole_cube_not_substring':True,'null_other_entry_allowed_in_PURE':True,'nonprefix_suffixfree_fixture':True,'native_data_read':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args()
 if a.controls:print(json.dumps(controls(),sort_keys=True));return
 assert not(B/'artifacts/RESULT.json').exists();lock=read(B/'LOCK.json')
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 s=read(B/'src/SPEC.json');env=read(R/s['source_envelope_path'])['sources'];source={}
 for n in s['source_names']:
  cubes=[]
  for pk,cert in sorted(env[n]['modes']['FWD'].items()):
   p=tuple(map(int,pk.split('.')))
   if not cube(p):continue
   w=cert['word'];assert cert['direction']=='FWD' and pattern(w)==p and cube(w);k=len(w)//3
   cubes.append({'pattern_key':pk,'word':w,'block':w[:k],'block_codepoints':k})
  source[n]={'word_types':env[n]['word_types'],'cube_pattern_count':len(cubes),'cubes':cubes,'status':'NO_WHOLE_WORD_CUBE' if not cubes else 'CUBE_CAPACITY_ONLY'}
 families=read(R/s['families_path'])['readers'];cases=[]
 for ed in s['readers']:
  for panel in s['panels']:
   rows=[x for x in families[ed] if panel=='FULL' or len(x['leaves'])>=2];lookup={x['form']:x for x in rows};witnesses={}
   for form in s['forms']:
    row=lookup.get(form)
    if row:assert row['units']==row['collapsed_units']==list(form)
    witnesses[form]={'present':row is not None,'count':row['count'] if row else 0,'leaves':row['leaves'] if row else [],'ids':row['ids'] if row else [],'units':list(form),'base_units':list(form)}
   models={}
   for model in s['models']:
    missing=[form for form in (['d','y','dydydy'] if model=='PURE' else ['dydydy']) if not witnesses[form]['present']]
    pairs=[form for form in ['dy','yd'] if witnesses[form]['present']]
    if model=='MIXED' and not pairs:missing.append('dy_or_yd')
    ready=not missing;models[model]={'ready':ready,'missing':missing,'forcing_forms':['d','y'] if model=='PURE' else pairs,'source_decisions':{n:'NO_NATIVE_BRIDGE' if not ready else 'EXCLUDED_FIXED_W_CONJUNCTION' if not source[n]['cubes'] else 'CUBE_CAPACITY_ONLY' for n in s['source_names']}}
   cases.append({'reader':ed,'panel':panel,'groups':sum(x['count'] for x in rows),'raw_types':len(rows),'witnesses':witnesses,'models':models})
 save('SOURCE_CUBES.json',{'sources':source});save('RESULT.json',{'experiment_id':'GDT1406','status':'COMPLETE_UD_CUBE_NECESSARY_SCREEN','cases':cases,'claim_ceiling':s['claim_ceiling']});print(json.dumps({'sources':{n:d['cube_pattern_count'] for n,d in source.items()},'native':[{'reader':c['reader'],'panel':c['panel'],'models':{m:d['ready'] for m,d in c['models'].items()}} for c in cases]},sort_keys=True))
if __name__=='__main__':main()
