from common import *
from model import compile_reading,execute,evaluate_contract,window
from independent import compile_reverse,execute_arithmetic,independently_check

def main():
    s=source();productions=s['whole_paragraph_clauses']
    tags=sorted({t for p in productions for t in p['terminal_tags']})
    lex={'invented_'+t:{'tag':t} for t in tags}
    lines=[dict(raw=' '.join('invented_'+t for t in p['terminal_tags'])) for p in productions]
    checks=[]
    def event(name,ticks,kind='note'):return dict(id=name,ticks=ticks,kind=kind,pitch=None if kind=='rest' else 60)
    for a in (2,3,5):
        parts={'M':[event('SYN_A',a),event('MN010',2),event('SYN_MR',6,'rest')],
               'P1':[event('SYN_UA',1),event('SYN_UB',2),event('SYN_UR',6,'rest')],
               'P2':[event('SYN_LA',2),event('SYN_LR',6,'rest'),event('SYN_LB',1)]}
        for n in (2,3,4):
            g=compile_reading(lines,lex,productions,n);h=compile_reverse(lines,lex,productions,n)
            assert g==h
            end,_=window(g,parts)
            for mode in ('BASELINE','STAR_OWNER','RESET_PES'):
                x=execute(g,parts,mode,end);y=execute_arithmetic(h,parts,mode,end)
                assert x==y,(a,n,mode)
                fx=evaluate_contract(g,parts,x);fy=independently_check(h,parts,y)
                assert fx==fy,(a,n,mode,fx,fy)
                assert bool(fx)==(mode=='RESET_PES' or (mode=='STAR_OWNER' and n>2))
                checks.append(dict(synthetic_main_first_ticks=a,n=n,mode=mode,failures=fx))
    # Every fitted construction is necessary; test without its final invented token.
    for index in range(14):
        changed=[dict(x) for x in lines];changed[index]['raw']=' '.join(changed[index]['raw'].split()[:-1])
        for fn in (compile_reading,compile_reverse):
            try:fn(changed,lex,productions,3)
            except (AssertionError,KeyError):pass
            else:raise AssertionError(('unrejected clause omission',index))
    # A serial positive-duration clock cannot start all three at zero, regardless
    # of their order. This is a necessary contradiction, not an invented trace.
    import itertools
    serial=[]
    for order in itertools.permutations(['A','B','C']):
        t=0;starts={}
        for voice in order:starts[voice]=t;t+={'A':2,'B':3,'C':1}[voice]
        assert len(set(starts.values()))==3
        serial.append(dict(order=order,starts=starts))
    write(A/'PREFLIGHT.json',dict(status='PASS',executed_utc=now(),performance_checks=checks,
          omitted_clause_checks=14,serial_start_orders=serial,
          scope='Invented terminals and events only; no target performance execution.'))
    print('PASS: 27 synthetic performances, 14 missing-clause negatives, 6 serial orders.')

if __name__=='__main__':main()
