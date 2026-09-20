import csv,datetime,hashlib,itertools,json,subprocess
from pathlib import Path
from model import parse_all,compile_reading,execute,variants,unsafe_states
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def write(name,x):(A/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    lock=read(E/'PREREG_LOCK.json')
    for n,h in lock['files'].items():assert sha(R/n)==h,n
    receipt=read(A/'PUBLIC_REGISTRATION.json');assert receipt['commit']
    assert subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],cwd=R).returncode==0
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();spec=read(E/'src/SPEC.json');draft=read(R/spec['source_draft'])
    lex={x['raw']:x['symbol'] for x in draft['lexicon']};packet=read(A/'SOURCE_PACKET.json');reader_results={};parses_by_reader={}
    for edition,source in packet['readers'].items():
        raw=[g for row in source['rows'] for g in row['groups']];unknown=[dict(source_group_id=g['source_group_id'],raw=g['ivtff_group_raw']) for g in raw if g['ivtff_group_raw'] not in lex]
        symbols=[lex.get(g['ivtff_group_raw'],'UNKNOWN:'+g['ivtff_group_raw']) for g in raw]
        parses=parse_all(symbols,spec) if source['whole_paragraph_contract'] else []
        status='PARSED_CONDITIONALLY' if parses else ('NO_COMPLETE_PARAGRAPH_CONTRACT' if not source['whole_paragraph_contract'] else 'FROZEN_READING_NO_FULL_COVERAGE')
        reader_results[edition]=dict(status=status,groups=len(raw),unknown_groups=unknown,parse_count=len(parses),strict_anchor_eligible=source['strict_anchor_eligible'],uncertain_groups=source['uncertain_groups'])
        parses_by_reader[edition]=parses
    primary=parses_by_reader['ZL3b'];cases=[]
    for pi,parsed in enumerate(primary):
        for i,v in enumerate(variants(spec)):
            case=dict(id=f'ZL-P{pi:02d}-V{i:02d}',variant=v,parse=parsed)
            try:
                program=compile_reading(parsed,v);case['program']=program;case['paths']=execute(program,v)
                case['status']='CONDITIONAL_CONSISTENT' if any(p['consistent'] for p in case['paths']) else 'CONTRADICTED_FIXED_VARIANT'
            except ValueError as ex:case.update(status='BINDING_CONTRADICTION',error=str(ex),paths=[])
            cases.append(case)
    # Full consequence equivalence within the finite tested scope. Keep parameter
    # values separate; agreement here never proves general semantic equivalence.
    groups={}
    for c in cases:
        key=json.dumps(dict(status=c['status'],hazards=c.get('program',{}).get('hazards'),references=c.get('program',{}).get('references'),paths=c['paths']),sort_keys=True)
        groups.setdefault(key,[]).append(c['id'])
    baseline=next((c for c in cases if c['id']=='ZL-P00-V00'),None);diagnostics=dict(hazard_graphs=[],animal_permutations=[])
    if baseline and baseline.get('paths'):
        trace=baseline['paths'][0]['trace'];edges=[('W','G'),('G','C'),('W','C')]
        for bits in itertools.product((0,1),repeat=3):
            graph=[list(e) for bit,e in zip(bits,edges) if bit];bad=unsafe_states(trace,graph)
            diagnostics['hazard_graphs'].append(dict(bits=list(bits),hazards=graph,violations=bad,consistent_with_trace=not bad,scope='ASSUMPTION_DIAGNOSTIC_NOT_FULL_READING'))
        for names in itertools.permutations(('wolf','goat','cabbage')):
            mapping=dict(zip(('W','G','C'),names));inverse={v:k for k,v in mapping.items()};hazards=[[inverse['wolf'],inverse['goat']],[inverse['goat'],inverse['cabbage']]];bad=unsafe_states(trace,hazards)
            diagnostics['animal_permutations'].append(dict(mapping=mapping,violations=bad,consistent_with_trace=not bad,scope='SOURCE_NAME_DIAGNOSTIC_NOT_LEXICAL_CONFIRMATION'))
    predicted=[(x['locus'],x['group'],x['clause']) for x in draft['all_63_positions']]
    raw=[g for row in packet['readers']['ZL3b']['rows'] for g in row['groups']]
    observed=[(g['source_group_id'].split('|')[1],int(g['source_group_index']),f'S{i+1:02d}') for i,c in enumerate(primary[0] if primary else []) for g in raw[c['start']:c['end']]]
    result=dict(status='COMPLETE_FINITE_CONDITIONAL_AUDIT',started_utc=started,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reader_results=reader_results,case_count=len(cases),consistent_cases=sum(c['status']=='CONDITIONAL_CONSISTENT' for c in cases),without_safety_consistent_cases=sum(any(p['without_safety_consistent'] for p in c['paths']) for c in cases),equivalence_classes=list(groups.values()),predicted_clause_positions_match=predicted==observed,claims=spec['claims'],publication_commit=receipt['commit'])
    write('PARSES.json',parses_by_reader);write('CASES.json',cases);write('DIAGNOSTICS.json',diagnostics);write('RESULT.json',result)
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        fields=['id',*spec['variants'],'status','paths','physical_complete_paths','safe_consistent_paths','without_safety_consistent_paths','hazards','first_physical_failure','safety_violations']
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
        for c in cases:
            ps=c['paths'];w.writerow(dict(id=c['id'],**c['variant'],status=c['status'],paths=len(ps),physical_complete_paths=sum(p['physical_complete'] for p in ps),safe_consistent_paths=sum(p['consistent'] for p in ps),without_safety_consistent_paths=sum(p['without_safety_consistent'] for p in ps),hazards=json.dumps(c.get('program',{}).get('hazards')),first_physical_failure=json.dumps([p['physical_failure'] for p in ps]),safety_violations=json.dumps([p['safety_violations'] for p in ps])))
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
