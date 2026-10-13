from pathlib import Path
import json,gzip,hashlib,csv
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1368_fragment_window_nucleus_capacity/artifacts/WINDOWS.json.gz').read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={};assert 'f100r' in allow
 for reader,windows in sorted(data.items()):
  chosen={};together=False
  for win in windows:
   rows=win['sources']
   for row in rows:
    if row['page']=='f100r' and row['locus']=='f100r.14' and int(row['source_group_index']) in (5,6):
     i=int(row['source_group_index']);assert row['edition']==reader and row['id']==f'{reader}|f100r.14|G{i:03d}' and row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
     if i in chosen:assert chosen[i]==row
     chosen[i]=row
   for a,b in zip(rows,rows[1:]):
    if a['id']==f'{reader}|f100r.14|G005' and b['id']==f'{reader}|f100r.14|G006':together=True
  sources=[chosen[i] for i in sorted(chosen)]
  if len(sources)!=2 or not together:panels[reader]={'status':'MISSING','sources':sources,'forward_overlaps':[],'reversed_record_overlaps':[]};continue
  u,v=(r['ivtff_group_raw'] for r in sources);forward=[];reverse=[]
  for n in range(1,min(len(u),len(v))):
   if u[-n:]==v[:n]:forward.append({'length':n,'piece':u[-n:]})
   if u[:n]==v[-n:]:reverse.append({'length':n,'piece':u[:n]})
  status='BOTH_ORIENTATIONS_EXCLUDED' if not forward and not reverse else 'PAIR_COMPATIBLE' if forward and reverse else 'ORIENTATION_SPECIFIC'
  panels[reader]={'status':status,'sources':sources,'forward_overlaps':forward,'reversed_record_overlaps':reverse};print(reader,u,v,status)
 (B/'artifacts/RESULT.json').write_text(json.dumps({'status':'LITERAL_OVERLAP_COUNTEREXAMPLE','panels':panels},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
