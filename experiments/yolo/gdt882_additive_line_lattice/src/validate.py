#!/usr/bin/env python3
"""Independent source/count and integer-certificate verification; no producer import."""
import argparse,csv,hashlib,io,json,re,subprocess
from collections import defaultdict,Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 spec=json.loads((E/'src/SPEC.json').read_text());result=json.loads((E/'artifacts/RESULT.json').read_text());chosen=json.loads((E/'artifacts/SELECTED_LINES.json').read_text());excluded=json.loads((E/'artifacts/EXCLUSIONS.json').read_text())
 for name,digest in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 proc=subprocess.run(result['guard']['command'],cwd=ROOT,text=True,capture_output=True,check=True)
 assert hashlib.sha256(proc.stdout.encode()).hexdigest()==result['guard']['projection_sha256']
 grouped=defaultdict(list)
 for r in csv.DictReader(io.StringIO(proc.stdout),delimiter='\t'):grouped[(r['edition'],r['locus'])].append(r)
 eligible=[];reject=[]
 for loc in sorted({k[1] for k in grouped}):
  allrows=[sorted(grouped.get((ed,loc),[]),key=lambda r:int(r['source_group_index'])) for ed in spec['editions']]
  for rr in allrows:
   if not rr:continue
   assert rr[0]['left_separator']=='LINE_START' and rr[-1]['right_separator']=='LINE_END'
   assert [int(r['source_group_index']) for r in rr]==list(range(1,len(rr)+1))
   assert all(int(r['source_group_count'])==len(rr) for r in rr)
   assert all(x['right_separator']==y['left_separator'] for x,y in zip(rr,rr[1:]))
  reason=None
  if any(not rr for rr in allrows):reason='MISSING_ALTERNATE_LOCUS'
  elif any(r['kind']!='P' for rr in allrows for r in rr):reason='NON_PROSE'
  elif any(not re.fullmatch('[a-z]+',r['ivtff_group_raw']) for rr in allrows for r in rr):reason='NON_LITERAL_OR_UNCERTAIN_CHARACTER'
  elif any(r['right_separator'] not in ['DEFINITE_SPACE','UNCERTAIN_SMALL_SPACE'] for rr in allrows for r in rr[:-1]):reason='DRAWING_OR_OTHER_GAP'
  elif len({''.join(r['ivtff_group_raw'] for r in rr) for rr in allrows})!=1:reason='ALTERNATE_STRING_DISAGREEMENT'
  if reason:reject.append([loc,reason]);continue
  eligible.append(dict(locus=loc,page=allrows[0][0]['page'],literal=''.join(r['ivtff_group_raw'] for r in allrows[0]),readings=[dict(edition=rr[0]['edition'],source_group_ids=[r['source_group_id'] for r in rr],groups=[r['ivtff_group_raw'] for r in rr],internal_separators=[r['right_separator'] for r in rr[:-1]]) for rr in allrows]))
 eligible.sort(key=lambda r:(hashlib.sha256((spec['order_salt']+':'+r['locus']).encode()).hexdigest(),r['locus']))
 assert chosen==eligible and excluded==reject
 abc=sorted(set(''.join(r['literal'] for r in eligible)));assert abc==result['alphabet']
 vv=[[Counter(r['literal'])[s] for s in abc] for r in eligible]
 dd=[[a-b for a,b in zip(v,vv[0])] for v in vv[1:]]
 lat=result['lattice'];basis=lat['basis'];coefs=lat['coefficients']
 assert len(basis)==len(coefs)
 for b,coef in zip(basis,coefs):
  assert [sum(int(c)*dd[int(i)][j] for i,c in coef.items()) for j in range(len(abc))]==b
 if lat['unit_lattice']:
  assert basis==[[int(i==j) for j in range(len(abc))] for i in range(len(abc))]
  assert result['status']=='NO_NONZERO_FIXED_ADDITIVE_LINE_INVARIANT'
 else:
  # Membership certificate is valid, but nonunit completeness additionally needs all original rows reduced to zero.
  piv=[next(j for j,x in enumerate(b) if x) for b in basis]
  assert piv==sorted(set(piv))
  for d in dd:
   v=d[:]
   for b,p in zip(basis,piv):
    assert v[p]%b[p]==0
    q=v[p]//b[p];v=[x-q*y for x,y in zip(v,b)]
   assert not any(v)
 out=dict(status='PASS',source_selection_reconstructed=True,exact_integer_certificate_verified=True,unit_lattice=lat['unit_lattice'],eligible_lines=len(eligible),alphabet_size=len(abc))
 data=json.dumps(out,sort_keys=True,separators=(',',':'))+'\n';p=E/'artifacts/VALIDATION.json'
 if a.check:assert p.read_text()==data
 else:p.write_text(data)
 print(data)
if __name__=='__main__':main()
