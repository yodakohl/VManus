"""Post-result complete reading/alias disclosure, not a new selection rule."""
from common import *
import collections,csv

def gloss(cl):
    k=cl['kind'];s=cl['symbols'];v=lambda x:dict(W='F1',G='F2',C='F3',FIRST_CARGO='FIRST_CARGO',OTHER_CARGO='OTHER_CARGO').get(x,x)
    if k=='INITIAL':return 'Zu Beginn: Frachten und Person gemeinsam am Ausgangsort.'
    if k=='GOAL':return 'Ziel: das andere Ufer ohne Schaden.'
    if k=='SAFETY':return 'Gefahrenpaare dürfen nicht ohne die Person zusammenbleiben.'
    if k=='CAPACITY':return 'Höchstens eine Fracht neben der Person; Beispiel '+v(s[4])+'.'
    if k=='WITH_OUT':return 'Mit dem Boot '+v(s[3])+' hinüberbringen.'
    if k=='THEN':return 'Dann.'
    if k=='EXCLUDE':return 'Ohne '+v(s[1])+' zurückfahren.'
    if k=='FERRY':return 'Mit '+v(s[1])+' zum anderen Ufer übersetzen.'
    if k=='WITH_RETURN':return 'Mit '+v(s[1])+' zurückfahren.'
    if k=='PAIR':return v(s[0])+' und '+v(s[3])+' sind unbeaufsichtigt ein gefährliches Paar.'
    if k=='COPY':return 'Entsprechendes Gefahrenpaar mit OTHER_CARGO; ersten Paarpartner ersetzen.'
    if k=='CONVEY':return 'Als Nächstes '+v(s[2])+' hinüberbringen.'
    if k=='STAY':return 'Die zuletzt transportierte Fracht dort zurücklassen.'
    if k=='ALONE':return 'Allein zurückfahren.'
    if k=='FINAL_TRIP':return 'Schließlich gemeinsam mit '+v(s[4])+' hinausfahren.'
    if k=='RESULT':return 'Die übrige Fracht ist zusammen mit '+v(s[3])+'.'
    if k=='CONCLUSION':return 'So sind alle dort unversehrt und von der Person begleitet.'
    raise AssertionError(k)

