"""Publish all complete candidate readings and reference assumptions after testing."""
import json,collections,csv
from pathlib import Path
P=Path(__file__).resolve().parents[1];A=P/'artifacts'
m=json.loads((P/'MODEL_v01.json').read_text());s=json.loads((P/'src/SOURCE.json').read_text());cs=json.loads((A/'CANDIDATES.json').read_text());rows=json.loads((A/'ROWS.json').read_text())
# Additional mechanical audit of the declared typed references. It does not test their truth.
types={e['value'] for e in m['lexicon'].values()};assert {'DAY','HOUR','RULER','NIGHT','METHOD'}<=types
bindings=[]
for pos,typ in [(40,'DAY'),(43,'HOUR')]:
 preceding=[i+1 for i,w in enumerate(s['words'][:39]) if m['lexicon'][w]['value']==typ]
 assert preceding
 bindings.append({'position':pos,'word':'dy','function':'typed most recent reference','required_type':typ,'antecedent_position':preceding[-1],'antecedent_word':s['words'][preceding[-1]-1]})
assert [(r['position'],r['antecedent_position']) for r in bindings]==[(40,36),(43,37)]
assert m['clauses'][5]['binding']['NIGHT']=='part of DAY, not added outside the complete day'
assert m['clauses'][3]['binding']['subject']=='most recent DAY register'
assert m['clauses'][4]['binding']['START']=='initial HOUR of DAY'
assert m['clauses'][9]['binding']['stores']=='method_A ruler after complete day'
assert m['clauses'][10]['binding']['same_reference']=='ruler stored by method_A, not absolute hour identity'
assert m['clauses'][11]['binding']['METHOD_76']=='most recent method (B)' and m['clauses'][11]['binding']['METHOD_78']=='preceding distinct method (A)'
(A/'REFERENCE_AUDIT.json').write_text(json.dumps({'status':'DECLARED_BINDINGS_WELL_TYPED','dy':bindings,'scope':'Post-result mechanical consistency audit, not a new manuscript or interpretation test. C01 DAY recurrence is not asserted equal to one seven-member H cycle.','independently_inferred_grammar':False},indent=2)+'\n')
changes={
 'AT_LAST':{'C10':'Zähle nun von der hellen Tageszeit durch den ganzen Tag bis zur letzten Stunde.'},
 'AFTER_FIRST_UNSKIPPED':{'C11':'Andere Rechnung: Überspringe ein Glied und ein Glied; gehe danach zum Nachfolger des ersten nicht übersprungenen Glieds im Kreis und erreiche dieselbe Herrschaftszuordnung.'},
 'ONE_REFERENT_FOR_DOUBLE':{'C11':'Andere Rechnung: Überspringe ein Glied, eben dieses eine Glied; wähle danach das erste nicht übersprungene Glied im Kreis und erreiche dieselbe Herrschaftszuordnung.'},
 'SAME_METHOD_REFERENCE':{'C12':'Die zuletzt ausgeführte Rechnung und diese selbe Rechnung stimmen hinsichtlich der Herrschaft einer Stunde überein.'},
 'NIGHT_REVERSE':{'C03':'Wenn während der hellen Tageszeit eine folgende Stunde beginnt, schreite zum nächsten Glied fort und setze nicht neu an.','C08':'Auf eine Nachtstunde folgt eine Stunde mit dem nächsten Glied der für die Nacht umgekehrt angesetzten Folge.'},
 'NIGHT_RESET':{'C03':'Wenn innerhalb eines Tageslicht- oder Nachtblocks eine folgende Stunde beginnt, schreite zum nächsten Glied fort und setze innerhalb dieses Blocks nicht neu an.','C08':'Bei Beginn der Nacht beginne beim ersten Herrscher erneut; anschließend folgt auf eine Nachtstunde eine Stunde mit dem nächsten Glied.'}
}
lines=['# Alle vollständigen Kandidaten und beobachteten Konsequenzen','',
'Alle Varianten haben dieselben 80 Rohgruppen und dieselben zwölf Satzspannen. Die Texte sind angenommene Paraphrasen; Wörter wie „während“, „umgekehrt“ und der Neustart in Nachtvarianten beruhen auf den ausdrücklich geänderten Satzregeln. Sie sind keine zusätzlich gelesenen Rohwörter. Jede Variante wird vollständig wiedergegeben.','',
'|Kandidat|Geprüfte Einstellungen|Stimmig|Bedingung|Unabhängige Bedeutungsprüfung|','|---|---|---|---|---|']
for c in cs:lines.append(f"|{c['candidate']}|{c['settings']}|{c['coherent_settings']}|{','.join(map(str,c['coherent_daylight_counts'])) or 'siehe unten'}|0|")
for c in cs:
 lines += ['', '## '+c['candidate'],'',c['status'],'',
 'Wortänderungen: `'+json.dumps(c['word_changes'],ensure_ascii=False)+'`. Satzregeländerungen: `'+json.dumps(c['grammar_changes'],ensure_ascii=False)+'`.','',
 '|Gruppen|Rohgruppen|Vollständige hypothetische Wiedergabe|','|---|---|---|']
 for clause in m['clauses']:
  de=changes.get(c['candidate'],{}).get(clause['id'],clause['german'])
  lines.append(f"|{clause['start']}–{clause['end']}|{' '.join(clause['words'])}|{de}|")
 examples=[r for r in rows if r['candidate']==c['candidate'] and r['initial_phase']==0]
 lines += ['', '|Tageslichtstunden, falls vorausgesetzt|Rechnung A|Rechnung B|C11 gleich|C12 Vergleich|Dio-Stundenfolge durchgehend|','|---|---|---|---|---|---|']
 for r in examples:lines.append(f"|{r['daylight_hours']}|{r['method_a_ruler']}|{r['method_b_ruler']}|{r['C11_same']}|{r['C12_agrees']}|{r['source_continuous_hours']}|")
 lines+=['','Die sechs übrigen Startphasen und sämtliche Schrittfolgen stehen in ROWS.json; keine wurden ausgelassen.']
(A/'ALL_READINGS.md').write_text('\n'.join(lines)+'\n')
with (A/'WORD_ASSIGNMENTS.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['word','value','german','origin','positions'])
 for word,e in sorted(m['lexicon'].items()):w.writerow([word,e['value'],e['german'],e['origin'],','.join(str(i+1) for i,x in enumerate(s['words']) if x==word)])
print('All seven full readings, all sixty word assignments and explicit typed-reference audit saved.')
