"""Independent all-optimal-LCS reader sensitivity validator for GDT1035.
No primary imports; --self-test uses synthetic strings only.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import re

EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
PANELS=('ZL_ALL_LITERAL_GROUPS','IT_ALL_LITERAL_GROUPS','UNIQUE_FORCED_COMMON')

class Invalid(Exception): pass

def need(ok,message):
    if not ok: raise Invalid(message)

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def literal(w): return re.fullmatch('[a-z]+',w) is not None

def same(a,b,path='root'):
    need(type(a) is type(b),path+': type differs')
    if isinstance(b,dict):
        need(a.keys()==b.keys(),path+': keys differ')
        for k in b: same(a[k],b[k],path+'.'+str(k))
    elif isinstance(b,list):
        need(len(a)==len(b),path+': length differs')
        for i,(x,y) in enumerate(zip(a,b)): same(x,y,path+f'[{i}]')
    else: need(a==b,path+': value differs '+repr(a)+' != '+repr(b))

def all_optimal(a,b):
    """Return length, possible edges, mandatory edges, mandatory A positions.

    Each optimal skip/match branch represents a set of optimal alignments.
    Unions preserve all possible edges; intersections preserve obligations.
    No choice of one best alignment or per-position deletion computation.
    """
    @lru_cache(None)
    def dp(i,j):
        if i==len(a) or j==len(b):
            return 0,frozenset(),frozenset(),frozenset()
        branches=[dp(i+1,j),dp(i,j+1)]
        if a[i]==b[j]:
            n,u,e,f=dp(i+1,j+1)
            edge=frozenset(((i,j),))
            branches.append((n+1,u|edge,e|edge,f|{i}))
        best=max(v[0] for v in branches)
        optimal=[v for v in branches if v[0]==best]
        union=frozenset().union(*(v[1] for v in optimal))
        edges=optimal[0][2].intersection(*(v[2] for v in optimal[1:]))
        positions=optimal[0][3].intersection(*(v[3] for v in optimal[1:]))
        return best,union,edges,positions
    return dp(0,0)

def alignment_rows(a,b):
    optimum,union,mandatory,forced=all_optimal(tuple(a),tuple(b))
    rows=[]
    for i,word in enumerate(a):
        partners=sorted(j+1 for x,j in union if x==i)
        is_forced=i in forced
        status=('NO_EXACT_ALIGNMENT' if not partners else
                'UNIQUE_FORCED_EXACT' if is_forced and len(partners)==1 else
                'FORCED_MULTIPLE_PARTNERS' if is_forced else 'OPTIONAL_EXACT')
        unique=status=='UNIQUE_FORCED_EXACT'
        need(unique == any(x==i for x,j in mandatory),'edge/position obligation equivalence')
        rows.append(dict(reference_index=i+1,word=word,possible_partners=partners,
                         forced=is_forced,status=status,literal=literal(word),
                         qualifies=literal(word) and unique,optimum=optimum))
    return rows

def exhaustive_alignments(a,b):
    """Small-fixture oracle: enumerate all increasing equal-token edge tuples."""
    def walk(i,j):
        yield ()
        for x in range(i,len(a)):
            for y in range(j,len(b)):
                if a[x]==b[y]:
                    for tail in walk(x+1,y+1): yield ((x,y),)+tail
    alignments=set(walk(0,0));best=max(map(len,alignments))
    optimal=[set(x) for x in alignments if len(x)==best]
    union=set().union(*optimal)
    edges=set.intersection(*optimal)
    mandatory_positions=set.intersection(*({i for i,j in x} for x in optimal))
    return best,frozenset(union),frozenset(edges),frozenset(mandatory_positions)

def inspect_paragraph(p,reader):
    page,leaf=p['page'],p['leaf']
    need(isinstance(page,str) and not page.startswith('f84') and page!='f116v','forbidden selector')
    m=re.fullmatch(r'f([0-9]+)[rv][0-9]*',page)
    need(m and type(leaf) is int and leaf==int(m.group(1)),'page/leaf')
    lines=p['lines']
    need(lines and p['id']==page+'|'+lines[0]['locus']+'-'+lines[-1]['locus'],'paragraph boundary')
    need(len({l['locus'] for l in lines})==len(lines),'duplicate line')
    offset=0;positions=[]
    for l in lines:
        need(l['locus'].startswith(page+'.') and l['offset']==offset,'line scope/offset')
        words,ids=l['words'],l['source_ids']
        need(all(isinstance(w,str) for w in words) and len(words)==len(ids),'word/ID shape')
        need(ids==[f"{reader}|{l['locus']}|G{i+1:03d}" for i in range(len(words))],'exact source IDs')
        for w,sid in zip(words,ids):
            positions.append(dict(word=w,source_id=sid,locus=l['locus'],anchor_eligible=l.get('anchor_eligible')))
        offset+=len(words)
    need(offset==p['groups'],'whole group count')
    return positions

def reconstruct_scope(spec,parent_spec,parent_scope,packet):
    need(set(packet)=={'ZL3b','IT2a','RF1b'},'packet readers')
    index={}
    for reader in ('ZL3b','IT2a'):
        index[reader]={}
        for p in packet[reader]:
            need(p['id'] not in index[reader],'ambiguous paragraph ID')
            index[reader][p['id']]=p
    scope=[];alignments=[]
    counters={panel:{'A':Counter(),'B':Counter()} for panel in PANELS}
    need(len(parent_scope)==len(parent_spec['records'])==4,'four source records')
    for record,oldscope in zip(parent_spec['records'],parent_scope):
        pid=record['paragraph'];family=record['family'];section=record['section']
        need(oldscope['paragraph']==pid and oldscope['family']==family and oldscope['section']==section,'parent scope ownership')
        need(all(pid in index[r] for r in index),'missing exact whole reader paragraph')
        zl,it=index['ZL3b'][pid],index['IT2a'][pid]
        zpositions=inspect_paragraph(zl,'ZL3b');ipositions=inspect_paragraph(it,'IT2a')
        same(zpositions,oldscope['positions'],'complete parent ZL positions')
        need(zl['groups']==record['groups'] and zl['page']==it['page'] and zl['leaf']==it['leaf'],'source record identity')
        need([l['locus'] for l in zl['lines']]==[l['locus'] for l in it['lines']],'exact physical line ownership')
        scope.append(dict(section=section,family=family,paragraph=pid,page=zl['page'],leaf=zl['leaf'],readers={'ZL3b':zl,'IT2a':it}))
        counters[PANELS[0]][family].update(p['word'] for p in zpositions if literal(p['word']))
        counters[PANELS[1]][family].update(p['word'] for p in ipositions if literal(p['word']))
        for zline,iline in zip(zl['lines'],it['lines']):
            for row in alignment_rows(zline['words'],iline['words']):
                i=row['reference_index']-1
                row.update(section=section,family=family,paragraph=pid,locus=zline['locus'],
                           source_id=zline['source_ids'][i],reference_line_eligible=zline.get('anchor_eligible'),
                           alternate_line_eligible=iline.get('anchor_eligible'),
                           partner_source_ids=[iline['source_ids'][j-1] for j in row['possible_partners']])
                alignments.append(row)
                if row['qualifies']: counters[PANELS[2]][family][row['word']]+=1
    need(len(alignments)==183,'complete183 reference rows')
    return scope,alignments,counters

def candidates_and_result(counters,alignments,pools,capacity):
    words=sorted(set().union(*(set(counters[p][f]) for p in PANELS for f in ('A','B'))))
    candidates=[];panels={}
    for panel in PANELS:
        A,B=counters[panel]['A'],counters[panel]['B'];empty=[];required=0;shared=0
        for w in words:
            a,b=A.get(w,0),B.get(w,0);req=min(a,b);required+=req
            options=[p['id'] for p in pools if a<=p['A_capacity'] and b<=p['B_capacity']] if a and b else []
            if a and b:
                shared+=1
                if not options:empty.append(w)
            decision='NOT_SHARED' if not(a and b) else 'NECESSARY_DOMAIN_NONEMPTY' if options else 'EMPTY_NECESSARY_DOMAIN'
            candidates.append(dict(panel=panel,word=w,A=a,B=b,required_pairs=req,possible_pools=options,decision=decision))
        panels[panel]=dict(A_positions=sum(A.values()),B_positions=sum(B.values()),shared_types=shared,
                           required_pairs=required,capacity=capacity,empty_domains=empty,
                           decision='REFUTED_FIXED_SHARED_CODE' if required>capacity or empty else 'NO_DECISION')
    result=dict(experiment='GDT1035',reference_positions=len(alignments),qualifying_positions=sum(r['qualifies'] for r in alignments),
                panels=panels,confirmed_words=0,independent_readers=False,independent_meaning_capacity=0,significance_claim=False)
    return candidates,result

def verify_parent_certificate(artifact):
    A,B,adj=artifact['A'],artifact['B'],artifact['adjacency'];cert=artifact['certificate']
    need(len(A)==95 and len(B)==88 and set(adj)==set(A),'complete parent graph')
    pairs=cert['pairs'];ca,cb=cert['cover_A'],cert['cover_B']
    need(len({a for a,b in pairs})==len({b for a,b in pairs})==len(pairs),'parent matching unique')
    need(all(a in A and b in B and b in adj[a] for a,b in pairs),'parent matching edges')
    need(len(set(ca))==len(ca) and len(set(cb))==len(cb) and set(ca)<=set(A) and set(cb)<=set(B),'parent cover nodes')
    need(all(a in ca or b in cb for a,neighbors in adj.items() for b in neighbors),'parent uncovered edge')
    need(len(ca)+len(cb)==len(pairs)==cert['size']==21,'unchanged parent21 optimum')
    return 21

def self_test():
    strings=[tuple(x) for n in range(4) for x in itertools.product(('a','b'),repeat=n)]
    for a in strings:
        for b in strings: need(all_optimal(a,b)==exhaustive_alignments(a,b),'all-optimal exhaustive oracle')
    row=alignment_rows(['a'],['a','a'])[0]
    need(row['forced'] and row['possible_partners']==[1,2] and row['status']=='FORCED_MULTIPLE_PARTNERS' and not row['qualifies'],'forced multiple')
    need(all(not r['forced'] and r['status']=='OPTIONAL_EXACT' for r in alignment_rows(['a','a'],['a'])),'optional duplicate')
    rows=alignment_rows(['a','[x:y]','b'],['a','[x:y]','b'])
    need([r['qualifies'] for r in rows]==[True,False,True] and rows[1]['optimum']==3,'uncertain participates unchanged')
    need(alignment_rows(['a'],['b'])[0]['status']=='NO_EXACT_ALIGNMENT','no exact edge')
    counters={p:{'A':Counter({'a':3}),'B':Counter({'a':2,'b':1})} for p in PANELS}
    candidates,result=candidates_and_result(counters,rows,[dict(id='v',A_capacity=2,B_capacity=2)],21)
    need(all(r['empty_domains']==['a'] and r['decision']=='REFUTED_FIXED_SHARED_CODE' for r in result['panels'].values()),'domain rejection')
    need(len(candidates)==6 and all(r['possible_pools']==[] for r in candidates if r['word']=='b'),'full common panel union')
    class Poison(dict):
        def __getitem__(self,k):
            if k=='lines':raise AssertionError('selector payload')
            return super().__getitem__(k)
    for page,leaf in [('f84r',84),('f84v',84),('f116v',116),('f1r',2)]:
        try:inspect_paragraph(Poison(page=page,leaf=leaf),'ZL3b')
        except Invalid:pass
        else:raise Invalid('poison selector accepted')
    return dict(status='PASS',all_optimal_oracle_pairs=len(strings)**2,forced_multiple=True,optional_duplicates=True,
                uncertain_raw_alignment=True,complete_panel_union=True,domain_decision=True,selector_poison=True)

def execute(spec):
    lock=read(EXP/'PREREG_LOCK.json');files=lock['files']
    essentials={str(EXP.relative_to(ROOT)/p) for p in ('METHOD.md','PREREGISTRATION.md','src/SPEC.json','src/run.py','src/validate.py')}
    need(essentials|set(spec['inputs'])<=set(files),'missing lock entries')
    for path,h in files.items():need(sha(ROOT/path)==h,'lock hash '+path)
    for path,h in spec['inputs'].items():need(sha(ROOT/path)==h,'input hash '+path)
    parent=ROOT/spec['parent']
    need(str((parent/'artifacts/SCOPE.json').relative_to(ROOT)) in spec['inputs'],'parent SCOPE must be bound')
    parent_lock=read(parent/'PREREG_LOCK.json')
    for path,h in parent_lock['files'].items():need(sha(ROOT/path)==h,'parent lock '+path)
    capacity=verify_parent_certificate(read(parent/'artifacts/CERTIFICATE.json'))
    pools=read(parent/'artifacts/WORD_DOMAINS.json')['pool_capacities']
    need(len(pools)==46 and len({p['id'] for p in pools})==46,'unchanged46 pool capacities')
    for p in pools:
        need(len(set(p['A_nodes']))==len(p['A_nodes'])==p['A_capacity'] and len(set(p['B_nodes']))==len(p['B_nodes'])==p['B_capacity'],'pool node capacities')
    scope,alignments,counters=reconstruct_scope(spec,read(parent/'src/SPEC.json'),read(parent/'artifacts/SCOPE.json'),read(ROOT/spec['packet']))
    candidates,result=candidates_and_result(counters,alignments,pools,capacity)
    for name,value in [('SCOPE.json',scope),('ALIGNMENTS.json',alignments),('CANDIDATES.json',candidates),('RESULT.json',result)]:
        same(read(EXP/'artifacts'/name),value,name)
    with (EXP/'artifacts/CANDIDATES.csv').open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f);csv_rows=list(reader)
        need(reader.fieldnames==list(candidates[0]),'CSV header')
    expected=[{k:'|'.join(v) if k=='possible_pools' else str(v) for k,v in r.items()} for r in candidates]
    same(csv_rows,expected,'CANDIDATES.csv')
    return dict(experiment='GDT1035',status='PASS',independent_implementation=True,primary_read_or_imported=False,
                lcs_method='memoized suffix DP; unions and intersections of all optimal branches; separate mandatory-reference-index intersection',
                input_hashes_verified=len(spec['inputs']),lock_files_verified=len(files),parent_lock_files_verified=len(parent_lock['files']),
                validator_sha256=sha(Path(__file__)),reference_positions=len(alignments),reconstructed_result=result,
                artifacts_compared=['SCOPE.json','ALIGNMENTS.json','CANDIDATES.json','CANDIDATES.csv','RESULT.json'],synthetic=self_test())

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--self-test',action='store_true');parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if not args.execute:
        print(json.dumps(self_test(),indent=2));return 0
    try:
        spec=read(EXP/'src/SPEC.json')
        need(tuple(spec['panels'])==PANELS and spec['reference']=='ZL3b' and spec['alternate']=='IT2a','fixed panels/readers')
        result=execute(spec)
    except Exception as e:
        result=dict(experiment='GDT1035',status='FAIL',error_type=type(e).__name__,error=str(e),primary_read_or_imported=False)
        (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False,indent=2));return 1
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
