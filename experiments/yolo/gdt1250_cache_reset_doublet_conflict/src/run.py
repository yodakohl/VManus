import csv,hashlib,itertools,json,re,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parents[1];ART=BASE/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((BASE/'src/SPEC.json').read_text())
 # Source-free check of the stated mandatory-hit, disjoint-mode invariant.
 cases=0
 for cap in (1,2,3):
  for n in range(1,8):
   for seq in itertools.product('abc',repeat=n):
    cache=[];out=[]
    for w in seq:
     out.append('R'+str(cache.index(w)) if w in cache else 'L'+w)
     if w in cache:cache.remove(w)
     cache.insert(0,w);del cache[cap:]
    assert out[0].startswith('L')
    assert all(a.startswith('R') for a,b in zip(out,out[1:]) if a==b)
    cases+=1
 for p,h in s['inputs'].items():assert sha(ROOT/p)==h,p
 pages=[r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')]
 assert len(pages)==179 and not any(p.startswith('f84') or p=='f116v' for p in pages)
 if not (ART/'METADATA.tsv').exists():
  cmd=['./vmanus-exp','query-tsv','experiments/semantic_assumptions/results/source_separator_transcription.tsv','--selector','page']
  for p in pages:cmd+=['--allow',p]
  cmd+=['--columns',','.join(s['metadata_columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
  r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
  (ART/'METADATA.tsv').write_text(r.stdout)
  (ART/'METADATA_RECEIPT.json').write_text(json.dumps({'command':cmd,'guard':r.stderr,'sha256':sha(ART/'METADATA.tsv')},indent=2)+'\n')
 assert sha(ART/'METADATA.tsv')==json.loads((ART/'METADATA_RECEIPT.json').read_text())['sha256']
 flags={}
 for r in csv.DictReader((ART/'METADATA.tsv').open(),delimiter='\t'):
  assert r['page'] in pages
  if r['kind']=='P' and r['source_group_index']=='1' and r['edition'] in ('ZL3b','IT2a'):
   k=(r['edition'],r['locus']);assert k not in flags;flags[k]=r['paragraph_start']
 starts={l for e,l in flags if e=='ZL3b' and flags[e,l]=='1' and flags.get(('IT2a',l))=='1'}
 lines=defaultdict(list)
 for r in csv.DictReader((ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/artifacts/GUARDED.tsv').open(),delimiter='\t'):
  assert r['page'] in pages
  if r['kind']=='P':lines[r['edition'],r['locus']].append(r)
 for rs in lines.values():rs.sort(key=lambda r:int(r['source_group_index']))
 ev={e:{'doublets':{},'starts':{}} for e in s['readers']}
 def add(e,k,w,l,i):ev[e][k].setdefault(w,[]).append({'locus':l,'index':i})
 for (e,l),rs in sorted(lines.items()):
  a=rs[0]
  if l in starts and a['source_group_index']=='1' and a['left_separator']=='LINE_START' and a['right_separator'] in ('DEFINITE_SPACE','LINE_END') and re.fullmatch('[a-z]+',a['ivtff_group_raw']):add(e,'starts',a['ivtff_group_raw'],l,1)
  for i in range(1,len(rs)-2):
   p,a,b,n=rs[i-1:i+3];w=a['ivtff_group_raw'];edges=[(p,a),(a,b),(b,n)]
   if re.fullmatch('[a-z]+',w) and w==b['ivtff_group_raw'] and all(int(y['source_group_index'])==int(x['source_group_index'])+1 and x['right_separator']==y['left_separator']=='DEFINITE_SPACE' for x,y in edges):add(e,'doublets',w,l,int(a['source_group_index']))
 result={'fixtures':cases,'consensus_start_loci':len(starts),'readers':{}};witness=[]
 for e in s['readers']:
  ds,ps=ev[e]['doublets'],ev[e]['starts'];conf=sorted(ds.keys()&ps.keys())
  result['readers'][e]={'doublet_types':len(ds),'doublet_events':sum(map(len,ds.values())),'start_types':len(ps),'start_events':sum(map(len,ps.values())),'conflicting_types':conf,'status':'CONTRADICTED' if conf else ('NO_COUNTERCASE' if ds and ps else 'NO_CAPACITY')}
  for w in conf:
   d,p=ds[w][0],ps[w][0];witness.append({'edition':e,'form':w,'doublet':d,'start':p,'doublet_line':lines[e,d['locus']],'start_line':lines[e,p['locus']]})
 for name,obj in [('RESULT',result),('EVENTS',ev),('WITNESSES',witness)]: (ART/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
