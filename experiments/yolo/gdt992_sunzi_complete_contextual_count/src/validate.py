#!/usr/bin/env python3
"""Independent source/input reconstruction and separate reverse finite check."""
import collections,csv,itertools,json,sys,time
from pathlib import Path
from shared import A,E,R,TARGET,OLD,module,read,put,utc,verify_lock,work,journal

def ground(atoms,words,code):
    assert set(code)==set(atoms) and all(isinstance(v,str) and v for v in code.values())
    for a,b in itertools.combinations(code.values(),2):assert not a.startswith(b) and not b.startswith(a)
    chars=''.join(words);offset=0;atom_ends=set();alignment=[];word_ends=[];n=0
    for w in words:n+=len(w);word_ends.append(n)
    wi=0
    for ai,a in enumerate(atoms):
        value=code[a];assert chars[offset:offset+len(value)]==value
        while offset>=word_ends[wi]:wi+=1
        assert offset+len(value)<=word_ends[wi]
        alignment.append(dict(atom_index=ai,atom=a,word_index=wi,value=value,start=offset,end=offset+len(value)))
        offset+=len(value);atom_ends.add(offset)
    assert offset==len(chars) and set(word_ends)<=atom_ends
    return alignment

def main():
    rev=module('frozen987reverse',OLD/'validate.py')
    if '--worker' in sys.argv:
        j=json.load(sys.stdin);print(json.dumps(rev.replay((j['atoms'],j['words'])),separators=(',',':')));return
    verify_lock();source=read(E/'src/SOURCE.json');streams={}
    for writer in ['PREFIX','POSTFIX']:
        stream=[]
        for c in source['clauses']:stream.extend(rev.serial(c['tree'],writer))
        assert stream==source['streams'][writer]['atoms'] and len(stream)==122 and len(set(stream))==27
        streams[writer]=stream
    cases=read(A/'PRIMARY_CASES.json.gz');receipt=read(A/'EXECUTION_RECEIPT.json');prim=journal('PRIMARY_JOURNAL.jsonl')
    rows=[]
    for edition,panel in read(R/TARGET).items():
        for p in panel:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            for writer in ['PREFIX','POSTFIX']:rows.append((edition,p,writer))
    assert len(cases)==len(rows)==2698
    jobs=[];alignments=[]
    for i,(c,(edition,p,writer)) in enumerate(zip(cases,rows),1):
        assert c['case']==i
        for key,val in dict(edition=edition,paragraph=p['id'],page=p['page'],leaf=p['leaf'],writer=writer,target_groups=p['groups'],source_atoms=122,source_types=27,independent_meaning_confirmation_capacity=0).items():assert c[key]==val,(i,key)
        bad=[line['locus'] for line in p['lines'] if not line['anchor_eligible']]
        if bad:
            assert c['status']=='UNKNOWN_SOURCE' and c['ineligible_lines']==bad;continue
        words=[word for line in p['lines'] for word in line['words']]
        assert c['words']==words and c['loci']==[line['locus'] for line in p['lines']]
        assert c['source_ids']==[line['source_ids'] for line in p['lines']]
        assert c['primary']==prim.get(i,dict(status='UNKNOWN_UNRETAINED'))
        assert c['status']==c['primary']['status']
        if c['status']=='SAT':
            alignment=ground(streams[writer],words,c['primary']['code'])
            alignments.append(dict(case=i,writer=writer,edition=edition,paragraph=p['id'],code=c['primary']['code'],words=words,alignment=alignment))
        elif c['status']=='UNSAT_FINITE':jobs.append((i,dict(atoms=streams[writer],words=words)))
        else:assert c['status'].startswith(('UNKNOWN_','ERROR_'))
    if '--assemble' not in sys.argv:work(Path(__file__).resolve(),jobs,receipt['deadline_unix'],8,'REVERSE_JOURNAL.jsonl')
    reverse=journal('REVERSE_JOURNAL.jsonl');assert set(reverse).issubset({i for i,j in jobs})
    conflicts=[]
    for c in cases:
        if c['status']=='UNSAT_FINITE':
            r=reverse.get(c['case'],dict(status='UNKNOWN_UNRETAINED'));c['reverse']=r
            if r['status']=='UNSAT_REPLAY':c['status']='CONTRADICTED_COMPLETE_EQUATION'
            elif r['status']=='SAT_REPLAY':c['status']='INVALID_PRIMARY_REVERSE_CONFLICT';conflicts.append(c['case'])
            else:
                assert r['status'].startswith(('UNKNOWN_','ERROR_'));c['status']='PRIMARY_EXHAUSTION_UNCORROBORATED'
        elif c['status']=='SAT':c['status']='CONDITIONAL_COMPLETE_CODE'
    counts=collections.Counter(c['status'] for c in cases)
    unresolved=sum(n for k,n in counts.items() if k.startswith(('UNKNOWN_','ERROR_')) and k!='UNKNOWN_SOURCE')+counts['PRIMARY_EXHAUSTION_UNCORROBORATED']
    result=dict(experiment='GDT992',cases=2698,status_counts=dict(counts),conditional_complete_codes=counts['CONDITIONAL_COMPLETE_CODE'],
        corroborated_complete_contradictions=counts['CONTRADICTED_COMPLETE_EQUATION'],computationally_unresolved=unresolved,
        source_unknown=counts['UNKNOWN_SOURCE'],decision='INVALID_CONFLICT' if conflicts else 'RETAIN_CONDITIONAL_CODES' if alignments else 'NO_WITNESS_COMPUTATION_INCOMPLETE' if unresolved else 'NO_LITERAL_COMPLETE_READING',
        independent_meaning_confirmation_capacity=0,confirmed_translated_words=0,significance_claim=False,code_uniqueness_claim=False,
        by_writer={w:dict(collections.Counter(c['status'] for c in cases if c['writer']==w)) for w in streams})
    validation=dict(status='FAIL' if conflicts else 'PASS',cases=2698,full_codes_checked=len(alignments),
        primary_exhaustions=len(jobs),reverse_retained=len(reverse),corroborated_exhaustions=counts['CONTRADICTED_COMPLETE_EQUATION'],
        uncorroborated_exhaustions=counts['PRIMARY_EXHAUSTION_UNCORROBORATED'],conflicts=conflicts,
        scope='source/input/ground-code checks and separately implemented reverse enumeration; same author, no meaning test')
    put('CASES.json.gz',cases);put('COMPLETE_ALIGNMENTS.json.gz',alignments);put('RESULT.json',result);put('VALIDATION.json',validation)
    columns=['case','edition','paragraph','leaf','writer','source_atoms','source_types','target_groups','status','independent_meaning_confirmation_capacity']
    with (A/'CANDIDATES.tsv').open('w') as h:
        out=csv.DictWriter(h,columns,delimiter='\t',lineterminator='\n',extrasaction='ignore');out.writeheader();out.writerows(cases)
    lines=['# Every complete conditional source alignment','','All lexical meanings and writing rules remain hypotheses. No code-uniqueness claim.']
    for a in alignments:
        lines+=['',f"## Case {a['case']} / {a['edition']} / {a['paragraph']} / {a['writer']}",'','| Word | Source primitives |','|---|---|']
        for wi,word in enumerate(a['words']):lines.append('| '+word+' | '+' + '.join(x['atom'] for x in a['alignment'] if x['word_index']==wi)+' |')
        lines+=['','Complete source content:']+['- '+c['id']+': '+c['meaning'] for c in source['clauses']]
        lines+=['','All code values are retained in COMPLETE_ALIGNMENTS.json.gz. Alternative keys and semantic renamings are not exhausted.']
    if not alignments:lines+=['','No complete code witness. Every contradiction and unknown remains in CANDIDATES.tsv.']
    (A/'COMPLETE_READINGS.md').write_text('\n'.join(lines)+'\n')
    receipt.update(validation_completed_utc=utc(),validation_elapsed_since_start_seconds=time.time()-receipt['started_unix']);put('EXECUTION_RECEIPT.json',receipt)
    print(json.dumps(result,indent=2));print(json.dumps(validation,indent=2))
    if conflicts:raise SystemExit(1)
if __name__=='__main__':main()
