from common import *
from model import parse, scenarios, valuations
from independent import interpret

def canonical(rows):
    return sorted(json.dumps(x,sort_keys=True) for x in rows)

def main():
    # Invented semantic streams, not manuscript or source positions.
    head=['SELECT','STOCK_NOUN','AND','DONOR_NOUN','PREPARE','RECEIVING_PART','OF_FIRST','BY','CUT',
          'METHODS','STOCK_ROLE','DONOR_ROLE','SHOOT_SOURCE']
    tail=['IF','REFUSES','GRAFT','NO','PRODUCT']
    streams=[]
    for seq in (['SPLIT'],['INNER_BARK'],['INNER_BARK','SPLIT']):
        for a,b in (('SUMMER','SPRING'),('SPRING','SPRING')):
            streams.append(head+seq+[a,'BUD',b]+tail)
    cases=[]
    for n,tokens in enumerate(streams):
        for mode in ('GROUPED','NEAREST'):
            g=parse(tokens,mode); h,ss,vv=interpret(tokens,mode)
            assert g==h and scenarios(g)==ss and canonical(valuations(g))==canonical(vv)
            cases.append(dict(case=f'positive-{n}-{mode}',status='PASS'))
    base=streams[0]
    mutations=[base[:i]+base[i+1:] for i in range(len(base))]
    mutations += [base+['EXTRA'],base[:13]+['BUD']+base[14:],base[:13]+['SPLIT','SPLIT']+base[14:]]
    for n,tokens in enumerate(mutations):
        for mode in ('GROUPED','NEAREST'):
            for fn in (parse,interpret):
                try: fn(tokens,mode)
                except (ValueError,AssertionError,IndexError): pass
                else: raise AssertionError(('unrejected synthetic',n,fn.__name__))
        cases.append(dict(case=f'negative-{n}',status='REJECTED_BOTH'))
    write(A/'PREFLIGHT.json',dict(status='PASS',executed_utc=now(),cases=cases,
          purpose='Software checks only; no target execution or meaning selection.'))
    print('PASS',len(cases),'synthetic cases')

if __name__=='__main__': main()
