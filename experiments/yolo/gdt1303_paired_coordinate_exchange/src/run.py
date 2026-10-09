"""One fixed 2x11 coordinate exchange on disjoint character pairs."""
import collections, gzip, hashlib, json, math, statistics
from pathlib import Path
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
ALPHABET='אבגדהוזחטיכלמנסעפצקרשת'
SOURCE='experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json'
TARGET='experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/RESULT.json'


def exchange(words, columns=11):
    lengths=list(map(len,words)); seq=[v for w in words for v in w]
    for i in range(0,len(seq)-1,2):
        a,b=seq[i:i+2]
        seq[i]=(a//columns)*columns+b%columns
        seq[i+1]=(b//columns)*columns+a%columns
    out=[];offset=0
    for n in lengths:
        out.append(seq[offset:offset+n]);offset+=n
    return out


def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for path,h in lock.items(): assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    src=json.loads((ROOT/SOURCE).read_text()); native=json.loads((ROOT/TARGET).read_text())
    hits=json.loads((ROOT/'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts/HITS.json').read_text())
    focal=[h for h in hits if h['locus']=='f40r.9' and h['raw']=='okaiin']
    assert len(focal)==3 and {h['edition'] for h in focal}=={'ZL3b','IT2a','RF1b'}
    assert all(h['source_indices']==['6','7','8'] for h in focal)
    assert len('okaiin')==6  # six individual working units, no multigraph label
    ladder=[];triples=0;length_six=0
    for section in src['source_sections']:
        for i,(a,b,c) in enumerate(zip(section['words'],section['words'][1:],section['words'][2:])):
            triples+=1
            if len(a)==len(b)==len(c)==6:
                length_six+=1
                if a[1:]==b[1:] and b[:-1]==c[:-1]:
                    ladder.append({'ref':section['ref'],'start_zero_based':i,'words':[a,b,c]})
    capacity={'status':'EVEN_TRIPLE_SOURCE_CAPACITY_EXCLUDED' if not ladder else 'NOT_EXCLUDED_BY_LADDER',
      'within_section_word_triples':triples,'length_six_triples':length_six,'ladder_witnesses':ladder,
      'native_focal_source_ids':{h['edition']:h['source_ids'] for h in focal},
      'scope':'Any fixed pair bijection on this source projection, preserved word boundaries and continuous disjoint pairing; not other source content.'}
    (P/'artifacts/LADDER_CAPACITY.json').write_text(json.dumps(capacity,ensure_ascii=False,indent=2)+'\n')
    ranks={c:i for i,c in enumerate(ALPHABET)}
    coded=[];words=[];source_words=0
    for section in src['source_sections']:
        raw=[[ranks[c] for c in w] for w in section['words']]
        out=exchange(raw);assert exchange(out)==raw
        assert [''.join(ALPHABET[i] for i in w) for w in exchange(out)]==section['words']
        coded.append({'ref':section['ref'],'words':out});words+=list(map(tuple,out));source_words+=len(raw)
    ll=list(map(len,words));pairs=collections.Counter((a,b) for w in words for a,b in zip(w,w[1:]));left=collections.Counter()
    for (a,b),n in pairs.items():left[a]+=n
    total=sum(pairs.values())
    entropy=-sum(n/total*math.log2(n/left[a]) for (a,b),n in pairs.items())
    metrics={'mean_length':statistics.mean(ll),'sd_length':statistics.pstdev(ll),'conditional_entropy':entropy}
    freq=collections.Counter(words)
    cells=[];totals=collections.defaultdict(lambda:dict(samples=0,joint=0,mean_length=0,sd_length=0,conditional_entropy=0))
    for cell in native['cells']:
        row={k:cell[k] for k in ['reader','field','value','eligible_groups','capacity']};checks=[]
        for sample in cell.get('samples',[]):
            target=sample['metrics'];within={k:abs(metrics[k]-target[k]) <= (target[k]*{'mean_length':.2,'sd_length':.25}[k] if k!='conditional_entropy' else .3) for k in metrics}
            joint=all(within.values());checks.append({'seed':sample['seed'],'sample_ids_sha256':sample['sample_ids_sha256'],'within':within,'joint':joint})
            t=totals[cell['reader']];t['samples']+=1;t['joint']+=joint
            for k,v in within.items():t[k]+=v
        row['comparisons']=checks;cells.append(row)
    result={'status':'FIXED_COORDINATE_SCREEN_FAILED' if all(t['joint']==0 for t in totals.values()) else 'NECESSARY_SCREEN_SURVIVES_ONLY',
      'source_words':source_words,'source_sections':len(coded),'source_letters':sum(ll),'within_word_pairs':total,'metrics':metrics,
      'frequency_diagnostics':{'types':len(freq),'top10_count':sum(n for _,n in freq.most_common(10))},
      'pair_counts':[[a,b,n] for (a,b),n in sorted(pairs.items())],'reader_results':dict(totals),'cells':cells}
    (P/'artifacts/CIPHER.json.gz').write_bytes(gzip.compress(json.dumps(coded,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    (P/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['cells','pair_counts']},indent=2))
    print(json.dumps(capacity,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
