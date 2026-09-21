from common import *
from certificate import inspect_certificate,TRIPS
from synthetic import fixtures
import itertools,collections,concurrent.futures,copy

def make_jobs():
    out=[]
    for base in fixtures():
        if not base['id'].endswith('_V0'):continue
        old=base['parse'];trips=[i for i,x in enumerate(old) if x['kind'] in TRIPS]
        variants=[('NO_MARKER',[]),('EARLY',[1]),('END',[len(old)-1]),('DOUBLE_END',[len(old)-1,len(old)-1])]
        if trips:variants += [('AFTER_FIRST',[trips[0]+1]),('FIRST_AND_END',[trips[0]+1,len(old)-1])]
        for label,markers in variants:
            parsed=[];pos=0
            for i,cl in enumerate(old):
                for _ in range(markers.count(i)):
                    parsed.append(dict(kind='THEN',symbols=['THEN'],start=pos,end=pos+1));pos+=1
                parsed.append(dict(cl,start=pos,end=pos+len(cl['symbols'])));pos+=len(cl['symbols'])
            words=['fixture'+str(i) for i in range(pos)];symbols=[s for c in parsed for s in c['symbols']]
            out.append(dict(id=base['id']+'_'+label,parse=parsed,variant=base['variant'],paragraph=dict(id='SYNTHETIC',words=words),lexicon=dict(zip(words,symbols))))
    return out

def one(j):
    import world,independent
    s,g=inputs();a=replay(j['parse'],j['variant'],s);b=replay(j['parse'],j['variant'],s,True);assert a==b,j['id']
    p=world.solve(j['paragraph'],j['lexicon'],g,j['variant'],3000,j['parse'])
    q=independent.check(j['paragraph'],j['lexicon'],g,j['variant'],3000,j['parse'])
    expected='sat' if a['status']=='COHERENT' else 'unsat';assert p['status']==q['status']==expected,(j['id'],a,p,q)
    return dict(id=j['id'],status=expected,certificate_valid=a['certificate']['valid'],old_existential=a['old_existential'])

def main():
    sequences=0
    for length in range(8):
        for seq in itertools.product(['FERRY','THEN','GOAL'],repeat=length):
            parsed=[dict(kind=k,start=i,end=i+1) for i,k in enumerate(seq)]
            a=inspect_certificate(parsed);b=inspect_certificate(parsed,True);assert a==b
            fresh=False;ok=True
            for k in seq:
                if k=='FERRY':fresh=True
                elif k=='THEN':ok=ok and fresh;fresh=False
            assert a['valid']==ok;sequences+=1
    jobs=make_jobs()
    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:rows=list(pool.map(one,jobs,chunksize=2))
    result=dict(status='PASS',abstract_event_sequences=sequences,complete_synthetic_narratives=len(rows),counts=dict(collections.Counter(r['status'] for r in rows)),rows=rows,scope='Synthetic only;new target certificate predicate not run before public registration.')
    put('PREFLIGHT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
if __name__=='__main__':main()
