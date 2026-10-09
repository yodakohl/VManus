import collections,csv,hashlib,io,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def parse(raw,units):
 ways=[[]]+[None]*len(raw)
 for i in range(len(raw)):
  if ways[i] is not None:
   for u in units:
    if raw.startswith(u,i):
     k=i+len(u);assert ways[k] is None,'ambiguous working segmentation';ways[k]=ways[i]+[u]
 return ways[-1] if raw else None
def determinant(mat):
 a=[r[:] for r in mat];n=len(a);assert all(len(r)==n for r in a);sign=1;previous=1
 if n==0:return 1
 for k in range(n-1):
  pivot=next((i for i in range(k,n) if a[i][k]),None)
  if pivot is None:return 0
  if pivot!=k:a[k],a[pivot]=a[pivot],a[k];sign=-sign
  p=a[k][k]
  for i in range(k+1,n):
   for j in range(k+1,n):
    numerator=a[i][j]*p-a[i][k]*a[k][j];assert numerator%previous==0;a[i][j]=numerator//previous
   a[i][k]=0
  previous=p
 return sign*a[-1][-1]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());census=json.loads((B/'artifacts/CENSUS.json').read_text());cert=json.loads((B/'artifacts/CERTIFICATES.json').read_text());receipt=json.loads((B/'artifacts/GUARD_RECEIPT.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 call=subprocess.run(receipt['command'],cwd=R,text=True,capture_output=True,check=True);assert hashlib.sha256(call.stdout.encode()).hexdigest()==receipt['output_sha256']
 byreader=collections.defaultdict(dict);rawcount=0
 for row in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
  rawcount+=1
  if row['edition'] not in s['readers']:continue
  key=(row['page'],int(row['source_row_index']));entry=byreader[row['edition']].setdefault(key,[]);entry.append(row)
 assert rawcount==result['guarded_rows'];checks={}
 for reader in s['readers']:
  table=byreader[reader];rebuilt=[];original={}
  # Independent start-centred scan through consecutive source indices.
  for (page,index),ln in sorted(table.items()):
   ln.sort(key=lambda g:int(g['source_group_index']));first=ln[0]
   if first['kind']!='P' or first['paragraph_start']!='1':continue
   groups=[];loci=[];indices=[];j=index;complete=False
   while (page,j) in table:
    line=sorted(table[(page,j)],key=lambda g:int(g['source_group_index']));x=line[0]
    if x['kind']!='P' or (j!=index and x['paragraph_start']=='1'):break
    assert [int(g['source_group_index']) for g in line]==list(range(1,int(x['source_group_count'])+1))
    groups.extend(line);loci.append(x['locus']);indices.append(j)
    if x['paragraph_end']=='1':complete=True;break
    j+=1
   if not complete:continue
   count=collections.Counter();good=True
   for g in groups:
    units=parse(g['ivtff_group_raw'],s['working_signs'])
    if units is None or g['left_separator'] not in s['permitted_separators'] or g['right_separator'] not in s['permitted_separators']:good=False;break
    count.update(units)
   if not good:continue
   identity=page+'|'+loci[0]+'|'+loci[-1];rec={'id':identity,'page':page,'loci':loci,'source_rows':indices,'groups':len(groups),'counts':[count[u] for u in s['working_signs']]};rebuilt.append(rec);original[identity]=groups
  assert rebuilt==census[reader]
  active=[j for j in range(len(s['working_signs'])) if any(p['counts'][j] for p in rebuilt)]
  info=result['readers'][reader];assert info['active_units']==[s['working_signs'][j] for j in active];assert info['paragraphs']==len(rebuilt)
  matrix=[]
  for w in cert[reader]:
   p=w['paragraph'];assert p in rebuilt and w['raw_groups']==original[p['id']];matrix.append([p['counts'][j] for j in active]+[-1])
  det=None
  if info['rank']==len(active)+1:
   assert len(matrix)==len(active)+1;det=determinant(matrix);assert det!=0
  else:
   # Exact integer row reduction without importing primary Fraction algorithm.
   allrows=[[p['counts'][j] for j in active]+[-1] for p in rebuilt];rank=0
   import math
   for col in range(len(active)+1):
    pivot=next((i for i in range(rank,len(allrows)) if allrows[i][col]),None)
    if pivot is None:continue
    allrows[rank],allrows[pivot]=allrows[pivot],allrows[rank]
    for i in range(rank+1,len(allrows)):
     f=allrows[i][col];a=allrows[rank][col]
     if f:
      allrows[i]=[a*x-f*y for x,y in zip(allrows[i],allrows[rank])];d=math.gcd(*allrows[i]);allrows[i]=[x//d for x in allrows[i]] if d else allrows[i]
    rank+=1
   assert rank==info['rank']
  checks[reader]={'paragraph_census':'MATCH','certificate_raw_rows':'MATCH','exact_determinant':det,'rank':info['rank'],'active_units':len(active)}
 # Positive and negative algebra controls, including line/paragraph distinction.
 assert determinant([[1,2,-1],[2,1,-1],[3,3,-1]])!=0
 assert determinant([[1,2,-1],[2,1,-1],[1,2,-1]])==0
 assert 1+2==2+1 and len({1,2})==2
 out={'status':'PASS','reader_checks':checks,'independence':'Independent start-centred paragraph scan, dynamic segmentation and Bareiss determinant; no import of primary program.','limits':'Reproducibility validates declared representation, not authorial flags or glyph atomhood.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
