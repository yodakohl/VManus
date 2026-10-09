"""Independent same-author stream-cut implementation and source reconstruction."""
from pathlib import Path
from collections import defaultdict
from itertools import product
import hashlib,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';N=8000

def load(p):return json.loads(p.read_text())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def by_cuts(words):
    stream=[];cuts=[]
    for w in words:
        stream.extend(map(ord,w));cuts.append(len(stream)+1)
    stream.append(-1);out=[];start=0
    for stop in cuts:out.append(stream[start:stop]);start=stop
    assert start==len(stream) and all(out)
    return out

def reverse_stream(groups):
    stream=[];original_stops=[]
    for g in groups:
        assert g;stream.extend(g);original_stops.append(len(stream)-1)
    assert stream[-1]==-1 and stream.count(-1)==1
    stream.pop();words=[];start=0
    for stop in original_stops:
        assert stop>start;words.append(''.join(map(chr,stream[start:stop])));start=stop
    assert start==len(stream)
    return words

def main():
    lock=load(A/'REGISTRATION_LOCK.json')
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert load(A/'RUN_RECEIPT.json')['runner_sha256']==hashlib.sha256((D/'src/run.py').read_bytes()).hexdigest()
    receipt=load(A/'SOURCE_RECEIPT.json');source=load(ROOT/receipt['source_file']);target=load(ROOT/receipt['target_summary_file'])['targets']
    for name in ['source','target_summary']:
        assert hashlib.sha256((ROOT/receipt[name+'_file']).read_bytes()).hexdigest()==receipt[name+'_sha256']
    saved=load(A/'ENCODED.json');freq=load(A/'FREQUENCIES.json');result=load(A/'RESULT.json');count_recipes=0;count_words=0;allpass=True
    for book in ('b4','w1','bs1','gr1'):
        sequences=[];flatwords=[];ranges=[];remaining=N;table=defaultdict(int);samples=[];units=0
        assert len(saved[book])==len(source[book])
        for i,recipe in enumerate(source[book]):
            words=recipe['words'];g=by_cuts(words);assert g==saved[book][i];assert reverse_stream(g)==words
            sequences.append(g);flatwords.extend(words);count_recipes+=1;count_words+=len(words);units+=sum(map(len,g))
            # Sequential emitted stream is self-delimited by its END unit.
            assert g[-1][-1]==-1 and all(-1 not in x for x in g[:-1])
            k=min(remaining,len(g))
            if k:ranges.append({'recipe_index':i,'first_group_index':0,'sample_count':k,'recipe_groups':len(g),'next_word_lookahead_outside_sample':k<len(g)})
            for j in range(k):samples.append(g[j]);table[tuple(g[j])]+=1
            remaining-=k
        assert remaining==0 and len(samples)==N
        got=result['books'][book];n_types=len(table);top=sum(sorted(table.values())[-10:]);base=defaultdict(int)
        for w in flatwords[:N]:base[w]+=1
        assert freq[book]==[{'units':list(g),'count':n} for g,n in sorted(table.items())]
        expected={'sample_groups':N,'types':n_types,'type_ratio':n_types/N,'top10_count':top,'top10_share':top/N,
            'source_baseline_types':len(base),'source_baseline_top10_count':sum(sorted(base.values())[-10:]),
            'end_units_in_sample':sum(-1 in g for g in samples),'sample_max_abstract_group_length':max(map(len,samples))}
        for k,v in expected.items():assert got[k]==v,(book,k)
        bookpass=True
        for ed,t in target.items():
            assert t['tokens']==N;v=round(N*t['type_ratio']);c=round(N*t['top10_share']);lim={'types':[v-400,v+400],'top10':[c-400,c+400],'native_types':v,'native_top10_count':c}
            assert result['native_limits'][ed]==lim
            ts={'types_pass':abs(n_types-v)<=400,'top10_pass':abs(top-c)<=400};ts['pass']=all(ts.values());assert got['reader_conditions'][ed]==ts;bookpass=bookpass and ts['pass']
        assert got['pass']==bookpass;allpass=allpass and bookpass
        r=receipt['books'][book];expected_r={'recipes':len(source[book]),'source_words':len(flatwords),'source_character_units':sum(map(len,flatwords)),
            'emitted_units':units,'emitted_groups':len(flatwords),'end_units':len(source[book]),'sample_recipe_ranges':ranges,'sample_sha256':digest(samples),'encoded_sha256':digest(sequences)}
        assert r==expected_r and units==r['source_character_units']+r['recipes']
    fixture_count=0;small=['a','b','aa','ab','ba','bb']
    for length in range(1,5):
        for words in product(small,repeat=length):
            assert reverse_stream(by_cuts(words))==list(words);fixture_count+=1
    def stripped(words):return [tuple(x for x in g if x!=-1) for g in by_cuts(words) if any(x!=-1 for x in g)]
    assert stripped(['a','b'])==stripped(['ab']) and by_cuts(['a','b'])!=by_cuts(['ab'])
    assert result['complete_recipe_roundtrips']==count_recipes and result['all_books_pass']==allpass
    assert result['status']==('SHIFT_ONE_FREQUENCY_SCREEN_PASS' if allpass else 'SHIFT_ONE_FREQUENCY_SCREEN_FAIL')
    out={'status':'PASS','same_author':True,'native_model_validated':False,'complete_recipe_roundtrips':count_recipes,'complete_source_words':count_words,
        'small_exhaustive_roundtrips':fixture_count,'lost_terminal_collision_confirmed':True,'all_fixed_source_conditions_pass':allpass,
        'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Source-preserving regrouping, source/sample receipts, counts and registered decisions only'}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
