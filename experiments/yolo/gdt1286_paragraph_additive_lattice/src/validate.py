import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
def determinant(matrix):
 a=[r[:] for r in matrix];n=len(a);sgn=1;prev=1
 if n==0:return 1
 for k in range(n-1):
  p=next((i for i in range(k,n) if a[i][k]),None)
  if p is None:return 0
  if p!=k:a[k],a[p]=a[p],a[k];sgn=-sgn
  pivot=a[k][k]
  for i in range(k+1,n):
   for j in range(k+1,n):
    num=a[i][j]*pivot-a[i][k]*a[k][j];assert num%prev==0;a[i][j]=num//prev
  for i in range(k+1,n):a[i][k]=0
  prev=pivot
 return sgn*a[-1][-1]
def check(rows,z):
 d=z['dimension'];H=z['basis'];C=z['coefficients'];assert len(H)==len(C)==z['rank'];assert all(len(row)==d for row in rows+H)
 assert 0<=z['rows_processed']<=len(rows)
 used=set()
 for h,c in zip(H,C):
  out=[0]*d
  for i,v in c.items():
   k=int(i);assert 0<=k<z['rows_processed'] and type(v)==int;used.add(k)
   for j in range(d):out[j]+=v*rows[k][j]
  assert out==h
 assert sorted(used)==z['used_indices']
 pivots=[]
 for h in H:
  k=next(i for i,x in enumerate(h) if x);assert h[k]>0 and (not pivots or k>pivots[-1]);pivots.append(k)
 for r in rows:
  rem=r[:]
  for k,h in zip(pivots,H):
   q,remainder=divmod(rem[k],h[k]);assert remainder==0
   rem=[a-q*b for a,b in zip(rem,h)]
  assert not any(rem)
 index=abs(determinant(H)) if len(H)==d else None
 assert index==z['index'];I=[[int(i==j) for j in range(d)] for i in range(d)]
 assert z['unit_lattice']==(H==I)
 if index==1:assert H==I
 return index

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 old=ROOT/'experiments/yolo/gdt1259_paragraph_integer_balance';source=json.loads((old/'artifacts/CENSUS.json').read_text());alphabet=json.loads((old/'src/SPEC.json').read_text())['working_signs'];matrices=json.loads((B/'artifacts/MATRICES.json').read_text());cert=json.loads((B/'artifacts/CERTIFICATES.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text())
 for reader,N in [('ZL3b',180),('IT2a',379)]:
  records=source[reader];m=matrices[reader];r=result['readers'][reader];z=cert[reader]
  assert len(records)==N and m['records']==records and m['columns']==alphabet+['COMMON_TOTAL_NEGATIVE']
  assert len(set(alphabet))==22 and all(any(p['counts'][j] for p in records) for j in range(22))
  assert all(not p['page'].startswith('f84') and p['page']!='f116v' for p in records)
  rows=[p['counts']+[-1] for p in records];assert m['matrix']==rows;index=check(rows,z)
  assert r['population_paragraphs']==N and r['pages']==len({p['page'] for p in records})
  assert r['rank']==z['rank'] and r['dimension']==23 and r['index']==index and r['processed_rows']==z['rows_processed']
  assert r['certificate_rows']==len(z['used_indices']) and r['certificate_ids']==[records[i]['id'] for i in z['used_indices']]
  assert r['status']==('ADDITIVE_PARAGRAPH_INVARIANT_EXCLUDED' if index==1 else 'NONTRIVIAL_QUOTIENT_CAPACITY')
 expected='BOTH_READERS_ALL_ABELIAN_PARAGRAPH_INVARIANTS_EXCLUDED' if all(c['index']==1 for c in cert.values()) else 'NONTRIVIAL_QUOTIENT_OR_MIXED';assert result['status']==expected
 fixtures=json.loads((B/'artifacts/FIXTURES.json').read_text());assert len(fixtures)==6 and all(f['status']=='PASS' for f in fixtures[:4])
 for f in fixtures[4:]:assert check(f['matrix'],f['lattice'])==f['expected_index']
 # Independent exhaustive modular checks for the two small paragraph fixtures.
 for m in range(2,9):
  for A in ([[2,-1],[3,-1]],[[2,-1],[4,-1]]):
   solutions=[(w,c) for w in range(m) for c in range(m) if all((row[0]*w+row[1]*c)%m==0 for row in A)]
   assert len(solutions)==(1 if A[1][0]==3 or m%2 else 2)
 out={'status':'PASS','source_count_rows':sum(len(r) for r in source.values()),'readers':{r:{'rank':z['rank'],'index':z['index'],'integer_identity_replayed':z['unit_lattice']} for r,z in cert.items()},'independence':'No import of lattice reduction; exact coefficient products, every-row integer membership and Bareiss determinant. Cached1259source reconstruction inherited, not repeated.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
