from pathlib import Path
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(n):return json.loads((B/n).read_text())
def main():
 for p,h in read('src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 source=json.loads(gzip.decompress((R/'experiments/yolo/gdt1342_qoky_written_predecessor/artifacts/SOURCE.json.gz').read_bytes()))
 allowed={x['page'] for x in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};assert len(allowed)==179
 assert all(r['page'] in allowed and not r['page'].startswith('f84') and r['page'] not in {'f1r','f116v'} for r in source)
 rows=[r for r in source if r['raw']=='daldy' or r['raw']=='olaiin'];saved=read('artifacts/SOURCE_CASES.json');assert [x['source'] for x in saved]==rows
 pattern=re.compile('ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]');strict=[]
 for s in saved:
  r=s['source'];tokens=pattern.findall(r['raw']);valid=''.join(tokens)==r['raw'];clear=all(r[k] in ('DEFINITE_SPACE','LINE_START','LINE_END') for k in ('left','right'))
  expected='STRICT' if valid and clear else 'PARSE_AND_SEAM_UNCERTAIN' if not valid and not clear else 'PARSE_UNCERTAIN' if not valid else 'SEAM_UNCERTAIN'
  assert s['classification']==expected
  if expected=='STRICT':strict.append(r)
 result=read('artifacts/RESULT.json')['readers']
 for ed,d in result.items():
  rr=[r for r in rows if r['edition']==ed];ss=[r for r in strict if r['edition']==ed]
  assert d['all_P_counts']=={w:sum(r['raw']==w for r in rr) for w in ('daldy','olaiin')}
  assert d['strict_counts']=={w:sum(r['raw']==w for r in ss) for w in ('daldy','olaiin')}
  assert d['strict_pages']=={w:sorted({r['page'] for r in ss if r['raw']==w}) for w in ('daldy','olaiin')}
  ds=[r for r in ss if r['raw']=='daldy' and r['locus']=='f45r.10'];os=sorted([r for r in ss if r['raw']=='olaiin'],key=lambda r:(r['row'],r['index']))
  enough=all(d['strict_counts'][w]>=2 for w in d['strict_counts']) and bool(ds) and bool(os)
  assert d['decision']==('TWO_CLASS_SORT_CONTRADICTED' if enough else 'SOURCE_CAPACITY_UNRESOLVED')
  assert d['witnesses']==([ds[0],os[0]] if enough else [])
 # Direct sorting, independently of the runner's graph edges.
 examined=0;solutions=[]
 for bits in itertools.product([0,1],repeat=3):
  c=dict(zip('dal',bits))
  for order in itertools.permutations('dal'):
   rank={x:i for i,x in enumerate(order)};valid=True
   for word in ('dald','la'):
    for color in (0,1):
     seq=[rank[x] for x in word if c[x]==color]
     if seq!=sorted(seq):valid=False
   examined+=1
   if valid:solutions.append([c,order])
 assert examined==48 and not solutions
 proof=read('artifacts/PROOF.json');assert len(proof['assignments'])==8 and proof['minimum_classes_for_triangle']==3
 for a in proof['assignments']:assert a['violated_edges']==[e for e in proof['edges'] if a['classes'][e[0]]==a['classes'][e[1]]]
 out={'status':'PASS','source_rows':len(rows),'independent_class_order_cases':examined,'solutions':len(solutions),'claim':'Source and fixed-code implication only; no native semantic or palaeographic confirmation.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
