"""Validate literal FB conservation and specified local argument pattern, not meanings."""
import json,hashlib,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
p=json.loads((HERE/'FB_FOCUS_PACKET.json').read_text())
a=json.loads((HERE/'FB_AUTHOR.json').read_text())
checks=[]
def check(label,value): checks.append({'check':label,'pass':bool(value)})
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
check('parent_bytes',sha(HERE/'ET_F111R_AUTHOR.json')==p['parent_sha256'])
check('nomination_bytes',sha(HERE/'FB_NOMINATION.md')==p['nomination_sha256'])
for name,digest in a['inputhashes'].items(): check('input:'+name,sha(ROOT/name)==digest)
old={}
for variant in ['G','I']:
 d=dict(p['parent_values_unchanged']['parent32'][variant]['dictionary'])
 d.update(p['parent_values_unchanged']['EQ14']);d.update(p['parent_values_unchanged']['ES13']);d.update(p['new_whole_outputs']);old[variant]=d
 check('retained61:'+variant,len(d)==61 and a['retained61'][variant]==d)
for key,pkey in [('parent_history_unchanged','chosen_material_event_history'),('parent_grammar_and_history_costs_unchanged','grammar_and_history_costs'),('parent_focus_known_roles_unchanged','focus_all_known_mentions_roles')]: check(key,a[key]==p[pkey])
def native(edition):
 if edition=='RF1b':
  return [(r['source_group_id'],r['locus'],r['ivtff_group_raw']) for r in p['RF_own_raw_lines36_43']]
 return [(sid,line['locus'],word) for line in p['full_native_focus_units'][edition]['lines'] for sid,word in zip(line['source_ids'],line['words'])]
positions={'IT2a':a['IT_positions'],**a['alternative_positions']}
known={r['source_id']:r for r in p['focus_all_known_mentions_roles']}
new=a['new_whole_values'];check('no_old_override',not(set(new)&set(old['G'])))
counts={}
for edition,rows in positions.items():
 expected=native(edition);check('all_raw_order_ids:'+edition,[(r['source_id'],r['locus'],r['raw']) for r in rows]==expected)
 check('position_count:'+edition,len(rows)=={'IT2a':82,'ZL3b':86,'RF1b':81}[edition])
 for r in rows:
  for variant in ['G','I']:
   val=old[variant].get(r['raw'],new.get(r['raw'],{}).get('value','UNKNOWN'))
   check('value:'+variant+':'+r['source_id'],r[variant+'_value']==val)
  check('rules:'+r['source_id'],all(rule in a['grammar_rules'] for rule in r['rule_ids']))
  if r['source_id'] in known: check('parent_role:'+r['source_id'],r.get('parent_commitment_literal')==known[r['source_id']])
 counts[edition]={'total':len(rows),'assigned':sum(r['value']!='UNKNOWN' for r in rows),'unknown':sum(r['value']=='UNKNOWN' for r in rows)}
 check('unknown_count:'+edition,counts[edition]['unknown']==a['counted_costs']['edition_position_counts'][edition]['unknown_positions'])
# Exact local typed sequence under the authored grammar; not an independent semantic parser.
core=a['IT_positions'][:10]
check('core_exact_atoms',[r['value'] for r in core]==['patient','boil-up','cleansing','root','oil','old','in','apply','that-material','skin'])
check('age_adjacency',core[4]['type']=='OIL_MATERIAL' and core[5]['type']=='AGE_PROPERTY')
check('reference_latest_material',core[8]['entity']==core[4]['entity']=='O0' and core[3]['entity']=='R0')
sc=a['source_consequences'];check('application_oil_argument',sc['application_argument']['resolved_material']=='O0' and sc['old_modifier']['target']=='O0')
check('whole_still_partial',a['counted_costs']['whole_context_fully_translated'] is False and all(c['unknown']>0 for c in counts.values()))
check('zero_confirmed_words',a['counted_costs']['confirmed_words']==0)
with (HERE/'FB_ALL_POSITION_OVERLAYS.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['edition','source_id','raw','G_value','I_value','role','entity','event'])
 for edition,rows in positions.items():
  for r in rows: w.writerow([edition,r['source_id'],r['raw'],r['G_value'],r['I_value'],r['role'],r['entity'],r['event']])
zr=a['alternative_positions']['ZL3b']
zbar=next(r for r in zr if r['source_id']=='ZL3b|f111r.37|G003')
zref=next(r for r in zr if r['source_id']=='ZL3b|f111r.37|G005')
check('retained_real_scope_conflict',zbar['value']=='UNKNOWN' and zref['raw']=='keeol' and zref['entity']=='O0' and 'R6' in zref['rule_ids'])
out={'status':'CONSERVATION_PASS_WITH_RETAINED_SCOPE_CONFLICT' if all(c['pass'] for c in checks) else 'CONSERVATION_FAIL','check_count':len(checks),'counts':counts,'meaning_validation':False,'whole_translation':False,'checks':checks}
(HERE/'FB_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
raise SystemExit(0 if out['status']=='CONSERVATION_PASS_WITH_RETAINED_SCOPE_CONFLICT' else 1)
