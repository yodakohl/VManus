import collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def dump(p,d):p.write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n')
def fit(ws,side):
 if not all(len(b)<len(a) and (a.startswith(b) if side=='RIGHT' else a.endswith(b)) for a,b in zip(ws,ws[1:])):return False,None
 chunks=[a[len(b):] if side=='RIGHT' else a[:len(a)-len(b)] for a,b in zip(ws,ws[1:])]+[ws[-1]]
 letters=list('abracadabra'[::-1] if side=='RIGHT' else 'abracadabra');key={}
 for letter,chunk in zip(letters,chunks):
  if letter in key and key[letter]!=chunk:return True,None
  key[letter]=chunk
 if len(set(key.values()))!=5:return True,None
 return True,key

def load(ed,s):
 out=[]
 for phase in ['DISCOVERY','EVALUATION']:
  p=ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json';d=json.loads(p.read_text())
  for row in d['lines']:
   m=row['metadata'];assert m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84')
   gs=[dict(zip(d['group_columns'],g)) for g in row['groups']];out.append((m,gs))
 return sorted(out,key=lambda z:(z[0]['page'],int(z[0]['source_row_index'])))
def valid(gs,complete=False,n=None):
 if not gs or not all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs):return False
 if complete and [int(g['source_group_index']) for g in gs]!=list(range(1,n+1)):return False
 return all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
def analyze(rows):
 den={k:dict(windows=0,eligible=0,RIGHT_nested=0,LEFT_nested=0,RIGHT_fits=0,LEFT_fits=0) for k in ['GROUP','LINE']};hits=[]
 def inspect(carrier,window,ok,ws,ids,loci,page):
  d=den[carrier];d['windows']+=1
  if not ok:return
  d['eligible']+=1
  for side in ['RIGHT','LEFT']:
   nested,key=fit(ws,side);d[side+'_nested']+=int(nested)
   if key is not None:
    d[side+'_fits']+=1;hits.append(dict(carrier=carrier,side=side,page=page,window=window,loci=loci,source_ids=ids,rungs=ws,key=key))
 by=collections.defaultdict(list)
 for m,gs in rows:
  by[m['page']].append((m,gs))
  for start in range(len(gs)-10):
   part=gs[start:start+11];inspect('GROUP',start,valid(part),[g['ivtff_group_raw'] for g in part],[[g['source_group_id']] for g in part],[m['locus']],m['page'])
 for page,lines in sorted(by.items()):
  for start in range(len(lines)-10):
   part=lines[start:start+11];ok=all(valid(gs,True,int(m['source_group_count'])) for m,gs in part)
   inspect('LINE',start,ok,[''.join(g['ivtff_group_raw'] for g in gs) for m,gs in part],[[g['source_group_id'] for g in gs] for m,gs in part],[m['locus'] for m,gs in part],page)
 return dict(lines=len(rows),selectors=len(by),denominators=den,hits=hits)
def main():
 lock=json.loads((E/'PREREG_LOCK.json').read_text());assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in lock['files'].items())
 s=json.loads((ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json').read_text());out={}
 for ed in s['editions']:
  r=analyze(load(ed,s));dump(E/'artifacts'/f'CENSUS_{ed}.json',r);out[ed]={k:v for k,v in r.items() if k!='hits'};out[ed]['fits']=len(r['hits'])
 result=dict(status='COMPLETE_CANDIDATE_REQUIRES_NATIVE_TEST' if any(v['fits'] for v in out.values()) else 'NO_COMPLETE_FIXED_CHARM_FIT',readings=out,meaning_claims=0,significance_claim=False,source_exposed=True);dump(E/'artifacts/RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
