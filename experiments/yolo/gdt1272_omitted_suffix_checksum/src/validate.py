"""Independent checker: no runner imports, direct inverse and conditional distributions."""
import collections, hashlib, json, math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def read(path):return json.loads(path.read_text())
def check():
    lock=read(P/'src/REGISTRATION_LOCK.json')
    for path,h in lock['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    src=read(ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json')
    old=read(ROOT/'experiments/yolo/gdt1229_fixed_wordbook_branch_rank/artifacts/RESULT.json')
    tolerances=read(ROOT/'experiments/yolo/gdt1229_fixed_wordbook_branch_rank/src/SPEC.json')['metrics']
    result=read(P/'artifacts/RESULT.json');cipher=read(P/'artifacts/CIPHER.json');table=read(P/'artifacts/WORDBOOK.json')
    alphabet='אבגדהוזחטיכלמנסעפצקרשת'; words=[w for s in src['source_sections'] for w in s['words']]; lex=set(words)
    signatures={}; buckets=collections.defaultdict(list)
    for w in lex:
        if len(w)<4:continue
        running=0; total=0
        for c in reversed(w[2:]):
            running+=alphabet.find(c)+1;total+=running
        signature=(w[:2],len(w)-2,total%19);signatures[w]=signature;buckets[signature].append(w)
    expected={}; mode={}
    for w in lex:
        s=signatures.get(w)
        short=s is not None and w[0]!=alphabet[-1] and s[1]<=21 and len(buckets[s])==1
        expected[w]=[alphabet.find(w[0]),alphabet.find(w[1]),s[1],s[2]] if short else [21]+[alphabet.find(c) for c in w]
        mode[w]='short' if short else 'literal'
    assert len(table)==len(lex)
    for row in table:assert row['code']==expected[row['word']] and row['mode']==mode[row['word']]
    assert {r['word'] for r in table}==lex
    assert len({tuple(v) for v in expected.values()})==len(lex)
    flat=[]; mode_tokens=collections.Counter()
    assert len(cipher)==len(src['source_sections'])
    for actual, original in zip(cipher,src['source_sections']):
        assert actual['ref']==original['ref'];decoded=[]
        for code in actual['words']:
            assert all(type(c) is int and 0<=c<22 for c in code)
            if code[0]==21:
                assert len(code)>1;w=''.join(alphabet[i] for i in code[1:])
            else:
                assert len(code)==4
                candidates=buckets.get((''.join(alphabet[i] for i in code[:2]),code[2],code[3]),[])
                assert len(candidates)==1;w=candidates[0]
            assert code==expected[w];decoded.append(w);flat.append(tuple(code));mode_tokens[mode[w]]+=1
        assert decoded==original['words']
    collisions=read(P/'artifacts/COLLISIONS.json')
    expected_collisions={(p,n,h):sorted(ws) for (p,n,h),ws in buckets.items() if len(ws)>1}
    assert {(x['prefix'],x['suffix_length'],x['checksum']):x['words'] for x in collisions}==expected_collisions
    n=len(flat); counts=collections.Counter(flat); lengths=collections.Counter(map(len,flat)); glyphs=collections.Counter(x for w in flat for x in w)
    transitions=collections.defaultdict(collections.Counter)
    for w in flat:
        for a,b in zip(w,w[1:]):transitions[a][b]+=1
    total=sum(glyphs.values()); mean=total/n; pairs=sum(sum(v.values()) for v in transitions.values())
    def entropy(counter):
        den=sum(counter.values())
        return sum((c/den)*math.log2(den/c) for c in counter.values())
    metrics={'mean_length':mean,'sd_length':math.sqrt(sum(c*(k-mean)**2 for k,c in lengths.items())/n),'type_ratio':len(counts)/n,'top10_share':sum(sorted(counts.values(),reverse=True)[:10])/n,'glyph_entropy':entropy(glyphs),'conditional_entropy':sum(sum(row.values())/pairs*entropy(row) for row in transitions.values())}
    for k,v in metrics.items():assert abs(v-result['metrics'][k])<1e-11,(k,v,result['metrics'][k])
    expected_counts={'source_words':len(words),'source_sections':len(cipher),'wordbook_types':len(lex),'wordbook_letters':sum(len(w) for w in lex),'indexed_buckets':len(buckets),'collision_buckets':len(expected_collisions),'collision_types':sum(len(v) for v in expected_collisions.values()),'collision_tokens':sum(w in signatures and len(buckets[signatures[w]])>1 for w in words),'source_letters':sum(len(w) for w in words),'escape_only_letters':sum(len(w)+1 for w in words),'encoded_letters':total}
    for k,v in expected_counts.items():assert result[k]==v,(k,v)
    assert result['mode_tokens']==dict(mode_tokens)
    assert result['mode_types']==dict(collections.Counter(mode.values()))
    assert result['length_histogram']==[list(x) for x in sorted(lengths.items())]
    assert sorted(counts.values())==sorted(collections.Counter(words).values())
    totals=collections.defaultdict(lambda:{'samples':0,'joint':0,**{k:0 for k in metrics}})
    assert len(old['cells'])==len(result['cells'])
    for oldcell,newcell in zip(old['cells'],result['cells']):
        for k in ['reader','field','value','eligible_groups','capacity']:assert oldcell[k]==newcell[k]
        assert len(oldcell.get('samples',[]))==len(newcell['comparisons'])
        for sample,answer in zip(oldcell.get('samples',[]),newcell['comparisons']):
            flags={}
            for k,(kind,tol) in tolerances.items():
                target=sample['metrics'][k];epsilon=tol*target if kind=='relative' else tol
                flags[k]=target-epsilon<=metrics[k]<=target+epsilon
            joint=all(flags.values())
            assert answer=={'seed':sample['seed'],'sample_ids_sha256':sample['sample_ids_sha256'],'within':flags,'joint':joint}
            t=totals[oldcell['reader']];t['samples']+=1;t['joint']+=joint
            for k,v in flags.items():t[k]+=v
    assert result['reader_results']==dict(totals)
    status='FIXED_CHECKSUM_SCREEN_EXCLUDED_ALL_READINGS' if all(v['joint']==0 for v in totals.values()) else 'NECESSARY_SCREEN_SURVIVES_ONLY'
    assert result['status']==status
    out={'status':'PASS','source_words_decoded':n,'dictionary_entries':len(lex),'native_cached_comparisons':sum(v['samples'] for v in totals.values()),'metrics_recomputed':metrics,'scope':'separate code by same author; fixed cached projections, no native reread or independent history'}
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':check()
