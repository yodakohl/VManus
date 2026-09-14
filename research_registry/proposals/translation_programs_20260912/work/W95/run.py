import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path(__file__).resolve().parent.relative_to(Path.cwd());B=D.parent
for f,h in json.loads((D/'FROZEN_INPUTS.json').read_text()).items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
ps=json.loads((B/'W89/PARAGRAPHS.json').read_text());model=json.loads((B/'P14/MODEL.json').read_text())
assert all(not p['page'].startswith('f84') and p['page']!='f116v' for p in ps)
fields={(f['edition'],f['paragraph'],f['at']):f for f in csv.DictReader((B/'W94/FIELDS.tsv').open(),delimiter='\t') if f['scope']=='RECORD'}
rows=[]
for p in ps:
 for l in p['lines']:
  for i,(w,at) in enumerate(zip(l['words'],l['source_ids'])):
   if w not in model['values']:continue
   head=l['words'][i-1] if i else ''
   kind='NO_LEFT_HEAD' if not head else 'MATERIAL_HEAD_ASSUMED' if head in model['materials'] else 'QUALITY_HEAD_ASSUMED' if head in model['qualities'] else 'VALUE_SEQUENCE' if head in model['values'] else 'UNKNOWN_HEAD'
   old=fields[p['edition'],p['id'],at]
   rows.append(dict(edition=p['edition'],paragraph=p['id'],page=p['page'],at=at,word=w,value=model['values'][w],head=head,head_at=l['source_ids'][i-1] if i else '',category=kind,numerator=old['numerator'],numerator_at=old['numerator_at'],denominator=old['denominator'],denominator_at=old['denominator_at'],raw_line=' '.join(l['words'])))
lookup={(r['edition'],r['paragraph'],r['at']):r for r in rows}
cycles=[]
for s in json.loads((B/'W94/SYSTEMS.json').read_text()):
 if (s['scope'],s['reading'],s['identity'])!=('RECORD','R','TYPE'):continue
 for c in s['chords']:
  endpoints=[dict(lookup[s['edition'],s['paragraph'],at],sign=sign) for at,sign in c['support']]
  kinds={e['category'] for e in endpoints}
  cycles.append(dict(edition=s['edition'],paragraph=s['paragraph'],closing_at=c['closing_at'],coefficients=c['coefficients'],nontrivial=c['nontrivial'],mixed_material_quality={'MATERIAL_HEAD_ASSUMED','QUALITY_HEAD_ASSUMED'}<=kinds,all_material=kinds=={'MATERIAL_HEAD_ASSUMED'},all_quality=kinds=={'QUALITY_HEAD_ASSUMED'},has_untyped=not kinds<={'MATERIAL_HEAD_ASSUMED','QUALITY_HEAD_ASSUMED'},endpoints=endpoints))
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
with (D/'CONTEXTS.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
dump('WITNESSES.json',cycles)
md=['# W95 — alle W94-Kreiszeugen und ihre vollständigen Endpunktzeilen','', 'Alle Kopfklassen sind alte Hypothesen. Kein Zeuge wird aus W94 entfernt.','']
for c in cycles:
 md+=['## '+c['edition']+' '+c['paragraph']+' / '+c['closing_at'],'','log(A/B/C)-Koeffizienten: '+str(c['coefficients'])+'; nichttrivial='+str(c['nontrivial']), '']
 for e in c['endpoints']:
  md += [e['at']+' '+e['word']+' ← '+(e['head'] or '[Zeilenbeginn]')+' / '+e['category'],'','`'+e['raw_line']+'`','']
(D/'WITNESSES.md').write_text('\n'.join(md)+'\n')
result=dict(value_positions=len(rows),all_witnesses=len(cycles),nontrivial=sum(c['nontrivial'] for c in cycles),head_counts={e:dict(Counter(r['category'] for r in rows if r['edition']==e)) for e in ['ZL3b','IT2a']},witness_counts={e:{flag:sum(c[flag] for c in cycles if c['edition']==e and c['nontrivial']) for flag in ['mixed_material_quality','all_material','all_quality','has_untyped']} for e in ['ZL3b','IT2a']},confirmed_meanings=0,independent_confirmation_capacity=0,reserved_access=False,W94_changed=False,decision='NO_UNIT_OR_REFERENCE_CHANGE_IDENTIFIED_NO_RATIO_REFIT')
dump('RESULT.json',result);print(json.dumps(result,indent=2))
# Complete source replay of every endpoint and every value position, without semantic scoring.
assert len(rows)==278 and len(cycles)==36 and sum(c['nontrivial'] for c in cycles)==26
assert {(r['edition'],r['paragraph'],r['at']) for r in rows}==set(fields)
for r in rows:
 p=next(p for p in ps if (p['edition'],p['id'])==(r['edition'],r['paragraph']))
 hits=[(l,j) for l in p['lines'] for j,a in enumerate(l['source_ids']) if a==r['at']]
 assert len(hits)==1
 l,j=hits[0];assert l['words'][j]==r['word'] and r['head']==(l['words'][j-1] if j else '')
 assert r['raw_line']==' '.join(l['words'])
dump('VALIDATION.json',dict(status='PASS',scope='all 278 source positions and immediate heads, frozen hashes, all 36 original witness supports retained',independent_validator=False,meaning_confirmation=False))
