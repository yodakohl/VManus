from pathlib import Path
from collections import Counter
import gzip,hashlib,json,itertools
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 source=json.loads(gzip.decompress((R/'experiments/yolo/gdt1342_qoky_written_predecessor/artifacts/SOURCE.json.gz').read_bytes()))
 classifications=json.loads(gzip.decompress((R/'experiments/yolo/gdt1343_default_vowel_terminal_capacity/artifacts/CLASSIFICATION.json.gz').read_bytes()))
 classes={x[0]:x[1] for x in classifications};assert len(classes)==len(source)==94855
 forms=('daldy','olaiin');rows=[r for r in source if r['raw'] in forms];result={}
 assert all(r['id'] in classes for r in source)
 for ed in ['ZL3b','IT2a','RF1b']:
  rr=[r for r in rows if r['edition']==ed];strict=[r for r in rr if classes[r['id']]=='STRICT'];counts={w:sum(r['raw']==w for r in strict) for w in forms}
  ds=[r for r in strict if r['raw']=='daldy' and r['locus']=='f45r.10'];os=sorted([r for r in strict if r['raw']=='olaiin'],key=lambda r:(r['row'],r['index']))
  enough=min(counts.values())>=2 and bool(ds) and bool(os)
  result[ed]={'all_P_counts':dict(Counter(r['raw'] for r in rr)),'strict_counts':counts,'strict_pages':{w:sorted({r['page'] for r in strict if r['raw']==w}) for w in forms},'decision':'TWO_CLASS_SORT_CONTRADICTED' if enough else 'SOURCE_CAPACITY_UNRESOLVED','witnesses':[ds[0],os[0]] if enough else []}
 edges=[['d','a'],['d','l'],['a','l']]
 assignments=[]
 for bits in itertools.product([0,1],repeat=3):
  c=dict(zip(['d','a','l'],bits));bad=[edge for edge in edges if c[edge[0]]==c[edge[1]]];assert bad
  assignments.append({'classes':c,'violated_edges':bad})
 save('SOURCE_CASES.json',[dict(source=r,classification=classes[r['id']]) for r in rows]);save('PROOF.json',{'edges':edges,'assignments':assignments,'minimum_classes_for_triangle':3,'claim':'Necessary triangle only; not complete native three-class feasibility.'})
 save('RESULT.json',{'readers':result,'claim_ceiling':'Fixed preserved-mask two-class sorting under inherited unit/group readings only; no meaning or general composition exclusion.'});print(json.dumps({ed:{k:v for k,v in d.items() if k!='strict_pages'} for ed,d in result.items()},indent=2))
if __name__=='__main__':main()
