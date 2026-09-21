"""Reverse recognition, relation reconstruction, arithmetic cycle expansion.

No import from the event-queue executor or forward compiler.
"""
import math

def compile_reverse(lines,lexicon,productions,n):
    assert len(lines)==len(productions)==14 and n in (2,3,4)
    words=[w for l in lines for w in l['raw'].split()];end=len(words);clauses=[]
    for line,p in zip(reversed(lines),reversed(productions)):
        length=len(line['raw'].split());start=end-length
        tags=[lexicon[w]['tag'] for w in words[start:end]]
        assert tags==p['terminal_tags']
        clauses.append(dict(id=p['id'],production=p['production'],start=start,end=end,tags=tags));end=start
    assert end==0
    voices=['R'+str(i) for i in range(n)];pes=['U','L'];followers=voices[1:]
    assigned=dict(zip(voices+pes,['M']*n+['P1','P2']))
    return dict(clauses=clauses[::-1],raw_roundtrip=words,rota=voices,followers=followers,pes=pes,
        assigned=assigned,repeat={**{v:'C02' for v in followers},'U':'C03','L':'C03+C09','R0':'source cyclic-rota assumption'},
        startup=['R0','U','L'],triggers={voices[i]:dict(owner=voices[i-1],cue='MN010',source='C07+C12' if i==1 else 'C08+C12') for i in range(1,n)},
        early_forbidden=followers,leader_exception='R0',rest_only={v:'M written rests' for v in followers},
        pause_locations={'U':'END','L':'INTERNAL'},no_added_end_rest=['L'],main_rests_longa=voices,
        count_scope=voices,count_excludes=pes,known_permitted_count=4,minimum_count=2,maximum_count=None,
        source_referents={'main':'M','upper':'P1','lower':'P2','cue':'MN010'})

def execute_arithmetic(graph,parts,mode='BASELINE',end=None):
    prefixes={};periods={}
    for key,events in parts.items():
        prefixes[key]=[];total=0
        for e in events:prefixes[key].append(total);total+=e['ticks']
        periods[key]=total
    delay=prefixes['M'][next(i for i,e in enumerate(parts['M']) if e['id']==graph['source_referents']['cue'])]
    n=len(graph['rota']);starts={'U':0,'L':0}
    for i,v in enumerate(graph['rota']):starts[v]=(min(i,1) if mode=='STAR_OWNER' else i)*delay
    if end is None:end=(n-1)*delay+math.lcm(*periods.values())
    resets=sorted(set(starts[v] for v in graph['followers'])) if mode=='RESET_PES' else []
    rows=[]
    for voice in graph['assigned']:
        part=graph['assigned'][voice];period=periods[part]
        limits=[starts[voice]]+([t for t in resets if starts[voice]<t<end] if voice in graph['pes'] else [])+[end]
        for epoch,(a,b) in enumerate(zip(limits,limits[1:])):
            for cycle in range((b-a+period-1)//period):
                for offset,e in zip(prefixes[part],parts[part]):
                    t=a+cycle*period+offset
                    if t>=b:break
                    stop=t+e['ticks'];cut=b<end and stop>b
                    rows.append([voice,e['id'],cycle,t,stop,min(stop,b),epoch,cut])
    return dict(mode=mode,starts=starts,window_end=end,events=sorted(rows,key=lambda r:(r[0],r[3],r[1])))

def independently_check(graph,parts,execution):
    rows=execution['events'];starts=execution['starts'];issues=[]
    for v in graph['startup']:
        if starts[v]!=0:issues.append('C06_INITIAL_ONSET')
    for v,edge in graph['triggers'].items():
        owner_first=next(x[3] for x in rows if x[0]==edge['owner'] and x[1]==edge['cue'])
        if starts[v]!=owner_first:issues.append('C07_C08_C12_OWNER:'+v)
        if starts[v]<owner_first:issues.append('C13_EARLY:'+v)
    for v,part in graph['assigned'].items():
        stream=[x for x in rows if x[0]==v];events=parts[part];count=len(events)
        if any(x[1]!=events[i%count]['id'] or x[2]!=i//count or x[6] or x[7] for i,x in enumerate(stream)):
            issues.append('PERSISTENT_PART:'+v)
        for x in stream:
            original=next(e for e in events if e['id']==x[1])
            if x[4]-x[3]!=original['ticks']:issues.append('DURATION:'+v)
        if any(b[3]!=a[4] for a,b in zip(stream,stream[1:])):issues.append('CONTINUITY:'+v)
        if part=='M' and any(e['ticks']!=6 for e in events if e['kind']=='rest'):issues.append('C10_LONGA:'+v)
    if parts['P1'][-1]['kind']!='rest':issues.append('C05_UPPER_END')
    if parts['P2'][-1]['kind']=='rest' or not any(e['kind']=='rest' for e in parts['P2'][1:-1]):issues.append('C05_C09_LOWER_INTERNAL')
    # Primary stops at the first persistence defect, so don't multiply secondary
    # continuity errors already certified by a reset event/epoch.
    issues=[x for x in issues if not (x.startswith('CONTINUITY:') and 'PERSISTENT_PART:'+x.split(':')[1] in issues)]
    return sorted(set(issues))
