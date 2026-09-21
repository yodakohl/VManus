from common import *
from independent import interpret

def canonical(rows):
    return sorted(json.dumps(x,sort_keys=True) for x in rows)

def main():
    check_lock()
    spec,source=inputs(); rows=read(A/'ROWS.json')
    raw=[w for line in source['exact_target']['main_record']['lines'] for w in line['words']]
    assert raw==[a['raw'] for a in source['all_group_alignment']]
    assert len(raw)==len(set(raw))==23
    tokens=[spec['lexicon'][w] for w in raw]
    outputs=[]
    for row in rows:
        g,ss,vv=interpret(tokens,row['candidate'])
        assert row['graph']==g and row['scenarios']==ss
        assert canonical(row['valuations'])==canonical(vv)
        assert row['roundtrip']==raw
        assert [i for c in g['clauses'] for i in range(c['start'],c['end'])]==list(range(23))
        assert len(vv)==54 and len(ss)==12
        for season in spec['season_domain']:
            licensed=[x['method'] for x in ss if x['season']==season and not x['refuses'] and x['instruction_licensed']]
            assert licensed==spec['expectations'][row['candidate']][season]
        # Every other graft's product can exist when this one is refused.
        for m in spec['method_domain']:
            others=[n for n in spec['method_domain'] if n!=m]
            assert any(v['refused'][m] and all(v['graft_products'][n] for n in others)
                       and v['stock_own_product'] for v in vv)
            assert any(not v['refused'][m] and not v['graft_products'][m] for v in vv)
        outputs.append(dict(candidate=row['candidate'],status='PASS',graph=g,scenarios=ss,valuations=vv))
    alternatives=read(A/'SOURCE_ALTERNATIVES.json')
    for obj in alternatives:
        expected=['tcho?','qofcho','chekeg'] if obj['reader']=='IT2a' else ['tcho']
        assert [x['raw'] for x in obj['unknown_forms']]==expected
    # One method/season difference, present for both supplied refusal values.
    differences=[(a['season'],a['method'],a['refuses']) for a,b in zip(rows[0]['scenarios'],rows[1]['scenarios']) if a!=b]
    assert differences==[('SUMMER','SPLIT',False),('SUMMER','SPLIT',True)]
    write(A/'INDEPENDENT.json',outputs)
    write(A/'VALIDATION.json',dict(status='PASS',executed_utc=now(),groups=23,candidates=2,
          scenario_rows=24,valuation_rows=108,scope_differences=differences,
          capacity='Same author and exposed sources; independent implementation, not independent meaning.'))
    print(json.dumps(read(A/'VALIDATION.json'),indent=2))

if __name__=='__main__': main()
