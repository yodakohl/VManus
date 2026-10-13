from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/CACHE).read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={}
 for reader,rows in sorted(data.items()):
  leaves=defaultdict(set)
  for row in rows:
   assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';f=row['ivtff_group_raw'];u=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',f);assert ''.join(u)==f and u==row['units'];leaves[f].add(int(re.match(r'f(\d+)',row['page']).group(1)))
  alphabet=sorted({c for row in rows for c in row['ivtff_group_raw']})
  for panel in ['FULL','GE2']:
   selected=[r for r in rows if panel=='FULL' or len(leaves[r['ivtff_group_raw']])>=2]
   chars={c:{'char':c,**{k+suffix:(0 if suffix=='_count' else None) for k in ['nonfinal','noninitial','middle'] for suffix in ['_count','_first']}} for c in alphabet}
   for row in selected:
    w=row['ivtff_group_raw']
    for i,c in enumerate(w):
     z=chars[c]
     flags={'nonfinal':i<len(w)-1,'noninitial':i>0,'middle':0<i<len(w)-1}
     for key,yes in flags.items():
      if yes:
       z[key+'_count']+=1
       if z[key+'_first'] is None:z[key+'_first']={'source':row,'offset_zero_based':i}
   counts={key:sum(z[key+'_count']>0 for z in chars.values()) for key in ['nonfinal','noninitial','middle']};counts['all']=len({c for row in selected for c in row['ivtff_group_raw']});models={}
   for name,overall,inside in [('restricted18',18,15),('full20',20,17)]:
    models[name]={direction:'EXCLUDED' if counts['all']>overall or counts[key]>inside else 'CAPACITY_ONLY' for direction,key in [('forward','nonfinal'),('reverse','noninitial'),('mixed_direction','middle')]}
   out={'groups':len(selected),'types':len({r['ivtff_group_raw'] for r in selected}),'alphabet':alphabet,'characters':[chars[c] for c in alphabet],'counts':counts,'models':models};panels[reader+'_'+panel]=out;print(reader,panel,counts,models,flush=True)
 save(B/'artifacts/RESULT.json',{'status':'RASM_RENDERING_CAPACITY_ENUMERATED','panels':panels,'scope':'Fixed single-character rendering of pinned technical rasm classes with preserved token boundaries; no general Arabic/abjad exclusion or native values.'})
if __name__=='__main__':main()
