from common import *
import model,independent,copy,collections

def fixtures():
    spec,_=inputs();shapes=spec['productions'];lex={};serial=0
    definitions=[('ACTION_PAIR',['BUILD','PAIR','UNDO','ITEM']),('PREREQUISITE',['COMPLETE','SOCIAL']),('SECRET_HABIT',['SECRET','UNDO','ACTOR']),('PUBLIC_PLEDGE',['PUBLIC','LIGHT','PLEDGE']),('UNTIL_HABIT',['UNTIL','COMPLETE','BUILD','UNIT','UNIT']),('RESPECTIVE_TIMES',['FIRST','SECOND','RESPECTIVE','ITEM','LIGHT','DARK']),('REPORT_DISCOVERY',['ASSISTANT','REPORT','AUDIENCE','DISCOVER','DARK']),('THEN_COMPLETE',['AFTER','FORCED','BUILD','ACTOR','END'])]
    blocks=[]
    def token(ty,v):
        nonlocal serial
        found=next((w for w,x in lex.items() if x==[ty,v]),None)
        if found:return found
        w='synthetic'+str(serial);serial+=1;lex[w]=[ty,v];return w
    for kind,values in definitions:blocks.append([token(ty,v) for ty,v in zip(shapes[kind],values,strict=True)])
    cases=[dict(id='BASE',blocks=blocks,expected='COMPLETE_CONDITIONAL_READING')]
    for name,index in [('NO_PAIR',0),('NO_PREREQUISITE',1),('NO_WORKER',2),('NO_ENDPOINT',4),('NO_PHASE_ATTACHMENT',5),('NO_AUDIENCE_OR_DISCOVERY',6)]:cases.append(dict(id=name,blocks=[b for i,b in enumerate(blocks) if i!=index],expected='INCOMPLETE_OR_CONTRADICTED'))
    for name,which,pos,value in [('OTHER_CLOTH',5,3,'SECOND_ITEM'),('OTHER_FINAL_WORKER',7,3,'SECOND_ACTOR'),('WRONG_ENDPOINT_ACTION',7,2,'UNDO'),('MIXED_ROW_VALUES',4,4,'OTHER_UNIT')]:
        bs=copy.deepcopy(blocks);ty=lex[bs[which][pos]][0];bs[which][pos]=token(ty,value);cases.append(dict(id=name,blocks=bs,expected='INCOMPLETE_OR_CONTRADICTED'))
    bs=copy.deepcopy(blocks);bs[2],bs[4]=bs[4],bs[2];cases.append(dict(id='ACTION_BEFORE_WORKER',blocks=bs,expected='INCOMPLETE_OR_CONTRADICTED'))
    bs=copy.deepcopy(blocks);bs[7],bs[6]=bs[6],bs[7];cases.append(dict(id='COMPLETION_BEFORE_DISCOVERY',blocks=bs,expected='INCOMPLETE_OR_CONTRADICTED'))
    # Unresolved literal is a coverage issue, distinct from a semantic failure.
    bs=copy.deepcopy(blocks);bs[7][-1]='unbound_fixture';cases.append(dict(id='UNKNOWN_SURFACE',blocks=bs,expected='SOURCE_FORMS_UNBOUND'))
    actual=dict(spec,lexicon=lex)
    return [(c,actual) for c in cases]

def main():
    rows=[]
    for case,spec in fixtures():
        words=sum(case['blocks'],[])
        for pairing in ['direct','reversed']:
            r=model.evaluate(words,spec,pairing);assert r['status']==case['expected'],(case,r)
            p=independent.parses(words,spec)
            assert p==[x['parse'] for x in r.get('parses',[])],case['id']
            for q,a in zip(p,r['parses'],strict=True):
                try:facts=independent.facts(q,pairing);ok=True
                except ValueError:ok=False
                assert ok==(a['status']=='COMPLETE_CONDITIONAL_READING'),case['id']
                if ok:
                    independent.validate_graph(q,a['graph'],pairing)
                    assert len(a['graph']['events'])==6 and len([x for x in a['graph']['events'] if 'asserted_state' in x])==1
                    assert not any(e['kind']=='SOCIAL' for e in a['graph']['events'])
            rows.append(dict(id=case['id'],pairing=pairing,status=r['status']))
    # Independently reject a strict temporal cycle; equal nonstrict ranks allowed.
    e=[dict(id='x'),dict(id='y')];assert temporal_witness(e,[['x','y',False],['y','x',False]])==dict(x=0,y=0)
    try:temporal_witness(e,[['x','y',True],['y','x',False]])
    except ValueError:pass
    else:raise AssertionError('cycle accepted')
    out=dict(status='PASS',synthetic_cases=len(rows),counts=dict(collections.Counter(x['status'] for x in rows)),rows=rows,scope='Invented surface forms/participants only;software fixtures,not manuscript alternatives or semantic evidence.')
    put('PREFLIGHT.json',out);print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
if __name__=='__main__':main()
