import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
D=Path('research_registry/proposals/translation_programs_20260912/work/P19');W=D.parent
I=W/'P11/INPUT.json';B=W/'P12/PROSE.tsv';C=W/'P28/PROSE.tsv'
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rs):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rs)
def norm(w):return w[:-4]+'ain' if w.endswith('aiin') else w
meta=list(csv.DictReader((D/'METADATA_PROJECTION.tsv').open(),delimiter='\t'));md={p:sorted({(r['hand'],r['section'],r['language']) for r in meta if r['page']==p}) for p in {r['page'] for r in meta}};assert all(len(x)==1 for x in md.values())
js('METADATA_SUMMARY.json',{'pages':md,'scope':'inherited transcription labels only; hand/section/language perfectly confounded in work scope','guard':{'selected':198,'skipped_forbidden':98,'skipped_not_allowed':5089},'query':'query-tsv transcription/voynich_zl3b_lines.tsv --selector page --allow f17r --allow f21r --allow f32v --allow f29v --allow f77r --allow f82r --allow f83r --columns page,section,language,hand'})
lines=[]
for l in json.loads(I.read_text())['lines']:lines.append(dict(package='HERB4',page=l['locus'].split('.')[0],record=l['locus'].split('.')[0],line=l['locus'],text=l['raw_line']))
for p in [B,C]:
 for l in csv.DictReader(p.open(),delimiter='\t'):lines.append(dict(package='BATH3',page=l['page'],record=l['record_id'],line=l['locus'],text=l['zl3b_line']))
# First pair, then remainder; no different rules in transfer part.
lines.sort(key=lambda l:(0 if l['page']=='f17r' else 1 if l['record']=='F83_P1' else 2))
flat=[]
for l in lines:
 for i,w in enumerate(l['text'].split(),1):flat.append(dict(package=l['package'],page=l['page'],record=l['record'],line=l['line'],locus=f'{l["line"]}:{i}',word=w))
