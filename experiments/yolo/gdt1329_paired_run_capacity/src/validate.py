from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,re
from fractions import Fraction
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split(),key=lambda x:(-len(x),x));PAT=re.compile('|'.join(A))
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');saved=read(B/'artifacts/CELLS.json');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;twos=0;nc=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();cells=collections.defaultdict(list);slots={};families={}
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';u=PAT.findall(g[2]);assert u==r['units'];joins+=1;source=[];runlengths=[];indices=[];fs=[]
     for unit,block in itertools.groupby(u):
      n=len(list(block))
      if unit in ('e','i'):indices.append(len(source));fs.append(unit);runlengths.append(n);source.append(unit)
      else:source.extend([unit]*n)
     if len(runlengths)!=2:continue
     twos+=1;k=(m['page'],tuple(source));cells[k].append({'id':g[0],'raw':g[2],'lengths':runlengths});slots[k]=indices;families[k]=''.join(fs)
  assert seen==set(byid);expected=[]
  for k,ev in sorted(cells.items()):
   if len(ev)<3 or any(len(set(e['lengths'][i] for e in ev))<2 for i in [0,1]):continue
   expected.append({'page':k[0],'leaf':int(re.match(r'f(\d+)',k[0])[1]),'source':list(k[1]),'slots':slots[k],'families':families[k],'events':sorted(ev,key=lambda x:x['id'])})
  assert expected==saved[ed];nc+=len(expected);leaves=sorted({c['leaf'] for c in expected});n=sum(len(c['events']) for c in expected);passed=len(expected)>=20 and n>=100 and len(leaves)>=10
  assert result['readers'][ed]=={'status':'NOMINAL_CAPACITY_ONLY' if passed else 'NO_CAPACITY_UPPER_BOUND','groups':len(rows),'exactly_two_run_occurrences':sum(len(v) for v in cells.values()),'exactly_two_run_cells':len(cells),'eligible_cells':len(expected),'eligible_occurrences':n,'physical_leaves':leaves,'families':{f:{'cells':sum(c['families']==f for c in expected),'occurrences':sum(len(c['events']) for c in expected if c['families']==f)} for f in ['ee','ei','ie','ii']},'permutations_run':0}
 # Independent centered rational computation for the cautionary toy.
 vals=[]
 for positions in itertools.combinations(range(4),2):
  y=[2 if j in positions else 1 for j in range(4)];x=[1,1,1,2];xx=[Fraction(v)-Fraction(sum(x),4) for v in x];yy=[Fraction(v)-Fraction(sum(y),4) for v in y];vals.append(sum(a*b for a,b in zip(xx,yy))**2/(sum(a*a for a in xx)*sum(b*b for b in yy)))
 assert vals==[Fraction(1,3)]*6 and result['fixtures']=={'status':'PASS','nominal_but_squared_correlation_invariant_permutations':6,'invariant_squared_correlation':'1/3'};assert result['status']==('PAIRED_RUN_CAPACITY_STOP_ALL_READINGS' if all(r['status']=='NO_CAPACITY_UPPER_BOUND' for r in result['readers'].values()) else 'READER_SPECIFIC_NOMINAL_CAPACITY')
 out={'status':'PASS','source_joins':joins,'exactly_two_run_occurrences':twos,'nominally_eligible_cells':nc,'toy_invariant_pairings':6,'native_permutations':0,'method':'Independent original source traversal, raw-token groupby extraction, full cell equality, exact threshold checks and rational fixture; no runner imported.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
