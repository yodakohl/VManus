from common import *
from model import compile_new,check_new,next_member
from independent import recognize,check_relations

s=source();productions=s['complete_new_block_clauses'];lex={};lines=[]
for j,p in enumerate(productions):
    ws=[]
    for i,tag in enumerate(p['terminal_tags']):
        w='invented_'+str(j)+'_'+str(i);lex[w]={'tag':tag};ws.append(w)
    lines.append(dict(raw=' '.join(ws)))
old=module('old_arithmetic',OLD/'src/independent.py');tested=[]
for n in (2,3,4):
    for length in (4,6):
        voices=['T'+str(i) for i in range(n)];pair=['U','L']
        parent=dict(rota=voices,pes=pair,assigned={**{v:'M' for v in voices},'U':'P1','L':'P2'},source_referents={'cue':'MN010'})
        parts={'M':[dict(id='MN001',ticks=1,kind='note'),dict(id='MN010',ticks=1,kind='note'),dict(id='MR',ticks=length-2,kind='rest')], 'P1':[dict(id='UN',ticks=1,kind='note'),dict(id='UR',ticks=1,kind='rest')], 'P2':[dict(id='LN',ticks=1,kind='note'),dict(id='LR',ticks=1,kind='rest'),dict(id='LN2',ticks=1,kind='note')]}
        trace=old.execute_arithmetic(parent,parts,end=24)
        for mode in read(E/'src/SPEC.json')['models']:
            g=compile_new(lines,lex,productions,parent,mode);a=check_new(g,parent,parts,trace,mode);b=check_relations(g,parent,parts,trace,mode)
            assert a['errors']==b,(mode,a['errors'],b)
            expected=mode in ('COMPANIONS_AS_PES','EVERY_MENTION_EXECUTES','DUPLICATE_PES_CURSOR') or (mode=='CO_ONSET_EVERY_MAIN_CYCLE' and length==4)
            assert bool(b)==expected
            assert recognize(lines,lex,productions)==(g['clauses'],g['raw_roundtrip'])
            tested.append(dict(n=n,main_period=length,mode=mode,errors=b))
        for part in ('P1','P2'):
            broken=json.loads(json.dumps(parts));broken[part][-1]['kind']='note' if part=='P1' else 'rest'
            g=compile_new(lines,lex,productions,parent);a=check_new(g,parent,broken,trace);b=check_relations(g,parent,broken,trace,'BASELINE')
            assert a['errors']==b and ('D04_PART_OR_PHASE' if part=='P1' else 'D05_PART_OR_PHASE') in b
for j in range(6):
    bad=json.loads(json.dumps(lines));bad[j]['raw']=' '.join(bad[j]['raw'].split()[:-1])
    for f in (lambda:compile_new(bad,lex,productions,parent),lambda:recognize(bad,lex,productions)):
        try:f()
        except AssertionError:pass
        else:raise AssertionError('omission accepted')
assert next_member(['X','Y'],0)==('X',1) and next_member(['X','Y'],1)==('Y',2)
try:next_member(['X','Y'],2)
except ValueError:pass
else:raise AssertionError('exhausted cursor accepted')
write(A/'PREFLIGHT.json',dict(status='PASS',executed_utc=now(),synthetic_model_cases=tested,rest_countercases=12,omitted_terminal_cases=6,cursor_exhaustion='rejected',target_compilation=False))
print('PASS: 30 invented performance/model cases, 12 rest countercases, 6 omitted terminals, exhausted cursor')
