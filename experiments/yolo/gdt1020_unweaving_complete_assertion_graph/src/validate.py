from common import *
import independent,collections

def main():
    checklock();spec,source=inputs();words=sum([l['raw'].split() for l in source['projected_lines']],[]);rows=read(A/'ROWS.json');assert len(rows)==len(spec['candidates'])
    expected_parses=independent.parses(words,spec);checks=[];reverse={tuple(x):w for w,x in spec['lexicon'].items()}
    for case,r in zip(spec['candidates'],rows,strict=True):
        assert case['id']==r['candidate'] and case['pairing']==r['pairing']
        assert expected_parses==[q['parse'] for q in r['result']['parses']]
        for q in r['result']['parses']:
            parse=q['parse'];flat=[reverse[tuple(t)] for c in parse for t in c['tokens']];assert flat==words
            try:expected=independent.facts(parse,r['pairing']);valid=True
            except ValueError:valid=False
            assert valid==(q['status']=='COMPLETE_CONDITIONAL_READING')
            if valid:
                graph=q['graph'];independent.validate_graph(parse,graph,r['pairing'])
                for i,(cl,t) in enumerate(zip(parse,graph['trace'],strict=True),1):
                    assert t['clause']=='C'+str(i) and all(t[k]==cl[k] for k in ['kind','start','end'])
                    assert t['new_events']==[e['id'] for e in graph['events'] if e['clause']==t['clause']]
                phases={e['action']:e['phase'] for e in graph['events'] if e['kind']=='HABIT'}
                assert phases==case['prediction'];kinds=collections.Counter(e['kind'] for e in graph['events'])
                assert kinds==dict(HABIT=2,PLEDGE=1,INFORM=1,DISCOVER=1,BOUNDED_ACTION=1)
                assert len(graph['prerequisites'])==len(graph['endpoints'])==1
                assert [e['phase'] for e in graph['events'] if e['kind']=='DISCOVER']==['NIGHT']
                assert sum('asserted_state' in e for e in graph['events'])==1
                checks.append(dict(candidate=r['candidate'],status='VERIFIED_CONDITIONAL_READING',events=expected,whole_positions=33,computed_habit_phases=phases,independent_meaning_capacity=0))
            else:checks.append(dict(candidate=r['candidate'],status='VERIFIED_BINDING_OR_CONTRADICTION',whole_positions=33))
    raw=[w for line in source['diplomatic_record']['lines'] for w in line['words']];missing=[dict(position=i+1,word=w) for i,w in enumerate(raw) if w not in spec['lexicon']]
    assert not independent.parses(raw,spec) and read(A/'DIPLOMATIC_SCOPE.json')['unknown']==missing
    put('INDEPENDENT.json',checks);put('VALIDATION.json',dict(status='PASS',candidates=len(rows),complete_parses=len(expected_parses),group_positions=33,checked_whole_graphs=len(checks),diplomatic_unbound_forms=missing,completed_utc=now(),claim='Implementation agreement on exposed conditional graph;not independently confirmed meaning.'))
    print(json.dumps(dict(status='PASS',candidates=len(rows),parses=len(expected_parses),graphs=len(checks),diplomatic_missing=len(missing))))
if __name__=='__main__':main()
