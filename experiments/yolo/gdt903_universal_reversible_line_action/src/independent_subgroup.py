#!/usr/bin/env python3
"""Ordinary difference subgroup, independently folded by full edge passes.

For a right action and fixed reference r, all w send s to one endpoint iff
H=<w r^-1> fixes s. This is NOT normal closure and does not assume endpoint=s.
Positive edges store(u,g,v); negative letters traverse the same edge backwards.
"""
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import time

SOURCE_SHA256='bd8b58523e4e49754f4e49e3901f00ecef748679d90ac46184e453294c8753c2'


def reduce_word(word):
    stack=[]
    for g in word:
        assert isinstance(g,int) and g
        if stack and stack[-1]==-g:stack.pop()
        else:stack.append(g)
    return stack


class UnionFind:
    def __init__(self,n):self.parent=list(range(n))
    def find(self,v):
        while self.parent[v]!=v:
            self.parent[v]=self.parent[self.parent[v]];v=self.parent[v]
        return v
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a==b:return False
        self.parent[max(a,b)]=min(a,b)
        return True


def canonical_core(edges,base,alphabet_size):
    # Remove dangling nonbase trees only. A base stem of a conjugate subgroup
    # remains: deleting it would change H to a conjugate subgroup.
    edges=set(edges);pruned=0
    while True:
        degree=defaultdict(int)
        for u,g,v in edges:degree[u]+=1;degree[v]+=1
        leaves={v for v,d in degree.items() if v!=base and d<=1}
        if not leaves:break
        old=len(edges);edges={e for e in edges if e[0] not in leaves and e[2] not in leaves}
        pruned+=old-len(edges)
    adj=defaultdict(dict)
    for u,g,v in sorted(edges):
        assert 1<=g<=alphabet_size
        assert g not in adj[u] or adj[u][g]==v
        assert -g not in adj[v] or adj[v][-g]==u
        adj[u][g]=v;adj[v][-g]=u
    numbers={base:0};queue=deque([base])
    while queue:
        u=queue.popleft()
        for g in sorted(adj[u]):
            v=adj[u][g]
            if v not in numbers:numbers[v]=len(numbers);queue.append(v)
    assert set(numbers)==({base}|{v for e in edges for v in [e[0],e[2]]})
    ce=sorted([numbers[u],g,numbers[v]] for u,g,v in edges)
    arcs=sorted([numbers[u],g,numbers[v]] for u,links in adj.items() for g,v in links.items())
    n=len(numbers)
    full=(n==1 and {g for u,g,v in ce}==set(range(1,alphabet_size+1)))
    finite=(len(arcs)==2*alphabet_size*n)
    return {'base_vertex':0,'vertex_count':n,'positive_edge_count':len(ce),
            'positive_edges':ce,'signed_transitions':arcs,'rank':len(ce)-n+1,
            'index':n if finite else 'INFINITE','equals_full_free_group':full,
            'pruned_positive_edges':pruned}


def fold_generators(generators,alphabet_size):
    edges=[];next_vertex=1;reduced_lengths=[]
    for word in generators:
        ww=reduce_word(word);reduced_lengths.append(len(ww));u=0
        for i,g in enumerate(ww):
            assert abs(g)<=alphabet_size
            v=0 if i==len(ww)-1 else next_vertex
            if v:next_vertex+=1
            edges.append((u,g,v) if g>0 else (v,-g,u));u=v
    uf=UnionFind(next_vertex);passes=[]
    initial={'vertices':next_vertex,'positive_edges':len(edges),
             'generators':len(reduced_lengths),'nonempty_reduced_generators':sum(n>0 for n in reduced_lengths)}
    edges=set(edges)
    while True:
        # Snapshot representatives before grouping; every merge in this pass is
        # justified by a collision already present in that snapshot.
        snapshot=sorted({(uf.find(u),g,uf.find(v)) for u,g,v in edges})
        outgoing=defaultdict(list)
        for u,g,v in snapshot:
            outgoing[(u,g)].append(v)
            outgoing[(v,-g)].append(u) # incoming positive collision
        merges=0
        for key,targets in sorted(outgoing.items()):
            first=targets[0]
            for other in targets[1:]:merges+=uf.union(first,other)
        edges={(uf.find(u),g,uf.find(v)) for u,g,v in snapshot}
        passes.append({'positive_edges_before':len(snapshot),'unions':merges,
                       'positive_edges_after':len(edges)})
        if not merges:break
    core=canonical_core(edges,uf.find(0),alphabet_size)
    # Every original generator must be a based loop in the resulting core.
    trans={(u,g):v for u,g,v in core['signed_transitions']}
    for word in generators:
        v=0
        for g in reduce_word(word):
            assert (v,g) in trans;v=trans[(v,g)]
        assert v==0
    core.update(initial_bouquet=initial,fold_passes=passes,generator_loop_replay='PASS')
    return core