assert len(flat)==1085
tab('INPUT.tsv',flat)
names={'cthy':'Kraut','chor':'Blüten','ctho':'Pulver','cthaiin':'Pflanzenportion','okaiin':'Ansatz','shedy':'Flüssigkeit','lchedy':'Zusatzstoff','qokaiin':'Gefäß'};verbs={'chedy':'erwärme','qokeedy':'fülle ein','sho':'verarbeite','qotchy':'zerkleinere'}
js('MODEL.json',{'names':names,'verbs':verbs,'E_quantities':{'daiin':'Q','dain':'R'},'N_rule':'all terminal aiin -> ain; normalized dai(i)n gets Q, R removed globally','G':'BATH quantities become duration of last complete action; HERB unchanged','bindings':'last material and separate last destination, record scope','meaning_status':'all hypothetical'})
js('SOURCE.json',{'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [I,B,C,D/'METADATA_PROJECTION.tsv',D/'DECISION.md']},'exposure':'all material previously exposed; no independent confirmation','sealed':['f84','f84r']})
forms=Counter(t['word'] for t in flat);fam=[]
for w in sorted(forms):
 if w.endswith('aiin'):
  short=norm(w);longpages=sorted({t['page'] for t in flat if t['word']==w});shortpages=sorted({t['page'] for t in flat if t['word']==short})
  fam.append(dict(long=w,short=short,long_count=forms[w],short_count=forms[short],long_pages=','.join(longpages),short_pages=','.join(shortpages) or 'NONE',same_label_pages=','.join(sorted(set(longpages)&set(shortpages))) or 'NONE',long_hands=','.join(sorted({md[p][0][0] for p in longpages})),short_hands=','.join(sorted({md[p][0][0] for p in shortpages})) or 'NONE'))
tab('ALL_VARIANT_FAMILIES.tsv',fam)
ops=[];qs=[];summary={}
for mode in ['E','N','G']:
 lex={norm(w) if mode=='N' else w:g for w,g in names.items()};rec=None;align=[]
 for t in flat:
  if rec!=t['record']:rec=t['record'];material=None;dest=None;previous_action=None
  raw=t['word'];w=norm(raw) if mode=='N' else raw;kind='OPEN';render='⟦'+raw+'⟧'
  if w in lex:
   kind='NOUN';render=lex[w]+'['+w+']'
   if w==(norm('qokaiin') if mode=='N' else 'qokaiin'):dest=(w,t['locus'])
   else:material=(w,t['locus'])
  elif w in verbs:
   kind='ACTION';missing=[]
   if material is None:missing.append('MATERIAL')
   if w=='qokeedy' and dest is None:missing.append('DESTINATION')
   o=dict(mode=mode,**t,material=material[0] if material else 'NA',material_source=material[1] if material else 'NA',destination=dest[0] if dest and w=='qokeedy' else 'NA',destination_source=dest[1] if dest and w=='qokeedy' else 'NA',status='COMPLETE' if not missing else 'MISSING_'+'_AND_'.join(missing))
   ops.append(o);render=verbs[w]+'('+o['material']+';Ziel='+o['destination']+';'+o['status']+')'
   if not missing:previous_action=(w,t['locus'])
  elif w in (['dain'] if mode=='N' else ['daiin','dain']):
   kind='QUANTITY';value='Q' if mode=='N' or w=='daiin' else 'R';dimension='DURATION' if mode=='G' and t['package']=='BATH3' else 'MATERIAL_AMOUNT';ref=previous_action if dimension=='DURATION' else material
   q=dict(mode=mode,**t,value=value,dimension=dimension,reference=ref[0] if ref else 'NA',reference_source=ref[1] if ref else 'NA',status='BOUND' if ref else 'MISSING_REFERENCE');qs.append(q);render=dimension+' '+value+'('+q['reference']+';Quelle='+q['reference_source']+')'
  align.append(dict(mode=mode,**t,normalized=w,kind=kind,rendering=render))
 tab(f'ALIGNMENT_{mode}.tsv',align)
 text=[f'# P19 — vollständige Fassung {mode}','','Alle deutschen Wortwerte und Q/R sind Hypothesen. ⟦…⟧ bleibt offen. Die sichtbare Quellform wird nicht ersetzt.','']
 for l in lines:text+=['**'+l['line']+' / '+l['record']+'** `'+l['text']+'`','',' · '.join(a['rendering'] for a in align if a['line']==l['line']),'']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
 summary[mode]={'groups':len(flat),'hypothesis':sum(a['kind']!='OPEN' for a in align),'open':sum(a['kind']=='OPEN' for a in align),'operations':dict(Counter(o['status'] for o in ops if o['mode']==mode)),'quantities':dict(Counter(q['status'] for q in qs if q['mode']==mode)),'dimensions':dict(Counter(q['dimension'] for q in qs if q['mode']==mode))}
tab('OPERATIONS.tsv',ops);tab('QUANTITIES.tsv',qs)
changes=[]
for e in ops:
 if e['mode']!='E':continue
 n=next(o for o in ops if o['mode']=='N' and o['locus']==e['locus'])
 # compare semantic equivalence classes and the actual source mentions, not spelling only
 if (norm(e['material']),e['material_source'],norm(e['destination']),e['destination_source'],e['status'])!=(n['material'],n['material_source'],n['destination'],n['destination_source'],n['status']):
  changes.append(dict(locus=e['locus'],word=e['word'],E_material=e['material'],N_material=n['material'],E_material_source=e['material_source'],N_material_source=n['material_source'],E_destination_source=e['destination_source'],N_destination_source=n['destination_source'],E_status=e['status'],N_status=n['status']))
tab('CHANGED_ACTION_BINDINGS.tsv',changes)
js('RESULT.json',{'status':'PARTIAL_OPTIONAL_SHORTENING_READING_HAND_REGISTER_CONFOUNDED','models':summary,'normalization_families':len(fam),'families_with_both_forms':sum(f['short_count']>0 for f in fam),'families_with_same_page_both':sum(f['same_label_pages']!='NONE' for f in fam),'changed_action_bindings':len(changes),'newly_complete_actions':sum(c['E_status']!='COMPLETE' and c['N_status']=='COMPLETE' for c in changes),'meaning_identifications':0,'independent_hand_register_cells':0,'independent_confirmation_capacity':0})
report=['# P19 — optionale Schreibverkürzung bleibt von Inhalt und Hand zu trennen','','Die eine terminale aiin→ain-Regel ist auf alle1085Gruppen der vollständigen HERB4/BATH3-Arbeitspakete angewendet. Sie kann zusätzliche ganze Formen in die hypothetische Lesung einbinden. Die vorhandenen Handetiketten bestimmen aber keine Schreiberregel: Hand1/H/A und Hand2/B/B sind im Arbeitsmaterial vollständig gekoppelt. Lange und kurze Formen stehen zudem innerhalb derselben Seite.','','| Fassung | Hypothesen / offen | Handlungen | Größenbindungen | Größenart |','|---|---|---|---|---|']
for m,r in summary.items():report.append(f'| {m} | {r["hypothesis"]} / {r["open"]} | {r["operations"]} | {r["quantities"]} | {r["dimensions"]} |')
report+=['','E hält ganze Formen auseinander und Q/R als Mengenklassen offen. N vereinigt alle terminalen aiin/ain-Formen mit einer einzigen Regel, einschließlich daiin/dain zu Q; es werden keine Zahlenwerte erkannt. G behält die getrennten Formen, liest die BATH-Größen jedoch als Dauer des letzten vollständigen Vorgangs. Alle Leser enthalten dieselben Quellgruppen und alle nicht gelesenen Reste.','','## Sämtliche Familien, nicht nur passende Beispiele','','| Lang | Kurz | Anzahl lang / kurz | Seiten mit beiden | Handetiketten lang / kurz |','|---|---|---|---|---|']
for f in fam:report.append(f'| {f["long"]} | {f["short"]} | {f["long_count"]} / {f["short_count"]} | {f["same_label_pages"]} | {f["long_hands"]} / {f["short_hands"]} |')
report+=['','Die Zahl der Familien bezeichnet den vollständigen Formkatalog dieser festen Regel, keine semantisch bestätigten Wortpaare. Klassen ohne bekannte Nomenkarte bleiben offen. Bei daiin/dain wird eine bisher mögliche Wertunterscheidung ausdrücklich aufgegeben; da Q und R keine unabhängig gelesenen Zahlen sind, kann dieser Test weder Gleichheit noch Ungleichheit beweisen.','','## Alle durch N geänderten Handlungsbindungen','','| Ort | E Materialquelle → N | E Gefäßquelle → N | E → N Vollständigkeit |','|---|---|---|---|']
for c in changes:report.append(f'| {c["locus"]} | {c["E_material_source"]} → {c["N_material_source"]} | {c["E_destination_source"]} → {c["N_destination_source"]} | {c["E_status"]} → {c["N_status"]} |')
report+=['','Die Tabelle entfernt reine Umbenennungen desselben bereits gebundenen Wortes. Ein neues Gefäßvorkommen kann nur die zuletzt genannte Gefäßquelle ändern, ohne einen zuvor unvollständigen Satz zu vervollständigen. Auch das wird getrennt von einer tatsächlich neu vollständigen Handlung gezählt. OPERATIONS.tsv bewahrt alle Fälle, QUANTITIES.tsv sämtliche Mengen-/Dauerbindungen.','','## Entscheidung','','N bleibt eine optionale Schreibhypothese mit konkreten Lesungsfolgen. Eine ausschließliche Ersetzung abhängig vom vorliegenden Handetikett erklärt die innerhalb derselben Seite vorhandenen beiden Formen nicht. Ein optionales Kürzen wäre damit vereinbar, ist aber nicht bewiesen. Die zwei beobachteten Hand/Genre-Zellen liefern keine unabhängige Trennung von Hand, Register und Sprachklasse. Die Etiketten stammen aus der Transkriptionsmetadatenlage, nicht aus einer neu durchgeführten paläographischen Zuschreibung.','','E/N unterscheiden die behauptete Wort-/Wertidentität; E/G die Mengenart und ihren Bezug. Ein gebundener Dauerbezug oder Materialbezug ist allein kein semantischer Gewinner. Keine richtige Mengen-/Zeitlesung, Sprache oder Schreiberkonvention gewählt. G ist eine durchgehende Gegenfassung und darf wegen anderer Bindungszahlen nicht ohne Bedeutungsprüfung verworfen werden. Alle Wortwerte sind Annahmen; keine Normalisierung wird in die Quelltranskription zurückgeschrieben.','','GDT167/417/865/920 und P12/P22/P24 bleiben unverändert. Keine p/f-Brücke oder freier Handschlüssel, keine Signifikanz und kein score-ready Relationspaket. Sämtliches Arbeitsmaterial war exponiert; f84/f84r bleiben geschlossen.','','## Nachrechnung','','SOURCE.json bindet begrenzte Textquellen, die vor Ausführung festgelegte Entscheidung und die ausschließlich bewachte Metadatenprojektion. METADATA_SUMMARY.json hält Abgrenzung und Konfundierung fest. Reproduktion: `python3 '+str(D/'build.py')+'`; `python3 '+str(D/'validate.py')+'` aus dem Repository. Vollständige Lesungen: READING_E/N/G.md.']
(D/'REPORT.md').write_text('\n'.join(report)+'\n');print(json.dumps(json.loads((D/'RESULT.json').read_text())))
