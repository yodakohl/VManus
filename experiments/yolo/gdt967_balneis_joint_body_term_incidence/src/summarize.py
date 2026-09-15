"""Post-run tuple-signature explanation of every visited prefix; no model changes."""
from pathlib import Path
import collections,csv,json,itertools
E=Path(__file__).resolve().parents[1];A=E/'artifacts'
read=lambda n:json.loads((A/n).read_text())
s=json.loads((E/'src/SOURCE_MATRIX.json').read_text());cols=s['columns'];rows=read('TARGET.json')['IT2a']

def consequence(ps,ids,js):
 req=collections.Counter(tuple(r['counts'][j] for j in js) for r in s['rows'])
 obs=collections.Counter(tuple(ps[p]['counts'][i] for p in ids) for i in range(len(rows)))
 used=collections.Counter(ids)
 inj=[{'profile':p,'required_distinct':k,'available_distinct':len(ps[p]['members'])} for p,k in used.items() if k>len(ps[p]['members'])]
 deficits=[{'signature':list(k),'required':n,'observed':obs[k],'source_records':[r['id'] for r in s['rows'] if tuple(r['counts'][j] for j in js)==k],'target_paragraphs':[r['id'] for i,r in enumerate(rows) if tuple(ps[p]['counts'][i] for p in ids)==k]} for k,n in sorted(req.items()) if obs[k]<n]
 return {'profiles':list(ids),'members':[ps[p]['members'] for p in ids],'status':'INJECTIVITY_CONTRADICTION' if inj else 'SIGNATURE_CAPACITY_CONTRADICTION' if deficits else 'PREFIX_COMPATIBLE','injectivity_deficits':inj,'count_deficits':deficits}

summary={}
for model in ['WHOLE_GROUP','WITHIN_GROUP_PIECE']:
 d=read(model+'.json');ps=d['profiles'];order=[cols.index(x) for x in d['search']['order']];domains=d['column_domains'];current=[()];counts=[];tables=[]
 for depth in range(3):
  next_prefix=[];table=[]
  for prior in current:
   for p in domains[cols[order[depth]]]:
    ids=prior+(p,);entry=consequence(ps,ids,order[:depth+1]);table.append(entry)
    if entry['status']=='PREFIX_COMPATIBLE':next_prefix.append(ids)
  counts.append(dict(collections.Counter(r['status'] for r in table)));tables.append(table);current=next_prefix
  with (A/f'{model}_DEPTH{depth+1}_CONSEQUENCES.tsv').open('w') as f:
   w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['families','profile_ids','all_carrier_alternatives','status','injectivity_deficits','all_count_deficits'])
   for r in table:w.writerow([','.join(cols[j] for j in order[:depth+1]),','.join(map(str,r['profiles'])),json.dumps(r['members']),r['status'],json.dumps(r['injectivity_deficits'],separators=(',',':')),json.dumps(r['count_deficits'],separators=(',',':'))])
  if not current:break
 assert not current,'This explanation is intended for the actually observed at-most-three-column contradiction; broader case remains unspecified.'
 summary[model]={'complete_contradiction_prefix':[cols[j] for j in order[:len(counts)]],'depth_counts':counts,'source_requirements':[{ 'signature':list(k),'required':n} for k,n in sorted(collections.Counter(tuple(r['counts'][j] for j in order[:len(counts)]) for r in s['rows']).items())]}
(A/'CONTRADICTION_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
