from common import *
from model import compile_reading,execute,evaluate_contract,window
import itertools

def main():
    check_lock();assert (A/'PUBLIC_REGISTRATION.json').exists()
    begun=now();s=source();sc=score();rows=[];graphs=[];serial=[]
    for n in (2,3,4):
        g=compile_reading(s['target']['owned_projection']['records'],s['lexicon'],s['whole_paragraph_clauses'],n)
        graphs.append(dict(n=n,graph=g))
        for branch in sc['documentary_duration_branches']:
            parts=source_parts(sc,branch);end,period=window(g,parts)
            for mode in ('BASELINE','STAR_OWNER','RESET_PES'):
                x=execute(g,parts,mode,end);failures=evaluate_contract(g,parts,x)
                rows.append(dict(n=n,branch=branch['id'],mode=mode,status='COHERENT' if not failures else 'CONTRADICTED',
                    failures=failures,common_period_ticks=period,**{k:v for k,v in x.items() if k!='mode'}))
            witnesses=[]
            for order in itertools.permutations(g['startup']):
                t=0;starts={}
                for voice in order:
                    starts[voice]=t;t+=parts[g['assigned'][voice]][0]['ticks']
                witnesses.append(dict(order=order,starts=starts,initially_simultaneous=len(set(starts.values()))==1))
            serial.append(dict(n=n,branch=branch['id'],status='CONTRADICTED_AT_STARTUP',
                               full_trace_status='NOT_EXECUTED_NECESSARY_CONTRADICTION',all_start_orders=witnesses))
    write(A/'GRAPHS.json',graphs);compact(A/'PERFORMANCES.json',rows);write(A/'SERIAL_COUNTERMODEL.json',serial)
    z=s['target']['diplomatic_primary_ZL3b'];unknown=[dict(locus=l['locus'],group=i+1,raw=w) for l in z['lines'] for i,w in enumerate(l['words']) if w not in s['lexicon']]
    write(A/'DIPLOMATIC_SCOPE.json',dict(status='SOURCE_FORMS_UNBOUND',unknown=unknown,alternative_scope=s['target']['alternative_reading_scope']))
    write(A/'RESULT.json',dict(status='COMPLETED_PENDING_VALIDATION',started_utc=begun,finished_utc=now(),
        groups=62,types=53,guessed_new_types=47,baseline_cases=sum(x['mode']=='BASELINE' for x in rows),
        status_counts={mode:{status:sum(x['mode']==mode and x['status']==status for x in rows) for status in ('COHERENT','CONTRADICTED')} for mode in ('BASELINE','STAR_OWNER','RESET_PES')},
        serial_cases=len(serial),confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'RESULT.json'),indent=2))

if __name__=='__main__':main()
