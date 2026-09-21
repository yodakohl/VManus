"""Fixed new declarations and consequences; no new performance engine."""
def recognize(lines,lex,productions):
    raw=[w for l in lines for w in l['words']];clauses=[];used=[];offset=0
    for line in lines:
        for p in (x for x in productions if x['locus']==line['locus']):
            a,b=p['groups'];words=line['words'][a-1:b]
            assert len(words)==b-a+1
            tags=[lex[w]['tag'] for w in words];assert tags==p['terminal_tags'],p['id']
            clauses.append(dict(id=p['id'],production=p['production'],start=offset+a-1,end=offset+b,tags=tags))
            used+=list(range(offset+a-1,offset+b))
        offset+=len(line['words'])
    assert used==list(range(len(raw))) and len(clauses)==len(productions)
    return clauses,raw

def bind(parent):
    rota=parent['rota'];u,l=parent['pes'];leader=rota[0]
    pred={v:rota[i-1] for i,v in enumerate(rota) if i}
    bank={v:('ENTER:'+v if v in rota else 'FIRST_PART_START:'+v+':'+parent['assigned'][v]) for v in rota+[u,l]}
    return dict(leader=leader,upper=u,lower=l,followers=rota[1:],later=rota[2:],predecessor=pred,event_bank=bank,
        cue=parent['source_referents']['cue'],same_performance=True,
        r_calls=[dict(follower=x,first=bank[x],second=bank[pred[x]],final=bank[leader]) for x in rota[2:]],
        qokaiin_roles=dict(F06=[leader],F10=[[leader,x] for x in rota[2:]]),
        F11_event_pairs=[[bank[x],bank[leader]] for x in rota[2:]])

def first_event(g,v):
    assert v in [g['leader']]+g['followers'],'ENTER_REQUIRES_ROTA_PERFORMER'
    return g['event_bank'][v]

def entry_time(g,trace,v):
    first_event(g,v);return trace['starts'][v]

def complete_stream(v,parent,parts,trace):
    p=parts[parent['assigned'][v]];stream=[e for e in trace['events'] if e[0]==v]
    offset=trace['starts'][v];ok=True
    for i,e in enumerate(stream):
        expected=p[i%len(p)]
        ok &= e[1]==expected['id'] and e[2]==i//len(p) and e[3]==offset and e[4]==offset+expected['ticks'] and e[6]==0 and e[7] is False
        offset+=expected['ticks']
    expected_covered=offset>=trace['window_end'] and bool(stream)
    return bool(ok and expected_covered),stream

def check(g,parent,parts,trace,mode):
    assert mode in ('V_PROHIBITIVE','V_POSITIVE')
    errors=[];ev={};starts=trace['starts'];leader=g['leader'];u=g['upper'];l=g['lower'];later=g['later'];followers=g['followers']
    def add(cid,ok,**evidence):
        ev[cid]=dict(satisfied=bool(ok),**evidence)
        if not ok:errors.append(cid)
    cue=g['cue'];repeat=[]
    for f in followers:
        ok,stream=complete_stream(f,parent,parts,trace)
        full=[e for e in stream if e[1]==parts[parent['assigned'][f]][-1]['id'] and e[4]<trace['window_end']]
        repeat.append(dict(voice=f,complete_stream=ok,repeat_boundaries=[e[4] for e in full],cue=parent['triggers'][f]['cue']))
    add('F01',all(x['complete_stream'] and x['cue']==cue for x in repeat),followers=repeat)
    pre_entry=[e for e in trace['events'] if e[0] in parent['rota'] and e[3]<starts[e[0]]]
    add('F02',not pre_entry,pre_entry_intervals=pre_entry,all_rota=parent['rota'])
    add('F03',len(parent['pes'])==len(set(parent['pes']))==2 and u in parent['pes'],group=parent['pes'],member=u)
    add('F04',starts[u]==entry_time(g,trace,leader)==0,upper_start=starts[u],entry=first_event(g,leader),entry_time=starts[leader])
    lower_ok,lower_stream=complete_stream(l,parent,parts,trace);period=sum(e['ticks'] for e in parts[parent['assigned'][l]])
    pair_rows=[]
    for x in later:
        predecessor=g['predecessor'][x];a=entry_time(g,trace,x);b=entry_time(g,trace,predecessor)
        pair_rows.append(dict(follower=x,predecessor=predecessor,first_event=first_event(g,x),prior_event=first_event(g,predecessor),times=[a,b],not_together=a!=b,
            lower= l,own_origin=starts[l],period=period,phase_at_entry=(a-starts[l])%period,natural_boundary=(a-starts[l])%period==0,complete_lower_stream=lower_ok))
    add('F05',all(x['not_together'] and x['complete_lower_stream'] for x in pair_rows),instances=pair_rows,vacuous=not later)
    add('F06',starts[u]==starts[l]==entry_time(g,trace,leader),group=[leader,u,l],onsets=[starts[v] for v in [leader,u,l]],referenced_entry=first_event(g,leader))
    owners=[dict(follower=f,actual=parent['triggers'][f]['owner'],required=g['predecessor'][f],actual_cue=parent['triggers'][f]['cue'],required_cue=cue) for f in followers]
    add('F07',all(x['actual']==x['required'] and x['actual_cue']==x['required_cue'] for x in owners),owners=owners)
    waiting=[dict(voice=f,interval=[0,starts[f]],bad_events=[e for e in trace['events'] if e[0]==f and e[3]<starts[f]]) for f in followers]
    add('F08',all(x['interval'][1]>0 and not x['bad_events'] for x in waiting),waiting=waiting)
    cues=[e[3] for e in trace['events'] if e[0]==leader and e[1]==cue and e[2]==0]
    guard=min(cues) if cues else None
    pending=[] if guard is None else [v for v in parent['rota'] if starts[v]>guard]
    violations=[] if guard is None else [e for e in trace['events'] if e[0] in pending and e[3]<=guard<e[4]]
    add('F09',guard is not None and not violations,guard_time=guard,pending_after_batch=pending,bad_events=violations)
    f10=[];f11=[]
    for x in later:
        a=entry_time(g,trace,leader);b=entry_time(g,trace,x);equal=a==b
        f10.append(dict(roles=[leader,x],times=[a,b],exists_common_time=equal,prohibition_satisfied=not equal))
        active=guard is not None
        f11.append(dict(roles=[x,leader],events=[first_event(g,x),first_event(g,leader)],times=[b,a],guard_attained=active,co_onset=equal,together=equal,polarity='PROHIBIT' if mode=='V_PROHIBITIVE' else 'REQUIRE',satisfied=(not active) or (not equal if mode=='V_PROHIBITIVE' else equal),same_relation_as_F10=True))
    add('F10',all(x['prohibition_satisfied'] for x in f10),instances=f10,vacuous=not later)
    add('F11',all(x['satisfied'] for x in f11),instances=f11,vacuous=not later,guard_time=guard,guard_is_existing_sing_process=True)
    return dict(status='CONTRADICTED' if errors else 'COHERENT',errors=errors,evidence=ev,ending_capacity='NO_DISCRIMINATING_CAPACITY' if not later else 'NONEMPTY_ASSUMED_SCOPE',new_entry_executions=0)
