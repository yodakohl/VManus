from common import *
from model import recognize,bind,check

def main():
    check_lock();assert (A/'PUBLIC_REGISTRATION.json').exists();begun=now()
    s=source();sp=spec();p=read(R/s['frozen_family']['parent_path']);p0=read(R/p['frozen_parent']['path']);sc=read(R/'research_registry/work_batches/ten_hours_20260915/ROTA_SOURCE_EVENTS.json')
    old=module('old_model',OLD/'src/model.py');second=module('second_model',SECOND/'src/model.py')
    traces=read(OLD/'artifacts/PERFORMANCES.json');oldgraphs=read(OLD/'artifacts/GRAPHS.json');secondgraphs=read(SECOND/'artifacts/GRAPHS.json');rows=[];graphs=[]
    clauses,raw=recognize(s['target']['full_record']['lines'],sp['lexicon'],s['complete_new_clauses'])
    for n in sp['n']:
        parent=old.compile_reading(p0['target']['owned_projection']['records'],p0['lexicon'],p0['whole_paragraph_clauses'],n)
        assert parent==next(x['graph'] for x in oldgraphs if x['n']==n)
        prior=second.compile_new(p['complete_new_block_clauses'],s['frozen_family']['all71_entries_unchanged'],p['complete_new_block_clauses'],parent)
        assert prior==next(x['new_graph'] for x in secondgraphs if x['n']==n and x['mode']=='BASELINE')
        g=bind(parent);graphs.append(dict(n=n,clauses=clauses,raw_roundtrip=raw,bindings=g))
        for branch in sc['documentary_duration_branches']:
            parts=parts_for(sc,branch);trace=next(x for x in traces if x['n']==n and x['branch']==branch['id'] and x['mode']=='BASELINE')
            assert old.evaluate_contract(parent,parts,trace)==[]
            assert second.check_new(prior,parent,parts,trace)['errors']==[]
            for mode in sp['models']:
                rows.append(dict(n=n,branch=branch['id'],mode=mode,complete_trace_events=len(trace['events']),**check(g,parent,parts,trace,mode)))
    write(A/'GRAPHS.json',graphs);write(A/'ROWS.json',rows)
    scope=dict(ZL_full_new_groups=55,ZL_new_ineligible_lines=[l['locus'] for l in s['target']['full_record']['lines'] if not l['anchor_eligible']],parent_scope_reference='GDT1024/artifacts/DIPLOMATIC_SCOPE.json',alternate_readers=[])
    for reader in ['IT2a','RF1b']:
        blocks=read(E/f'src/{reader}_WHOLE_BLOCKS.json');issues=[]
        for b in blocks:
            for line in b['lines']:
                expected=next((l for l in s['target']['full_record']['lines'] if l['locus']==line['locus']),None)
                if expected is None or line['words']!=expected['words']:
                    issues.append(dict(locus=line['locus'],actual_words=line['words'],actual_tags=[sp['lexicon'][w]['tag'] if w in sp['lexicon'] else 'UNBOUND:'+w for w in line['words']],required_words=expected['words'] if expected else [],unknown=[w for w in line['words'] if w not in sp['lexicon']]))
        scope['alternate_readers'].append(dict(reader=reader,whole_blocks=[dict(id=b['id'],groups=b['groups']) for b in blocks],issues=issues,status='NO_OWNED_PARAGRAPHS' if not blocks else 'NO_COMPLETE_FIXED_READING' if issues else 'SAME_LITERAL_WORD_SEQUENCE'))
    write(A/'DIPLOMATIC_SCOPE.json',scope)
    write(A/'RESULT.json',dict(status='COMPLETED_PENDING_VALIDATION',started_utc=begun,finished_utc=now(),joint_groups=150,joint_types=91,new_types=20,new_positions=23,reused_old_types=18,reused_old_positions=32,new_productions=11,new_binding_conventions=10,models={mode:{status:sum(x['mode']==mode and x['status']==status for x in rows) for status in ['COHERENT','CONTRADICTED']} for mode in sp['models']},n2_ending_capacity='VACUOUS_NO_DISCRIMINATING_CAPACITY',confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'RESULT.json'),indent=2))
if __name__=='__main__':main()
