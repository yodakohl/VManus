"""Post-result disclosure only; all locked science stays unchanged."""
from common import *
import csv,ast

def table(name,rows):
    with (A/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

s=source();sc=score();rows=read(A/'PERFORMANCES.json');graphs=read(A/'GRAPHS.json');pred=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'))
candidates=[];phases=[]
for r in rows:
    p=next(p for p in pred if p['branch']==r['branch'] and int(p['rota_singers'])==r['n'])
    if r['mode']=='BASELINE':
        assert [r['starts']['R'+str(i)] for i in range(r['n'])]==ast.literal_eval(p['expected_starts_ticks'])
        assert r['window_end']==int(p['window_end_ticks']) and r['status']==p['expected_full_result']
        period=int(p['pes_period_ticks'])
        for i,t in enumerate(ast.literal_eval(p['expected_starts_ticks'])):
            for voice in ['U','L']:
                ev=next(x for x in r['events'] if x[0]==voice and x[3]<=t<x[5])
                phases.append(dict(branch=r['branch'],rota_singers=r['n'],entry='R'+str(i),entry_breves=t/2,pes=voice,phase_breves=(t%period)/2,owned_event=ev[1],cycle=ev[2],event_started_breves=ev[3]/2))
    candidates.append(dict(branch=r['branch'],rota_singers=r['n'],mode=r['mode'],status=r['status'],starts_breves=json.dumps({k:v/2 for k,v in r['starts'].items()},sort_keys=True),window_end_breves=r['window_end']/2,event_rows=len(r['events']),contradictions=';'.join(r['failures']),independent_meaning_capacity=0))
for r in read(A/'SERIAL_COUNTERMODEL.json'):
    candidates.append(dict(branch=r['branch'],rota_singers=r['n'],mode='SINGLE_GLOBAL_CLOCK',status=r['status'],starts_breves='all six orders in SERIAL_COUNTERMODEL.json',window_end_breves='not executed',event_rows=0,contradictions='C06 initial simultaneity',independent_meaning_capacity=0))
positions=[];i=0
for c in s['whole_paragraph_clauses']:
    for group,w in enumerate(c['raw'].split(),1):
        i+=1;v=s['lexicon'][w]
        positions.append(dict(position=i,locus=c['locus'],group=group,raw_projection=w,clause=c['id'],production=c['production'],tag=v['tag'],hypothetical_meaning=v['meaning'],origin=v['status'],confirmed=False))
table('CANDIDATES.tsv',candidates);table('ALL_POSITIONS.tsv',positions);table('ENTRY_PHASES.tsv',phases)
result=read(A/'RESULT.json');result.update(status='SUPPORTED_LIMITED_COMPLETE_PROJECTED_ROTA_ACCOUNT',validation='PASS',diplomatic_unbound_forms=2,complete_event_rows_independently_compared=read(A/'INDEPENDENT.json')['complete_event_rows_compared'],significance=False)
write(A/'RESULT.json',result)
print(json.dumps(result,indent=2))
