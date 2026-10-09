"""One compound code, with explicit activity accounting."""
def models(A):
    out=[]
    for g in A:
        for h in A:
            for side in ('after','before'):
                if g==h and side=='before':continue
                out.append({'id':len(out),'missing_singleton':g,'companion':h,'side':side,
                            'compound':[g,h]if side=='after'else[h,g]})
    return out


def direct(w,m):
    g,h,side=m['missing_singleton'],m['companion'],m['side']
    positions=[i for i,c in enumerate(w)if c==g]
    if g==h:
        i=0
        while i<len(positions):
            if i+1==len(positions)or positions[i+1]!=positions[i]+1:return None
            i+=2
        return len(positions)//2
    offset=1 if side=='after'else -1
    for i in positions:
        j=i+offset
        if j<0 or j>=len(w)or w[j]!=h:return None
    return len(positions)


def select(records,N,percentages):
    def minimum(candidates):
        if not candidates:return {'status':'NO_CAPACITY','minimum_failed_tokens':None,'model_ids':[]}
        low=min(x['failed_tokens']for x in candidates)
        return {'status':'DESCRIPTIVE_MINIMUM','minimum_failed_tokens':low,'model_ids':[x['id']for x in candidates if x['failed_tokens']==low]}
    active=[r for r in records if r['active_tokens']>0]
    output={'active_at_least_one':minimum(active),'activity_percentages':{},'per_missing_sign':{},'pareto_model_ids':[]}
    for p in percentages:
        minimum_active=(p*N+99)//100
        value=minimum([r for r in active if r['active_tokens']>=minimum_active]);value['minimum_active_tokens']=minimum_active
        output['activity_percentages'][str(p)]=value
    for g in sorted({r['missing_singleton']for r in records}):
        output['per_missing_sign'][g]=minimum([r for r in active if r['missing_singleton']==g])
    output['pareto_model_ids']=[r['id']for r in active if not any(x['failed_tokens']<=r['failed_tokens']and x['active_tokens']>=r['active_tokens']and(x['failed_tokens']<r['failed_tokens']or x['active_tokens']>r['active_tokens'])for x in active)]
    return output
