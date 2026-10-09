import json,gzip,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
LETTERS=list('אבגדהוזחטיכלמנסעפצקרשת')
def hash_json(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def entropy(counts):
    total=sum(counts)
    return -sum((c/total)*math.log2(c/total) for c in counts if c)
def main():
    for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    source=json.loads((ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json').read_text())
    native=json.loads((ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/RESULT.json').read_text())
    cipher=json.loads(gzip.decompress((P/'artifacts/CIPHER.json.gz').read_bytes()));result=json.loads((P/'artifacts/RESULT.json').read_text())
    assert len(cipher)==len(source['source_sections'])==len(result['section_receipts'])==71
    all_encoded=[];charcount=0
    for original,encoded,receipt in zip(source['source_sections'],cipher,result['section_receipts']):
        assert original['ref']==encoded['ref']==receipt['ref'];assert len(original['words'])==len(encoded['words'])
        previous='';restored=[]
        for plain,nums in zip(original['words'],encoded['words']):
            assert len(nums)==len(plain) and all(type(v)==int and 0<=v<22 for v in nums)
            current=[]
            for j,delta in enumerate(nums):
                ref=LETTERS.index(previous[j]) if j<len(previous) else 0
                # Walk the ring instead of importing/subtracting primary ranks.
                possible=[step for step in range(22) if LETTERS[(ref+step)%22]==plain[j]]
                assert possible==[delta]
                current.append(LETTERS[(ref+delta)%22])
            decoded=''.join(current);assert decoded==plain
            previous=decoded;restored.append(decoded);all_encoded.append(tuple(nums));charcount+=len(nums)
        assert receipt==dict(ref=original['ref'],word_count=len(restored),source_sha256=hash_json(restored),encoded_sha256=hash_json(encoded['words']),roundtrip=True)
    assert len(all_encoded)==source['tokens']==6288 and charcount==24668
    sizes=Counter(map(len,all_encoded));mean=sum(k*n for k,n in sizes.items())/len(all_encoded)
    sd=math.sqrt(sum(k*k*n for k,n in sizes.items())/len(all_encoded)-mean*mean)
    pairs=Counter();left=Counter()
    for word in all_encoded:
        for j in range(1,len(word)):pairs[(word[j-1],word[j])]+=1;left[word[j-1]]+=1
    h=entropy(list(pairs.values()))-entropy(list(left.values()));metrics=dict(mean_length=mean,sd_length=sd,conditional_entropy=h)
    for k,v in metrics.items():assert abs(result['metrics'][k]-v)<1e-10,(k,v)
    assert result['source_words']==6288 and result['source_sections']==71 and result['source_letters']==charcount
    assert result['within_word_pairs']==sum(pairs.values())==18380
    assert result['pair_counts']==[[a,b,n] for (a,b),n in sorted(pairs.items())]
    assert result['length_histogram']==[[k,v] for k,v in sorted(sizes.items())]
    counts=Counter(all_encoded);top=sum(sorted(counts.values(),reverse=True)[:10]);assert result['frequency_diagnostics']==dict(word_types=len(counts),type_share=len(counts)/6288,top10_count=top,top10_share=top/6288)
    assert len(native['cells'])==len(result['cells'])==42
    totals=defaultdict(lambda:dict(samples=0,joint=0,mean_length=0,sd_length=0,conditional_entropy=0));noscope=0
    for before,after in zip(native['cells'],result['cells']):
        for k in ['reader','field','value','eligible_groups','capacity']:assert before[k]==after[k]
        samples=before.get('samples',[]);assert len(samples)==len(after['comparisons'])
        if not samples:noscope+=1
        for old,new in zip(samples,after['comparisons']):
            t=old['metrics'];within=dict(mean_length=.8*t['mean_length']<=mean<=1.2*t['mean_length'],sd_length=.75*t['sd_length']<=sd<=1.25*t['sd_length'],conditional_entropy=t['conditional_entropy']-.3<=h<=t['conditional_entropy']+.3)
            assert new==dict(seed=old['seed'],sample_ids_sha256=old['sample_ids_sha256'],within=within,joint=all(within.values()))
            c=totals[before['reader']];c['samples']+=1;c['joint']+=int(all(within.values()))
            for k,v in within.items():c[k]+=int(v)
    assert result['reader_results']==dict(totals)
    status='FIXED_WORD_COLUMN_SCREEN_EXCLUDED_ALL_READINGS' if all(r['joint']==0 for r in totals.values()) else 'NECESSARY_SCREEN_SURVIVES_ONLY';assert result['status']==status
    out=dict(status='PASS',whole_sections=71,source_words=6288,source_letters=charcount,source_pairs=sum(pairs.values()),sample_comparisons=sum(r['samples'] for r in totals.values()),untested_capacity_cells=noscope,conditional_entropy_joint_minus_context=h,verification='ring-walk forward, additive inverse, whole-buffer replacement, independent moments/entropy/gates; no primary imports')
    (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
