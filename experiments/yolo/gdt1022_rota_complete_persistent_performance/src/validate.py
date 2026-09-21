from common import *
from independent import compile_reverse,execute_arithmetic,independently_check
from fractions import Fraction
import math

def independently_make_parts(s,b):
    parts={}
    for name in ('M','P1','P2'):
        parts[name]=[]
        for e in s['events']:
            if e['part']!=name:continue
            duration=Fraction(b['changes'].get(e['id'],s['baseline_conditional_duration_breves'][e['id']]))
            ticks=duration.numerator*2//duration.denominator
            assert Fraction(ticks,2)==duration
            parts[name].append(dict(id=e['id'],ticks=ticks,kind={'pause':'rest','note':'note'}[e['kind']],pitch=(e.get('pitch_reading') or {}).get('midi_under_c4_octave_convention')))
    return parts

def main():
    check_lock();s=source();sc=score();rows=read(A/'PERFORMANCES.json');graphs=read(A/'GRAPHS.json');checks=[]
    assert len(rows)==36 and len(graphs)==3
    raw=[w for l in s['target']['owned_projection']['records'] for w in l['raw'].split()]
    assert len(raw)==62 and len(set(raw))==53
    for saved in graphs:
        n=saved['n'];g=compile_reverse(s['target']['owned_projection']['records'],s['lexicon'],s['whole_paragraph_clauses'],n)
        assert saved['graph']==g and g['raw_roundtrip']==raw
        assert [i for c in g['clauses'] for i in range(c['start'],c['end'])]==list(range(62))
        assert set(r for c in s['whole_paragraph_clauses'] for r in c['source_relationship'] if r.startswith('R0') and len(r)==3)=={'R01','R02','R03','R04','R05','R06','R07'}
        for branch in sc['documentary_duration_branches']:
            parts=independently_make_parts(sc,branch)
            periods={k:sum(e['ticks'] for e in es) for k,es in parts.items()}
            assert periods=={'M':288,'P1':46 if branch['id'].startswith('C2') else 48,'P2':46 if branch['id'].startswith('C2') else 48}
            horizon=(n-1)*24+math.lcm(*periods.values())
            for mode in ('BASELINE','STAR_OWNER','RESET_PES'):
                actual=next(x for x in rows if x['n']==n and x['branch']==branch['id'] and x['mode']==mode)
                expected=execute_arithmetic(g,parts,mode,horizon)
                for key,value in expected.items():assert actual[key]==value,(n,branch['id'],mode,key)
                failures=independently_check(g,parts,expected)
                assert actual['failures']==failures
                assert bool(failures)==(mode=='RESET_PES' or (mode=='STAR_OWNER' and n>2))
                checks.append(dict(n=n,branch=branch['id'],mode=mode,status='PASS',event_count=len(expected['events']),failures=failures))
                if mode=='BASELINE':
                    assert [expected['starts'][v] for v in g['rota']]==list(range(0,n*24,24))
                    for v in g['followers']:
                        t=expected['starts'][v]
                        for pes in g['pes']:
                            ev=next(x for x in expected['events'] if x[0]==pes and x[3]<=t<x[5])
                            # Event provenance plus cycle proves no phase restart.
                            offsets={};at=0
                            for e in parts[g['assigned'][pes]]:offsets[e['id']]=at;at+=e['ticks']
                            phase=offsets[ev[1]]+(t-ev[3])
                            assert phase==t%at
            cert=next(c for c in read(A/'SERIAL_COUNTERMODEL.json') if c['n']==n and c['branch']==branch['id'])
            assert len(cert['all_start_orders'])==6
            assert all(not x['initially_simultaneous'] and len(set(x['starts'].values()))==3 for x in cert['all_start_orders'])
    unknown=read(A/'DIPLOMATIC_SCOPE.json')['unknown']
    assert [x['raw'] for x in unknown]==['[?:s]cheol','so[r:s]']
    write(A/'INDEPENDENT.json',dict(status='PASS',checks=checks,complete_event_rows_compared=sum(x['event_count'] for x in checks)))
    write(A/'VALIDATION.json',dict(status='PASS',executed_utc=now(),complete_performances=36,baseline_cases=12,
          source_branches=4,groups=62,source_forms_unbound=2,capacity='Same root author and exposed sources; no independent meaning confirmation.'))
    print(json.dumps(read(A/'VALIDATION.json'),indent=2))

if __name__=='__main__':main()
