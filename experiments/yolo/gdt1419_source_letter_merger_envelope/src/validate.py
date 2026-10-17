#!/usr/bin/env python3
"""Independent source-directed mapping and finite graph-envelope verifier."""
import argparse, collections, gzip, hashlib, itertools, json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
A=E/'artifacts'
def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def legal(word,units):
    if len(word)!=len(units): return False
    # Pairwise implication, not the primary's prospective dictionary construction.
    return all(word[i]!=word[j] or units[i]==units[j]
               for i in range(len(word)) for j in range(i))
def layers(candidates,edges):
    if not candidates:return []
    result=[set(candidates[0])]
    for eligible in candidates[1:]:
        result.append({v for v in eligible if any((u,v) in edges for u in result[-1])})
    return result
def controls():
    checks=0
    for n in range(5):
        for chars in itertools.product('abc',repeat=n):
            word=''.join(chars);letters=sorted(set(word))
            for units in itertools.product('xy',repeat=n):
                oracle=any(tuple(dict(zip(letters,values))[c] for c in word)==units
                           for values in itertools.product('xy',repeat=len(letters)))
                assert legal(word,units)==oracle
                checks+=1
    assert legal('ab',('x','x')) and not legal('aa',('x','y'))
    path_checks=0
    nodes=('a','b')
    all_edges=list(itertools.product(nodes,repeat=2))
    subsets=[set(),{'a'},{'b'},{'a','b'}]
    for mask in range(16):
        edges={e for i,e in enumerate(all_edges) if mask>>i&1}
        for cs in itertools.product(subsets,repeat=3):
            got=layers(cs,edges)
            wanted={path[-1] for path in itertools.product(*cs)
                    if all(e in edges for e in zip(path,path[1:]))}
            assert got[-1]==wanted;path_checks+=1
    assert legal('ab',('x','y')) and legal('ac',('z','x'))
    assert layers([{'ab'},{'ac'}],{('ab','ac')})[-1]=={'ac'}
    assert not any(tuple(dict(zip('abc',v))[c] for c in 'ab')==('x','y')
                   and tuple(dict(zip('abc',v))[c] for c in 'ac')==('z','x')
                   for v in itertools.product('xyz',repeat=3))
    return {'status':'PASS','complete_function_cases':checks,'graph_path_cases':path_checks,
            'allowed_merge_forbidden_split':True,'envelope_false_positive_verified':True,
            'primary_imported_or_read_for_implementation':False}
def reconstruct(s):
    packet=read(ROOT/s['native_path']);unit=packet['source_unit']
    assert unit['edition']=='IT2a'
    assert [line['metadata']['locus'] for line in unit['lines']]==['f75v.'+str(i) for i in range(43,50)]
    signs=sorted(s['signs'],key=lambda x:(-len(x),x));rows=[];parsed=[]
    for line in unit['lines']:
        assert len(line['groups'])==int(line['metadata']['source_group_count'])
        for pos,row in enumerate(line['groups'],1):
            assert int(row[1])==pos
            word=row[2];units=[];cursor=0
            while cursor<len(word):
                choices=[x for x in signs if word.startswith(x,cursor)]
                assert choices,word
                x=choices[0];units.append(x);cursor+=len(x)
            rows.append(row);parsed.append(units)
    assert len(rows)==77 and rows==packet['original_groups'] and parsed==packet['original_units']
    recipes=read(ROOT/s['recipe_path']);deot=read(ROOT/s['deot_path']);other=read(ROOT/s['other_path'])
    records={}
    for name in s['source_names']:
        if name in ('b4','w1','bs1','gr1'):rs=[r['words'] for r in recipes[name]]
        elif name=='deot':rs=[r['words'] for r in deot['source_sections']]
        else:
            seq=other[name]['PRIMARY']['units'];assert len(seq)==8000
            grouped=[(key,list(g)) for key,g in itertools.groupby(seq,key=lambda r:r['sentence_index'])]
            assert len(grouped)==len({key for key,g in grouped})
            rs=[[r['unit'] for r in g] for key,g in grouped]
        assert all(all(isinstance(w,str) and w for w in r) for r in rs)
        records[name]=rs
    rebuilt={}
    for name,rs in records.items():
        W={w for r in rs for w in r};edges={e for r in rs for e in zip(r,r[1:])}
        bylength=collections.defaultdict(list)
        for w in sorted(W):bylength[len(w)].append(w)
        cs=[{w for w in bylength[len(us)] if legal(w,us)} for us in parsed]
        rebuilt[name]={'candidates':cs,'reachable':layers(cs,edges),'vocabulary':W,'edges':edges,'records':rs}
    return rows,parsed,rebuilt
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls()));return
    lock=read(E/'LOCK.json')
    for path,h in lock['files'].items():
        assert not Path(path).is_absolute() and sha(ROOT/path)==h,path
    s=read(E/'src/SPEC.json');rows,units,rebuilt=reconstruct(s)
    result=read(A/'RESULT.json')
    assert result['experiment_id']=='GDT1419' and result['status']=='NECESSARY_FORWARD_MERGER_ENVELOPE'
    groups=[{'id':r[0],'raw':r[2],'units':u} for r,u in zip(rows,units)]
    assert result['groups']==groups and result['claim_ceiling']==s['decision']
    assert result['lock_sha256']==sha(E/'LOCK.json')
    def sethash(values):
        return hashlib.sha256(json.dumps(sorted(values),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    expected=[]
    for name in s['source_names']:
        d=rebuilt[name];cs=d['candidates'];reach=d['reachable']
        def first_empty(layers_):
            for i,values in enumerate(layers_):
                if not values:return {'position':i+1,**groups[i]}
            return None
        expected.append({'source':name,'word_types':len(d['vocabulary']),
            'source_records':len(d['records']),'source_tokens':sum(map(len,d['records'])),
            'source_edges':len(d['edges']),
            'candidate_counts':[len(x) for x in cs],'candidate_sha256':[sethash(x) for x in cs],
            'reachable_counts':[len(x) for x in reach],'reachable_sha256':[sethash(x) for x in reach],
            'first_empty_candidate':first_empty(cs),'first_empty_path':first_empty(reach),
            'status':'RELAXED_PATH_EXISTS_NO_KEY_ESTABLISHED' if reach[-1] else 'EXCLUDED_BY_NECESSARY_ENVELOPE'})
    assert result['cases']==expected
    own=controls()
    receipt={'experiment_id':'GDT1419','status':'PASS_INDEPENDENT_ENVELOPE_RECONSTRUCTION',
             'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(E/'LOCK.json'),
             'result_sha256':sha(A/'RESULT.json'),'controls':own,'original_groups':len(rows),
             'cases':[{'source':c['source'],'status':c['status']} for c in expected],
             'scope':'Necessary per-word forward-function and source-bigram envelope only. No shared-key, inverse uniqueness, native meaning or source identity established. No primary implementation imported.'}
    out=A/'VALIDATION.json'
    if out.exists():assert read(out)==receipt
    else:out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'cases':len(expected)}))
if __name__=='__main__':main()