def main():
    s,g=inputs();cases=read(A/'PREDICTIONS.json');primary=read(A/'ROWS.json');checks=read(A/'INDEPENDENT.json');panel=read(A/'PANEL.json');originals={r['id']:r for r in read(A/'ORIGINAL_CANDIDATES.json')}
    summaries=[];assignments=[];docs=['# Vollständige gemeinsame Modelllesungen','',
      'Alle20primären und alle verfügbaren unabhängigen positiven Wörterbücher werden gezeigt.',
      'F1/F2/F3 sind austauschbare Frachtvariablen (W/G/C),keine entzifferten Namen.',
      'Jede Fassung ist eine bedingte Modellwiedergabe. Viele neue Wörter werden als Dann gelesen;',
      'Folgen solcher Wörter bleiben sichtbar und werden nicht stilistisch geglättet.',
      'FIRST_CARGO und OTHER_CARGO sind Verweisfunktionen der daneben genannten Einstellung.',
      'Für den alten Absatz steht jeweils der erste vorab gelistete Mitgliedskandidat;',
      'alle312Mitglieder und492geprüften Umbenennungen bleiben in den vollständigen Tabellen.','']
    for case,p,check in zip(cases,primary,checks):
        for engine,r in [('primary',p),('independent',check['independent'])]:
            if r['status']!='sat' or not r['witness_check']['verified']:continue
            w=r['witness'];parse=w['parse'];result=r['witness_check']['primary']['result'];paths=[p for p in result['paths'] if p['consistent']]
            member=case['members'][0];orig=originals[member['original_id']];rename=member['original_to_canonical'][0]
            oldcode={word:rename.get(value,value) for word,value in orig['code'].items()};merged={**oldcode,**w['aliases']};assert all(merged[word]==value for word,value in oldcode.items())
            oldparse=[dict(cl,symbols=[rename.get(value,value) for value in cl['symbols']]) for cl in orig['parse']]
            newwords=set(w['aliases'])-set(oldcode);counts=collections.Counter(w['aliases'][word] for word in newwords);run=0;longest=0
            for cl in parse:
                run=run+1 if cl['kind']=='THEN' else 0;longest=max(run,longest)
            q=w['aliases']['qokedy'];degree=sum(q in pair for pair in result['hazards'])
            summ=dict(case=case['id'],engine=engine,context_index=case['context_index'],class_name=case['class_name'],variant_index=case['variant_index'],groups=len(panel[case['context_index']]['words']),new_spellings=len(newwords),new_THEN_spellings=counts['THEN'],THEN_positions=sum(cl['kind']=='THEN' for cl in parse),longest_THEN_run=longest,cargos=len(result['cargo']),hazard_pairs=len(result['hazards']),qokedy_hazard_degree=degree,voyage_counts=','.join(map(str,sorted({len(p['trace'])-1 for p in paths}))),consistent_paths=len(paths),original_example=member['original_id'],independent_meaning_capacity=0)
            summaries.append(summ);oldcounts=collections.Counter(panel[0]['words']);newcounts=collections.Counter(panel[case['context_index']]['words'])
            for word,value in sorted(merged.items()):assignments.append(dict(case=case['id'],engine=engine,word=word,value=value,old_occurrences=oldcounts[word],new_occurrences=newcounts[word],new_word=word not in oldcode))
            docs+=['## '+case['id']+' / '+engine,'','Kontext: '+panel[case['context_index']]['id']+'. Alter Vertreter: '+member['original_id']+'.',
                   'Einstellung: `'+json.dumps(case['variant'],sort_keys=True)+'`.','',
                   str(len(newwords))+' neue Wortzuordnungen; '+str(summ['THEN_positions'])+' Dann-Stellen; längste Dann-Folge '+str(longest)+'.',
                   'Neue Welt: '+str(len(result['cargo']))+' Frachten, '+str(len(result['hazards']))+' Gefahrenpaare, Fahrtenzahlen '+summ['voyage_counts']+'.','']
            for label,pdata,parsed in [('Alter vollständiger Absatz',panel[0],oldparse),('Neuer vollständiger Absatz',panel[case['context_index']],parse)]:
                docs+=['### '+label,'','|Gruppen,1-basiert|Unveränderte Rohgruppen|Bedingte Modellwiedergabe|','|---|---|---|']
                for cl in parsed:
                    raw=' '.join(pdata['words'][cl['start']:cl['end']]).replace('|','\\|');docs.append('|'+str(cl['start']+1)+'–'+str(cl['end'])+'|`'+raw+'`|'+gloss(cl)+'|')
            docs+=['','Vollständige Fahrtenfolge eines tatsächlich konsistenten neuen Pfads (die übrigen stehen in den Ausführungsartefakten):','',
                   ' → '.join('leer' if t['load'] is None else dict(W='F1',G='F2',C='F3')[t['load']] for t in paths[0]['trace'][1:]),'']
    for name,rows in [('WITNESS_SUMMARY.tsv',summaries),('ALL_WORD_ASSIGNMENTS.tsv',assignments)]:
        with (A/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    (A/'READINGS.md').write_text('\n'.join(docs).rstrip()+'\n')
    summary=dict(primary_counts=dict(collections.Counter(r['status'] for r in primary)),independent_counts=dict(collections.Counter(r['independent']['status'] for r in checks)),saved_verified_canonical_witnesses=len(summaries),new_cargo_counts=dict(collections.Counter(r['cargos'] for r in summaries)),new_hazard_pair_counts=dict(collections.Counter(r['hazard_pairs'] for r in summaries)),THEN_positions_range=[min(r['THEN_positions'] for r in summaries),max(r['THEN_positions'] for r in summaries)],longest_THEN_run_range=[min(r['longest_THEN_run'] for r in summaries),max(r['longest_THEN_run'] for r in summaries)],new_THEN_spellings_range=[min(r['new_THEN_spellings'] for r in summaries),max(r['new_THEN_spellings'] for r in summaries)],hazard_witnesses=[r for r in summaries if r['hazard_pairs']],independent_meaning_capacity=0,confirmed_words=0)
    put('WITNESS_SUMMARY.json',summary)
    candidates=[]
    with (A/'CANDIDATES.tsv').open() as f:allrows=list(csv.DictReader(f,delimiter='\t'))
    for oid,orig in originals.items():
        for pi in (2,4):
            local=[r for r in allrows if r['original']==oid and int(r['context_index'])==pi];assert {int(r['variant']) for r in local}==set(orig['valid_variants'])
            candidates.append(dict(original=oid,context_index=pi,valid_original_variants=','.join(map(str,orig['valid_variants'])),positive_variants=','.join(r['variant'] for r in local if r['decision']=='VERIFIED_SHARED_READING'),excluded_variants=','.join(r['variant'] for r in local if r['decision']=='VERIFIED_UNSAT'),unknown_variants=','.join(r['variant'] for r in local if r['decision']=='UNKNOWN'),independent_meaning_capacity=0))
    with (A/'ORIGINAL_CANDIDATE_SUMMARY.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(candidates[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(candidates)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
