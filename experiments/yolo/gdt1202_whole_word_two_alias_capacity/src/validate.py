"""Separate indexed-source count and occurrence allocation; no runner import."""
from pathlib import Path
from collections import Counter
from itertools import product
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def read(n):return json.loads((A/n).read_text())
def fixtures():
    checked=0
    # Exhaust all at-most-two partitions of two sample word frequencies,
    # zero-padding. Balancing must minimize every pooled top-k sum.
    for n,m in product(range(1,13),repeat=2):
        even=sorted([n//2,n-n//2,m//2,m-m//2],reverse=True)
        for x,y in product(range(n+1),range(m+1)):
            candidate=sorted([x,n-x,y,m-y],reverse=True)
            assert sum(v>0 for v in candidate)<=min(n,2)+min(m,2)
            for k in range(1,5):assert sum(candidate[:k])>=sum(even[:k])
            checked+=1
    merges=0
    for cells in product(range(1,5),repeat=4):
        before=sorted(cells,reverse=True)
        for i in range(4):
            for j in range(i+1,4):
                after=sorted([cells[i]+cells[j]]+[x for k,x in enumerate(cells) if k not in (i,j)]+[0],reverse=True)
                for k in range(1,5):assert sum(after[:k])>=sum(before[:k])
                merges+=1
    return checked,merges

def main():
    for p,h in read('REGISTRATION_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert read('RUN_RECEIPT.json')['runner_sha256']==hashlib.sha256((D/'src/run.py').read_bytes()).hexdigest()
    receipt=read('SOURCE_RECEIPT.json');source=json.loads((ROOT/receipt['source_file']).read_text());target=json.loads((ROOT/receipt['target_summary_file']).read_text())['targets']
    assert hashlib.sha256((ROOT/receipt['source_file']).read_bytes()).hexdigest()==receipt['source_sha256']
    assert hashlib.sha256((ROOT/receipt['target_summary_file']).read_bytes()).hexdigest()==receipt['target_summary_sha256']
    result=read('RESULT.json');tables=read('FREQUENCIES.json');assert set(result['books'])==set(tables)=={'b4','w1','bs1','gr1'}
    partition_checks,merge_checks=fixtures();total_recipes=total_words=0;failure_conditions=[]
    for book in ('b4','w1','bs1','gr1'):
        located=[];ranges=[];full_word_count=0
        for ri,r in enumerate(source[book]):
            full_word_count+=len(r['words']);taken=0
            for wi,w in enumerate(r['words']):
                assert isinstance(w,str) and w
                if len(located)<8000:located.append((ri,wi,w));taken+=1
            if taken:ranges.append({'recipe_index':ri,'first_word_index':0,'sample_count':taken,'stored_recipe_words':len(r['words'])})
        assert len(located)==8000
        sample=[w for ri,wi,w in located];counts=Counter(sample);freq=tables[book]
        assert [row['word'] for row in freq]==sorted(counts)
        # An independent occurrence-by-occurrence alternating allocation for
        # each source word achieves the balanced RELAXATION, not a cheap writer.
        bins={w:[0,0] for w in counts};seen=Counter()
        for word in sample:bins[word][seen[word]%2]+=1;seen[word]+=1
        for row in freq:
            assert row['count']==counts[row['word']]
            assert row['balanced_two_counts']==bins[row['word']]
        cells=sorted([(n,w,i) for w,pair in bins.items() for i,n in enumerate(pair) if n],key=lambda x:(-x[0],x[1],x[2]))
        types=len(cells);top=sum(n for n,w,i in cells[:10]);assert sum(n for n,w,i in cells)==8000
        r=result['books'][book]
        assert r['sample_words']==8000 and r['source_types']==len(counts)
        assert r['source_singletons']==sum(n==1 for n in counts.values())
        assert r['source_top10_count']==sum(sorted(counts.values())[-10:])
        assert r['two_alias_types_upper_count']==types and types==2*len(counts)-r['source_singletons']
        assert r['two_alias_top10_lower_count']==top and r['two_alias_top10_lower_share']==top/8000
        assert r['balanced_top10_cells']==[{'word':w,'alias_index':i,'count':n} for n,w,i in cells[:10]]
        oks=[]
        for ed,t in target.items():
            assert t['tokens']==8000
            # Convert the known exact 8000-token ratios to integral counts.
            v=int(t['type_ratio']*8000+0.5);mass=int(t['top10_share']*8000+0.5)
            assert abs(v/8000-t['type_ratio'])<1e-12 and abs(mass/8000-t['top10_share'])<1e-12
            limits={'native_types':v,'native_top10_count':mass,'types_lower_count':v-400,'top10_upper_count':mass+400}
            assert result['native_limits'][ed]==limits
            good_type=types>=v-400;good_top=top<=mass+400
            expected={**limits,'types_not_excluded':good_type,'concentration_not_excluded':good_top,'not_excluded':good_type and good_top}
            assert r['reader_conditions'][ed]==expected
            oks.append(expected['not_excluded'])
            if not good_type:failure_conditions.append([book,ed,'types'])
            if not good_top:failure_conditions.append([book,ed,'top10'])
        assert r['not_excluded']==all(oks)
        sr=receipt['books'][book]
        assert sr['sample_recipe_ranges']==ranges and sr['full_recipes']==len(source[book]) and sr['full_words']==full_word_count
        assert sr['ordered_sample_sha256']==hashlib.sha256(json.dumps(sample,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        assert sr['frequency_table_sha256']==hashlib.sha256(json.dumps(freq,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        total_recipes+=len(source[book]);total_words+=full_word_count
    assert result['source_recipes']==total_recipes and result['source_words']==total_words
    ok=not failure_conditions;assert result['all_books_not_excluded']==ok
    assert result['status']==('WHOLE_WORD_TWO_ALIAS_NOT_EXCLUDED' if ok else 'WHOLE_WORD_TWO_ALIAS_CAPACITY_EXCLUDED')
    validation={'status':'PASS','scope':'Exact projected whole-word source sample, optimistic two-alias bound and fixed decision only',
       'same_author':True,'native_model_validated':False,'partition_fixtures':partition_checks,'merge_fixtures':merge_checks,
       'checked_books':4,'sample_words_per_book':8000,'source_recipes':total_recipes,'source_words':total_words,
       'failed_book_reader_directions':failure_conditions,'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps({k:v for k,v in validation.items() if k!='failed_book_reader_directions'},indent=2))
if __name__=='__main__':main()
