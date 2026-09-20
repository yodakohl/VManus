"""Independent backwards regex parsing and bit-position replay; no runner import."""
import csv,datetime,itertools,json,re,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def regex_parses(words,spec):
    text=' '.join(words);offsets=[0]
    for w in words:offsets.append(offsets[-1]+len(w)+1)
    regexes=[]
    for k,pattern in spec['patterns'].items():
        bits=['(?:'+'|'.join(map(re.escape,spec['types'][p[1:]]))+')' if p.startswith('@') else re.escape(p) for p in pattern]
        regexes.append((k,re.compile(' '.join(bits)+r'(?= |$)')))
    suffix={len(words):[[]]}
    for i in range(len(words)-1,-1,-1):
        suffix[i]=[]
        for k,r in regexes:
            m=r.match(text,offsets[i])
            if m is None:continue
            j=i+len(m.group().split())
            suffix[i].extend([dict(kind=k,start=i,end=j,symbols=words[i:j])]+s for s in suffix[j])
    return suffix[0]

def replay(parsed,v):
    names=('M','B','C','G','W');bits={n:1<<i for i,n in enumerate(names)}
    symbols=[s for c in parsed for s in c['symbols']]
    first_positions={n:symbols.index(n) for n in ('W','G','C') if n in symbols}
    cargo=set(first_positions);events=[];hazards=set();references=[];pair=None
    def cargo_ref(word,start,cid):
        if word in cargo:return word
        prior=sorted((x for x in cargo if first_positions[x]<start),key=first_positions.get)
        if word=='FIRST_CARGO':answer=prior[0] if v['first']=='FIRST' else prior[-1]
        elif word=='OTHER_CARGO':
            if v['other']=='FIRST':answer=prior[0]
            else:
                rest=set(prior)-set(pair);assert len(rest)==1;answer=next(iter(rest))
        else:raise AssertionError(word)
        references.append(dict(clause=cid,symbol=word,value=answer,prior_cargo=prior));return answer
    for n,c in enumerate(parsed,1):
        s=c['symbols'];k=c['kind'];i=c['start'];cid=f'S{n:02d}';r=lambda word:cargo_ref(word,i,cid)
        event=[cid,k,None,None]
        if k=='PAIR':pair=(r(s[0]),r(s[3]));hazards.add(tuple(sorted(pair)))
        elif k=='COPY':
            other=r('OTHER_CARGO');new=(other,pair[1]) if v['copy']=='FIRST' else (pair[0],other);hazards.add(tuple(sorted(new)))
        elif k=='WITH_OUT':event[2:]=['OUT',r(s[3])]
        elif k=='EXCLUDE':event[2:]=[v['exclude'],r(s[1])]
        elif k=='FERRY':event[2:]=['OPPOSITE',r(s[1])]
        elif k=='WITH_RETURN':event[2:]=['RETURN',r(s[1])]
        elif k=='CONVEY':event[2:]=['OUT',r(s[2])]
        elif k=='ALONE':event[2:]=['RETURN',None]
        elif k=='FINAL_TRIP':event[2:]=['OUT',r(s[4])]
        elif k=='RESULT':event[3]=r(s[3])
        events.append(event)
    def bank(state,n):return bool(state&bits[n])
    def positions(state):return {n:('R' if bank(state,n) else 'L') for n in names}
    # Paths carry independent compact state, not mutable position dictionaries.
    paths=[(0,[dict(clause='INITIAL',load=None,positions=positions(0))],None,[],None,None,False,[])]
    for cid,k,mode,arg in events:
        future=[]
        for state,trace,failure,assertions,last,stay,finished,theres in paths:
            if failure is not None:future.append((state,trace,failure,assertions,last,stay,finished,theres));continue
            if mode is not None:
                target=not bank(state,'M') if mode=='OPPOSITE' else mode=='OUT'
                loads=[None]+sorted(x for x in cargo if bank(state,x)==bank(state,'M') and x!=arg) if mode=='EXCLUDING' else [arg]
                for load in loads:
                    errors=[]
                    if finished:errors.append('TRIP_AFTER_FINALLY')
                    if bank(state,'B')!=bank(state,'M'):errors.append('BOAT_NOT_AT_AGENT')
                    if load is not None and bank(state,load)!=bank(state,'M'):errors.append('CARGO_NOT_AT_AGENT')
                    if target==bank(state,'M'):errors.append('NO_INTERBANK_CROSSING')
                    if errors:
                        failure=dict(clause=cid,attempted_load=load,destination='R' if target else 'L',reasons=errors)
                        future.append((state,trace,failure,list(assertions),last,stay,finished,list(theres)));continue
                    toggle=bits['M']|bits['B']|(bits[load] if load else 0);after=state^toggle;checks=list(assertions)
                    if stay is not None and load!=stay[0] and bank(after,stay[0])!=stay[1]:checks.append(dict(clause=cid,reason='STAY_VIOLATED'))
                    future.append((after,trace+[dict(clause=cid,load=load,positions=positions(after))],None,checks,load,None,k=='FINAL_TRIP',list(theres)))
            else:
                checks=list(assertions);there=True if v['there']=='GOAL' else bank(state,'M');locs=list(theres)
                if k=='STAY':
                    if last is None:checks.append(dict(clause=cid,reason='NO_CARGO_FOR_STAY'))
                    else:
                        if bank(state,last)!=there:checks.append(dict(clause=cid,reason='STAY_BANK_FALSE'))
                        stay=(last,there)
                    locs.append(dict(clause=cid,bank='R' if there else 'L'))
                elif k=='RESULT':
                    if last is None or arg not in cargo-{last} or any(bank(state,x)!=bank(state,'M') for x in cargo):checks.append(dict(clause=cid,reason='JOINING_RESULT_FALSE'))
                elif k=='CONCLUSION':
                    if any(bank(state,x)!=there for x in (*cargo,'M')):checks.append(dict(clause=cid,reason='FINAL_LOCAL_ASSERTION_FALSE'))
                    locs.append(dict(clause=cid,bank='R' if there else 'L'))
                future.append((state,trace,None,checks,last,stay,finished,locs))
        paths=future
    output=[]
    for state,trace,failure,assertions,last,stay,finished,theres in paths:
        bad=[dict(after=t['clause'],pair=list(pair),bank=t['positions'][pair[0]]) for t in trace for pair in sorted(hazards) if t['positions'][pair[0]]==t['positions'][pair[1]]!=t['positions']['M']]
        goal=all(bank(state,x) for x in (*cargo,'M')) if failure is None else None
        unsafeless=failure is None and not assertions and goal
        p=dict(positions=positions(state),trace=trace,physical_failure=failure,assertions=assertions,safety_violations=bad,physical_complete=failure is None,goal_reached=goal,without_safety_consistent=unsafeless,consistent=unsafeless and not bad)
        if theres:p['there_references']=theres
        output.append(p)
    return output,[list(p) for p in sorted(hazards)],references

