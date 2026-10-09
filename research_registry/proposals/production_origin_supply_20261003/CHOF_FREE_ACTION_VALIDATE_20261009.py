import gzip,hashlib,json
from pathlib import Path
b=Path('research_registry/proposals/production_origin_supply_20261003');p=json.loads((b/'CHOF_FREE_ACTION_CERTIFICATE_20261009.json').read_text());old=json.loads(Path(p['inputs'][0]['path']).read_text());dep=json.loads((b/'CHOF_ENDPOINT_DEPENDENCY_20261009.json').read_text());cache=Path(dep['source']['path']);assert hashlib.sha256(cache.read_bytes()).hexdigest()==dep['source']['sha256'];rows=json.loads(gzip.decompress(cache.read_bytes()));count=0
for ed,d in old.items():
 ns={side:{n['old_id']:n for n in vv} for side,vv in d['chains'].items()};seen=set()
 def verify(side,i):
  global count
  n=ns[side][i];w=tuple(n['word']);key=(side,i)
  if key in seen:return w
  if n['parents'] is None:
   assert ''.join(w)!='chof'
   matches={r['id'] for r in rows[ed] if tuple(r['units'])==w};assert set(n['source_ids'])==matches
  else:
   u,v=(verify(side,j) for j in n['parents']);assert v==(u+w if side=='LEFT' else w+u)
  seen.add(key);count+=1;return w
 for unit,(side,i) in d['targets'].items():
  if unit!='f':assert verify(side,i)==(unit,)
 ch=d['targets']['ch'];ee=d['targets']['e'];assert verify(*ch)==('ch',) and verify(*ee)==('e',)
 r=p['readers'][ed]['replacement_f_proof']['whole_source'];assert r in rows[ed];assert r['units']==['ch','e','e','f']
 for w in ['ol','olol']:
  assert d['square'][w]
  ids={r['id'] for r in rows[ed] if r['ivtff_group_raw']==w};assert ids=={r['id'] for r in d['square'][w]}
v={'status':'PASS','scope':'Independent recursive old ancestry/raw source binding, plus algebraic composition proof; not image confirmation','checked_old_nodes':count,'readers':3,'all_target_units_per_reader':22,'rare_replacement_folio':'f78v','source_free_review':'Bounded producer confirmed action argument; did not inspect native rows.'}
(b/'CHOF_FREE_ACTION_VALIDATION_20261009.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
