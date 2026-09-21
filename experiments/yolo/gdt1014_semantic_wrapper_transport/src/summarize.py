"""Post-result disclosure of every saved witness; no new solver calls."""
from common import *
from wrappers import relations,contradictions
import collections,csv,itertools

def table(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    cases=read(A/'PREDICTIONS.json');ps=read(A/'ROWS.json');inds=read(A/'INDEPENDENT.json');panel=read(A/'PANEL.json');old={r['id']:r for r in read(A/'ORIGINAL_CANDIDATES.json')}
    gloss=load('experiments/yolo/gdt1013_transport_complete_long_worlds/src/summarize.py','render1013').gloss
    summaries=[];functions=[];words=[];docs=['# Sämtliche vollständigen Lesungen unter der zusätzlichen Bausteinregel','',
      'Die Werte sind bedingte Modellannahmen. F1/F2/F3 bleiben austauschbare Frachtvariablen.',
      'Alle gespeicherten positiven Fassungen werden vollständig gezeigt; Wiederholungen bleiben sichtbar.',
      'Der alte Absatz wird jeweils am ersten vorab benannten Mitglied gezeigt; alle Mitglieder sind geprüft.','']
    for case,p,ind in zip(cases,ps,inds):
        for engine,r in [('primary',p),('independent',ind['independent'])]:
            if r['status']!='sat' or not r['witness_check']['verified']:continue
            code=r['witness']['aliases'];parse=r['witness']['parse'];assert not contradictions(code,case['groups']);new=set(code)-set(case['canonical_lexicon']);by={};active=0;cells=0;multi=0;connected={w for g in case['groups'] for pair in g['pairs'] for w in pair}
            for group in case['groups']:
                d=collections.defaultdict(list)
                for base,out in group['pairs']:d[code[base]].append((base,out,code[out]))
                for val,items in d.items():
                    cells+=1;multi+=len(items)>1;active+=len(items)*(len(items)-1)//2
                    functions.append(dict(case=case['id'],engine=engine,side=group['side'],affix=group['affix'],input_value=val,output_value=items[0][2],attested_base_words=','.join(x[0] for x in items),attested_results=','.join(x[1] for x in items),multiple_distinct_bases=len(items)>1))
            res=r['witness_check']['primary']['result'];paths=[x for x in res['paths'] if x['consistent']];longest=0;run=0
            for cl in parse:run=run+1 if cl['kind']=='THEN' else 0;longest=max(longest,run)
            summary=dict(case=case['id'],engine=engine,family=case['family'],context_index=case['context_index'],variant=case['variant_index'],new_word_assignments=len(new),new_words_in_wrapper_relations=len(new&connected),total_wrapper_functions=len(case['groups']),observed_function_input_cells=cells,reused_input_cells=multi,active_equal_input_pair_constraints=active,THEN_positions=sum(cl['kind']=='THEN' for cl in parse),new_THEN_spellings=sum(code[w]=='THEN' for w in new),longest_THEN_run=longest,cargos=len(res['cargo']),hazard_pairs=len(res['hazards']),voyage_counts=','.join(map(str,sorted({len(x['trace'])-1 for x in paths}))),independent_meaning_capacity=0);summaries.append(summary)
            for word,value in sorted(code.items()):words.append(dict(case=case['id'],engine=engine,word=word,value=value,old=word in case['canonical_lexicon'],wrapper_connected=word in connected))
            member=case['members'][0];original=old[member['original_id']];ren=member['original_to_canonical'];oldparse=[dict(cl,symbols=[ren.get(v,v) for v in cl['symbols']]) for cl in original['parse']]
            docs+=['## '+case['id']+' / '+engine,'',case['context']+'; ursprünglicher Vertreter '+member['original_id']+'.',
                   'Einstellung: `'+json.dumps(case['variant'],sort_keys=True)+'`.','',
                   f"{len(new)} neue Wortwerte; {summary['new_words_in_wrapper_relations']} davon in einer Bausteinrelation. {summary['THEN_positions']} Dann-Stellen, längste Folge {longest}. {len(res['cargo'])} Frachten; {len(res['hazards'])} Gefahrenpaare; Fahrtenzahlen {summary['voyage_counts']}.",'']
            for label,pdata,parsed in [('Ursprünglicher vollständiger Absatz',panel[0],oldparse),('Zusätzlicher vollständiger Absatz',panel[case['context_index']],parse)]:
                docs+=['### '+label,'','|Gruppen|Rohgruppen|Bedingte Wiedergabe|','|---|---|---|']
                for cl in parsed:
                    raw=' '.join(pdata['words'][cl['start']:cl['end']]).replace('|','\\|');docs.append('|'+str(cl['start']+1)+'–'+str(cl['end'])+'|`'+raw+'`|'+gloss(cl)+'|')
            docs.append('')
    assert summaries
    for name,rows in [('WITNESS_SUMMARY.tsv',summaries),('FUNCTIONS.tsv',functions),('ALL_WORD_ASSIGNMENTS.tsv',words)]:table(name,rows)
    (A/'READINGS.md').write_text('\n'.join(docs).rstrip()+'\n')
    selected_fields=['new_word_assignments','new_words_in_wrapper_relations','observed_function_input_cells','reused_input_cells','active_equal_input_pair_constraints','THEN_positions','new_THEN_spellings','longest_THEN_run']
    summary=dict(saved_verified_witnesses=len(summaries),primary_counts=dict(collections.Counter(r['status'] for r in ps)),independent_counts=dict(collections.Counter(r['independent']['status'] for r in inds)),ranges={k:[min(x[k] for x in summaries),max(x[k] for x in summaries)] for k in selected_fields},cargo_counts=dict(collections.Counter(r['cargos'] for r in summaries)),hazard_pair_counts=dict(collections.Counter(r['hazard_pairs'] for r in summaries)),confirmed_words=0,independent_meaning_capacity=0)
    put('WITNESS_SUMMARY.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
