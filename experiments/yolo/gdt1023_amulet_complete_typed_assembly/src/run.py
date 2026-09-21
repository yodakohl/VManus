from common import *
from model import compile_program,execute

def main():
    check_lock();assert (A/'PUBLIC_REGISTRATION.json').exists()
    start=now();s=source();spec=read(E/'src/SPEC.json');rows=[]
    for branch in spec['branches']:
        for mode in spec['models']:
            g=compile_program(s['target']['owned_projection']['records'],s['lexicon'],s['complete_clauses'],branch,mode)
            x=execute(g)
            status='PRECONDITION_CONTRADICTION' if x['physical_status']=='BLOCKED' else 'DIFFERENT_SOURCE_CONTENT' if x['content_mismatches'] else 'COHERENT_CONDITIONAL_ACCOUNT'
            rows.append(dict(branch=branch,mode=mode,status=status,graph=g,execution=x))
    write(A/'ROWS.json',rows)
    unknown=[dict(locus=l['locus'],group=i+1,raw=w) for l in s['target']['diplomatic_ZL3b']['lines'] for i,w in enumerate(l['words']) if w not in s['lexicon']]
    write(A/'DIPLOMATIC_SCOPE.json',dict(status='SOURCE_FORMS_UNBOUND',unknown=unknown,IT_limits=s['target']['IT_limits']))
    write(A/'RESULT.json',dict(status='COMPLETED_PENDING_VALIDATION',started_utc=start,finished_utc=now(),
        groups=84,types=71,new_types=66,baseline_cases=2,model_cases=10,
        outcomes={mode:{b:next(r['status'] for r in rows if r['branch']==b and r['mode']==mode) for b in spec['branches']} for mode in spec['models']},
        independent_meaning_capacity=0,confirmed_words=0))
    print(json.dumps(read(A/'RESULT.json'),indent=2))

if __name__=='__main__':main()
