#!/usr/bin/env python3
"""Local proof-producing folds of all line paths with common, distinct endpoints."""
from collections import deque
import time

def initial_paths(words,alphabet):
    labels={a:i+1 for i,a in enumerate(alphabet)};edges=[];n=2
    for word in words:
        assert word
        u=0
        for k,a in enumerate(word):
            v=1 if k==len(word)-1 else n
            if v==n:n+=1
            edges.append((u,labels[a],v));u=v
    return n,edges

def adjacency(vertices,edges):
    adj={i:{} for i in range(vertices)}
    for u,a,v in edges:
        assert a>0 and (a not in adj[u] or adj[u][a]==v)
        assert -a not in adj[v] or adj[v][-a]==u
        adj[u][a]=v;adj[v][-a]=u
    return adj

def canonical(adj,base,terminal=None):
    numbering={base:0};queue=deque([base])
    while queue:
        u=queue.popleft()
        for a,v in sorted(adj[u].items()):
            if v not in numbering:numbering[v]=len(numbering);queue.append(v)
    assert len(numbering)==len(adj),'Graph must be connected'
    out={'vertices':len(adj),'edges':sorted([numbering[u],a,numbering[v]] for u,es in adj.items() for a,v in es.items() if a>0)}
    if terminal is None:out['base']=0
    else:out.update(start=0,terminal=numbering[terminal])
    return out

def pointed_core(graph):
    adj=adjacency(graph['vertices'],graph['edges']);base=graph.get('start',graph.get('base',0))
    queue=deque(v for v in adj if v!=base and len(adj[v])<=1)
    while queue:
        v=queue.popleft()
        if v not in adj or v==base or len(adj[v])>1:continue
        for a,u in list(adj[v].items()):
            assert adj[u][-a]==v;del adj[u][-a]
            if u!=base and len(adj[u])<=1:queue.append(u)
        del adj[v]
    return canonical(adj,base)

def complete(graph,alphabet):
    n=graph['vertices'];edges=list(graph['edges']);terminal=graph['terminal']
    if n==1:
        used={a for _,a,_ in edges};missing=next((a for a in range(1,len(alphabet)+1) if a not in used),None)
        if missing is None:return None
        edges.append([0,missing,1]);n=2
    permutations={}
    for a,char in enumerate(alphabet,1):
        p=[None]*n;used=set()
        for u,label,v in edges:
            if label!=a:continue
            assert p[u] is None or p[u]==v;p[u]=v
            assert v not in used;used.add(v)
        for u,v in zip((i for i,x in enumerate(p) if x is None),(i for i in range(n) if i not in used)):p[u]=v
        assert sorted(p)==list(range(n));permutations[char]=p
    return {'states':n,'start':0,'terminal':terminal,'permutations':permutations,'construction':'Sorted missing origins paired with sorted missing images independently for each character; compatibility witness only.'}

def replay(words,witness):
    p=witness['permutations'];n=witness['states'];start=witness['start'];end=witness['terminal']
    assert all(sorted(row)==list(range(n)) for row in p.values())
    for word in words:
        q=start
        for a in word:q=p[a][q]
        assert q==end
    reached={start};queue=deque([start])
    while queue:
        q=queue.popleft()
        for row in p.values():
            r=row[q]
            if r not in reached:reached.add(r);queue.append(r)
    assert len(reached)>1 and len(reached)==n
    return True

def fold(words,alphabet,deadline=None):
    def checktime():
        if deadline is not None and time.monotonic()>=deadline:raise TimeoutError
    checktime();n,edges=initial_paths(words,alphabet);parent=list(range(n));size=[1]*n;adj=[{} for _ in range(n)];queue=deque();log=[]
    def find(u):
        while parent[u]!=u:parent[u]=parent[parent[u]];u=parent[u]
        return u
    def insert(u,label,v,e,d):
        if label in adj[u]:
            old,old_e,old_d=adj[u][label];assert old_d==d;queue.append((old,v,old_e,e,d))
        else:adj[u][label]=(v,e,d)
    for e,(u,a,v) in enumerate(edges):
        insert(u,a,v,e,1);insert(v,-a,u,e,-1)
    while queue:
        u,v,e1,e2,d=queue.popleft();u=find(u);v=find(v)
        if u==v:continue
        if len(log)%1024==0:checktime()
        # Store a verifiable local necessity, not just unexplained root IDs.
        x,a,y=edges[e1];z,b,t=edges[e2];assert a==b
        if d<0:x,y=y,x;z,t=t,z
        assert find(x)==find(z) and {find(y),find(t)}=={u,v}
        log.append([e1,e2,d])
        if size[u]<size[v]:u,v=v,u
        parent[v]=u;size[u]+=size[v]
        for label,(target,e,direction) in adj[v].items():
            if label in adj[u]:
                old,old_e,old_d=adj[u][label];assert old_d==direction;queue.append((old,target,old_e,e,direction))
            else:adj[u][label]=(target,e,direction)
        adj[v].clear()
    checktime();roots={find(i) for i in range(n)};final={u:{} for u in roots}
    for u,a,v in edges:
        u=find(u);v=find(v)
        assert a not in final[u] or final[u][a]==v;assert -a not in final[v] or final[v][-a]==u
        final[u][a]=v;final[v][-a]=u
    graph=canonical(final,find(0),find(1));core=pointed_core(graph)
    full=core['vertices']==1 and len(core['edges'])==len(alphabet)
    completion=None if full else complete(graph,alphabet)
    if completion is not None:replay(words,completion)
    checktime()
    return {'initial_vertices':n,'initial_edges':len(edges),'union_count':len(log),'graph':graph,'core':core,'full_group':full,'completion':completion},log
