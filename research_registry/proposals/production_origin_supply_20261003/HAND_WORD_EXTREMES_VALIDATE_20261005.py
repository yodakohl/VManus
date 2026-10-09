"""Verify manual packet against selector-first source rows; no visual adjudication."""
from pathlib import Path
import csv,io,json,hashlib,subprocess
P=Path('research_registry/proposals/production_origin_supply_20261003')
packet_path=P/'HAND_WORD_EXTREMES_PACKET_20261005.json'
p=json.loads(packet_path.read_text())
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(P/'HAND_WORD_EXTREMES_SELECTION_20261005.json')==p['selection_sha256']
assert sha(P/'HAND_WORD_EXTREMES_EXTRACT_20261005.py')==p['extractor_sha256']
columns=p['cache_receipt']['inputs']['columns']
loci=sorted({x['locus'] for x in p['lines']})
cmd=['./vmanus-exp','query-tsv',p['cache_receipt']['inputs']['source'],'--selector','locus']
for loc in loci:cmd+=['--allow',loc]
cmd+=['--columns',','.join(columns)]
r=subprocess.run(cmd,text=True,capture_output=True,check=True)
raw=list(csv.DictReader(io.StringIO(r.stdout),delimiter='\t'))
for row in raw:
 for k in ('source_group_index','source_group_count'):row[k]=int(row[k])
bound=[g for line in p['lines'] for g in line['groups']]
assert sorted(raw,key=lambda x:x['source_group_id'])==sorted(bound,key=lambda x:x['source_group_id'])
assert len({g['source_group_id'] for g in bound})==len(bound)
profiles=json.loads((P/'HAND_WORD_EXTREMES_PROFILES_20261005.json').read_text())
assert profiles['source_receipt']==p['cache_receipt']
mp={x['form']:x for x in profiles['profiles']}
assert set(mp)==set(p['forms'])
for ed,rows in p['frequent'].items():
 for q in rows:assert mp[q['form']]['editions'][ed]['count']==q['n']
for ed,rows in p['long'].items():
 for q in rows:
  assert ''.join(q['glyphs'])==q['form'] and len(q['glyphs'])==q['length']
  assert mp[q['form']]['editions'][ed]['count']==q['n']
for q in p['rare'].values():
 if q['selected']:
  assert all(e['count']==1 for e in mp[q['selected']]['editions'].values())
v=json.loads((P/'HAND_WORD_EXTREMES_VISUAL_OBSERVATION_20261005.json').read_text())
for page,orig in [('F2R','.cache/word_extremes_20261005/f2r_original.jpg'),('F114R','experiments/yolo/gdt861_extended_entity_native_comparison/runtime/1006272.jpg')]:
 scope=P/('HAND_WORD_EXTREMES_VISUAL_SCOPE_20261005.json' if page=='F2R' else 'HAND_WORD_EXTREMES_F114R_VISUAL_SCOPE_20261005.json')
 s=json.loads(scope.read_text());assert sha(orig)==s['sha256']
 rec=json.loads((P/f'HAND_WORD_EXTREMES_{page}_REGION_RECEIPT_20261005.json').read_text())
 region='.cache/word_extremes_20261005/'+('f2r_line1.jpg' if page=='F2R' else 'f114r_line39.jpg')
 assert sha(region)==rec['region_sha256']
 assert rec['registered_utc']<rec['downloaded_utc']<v['recorded_utc']
out={'status':'PASS','source_groups':len(bound),'complete_reader_lines':len(p['lines']),'physical_loci':len(loci),'profile_forms':len(mp),'scope':'Guarded source identity and raw boundaries, cached profile consistency, image hashes and receipt ordering. Does not independently re-enumerate ranking or validate visual/linguistic interpretation.','same_author':True,'native_meanings':0,'guard_stats':r.stderr.strip(),'files':{str(f):sha(f) for f in sorted(P.glob('HAND_WORD_EXTREMES*20261005.*')) if 'VALIDATION_' not in f.name}}
(P/'HAND_WORD_EXTREMES_VALIDATION_20261005.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','source_groups','complete_reader_lines','physical_loci','profile_forms','scope')},indent=2))
