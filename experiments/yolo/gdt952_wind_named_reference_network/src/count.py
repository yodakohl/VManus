"""Exact counts and marginals by connected-component embeddings and disjoint masks."""
from collections import defaultdict
from functools import lru_cache
from math import factorial

def components(n,edges):
    unseen=set(range(n));out=[]
    while unseen:
        todo=[min(unseen)];seen=set(todo)
        while todo:
            u=todo.pop()
            for a,b in edges:
                v=b if a==u else a if b==u else None
                if v is not None and v not in seen:
                    seen.add(v);todo.append(v)
        unseen-=seen;out.append(sorted(seen))
    return sorted(out,key=lambda c:(-len(c),c))

def solve(n,edges,adj):
    """All bijections f with adj[f(a)][f(b)] for every source edge (a,b)."""
    if all(adj[i][j] for i in range(n) for j in range(n) if i!=j):
        return {'count':factorial(n),'marginals':[[factorial(n-1)]*n for _ in range(n)],'components':components(n,edges)}
    comps=components(n,edges);tables=[]
    for comp in comps:
        es=[(a,b) for a,b in edges if a in comp]
        order=sorted(comp,key=lambda u:(-sum(u in e for e in es),u))
        # mask -> count and per-node/per-position embedding counts
        counts=defaultdict(int);marg=defaultdict(lambda:defaultdict(int));assigned={}
        def visit(depth,mask):
            if depth==len(order):
                counts[mask]+=1
                for u,v in assigned.items():marg[mask][(u,v)]+=1
                return
            u=order[depth]
            for v in range(n):
                if mask>>v&1:continue
                if any(a==u and b in assigned and not adj[v][assigned[b]] or
                       b==u and a in assigned and not adj[assigned[a]][v]
                       for a,b in es):continue
                assigned[u]=v;visit(depth+1,mask|(1<<v));del assigned[u]
        visit(0,0);tables.append((dict(counts),dict(marg)))
    full=(1<<n)-1
    @lru_cache(None)
    def suffix(i,mask):
        if i==len(tables):return int(mask==full)
        return sum(c*suffix(i+1,mask|m) for m,c in tables[i][0].items() if not m&mask)
    total=suffix(0,0);result=[[0]*n for _ in range(n)]
    prefix={0:1}
    for i,(counts,marg) in enumerate(tables):
        coeff=defaultdict(int);nxt=defaultdict(int)
        for used,pcount in prefix.items():
            for m,c in counts.items():
                if m&used:continue
                coeff[m]+=pcount*suffix(i+1,used|m)
                nxt[used|m]+=pcount*c
        for m,k in coeff.items():
            for (u,v),c in marg[m].items():result[u][v]+=k*c
        prefix=dict(nxt)
    assert all(sum(row)==total for row in result)
    assert all(sum(row[v] for row in result)==total for v in range(n))
    return {'count':total,'marginals':result,'components':comps,
            'component_mask_counts':[len(t[0]) for t in tables],
            'component_embedding_counts':[sum(t[0].values()) for t in tables]}
