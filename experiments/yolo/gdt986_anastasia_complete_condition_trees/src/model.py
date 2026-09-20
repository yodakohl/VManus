"""Finite whole-string code with atom-aligned written words."""
import bisect
import collections
import heapq
import itertools
import time


def prefix_bound(counts, alphabet_size):
    weights = list(counts.values())
    if len(weights) == 1:
        return weights[0]
    if alphabet_size < 2:
        return None
    weights += [0] * ((-(len(weights)-1)) % (alphabet_size-1))
    heapq.heapify(weights)
    cost = 0
    while len(weights) > 1:
        total = sum(heapq.heappop(weights) for _ in range(alphabet_size))
        cost += total
        heapq.heappush(weights,total)
    return cost


def necessary(atoms, words):
    counts=collections.Counter(atoms)
    text=''.join(words)
    bound=prefix_bound(counts,len(set(text)))
    out=dict(source_atoms=len(atoms),target_characters=len(text),target_groups=len(words),
             alphabet_size=len(set(text)),prefix_length_lower_bound=bound)
    if len(text)<len(atoms):
        return dict(out,status='CONTRADICTED_NONEMPTY_LENGTH')
    if len(words)>len(atoms):
        return dict(out,status='CONTRADICTED_WORD_BOUNDARIES')
    if bound is None or bound>len(text):
        return dict(out,status='CONTRADICTED_PREFIX_LENGTH')
    upper={a:min(max(map(len,words)),(len(text)-(len(atoms)-k))//k) for a,k in counts.items()}
    pieces={w[i:j] for w in words for i in range(len(w)) for j in range(i+1,len(w)+1)}
    repeat_counts={p:sum(w.count(p) for w in words) for p in pieces}
    domains={a:sorted(p for p in pieces if len(p)<=upper[a] and repeat_counts[p]>=k)
             for a,k in sorted(counts.items()) if k>1}
    empty=[a for a,values in domains.items() if not values]
    out.update(code_length_bounds=upper,repeated_domains=domains,empty_domains=empty)
    out['status']='CONTRADICTED_REPEATED_DOMAIN' if empty else 'REQUIRES_FULL_EQUATION'
    return out


def witness(atoms, words, code):
    errors=[]
    if set(code)!=set(atoms) or any(not isinstance(v,str) or not v for v in code.values()):
        return dict(valid=False,errors=['incomplete_or_empty_code'])
    values=sorted(code.values())
    if any(b.startswith(a) for a,b in zip(values,values[1:])):
        errors.append('noninjective_or_prefix_collision')
    output=''.join(code[a] for a in atoms)
    if output!=''.join(words):errors.append('whole_output_mismatch')
    word_ends=list(itertools.accumulate(map(len,words)))
    atom_ends=list(itertools.accumulate(len(code[a]) for a in atoms))
    if not set(word_ends).issubset(set(atom_ends)):errors.append('seam_inside_atom')
    counts=collections.Counter(atoms)
    rows=[]
    start=0
    for i,(a,end) in enumerate(zip(atoms,atom_ends)):
        wi=bisect.bisect_right(word_ends,start)
        rows.append(dict(atom_index=i,atom=a,value=code[a],char_start=start,char_end=end,
                         word_index=wi,word=words[wi] if wi<len(words) else None))
        start=end
    singleton_chars=sum(len(code[a]) for a in atoms if counts[a]==1)
    return dict(valid=not errors,errors=errors,alignment=rows,
                singleton_characters=singleton_chars,total_characters=len(output),
                singleton_character_share=singleton_chars/len(output) if output else None)


def solve(job):
    import cvc5
    from cvc5 import Kind as K
    started=time.monotonic()
    atoms=job['atoms'];words=job['words'];text=''.join(words)
    prelim=necessary(atoms,words)
    if prelim['status']!='REQUIRES_FULL_EQUATION':
        return dict(status=prelim['status'],necessary=prelim,elapsed_seconds=time.monotonic()-started)
    s=cvc5.Solver();s.setLogic('QF_SLIA')
    s.setOption('produce-models','true');s.setOption('incremental','true');s.setOption('strings-exp','true')
    symbols=sorted(set(atoms));vs={a:s.mkConst(s.getStringSort(),f'atom_{i}') for i,a in enumerate(symbols)}
    def term(kind,*xs):return s.mkTerm(kind,*xs)
    def conjunction(xs):return xs[0] if len(xs)==1 else term(K.AND,*xs)
    def disjunction(xs):return xs[0] if len(xs)==1 else term(K.OR,*xs)
    for a,v in vs.items():
        length=term(K.STRING_LENGTH,v)
        s.assertFormula(term(K.GEQ,length,s.mkInteger(1)))
        s.assertFormula(term(K.LEQ,length,s.mkInteger(prelim['code_length_bounds'][a])))
        if a in prelim['repeated_domains']:
            s.assertFormula(disjunction([term(K.EQUAL,v,s.mkString(x)) for x in prelim['repeated_domains'][a]]))
    for a,b in itertools.combinations(symbols,2):
        s.assertFormula(term(K.NOT,term(K.STRING_PREFIX,vs[a],vs[b])))
        s.assertFormula(term(K.NOT,term(K.STRING_PREFIX,vs[b],vs[a])))
    equation=term(K.STRING_CONCAT,*[vs[a] for a in atoms]) if len(atoms)>1 else vs[atoms[0]]
    s.assertFormula(term(K.EQUAL,equation,s.mkString(text)))
    positions=[s.mkInteger(0)]
    for i,a in enumerate(atoms):
        p=s.mkConst(s.getIntegerSort(),f'end_{i}')
        s.assertFormula(term(K.EQUAL,p,term(K.ADD,positions[-1],term(K.STRING_LENGTH,vs[a]))))
        positions.append(p)
    for seam in list(itertools.accumulate(map(len,words)))[:-1]:
        s.assertFormula(disjunction([term(K.EQUAL,p,s.mkInteger(seam)) for p in positions[1:-1]]))
    for a,value in job.get('pinned_code',{}).items():
        s.assertFormula(term(K.EQUAL,vs[a],s.mkString(value)))
    def check(seconds):
        s.setOption('tlimit-per',str(int(seconds*1000)))
        answer=s.checkSat()
        return 'SAT' if answer.isSat() else 'UNSAT_SOLVER' if answer.isUnsat() else 'UNKNOWN_SOLVER'
    def get_code():return {a:s.getValue(v).getStringValue() for a,v in vs.items()}
    status=check(job.get('seconds',30))
    out=dict(status=status,solver='cvc5',solver_version=cvc5.__version__,necessary=prelim,
             elapsed_seconds=time.monotonic()-started)
    if status!='SAT':return out
    code=get_code();ground=witness(atoms,words,code)
    if not ground['valid']:
        return dict(out,status='ERROR_WITNESS',witness=ground)
    out.update(code=code,witness=ground,projections={})
    if job.get('projections',True):
        for a in sorted(prelim['repeated_domains']):
            s.push();s.assertFormula(term(K.NOT,term(K.EQUAL,vs[a],s.mkString(code[a]))))
            result=check(1);query={'status':result}
            if result=='SAT':
                alternate=get_code();g=witness(atoms,words,alternate)
                assert g['valid'] and alternate[a]!=code[a]
                query.update(alternative_code=alternate,alternative_value=alternate[a])
            out['projections'][a]=query
            s.pop()
    out['elapsed_seconds']=time.monotonic()-started
    return out
