#!/usr/bin/env python3
"""Finite exact cancellation certificate; no string solver or text normalization."""
import argparse, collections, hashlib, itertools, json, time
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
ROLES=('location','mercury','companion'); IDS=('MS03','MS09','MJ03','MJ09')
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def incomparable(x,y):return not(x.startswith(y) or y.startswith(x))
def prefix_free(code):return all(code.values()) and all(incomparable(a,b) for a,b in itertools.combinations(code.values(),2))
def compile_source(source):
    rows={p['id']:p for p in source['programs']};assert source['program_count']==24 and len(rows)==24
    expected={'MS03':(['HOUSE','N03'],['SATURN'],['RET']),'MS09':(['HOUSE','N09'],['SATURN'],['RET']),'MJ03':(['HOUSE','N03'],['JUPITER'],['RET','REF','N09']),'MJ09':(['HOUSE','N09'],['JUPITER'],['REF','N03'])}
    for rid,(loc,comp,body) in expected.items():
        p=rows[rid];assert p['header_factors']=={'location':loc,'mercury':['MERCURY'],'companion':comp} and p['after_header']==['PARTILE'] and p['body_atoms']==body
    templates=[]
    for order in itertools.permutations(ROLES):
        eq={rid:sum((rows[rid]['header_factors'][k] for k in order),[])+rows[rid]['after_header']+rows[rid]['body_atoms'] for rid in IDS}
        a,b,c,d=(eq[r] for r in IDS);at=a.index('N03');u,v=a[:at],a[at+1:]
        assert b==u+['N09']+v and len(u)>=1 and len(v)>=2 and c[-1]=='N09' and d[-1]=='N03'
        assert len(u+v)==5 and len(set(u+v))==5
        templates.append(dict(order=list(order),equations=eq,U_atoms=u,V_atoms=v))
    return templates

def ends_index(texts):
    suffixes=collections.defaultdict(list)
    for i,t in enumerate(texts):
        for start in range(1,len(t)):suffixes[t[start:]].append(i)
    return suffixes

def common(a,b):
    p=0
    while p<min(len(a),len(b)) and a[p]==b[p]:p+=1
    s=0
    while s<min(len(a),len(b)) and a[-s-1]==b[-s-1]:s+=1
    return p,s

def relaxed(texts):
    suffixes=ends_index(texts);pairs=[];cuts=[]
    for a,b in itertools.combinations(range(len(texts)),2):
        A,B=texts[a],texts[b];p,s=common(A,B);n=pf=xs=ys=cs=0;combos=0
        for u in range(1,p+1):
            for v in range(2,min(s,len(A)-u-1,len(B)-u-1)+1):
                n+=1;X,Y=A[u:len(A)-v],B[u:len(B)-v]
                if not incomparable(X,Y):continue
                pf+=1;dx=[i for i in suffixes.get(X,()) if i not in (a,b)]
                if not dx:continue
                xs+=1;cy=[i for i in suffixes.get(Y,()) if i not in (a,b)]
                if not cy:continue
                ys+=1;count=sum(c!=d for c in cy for d in dx)
                if not count:continue
                cs+=1;combos+=count;cuts.append(dict(a=a,b=b,u=u,v=v,X=X,Y=Y,C_indices=cy,D_indices=dx))
        pairs.append([a,b,p,s,n,pf,xs,ys,cs,combos])
    return dict(columns=['a','b','lcp','lcs','cuts','prefix_incomparable','X_external_suffix','XY_external_suffix','four_distinct_cuts','four_distinct_combinations'],rows=pairs),cuts

def factor(text,atoms,code):
    if not atoms:
        if not text:yield code
        return
    for k in range(1,len(text)-len(atoms)+2):
        word=text[:k]
        if all(incomparable(word,val) for val in code.values()):
            yield from factor(text[k:],atoms[1:],dict(code,**{atoms[0]:word}))

def render(atoms,code):return ''.join(code[a] for a in atoms)
def exact(texts,cuts,templates):
    by_text={t:i for i,t in enumerate(texts)};found=[];counts=[collections.Counter() for _ in templates]
    for cut in cuts:
        u,v=cut['u'],cut['v'];U=texts[cut['a']][:u];V=texts[cut['a']][-v:]
        for reverse in (False,True):
            a,b=(cut['b'],cut['a']) if reverse else (cut['a'],cut['b']);X,Y=(cut['Y'],cut['X']) if reverse else (cut['X'],cut['Y']);ci=cut['D_indices'] if reverse else cut['C_indices']
            for ti,t in enumerate(templates):
                counts[ti]['oriented_relaxed_cuts']+=1
                eq=t['equations'];ce=eq['MJ03'];jp,fp=ce.index('JUPITER'),ce.index('REF');assert jp<fp and ce.count('JUPITER')==ce.count('REF')==1
                for first in factor(U,t['U_atoms'],{'N03':X,'N09':Y}):
                    for code in factor(V,t['V_atoms'],first):
                        counts[ti]['seven_atom_factorizations']+=1
                        assert render(eq['MS03'],code)==texts[a] and render(eq['MS09'],code)==texts[b]
                        pre=render(ce[:jp],code);mid=render(ce[jp+1:fp],code)
                        for c in ci:
                            C=texts[c]
                            if c in (a,b) or not C.startswith(pre) or not C.endswith(Y):continue
                            rest=C[len(pre):len(C)-len(Y)]
                            for size in range(1,len(rest)-len(mid)):
                                counts[ti]['jupiter_length_trials']+=1
                                if rest[size:size+len(mid)]!=mid:continue
                                J,F=rest[:size],rest[size+len(mid):];full=dict(code,JUPITER=J,REF=F)
                                if not prefix_free(full):continue
                                assert render(ce,full)==C
                                D=render(eq['MJ09'],full);d=by_text.get(D)
                                if d is None or d in (a,b,c):continue
                                outputs=dict(zip(IDS,[a,b,c,d]));assert all(render(eq[r],full)==texts[i] for r,i in outputs.items())
                                counts[ti]['witnesses']+=1;found.append(dict(header_order=t['order'],outputs=outputs,code=full))
    seen=set()
    for w in found:
        k=enc(w);assert k not in seen;seen.add(k)
    return found,[dict(c) for c in counts]

