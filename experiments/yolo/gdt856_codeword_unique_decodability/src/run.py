import argparse,collections,hashlib,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x,check=False):
 p=E/'artifacts'/n
 if check:assert p.read_text()==enc(x),n
 else:p.write_text(enc(x))
def valid(words,expected=None):
 issues=[]
 if any(not isinstance(w,str) or w=='' for w in words):issues.append('EMPTY_OR_NONSTRING_UNIT')
 if len(set(words))!=len(words):issues.append('DUPLICATE_UNITS')
 if expected is not None and len(words)!=expected:issues.append('UNIT_COUNT')
 return issues
def solve(words):
 issues=valid(words)
 if issues:return dict(status='INVALID_INVENTORY_STOP',issues=issues)
 code=sorted(words);suffixes=sorted({w[i:] for w in code for i in range(1,len(w))});queue=collections.deque();states=[];seen={};edges=[];initial=[]
 def add(side,residual,left,right):
  key=(side,residual)
  if key not in seen:
   sid=len(states);seen[key]=sid;states.append(dict(id=sid,side=side,residual=residual,left=left,right=right));queue.append(sid)
  return seen[key]
 for u,v in itertools.combinations(code,2):
  if v.startswith(u):sid=add('R',v[len(u):],[u],[v]);initial.append(dict(left=u,right=v,state=sid))
  elif u.startswith(v):sid=add('L',u[len(v):],[u],[v]);initial.append(dict(left=u,right=v,state=sid))
 checked=[];witness=None
 while queue and witness is None:
  sid=queue.popleft();state=states[sid];checked.append(sid);r=state['residual'];side=state['side']
  for word in code:
   left=list(state['left']);right=list(state['right']);(right if side=='L' else left).append(word)
   if r==word:
    witness=dict(left=left,right=right,concatenation=''.join(left));edges.append(dict(source=sid,word=word,target='COLLISION'));break
   if r.startswith(word):newside=side;res=r[len(word):]
   elif word.startswith(r):newside='R' if side=='L' else 'L';res=word[len(r):]
   else:continue
   nid=add(newside,res,left,right);edges.append(dict(source=sid,word=word,target=nid))
 assert all(s['residual'] in suffixes for s in states)
 certificate=dict(suffix_universe=suffixes,state_bound=2*len(suffixes),initial=initial,states=states,edges=edges,checked=checked,complete=witness is None)
 return dict(status='NON_UD_COLLISION_WITNESS' if witness else 'UNIQUELY_DECODABLE_FINITE_CERTIFICATE',witness=witness,certificate=certificate)
def controls():
 cases=[(['0','01'],'UNIQUELY_DECODABLE_FINITE_CERTIFICATE'),(['0','01','10'],'NON_UD_COLLISION_WITNESS'),(['0','1'],'UNIQUELY_DECODABLE_FINITE_CERTIFICATE'),(['a','aa'],'NON_UD_COLLISION_WITNESS'),(['a','a'],'INVALID_INVENTORY_STOP'),(['a',''],'INVALID_INVENTORY_STOP')];out=[]
 for words,expected in cases:
  result=solve(words);assert result['status']==expected
  if result.get('witness'):
   w=result['witness'];assert w['left']!=w['right'] and ''.join(w['left'])==''.join(w['right'])==w['concatenation']
  out.append(dict(code=words,expected=expected,result=result))
 return dict(status='PASS_FINITE_CODE_CONTROLS',cases=out)
def read_units(raw):
 lines=raw.decode('utf-8').splitlines()
 if not lines or lines[0].split('\t')[0]!='unit':return [],['INVALID_UNIT_HEADER']
 # Project the first field before interpreting any remaining frequency fields.
 words=[line.partition('\t')[0] for line in lines[1:]]
 return words,[]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
 if a.controls:save('CONTROLS.json',controls(),a.check);print('CONTROLS_PASS_NO_INVENTORY_READ');return
 s=json.loads((E/'src/SPEC.json').read_text());raw=(ROOT/s['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==s['source_sha256'];words,issues=read_units(raw);issues+=valid(words,s['expected_units']);result=dict(status='INVALID_INVENTORY_STOP',issues=issues) if issues else solve(words);result.update(source_sha256=s['source_sha256'],units=len(words),alphabet=s['alphabet'],scope=s['scope']);save('CODEWORDS.json',words,a.check);save('RESULT.json',result,a.check);print(enc({k:v for k,v in result.items() if k!='certificate'}))
if __name__=='__main__':main()
