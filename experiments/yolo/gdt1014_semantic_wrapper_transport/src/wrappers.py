"""Literal wrapper scope and semantic-function constraints; no normalization."""
import collections,itertools,re

def relations(words):
    words=set(words);good={w for w in words if re.fullmatch('[a-z]+',w)};groups=collections.defaultdict(set)
    for base in sorted(good):
        for out in sorted(good):
            if not 1<=len(out)-len(base)<=3:continue
            if out.endswith(base):groups[('L',out[:-len(base)])].add((base,out))
            if out.startswith(base):groups[('R',out[len(base):])].add((base,out))
    return [dict(side=side,affix=affix,pairs=[list(p) for p in sorted(pairs)]) for (side,affix),pairs in sorted(groups.items()) if len(pairs)>=2]

def contradictions(code,groups):
    out=[]
    for group in groups:
        by=collections.defaultdict(list)
        for base,word in group['pairs']:by[code[base]].append((base,word,code[word]))
        for value,items in by.items():
            if len({x[2] for x in items})>1:out.append(dict(side=group['side'],affix=group['affix'],input_value=value,observed=items))
    return out

def impose_z3(b,groups):
    import z3
    s=b['solver'];num=b['num'];lex=b['lexicon'];x=lambda w:z3.IntVal(num[lex[w]]) if w in lex else b['xs'][w]
    count=0
    for group in groups:
        for (a,bw),(c,d) in itertools.combinations(group['pairs'],2):
            s.add(z3.Implies(x(a)==x(c),x(bw)==x(d)));count+=1
    return count
