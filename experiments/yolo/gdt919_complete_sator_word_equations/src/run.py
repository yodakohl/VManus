import collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];WORDS=['sator','arepo','tenet','opera','rotas']
def dump(n,d):(E/'artifacts'/n).write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n')
def admissible(ws):return len(set(ws))==5 and min(map(len,ws))>=5 and len(ws[0])==len(ws[4]) and len(ws[1])==len(ws[3])
def solve(ws):
 if not admissible(ws):return []
 w1,w2,w3,w4,w5=ws;n=len(w1);out=[]
 for ns in range(1,n-3):
  s=w1[:ns]
  if not w5.endswith(s):continue
  for nr in range(1,n-ns-2):
   r=w1[n-nr:]
   if not w5.startswith(r):continue
   u=w1[ns:n-nr];v=w5[nr:n-ns]
   for na in range(1,len(u)-1):
    a=u[:na]
    if not v.endswith(a):continue
    for no in range(1,len(u)-na):
     o=u[len(u)-no:]
     if not v.startswith(o):continue
     t=u[na:len(u)-no]
     if v[no:len(v)-na]!=t:continue
     if len({s,a,t,o,r})!=5:continue
     pref=a+r;suff=o
     if not w2.startswith(pref) or not w2.endswith(suff) or len(w2)<len(pref)+len(suff)+2:continue
     inner=w2[len(pref):len(w2)-len(suff)]
     for ne in range(1,len(inner)):
      e,p=inner[:ne],inner[ne:]
      if w4!=o+p+e+r+a:continue
      pref3=t+e;suff3=e+t
      if not w3.startswith(pref3) or not w3.endswith(suff3) or len(w3)<=len(pref3)+len(suff3):continue
      nn=w3[len(pref3):len(w3)-len(suff3)];key=dict(zip('satorepn',[s,a,t,o,r,e,p,nn]))
      if len(set(key.values()))!=8:continue
      assert [''.join(key[c] for c in w) for w in WORDS]==ws
      out.append(key)
 return out

def intake(ed):
 parent=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer';spec=json.loads((parent/'src/SPEC.json').read_text());out=[]
 for phase in ['DISCOVERY','EVALUATION']:
  d=json.loads((parent/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text())
  for row in d['lines']:
   m=row['metadata'];assert m['page'] in spec['partitions'][phase] and not m['page'].startswith('f84');out.append((m,[dict(zip(d['group_columns'],g)) for g in row['groups']]))
 return sorted(out,key=lambda r:(r[0]['page'],int(r[0]['source_row_index'])))
def valid(gs,whole=False,n=None):
 if not gs or not all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs):return False
 if whole and [int(g['source_group_index']) for g in gs]!=list(range(1,n+1)):return False
 return all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
def analyze(rows):
 den={k:dict(windows=0,eligible=0,length_and_distinct=0,fit_windows=0,keys=0) for k in ['GROUP','LINE']};hits=[];by=collections.defaultdict(list)
 def inspect(carrier,loc,start,ok,ws,ids,page):
  d=den[carrier];d['windows']+=1
  if not ok:return
  d['eligible']+=1
  if not admissible(ws):return
  d['length_and_distinct']+=1;matched=False
  for order,ww in [('SATOR',ws),('ROTAS',list(reversed(ws)))]:
   keys=solve(ww)
   if keys:hits.append(dict(carrier=carrier,source_order=order,page=page,loci=loc,start=start,words=ws,source_ids=ids,keys=keys));d['keys']+=len(keys);matched=True
  d['fit_windows']+=int(matched)
 for m,gs in rows:
  by[m['page']].append((m,gs))
  for i in range(len(gs)-4):
   part=gs[i:i+5];inspect('GROUP',[m['locus']],int(part[0]['source_group_index']),valid(part),[g['ivtff_group_raw'] for g in part],[[g['source_group_id']] for g in part],m['page'])
 for page,lines in sorted(by.items()):
  for i in range(len(lines)-4):
   part=lines[i:i+5];inspect('LINE',[m['locus'] for m,gs in part],i,all(valid(gs,True,int(m['source_group_count'])) for m,gs in part),[''.join(g['ivtff_group_raw'] for g in gs) for m,gs in part],[[g['source_group_id'] for g in gs] for m,gs in part],page)
 return dict(lines=len(rows),selectors=len(by),denominators=den,hits=hits)
def main():
 lock=json.loads((E/'PREREG_LOCK.json').read_text());assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in lock['files'].items());out={}
 for ed in ['ZL3b','IT2a','RF1b']:
  r=analyze(intake(ed));dump(f'CENSUS_{ed}.json',r);out[ed]={k:v for k,v in r.items() if k!='hits'};out[ed]['fit_records']=len(r['hits'])
 result=dict(status='COMPLETE_FORMULA_CANDIDATE' if any(d['fit_records'] for d in out.values()) else 'NO_COMPLETE_SATOR_EQUATION_FIT',readings=out,meaning_claims=0,significance_claim=False,source_exposed=True);dump('RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
