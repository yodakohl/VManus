from pathlib import Path
from fractions import Fraction
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def accepts(w,h):
 valid=[False]*(len(w)+2);valid[len(w)]=True
 for i in range(len(w)-1,-1,-1):valid[i]=valid[i+2] if w[i] in h else valid[i+1]
 return valid[0]
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');tables=read(B/'artifacts/ALL_HEAD_COUNTS.json');saved=read(B/'artifacts/RESIDUAL_WITNESSES.json');res=read(B/'artifacts/RESULT.json');old=read(R/'experiments/yolo/gdt1331_paired_word_shared_carrier_bound/artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};pattern=re.compile('|'.join(sorted(U,key=lambda s:(-len(s),s))));joins=0;checked=0;witnesses=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set()
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert pattern.findall(g[2])==r['units'];assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';joins+=1
  assert seen==set(byid);grouped={}
  for row in rows:grouped.setdefault(tuple(row['units']),[]).append(row)
  expected=[];bad_by_head={};n=len(rows)
  for h in itertools.combinations(U,3):
   bad=[];failedtypes=0;free=0
   for w,instances in grouped.items():
    if not accepts(w,h):bad.extend(instances);failedtypes+=1
    if all(u not in h for u in w):free+=len(instances);assert accepts(w,h)
   m=len(bad);expected.append({'heads':list(h),'unparsed':m,'unparsed_types':failedtypes,'unparsed_selectors':len({r['page'] for r in bad}),'parsable':n-m,'head_free':free,'bound_among_parsable':[free,n-m],'share_original_panel':[free,n]});bad_by_head[h]=sorted(bad,key=lambda r:r['id'])
  assert expected==tables[ed];checked+=len(expected);zero=[r for r in expected if r['unparsed']==0];assert len(zero)==old['readers'][ed]['compatible_head_sets']==1;assert zero[0]['heads']==old['readers'][ed]['selected_minimizing_heads'];assert zero[0]['head_free']==old['readers'][ed]['minimum_identical_source_pair_count']
  # A row lies on the envelope iff no row weakly better in both axes exists
  # with at least one strict improvement. Retain all equal coordinate ties.
  ratios=[Fraction(r['head_free'],r['parsable']) for r in expected];front={}
  for i,r in enumerate(expected):
   dominated=any(t['unparsed']<=r['unparsed'] and ratios[j]<=ratios[i] and (t['unparsed']<r['unparsed'] or ratios[j]<ratios[i]) for j,t in enumerate(expected))
   if not dominated:front.setdefault((r['unparsed'],ratios[i]),[]).append(r['heads'])
  f=[{'unparsed':cost,'lower_bound':[value.numerator,value.denominator],'heads':heads} for (cost,value),heads in sorted(front.items())];assert res['readers'][ed]['frontier']==f
  budgets={}
  for k in (0,1,2,5,10,20,50,100):budgets.setdefault(k,[]).append('count:'+str(k))
  for a,b in ((1,1000),(5,1000),(1,100),(2,100),(5,100),(1,10)):budgets.setdefault(n*a//b,[]).append('fraction:'+str(a)+'/'+str(b))
  out=[];selected=set()
  for b,labels in sorted(budgets.items()):
   indices=[i for i,r in enumerate(expected) if r['unparsed']<=b];v=min(ratios[i] for i in indices) if indices else None;ties=[expected[i] for i in indices if ratios[i]==v];out.append({'budget':b,'labels':labels,'lower_bound':[v.numerator,v.denominator] if v is not None else None,'heads':[r['heads'] for r in ties],'selected':ties[0] if ties else None})
   if ties:selected.add(tuple(ties[0]['heads']))
  assert res['readers'][ed]=={'groups':n,'head_sets':1540,'frontier':f,'budgets':out}
  witness=[{'heads':list(h),'unparsed_rows':bad_by_head[h]} for h in sorted(selected)];assert saved[ed]==witness;witnesses+=sum(len(r['unparsed_rows']) for r in witness)
 assert res['fixtures']=={'status':'PASS','prefix_cases':508,'ratio_denominators_and_ties':True}
 controls=0
 for h in ((),('x',),('y',),('x','y')):
  codes=[u for u in 'xy' if u not in h]+[u+v for u in h for v in 'xy'];lang={''}
  for size in range(7):
   for w in map(''.join,itertools.product('xy',repeat=size)):
    if any(w.endswith(c) and w[:-len(c)] in lang for c in codes):lang.add(w)
    assert accepts(w,h)==(w in lang);controls+=1
 out={'status':'PASS','source_joins':joins,'head_set_counts':checked,'selected_residual_occurrences':witnesses,'independent_prefix_controls':controls,'zero_residual_reproduces1331':True,'method':'Raw-source joins and backward DP; pairwise rational dominance frontier independent of runner grouping; exact budget ties and residual inventories.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