def differences(words,reference):
    inverse=[-g for g in reversed(reference)]
    return [reduce_word(w+inverse) for w in words]


def self_test():
    def graph(texts,alphabet='ab'):
        enc={a:i+1 for i,a in enumerate(alphabet)}
        ww=[[enc[a] for a in w] for w in texts]
        return fold_generators(differences(ww,ww[0]),len(alphabet))
    g=graph(['a','b'])
    assert g['vertex_count']==2 and g['rank']==1 and not g['equals_full_free_group']
    assert g['positive_edges']==[[0,1,1],[0,2,1]] # common other endpoint
    g=graph(['a','aa','ab']);assert g['equals_full_free_group']
    g=graph(['a','aa']);assert not g['equals_full_free_group'] and g['positive_edges']==[[0,1,0]]
    g=graph(['a','aaa','ba','ab']);assert g['index']==2 and g['rank']==3
    g=fold_generators([[1,2,-1]],2)
    assert g['vertex_count']==2 and g['rank']==1 and g['positive_edges']==[[0,1,1],[1,2,1]]
    g=fold_generators([[1,-1],[]],2);assert g['vertex_count']==1 and not g['positive_edges']
    g=fold_generators([[1,2],[1,3]],3) # outgoing collision
    assert g['rank']==2 and len(g['positive_edges'])==3
    g=fold_generators([[1,3],[2,3]],3) # incoming collision
    assert g['rank']==2 and len(g['positive_edges'])==3
    assert canonical_core({(0,1,0),(0,2,1)},0,2)['pruned_positive_edges']==1
    # Generator order/inversion changes presentation but not canonical subgroup.
    gens=[[1,2,-1],[1,1],[2,1,-2]]
    a=fold_generators(gens,2);b=fold_generators([[-g for g in reversed(w)] for w in reversed(gens)],2)
    assert a['positive_edges']==b['positive_edges']
    print('PASS ten synthetic tests: common other endpoint, full/proper groups, index2, nonnormal base stem, cancellation, incoming/outgoing folds, pruning, presentation invariance')


def main():
    started=time.monotonic();ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path);ap.add_argument('--output',type=Path)
    ap.add_argument('--reference',default='f19r.8');ap.add_argument('--self-test',action='store_true')
    a=ap.parse_args()
    if a.self_test:self_test();return
    raw=a.source.read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA256
    rows=json.loads(raw);assert len(rows)==413 and len({r['locus'] for r in rows})==413
    alphabet=sorted({c for r in rows for c in r['literal']});assert len(alphabet)==20
    assert all(r['literal'] and r['literal'].isascii() and r['literal'].isalpha() and r['literal'].islower() for r in rows)
    enc={c:i+1 for i,c in enumerate(alphabet)}
    words=[[enc[c] for c in r['literal']] for r in rows]
    refs=[i for i,r in enumerate(rows) if r['locus']==a.reference];assert len(refs)==1
    ref=words[refs[0]];gens=differences(words,ref)
    core=fold_generators(gens,len(alphabet))
    out={'schema':'GDT903_INDEPENDENT_DIFFERENCE_SUBGROUP_V1','source_sha256':SOURCE_SHA256,
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'reference_locus':a.reference,'alphabet':alphabet,'signed_label_convention':'positive labels1..20 in sorted literal alphabet; inverse negative; BFS uses numeric sorted signed labels',
         'source_line_count':len(rows),'difference_reduced_lengths':[len(w) for w in gens],
         'subgroup_definition':'ordinary subgroup generated by wi wref^-1; not normal closure',
         'action_convention':'right action; all source words send base s to one common endpoint, not assumed equal to s',
         'core':core,'status':'ONLY_TRIVIAL_BASE_ORBIT' if core['equals_full_free_group'] else 'PROPER_SUBGROUP_NONTRIVIAL_ACTION_NOT_EXCLUDED',
         'elapsed_seconds':time.monotonic()-started,
         'claim_ceiling':'Equality H=F forces every literal generator to fix the base, hence common endpoint equals base; it does not force actions on disconnected states or all encodings to be trivial.'}
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'vertices':core['vertex_count'],'edges':core['positive_edge_count'],'rank':core['rank'],'elapsed_seconds':out['elapsed_seconds']}))


if __name__=='__main__':main()
