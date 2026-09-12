import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P02');W=D.parent;S=W/'P11/INPUT.json'
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rr):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
source=json.loads(S.read_text());pages=['f29v','f32v','f17r','f21r'];lines=[r for p in pages for r in source['lines'] if r['locus'].split('.')[0]==p]
flat=[]
for r in lines:
 for i,w in enumerate(r['groups'],1):flat.append(dict(record=r['locus'].split('.')[0],line=r['locus'],locus=f'{r["locus"]}:{i}',word=w))
nouns={'okaiin':('A','Ansatz'),'cthy':('B','Kraut'),'chor':('C','Blüten')}
ops={'shytchy':('benetze','RIGHT','moisture','WET'),'otshy':('kühle','RIGHT','temperature','COLD'),'shot':('erwärme','LEFT','temperature','HOT'),'qotchy':('zerkleinere','LEFT','texture','GROUND'),'cpho':('zerstoße','LEFT','texture','GROUND'),'cphos':('zerreibe','LEFT','texture','GROUND')}
assertions={'chol':{'moisture':'DRY'},'shol':{'moisture':'WET'},'shy':{'moisture':'WET'},'oltchy':{'temperature':'COLD','moisture':'DRY'}}
axes=['moisture','temperature','texture']
model={'nouns':nouns,'operators':ops,'assertions':assertions,'CARRY':'same local instance for each whole noun','NEW':'fresh instance only on each okaiin; cthy/chor stable','axes':axes,'time':'source order; forward operation applied at target mention, source retained','assertion_conflict':'retain predicted state, do not overwrite contradiction','unknown_groups':'preserved, no simulated state effects claimed'}
js('MODEL.json',model);js('SOURCE.json',{'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S,D/'DECISION.md']},'scope':pages,'exposure':'Four previously exposed HERB4 paragraphs, not whole pages; no held evaluation','source_correction':'P02 starting observation shol chol shol belongs to f21r.11, not f32v. Original proposal unchanged.','sealed':['f84','f84r']});tab('INPUT.tsv',flat)
def show(st):return ';'.join(k+'='+st[k] for k in axes)
allalign={};mentions=[];events=[];checks=[];summary={}
for mode in ['CARRY','NEW']:
 rec=None;align=[]
 for j,t in enumerate(flat):
  if rec!=t['record']:rec=t['record'];state={};provenance={};current=None;lastloc=None;ids={};counts=Counter();pending={}
  w=t['word'];loc=t['locus'];kind='OPEN';render=f'⟦{w}⟧'
  def apply(op,identity,targetloc,actionloc):
   axis,value=ops[op][2:];before=show(state[identity]) if identity else 'NA'
   if identity:state[identity][axis]=value;provenance[identity][axis]=actionloc
   events.append(dict(mode=mode,record=rec,action_source=actionloc,execution_at=targetloc,word=op,target=identity or 'NA',axis=axis,value=value,before=before,after=show(state[identity]) if identity else 'NA',status='BOUND_TARGET_MISSING_LIQUID' if identity and op=='shytchy' else 'BOUND' if identity else 'MISSING_TARGET'))
  if w in nouns:
   kind='NOUN';slot,gloss=nouns[w];fresh=slot not in ids or (mode=='NEW' and slot=='A');counts[slot]+=int(fresh)
   if fresh:ids[slot]=slot+str(counts[slot]);state[ids[slot]]={a:'UNKNOWN' for a in axes};provenance[ids[slot]]={a:'NA' for a in axes}
   identity=ids[slot];before=show(state[identity]);prior=show(provenance[identity]);current=identity;lastloc=loc
   for op,actionloc in pending.pop(loc,[]):apply(op,identity,loc,actionloc)
   mentions.append(dict(mode=mode,**t,identity=identity,introduction='NEW_INSTANCE' if fresh else 'REUSED_INSTANCE',before=before,prior_axis_sources=prior,after=show(state[identity]),axis_sources=show(provenance[identity])))
   render=f'{gloss}[{identity};'+('neue Instanz' if fresh else 'wiederaufgenommen')+';'+show(state[identity])+']'
  elif w in ops:
   kind='ACTION';gloss,direction,axis,val=ops[w]
   if direction=='LEFT':
    apply(w,current,loc,loc);render=f'{gloss}({current or "ZIEL FEHLT"};Quelle={lastloc or "NA"})'
   else:
    target=None
    for u in flat[j+1:]:
     if u['line']!=t['line'] or u['word'] in ops:break
     if u['word'] in nouns:target=u;break
    if target:pending.setdefault(target['locus'],[]).append((w,loc))
    else:apply(w,None,loc,loc)
    render=f'{gloss}(Zielnennung={target["locus"] if target else "FEHLT"};Vollzug erst dort)'
  elif w in assertions:
   kind='STATE';parts=[]
   for axis,value in assertions[w].items():
    old=state[current][axis] if current else 'UNKNOWN';pr=provenance[current][axis] if current else 'NA'
    status='MISSING_TARGET' if not current else 'INITIAL_CONSTRAINT' if old=='UNKNOWN' else 'CONSISTENT' if old==value else 'CONFLICT'
    checks.append(dict(mode=mode,**t,target=current or 'NA',target_source=lastloc or 'NA',axis=axis,predicted=old,asserted=value,prior_source=pr,status=status))
    if current and old=='UNKNOWN':state[current][axis]=value;provenance[current][axis]=loc
    parts.append(axis+'='+value+'['+status+';vorher='+old+';Quelle='+pr+']')
   render=(current or 'ZIEL FEHLT')+':'+','.join(parts)
  align.append(dict(mode=mode,**t,kind=kind,rendering=render))
 allalign[mode]=align;tab(f'ALIGNMENT_{mode}.tsv',align)
 text=[f'# P02 — vollständige Verlaufsfassung {mode}','','Alle deutschen Wörter, Teilnehmer und Zustandsachsen sind Hypothesen. ⟦…⟧ bleibt offen. Die Ereignisordnung ist keine gelesene Zeitdauer. Konflikte werden nicht durch ungeschriebene Änderungen repariert.','']
 for page in pages:
  text += ['## '+page,'']
  for line in lines:
   if line['locus'].split('.')[0]==page:text += ['**'+line['locus']+'** `'+line['raw_line']+'`','',' · '.join(r['rendering'] for r in align if r['line']==line['locus']),'']
  text+=['### Ereignisse und Zustandserhaltung','']
  for e in events:
   if e['mode']==mode and e['record']==page:text += [f'- {e["action_source"]}, Vollzug {e["execution_at"]}: {ops[e["word"]][0]} {e["target"]}. {e["before"]} → {e["after"]}; {e["status"]}.']
  for c in checks:
   if c['mode']==mode and c['record']==page:text += [f'- {c["locus"]}: {c["target"]} soll {c["axis"]}={c["asserted"]} haben; fortgeführter Wert {c["predicted"]} aus {c["prior_source"]}; {c["status"]}.']
  text+=['']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
 ee=[e for e in events if e['mode']==mode];cc=[c for c in checks if c['mode']==mode];mm=[m for m in mentions if m['mode']==mode]
 summary[mode]={'groups':len(align),'hypothesis':sum(r['kind']!='OPEN' for r in align),'open':sum(r['kind']=='OPEN' for r in align),'operations':dict(Counter(e['status'] for e in ee)),'state_axis_checks':dict(Counter(c['status'] for c in cc)),'instances_per_record':{p:len({m['identity'] for m in mm if m['record']==p}) for p in pages}}
tab('MENTIONS.tsv',mentions);tab('OPERATIONS.tsv',events);tab('STATE_CHECKS.tsv',checks)
diffs=[]
for a in mentions:
 if a['mode']=='CARRY':
  b=next(m for m in mentions if m['mode']=='NEW' and m['locus']==a['locus'])
  if a['identity']!=b['identity'] or a['after']!=b['after']:
   later=[c for c in checks if c['mode']=='CARRY' and c['record']==a['record'] and c['target']==a['identity'] and next(i for i,t in enumerate(flat) if t['locus']==c['locus'])>next(i for i,t in enumerate(flat) if t['locus']==a['locus'])]
   diffs.append(dict(record=a['record'],locus=a['locus'],word=a['word'],CARRY_identity=a['identity'],NEW_identity=b['identity'],CARRY_state=a['after'],NEW_state=b['after'],state_source=a['axis_sources'],later_checks=','.join(c['locus'] for c in later) or 'NONE',decision='NO_LATER_STATE_TEST' if not later else 'CONDITIONAL_CHECK_AVAILABLE'))
tab('IDENTITY_CONSEQUENCES.tsv',diffs)
js('RESULT.json',{'status':'PARTIAL_STATE_CARRY_READING_ONE_UNTESTED_COLD_RETURN','models':summary,'identity_differences':len(diffs),'identity_differences_with_later_state_check':sum(d['later_checks']!='NONE' for d in diffs),'meaning_identifications':0,'independent_confirmation_capacity':0,'scope':'all four exposed HERB4 paragraphs; initial f29v and f32v, then f17r/f21r'})
rep=['# P02 — derselbe Ansatz muss seinen Zustand behalten','','Die feste Lesung erzeugt einen konkreten Unterschied: Auf f29v.4:9 kehrt in CARRY der zuvor gekühlte Ansatz A1 zurück. NEW führt dort A2 mit unbekanntem Zustand ein. Danach folgt im Arbeitsabsatz keine Zustandsangabe, die zwischen beiden entscheidet. Das ist eine neue bedingte Zustandsvorhersage, keine erkannte Bedeutung von okaiin oder otshy.','','| Fassung | Gruppen | Hypothesen / offen | Aktionen | Zustandsprüfungen (Achsen) |','|---|---:|---|---|---|']
for m,c in summary.items():rep.append(f'| {m} | {c["groups"]} | {c["hypothesis"]} / {c["open"]} | {c["operations"]} | {c["state_axis_checks"]} |')
rep+=['','Die Zustandsprüfung arbeitet auf einzelnen Achsen; oltchy erzeugt zwei Prüfzeilen, keine zwei unabhängigen Wörter. Benetzen hat ein Ziel, aber keine gebundene Benetzungsflüssigkeit. Ein Konsistenztreffer bestätigt keine Wortbedeutung.','','## Konkreter Verlauf auf f29v.4','','1. otshy .4:2 wird probeweise als „kühle“ gelesen; die folgende Ansatznennung okaiin .4:3 bindet den Vollzug. A1 erhält COLD. Diese Aktionslesung ist ausdrücklich neu gegenüber der früheren Qualitätsglosse.','2. cthy .4:4 wechselt den aktiven Teilnehmer zu B1. Seine früheren Zustände bleiben erhalten; oltchy prüft Kälte und Trockenheit an B1.','3. shot .4:7 erwärmt B1. Es erwärmt unter der festen Referenzregel nicht A1.','4. okaiin .4:9 nimmt in CARRY A1 samt COLD wieder auf. NEW führt A2 ein und übernimmt COLD nicht. Das unbekannte sho dazwischen wurde nicht als Zustandstransport oder Neuheitsmarker gedeutet.','','Die zweite Nennung ist in NEW der angenommene Einführungsträger; ein besonderer Neuheitsmarker und ein Beschaffungsprozess sind nicht gelesen. Weil kein späterer Zustand an A2/A1 geschrieben zugeordnet wird, sind beide Anfangsannahmen weiter möglich. A2 kann kalt sein, muss es aber nach diesem Modell nicht sein.','','## Alle Konflikte und fehlenden Zustandsziele (CARRY; NEW identisch)','','| Ort | Teilnehmer | Achse | fortgeführt / behauptet | Herkunft | Befund |','|---|---|---|---|---|---|']
for c in checks:
 if c['mode']=='CARRY' and c['status'] in ['CONFLICT','MISSING_TARGET']:rep.append(f'| {c["locus"]} | {c["target"]} | {c["axis"]} | {c["predicted"]} / {c["asserted"]} | {c["prior_source"]} | {c["status"]} |')
rep+=['','Die Trockenbehauptungen auf f29v hängen mehrfach an demselben zuvor benetzten B1. Ohne angenommenes Trocknungsereignis widersprechen sie diesem Konto. Wiederholte Konflikte werden einzeln erhalten, aber nicht als unabhängige Widerlegungen gezählt. Die Konfliktbehandlung überschreibt WET nicht stillschweigend mit DRY. Das ist ein Urteil über diese feste Verlaufshypothese, nicht über die Rezeptgattung.','','Die Folge shol chol shol steht auf f21r.11. Der alte P02-Vorschlag nennt hier f32v irrtümlich; er bleibt bytegleich, die Korrektur steht in DECISION.md/SOURCE.json. Auf f21r setzt die erste Feuchtigkeitsangabe zunächst einen unbekannten Zustand; die anschließende Trockenangabe kollidiert damit. Das erneute WET ist mit dem unverändert geführten Konto vereinbar, belegt aber keine durchgeführte Rückbefeuchtung. Dieses schon aus P18 bekannte Zustandsproblem ist kein neuer Entzifferungsfund.','','f32v ist als vorgesehener zweiter Absatz vollständig mitgelesen; dort gibt es kein okaiin und deshalb keine Übertragungskapazität für dessen Identitätsregel. Auch f17r besitzt keinen Ansatzbeleg, f21r nur einen. Die drei Teilnehmerkarten sind bewusst klein: andere offene Wörter könnten weitere Teilnehmer oder Vorgänge nennen; sie dürfen im aktuellen Konto nicht als kostenlose Reparatur eingesetzt werden.','','## Entscheidung und Nachrechnung','','CARRY liefert die konkrete Vorhersage „derselbe Ansatz bleibt kalt“, NEW lässt den späteren Ansatz offen. Keine der beiden Fassungen wird als richtige Identität ausgewählt. Beide behalten dieselben Zustandskonflikte und sind keine kohärente Gesamtübersetzung. Für eine weitere inhaltliche Lesung fehlt ein ausdrücklich zugeordneter späterer Zustand oder eine anders begründete durchgängige Ereignissprache. Keine Reserveseite wurde dafür geöffnet.','','MENTIONS.tsv bewahrt Zustand und Ursprung jeder Achse an jeder Nennung; OPERATIONS.tsv beide Koordinaten präpositiver Ereignisse; STATE_CHECKS.tsv alle Aussagen; IDENTITY_CONSEQUENCES.tsv jede Modellabweichung. Beide READING-Dateien enthalten die vollständigen Absätze. SOURCE.json bindet die begrenzte Quelle und die vor Ausführung geschriebene Entscheidung.','','`python3 '+str(D/'build.py')+'`; `python3 '+str(D/'validate.py')+'` aus dem Repository. GDT559/700/809 und P12/P06 bleiben unverändert. Keine Signifikanz, keine bestätigten Wörter, keine unabhängige Bestätigung; f84/f84r geschlossen.']
(D/'REPORT.md').write_text('\n'.join(rep)+'\n');print(json.dumps(summary))
