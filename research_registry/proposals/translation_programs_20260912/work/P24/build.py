import csv, json, hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P24')
W=D.parent
sources=[W/'P12/PROSE.tsv', W/'P28/PROSE.tsv', W/'P12/MODEL.json', D/'DECISION.md']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def js(name,obj): (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def tab(name,rows):
    with (D/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rows)
lines=[]
for p,page in [(sources[0],'f83r'),(sources[1],'f82r')]:
    lines += [r for r in csv.DictReader(p.open(),delimiter='\t') if r['page']==page]
assert set(r['page'] for r in lines)=={'f83r','f82r'}
tab('PROSE.tsv',lines)
js('SOURCE.json',{'inputs':{str(p):digest(p) for p in sources},'scope':['f83r','f82r'],'exposure':'Both pages previously exposed; f83r motivation inspected before decision. f82r is unchanged-rule transfer, not independent confirmation. Only cached bounded projections read.','sealed':['f84','f84r']})
model={'pairs':{'B':['okaiin','qokaiin'],'FILL':['okeedy','qokeedy']},'nouns':{'shedy':'A','lchedy':'C','okaiin':'B','qokaiin':'B'},'glosses':{'A':'Flüssigkeit','B':'Gefäß','C':'Zusatzstoff'},'actions':{'chedy':'erwärme','okeedy':'fülle ein','qokeedy':'fülle ein'},'R':'q if prior identical reference else base','I':'base if prior identical reference else q','scope':'record','identity':'P12 L1 REUSE; event signature patient+destination; no forward arguments','L':'distinct whole lexemes with separate Bq/B0 identities; no form prediction'}
js('MODEL.json',model)
all_align={}; refs=[];pred=[];register=[]; totals={}
for mode in ['R','I','L']:
    alignment=[]; reading=[f'# P24 — vollständiges Prose-Arbeitsblatt, Fassung {mode}','', 'Alle deutschen Wörter sind Hypothesen. ⟦…⟧ bleibt unübersetzt. Fehlende Rollen werden nicht ergänzt. IDs gelten nur im jeweiligen Record.','']
    record=None
    for line in lines:
        if line['record_id']!=record:
            record=line['record_id']; seen={}; events={}; patient=None; dest=None
            reading += [f'## {line["page"]} / {record}','']
        chunks=[]
        for i,word in enumerate(line['zl3b_line'].split(),1):
            loc=f'{line["locus"]}:{i}'; before_patient=patient; before_dest=dest
            kind='open'; rendering=f'⟦{word}⟧'; identity='NA'; antecedent='NA'; state='NA'; prediction='NA'; verdict='NA'
            if word in model['nouns']:
                kind='noun'; identity=model['nouns'][word]
                if mode=='L' and identity=='B': identity='Bq' if word=='qokaiin' else 'B0'
                antecedent=seen.get(identity,'NA'); state='KNOWN' if antecedent!='NA' else 'NEW'
                gloss=model['glosses'][model['nouns'][word]]
                if mode=='L' and word=='okaiin': gloss='Behälter'
                rendering=f'{gloss}[{identity};{state};vorher={antecedent}]'
                if word in ('okaiin','qokaiin') and mode!='L':
                    prediction=('qokaiin' if state=='KNOWN' else 'okaiin') if mode=='R' else ('okaiin' if state=='KNOWN' else 'qokaiin')
                seen[identity]=loc
                if identity in ['A','C']: patient=(identity,loc)
                else: dest=(identity,loc)
            elif word in model['actions']:
                kind='action'; isfill=word!='chedy'
                gloss=model['actions'][word]
                if mode=='L' and word=='okeedy': gloss='gieße um'
                rendering=f'{gloss}(Patient={patient[0] if patient else "FEHLT"}' + (f';Ziel={dest[0] if dest else "FEHLT"}' if isfill else '')+')'
                if isfill:
                    if patient and dest:
                        identity=f'{patient[0]}>{dest[0]}'
                        if mode=='L': identity=word+':'+identity
                        antecedent=events.get(identity,'NA');state='KNOWN' if antecedent!='NA' else 'NEW'
                        events[identity]=loc
                        if mode!='L': prediction=('qokeedy' if state=='KNOWN' else 'okeedy') if mode=='R' else ('okeedy' if state=='KNOWN' else 'qokeedy')
                    else: state='UNRESOLVED'
                    rendering+=f'[{state};Vorgangsbezug={antecedent}]'
            if prediction!='NA': verdict='MATCH' if prediction==word else 'CONTRADICTION'
            elif word in ('okeedy','qokeedy') and mode!='L': verdict='UNRESOLVED'
            base={'mode':mode,'page':line['page'],'record':record,'locus':loc,'word':word}
            row=dict(base,kind=kind,identity=identity,prior=antecedent,state=state,prediction=prediction,verdict=verdict,rendering=rendering)
            alignment.append(row); chunks.append(rendering)
            if kind!='open': register.append(dict(base,kind=kind,identity=identity,prior=antecedent,patient=before_patient[0] if before_patient else 'NA',patient_source=before_patient[1] if before_patient else 'NA',destination=before_dest[0] if before_dest else 'NA',destination_source=before_dest[1] if before_dest else 'NA',state=state))
            if mode!='L' and word in ('okaiin','qokaiin','okeedy','qokeedy'): pred.append(row)
        reading += [f'**{line["locus"]}** `{line["zl3b_line"]}`','', ' · '.join(chunks),'']
    tab(f'ALIGNMENT_{mode}.tsv',alignment); (D/f'READING_{mode}.md').write_text('\n'.join(reading).rstrip()+'\n'); all_align[mode]=alignment
    totals[mode]={page:dict(Counter(r['verdict'] for r in pred if r['mode']==mode and r['page']==page)) for page in ['f83r','f82r']} if mode!='L' else {'no_form_constraint':True}
tab('PREDICTIONS.tsv',pred);tab('REGISTER.tsv',register)
coverage={p:{'lines':sum(r['page']==p for r in lines),'groups':sum(r['page']==p for r in all_align['R']),'hypothesis':sum(r['page']==p and r['kind']!='open' for r in all_align['R'])} for p in ['f83r','f82r']}
for c in coverage.values(): c['open']=c['groups']-c['hypothesis']
js('RESULT.json',{'status':'PARTIAL_REFERENCE_READING_BOTH_FIXED_DIRECTIONS_CONTRADICTED','coverage':coverage,'form_predictions':totals,'target_occurrences':len(pred)//2,'target_forms':dict(Counter(r['word'] for r in pred if r['mode']=='R')),'scorable_forms':dict(Counter(r['word'] for r in pred if r['mode']=='R' and r['verdict']!='UNRESOLVED')),'independent_meaning_confirmations':0,'selection_capacity':'No second instance of B or explicit choice relation in inherited REUSE model; contrastive-selection reading not tested.','scope_limit':'Complete cached prose work packages, not complete decipherment or independent full-folio confirmation.'})
report=['# P24 — Referenzstatus muss die geschriebene Form vorhersagen','', 'Beide festen Richtungen kollidieren mit dem Text unter der übernommenen P12-Referenzannahme. Die lexikalische Gegenfassung L bleibt möglich, ohne damit belegt zu sein. Alle Bedeutungen sind vorläufig.','', '| Arbeitsblatt | Zeilen | Gruppen | Hypothesen | Offen |','|---|---:|---:|---:|---:|']
for p,c in coverage.items(): report.append(f'| {p} | {c["lines"]} | {c["groups"]} | {c["hypothesis"]} | {c["open"]} |')
report+=['','| Fassung | Blatt | Form passt | Widerspruch | Argument fehlt |','|---|---|---:|---:|---:|']
for m in ['R','I']:
 for p,c in totals[m].items():report.append(f'| {m} | {p} | {c.get("MATCH",0)} | {c.get("CONTRADICTION",0)} | {c.get("UNRESOLVED",0)} |')
report+=['','R: q bei verfügbarer identischer Referenz, sonst Basis. I: umgekehrt. Zwei feste Ganzformpaare: okaiin/qokaiin und okeedy/qokeedy; keine produktive q-Regel. B wird als derselbe Gefäßgegenstand angenommen; FÜLLEN als derselbe Vorgangstyp mit gleichem Patient und Ziel. Recordgrenzen setzen das Register zurück. Deutsche Kategorien und Identitäten sind P12-L1/REUSE-Hypothesen. Die Gleichsetzungen der zwei Formpaare sind hier zusätzliche Annahmen.','','## Sämtliche konkreten Formprüfungen','','| Ort | Wort | Bezug | Früherer Beleg | R erwartet / Befund | I erwartet / Befund |','|---|---|---|---|---|---|']
ri={(r['locus'],r['mode']):r for r in pred}
for r in pred:
 if r['mode']=='R':
  t=ri[(r['locus'],'I')];report.append(f'| {r["locus"]} | {r["word"]} | {r["identity"]}/{r["state"]} | {r["prior"]} | {r["prediction"]}/{r["verdict"]} | {t["prediction"]}/{t["verdict"]} |')
report+=['','## Entscheidung und nicht unterscheidbare Unterschiede','','Alle 29 entscheidbaren Zielfälle sind q-Formen: 11 neue und 18 bekannte Referenzen. Die beiden Basisformen okeedy (.30:2 und .31:3 auf f83r) gehören zu den neun argumentarmen Fällen; okaiin fehlt auf beiden Arbeitsblättern. Damit fehlt ein entscheidbarer q/Basis-Kontrast vollständig. Gerade die motivierende unmittelbare Folge auf .30 ist ohne Ziel keine gebundene Vorgangswiederaufnahme. f82r.15:4→.16:1 liefert unter der Hypothese denselben vollständigen C>B-Vorgang, behält aber qokeedy statt einer statusbedingten Formänderung. Dies sind Grenzen des konkreten Modells, kein neuer morphologischer Fund.','','Kein R/I-Modell als unbedingte gemeinsame Regel behalten; kein Nachbessern durch unsichtbare Referenten. Ein vorangestelltes q kann unter diesem Modell nicht durchgehend den behaupteten Referenzstatus tragen. Das widerlegt weder jede Referenzgrammatik noch die Möglichkeit unterschiedlicher Lexeme. L zeigt an jeder Textstelle eine solche Gegenfassung, hat aber keine Formvorhersage und darf deshalb nicht als fehlerfreier Gewinner gezählt werden. Andere Lesungen müssen konkret zusätzliche Referenzunterscheidungen herleiten, statt diese nach dem Wortbild festzulegen.','','Die Namen Flüssigkeit, Zusatzstoff und Gefäß könnten unter unveränderter Typ-/Referenzstruktur umbenannt werden; die Formprüfung identifiziert ihre Bedeutung nicht. Wiederholter Typ ist nicht bewiesene Objektidentität. Bei frischen Instanzen könnte der Status anders ausfallen; dies ist hier kein nachträglicher Ausweg und wurde nicht als weiterer Kandidat optimiert. Eine kontrastive Gefäßauswahl besitzt unter REUSE keine zwei verfügbaren B-Instanzen und keine ausdrückliche Auswahlrelation.','','f83r und f82r sind beide vorbekanntes Projektmaterial. f82r prüft unveränderte Anwendung, liefert aber keine unabhängige Bestätigung; beide ganzen physischen Blätter sind vorbelastet. Die Arbeitsdateien decken Prose-Arbeitsblätter ab, nicht alle Bildlabels oder jede mögliche Inschrift. f84/f84r und weitere Reserven bleiben ungeöffnet. Keine Signifikanz, kein bestätigtes Wort, keine score-ready Relationsevidenz.','','## Reproduktion','','`python3 '+str(D/'build.py')+'` und `python3 '+str(D/'validate.py')+'` aus dem Repository. SOURCE.json bindet die bestehenden begrenzten Projektionen und die vor Ausführung geschriebene DECISION.md. PREDICTIONS.tsv enthält jeden Zielfall; REGISTER.tsv alle Nomen/Aktionen; ALIGNMENT_R/I/L.tsv und READING_R/I/L.md bewahren sämtliche Gruppen samt Lücken.','','GDT269/289/290 untersuchten Positionsübertragung; GDT751/752 q/Basis-Kontakte und geerbte Rollen; GDT863 unmittelbares qo-Echo. Ihre Befunde bleiben unverändert. Der neue Unterschied ist die explizite Vorgangssignatur aus Patient und Ziel vor der Formwahl, nicht ein erneuter Positionstest.']
(D/'REPORT.md').write_text('\n'.join(report)+'\n')
print(json.dumps(json.loads((D/'RESULT.json').read_text()),ensure_ascii=False))
