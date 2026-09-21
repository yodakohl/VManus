from common import *
from independent import compile_reverse,execute_facts

def main():
    check_lock();s=source();spec=read(E/'src/SPEC.json');rows=read(A/'ROWS.json');checks=[]
    raw=[w for l in s['target']['owned_projection']['records'] for w in l['raw'].split()]
    assert len(raw)==84 and len(set(raw))==71 and len(rows)==10
    for r in rows:
        g=compile_reverse(s['target']['owned_projection']['records'],s['lexicon'],s['complete_clauses'],r['branch'],r['mode'])
        x=execute_facts(g)
        assert r['graph']==g and r['execution']==x
        assert g['raw_roundtrip']==raw
        assert [i for c in g['clauses'] for i in range(c['start'],c['end'])]==list(range(84))
        expected='PRECONDITION_CONTRADICTION' if r['mode'] in ['EARLY_ENCLOSE','IMAGE_AS_PART','BOTH_BRANCHES'] else 'DIFFERENT_SOURCE_CONTENT' if r['mode']=='CHOICE_IN_IMAGE' and r['branch']=='H' else 'COHERENT_CONDITIONAL_ACCOUNT'
        assert r['status']==expected
        goal=x['trace'][1];before=goal['before'];after=goal['after']
        assert {k:v for k,v in before.items() if k!='goals'}=={k:v for k,v in after.items() if k!='goals'}
        assert not after['enclosed'] and after['components']==[]
        if r['mode']=='BASELINE':
            end=x['final_state'];assert end['enclosed'] and end['worn_by']=='W'
            assert end['image_host']=='S' and end['depicted_kind']=='E'
            assert end['under']==['G','P'] and end['components']==['G','P','S'] and g['part_kind']==r['branch']
            assert end['closed_section']==['FIRST','ALPHA']
            assert end['claims']==[['CLAIM_PROTECTION','A','W','Cyranides I.1.1-38'],['CLAIM_SOCIAL','A','W','RULERS','GREAT_PEOPLE','PEOPLE_OF_STANDING'],['CLAIM_OTHER','A']]
            assert len([t for t in x['trace'] if t['operation'][1]=='ENCLOSE'])==1
            assert len([t for t in x['trace'] if t['operation'][1]=='PLACE'])==1
            assert not x['unexecuted_plan']
            assert g['typed_of'][0]['right']=='E' and g['body_source']['kind']==r['branch']
            for step in x['trace']:
                st=step['after']
                if st['image_host'] is not None:assert st['image_host']=='S' and st['depicted_kind']=='E'
                assert set(st['components'])<=set(['S','G','P']) and 'I' not in st['components']
        checks.append(dict(branch=r['branch'],mode=r['mode'],status='PASS',executed_operations=len(x['trace']),unexecuted_operations=len(x['unexecuted_plan']),first_failure=x['first_failure'],content_mismatches=x['content_mismatches']))
    assert [x['raw'] for x in read(A/'DIPLOMATIC_SCOPE.json')['unknown']]==['{ck}al','q{cphh}edy','dche[o:?]kedy']
    write(A/'INDEPENDENT.json',dict(status='PASS',checks=checks,implementation='Separate fact transition representation; same root author and exposed inputs.'))
    write(A/'VALIDATION.json',dict(status='PASS',executed_utc=now(),full_baseline_cases=2,all_model_cases=10,groups=84,raw_forms_unbound=3,confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'VALIDATION.json'),indent=2))

if __name__=='__main__':main()