def positive_fixture(templates):
    atoms=sorted(set().union(*(set(t['equations'][r]) for t in templates for r in IDS)));code={a:chr(65+i)+'z' for i,a in enumerate(atoms)};assert len(code)==9 and prefix_free(code)
    results=[]
    for ti,t in enumerate(templates):
        targets={r:render(t['equations'][r],code) for r in IDS};texts=sorted(targets.values());assert len(set(texts))==4
        pairs,cuts=relaxed(texts);witnesses,counts=exact(texts,cuts,[t]);want=dict(header_order=t['order'],outputs={r:texts.index(v) for r,v in targets.items()},code=code)
        assert want in witnesses,(ti,'planted positive not recovered')
        # Exchange N03/N09 values to force the opposite A/B source orientation.
        other=dict(code,N03=code['N09'],N09=code['N03']);sw={r:render(t['equations'][r],other) for r in IDS};tt=sorted(sw.values());pp,cc=relaxed(tt);ww,_=exact(tt,cc,[t]);assert dict(header_order=t['order'],outputs={r:tt.index(v) for r,v in sw.items()},code=other) in ww
        results.append(dict(header_order=t['order'],both_source_orientations_recovered=True,fixture_witnesses=len(witnesses),swapped_fixture_witnesses=len(ww)))
    return results

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fixture-only',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args();spec=json.loads((E/'src/SPEC.json').read_text());sp=ROOT/spec['source']['path'];assert sha(sp)==spec['source']['sha256'];templates=compile_source(json.loads(sp.read_text()));fixtures=positive_fixture(templates)
    if a.fixture_only:print(enc(fixtures));return
    tp=ROOT/spec['target']['path'];assert sha(tp)==spec['target']['sha256'];target=json.loads(tp.read_text());panel=target['panels'][spec['panel']];assert len(panel)==259
    ids=collections.defaultdict(list)
    for row in panel:
        assert not row['page'].startswith('f84') and int(row['physical_folio'][1:])%2==1 and row['text']==' '.join(row['words']);ids[row['text']].append(row['id'])
    texts=sorted(ids);start=time.monotonic();pairs,cuts=relaxed(texts);witnesses,counts=exact(texts,cuts,templates)
    result=dict(status='FIXED_899_FULL_MODEL_EXCLUDED' if not witnesses else 'FOUR_RECORD_WITNESSES_FULL_899_MODEL_UNRESOLVED',target_paragraphs=len(panel),target_distinct_strings=len(texts),pairs=len(pairs['rows']),relaxed_cuts=len(cuts),relaxed_four_distinct_combinations=sum(x[-1] for x in pairs['rows']),exact_four_record_witnesses=len(witnesses),header_orders=[dict(order=t['order'],counts=c,status='EXCLUDED_BY_NECESSARY_FOUR_RECORDS' if not c.get('witnesses',0) else 'PARTIAL_FOUR_RECORD_WITNESSES_ONLY') for t,c in zip(templates,counts)],pair_stage_totals={k:sum(row[i] for row in pairs['rows']) for i,k in enumerate(pairs['columns']) if i>=4},source_sha256=spec['source']['sha256'],target_sha256=spec['target']['sha256'],claim_ceiling='Fixed899 source/compiler/nonerasing-prefix-code/target conjunction only; no general astrology exclusion or meaning.')
    objects={'THEOREM.json':templates,'FIXTURES.json':fixtures,'TARGET_IDS.json':{'strings':[dict(text=t,ids=ids[t]) for t in texts]},'PAIRS.json':pairs,'RELAXED.json':cuts,'WITNESSES.json':witnesses,'RESULT.json':result}
    for name,obj in objects.items():
        p=E/'artifacts'/name
        if a.check:assert p.read_text()==enc(obj),name
        else:p.write_text(enc(obj))
    print(json.dumps(result,indent=2));print('enumeration_seconds',time.monotonic()-start)
if __name__=='__main__':main()
