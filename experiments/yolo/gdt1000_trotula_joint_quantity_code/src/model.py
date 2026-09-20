"""Finite content-part writer and exhaustive necessary quantity constraints."""
import itertools,time

Q={'QD1','QD2','QS1'}

def split_stream(atoms):
    chunks=[[]];quantities=[]
    for a in atoms:
        if a in Q:quantities.append(a);chunks.append([])
        else:chunks[-1].append(a)
    return chunks,quantities

def segment_ok(atoms,words):
    return (not atoms and not words) or (bool(atoms) and bool(words) and len(words)<=len(atoms)<=sum(map(len,words)))

def placements(atoms,words):
    chunks,qs=split_stream(atoms)
    assert len(qs)==2
    for i in range(len(words)):
        if not segment_ok(chunks[0],words[:i]):continue
        for j in range(i+1,len(words)):
            if segment_ok(chunks[1],words[i+1:j]) and segment_ok(chunks[2],words[j+1:]):
                yield dict(zip(qs,(words[i],words[j]))),[i,j]

def unit_frames(one,two):
    n=len(two)-len(one)
    if n<=0:return []
    out=[]
    for k in range(len(one)-n+1):
        left,inc,right=one[:k],one[k:k+n],one[k+n:]
        if inc and (left or right) and left+inc+inc+right==two:
            out.append(dict(I=inc,L_D=left,R_D=right))
    return out

def other_unit(word,inc):
    out=[]
    for k in range(len(word)-len(inc)+1):
        if word[k:k+len(inc)]==inc and len(word)>len(inc):
            out.append(dict(L_S=word[:k],R_S=word[k+len(inc):]))
    return out

def prelim(recipe,atoms,words):
    if len(words)>len(atoms):return dict(status='CONTRADICTED_WORD_CAPACITY',options=[])
    if sum(map(len,words))<len(atoms):return dict(status='CONTRADICTED_NONEMPTY_LENGTH',options=[])
    options=[]
    for values,indices in placements(atoms,words):
        if recipe=='IV15':
            frames=unit_frames(values['QD1'],values['QD2'])
            if frames:options.append(dict(values=values,indices=indices,frames=frames))
        else:
            d,s=values['QD1'],values['QS1']
            if d==s:continue
            common={d[i:j] for i in range(len(d)) for j in range(i+1,len(d)+1) if j-i<len(d)} & {s[i:j] for i in range(len(s)) for j in range(i+1,len(s)+1) if j-i<len(s)}
            if common:options.append(dict(values=values,indices=indices,possible_I=sorted(common)))
    return dict(status='NECESSARY_QUANTITY_COMPATIBLE' if options else 'CONTRADICTED_QUANTITY_PLACEMENT',options=options)

def joint_numeric(a,b):
    triples={}
    for x in a:
        for y in b:
            if x['values']['QD1']!=y['values']['QD1']:continue
            one,two,scr=x['values']['QD1'],x['values']['QD2'],y['values']['QS1']
            if len({one,two,scr})!=3:continue
            for f in x['frames']:
                for g in other_unit(scr,f['I']):
                    if (g['L_S'],g['R_S'])==(f['L_D'],f['R_D']):continue
                    frame=dict(f,**g);key=(one,two,scr)
                    if frame not in triples.setdefault(key,[]):triples[key].append(frame)
    return [dict(values=dict(zip(('QD1','QD2','QS1'),key)),frames=frames) for key,frames in sorted(triples.items())]

def ground(streams,words,code,numeric):
    issues=[];ordinary={a:v for a,v in code.items() if a not in Q}
    if any(not v for v in code.values()):issues.append('empty_code')
    if set(code)!=set().union(*map(set,streams)):issues.append('code_inventory')
    for a,b in itertools.combinations(sorted(ordinary),2):
        if ordinary[a].startswith(ordinary[b]) or ordinary[b].startswith(ordinary[a]):issues.append('prefix_collision')
    vals={a:code[a] for a in Q}
    allowed=[x for x in numeric if x['values']==vals]
    if not allowed:issues.append('numeric_code_not_allowed')
    alignment=[]
    for atoms,ws in zip(streams,words):
        text=''.join(ws);output=''.join(code[a] for a in atoms)
        if output!=text:issues.append('whole_string')
        starts=[0]+list(itertools.accumulate(map(len,ws)))[:-1];ends=list(itertools.accumulate(map(len,ws)))
        pos=0;boundaries={0};rows=[]
        for a in atoms:
            end=pos+len(code[a]);boundaries.add(end)
            wi=next((i for i,(lo,hi) in enumerate(zip(starts,ends)) if lo<=pos<hi),None)
            if a in Q and (wi is None or pos!=starts[wi] or end!=ends[wi]):issues.append('quantity_seam')
            rows.append(dict(atom=a,code=code[a],start=pos,end=end,word_index=wi));pos=end
        if not set(ends)<=boundaries:issues.append('word_seam')
        for i,w in enumerate(ws):
            assigned=[r['atom'] for r in rows if r['word_index']==i]
            if not any(a in Q for a in assigned) and w in vals.values():issues.append('quantity_collision')
        alignment.append(rows)
    return dict(valid=not issues,issues=sorted(set(issues)),alignment=alignment,numeric_frames=allowed[0]['frames'] if allowed else [])

