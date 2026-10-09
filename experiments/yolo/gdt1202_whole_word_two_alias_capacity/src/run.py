"""Optimistic capacity, at most two spellings per complete source word."""
from pathlib import Path
from collections import Counter
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
SOURCE=ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
BOOKS=('b4','w1','bs1','gr1');N=8000

def save(name,data):(A/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def native_limits(targets):
    out={}
    for ed,t in targets.items():
        assert t['tokens']==N
        v=round(t['type_ratio']*N);top=round(t['top10_share']*N)
        assert abs(v/N-t['type_ratio'])<1e-12 and abs(top/N-t['top10_share'])<1e-12
        out[ed]={'native_types':v,'native_top10_count':top,'types_lower_count':v-400,'top10_upper_count':top+400}
    return out

def main():
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    source=json.loads(SOURCE.read_text());limits=native_limits(json.loads(TARGET.read_text())['targets'])
    tables={};receipts={};books={}
    for book in BOOKS:
        words=[w for recipe in source[book] for w in recipe['words']]
        assert len(words)>=N and all(isinstance(w,str) and w for w in words)
        sample=words[:N];counts=Counter(sample);cells=[];table=[]
        for word,n in sorted(counts.items()):
            bins=[(n+1)//2,n//2];table.append({'word':word,'count':n,'balanced_two_counts':bins})
            cells.extend((cnt,word,alias) for alias,cnt in enumerate(bins) if cnt)
        cells.sort(key=lambda c:(-c[0],c[1],c[2]));tmax=sum(min(n,2) for n in counts.values());cmin=sum(c[0] for c in cells[:10])
        assert tmax==len(cells) and sum(c[0] for c in cells)==N
        tests={ed:{**lims,'types_not_excluded':tmax>=lims['types_lower_count'],
            'concentration_not_excluded':cmin<=lims['top10_upper_count']} for ed,lims in limits.items()}
        for row in tests.values():row['not_excluded']=row['types_not_excluded'] and row['concentration_not_excluded']
        books[book]={'sample_words':N,'source_types':len(counts),'source_singletons':sum(n==1 for n in counts.values()),
            'source_top10_count':sum(sorted(counts.values(),reverse=True)[:10]),
            'two_alias_types_upper_count':tmax,'two_alias_top10_lower_count':cmin,
            'two_alias_top10_lower_share':cmin/N,'reader_conditions':tests,'not_excluded':all(t['not_excluded'] for t in tests.values()),
            'balanced_top10_cells':[{'word':w,'alias_index':i,'count':n} for n,w,i in cells[:10]]}
        ranges=[];remaining=N
        for i,recipe in enumerate(source[book]):
            k=min(remaining,len(recipe['words']))
            if k:ranges.append({'recipe_index':i,'first_word_index':0,'sample_count':k,'stored_recipe_words':len(recipe['words'])})
            remaining-=k
            if remaining==0:break
        assert remaining==0
        receipts[book]={'full_recipes':len(source[book]),'full_words':len(words),'sample_recipe_ranges':ranges,
            'ordered_sample_sha256':hashlib.sha256(json.dumps(sample,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),
            'frequency_table_sha256':hashlib.sha256(json.dumps(table,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
        tables[book]=table
    ok=all(r['not_excluded'] for r in books.values())
    result={'experiment':'GDT1202','status':'WHOLE_WORD_TWO_ALIAS_NOT_EXCLUDED' if ok else 'WHOLE_WORD_TWO_ALIAS_CAPACITY_EXCLUDED',
        'books':books,'native_limits':limits,'all_books_not_excluded':ok,
        'source_recipes':sum(x['full_recipes'] for x in receipts.values()),'source_words':sum(x['full_words'] for x in receipts.values()),
        'scope':'Necessary optimistic bound on four exposed source projections only; no full writer, native meanings, general language exclusion or independent confirmation.'}
    save('FREQUENCIES.json',tables);save('SOURCE_RECEIPT.json',{'source_file':str(SOURCE.relative_to(ROOT)),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'target_summary_file':str(TARGET.relative_to(ROOT)),
        'target_summary_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'books':receipts})
    save('RESULT.json',result);save('RUN_RECEIPT.json',{'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print(json.dumps({'status':result['status'],'limits':limits,'books':{b:{k:v for k,v in r.items() if k not in ('reader_conditions','balanced_top10_cells')} for b,r in books.items()}},indent=2))
if __name__=='__main__':main()
