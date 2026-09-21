"""New declarations only; the original performance engine stays frozen."""
def next_member(pair,cursor):
    if not 0<=cursor<len(pair):raise ValueError('cursor exhausted')
    return pair[cursor],cursor+1

def compile_new(lines,lexicon,productions,parent,mode='BASELINE'):
    assert len(lines)==len(productions)==6
    clauses=[];raw=[]
    for line,p in zip(lines,productions):
        ws=line['raw'].split();ts=[lexicon[w]['tag'] for w in ws]
        assert ts==p['terminal_tags'],p['id']
        clauses.append(dict(id=p['id'],production=p['production'],start=len(raw),end=len(raw)+len(ws),tags=ts));raw+=ws
    pair=parent['pes'];rota=parent['rota'];leader=rota[0];cursor=0;enumerated=[]
    # D03 has two calls of one operation, over one inherited ordered bank.
    for tag in clauses[2]['tags'][3:]:
        assert tag=='START_NEXT_PES'
        member,cursor=next_member(pair,cursor);enumerated.append(member)
    if mode=='DUPLICATE_PES_CURSOR':enumerated=[pair[0]]*len(enumerated)
    companions=pair[:] if mode=='COMPANIONS_AS_PES' else rota[:]
    bank={v:('ENTER:'+v if v in rota else 'FIRST_PART_START:'+v+':'+parent['assigned'][v]) for v in rota+pair}
    declarations=[dict(clause='D01',events=[bank[v] for v in [leader]+pair],kind='INITIAL'),dict(clause='D03',events=[bank[v] for v in [leader]+enumerated],kind='RESTATE')]
    return dict(clauses=clauses,raw_roundtrip=raw,case_binding='next explicit ROTA: f83r.31',
        parent_roles=dict(rota=rota,pes=pair,leader=leader),sole_starter=leader,
        event_bank=bank,onset_declarations=declarations,pes_enumeration=enumerated,
        cursor_final=cursor,upper=pair[0],lower=pair[1],companions=companions,
        silent_at_initial=rota[1:],co_onset_pairs=[[leader,*pair],[pair[0],leader]],
        preserve_cycles=pair[:],group_disjoint=[pair,companions])

def check_new(g,parent,parts,trace,mode='BASELINE'):
    errors=[];evidence={};starts=trace['starts'];events=trace['events']
    pair=parent['pes'];rota=parent['rota'];leader=rota[0]
    initial=all(starts[v]==0 for v in [leader]+pair)
    evidence['D01']=dict(initial_onsets={v:starts[v] for v in [leader]+pair},equal_initial=initial)
    if not initial:errors.append('D01_INITIAL_ONSET')
    silent=all(starts[v]>0 for v in g['silent_at_initial'])
    evidence['D02']=dict(starter=g['sole_starter'],same_leader=g['sole_starter']==leader,silent_pending=silent,shared_case=True)
    if g['sole_starter']!=leader or not silent:errors.append('D02_IDENTITY_OR_SILENCE')
    enumeration=g['pes_enumeration']==pair and g['cursor_final']==len(pair)
    evidence['D03']=dict(enumerated=g['pes_enumeration'],cursor=g['cursor_final'],complete=enumeration,distinct_first_events=len(set(e for d in g['onset_declarations'] for e in d['events'])))
    if not enumeration:errors.append('D03_NOT_COMPLETE_ORDERED_PAIR')
    if mode=='EVERY_MENTION_EXECUTES':
        active=set();steps=[]
        for d in g['onset_declarations']:
            for event in d['events']:
                failed=event in active;steps.append(dict(clause=d['clause'],event=event,already_active=failed))
                if failed:break
                active.add(event)
            if failed:break
        evidence['literal_mentions']=steps
        if failed:errors.append('D03_SECOND_FIRST_ENTRY')
    for clause,v,terminal in [('D04',g['upper'],True),('D05',g['lower'],False)]:
        p=parts[parent['assigned'][v]];stream=[e for e in events if e[0]==v]
        has_terminal=p[-1]['kind']=='rest';has_internal=any(e['kind']=='rest' for e in p[1:-1])
        phase_ok=all(e[1]==p[i%len(p)]['id'] and e[2]==i//len(p) and e[6]==0 and not e[7] and e[4]-e[3]==p[i%len(p)]['ticks'] for i,e in enumerate(stream))
        continuity=all(b[3]==a[4] for a,b in zip(stream,stream[1:]))
        first=starts[v]==starts[leader]
        ok=has_terminal==terminal and (terminal or has_internal) and phase_ok and continuity and first
        evidence[clause]=dict(voice=v,assigned=parent['assigned'][v],terminal_rest=has_terminal,internal_rest=has_internal,all_events_preserved=phase_ok,continuous=continuity,first_co_onset=first,event_count=len(stream))
        if not ok:errors.append(clause+'_PART_OR_PHASE')
    disjoint=not set(g['group_disjoint'][0])&set(g['group_disjoint'][1])
    old_extent=g['companions']==rota
    evidence['D06']=dict(disjoint=disjoint,old_companions_extent=old_extent,silent_pending=silent)
    if not disjoint or not old_extent or not silent:errors.append('D06_GROUP_OR_SILENCE')
    if mode=='CO_ONSET_EVERY_MAIN_CYCLE':
        main_starts=[e[3] for e in events if e[0]==leader and e[1]==parts[parent['assigned'][leader]][0]['id']]
        checks=[]
        for t in main_starts:
            simultaneous={v:any(e[0]==v and e[1]==parts[parent['assigned'][v]][0]['id'] and e[3]==t for e in events) for v in pair}
            checks.append(dict(time_ticks=t,pes_first_event=simultaneous))
        evidence['every_main_cycle']=checks
        if any(not all(c['pes_first_event'].values()) for c in checks):errors.append('STRONGER_EVERY_MAIN_RESTART_CO_ONSET')
    return dict(status='CONTRADICTED' if errors else 'COHERENT',errors=sorted(set(errors)),evidence=evidence)

def conditional_it(parent,parts):
    rows=[]
    for v in parent['rota']:
        p=parts[parent['assigned'][v]]
        rows.append(dict(voice=v,part=parent['assigned'][v],terminal_event=p[-1]['id'],has_terminal_rest=p[-1]['kind']=='rest',violates_new_without_terminal_rest=p[-1]['kind']=='rest'))
    return dict(status='CONTRADICTED' if any(x['violates_new_without_terminal_rest'] for x in rows) else 'COHERENT',scope='Conditional predicate application only; fixed D05 grammar does not license IT quantifier',rows=rows)
