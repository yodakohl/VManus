from common import *
from model import bind,check,first_event,entry_time,recognize
from independent import verify,recognize_reverse
from copy import deepcopy

def main():
    old=module('old_engine',OLD/'src/model.py');tests=[]
    for n in (2,3,4):
        rota=[f'T{i}' for i in range(n)]
        parent=dict(rota=rota,followers=rota[1:],pes=['U','L'],assigned={**{v:'M' for v in rota},'U':'P1','L':'P2'},startup=[rota[0],'U','L'],triggers={v:dict(owner=rota[i],cue='MX') for i,v in enumerate(rota[1:])},source_referents=dict(cue='MX'))
        parts={k:[dict(id=k+'A',ticks=2,kind='note',pitch=60),dict(id='MX' if k=='M' else k+'B',ticks=3,kind='note',pitch=62),dict(id=k+'Z',ticks=1,kind='rest',pitch=None)] for k in ('M','P1','P2')}
        g=bind(parent);t=old.execute(parent,parts)
        for mode in ('V_PROHIBITIVE','V_POSITIVE'):
            r=check(g,parent,parts,t,mode);assert r['errors']==verify(parent,parts,t,mode)
            assert r['errors']==(['F11'] if mode=='V_POSITIVE' and n>2 else [])
            tests.append(dict(test='synthetic_scope',n=n,mode=mode,errors=r['errors']))
        for v in rota:assert first_event(g,v)=='ENTER:'+v and entry_time(g,t,v)==t['starts'][v]
        for v in ('U','L'):
            try:first_event(g,v)
            except AssertionError:pass
            else:raise AssertionError('pes accepted by first-entry reference')
        for mutation in ['missing_follower_event','upper_wrong_time','lower_wrong_time','wrong_cue','star_owner','reset_pes']:
            pp=deepcopy(parent);tt=deepcopy(t)
            if mutation=='missing_follower_event':tt['events'].remove(next(e for e in tt['events'] if e[0]==rota[1]))
            if mutation=='upper_wrong_time':tt['starts']['U']=1
            if mutation=='lower_wrong_time':tt['starts']['L']=1
            if mutation=='wrong_cue':pp['triggers'][rota[-1]]['cue']='not_the_cue'
            if mutation=='star_owner':pp['triggers'][rota[-1]]['owner']=rota[0]
            if mutation=='reset_pes':tt=old.execute(parent,parts,'RESET_PES')
            r=check(g,pp,parts,tt,'V_PROHIBITIVE');assert r['errors']==verify(pp,parts,tt,'V_PROHIBITIVE'),(mutation,r['errors'])
            if mutation not in ('star_owner','reset_pes') or n>2:assert r['errors'],mutation
            tests.append(dict(test=mutation,n=n,errors=r['errors']))
    # Invented surface names, not the manuscript strings or candidate performance.
    lex={f'w{i}':dict(tag=f'TAG{i}') for i in range(22)};lines=[];prods=[]
    for i in range(11):
        lines.append(dict(locus=f'toy.{i}',words=[f'w{2*i}',f'w{2*i+1}']))
        prods.append(dict(id=f'F{i+1:02}',locus=f'toy.{i}',groups=[1,2],production=f'Toy{i}',terminal_tags=[f'TAG{2*i}',f'TAG{2*i+1}']))
    assert recognize(lines,lex,prods)==recognize_reverse(lines,lex,prods)
    for i in range(11):
        bad=deepcopy(lines);bad[i]['words'].pop()
        for f in (recognize,recognize_reverse):
            try:f(bad,lex,prods)
            except (AssertionError,KeyError):pass
            else:raise AssertionError('omitted terminal accepted')
    write(A/'PREFLIGHT.json',dict(status='PASS',created_utc=now(),synthetic_model_cases=tests,omitted_production_tests=11,pes_entry_type_checks=6,scope='Invented model and surface fixtures before public lock; no target execution.'))
    print('PREFLIGHT PASS:24 synthetic cases,11 omitted productions,6 type checks')
if __name__=='__main__':main()
