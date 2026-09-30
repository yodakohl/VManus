"""Finite ET conservation check; no semantic scorer, no cache rebuild."""
import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.word_profiles import ensure_cache,occurrences
P=Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')
load=lambda f:json.loads(f.read_text())
a=load(P/'ET_F111R_AUTHOR.json');p=load(P/'ET_FAMILY_PREDICTION.json');s=load(P/'ES_JOINT_FAMILY_AUTHOR.json')
hashfile=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert hashfile(P/'ET_FAMILY_PREDICTION.json')==a['prediction_receipt']['sha256']=='01d8ee89064a37eedabc97b43a0d1c8c95af19d03d85b1fc41811d338e0c929c'
assert hashfile(P/'ES_JOINT_FAMILY_AUTHOR.json')==p['parent_ES_sha256']=='0cfd8207dbd23755a6a1b8a9c71a4edcb4897fbc1d6700968066ac7bf3035986'
assert a['parent_values_unchanged']==p['unchanged_parent_values']
assert a['parent_values_unchanged']['parent32']==s['parent32_models_unchanged']
assert a['parent_values_unchanged']['EQ14']==s['prospective_EQ14_unchanged']
assert a['parent_values_unchanged']['ES13']==s['new_exact_whole_values']
assert a['new_whole_outputs']==p['new_whole_outputs']
selectors=a['source_guard_receipt']['selectors'];assert len(selectors)==179 and all(not x.startswith('f84') and x!='f116v' for x in selectors)
c=ensure_cache();cols=['edition','page','locus','source_group_id','ivtff_group_raw','left_separator','right_separator']
project=lambda r:{k:r[k] for k in cols}
actual={r['source_group_id']:project(r) for f in ('lkedy','lkeedy') for r in occurrences(c,f)}
assert len(actual)==175
assert {x['occurrence']['source_group_id']:x['occurrence'] for x in a['all_exact_new_occurrences']}==actual
for x in a['all_exact_new_occurrences']:
 r=x['occurrence'];assert r['page'] in selectors
 own=[project(dict(t)) for t in c.execute('SELECT * FROM groups WHERE edition=? AND page=? AND locus=? ORDER BY source_group_index',(r['edition'],r['page'],r['locus']))]
 assert x['full_own_raw_line']==own
native=load(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'))
missing=[];counts={}
for e in ('ZL3b','IT2a'):
 units=native[e];assert all(u['page'] in selectors for u in units)
 chosen=[u for u in units if any(w in ('lkedy','lkeedy') for l in u['lines'] for w in l['words'])]
 assert {u['id']:u for u in chosen}=={u['id']:u for u in a['all_new_use_native_paragraphs_ZL_IT'][e]}
 focus=[u for u in units if u['id']=='f111r|f111r.36-f111r.43'];assert len(focus)==1 and focus[0]==a['full_native_focus_units'][e]
 counts[e]=sum(len(l['words']) for l in focus[0]['lines'])
 covered={sid for u in chosen for l in u['lines'] for sid in l['source_ids']}
 missing.extend(k for k,r in actual.items() if r['edition']==e and k not in covered)
assert sorted(missing)==sorted(x['source_id'] for x in a['native_all_use_coverage_limit'])
assert len(missing)==4
rf=[project(dict(r)) for r in c.execute("SELECT * FROM groups WHERE edition='RF1b' AND page='f111r' ORDER BY CAST(substr(locus,instr(locus,'.')+1) AS INTEGER),source_group_index") if 36<=int(r['locus'].split('.')[-1])<=43]
assert rf==a['RF_own_raw_lines36_43'] and len(rf)==81
assert counts=={'ZL3b':86,'IT2a':82}
print(json.dumps({'mechanical':'PASS','focus_groups':counts,'RF_own_groups':81,'exact_occurrences':175,'native_missing_source_ids':sorted(missing),'hashes':{f:hashfile(P/f) for f in ['ET_F111R_AUTHOR.json','ET_FAMILY_PREDICTION.json','ES_JOINT_FAMILY_AUTHOR.json','ET_FORM_AND_ROLE_PRIORS.json']},'native928_sha256':hashfile(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'))}))
