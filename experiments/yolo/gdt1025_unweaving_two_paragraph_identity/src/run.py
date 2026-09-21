from common import *
import model

def main():
    check_lock();assert (A/'PUBLIC_REGISTRATION.json').exists();begun=now()
    s=source();sp=spec();oldsp=read(OLD/'src/SPEC.json')
    oldmodel=module('old_forward',OLD/'src/model.py')
    words=[w for c in s['new_complete_clauses'] for w in c['raw'].split()]
    parsed,unknown=oldmodel.parse_all(words,sp)
    assert not unknown
    oldrows=read(OLD/'artifacts/ROWS.json');rows=[]
    for pairing in sp['pairings']:
        parent=next(x['result']['parses'][0]['graph'] for x in oldrows if x['pairing']==pairing)
        for mode in sp['modes']:
            readings=[]
            for p in parsed:
                try:
                    graph=model.construct(p);result=model.join(graph,parent,mode)
                    readings.append(dict(parse=p,new_graph=graph,joint=result))
                except ValueError as e:readings.append(dict(parse=p,status='CONSTRUCTION_FAILURE',error=str(e)))
            rows.append(dict(pairing=pairing,mode=mode,complete_parse_count=len(parsed),readings=readings))
    write(A/'ROWS.json',rows)
    it=s['target']['alternate_reader_comparator'];unknown_it=[dict(locus=l['locus'],group=i,raw=w) for l in it['lines'] for i,w in enumerate(l['words'],1) if w not in sp['lexicon']]
    write(A/'DIPLOMATIC_SCOPE.json',dict(new_ZL_groups=63,IT_groups=64,IT_unknown=unknown_it,IT_status='NO_COMPLETE_FIXED_READING',new_ZL_ineligible_lines=[l['locus'] for l in s['target']['new_complete_record']['lines'] if not l['anchor_eligible']],old_ZL_unbound=["salche'dy",'saii@208;']))
    write(A/'RESULT.json',dict(status='COMPLETED_PENDING_VALIDATION',started_utc=begun,finished_utc=now(),groups=96,types=64,new_types=40,reused_old_types=7,reused_old_positions=17,parse_count=len(parsed),outcomes=[dict(pairing=r['pairing'],mode=r['mode'],statuses=[x.get('joint',{}).get('status',x.get('status')) for x in r['readings']]) for r in rows],confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'RESULT.json'),indent=2))

if __name__=='__main__':main()
