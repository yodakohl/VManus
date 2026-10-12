from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,itertools,json,re,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(p,j):
 raw=(json.dumps(j,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def odd_runs(w,e):
 ans=[];i=0
 while i<len(w):
  if w[i]!=e:i+=1;continue
  j=i+1
  while j<len(w) and w[j]==e:j+=1
  if (j-i)%2:ans.append([i,j])
  i=j
 return ans
def unquote(w,e):
 out=[];i=0
 while i<len(w):
  a=w[i];out.append(a)
  if a==e:
   if i+1==len(w) or w[i+1]!=e:return None
   i+=2
  else:i+=1
 return tuple(out)
def controls():
 cases=roundtrips=0
 for n in range(1,8):
  for w in itertools.product('abc',repeat=n):
   for e in 'abc':
    assert (not odd_runs(w,e))==(unquote(w,e) is not None)
    if n<=5:
     quoted=tuple(u for a in w for u in ((a,a) if a==e else (a,)));assert unquote(quoted,e)==w and not odd_runs(quoted,e);roundtrips+=1
    cases+=1
 out={'status':'PASS','source_free':True,'parity_parser_cases':cases,'literal_roundtrips':roundtrips,'E_first_is_deliberately_unconstrained':True};save(B/'artifacts/CONTROLS.json',out);print(out)
def leaf(row):return int(re.match(r'f(\d+)',row['page'])[1])
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={};cert={}
 for reader,rows in sorted(data.items()):
  full=defaultdict(list)
  for row in rows:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',row['ivtff_group_raw'])==row['units'];assert ''.join(row['units'])==row['ivtff_group_raw'];full[tuple(row['units'])].append(row)
  for panel in ['FULL','GE2']:
   occ={w:rr for w,rr in sorted(full.items()) if panel=='FULL' or len({leaf(r) for r in rr})>=2};alpha=sorted({a for w in occ for a in w});assert len(alpha)==22;total=sum(map(len,occ.values()));keys={};packet={}
   for e in alpha:
    starts={w:rr for w,rr in occ.items() if w[0]==e};literal={w:rr for w,rr in occ.items() if w[0]!=e};containing={w:rr for w,rr in literal.items() if e in w};bad={w:rr for w,rr in containing.items() if odd_runs(w,e)}
    violations=[{'word':list(w),'odd_intervals':odd_runs(w,e),'source_ids':[r['id'] for r in rr]} for w,rr in bad.items()];packet[e]=violations
    witness=None
    if bad:
     w=min(bad);rr=bad[w];witness={'word':list(w),'odd_intervals':odd_runs(w,e),'count':len(rr),'physical_leaves':sorted({leaf(r) for r in rr}),'first_row':rr[0]}
    count=sum(map(len,bad.values()));den=sum(map(len,containing.values()));keys[e]={'granted_initial_groups':sum(map(len,starts.values())),'literal_groups':sum(map(len,literal.values())),'literal_containing_groups':den,'violating_groups':count,'violating_types':len(bad),'violating_physical_leaves':sorted({leaf(r) for rr in bad.values() for r in rr}),'conditional_fraction':[count,den],'witness':witness,'survives':not bad}
   name=reader+'_'+panel;survivors=[e for e,v in keys.items() if v['survives']];panels[name]={'groups':total,'types':len(occ),'keys':keys,'surviving_markers':survivors,'status':'NO_MARKER' if not survivors else 'NECESSARY_SYNTAX_SURVIVORS'};cert[name]=packet;print(name,'survivors',survivors,'q',keys['q']['conditional_fraction'],flush=True)
 save(B/'artifacts/RESULT.json',{'status':'EXACT_QUOTED_LITERAL_MARKER_SCREEN','panels':panels,'scope':'Necessary one-prefix-marker/doubled-literal syntax only; initial-marker groups unrestricted, no language/phonetics/meaning.'});save(B/'artifacts/VIOLATIONS.json.gz',cert)
if __name__=='__main__':controls() if '--controls' in sys.argv else main()
