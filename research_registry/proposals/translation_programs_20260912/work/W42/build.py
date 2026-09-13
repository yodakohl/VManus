"""Four fixed dimension contracts on the exposed complete HERB4 packet."""
import csv,json,hashlib
from pathlib import Path
from collections import defaultdict
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text())
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
raw=list(csv.DictReader(Path(S['source']).open(),delimiter='\t'))
lex={r['form']:r['meaning_hypothesis'] for r in csv.DictReader(Path(S['lexicon']).open(),delimiter='\t')}
materials=set(json.loads(Path(S['materials']).read_text())['material_forms'])
assert len(raw)==145 and set(r['record'] for r in raw)==set(S['records'])
assert all(not r['record'].startswith('f84') for r in raw)
def tab(name,rs,cols):
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rs)
fields=[];actions=[];totals=[];predictions=[]
for rec in S['records']:
 rows=[r for r in raw if r['record']==rec];paired={}
 for i,r in enumerate(rows[:-1]):
  if r['word']=='daiin' and rows[i+1]['word']=='daiin':
   ms=[]
   for x in reversed(rows[:i]):
    if x['word'] in materials and x['word'] not in [m['word'] for m in ms]:ms.append(x)
    if len(ms)==2:break
   ms.reverse()
   if len(ms)==2:paired[r['at']]=ms[0];paired[rows[i+1]['at']]=ms[1]
 fs=[]
 for i,r in enumerate(rows):
  if r['word']!='daiin':continue
  m=paired.get(r['at']) or next((x for x in reversed(rows[:i]) if x['word'] in materials),None)
  a=next((x for x in reversed(rows[:i]) if x['word'] in S['actions']),None)
  between=rows[rows.index(a)+1:i] if a else rows[:i]
  f=dict(record=rec,at=r['at'],word=r['word'],material_at=m['at'] if m else 'MISSING',material_word=m['word'] if m else 'MISSING',action_at=a['at'] if a else 'MISSING',action_word=a['word'] if a else 'MISSING',binding='DISTRIBUTED_XX' if r['at'] in paired else 'LAST_MATERIAL',action_to_value_raw=' '.join(x['word'] for x in between),unknown_between=sum(x['word'] not in lex for x in between))
  fs.append(f);fields.append(f)
  mat=lex.get(f['material_word'],'?');act=lex.get(f['action_word'],'?')
  for model in S['models']:
   if model=='M':meaning='Masse('+mat+') = Q·U_M';unit='U_M unknown';missing=[] if m else ['MATERIAL']
   if model=='E':meaning='Gesamtaufwand für '+act+' @'+f['action_at']+' = Q·U_E';unit='U_E unknown';missing=[] if a else ['ACTION']
   if model=='L':meaning='Aufwand für '+act+' an '+mat+' = Q·U_E';unit='U_E unknown';missing=[k for k,b in [('ACTION',not a),('MATERIAL',not m)] if b]
   if model=='T':meaning='Tarif für '+act+' an '+mat+' = Q·U_E/U_M; Aufwand = Tarif × unbekannte Materialmasse';unit='U_E,U_M,material mass unknown';missing=[k for k,b in [('ACTION',not a),('MATERIAL',not m)] if b]
   predictions.append(dict(model=model,**f,prediction=meaning,missing=','.join(missing) or 'NONE',units=unit,independent_confirmation_capacity=0))
 for r in rows:
  if r['word'] not in S['actions']:continue
  attached=[f for f in fs if f['action_at']==r['at']]
  pairs=sorted({f['material_word'] for f in attached if f['material_word']!='MISSING'})
  actions.append(dict(record=rec,at=r['at'],word=r['word'],gloss=lex[r['word']],value_loci=','.join(f['at'] for f in attached) or 'NONE',fields=len(attached),distinct_materials=','.join(pairs) or 'NONE',E_partial_work='Q*U_E' if attached else 'UNKNOWN_UNPRICED',L_partial_work=str(len(pairs))+'*Q*U_E' if pairs else 'UNKNOWN_UNPRICED',T_partial_work='Q*U_E/U_M*('+'+'.join('m('+p+')' for p in pairs)+')' if pairs else 'UNKNOWN_UNPRICED'))
 af=[a for a in actions if a['record']==rec]
 count_e=len({f['action_at'] for f in fs if f['action_at']!='MISSING'})
 count_l=len({(f['action_at'],f['material_word']) for f in fs if f['action_at']!='MISSING' and f['material_word']!='MISSING'})
 totals.append(dict(record=rec,groups=len(rows),daiin_fields=len(fs),action_occurrences=len(af),actions_without_daiin=sum(a['fields']==0 for a in af),M_distinct_materials=len({f['material_word'] for f in fs if f['material_word']!='MISSING'}),E_priced_work_units=count_e,L_priced_work_units=count_l,T_numeric_total='UNDETERMINED_MASSES',whole_record_total='NOT_IDENTIFIED_UNPRICED_ACTIONS_AND_UNITS'))
alignment=[]
for model in S['models']:
 pby={p['at']:p for p in predictions if p['model']==model}
 for r in raw:alignment.append(dict(model=model,record=r['record'],at=r['at'],word=r['word'],reading=pby[r['at']]['prediction'] if r['at'] in pby else lex.get(r['word'],'⟦'+r['word']+'⟧')))
tab('FIELDS.tsv',fields,list(fields[0]));tab('PREDICTIONS.tsv',predictions,list(predictions[0]));tab('ACTIVITY_ACCOUNTS.tsv',actions,list(actions[0]));tab('RECORD_ACCOUNTS.tsv',totals,list(totals[0]));tab('ALIGNMENT.tsv',alignment,list(alignment[0]))
md=['# W42 — vollständige vier Lesungen','','Alle Bedeutungen und Einheiten sind hypothetisch. Rechnerische Teilkonten sind keine geschriebenen Summen.','']
for rec in S['records']:
 md+=['## '+rec,'']
 for line in dict.fromkeys(r['locus'] for r in raw if r['record']==rec):
  rr=[r for r in raw if r['locus']==line];md+=[line+': `'+ ' '.join(r['word'] for r in rr)+'`','']
  for model in S['models']:md += [model+': '+' · '.join(a['reading'] for a in alignment if a['model']==model and a['at'].rsplit(':',1)[0]==line),'']
(D/'READING.md').write_text('\n'.join(md)+'\n')
result=dict(groups=len(raw),records=len(totals),fields=len(fields),predictions=len(predictions),known_positions=sum(r['word'] in lex for r in raw),open_positions=sum(r['word'] not in lex for r in raw),actions=len(actions),priced_actions=sum(a['fields']>0 for a in actions),unpriced_actions=sum(a['fields']==0 for a in actions),record_accounts=totals,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
