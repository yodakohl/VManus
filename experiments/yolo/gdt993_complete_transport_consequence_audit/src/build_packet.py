import hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
spec=json.loads((E/'src/SPEC.json').read_text());paragraphs=json.loads((R/spec['paragraph_cache']).read_text());wanted={f"f83r.{n}" for n in spec['line_numbers']};readers={};receipts={}
for edition in ('ZL3b','IT2a','RF1b'):
 path=R/(spec['source_prefix']+edition+'.json');x=json.loads(path.read_text());receipts[str(path.relative_to(R))]=hashlib.sha256(path.read_bytes()).hexdigest();rows=[]
 for row in x['lines']:
  if row['metadata']['locus'] in wanted:rows.append(dict(metadata=row['metadata'],groups=[dict(zip(x['group_columns'],g)) for g in row['groups']]))
 rows.sort(key=lambda x:int(x['metadata']['locus'].split('.')[1]));assert len(rows)==7
 owned=[p for p in paragraphs[edition] if p['id']=='f83r|f83r.18-f83r.24']
 uncertain=[g['source_group_id'] for row in rows for g in row['groups'] if g['left_separator'] not in ('LINE_START','DEFINITE_SPACE') or g['right_separator'] not in ('LINE_END','DEFINITE_SPACE')]
 readers[edition]=dict(rows=rows,whole_paragraph_contract=len(owned)==1,strict_anchor_eligible=bool(owned) and all(l['anchor_eligible'] for l in owned[0]['lines']),uncertain_groups=uncertain,paragraph_metadata=owned)
out=dict(scope='Already admitted exposed f83r.18-24 only;raw groups and boundaries preserved',source_receipts=receipts,readers=readers,confirmation_capacity=0)
(E/'artifacts/SOURCE_PACKET.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({e:dict(rows=len(r['rows']),groups=sum(len(x['groups']) for x in r['rows']),whole=r['whole_paragraph_contract'],strict=r['strict_anchor_eligible']) for e,r in readers.items()}))
