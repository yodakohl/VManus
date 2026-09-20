"""Finite whole-reading audit. No word learning or manuscript normalization."""
import copy,itertools

CARGO=('W','G','C')

def parse_all(symbols,spec):
    memo={len(symbols):[[]]}
    def rec(i):
        if i in memo:return memo[i]
        out=[]
        for kind,pat in spec['patterns'].items():
            chunk=symbols[i:i+len(pat)]
            if len(chunk)!=len(pat):continue
            if all(s in spec['types'][p[1:]] if p.startswith('@') else s==p for s,p in zip(chunk,pat)):
                out.extend([[dict(kind=kind,start=i,end=i+len(pat),symbols=chunk)]+tail for tail in rec(i+len(pat))])
        memo[i]=out;return out
    return rec(0)

def compile_reading(parsed,variant):
    kinds=[c['kind'] for c in parsed]
    for required in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'):
        if kinds.count(required)!=1:raise ValueError('MISSING_OR_DUPLICATE_'+required)
    if kinds[0]!='INITIAL' or kinds[-1]!='CONCLUSION':raise ValueError('BAD_PARAGRAPH_SCOPE')
    introduced=[];last_pair=None;hazards=[];nodes=[];references=[]
    cargo=set(s for c in parsed for s in c['symbols'] if s in CARGO)
    def ref(s,cid):
        if s in CARGO:return s
        if s=='FIRST_CARGO':
            if not introduced:raise ValueError('NO_PRIOR_CARGO')
            v=introduced[0 if variant['first']=='FIRST' else -1]
        elif s=='OTHER_CARGO':
            if variant['other']=='FIRST':
                if not introduced:raise ValueError('NO_PRIOR_CARGO')
                v=introduced[0]
            else:
                if last_pair is None:raise ValueError('NO_PAIR_FOR_OTHER')
                rest=set(introduced)-set(last_pair)
                if len(rest)!=1:raise ValueError('NONUNIQUE_OTHER')
                v=next(iter(rest))
        else:raise ValueError('NOT_CARGO_REFERENCE:'+s)
        references.append(dict(clause=cid,symbol=s,value=v,prior_cargo=list(introduced)))
        return v
    for i,c in enumerate(parsed):
        cid=f'S{i+1:02d}';s=c['symbols'];k=c['kind'];n=dict(clause=cid,kind=k,start=c['start'],end=c['end'])
        # Explicit names are introduced in source order; no reference production
        # in this finite fragment places a later explicit name before its reference.
        for name in s:
            if name in CARGO and name not in introduced:introduced.append(name)
        if k=='WITH_OUT':n.update(op='TRIP',mode='OUT',load=ref(s[3],cid),instrument=s[1])
        elif k=='EXCLUDE':n.update(op='TRIP',mode=variant['exclude'],load=ref(s[1],cid))
        elif k=='FERRY':n.update(op='TRIP',mode='OPPOSITE',load=ref(s[1],cid))
        elif k=='WITH_RETURN':n.update(op='TRIP',mode='RETURN',load=ref(s[1],cid))
        elif k=='CONVEY':n.update(op='TRIP',mode='OUT',load=ref(s[2],cid))
        elif k=='ALONE':n.update(op='TRIP',mode='RETURN',load=None)
        elif k=='FINAL_TRIP':n.update(op='TRIP',mode='OUT',load=ref(s[4],cid),final=True)
        elif k=='PAIR':
            last_pair=(ref(s[0],cid),ref(s[3],cid));n['pair']=list(last_pair)
            if len(set(last_pair))!=2:raise ValueError('PAIR_ARGUMENTS_IDENTICAL')
            hazards.append(tuple(sorted(last_pair)))
        elif k=='COPY':
            if last_pair is None:raise ValueError('NO_PAIR_TO_COPY')
            r=ref('OTHER_CARGO',cid);pair=list(last_pair);pair[0 if variant['copy']=='FIRST' else 1]=r
            if len(set(pair))!=2:raise ValueError('COPIED_PAIR_ARGUMENTS_IDENTICAL')
            n['pair']=pair;hazards.append(tuple(sorted(pair)))
        elif k=='RESULT':n['explicit_cargo']=ref(s[3],cid)
        nodes.append(n)
    return dict(nodes=nodes,hazards=[list(x) for x in sorted(set(hazards))],references=references,cargo=sorted(cargo))

