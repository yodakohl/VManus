"""Render the exhaustive candidate/paragraph consequences; no source access."""
import csv
import io
import json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
read=lambda n:json.loads((E/'artifacts'/n).read_text())
pred=read('PREDICTIONS.json');sel=read('SELECTION.json');conf=read('CONFIRMATION.json')
si={c['candidate']:c for c in sel['candidates']};ci={c['candidate']:c for c in conf['candidates']}
order=pred['node_order'];rows=[];details=[]
for c in pred['candidates']:
 name=c['candidate'];s=si[name];q=ci[name]
 complete=name in conf['full_contract_survivors']
 def obs_text(out):
  return '; '.join(o['paragraph_id']+'@'+o['page']+':'+','.join(str(o['observed_counts'][r]) for r in order)+(' PASS' if o['passed'] else ' FAIL') for o in out['observations']) or 'NO_CAPACITY'
 row=dict(candidate=name,full_predicate_class=c['full_predicate_class'],positive_only_class=c['positive_only_class'],
          S_head='.'.join(c['lexicon']['head_forms']['S']),
          expected_vector=','.join(str(c['expected_counts'][r]) for r in order),
          selection_observed=obs_text(s),selection_status=s['status'],confirmation_observed=obs_text(q),confirmation_status=q['status'],
          selection_leaves=','.join(s['independent_leaves']),confirmation_leaves=','.join(q['independent_leaves']),
          confirmation_leaf_capacity=len(q['independent_leaves']),
          full_contract_status='COMPATIBLE' if complete else 'CONTRADICTED',
          additional_confirmation='PASS' if name in conf['additionally_confirmed'] else 'NO_CAPACITY' if not q['observations'] else 'NO_SURVIVING_CONFIRMED_CANDIDATE',
          significance='NOT_ASSESSED',meaning='NOT_CONFIRMED')
 row.update({r+'_mention':'.'.join(c['lexicon']['mention_forms'][r]) for r in order})
 row['contradictions']='; '.join(phase+':'+o['paragraph_id']+':'+v['role']+' expected '+str(v['expected'])+' observed '+str(v['observed']) for phase,out in [('selection',s),('confirmation',q)] for o in out['observations'] for v in o['contradictions'])
 rows.append(row)
 for phase,out in [('selection',s),('confirmation',q)]:
  for o in out['observations']:
   details.append(dict(candidate=name,phase=phase,paragraph_id=o['paragraph_id'],page=o['page'],physical_folio=o['physical_folio'],
                       expected_vector=row['expected_vector'],observed_vector=','.join(str(o['observed_counts'][r]) for r in order),passed=o['passed'],
                       contradictions=json.dumps(o['contradictions'],separators=(',',':')),matched_groups=json.dumps(o['matched_groups'],separators=(',',':'))))
for name,data in [('CANDIDATE_RESULTS.tsv',rows),('PARAGRAPH_RESULTS.tsv',details)]:
 b=io.StringIO();w=csv.DictWriter(b,fieldnames=list(data[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(data);(E/'artifacts'/name).write_text(b.getvalue())
lines=['# Alle18 Kandidaten: Senecio-Folgeprüfung','','STA-Formen bleiben unverändert. Vektorreihenfolge: **C,B,D,L,M,S**; Soll für jeden Absatz: **0,1,1,0,0,0**. Die vollständigen Formen, Vorkommen und Widersprüche stehen in CANDIDATE_RESULTS.tsv und PARAGRAPH_RESULTS.tsv.','','| Kandidat | Positive Klasse | Auswahl: Absatz, Istvektor | Bestätigung: Absatz, Istvektor | Getrennte Bestätigungsblätter | Gesamt |','|---|---|---|---|---:|---|']
for r in rows:
 lines.append('|'+r['candidate']+'|'+r['positive_only_class']+'|'+r['selection_observed']+'|'+r['confirmation_observed']+'|'+str(r['confirmation_leaf_capacity'])+'|'+r['full_contract_status']+'|')
lines+=['','Auswahlüberlebende: '+(', '.join(sel['survivors']) or 'keine')+'.',
        'Zusätzlich bestätigt: '+(', '.join(conf['additionally_confirmed']) or 'keine')+'.',
        'Auswahlkompatibel ohne Bestätigungskapazität: '+(', '.join(conf['selection_only_no_confirmation']) or 'keine')+'.',
        'Vorhersagen:18 verschiedene vollständige Prädikate,4 Gruppen gleicher positiver Konsequenzen. Gleiches beobachtetes Scheitern macht verschiedene Vorhersagen nicht identisch. Fehlende Formen identifizieren ihre semantischen Rollen nicht. Keine Signifikanz oder bestätigten Pflanzennamen.']
(E/'artifacts/CANDIDATE_TABLE.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'candidates':len(rows),'candidate_paragraph_evaluations':len(details),'selection_survivors':sel['survivors'],'full_survivors':conf['full_contract_survivors']}))
