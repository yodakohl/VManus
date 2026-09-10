#!/usr/bin/env python3
"""Independent full positive replay and necessary-cut audit, not an UNSAT proof.
Source role sequences use the separately audited B-observer compiler only.
No primary fit.py or role_source.py imports. Actual inputs are opened only by CLI.
"""
import argparse,hashlib,json
from pathlib import Path

def require(ok,label):
    if not ok: raise ValueError(label)
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def index(x,n): return type(x) is int and 0<=x<n

def replay(records, paragraphs, witness):
    atoms={a for r in records for a in r['sequence']}
    lex=witness['lexicon']; selected=witness['paragraph_indices']; morph=witness['morphology']
    require(set(lex)==atoms,'complete lexicon')
    require(all(isinstance(w,str) and w for w in lex.values()),'nonempty whole words')
    require(len(set(lex.values()))==len(lex),'global lexicon injective')
    require(len(selected)==len(records) and all(index(j,len(paragraphs)) for j in selected),'record assignment bounds')
    require(len(set(selected))==len(selected),'distinct paragraphs')
    rev={w:a for a,w in lex.items()}
    for r,j in zip(records,selected):
        words=paragraphs[j]['words']
        require(bool(words) and words[0]==lex[r['head_atom']],'first raw word head')
        require([rev[w] for w in words if w in rev]==r['sequence'],'complete global-background projection')
    needed=set()
    for a in atoms:
        if not a.startswith(('PITCH:','VOICE:')): continue
        family,role,rootname=a.split(':',2)
        rk='root/'+family+'/'+rootname;pk='prefix/'+family+':'+role;sk='suffix/'+family+':'+role
        needed.update((rk,pk,sk))
        require(all(k in morph and isinstance(morph[k],str) for k in (rk,pk,sk)),'morphology keys')
        require(bool(morph[rk]),'nonempty semantic root')
        require(morph[pk]+morph[rk]+morph[sk]==lex[a],'shared literal factorization')
    require(set(morph)==needed,'exact morphology variables')
    return True

def check_cuts(records,paragraphs,cuts):
    words=sorted({w for p in paragraphs for w in p['words']})
    atoms={a for r in records for a in r['sequence']}
    for cut in cuts:
        require(len(cut)==6,'cut arity')
        i,a,b,j,wa,wb=cut
        require(index(i,len(records)) and index(j,len(paragraphs)),'cut record/paragraph bounds')
        require(a in atoms and b in atoms and a!=b,'cut distinct atoms')
        require(index(wa,len(words)) and index(wb,len(words)) and wa!=wb,'cut word bounds/injectivity')
        expected=[0 if t==a else 1 for t in records[i]['sequence'] if t in (a,b)]
        actual=[0 if t==words[wa] else 1 for t in paragraphs[j]['words'] if t in (words[wa],words[wb])]
        require(expected!=actual,'binary cut must forbid actual mismatch')
    return len(cuts)

def selftest():
    records=[{'head_atom':'PITCH:0:A','sequence':['PITCH:0:A','VOICE:0:ut','VOICE:0:ut']},{'head_atom':'PITCH:0:B','sequence':['PITCH:0:B','VOICE:0:ut']}]
    paragraphs=[{'words':['pa','bg','vu','vu']},{'words':['pb','vu','bg']}]
    w={'lexicon':{'PITCH:0:A':'pa','PITCH:0:B':'pb','VOICE:0:ut':'vu'},'paragraph_indices':[0,1],'morphology':{'root/PITCH/A':'a','root/PITCH/B':'b','root/VOICE/ut':'u','prefix/PITCH:0':'p','suffix/PITCH:0':'','prefix/VOICE:0':'v','suffix/VOICE:0':''}}
    replay(records,paragraphs,w)
    def fails(fn):
        try:fn()
        except ValueError:return
        raise AssertionError('invalid fixture accepted')
    for modify in [lambda z:z['paragraph_indices'].__setitem__(1,0),lambda z:z['morphology'].__setitem__('root/VOICE/ut',''),lambda z:z['lexicon'].__setitem__('PITCH:0:B','pa')]:
        z=json.loads(json.dumps(w));modify(z);fails(lambda:replay(records,paragraphs,z))
    bad=[{'words':['pa','vu','vu']},{'words':['pb','pa','vu']}]
    fails(lambda:replay(records,bad,w)) # globally assigned word cannot be background
    words=sorted({t for p in paragraphs for t in p['words']})
    cut=[0,'PITCH:0:A','VOICE:0:ut',1,words.index('pa'),words.index('vu')]
    check_cuts(records,paragraphs,[cut])
    cut[3]=0;fails(lambda:check_cuts(records,paragraphs,[cut]))
    z=json.loads(json.dumps(w));z['paragraph_indices'][0]=-1;fails(lambda:replay(records,paragraphs,z))
    return {'status':'PASS','scope':'invented positive, global-background, injectivity, root, bounds and necessary-cut fixtures'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--selftest',action='store_true')
    for name in ('fit','source','target','model-spec','observer','domains','output'):p.add_argument('--'+name,type=Path)
    args=p.parse_args()
    if args.selftest:print(json.dumps(selftest()));return
    require(all(getattr(args,n) for n in ['fit','source','target','model_spec','observer','domains','output']),'all paths required')
    from independent_role_domains import audit_source
    fit=json.loads(args.fit.read_bytes());source=json.loads(args.source.read_bytes());target=json.loads(args.target.read_bytes());spec=json.loads(args.model_spec.read_bytes());observer=json.loads(args.observer.read_bytes())
    for field,path in [('source_sha256',args.source),('target_sha256',args.target),('model_spec_sha256',args.model_spec),('domains_sha256',args.domains)]:require(fit[field]==digest(path),'bound '+field)
    cases=audit_source(source,observer,spec)
    require(index(fit['case'],len(cases)),'case bounds')
    records=cases[fit['case']];require(len(records)==22,'all22records')
    paragraphs=target['panels'][fit['panel']]
    count=0; first=fit['initial']; require(first['status']==fit['status'],'initial status consistency')
    if first['status']=='SAT':replay(records,paragraphs,first['witness']);count+=1
    for q in fit['projections']:
        r=q['result'];require(r['status'] in ('SAT','UNSAT','UNKNOWN'),'query status')
        if r['status']=='SAT':
            replay(records,paragraphs,r['witness']);count+=1
            a=first['witness'];b=r['witness'];kind=q['kind'];key=q['key']
            if kind=='form':different=a['lexicon'][key]!=b['lexicon'][key]
            elif kind=='paragraph':different=a['paragraph_indices'][int(key)]!=b['paragraph_indices'][int(key)]
            elif kind=='morphology':different=a['morphology'][key]!=b['morphology'][key]
            else:raise ValueError('unknown projection kind')
            require(different,'counterexample changes queried value')
    cuts=check_cuts(records,paragraphs,fit['cuts'])
    here=Path(__file__).parent
    out={'status':'PASS','scope':'Positive witnesses and necessary cuts only; UNSAT and universal-value proofs NOT independently established by this audit.','witnesses_checked':count,'cuts_checked':cuts,'fit_sha256':digest(args.fit),'source_sha256':digest(args.source),'target_sha256':digest(args.target),'model_spec_sha256':digest(args.model_spec),'observer_sha256':digest(args.observer),'auditor_sha256':digest(__file__),'source_compiler_dependencies':{name:digest(here/name) for name in ['independent_role_domains.py','independent_domains.py']}}
    args.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