def unsafe_states(trace,hazards):
    return [dict(after=t['clause'],pair=list(pair),bank=t['positions'][pair[0]])
            for t in trace for pair in hazards
            if t['positions'][pair[0]]==t['positions'][pair[1]]!=t['positions']['M']]

def execute(program,variant):
    # The one vehicle's initial co-location is the draft's explicit first-trip
    # presupposition. It is not a discovered manuscript statement.
    initial={k:'L' for k in ('M','B',*program['cargo'])}
    paths=[dict(positions=initial,trace=[dict(clause='INITIAL',load=None,positions=copy.deepcopy(initial))],physical_failure=None,assertions=[],last_load=None,stay=None,final_seen=False)]
    for node in program['nodes']:
        new=[]
        for old in paths:
            if old['physical_failure'] is not None:new.append(old);continue
            st=old['positions'];k=node['kind'];cid=node['clause']
            if node.get('op')=='TRIP':
                dst=('R' if st['M']=='L' else 'L') if node['mode']=='OPPOSITE' else ('R' if node['mode']=='OUT' else 'L')
                choices=([None]+[x for x in program['cargo'] if st[x]==st['M'] and x!=node['load']]) if node['mode']=='EXCLUDING' else [node['load']]
                for load in choices:
                    p=copy.deepcopy(old);s=p['positions'];reasons=[]
                    if p['final_seen']:reasons.append('TRIP_AFTER_FINALLY')
                    if s['B']!=s['M']:reasons.append('BOAT_NOT_AT_AGENT')
                    if load is not None and s[load]!=s['M']:reasons.append('CARGO_NOT_AT_AGENT')
                    if dst==s['M']:reasons.append('NO_INTERBANK_CROSSING')
                    if reasons:
                        p['physical_failure']=dict(clause=cid,attempted_load=load,destination=dst,reasons=reasons);new.append(p);continue
                    s['M']=s['B']=dst
                    if load is not None:s[load]=dst
                    if p['stay'] is not None:
                        target,bank=p['stay']
                        if load!=target and s[target]!=bank:p['assertions'].append(dict(clause=cid,reason='STAY_VIOLATED'))
                        p['stay']=None
                    p['trace'].append(dict(clause=cid,load=load,positions=copy.deepcopy(s)))
                    p['last_load']=load;p['final_seen']=bool(node.get('final'));new.append(p)
            else:
                p=copy.deepcopy(old);bank='R' if variant['there']=='GOAL' else st['M']
                if k=='STAY':
                    target=p['last_load']
                    if target is None:p['assertions'].append(dict(clause=cid,reason='NO_CARGO_FOR_STAY'))
                    else:
                        if st[target]!=bank:p['assertions'].append(dict(clause=cid,reason='STAY_BANK_FALSE'))
                        p['stay']=(target,bank)
                    p.setdefault('there_references',[]).append(dict(clause=cid,bank=bank))
                elif k=='RESULT':
                    load=p['last_load'];rest=set(program['cargo'])-{load}
                    if load is None or node['explicit_cargo'] not in rest or len({st[x] for x in ('M',*program['cargo'])})!=1:p['assertions'].append(dict(clause=cid,reason='JOINING_RESULT_FALSE'))
                elif k=='CONCLUSION':
                    if any(st[x]!=bank for x in ('M',*program['cargo'])):p['assertions'].append(dict(clause=cid,reason='FINAL_LOCAL_ASSERTION_FALSE'))
                    p.setdefault('there_references',[]).append(dict(clause=cid,bank=bank))
                new.append(p)
        paths=new
    for p in paths:
        p['safety_violations']=unsafe_states(p['trace'],program['hazards'])
        p['physical_complete']=p['physical_failure'] is None
        p['goal_reached']=(all(p['positions'][x]=='R' for x in ('M',*program['cargo'])) if p['physical_complete'] else None)
        p['without_safety_consistent']=p['physical_complete'] and not p['assertions'] and p['goal_reached']
        p['consistent']=p['without_safety_consistent'] and not p['safety_violations']
        p.pop('stay',None);p.pop('last_load',None);p.pop('final_seen',None)
    return paths

def variants(spec):
    keys=list(spec['variants'])
    return [dict(zip(keys,vals)) for vals in itertools.product(*(spec['variants'][k] for k in keys))]
