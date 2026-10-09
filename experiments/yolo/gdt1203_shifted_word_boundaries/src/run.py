"""Fixed right-shift of source word boundaries, with a transmitted END unit."""
from pathlib import Path
from collections import Counter
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
SOURCE=ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
BOOKS=('b4','w1','bs1','gr1');N=8000;END=-1

def dump(name,data): (A/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def digest(data): return hashlib.sha256(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def encode(words):
    assert words and all(isinstance(w,str) and w for w in words)
    if len(words)==1:return [[ord(c) for c in words[0]]+[END]]
    out=[]
    for i,w in enumerate(words):
        body=w if i==0 else w[1:]
        out.append([ord(c) for c in body]+([ord(words[i+1][0])] if i+1<len(words) else [END]))
    assert all(out)
    return out

def decode(groups):
    assert groups and all(groups) and groups[-1][-1]==END
    assert sum(x==END for g in groups for x in g)==1
    if len(groups)==1:return [''.join(chr(x) for x in groups[0][:-1])]
    words=[''.join(chr(x) for x in groups[0][:-1])]
    for prev,g in zip(groups,groups[1:]): words.append(chr(prev[-1])+''.join(chr(x) for x in g[:-1]))
    assert all(words)
    return words

def main():
    lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets'];limits={}
    for ed,t in targets.items():
        assert t['tokens']==N
        v=round(t['type_ratio']*N);c=round(t['top10_share']*N)
        assert abs(v/N-t['type_ratio'])<1e-12 and abs(c/N-t['top10_share'])<1e-12
        limits[ed]={'types':[v-400,v+400],'top10':[c-400,c+400],'native_types':v,'native_top10_count':c}
    books={};encoded={};freq={};receipts={};total_roundtrips=0
    for book in BOOKS:
        encoded[book]=[];remaining=N;ranges=[];words=[]
        for i,recipe in enumerate(source[book]):
            g=encode(recipe['words']);assert decode(g)==recipe['words'];total_roundtrips+=1
            assert len(g)==len(recipe['words']);encoded[book].append(g);words.extend(recipe['words'])
            k=min(remaining,len(g))
            if k:ranges.append({'recipe_index':i,'first_group_index':0,'sample_count':k,'recipe_groups':len(g),'next_word_lookahead_outside_sample':k<len(g)})
            remaining-=k
        allgroups=[g for recipe in encoded[book] for g in recipe];assert len(allgroups)>=N and remaining==0
        sample=allgroups[:N];counts=Counter(map(tuple,sample));types=len(counts);top=sum(sorted(counts.values(),reverse=True)[:10]);base=Counter(words[:N])
        tests={ed:{'types_pass':lim['types'][0]<=types<=lim['types'][1],'top10_pass':lim['top10'][0]<=top<=lim['top10'][1]} for ed,lim in limits.items()}
        for t in tests.values():t['pass']=t['types_pass'] and t['top10_pass']
        books[book]={'sample_groups':N,'types':types,'type_ratio':types/N,'top10_count':top,'top10_share':top/N,
            'source_baseline_types':len(base),'source_baseline_top10_count':sum(sorted(base.values(),reverse=True)[:10]),
            'end_units_in_sample':sum(END in g for g in sample),'sample_max_abstract_group_length':max(map(len,sample)),
            'reader_conditions':tests,'pass':all(t['pass'] for t in tests.values())}
        freq[book]=[{'units':list(g),'count':n} for g,n in sorted(counts.items())]
        receipts[book]={'recipes':len(source[book]),'source_words':len(words),'source_character_units':sum(map(len,words)),
            'emitted_units':sum(len(g) for g in allgroups),'emitted_groups':len(allgroups),'end_units':len(source[book]),
            'sample_recipe_ranges':ranges,'sample_sha256':digest(sample),'encoded_sha256':digest(encoded[book])}
        assert receipts[book]['emitted_units']==receipts[book]['source_character_units']+receipts[book]['end_units']
    ok=all(r['pass'] for r in books.values());result={'experiment':'GDT1203','status':'SHIFT_ONE_FREQUENCY_SCREEN_PASS' if ok else 'SHIFT_ONE_FREQUENCY_SCREEN_FAIL',
        'books':books,'native_limits':limits,'all_books_pass':ok,'complete_recipe_roundtrips':total_roundtrips,
        'scope':'Fixed source regrouping and two necessary frequency metrics only; no rendered glyph writer, native meanings, independent holdout or historical attestation.'}
    dump('ENCODED.json',encoded);dump('FREQUENCIES.json',freq);dump('RESULT.json',result)
    dump('SOURCE_RECEIPT.json',{'source_file':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'target_summary_file':str(TARGET.relative_to(ROOT)),'target_summary_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'books':receipts})
    dump('RUN_RECEIPT.json',{'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
