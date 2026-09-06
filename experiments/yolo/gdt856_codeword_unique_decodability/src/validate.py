"""Separate residual-set closure plus explicit witness/certificate checks."""
import argparse,hashlib,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def load(n):return json.loads((E/'artifacts'/n).read_text())
def independent(code):
 if any(not isinstance(w,str) or not w for w in code) or len(set(code))!=len(code):return 'INVALID'
 residual={v[len(u):] for u in code for v in code if u!=v and v.startswith(u)};visited=set()
 while residual:
  r=residual.pop()
  if r in code:return 'NON_UD'
  visited.add(r)
  for w in code:
   for long,short in [(r,w),(w,r)]:
    if long.startswith(short):
     tail=long[len(short):]
     if not tail:return 'NON_UD'
     if tail not in visited:residual.add(tail)
 return 'UD'
def verify(code,result):
 decision=independent(code)
 if decision=='INVALID':assert result['status']=='INVALID_INVENTORY_STOP';return
 if decision=='NON_UD':
  assert result['status']=='NON_UD_COLLISION_WITNESS';w=result['witness'];assert w['left']!=w['right'];assert all(x in code for x in w['left']+w['right']);assert ''.join(w['left'])==''.join(w['right'])==w['concatenation'];return
 assert result['status']=='UNIQUELY_DECODABLE_FINITE_CERTIFICATE' and result['witness'] is None;c=result['certificate'];assert c['complete'];states=c['states'];assert [s['id'] for s in states]==list(range(len(states)));lookup={(s['side'],s['residual']):s['id'] for s in states};assert len(lookup)==len(states)
 suffixes=sorted({w[i:] for w in code for i in range(1,len(w))});assert c['suffix_universe']==suffixes and c['state_bound']==2*len(suffixes) and len(states)<=c['state_bound'];assert set(c['checked'])==set(range(len(states))) and len(c['checked'])==len(states)
 for s in states:
  assert s['residual'] in suffixes;assert all(w in code for w in s['left']+s['right']);a,b=''.join(s['left']),''.join(s['right']);assert a==b+s['residual'] if s['side']=='L' else b==a+s['residual']
 initial=[]
 for u,v in itertools.combinations(sorted(code),2):
  if v.startswith(u):initial.append(dict(left=u,right=v,state=lookup['R',v[len(u):]]))
  elif u.startswith(v):initial.append(dict(left=u,right=v,state=lookup['L',u[len(v):]]))
 assert initial==c['initial'];expected=set()
 for st in states:
  r=st['residual']
  for w in code:
   assert r!=w
   if r.startswith(w):key=(st['side'],r[len(w):])
   elif w.startswith(r):key=('L' if st['side']=='R' else 'R',w[len(r):])
   else:continue
   expected.add((st['id'],w,lookup[key]))
 assert expected=={(e['source'],e['word'],e['target']) for e in c['edges']} and len(expected)==len(c['edges'])
 reached={i['state'] for i in initial}
 while True:
  extra={b for a,w,b in expected if a in reached}
  if extra<=reached:break
  reached|=extra
 assert reached==set(range(len(states)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args();controls=load('CONTROLS.json')
 for case in controls['cases']:verify(case['code'],case['result']);assert case['result']['status']==case['expected']
 if a.controls:print('INDEPENDENT_CONTROLS_PASS_NO_INVENTORY_READ');return
 s=json.loads((E/'src/SPEC.json').read_text());raw=(ROOT/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];lines=raw.decode('utf-8').splitlines();headerokay=bool(lines) and lines[0].split('\t')[0]=='unit';words=[x.partition('\t')[0] for x in lines[1:]] if headerokay else [];assert words==load('CODEWORDS.json');r=load('RESULT.json');assert r['source_sha256']==s['source_sha256'] and r['units']==len(words)
 if not headerokay or len(words)!=98 or independent(words)=='INVALID':assert r['status']=='INVALID_INVENTORY_STOP'
 else:verify(words,r)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_RESIDUAL_CLOSURE_AND_WITNESS_OR_CERTIFICATE',units=len(words),code_status=r['status'],manuscript_semantics=False),indent=2)+'\n');print('PASS')
if __name__=='__main__':main()
