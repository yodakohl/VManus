#!/usr/bin/env python3
"""Separate source/case/certificate checker; imports no experiment runner/model."""
import collections
import csv
import hashlib
import itertools
import json
from pathlib import Path
import sys

E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
PARENT=R/'experiments/yolo/gdt967_balneis_joint_body_term_incidence/artifacts'


def read(p):return json.loads(p.read_text())


def serial(t,order):
    if not isinstance(t,list):return [t]
    output=[]
    if order=='PREFIX':output.append(t[0])
    for child in t[1:]:output.extend(serial(child,order))
    if order=='POSTFIX':output.append(t[0])
    return output


def lower(counts,d):
    if len(counts)==1:return sum(counts.values())
    if d<2:return None
    q=sorted(counts.values())
    while (len(q)-1)%(d-1):q.insert(0,0)
    cost=0
    while len(q)>1:
        weight=sum(q[:d]);q=sorted(q[d:]+[weight]);cost+=weight
    return cost


def available(piece,words):
    n=0
    for word in words:
        i=0
        while i<=len(word)-len(piece):
            if word[i:i+len(piece)]==piece:n+=1;i+=len(piece)
            else:i+=1
    return n


def certificate(seq,words):
    counts=collections.Counter(seq);N=sum(map(len,words));D=len(set(''.join(words)))
    h=lower(counts,D)
    base={'source_atoms':len(seq),'target_characters':N,'target_groups':len(words),'alphabet_size':D,'prefix_length_lower_bound':h}
    if N<len(seq):return dict(base,status='CONTRADICTED_NONEMPTY_LENGTH')
    if len(words)>len(seq):return dict(base,status='CONTRADICTED_WORD_BOUNDARIES')
    if h is None or h>N:return dict(base,status='CONTRADICTED_PREFIX_LENGTH')
    maximum=max(map(len,words));upper={a:min(maximum,(N-len(seq)+v)//v) for a,v in counts.items()}
    pieces=set()
    for word in words:
        for length in range(1,len(word)+1):
            for start in range(len(word)-length+1):pieces.add(word[start:start+length])
    capacities={p:available(p,words) for p in pieces}
    domains={a:sorted(p for p in pieces if len(p)<=upper[a] and capacities[p]>=v)
             for a,v in sorted(counts.items()) if v>1}
    empty=[a for a,v in domains.items() if not v]
    return dict(base,status='CONTRADICTED_REPEATED_DOMAIN' if empty else 'REQUIRES_FULL_EQUATION',
                code_length_bounds=upper,repeated_domains=domains,empty_domains=empty)


def ground(seq,words,code):
    assert set(code)==set(seq)
    assert all(isinstance(v,str) and v for v in code.values())
    for a,b in itertools.combinations(code,2):
        assert not code[a].startswith(code[b]) and not code[b].startswith(code[a])
    target=''.join(words);offset=0;ends={0};rows=[];word_start=0;wi=0
    for i,atom in enumerate(seq):
        while offset==word_start+len(words[wi]) and wi<len(words)-1:
            word_start+=len(words[wi]);wi+=1
        value=code[atom];assert target[offset:offset+len(value)]==value
        assert offset+len(value)<=word_start+len(words[wi])
        rows.append(dict(atom_index=i,atom=atom,value=value,char_start=offset,char_end=offset+len(value),word_index=wi,word=words[wi]))
        offset+=len(value);ends.add(offset)
    assert offset==len(target)
    k=0
    for word in words:k+=len(word);assert k in ends
    counts=collections.Counter(seq);single=sum(len(code[a]) for a in seq if counts[a]==1)
    return rows,single


def main():
    source=read(E/'src/SOURCE.json');raw=(R/source['source_path']).read_text().splitlines()
    assert hashlib.sha256((R/source['source_path']).read_bytes()).hexdigest()==source['source_sha256']
    assert source['heading_line']==122 and source['heading_exact']==raw[121]
    spans=[[123],[124],[125],[126],[127,128],[129,130],[131],[132],[133,134]]
    assert [c['source_lines'] for c in source['clauses']]==spans
    assert [n for c in source['clauses'] for n in c['source_lines']]==list(range(123,135))
    arities={'BEGIN_RECORD':0}
    def check_tree(t):
        if isinstance(t,str):symbol,arity=t,0
        else:symbol,arity=t[0],len(t)-1
        assert symbol not in arities or arities[symbol]==arity
        arities[symbol]=arity
        if isinstance(t,list):
            for child in t[1:]:check_tree(child)
    for i,c in enumerate(source['clauses']):
        assert c['id']==f'C{i+1}' and c['tree'][0]=='ASSERT'
        assert c['source_exact']==[raw[n-1] for n in c['source_lines']]
        check_tree(c['tree'])
    assert arities==source['arities'] and len(arities)==47
    streams={}
    for order in ('PREFIX','POSTFIX'):
        seq=['BEGIN_RECORD'];align=[dict(index=0,atom='BEGIN_RECORD',clause=None,source_lines=[])]
        for c in source['clauses']:
            for a in serial(c['tree'],order):
                align.append(dict(index=len(seq),atom=a,clause=c['id'],source_lines=c['source_lines']));seq.append(a)
        assert len(seq)==111
        assert source['streams'][order]==dict(atoms=seq,counts=dict(sorted(collections.Counter(seq).items())),alignment=align)
        streams[order]=seq
    # Explicit source ownership obligations, not a truth or Latin-meaning proof.
    assert source['clauses'][3]['tree']==['ASSERT',['ALSO',['RENEW',['WATER_OF','BATH'],['POWERS_OF',['BODY_OF','PERSON']]]]]
    assert ['RENEW','PERSON',['WATER_OF','BATH']] in source['clauses'][8]['tree'][1][1][1]
    assert 'ENDURE' in streams['PREFIX'] and 'HEAT_OF' in streams['PREFIX']
    if '--source-only' in sys.argv:
        print(json.dumps({'status':'PASS','scope':'source/compiler coverage and ownership shapes only','lines':12,'trees':9,'atoms':111,'types':47}));return
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    original=read(R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json')
    target=read(PARENT/'TARGET.json');scope=read(PARENT/'SCOPE.json')
    allowed={f'f{n}{side}' for n in range(75,84) for side in 'rv'}
    for ed,paragraphs in original.items():
        rows=[];literal=[]
        for p in paragraphs:
            if p['page'] not in allowed:continue
            bad=[x['locus'] for x in p['lines'] if not x['anchor_eligible']]
            rows.append(dict(id=p['id'],page=p['page'],leaf=p['leaf'],groups=p['groups'],literal=not bad,ineligible_lines=bad))
            if not bad:literal.append(dict(id=p['id'],page=p['page'],leaf=p['leaf'],words=[w for line in p['lines'] for w in line['words']],loci=[line['locus'] for line in p['lines']],source_ids=[v for line in p['lines'] for v in line['source_ids']]))
        assert target[ed]==sorted(literal,key=lambda p:p['id'])
        assert scope[ed]==dict(complete=len(rows),literal=len(literal),nonliteral=len(rows)-len(literal),rows=rows,independent_confirmation_capacity=0)
    assert read(A/'SCOPE.json')==scope
    cases=read(A/'CASES.json');index={(c['edition'],c['paragraph'],c['writer']):c for c in cases}
    expected=[(ed,p['id'],order) for ed,panel in scope.items() for p in panel['rows'] for order in streams]
    assert len(index)==len(cases)==len(expected) and set(index)==set(expected)
    checked=collections.Counter();sat=0;alternatives=0;solver_unsat=0
    for ed,panel in scope.items():
        eligible={p['id']:p for p in target[ed]}
        for p in panel['rows']:
            for order,seq in streams.items():
                c=index[(ed,p['id'],order)];assert c['page']==p['page'] and c['leaf']==p['leaf']
                assert c['target_groups']==p['groups'] and c['independent_confirmation_capacity']==0
                if not p['literal']:
                    assert c['status']=='UNKNOWN_SOURCE' and c['ineligible_lines']==p['ineligible_lines'];checked[c['status']]+=1;continue
                row=eligible[p['id']]
                for k in ('words','loci','source_ids'):assert c[k]==row[k]
                cert=certificate(seq,c['words'])
                if c['status'].startswith(('ERROR_','UNKNOWN_WALL')):
                    checked[c['status']]+=1;continue
                assert cert==c['necessary']
                if cert['status']!='REQUIRES_FULL_EQUATION':assert c['status']==cert['status']
                else:assert c['status'] in ('SAT','UNSAT_SOLVER','UNKNOWN_SOLVER')
                if c['status']=='UNSAT_SOLVER':solver_unsat+=1
                if c['status']=='SAT':
                    rows,single=ground(seq,c['words'],c['code']);sat+=1
                    assert c['witness']==dict(valid=True,errors=[],alignment=rows,singleton_characters=single,total_characters=sum(map(len,c['words'])),singleton_character_share=single/sum(map(len,c['words'])))
                    assert set(c['projections'])==set(cert['repeated_domains'])
                    for atom,query in c['projections'].items():
                        assert query['status'] in ('SAT','UNSAT_SOLVER','UNKNOWN_SOLVER')
                        if query['status']=='SAT':
                            ground(seq,c['words'],query['alternative_code']);alternatives+=1
                            assert query['alternative_code'][atom]==query['alternative_value']!=c['code'][atom]
                checked[c['status']]+=1
    summary=read(A/'RESULT.json')
    for ed,panel in scope.items():
        for order in streams:
            rows=[c for c in cases if c['edition']==ed and c['writer']==order]
            s=summary['panels'][ed][order]
            assert s['case_status_counts']==dict(collections.Counter(c['status'] for c in rows))
            assert s['complete_paragraphs']==len(rows)
            assert s['full_witnesses']==sum(c['status']=='SAT' for c in rows)
            assert s['computational_unknown_or_errors']==sum(c['status'].startswith(('ERROR','UNKNOWN')) and c['status']!='UNKNOWN_SOURCE' for c in rows)
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(cases)
    for row,c in zip(table,cases):
        assert (row['edition'],row['paragraph'],row['writer'],row['status'])==(c['edition'],str(c['paragraph']),c['writer'],c['status'])
        assert int(row['predicted_source_atoms'])==111 and int(row['target_groups'])==c['target_groups']
    receipt=read(A/'EXECUTION_RECEIPT.json');assert receipt['source_case_count']==len(cases)
    assert receipt['solver_job_count']==sum(c['status']!='UNKNOWN_SOURCE' for c in cases)
    result=dict(status='PASS',scope='Separate same-author source/coverage/necessary-certificate/ground-witness validation; no meaning certification or independent solver UNSAT proof',
                source_lines=12,trees=9,atom_occurrences=111,atom_types=47,cases=len(cases),case_status_counts=dict(checked),
                complete_witnesses_checked=sat,alternative_codes_checked=alternatives,solver_unsat_not_independently_proved=solver_unsat,
                confirmed_words=0,independent_confirmation_capacity=0)
    (A/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