def solve(job):
    import cvc5
    from cvc5 import Kind as K
    start=time.monotonic();streams=job['streams'];words=job['words'];numeric=job['numeric']
    s=cvc5.Solver();s.setLogic('QF_SLIA');s.setOption('produce-models','true');s.setOption('incremental','true');s.setOption('strings-exp','true')
    atoms=sorted(set().union(*map(set,streams)));vs={a:s.mkConst(s.getStringSort(),a) for a in atoms}
    def op(k,*xs):return s.mkTerm(k,*xs)
    def conjunction(xs):return s.mkBoolean(True) if not xs else xs[0] if len(xs)==1 else op(K.AND,*xs)
    def disjunction(xs):return s.mkBoolean(False) if not xs else xs[0] if len(xs)==1 else op(K.OR,*xs)
    maxlen=max(len(w) for ws in words for w in ws)
    for a,v in vs.items():
        s.assertFormula(op(K.GEQ,op(K.STRING_LENGTH,v),s.mkInteger(1)))
        s.assertFormula(op(K.LEQ,op(K.STRING_LENGTH,v),s.mkInteger(maxlen)))
    for a,b in itertools.combinations([a for a in atoms if a not in Q],2):
        s.assertFormula(op(K.NOT,op(K.STRING_PREFIX,vs[a],vs[b])))
        s.assertFormula(op(K.NOT,op(K.STRING_PREFIX,vs[b],vs[a])))
    s.assertFormula(disjunction([conjunction([op(K.EQUAL,vs[a],s.mkString(v)) for a,v in x['values'].items()]) for x in numeric]))
    for row,(stream,ws) in enumerate(zip(streams,words)):
        text=''.join(ws);s.assertFormula(op(K.EQUAL,op(K.STRING_CONCAT,*[vs[a] for a in stream]),s.mkString(text)))
        positions=[s.mkInteger(0)]
        for i,a in enumerate(stream):
            p=s.mkConst(s.getIntegerSort(),f'end_{row}_{i}')
            s.assertFormula(op(K.EQUAL,p,op(K.ADD,positions[-1],op(K.STRING_LENGTH,vs[a]))));positions.append(p)
        ends=list(itertools.accumulate(map(len,ws)));starts=[0]+ends[:-1]
        for end in ends[:-1]:s.assertFormula(disjunction([op(K.EQUAL,p,s.mkInteger(end)) for p in positions[1:-1]]))
        for i,a in enumerate(stream):
            if a in Q:s.assertFormula(disjunction([conjunction([op(K.EQUAL,positions[i],s.mkInteger(lo)),op(K.EQUAL,positions[i+1],s.mkInteger(hi))]) for lo,hi in zip(starts,ends)]))
        # Numeric words cannot also occur as an ordinary-content word in this pair.
        for lo,hi,w in zip(starts,ends,ws):
            q_at_word=disjunction([conjunction([op(K.EQUAL,positions[i],s.mkInteger(lo)),op(K.EQUAL,positions[i+1],s.mkInteger(hi))]) for i,a in enumerate(stream) if a in Q])
            matches_numeric=disjunction([op(K.EQUAL,vs[a],s.mkString(w)) for a in Q])
            s.assertFormula(op(K.IMPLIES,matches_numeric,q_at_word))
    for a,v in job.get('pinned_code',{}).items():s.assertFormula(op(K.EQUAL,vs[a],s.mkString(v)))
    def check(seconds):
        s.setOption('tlimit-per',str(int(seconds*1000)));r=s.checkSat()
        return 'SAT' if r.isSat() else 'UNSAT_SOLVER' if r.isUnsat() else 'UNKNOWN_SOLVER'
    def code():return {a:s.getValue(v).getStringValue() for a,v in vs.items()}
    status=check(job.get('seconds',3));out=dict(status=status,solver='cvc5',solver_version=cvc5.__version__)
    if status=='SAT':
        c=code();w=ground(streams,words,c,numeric)
        if not w['valid']:return dict(status='ERROR_WITNESS',witness=w)
        out.update(code=c,witness=w)
        # Ask for any different ordinary code or numeric projection, not restart agreement.
        s.assertFormula(disjunction([op(K.NOT,op(K.EQUAL,vs[a],s.mkString(v))) for a,v in c.items()]))
        alt=check(job.get('alternative_seconds',1));out['alternative_status']=alt
        if alt=='SAT':
            c2=code();w2=ground(streams,words,c2,numeric);assert w2['valid'];out.update(alternative_code=c2,alternative_witness=w2)
    out['elapsed_seconds']=time.monotonic()-start
    return out