def main():
    for path,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
    spec=read(E/'src/SPEC.json');draft=read(R/spec['source_draft']);packet=read(A/'SOURCE_PACKET.json');actual=read(A/'CASES.json');result=read(A/'RESULT.json');stored_parses=read(A/'PARSES.json');lex={x['raw']:x['symbol'] for x in draft['lexicon']}
    paragraph_cache=read(R/spec['paragraph_cache'])
    for edition,source in packet['readers'].items():
        cached=read(R/(spec['source_prefix']+edition+'.json'));cols=cached['group_columns'];original=[x for x in cached['lines'] if x['metadata']['locus'] in {f'f83r.{n}' for n in spec['line_numbers']}]
        assert len(original)==7
        originals={x['metadata']['locus']:[dict(zip(cols,g)) for g in x['groups']] for x in original}
        for line in source['rows']:assert originals[line['metadata']['locus']]==line['groups']
        owned=[p for p in paragraph_cache[edition] if p['id']=='f83r|f83r.18-f83r.24']
        assert source['paragraph_metadata']==owned
        assert source['whole_paragraph_contract']==(len(owned)==1)
        assert source['strict_anchor_eligible']==(bool(owned) and all(l['anchor_eligible'] for l in owned[0]['lines']))
        raw=[g for line in source['rows'] for g in line['groups']]
        uncertain=[g['source_group_id'] for g in raw if g['left_separator'] not in ('LINE_START','DEFINITE_SPACE') or g['right_separator'] not in ('LINE_END','DEFINITE_SPACE')]
        assert source['uncertain_groups']==uncertain
        rr=result['reader_results'][edition]
        assert rr['groups']==len(raw) and rr['uncertain_groups']==uncertain and rr['strict_anchor_eligible']==source['strict_anchor_eligible']
        assert rr['unknown_groups']==[dict(source_group_id=g['source_group_id'],raw=g['ivtff_group_raw']) for g in raw if g['ivtff_group_raw'] not in lex]
        words=[lex.get(g['ivtff_group_raw'],'UNKNOWN:'+g['ivtff_group_raw']) for l in source['rows'] for g in l['groups']]
        ps=regex_parses(words,spec) if source['whole_paragraph_contract'] else []
        assert ps==stored_parses[edition],edition
        assert rr['parse_count']==len(ps)
        assert rr['status']==('PARSED_CONDITIONALLY' if ps else ('NO_COMPLETE_PARAGRAPH_CONTRACT' if not owned else 'FROZEN_READING_NO_FULL_COVERAGE'))
    vs=[dict(zip(spec['variants'],v)) for v in itertools.product(*spec['variants'].values())]
    expected_ids=[f'ZL-P{pi:02d}-V{vi:02d}' for pi in range(len(stored_parses['ZL3b'])) for vi in range(32)]
    assert [c['id'] for c in actual]==expected_ids
    for c in actual:
        vi=int(c['id'].split('V')[1]);assert c['variant']==vs[vi]
        pi=int(c['id'].split('-P')[1].split('-')[0]);assert c['parse']==stored_parses['ZL3b'][pi]
        paths,hazards,refs=replay(c['parse'],c['variant'])
        assert paths==c['paths'],('paths',c['id'])
        assert hazards==c['program']['hazards'],('hazards',c['id'])
        assert refs==c['program']['references'],('references',c['id'])
        assert c['status']==('CONDITIONAL_CONSISTENT' if any(p['consistent'] for p in paths) else 'CONTRADICTED_FIXED_VARIANT')
    equivalence={}
    for c in actual:
        key=json.dumps(dict(status=c['status'],hazards=c['program']['hazards'],references=c['program']['references'],paths=c['paths']),sort_keys=True)
        equivalence.setdefault(key,[]).append(c['id'])
    assert result['equivalence_classes']==list(equivalence.values())
    raw=[g for line in packet['readers']['ZL3b']['rows'] for g in line['groups']]
    predicted=[(x['locus'],x['group'],x['clause']) for x in draft['all_63_positions']]
    observed=[(g['source_group_id'].split('|')[1],int(g['source_group_index']),f'S{i+1:02d}') for i,c in enumerate(stored_parses['ZL3b'][0] if stored_parses['ZL3b'] else []) for g in raw[c['start']:c['end']]]
    assert result['predicted_clause_positions_match']==(predicted==observed)
    assert result['claims']==spec['claims']
    with (A/'CANDIDATES.tsv').open() as f: table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(actual)
    for row,c in zip(table,actual):
        assert row['id']==c['id'] and row['status']==c['status']
        for k,value in c['variant'].items(): assert row[k]==value
        assert int(row['paths'])==len(c['paths'])
        for label,key in [('physical_complete_paths','physical_complete'),('safe_consistent_paths','consistent'),('without_safety_consistent_paths','without_safety_consistent')]:assert int(row[label])==sum(p[key] for p in c['paths'])
        assert json.loads(row['hazards'])==c['program']['hazards']
        assert json.loads(row['first_physical_failure'])==[p['physical_failure'] for p in c['paths']]
        assert json.loads(row['safety_violations'])==[p['safety_violations'] for p in c['paths']]
    diagnostic=read(A/'DIAGNOSTICS.json');baseline=actual[0]['paths'][0]['trace'];edges=[['W','G'],['G','C'],['W','C']]
    def safe(graph):return all(t['positions'][a]!=t['positions'][b] or t['positions'][a]==t['positions']['M'] for a,b in graph for t in baseline)
    for bits,row in zip(itertools.product((0,1),repeat=3),diagnostic['hazard_graphs']):assert row['consistent_with_trace']==safe([e for b,e in zip(bits,edges) if b])
    assert len(diagnostic['hazard_graphs'])==8 and len(diagnostic['animal_permutations'])==6
    for row in diagnostic['animal_permutations']:
        inv={v:k for k,v in row['mapping'].items()};assert row['consistent_with_trace']==safe([[inv['wolf'],inv['goat']],[inv['goat'],inv['cabbage']]])
    assert result['case_count']==len(actual)
    assert result['consistent_cases']==sum(any(p['consistent'] for p in c['paths']) for c in actual)
    assert result['without_safety_consistent_cases']==sum(any(p['without_safety_consistent'] for p in c['paths']) for c in actual)
    out=dict(status='PASS',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases_checked=len(actual),reader_parses_checked=3,diagnostics_checked=14,implementation='independent backwards regex parser and bit-position replay; same root author, no independent meaning',confirmed_words=0)
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
