"""Complete fixed declaration grammar and persistent event-queue executor."""
import heapq
import math

def compile_reading(lines,lexicon,productions,n):
    assert n in (2,3,4)
    assert len(lines)==len(productions)==14
    consumed=[]; clauses=[];cursor=0
    for line,p in zip(lines,productions):
        words=line['raw'].split();tags=[lexicon[w]['tag'] for w in words]
        assert tags==p['terminal_tags'],p['id']
        clauses.append(dict(id=p['id'],production=p['production'],start=cursor,end=cursor+len(words),tags=tags))
        consumed.extend(words);cursor+=len(words)
    # The whole declaration block is compiled before startup; C14 changes C13.
    rota=['R'+str(i) for i in range(n)]
    followers=rota[1:]
    pair=['U','L']
    assigned={rota[0]:'M',**{r:'M' for r in followers},'U':'P1','L':'P2'}
    repeat={r:'C02' for r in followers}
    repeat.update({'U':'C03','L':'C03+C09',rota[0]:'source cyclic-rota assumption'})
    triggers={followers[0]:dict(owner=rota[0],cue='MN010',source='C07+C12')}
    for i,r in enumerate(followers[1:],2):
        triggers[r]=dict(owner=rota[i-1],cue=triggers[followers[0]]['cue'],source='C08+C12')
    early_forbidden=list(rota)
    early_forbidden.remove(rota[0])
    return dict(clauses=clauses,raw_roundtrip=consumed,rota=rota,followers=followers,pes=pair,
        assigned=assigned,repeat=repeat,startup=[rota[0],*pair],triggers=triggers,
        early_forbidden=early_forbidden,leader_exception=rota[0],
        rest_only={r:'M written rests' for r in followers},
        pause_locations={'U':'END','L':'INTERNAL'},no_added_end_rest=['L'],
        main_rests_longa=list(rota),count_scope=rota,count_excludes=pair,
        known_permitted_count=4,minimum_count=2,maximum_count=None,
        source_referents={'main':'M','upper':'P1','lower':'P2','cue':'MN010'})

def timings(graph,parts,mode='BASELINE'):
    starts={v:0 for v in graph['startup']}
    while len(starts)<len(graph['assigned']):
        changed=False
        for voice,trigger in graph['triggers'].items():
            owner=graph['rota'][0] if mode=='STAR_OWNER' else trigger['owner']
            if voice in starts or owner not in starts: continue
            elapsed=0
            for e in parts[graph['assigned'][owner]]:
                if e['id']==trigger['cue']: break
                elapsed+=e['ticks']
            else: raise AssertionError('unowned cue')
            starts[voice]=starts[owner]+elapsed;changed=True
        assert changed,'unresolved dependency'
    return starts

def window(graph,parts):
    starts=timings(graph,parts)
    period=math.lcm(*(sum(e['ticks'] for e in p) for p in parts.values()))
    return max(starts.values())+period,period

def execute(graph,parts,mode='BASELINE',end=None):
    assert mode in ('BASELINE','STAR_OWNER','RESET_PES')
    starts=timings(graph,parts,mode)
    if end is None:end,_=window(graph,parts)
    resets=sorted(set(starts[r] for r in graph['followers'])) if mode=='RESET_PES' else []
    heap=[];events=[]
    for v,t in starts.items():heapq.heappush(heap,(t,v,0,0,0))
    while heap:
        t,v,index,cycle,epoch=heapq.heappop(heap)
        if t>=end:continue
        p=parts[graph['assigned'][v]];event=p[index]
        natural_end=t+event['ticks']
        reset=next((x for x in resets if t<x<=natural_end),None) if v in graph['pes'] else None
        actual_end=reset if reset is not None else natural_end
        events.append([v,event['id'],cycle,t,natural_end,min(actual_end,end),epoch,reset is not None and reset<natural_end])
        if reset is not None:
            heapq.heappush(heap,(reset,v,0,0,epoch+1))
        else:
            nxt=(index+1)%len(p)
            heapq.heappush(heap,(natural_end,v,nxt,cycle+(nxt==0),epoch))
    return dict(mode=mode,starts=starts,window_end=end,
                events=sorted(events,key=lambda r:(r[0],r[3],r[1])))

def evaluate_contract(graph,parts,execution):
    failures=[];starts=execution['starts'];events=execution['events']
    if any(starts[v]!=0 for v in graph['startup']):failures.append('C06_INITIAL_ONSET')
    for voice,t in graph['triggers'].items():
        cue_events=[e for e in events if e[0]==t['owner'] and e[1]==t['cue'] and e[2]==0]
        assert len(cue_events)==1
        if starts[voice]!=cue_events[0][3]:failures.append('C07_C08_C12_OWNER:'+voice)
        if voice in graph['early_forbidden'] and starts[voice]<cue_events[0][3]:failures.append('C13_EARLY:'+voice)
    for v in graph['assigned']:
        rows=[e for e in events if e[0]==v];p=parts[graph['assigned'][v]]
        for i,e in enumerate(rows):
            expected=p[i%len(p)]
            if e[1]!=expected['id'] or e[2]!=i//len(p) or e[6]!=0 or e[7]:
                failures.append('PERSISTENT_PART:'+v);break
            if e[4]-e[3]!=expected['ticks']:failures.append('DURATION:'+v);break
            if i and e[3]!=rows[i-1][4]:failures.append('CONTINUITY:'+v);break
        rests=[e for e in p if e['kind']=='rest']
        if v in graph['main_rests_longa'] and any(e['ticks']!=6 for e in rests):failures.append('C10_LONGA:'+v)
    if parts['P1'][-1]['kind']!='rest':failures.append('C05_UPPER_END')
    if parts['P2'][-1]['kind']=='rest' or not any(e['kind']=='rest' for e in parts['P2'][1:-1]):failures.append('C05_C09_LOWER_INTERNAL')
    return sorted(set(failures))
