"""Post-result rendering and exact grouping only; no selection or new solver."""
from common import *
import collections,csv

def main():
    rows=read(A/'ROWS.json');pred={p['id']:p for p in read(A/'PREDICTIONS.json')};failures=[];counts=collections.Counter();details=collections.Counter();grouped={}
    for row in rows:
        p=pred[row['id']];signature=(row['context_index'],'FIRST_REFERENCE' if p['shared_values']['chedy']=='FIRST_CARGO' else 'DIFFERENT_CARGO_NAME')
        grouped.setdefault(signature,[]).append(row)
        for wi,w in enumerate(row['witnesses']):
            for v in w['meaning_check'].get('variants',[]):
                if v['variant_index'] not in row['original_valid_variants']:continue
                r=v['paragraphs'][1];counts[r['status']]+=1
                if r['status']=='BINDING_CONTRADICTION':reason=r['error'];details[reason]+=1
                else:
                    reasons=[]
                    for path in r['paths']:
                        reasons.extend((path.get('physical_failure') or {}).get('reasons',[]))
                        reasons.extend(a['reason'] for a in path.get('assertions',[]))
                        if not path['goal_reached']:reasons.append('GOAL_NOT_REACHED')
                    details.update(reasons);reason=','.join(sorted(set(reasons)))
                failures.append([row['id'],wi,v['variant_index'],r['status'],reason,0])
    with (A/'SOURCE_VALID_SETTING_FAILURES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['candidate','witness','variant','added_passage_status','recorded_reasons','independent_meaning_capacity']);w.writerows(failures)
    put('FAILURE_SUMMARY.json',dict(source_valid_setting_cases=len(failures),statuses=dict(counts),binding_case_or_path_event_counts=dict(details),warning='Binding counts count cases;physical/assertion counts count path events and may overlap. Known-original-valid variants only;all32settings remain in ROWS.'))
    with (A/'GROUPED_OUTCOMES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['context_index','chedy_class','original_codes','bank_SAT','bank_UNSAT','saved_maps','coherent_common_settings','independent_meaning_capacity'])
        for (pi,kind),rs in sorted(grouped.items()):w.writerow([pi,kind,len(rs),sum(r['status']=='SAT' for r in rs),sum(r['status']=='UNSAT' for r in rs),sum(len(r['witnesses']) for r in rs),sum(v['status']=='COHERENT_COMMON_READING' for r in rs for x in r['witnesses'] for v in x['meaning_check'].get('variants',[])),0])
    panel=read(A/'PANEL.json');families={}
    for r in read(A/'ORIGINAL_CANDIDATES.json'):
        seen=[]
        for cl in r['parse']:
            for v in cl['symbols']:
                if v in ('W','G','C') and v not in seen:seen.append(v)
        renaming={v:'F'+str(i+1) for i,v in enumerate(seen)}
        code={w:renaming.get(v,v) for w,v in r['code'].items()};key=json.dumps(code,sort_keys=True)
        families.setdefault(key,dict(code=code,parse=[dict(c,symbols=[renaming.get(v,v) for v in c['symbols']]) for c in r['parse']],members=[]))['members'].append(dict(id=r['id'],renaming=renaming,valid_variants=r['valid_variants']))
    assert len(families)==6 and all(len(f['members'])==6 for f in families.values())
    docs=['# Sechs bedingte Lesungsfamilien des Ausgangsabsatzes','',
          'Post-result rendering of the complete GDT1011 result, not a new translation test.',
          'Alle36vollständigen Wörterbücher werden erhalten. Nur die austauschbaren drei',
          'Frachtbezeichner werden nach ihrer ersten ausdrücklichen Nennung F1/F2/F3 genannt.',
          'Jede Familie enthält genau sechs Umbenennungen; gültige Einstellungen sind',
          'innerhalb der Familie gleich. F1 ist keine behauptete Tier- oder Pflanzenart.',
          'Alle Bedeutungen, Satzregeln und der unsichere ZL63Gruppen-Absatz sind Annahmen.',
          'Die folgende deutsche Wiedergabe erklärt das Modell; sie ist keine bestätigte',
          'Übersetzung. FIRST_CARGO/OTHER_CARGO bleiben einstellungsabhängige Verweise.',
          'Die eingeschlossenen Voynich-Rohgruppen werden unverändert wiedergegeben.','',
          '|Familie|lchedy|qokedy|chedy|saiin|Gültige Einstellungsnummern|',
          '|---|---|---|---|---|---|']
    for i,f in enumerate(families.values(),1):
        assert len({tuple(m['valid_variants']) for m in f['members']})==1
        docs.append('|'+str(i)+'|'+'|'.join(f['code'][w] for w in ['lchedy','qokedy','chedy','saiin'])+'|'+','.join(map(str,f['members'][0]['valid_variants']))+'|')
    def say(c):
        k=c['kind'];s=c['symbols']
        if k=='INITIAL':return 'Zu Beginn: Frachten und Person gemeinsam am Ausgangsort.'
        if k=='GOAL':return 'Ziel: das andere Ufer ohne Schaden.'
        if k=='SAFETY':return 'Gefahrenpaare dürfen nicht ohne die Person zusammenbleiben.'
        if k=='CAPACITY':return 'Höchstens eine Fracht neben der Person; Beispiel: '+s[4]+'.'
        if k=='WITH_OUT':return 'Mit dem Boot '+s[3]+' hinüberbringen.'
        if k=='THEN':return 'Dann.'
        if k=='EXCLUDE':return 'Ohne '+s[1]+' zurückfahren (gültige Einstellung EXCLUDING).'
        if k=='FERRY':return 'Mit '+s[1]+' zum anderen Ufer übersetzen.'
        if k=='WITH_RETURN':return 'Mit '+s[1]+' zurückfahren.'
        if k=='PAIR':return s[0]+' und '+s[3]+' wären unbeaufsichtigt ein gefährliches Paar.'
        if k=='COPY':return 'Die entsprechende Paarbeziehung mit OTHER_CARGO übernehmen; den ersten Paarpartner ersetzen.'
        if k=='CONVEY':return 'Als Nächstes '+s[2]+' hinüberbringen.'
        if k=='STAY':return 'Dort zurücklassen (im Modell die zuletzt transportierte Fracht).'
        if k=='ALONE':return 'Allein zurückfahren.'
        if k=='FINAL_TRIP':return 'Schließlich gemeinsam mit '+s[4]+' hinausfahren.'
        if k=='RESULT':return 'Ergebnis: die übrige Fracht ist zusammen mit '+s[3]+'.'
        if k=='CONCLUSION':return 'So sind alle dort unversehrt und von der Person begleitet.'
        raise AssertionError(k)
    source_rows={r['id']:r for r in read(R/inputs()[0]['source_original_rows'])}
    for i,f in enumerate(families.values(),1):
        docs+=['','## Familie '+str(i),'','Mitglieder: '+', '.join(m['id'] for m in f['members'])+'.','',
               '|Gruppen, 1-basiert|Unveränderte Rohgruppen|Modellwiedergabe|','|---|---|---|']
        for cl in f['parse']:docs.append('|'+str(cl['start']+1)+'–'+str(cl['end'])+'|`'+' '.join(panel[0]['words'][cl['start']:cl['end']])+'`|'+say(cl)+'|')
        m=f['members'][0];r=source_rows[m['id']];traces=set()
        for vi in r['valid_variants']:
            for path in r['full_replays'][vi]['paths']:
                if path['consistent'] and len(path['trace'])==8:
                    loads=tuple(m['renaming'].get(t['load'],t['load']) for t in path['trace'][1:]);traces.add(loads)
        docs+=['','Alle erhaltenen vollständigen Fahrtenfolgen dieses Vertreters:']
        for loads in sorted(traces,key=str):docs+=['',' → '.join(x if x is not None else 'leer' for x in loads)]
    docs+=['','## Was diese Prüfung offenlässt','',
           'Alle sechs Familien bleiben durch den f50r-Ufertest ununterschieden.',
           'Die inhaltlich zentrale Fracht gehört in jeder gültigen Einstellung zu',
           'beiden Gefahrenpaaren und wird durch qokedy bezeichnet. Die absolute',
           'Benennung und die oben sichtbaren Gleichheiten/Verweisalternativen bleiben offen.',
           'Der spätere f50r-Absatz besitzt noch keine vollständige gemeinsame Lesung.',
           'Andere GDT1003-Paare behalten ihre eigenen bedingt stimmigen Lesungen.',
           'Bestätigte Wörter und unabhängige Bedeutungskapazität:0.']
    put('ORIGINAL_ALPHA_FAMILIES.json',list(families.values()));(A/'ORIGINAL_READING_FAMILIES.md').write_text('\n'.join(docs)+'\n')
    print(json.dumps(dict(source_valid_setting_cases=len(failures),statuses=dict(counts),original_alpha_families=len(families)),indent=2))
if __name__=='__main__':main()
