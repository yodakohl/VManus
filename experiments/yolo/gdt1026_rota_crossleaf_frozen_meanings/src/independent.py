"""Independent arithmetic/set constraints; no import from new model."""
def recognize_reverse(lines,lex,productions):
    raw=[w for l in lines for w in l['words']];end=len(raw);out=[]
    for p in reversed(productions):
        count=p['groups'][1]-p['groups'][0]+1;start=end-count
        tags=[lex[w]['tag'] for w in raw[start:end]];assert tags==p['terminal_tags']
        out.append(dict(id=p['id'],production=p['production'],start=start,end=end,tags=tags));end=start
    assert end==0
    return out[::-1],raw

def stream_expected(v,parent,parts,trace):
    part=parts[parent['assigned'][v]];length=sum(p['ticks'] for p in part);start=trace['starts'][v]
    expected=set();prefix=0
    for p in part:
        for k in range((trace['window_end']-start+length-1)//length):
            t=start+k*length+prefix
            if t<trace['window_end']:expected.add((v,p['id'],k,t,t+p['ticks'],0,False))
        prefix+=p['ticks']
    actual=[tuple(e[:5]+e[6:]) for e in trace['events'] if e[0]==v]
    return set(actual)==expected and len(actual)==len(expected)

def verify(parent,parts,trace,mode):
    rota=parent['rota'];leader=rota[0];u,l=parent['pes'];F=rota[1:];later=rota[2:];times=trace['starts'];errors=[]
    cue=parent['source_referents']['cue'];streams={v:[e for e in trace['events'] if e[0]==v] for v in parent['assigned']}
    conditions={
      'F01':all(stream_expected(f,parent,parts,trace) and parent['triggers'][f]['cue']==cue for f in F),
      'F02':all(e[3]>=times[v] for v in rota for e in streams[v]),
      'F03':len(parent['pes'])==2 and u!=l,
      'F04':times[u]==times[leader]==0,
      'F05':all(times[x]!=times[rota[rota.index(x)-1]] and stream_expected(l,parent,parts,trace) for x in later),
      'F06':len({times[v] for v in (u,l,leader)})==1,
      'F07':all(parent['triggers'][x]['owner']==rota[i] and parent['triggers'][x]['cue']==cue for i,x in enumerate(F)),
      'F08':all(times[f]>0 and all(e[3]>=times[f] for e in streams[f]) for f in F),
      'F10':all(times[x]!=times[leader] for x in later)
    }
    cue_events=[e for e in streams[leader] if e[1]==cue and e[2]==0]
    t=cue_events[0][3] if cue_events else None
    conditions['F09']=t is not None and not any(e[3]<=t<e[4] for v in rota if times[v]>t for e in streams[v])
    conditions['F11']=all(t is None or ((times[x]!=times[leader]) if mode=='V_PROHIBITIVE' else (times[x]==times[leader])) for x in later)
    return sorted((k for k,v in conditions.items() if not v),key=lambda x:int(x[1:]))
