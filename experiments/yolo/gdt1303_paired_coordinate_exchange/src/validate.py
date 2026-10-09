"""Independent rectangle lookup, source inverse, metrics and sample replay."""
import collections,gzip,hashlib,itertools,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
ALPHABET='אבגדהוזחטיכלמנסעפצקרשת'


def table_exchange(seq, rows, cols):
    table=[[r*cols+c for c in range(cols)] for r in range(rows)]
    coordinate={v:(r,c) for r,row in enumerate(table) for c,v in enumerate(row)}
    out=[]
    it=iter(seq)
    for a in it:
        b=next(it,None)
        if b is None:out.append(a);break
        r,c=coordinate[a];s,d=coordinate[b]
        out.extend([table[r][d],table[s][c]])
    return out


def ent(counts):
    total=sum(counts)
    return -sum(n/total*math.log2(n/total) for n in counts if n)


def main():
    for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
    src=json.loads((ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json').read_text())
    target=json.loads((ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/RESULT.json').read_text())
    cipher=json.loads(gzip.decompress((P/'artifacts/CIPHER.json.gz').read_bytes()));res=json.loads((P/'artifacts/RESULT.json').read_text())
    assert len(cipher)==len(src['source_sections'])==71
    ll=[];paircounts=collections.Counter();types=collections.Counter();blocks=0;odd=0
    for s,c in zip(src['source_sections'],cipher):
        assert s['ref']==c['ref'];assert list(map(len,s['words']))==list(map(len,c['words']))
        original=[ALPHABET.index(ch) for w in s['words'] for ch in w];actual=sum(c['words'],[])
        assert table_exchange(original,2,11)==actual
        decoded=table_exchange(actual,2,11);offset=0
        for word in s['words']:
            assert ''.join(ALPHABET[i] for i in decoded[offset:offset+len(word)])==word;offset+=len(word)
        for i in range(0,len(original)-1,2):
            a,b=original[i:i+2];x,y=actual[i:i+2]
            assert (a==b)==(x==y)
            assert a//11==x//11 and b//11==y//11
            assert a%11==y%11 and b%11==x%11
            blocks+=1
        if len(original)%2:assert actual[-1]==original[-1];odd+=1
        for w in c['words']:
            ll.append(len(w));types[tuple(w)]+=1;paircounts.update(zip(w,w[1:]))
    mean=sum(ll)/len(ll);sd=math.sqrt(sum((n-mean)**2 for n in ll)/len(ll));left=collections.Counter()
    for (a,b),n in paircounts.items():left[a]+=n
    metrics={'mean_length':mean,'sd_length':sd,'conditional_entropy':ent(list(paircounts.values()))-ent(list(left.values()))}
    assert all(abs(metrics[k]-res['metrics'][k])<1e-10 for k in metrics)
    assert res['pair_counts']==[[a,b,n] for (a,b),n in sorted(paircounts.items())]
    assert res['source_words']==len(ll)==6288 and res['source_letters']==sum(ll)==24668
    assert res['source_sections']==len(cipher) and res['within_word_pairs']==sum(paircounts.values())
    assert res['frequency_diagnostics']=={'types':len(types),'top10_count':sum(n for _,n in types.most_common(10))}
    totals=collections.defaultdict(lambda:dict(samples=0,joint=0,mean_length=0,sd_length=0,conditional_entropy=0));samples=0;unscored=0
    for old,new in zip(target['cells'],res['cells']):
        for k in ['reader','field','value','eligible_groups','capacity']:assert new[k]==old[k]
        assert len(new['comparisons'])==len(old.get('samples',[]))
        if not new['comparisons']:unscored+=1
        for sample,record in zip(old.get('samples',[]),new['comparisons']):
            t=sample['metrics'];checks={'mean_length':.8*t['mean_length']<=mean<=1.2*t['mean_length'],'sd_length':.75*t['sd_length']<=sd<=1.25*t['sd_length'],'conditional_entropy':t['conditional_entropy']-.3<=metrics['conditional_entropy']<=t['conditional_entropy']+.3}
            assert record=={'seed':sample['seed'],'sample_ids_sha256':sample['sample_ids_sha256'],'within':checks,'joint':all(checks.values())}
            out=totals[old['reader']];out['samples']+=1;out['joint']+=all(checks.values())
            for k,v in checks.items():out[k]+=v
            samples+=1
    assert len(target['cells'])==len(res['cells']) and dict(totals)==res['reader_results']
    expected='FIXED_COORDINATE_SCREEN_FAILED' if all(t['joint']==0 for t in totals.values()) else 'NECESSARY_SCREEN_SURVIVES_ONLY'
    assert expected==res['status']
    cap=json.loads((P/'artifacts/LADDER_CAPACITY.json').read_text())
    found=[];ntriples=0;n6=0
    for section in src['source_sections']:
        ws=section['words']
        for middle in range(1,len(ws)-1):
            ntriples+=1
            triple=ws[middle-1:middle+2]
            if [len(w) for w in triple]!=[6,6,6]:continue
            n6+=1
            # Explicit coordinate equalities, not the runner's slice predicate.
            valid=all(triple[0][j]==triple[1][j] for j in range(1,6)) and all(triple[1][j]==triple[2][j] for j in range(5))
            if valid:found.append({'ref':section['ref'],'start_zero_based':middle-1,'words':triple})
    assert cap['within_section_word_triples']==ntriples and cap['length_six_triples']==n6
    assert cap['ladder_witnesses']==found
    assert cap['status']==('NOT_EXCLUDED_BY_LADDER' if found else 'EVEN_TRIPLE_SOURCE_CAPACITY_EXCLUDED')
    hits=json.loads((ROOT/'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts/HITS.json').read_text())
    for ed,ids in cap['native_focal_source_ids'].items():
        hh=[h for h in hits if h['edition']==ed and h['locus']=='f40r.9']
        assert len(hh)==1 and hh[0]['source_ids']==ids
        assert all(g['ivtff_group_raw']=='okaiin' and g['left_separator']==g['right_separator']=='DEFINITE_SPACE' for g in hh[0]['groups'])
    assert set(cap['native_focal_source_ids'])=={'ZL3b','IT2a','RF1b'}
    # All short streams on2x2,2x3 rectangles; every possible single space position.
    import importlib.util
    spec=importlib.util.spec_from_file_location('candidate',P/'src/run.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    toy=0
    for rows,cols in [(2,2),(2,3)]:
        for n in range(6):
            for seq in itertools.product(range(rows*cols),repeat=n):
                expected_toy=table_exchange(seq,rows,cols)
                assert table_exchange(expected_toy,rows,cols)==list(seq)
                for cut in range(n+1):
                    words=[list(seq[:cut]),list(seq[cut:])]
                    actual_toy=module.exchange(words,cols)
                    assert sum(actual_toy,[])==expected_toy
                    assert module.exchange(actual_toy,cols)==words
                    toy+=1
    result={'status':'PASS','source_words_recovered':len(ll),'coordinate_pairs_checked':blocks,'odd_section_tails_checked':odd,'native_comparisons_replayed':samples,'unscored_cells_retained':unscored,'exhaustive_stream_split_cases':toy,'source_triple_capacity':cap['status'],'source_triples_checked':ntriples,'scope':'Separate source/metric implementation by root; fixture comparison imports runner only after independent expected outputs. Not historical or semantic confirmation.'}
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
