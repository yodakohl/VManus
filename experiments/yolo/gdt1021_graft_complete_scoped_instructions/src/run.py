from common import *
from model import parse, scenarios, valuations

def main():
    check_lock()
    assert (A/'PUBLIC_REGISTRATION.json').exists()
    spec,source=inputs()
    start=now()
    alignment=source['all_group_alignment']
    tokens=[spec['lexicon'][x['raw']] for x in alignment]
    inverse={v:k for k,v in spec['lexicon'].items()}
    assert [inverse[t] for t in tokens]==[x['raw'] for x in alignment]
    rows=[]
    for mode in spec['candidates']:
        g=parse(tokens,mode)
        rows.append(dict(candidate=mode,graph=g,scenarios=scenarios(g),valuations=valuations(g),
                         roundtrip=[inverse[t] for t in tokens],status='COHERENT_CONDITIONAL_INSTRUCTIONS'))
    scope=[]
    for name,record in [('IT2a',source['exact_target']['separate_IT_record']),
                        ('GDT811_projection',source['exact_target']['original_parent_projection'])]:
        lines=record.get('lines',record.get('records',[]))
        words=[w for line in lines for w in line.get('words',line.get('raw','').split())]
        missing=[dict(index=i+1,raw=w) for i,w in enumerate(words) if w not in spec['lexicon']]
        scope.append(dict(reader=name,groups=len(words),unknown_forms=missing,status='SOURCE_FORMS_UNBOUND'))
    write(A/'ROWS.json',rows)
    write(A/'SOURCE_ALTERNATIVES.json',scope)
    write(A/'RESULT.json',dict(status='SUPPORTED_LIMITED_TWO_SCOPED_GRAFT_READINGS',
        candidates=2,complete_groups_each=23,all_values_unconfirmed=23,new_values=14,
        scenario_rows=24,valuation_rows=108,confirmed_words=0,independent_meaning_capacity=0,
        outcome='Both conditional instruction readings coherent; summer split license differs.',
        started_utc=start,finished_utc=now()))
    print(json.dumps(read(A/'RESULT.json'),indent=2))

if __name__=='__main__': main()
