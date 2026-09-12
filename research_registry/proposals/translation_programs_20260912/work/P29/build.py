import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P29');W=D.parent;I=W/'P11/INPUT.json';L=W/'P05/MODELS.json';N=W/'P11/COMMON_LEXICON.tsv'
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rr):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
models=json.loads(L.read_text());lex={'A':models['v03'],'R':models['v01']};changes={k:{'A':lex['A'][k],'R':lex['R'][k]} for k in lex['A'] if lex['A'][k]!=lex['R'][k]};assert set(changes)=={'qotchy','qotcheaiin','shan','sy'}
lines=json.loads(I.read_text())['lines'];flat=[]
for r in lines:
 for i,w in enumerate(r['groups'],1):flat.append(dict(record=r['locus'].split('.')[0],line=r['locus'],locus=f'{r["locus"]}:{i}',word=w))
materials={r['word'] for r in csv.DictReader(N.open(),delimiter='\t') if r['type']=='MATERIAL' and r['word'] in lex['A']}|{'odan'}
baseops={'chetchy':'GRIND','shytchy':'WET','chey':'CHECK','shey':'POUR','qotchy':'SIEVE','she':'REST','shot':'HEAT','cphos':'GRIND','shckhy':'MIX','otchy':'TAKE','skey':'RETAIN','cpho':'GRIND','chy':'PROCESS'}
materials-=set(baseops) # P05 action words cannot also introduce a P11 material.
history=json.loads((D/'HISTORICAL_CLAUSES.json').read_text());sourcefamilies={f:[r for r in history if r['family']==f] for f in {r['family'] for r in history}}
js('MODEL.json',{'lexicons':lex,'global_revisions':changes,'materials':sorted(materials),'operations_A':baseops,'operations_R':'same except qotchy FILTER','pairing':'nth target occurrence with nth source occurrence in same family; separately per complete paragraph; no reordering','editorial_rules':['generic material role comparison preserves identity and quantities','SOAK as WET, BOIL as HEAT; precise conditions retained as obligations','expand repeated subjects preserving source identity'],'full_correspondence':'requires operation, material flow, condition and order; family pair alone never complete'})
inputs=[I,L,N,D/'DECISION.md',D/'HISTORICAL_CLAUSES.json',D/'HISTORICAL_TEXT.txt',D/'HISTORICAL_PROVENANCE.json']
js('SOURCE.json',{'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'exposure':'P05 predates current source comparison but all project readings and source banks exposed; not blind','historical_url':'https://www.persee.fr/doc/bec_0373-6237_1925_num_86_1_460583','sealed':['f84','f84r']});tab('INPUT.tsv',flat)
allops=[];allpairs=[];inversions=[];summary={}
for mode in ['A','R']:
 opmap=dict(baseops)
 if mode=='R':opmap['qotchy']='FILTER'
 ops=[];align=[];rec=None
 for j,t in enumerate(flat):
  if rec!=t['record']:rec=t['record'];last=None;seen=Counter()
  w=t['word'];render=lex[mode].get(w,'⟦'+w+'⟧');kind='OPEN' if w not in lex[mode] else 'OTHER_ASSUMPTION'
  if w in materials:last=(w,t['locus']);kind='MATERIAL'
  if w in opmap:
   kind='OPERATION';family=opmap[w];seen[family]+=1;target=last
   if w=='shytchy':
    target=None
    for u in flat[j+1:]:
     if u['line']!=t['line'] or u['word'] in opmap:break
     if u['word'] in materials:target=(u['word'],u['locus']);break
   candidates=sourcefamilies.get(family,[]);source=candidates[seen[family]-1] if len(candidates)>=seen[family] else None
   o=dict(mode=mode,**t,family=family,occurrence=seen[family],material=target[0] if target else 'NA',material_source=target[1] if target else 'NA',argument_status='ASSUMED_SINGLE_MATERIAL' if target else 'MISSING_MATERIAL',source_partner=source['id'] if source else 'NONE',source_order=source['order'] if source else -1,source_material=source['material'] if source else 'NA',source_conditions=source['conditions'] if source else 'NA',correspondence='OPERATION_FAMILY_ONLY' if source else 'NO_SOURCE_EVENT',material_flow_binding='UNBOUND',condition_binding='UNBOUND')
   ops.append(o);render+=f'({o["material"]};Quelle={o["material_source"]};{o["argument_status"]})'
  align.append(dict(mode=mode,**t,kind=kind,rendering=render))
 allops+=ops;tab(f'ALIGNMENT_{mode}.tsv',align)
 psum={}
 for rec in dict.fromkeys(t['record'] for t in flat):
  oo=[o for o in ops if o['record']==rec];paired=[o for o in oo if o['source_partner']!='NONE'];used={o['source_partner'] for o in paired}
  for h in history:
   target=next((o for o in paired if o['source_partner']==h['id']),None)
   allpairs.append(dict(mode=mode,record=rec,source_id=h['id'],source_family=h['family'],source_statement=h['meaning'],source_material=h['material'],source_conditions=h['conditions'],target_locus=target['locus'] if target else 'NONE',target_material=target['material'] if target else 'NONE',decision='FAMILY_ONLY_MATERIAL_AND_CONDITION_UNBOUND' if target else 'NO_TARGET_EVENT'))
  inv=[]
  for i,a in enumerate(paired):
   for b in paired[i+1:]:
    if a['source_order']>b['source_order']:
     row=dict(mode=mode,record=rec,target_earlier=a['locus'],target_later=b['locus'],source_earlier_in_target=a['source_partner'],source_later_in_target=b['source_partner'],decision='ORDER_INVERSION_NOT_LICENSED');inversions.append(row);inv.append(row)
  psum[rec]={'target_operations':len(oo),'family_pairs':len(paired),'source_unmatched':len(history)-len(used),'target_unmatched':len(oo)-len(paired),'order_inversions':len(inv),'complete_statement_correspondences':0,'filter_events':sum(o['family']=='FILTER' for o in oo),'heat_events':sum(o['family']=='HEAT' for o in oo)}
 text=[f'# P29 — vollständige autonome Lesung {mode}','','A=P05-v03 (trockene Verarbeitung), R=P05-v01 (Nassfassung). Alle Glossen bleiben Annahmen; ⟦…⟧ bleibt offen. Die neue feste Argumentzuordnung ist eine Zusatzannahme, keine behauptete alte P05-Grammatik.','']
 for rec in psum:
  text+=['## '+rec,'']
  for line in lines:
   if line['locus'].split('.')[0]==rec:text+=['**'+line['locus']+'** `'+line['raw_line']+'`','',' · '.join(r['rendering'] for r in align if r['line']==line['locus']),'']
  text+=['### Vollständiger Ereignisvergleich','']
  for o in ops:
   if o['record']==rec:text.append(f'- {o["locus"]}: {o["family"]} an {o["material"]}; {o["source_partner"]} ist höchstens ein Operationsfamilienpartner, Materialfluss/Bedingung ungebunden.')
  text+=['','Alle weiteren Nomen, Zustände und Größen bleiben oben ausgeschrieben; sie erhalten durch eine Verbfamilienähnlichkeit keine historische Identität.','']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
 summary[mode]={'groups':len(align),'hypothesis':sum(r['kind']!='OPEN' for r in align),'open':sum(r['kind']=='OPEN' for r in align),'paragraphs':psum}
tab('TARGET_EVENTS.tsv',allops);tab('SOURCE_TARGET_TABLE.tsv',allpairs);tab('ORDER_CONFLICTS.tsv',inversions)
js('RESULT.json',{'status':'PARTIAL_ONE_SOURCE_REDACTION_READING_NOT_SUPPORTED','models':summary,'historical_statements':len(history),'source_heat_events':sum(h['family']=='HEAT' for h in history),'source_filter_events':sum(h['family']=='FILTER' for h in history),'confirmed_meanings':0,'source_identity_selected':False,'independent_confirmation_capacity':0,'scope':'All four exposed HERB4 paragraphs separately compared with one complete historical recipe; no chapter montage'})
report=['# P29 — das vollständige Tintenrezept trägt die HERB4-Lesung nicht','','Die eine gewählte Quelle liefert unter den drei festen Bearbeitungsregeln keine vollständig gebundene Aussagekorrespondenz. Die Nassfassung R gewinnt zwei allgemeine Filter-Parallelen gegenüber A, aber keine passende vollständige Folge. Quellenidentität wird für diesen Kandidaten nicht übernommen; die eigenständigen P05-Lesungen bleiben mit ihren offenen Stellen und bisherigen Problemen erhalten.','','Quelle: [Recette d’encre du XIVe siècle,1925,S.484](https://www.persee.fr/doc/bec_0373-6237_1925_num_86_1_460583), vollständige veröffentlichte lateinische Rezepttranskription aus BnF lat.8651 f88v. HISTORICAL_TEXT.txt und HISTORICAL_CLAUSES.json enthalten den ganzen Rezepttext, nicht nur die alte Ausdrucksbank. Der französische Herausgeberkommentar ist kein Rezeptbestandteil.','','A und R enthalten alle145HERB4-Gruppen, je90hypothetisch und55offen. R übernimmt die ältere P05-Nassfassung mit genau vier globalen Änderungen (MODEL.json); kein neues Einzelfallwörterbuch. Die autonome Vorlage bestand vor dem aktuellen Vergleich; eine quellenunbeeinflusste oder blinde Entstehung wird ausdrücklich nicht behauptet.','','## Ganze Absätze, keine passenden Einzelstellen','','| Fassung | Absatz | Zieloperationen | reine Familienpaare | Quellaussagen ohne Partner /16 | Zieloperationen ohne Partner | Ordnungsumkehrungen | vollständig gebundene Aussagen |','|---|---|---:|---:|---:|---:|---:|---:|']
for m,s in summary.items():
 for p,c in s['paragraphs'].items():report.append(f'| {m} | {p} | {c["target_operations"]} | {c["family_pairs"]} | {c["source_unmatched"]} | {c["target_unmatched"]} | {c["order_inversions"]} | 0 |')
report+=['','Familienpaare sind keine Übersetzungstreffer. Das n-te Vorkommen einer Familie erhält das n-te Quellvorkommen; diese feste Diagnose ist keine optimierte Ausrichtung und widerlegt keine beliebige freie Paraphrase. SOURCE_TARGET_TABLE.tsv zeigt für jeden Absatz alle16Quellaussagen, TARGET_EVENTS.tsv zusätzlich jedes Zielereignis ohne Partner.','','## Alle konkreten Operationspaare','','| Fassung | Ziel | Familie | Quellaussage | Zielmaterial / Quellmaterial | fehlende Quellbedingung |','|---|---|---|---|---|---|']
for o in allops:
 if o['source_partner']!='NONE':report.append(f'| {o["mode"]} | {o["locus"]} | {o["family"]} | {o["source_partner"]} | {o["material"]} / {o["source_material"]} | {o["source_conditions"]} |')
report+=['','## Warum die ungewöhnliche Abfolge nicht übernommen werden kann','','Die Quelle enthält drei Filtrationen und vier Hitzeereignisse: Kochen bis zur Hälfte, Rückkehr ans Feuer, Kochen bis zur Gummiauflösung und kurzes Kochen der letzten Mischung. R hat in jedem der beiden einschlägigen Absätze nur eine angenommene Filtration; nur f29v hat überhaupt eine Erwärmung. Die getrennten Absätze dürfen nicht zu einem Rezept zusammengeschnitten werden. Auch gemeinsam böten sie nur zwei Filterstellen.','','Auf f29v folgt die angenommene Erwärmung erst nach dem Filtervorgang; die fest gepaarten ersten Quellereignisse verlangen Erhitzen vor Filtern. Auf f32v steht das vermische vor entnimm und Filter; im Quellenpaar liegt das Wein-/Vitriol-Mischen später. ORDER_CONFLICTS.tsv hält jede Umkehrung fest, ohne Operationen passend umzunummerieren.','','Nachtfrist, Halbvolumen, Auflösung des Gummis und die spezifischen Maße erhalten keine gebundene Voynich-Aussage. Standzeit oder festgelegte Dosis ersetzen weder bis morgens noch ein konkretes Mengenverhältnis. Keine Materialkorrespondenz hält hier zugleich Zutatenidentität, Ein-/Ausgaben und alle Wiederaufnahmen fest. Allgemeine Operationen und frei angenommene Stoffnamen genügen nicht.','','Die source repone ... ad ignem ist Rückkehr ans Feuer, kein Ruhenlassen. Deshalb bekommen die beiden she≈lasse stehen-Stellen keinen S06-Partner. GDT755s Quellenhinweis wird so präzisiert, nicht als neue Manuskriptentdeckung ausgegeben. Auch die automatische Verallgemeinerung von Kochen zu Erhitzen verliert eine Intensitätsbedingung, die im Tableau offen bleibt.','','## Entscheidung und Reproduktion','','Den konkreten Tintenrezept-Vorlagenkandidaten nicht behalten: Es müssten überwiegend fehlende Bedingungen, Zutatenbezüge und Operationen ergänzt oder unzulässige Umstellungen vorgenommen werden. A/R bleiben autonome partielle Herstellungsentwürfe, keine bestätigten Rezeptinhalte. P05s frühere Feuchte-/Trockenheits- und Produktidentitätslücken werden durch den Vergleich nicht beseitigt. Kein neuer Decoder, keine Behauptung allgemeiner Quellenlosigkeit, keine Signifikanz und keine Wortbedeutung bestätigt.','','SOURCE.json bindet die autonome Vorlage, die gesamte historische Transkription und die vor Ausführung festgelegte Entscheidung. READING_A/R.md und ALIGNMENT_A/R.tsv bewahren alle Gruppen. Reproduktion: `python3 '+str(D/'build.py')+'`; `python3 '+str(D/'validate.py')+'` aus dem Repository. GDT341/343/887/893/894/923 bleiben unverändert. Keine neuen Voynich-Seiten oder Kontakte; f84/f84r geschlossen.']
(D/'REPORT.md').write_text('\n'.join(report)+'\n');print(json.dumps(summary))
