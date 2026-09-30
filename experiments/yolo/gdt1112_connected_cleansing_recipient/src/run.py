"""Conditional whole-form role accounting, never a semantic decoder."""
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; HERE=Path(__file__).resolve().parents[1]

def save_tsv(name,rows):
    with (HERE/'artifacts'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    model=json.loads((HERE/'src/MODEL.json').read_text());source=json.loads((HERE/'src/SOURCE.json').read_text());lock=json.loads((HERE/'MODEL_LOCK.json').read_text())
    for p,s in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==s
    alignment=[];cases=[];graphs=[];summaries={};full=['# Complete raw units and three partial C0 readings','All glosses are hypotheses; UNKNOWN groups are retained. No claimed sentence boundary or translation.\n']
    for u in source['units']:
        full.append('## '+u['id']+(' (native)' if u['native'] else ' (unmarked RF window)'))
        flat=[{**g,'locus':l['locus']} for l in u['lines'] for g in l['groups']]
        for line in u['lines']:
            full.append('- '+line['locus']+': '+' | '.join(g['raw'] for g in line['groups']))
            for c,m in model['candidates'].items():
                vals=[]
                for j,g in enumerate(line['groups']):
                    v=m['lexicon'].get(g['raw']);gloss=v['gloss'] if v else 'UNKNOWN';typ=v['type'] if v else 'UNBOUND'
                    if g['raw']=='s' and j+1<len(line['groups']) and line['groups'][j+1]['raw']=='chol':gloss='Teil/Posten von (nur s chol)';typ='PORTION_PREFIX_SCOPED'
                    alignment.append({'candidate':c,'unit':u['id'],'native':str(u['native']),'id':g['id'],'locus':line['locus'],'raw':g['raw'],'gloss':gloss,'type':typ,'confidence':'C0' if typ!='UNBOUND' else 'UNREAD','independent_capacity':0})
                    vals.append(gloss)
                full.append('  - '+c+': '+' | '.join(vals))
        for i,g in enumerate(flat):
            if g['raw']!='lkchey':continue
            slots={'Q':flat[i-1] if i else None,'P':flat[i+1] if i+1<len(flat) else None,'U':flat[i+2] if i+2<len(flat) else None}
            for c,m in model['candidates'].items():
                known={s:m['lexicon'].get(v['raw']) if v else None for s,v in slots.items()};missing=[s for s,v in slots.items() if v is None]
                wrong=[s for s,v in known.items() if v and v['type'] not in m['slot_types'][s]];unknown=[s for s,v in known.items() if slots[s] is not None and not v]
                status='ARITY_CONTRADICTION' if missing else 'TYPE_CONTRADICTION' if wrong else 'UNBOUND_SLOT_MEANINGS' if unknown else 'C0_TYPED_GRAPH_ONLY'
                attach=i>=3 and [x['raw'] for x in flat[i-3:i]]==['qotchy','chody','qotain']
                row={'candidate':c,'unit':u['id'],'marker_id':g['id'],'locus':g['locus'],'native':str(u['native']),'Q_raw':slots['Q']['raw'] if slots['Q'] else '', 'P_raw':slots['P']['raw'] if slots['P'] else '', 'U_raw':slots['U']['raw'] if slots['U'] else '', 'required_types':json.dumps(m['slot_types'],sort_keys=True), 'assigned_types':json.dumps({s:v['type'] if v else 'UNBOUND' for s,v in known.items()},sort_keys=True),'missing':','.join(missing),'incompatible':','.join(wrong),'unbound':','.join(unknown),'status':status,'qotchy_chody_attachment':str(attach),'independent_capacity':0}
                cases.append(row)
                graphs.append({'candidate':c,'marker_id':g['id'],'unit':u['id'],'native':u['native'],'relation':m['lexicon']['lkchey']['gloss'],'slots':{s:{'id':v['id'],'raw':v['raw'],'proposed_type':known[s]['type'] if known[s] else 'UNBOUND','role_allowed_types':m['slot_types'][s]} if v else None for s,v in slots.items()},'attachment':{'efficacy_or_state_id':flat[i-3]['id'],'usage_id':flat[i-2]['id'],'nominal_head_id':flat[i-1]['id']} if attach else None,'status':status,'semantic_binding_independent':False})
    for c in model['candidates']:
        native=[r for r in cases if r['candidate']==c and r['native']=='True'];window=[r for r in cases if r['candidate']==c and r['native']=='False']
        statuses=dict(Counter(r['status'] for r in native));bad=any('CONTRADICTION' in r['status'] for r in native)
        a=[r for r in alignment if r['candidate']==c]
        summaries[c]={'native_cases':len(native),'native_statuses':statuses,'RF_window_cases':len(window),'aligned_positions':len(a),'hypothesized_positions':sum(r['type']!='UNBOUND' for r in a),'unread_positions':sum(r['type']=='UNBOUND' for r in a),'conditional_construction_decision':'STRICT_CONJUNCTION_CONTRADICTED' if bad else 'MINIMAL_CAPACITY_NOT_MEANING_CONFIRMATION','independent_confirmation_capacity':0}
    result={'decision':'CONNECTED_C0_NO_MEANING_SELECTION','phase':model['phase'],'source_units':len(source['units']),'unique_source_groups':len(alignment)//len(model['candidates']),'alignment_rows':len(alignment),'case_rows':len(cases),'native_paragraph_source_denominators':source['selection']['complete_source_paragraphs'],'native_marker_counts':source['selection']['native_marker_counts'],'physical_leaves':sorted({re.match(r'f(\d+)',u['page']).group(1) for u in source['units']},key=int),'candidate_summaries':summaries,'geometry_prediction_group':['BODY','STOCK','DOSE'],'differences_not_discriminated':'body/drug-stock endpoint and expelled matter versus impurity; quantity-condition-recipient relation; all glosses stipulated','source_specific_803_package_tested':False,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':False,'no_repaired_candidates':True}
    save_tsv('ALIGNMENT.tsv',alignment);save_tsv('CANDIDATE_TABLE.tsv',cases)
    (HERE/'artifacts/GRAPHS.json').write_text(json.dumps(graphs,ensure_ascii=False,indent=2)+'\n')
    (HERE/'artifacts/FULL_READER.md').write_text('\n'.join(full)+'\n')
    (HERE/'artifacts/RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
