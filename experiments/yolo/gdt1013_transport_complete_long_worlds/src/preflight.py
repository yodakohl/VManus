from common import *
import copy,itertools,concurrent.futures,collections

def synthetic(parsed):
    raw=[];lex={};out=[]
    for cl in parsed:
        start=len(raw)
        for symbol in cl['symbols']:
            w='fixture'+str(len(raw));raw.append(w);lex[w]=symbol
        out.append(dict(start=start,end=len(raw),kind=cl['kind'],symbols=cl['symbols']))
    return dict(paragraph=dict(id='SYNTHETIC',words=raw),lexicon=lex,parse=out)

def fixtures():
    s,g=inputs();settings=[dict(zip(g['variants'],x)) for x in itertools.product(*g['variants'].values())]
    family=read(R/'experiments/yolo/gdt1012_transport_necessary_bank_sequence/artifacts/ORIGINAL_ALPHA_FAMILIES.json')
    original={r['id']:r for r in read(A/'ORIGINAL_CANDIDATES.json')};panel=read(A/'PANEL.json');sources=[]
    for f in family:
        r=original[f['members'][0]['id']];sources.append(dict(id='KNOWN_'+r['id'],paragraph=panel[0],lexicon=r['code'],parse=r['parse']))
    base=copy.deepcopy(sources[0]['parse'])
    def add(name,parsed):sources.append(dict(id=name,**synthetic(parsed)))
    for name,left,right in [('COPY_BEFORE_PAIR',7,11),('EARLY_PAIR',6,10),('RETURN_ORDER_SWAP',6,7)]:
        parsed=copy.deepcopy(base);parsed[left],parsed[right]=parsed[right],parsed[left];add(name,parsed)
    for name,where,offset,val in [('SAME_PAIR',10,0,base[10]['symbols'][3]),('FIRST_PAIR',10,0,'FIRST_CARGO'),('OTHER_PAIR',10,0,'OTHER_CARGO'),('FIRST_FERRY',7,1,'FIRST_CARGO'),('OTHER_FERRY',7,1,'OTHER_CARGO'),('FIRST_RESULT',16,3,'FIRST_CARGO'),('OTHER_RESULT',16,3,'OTHER_CARGO')]:
        parsed=copy.deepcopy(base);parsed[where]['symbols'][offset]=val;add(name,parsed)
    for name,position,node in [('EXTRA_COPY',12,base[11]),('COPY_WITHOUT_PRIOR_PAIR',4,base[11]),('TRIP_AFTER_FINAL',16,base[7]),('STAY_WITHOUT_TRIP',4,base[13]),('SECOND_PAIR_NO_COPY_UPDATE',12,base[10]),('SECOND_STAY',14,base[13])]:
        parsed=copy.deepcopy(base);parsed.insert(position,copy.deepcopy(node));add(name,parsed)
    def node(kind,overrides=None):
        sy=[g['types'][t[1:]][0] if t.startswith('@') else t for t in g['patterns'][kind]]
        for i,v in (overrides or {}).items():sy[i]=v
        return dict(kind=kind,symbols=sy)
    prefix=[node(k) for k in ['INITIAL','GOAL','SAFETY','CAPACITY']];end=node('CONCLUSION')
    bodies=[('ONE_CARGO',[node('FERRY',{1:'W'})]),('WRONG_FIRST_RETURN',[node('ALONE')]),('TWO_CARGOS',[node('FERRY',{1:'G'}),node('ALONE'),node('FERRY',{1:'W'})]),('TWO_CARGOS_WITH_PAIR',[node('FERRY',{1:'G'}),node('ALONE'),node('FERRY',{1:'W'}),node('PAIR',{0:'W',3:'G'})]),('PRIOR_VERSUS_FUTURE_NAME',[node('FERRY',{1:'FIRST_CARGO'}),node('ALONE'),node('FERRY',{1:'G'})]),('REPEATED_NAME_IS_NOT_RECENT',[node('PAIR',{0:'W',3:'G'}),node('FERRY',{1:'W'}),node('ALONE'),node('FERRY',{1:'FIRST_CARGO'})])]
    for name,body in bodies:add(name,prefix+body+[end])
    prior=read(R/s['source_rows']);wanted=['L02_009_P2','L02_009_P4','L02_054_P2','L02_054_P4']
    for r in prior:
        if r['id'] in wanted:
            for i,w in enumerate(r['witnesses']):sources.append(dict(id='FAILED_'+r['id']+'_'+str(i),paragraph=panel[r['context_index']],lexicon=w['aliases'],parse=w['parses'][1]))
    jobs=[]
    for source in sources:
        for vi,variant in enumerate(settings):jobs.append({**source,'id':source['id']+'_V'+str(vi),'variant_index':vi,'variant':variant})
    return jobs

def one(j):
    import world,independent
    s,g=inputs();primary=replay(j['parse'],j['variant'],s);other=replay(j['parse'],j['variant'],s,True);assert primary==other,j['id']
    expected=primary['status']=='COHERENT'
    a=world.solve(j['paragraph'],j['lexicon'],g,j['variant'],5000,j['parse'])
    b=independent.check(j['paragraph'],j['lexicon'],g,j['variant'],5000,j['parse'])
    assert a['status']==b['status']==('sat' if expected else 'unsat'),(j['id'],expected,a['status'],b['status'],primary.get('error'))
    return dict(id=j['id'],expected=expected,primary=a['status'],independent=b['status'],ground_status=primary['status'],error=primary.get('error'))

def main():
    jobs=fixtures();put('PREFLIGHT_CASES.json',jobs)
    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:rows=list(pool.map(one,jobs,chunksize=2))
    result=dict(status='PASS',cases=len(rows),outcomes=dict(collections.Counter(r['primary'] for r in rows)),checks=rows,meaning='Known and synthetic differential software checks;no new unconstrained target query.')
    put('PREFLIGHT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
