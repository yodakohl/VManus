"""Reverse coverage and relational checks; no import from new model."""
def recognize(lines,lexicon,productions):
    raw=[w for l in lines for w in l['raw'].split()];end=len(raw);out=[]
    assert len(lines)==len(productions)==6
    for line,p in zip(lines[::-1],productions[::-1]):
        begin=end-len(line['raw'].split());tags=[lexicon[w]['tag'] for w in raw[begin:end]]
        assert tags==p['terminal_tags']
        out.append(dict(id=p['id'],production=p['production'],start=begin,end=end,tags=tags));end=begin
    assert end==0
    return out[::-1],raw

def check_relations(g,parent,parts,trace,mode):
    errors=[];times=trace['starts'];streams={v:[x for x in trace['events'] if x[0]==v] for v in parent['assigned']}
    leader=parent['rota'][0];u,l=parent['pes'];rota=set(parent['rota']);pes={u,l}
    if {times[v] for v in pes|{leader}}!={0}:errors.append('D01_INITIAL_ONSET')
    if g['sole_starter']!=leader or any(times[v]<=0 for v in rota-{leader}):errors.append('D02_IDENTITY_OR_SILENCE')
    enum_rel={(i,v) for i,v in enumerate(g['pes_enumeration'])}
    if enum_rel!={(0,u),(1,l)} or g['cursor_final']!=2:errors.append('D03_NOT_COMPLETE_ORDERED_PAIR')
    if mode=='EVERY_MENTION_EXECUTES':
        flattened=[e for d in g['onset_declarations'] for e in d['events']]
        if any(e in flattened[:i] for i,e in enumerate(flattened)):errors.append('D03_SECOND_FIRST_ENTRY')
    for clause,v,expect_end in [('D04',u,True),('D05',l,False)]:
        p=parts[parent['assigned'][v]];stream=streams[v]
        offset=0;prefix={}
        for e in p:prefix[e['id']]=offset;offset+=e['ticks']
        actual_end_rest=p[-1]['kind']=='rest'
        bad=actual_end_rest!=expect_end or (not expect_end and not any(e['kind']=='rest' for e in p[1:-1]))
        if times[v]!=times[leader]:bad=True
        actual_events={tuple(x[:5]+x[6:]) for x in stream}
        expected_count=0
        for cycle in range((trace['window_end']-times[v]+offset-1)//offset):
            for e in p:
                start=times[v]+cycle*offset+prefix[e['id']]
                if start>=trace['window_end']:continue
                expected_count+=1
                if (v,e['id'],cycle,start,start+e['ticks'],0,False) not in actual_events:bad=True
        if len(stream)!=expected_count:bad=True
        if bad:errors.append(clause+'_PART_OR_PHASE')
    if set(g['companions'])!=rota or set(g['group_disjoint'][0])&set(g['group_disjoint'][1]) or any(times[v]<=0 for v in rota-{leader}):errors.append('D06_GROUP_OR_SILENCE')
    if mode=='CO_ONSET_EVERY_MAIN_CYCLE':
        period=sum(e['ticks'] for e in parts[parent['assigned'][leader]])
        for t in range(times[leader],trace['window_end'],period):
            for v in (u,l):
                p=parts[parent['assigned'][v]];period_p=sum(e['ticks'] for e in p)
                if (t-times[v])%period_p:errors.append('STRONGER_EVERY_MAIN_RESTART_CO_ONSET')
    return sorted(set(errors))
