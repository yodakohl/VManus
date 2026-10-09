import json,gzip,hashlib,math,statistics,itertools,sys,datetime
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
ALPHABET='אבגדהוזחטיכלמנסעפצקרשת'
GLYPHS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
SOURCE=ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json'
NATIVE=ROOT/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/RESULT.json'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def encode(words,alphabet):
    rank={c:i for i,c in enumerate(alphabet)};old=[];out=[]
    for word in words:
        now=[rank[c] for c in word];out.append([(v-(old[j] if j<len(old) else 0))%len(alphabet) for j,v in enumerate(now)]);old=now
    return out

def decode(words,alphabet):
    old=[];out=[]
    for word in words:
        now=[(v+(old[j] if j<len(old) else 0))%len(alphabet) for j,v in enumerate(word)];out.append(''.join(alphabet[v] for v in now));old=now
    return out

def controls():
    alphabet='ABC';words=[''.join(w) for n in range(1,4) for w in itertools.product(alphabet,repeat=n)];count=0
    for n in range(1,4):
        for seq in itertools.product(words,repeat=n):
            assert decode(encode(seq,alphabet),alphabet)==list(seq);count+=1
    example=['ABC','AC','ACDE','ACDE'];coded=encode(example,'ABCDE');assert coded==[[0,1,2],[0,1],[0,0,3,4],[0,0,0,0]]
    assert decode(coded,'ABCDE')==example
    assert encode(['C'],'ABC')==[[2]] # fresh reset, not inherited previous word
    return dict(status='PASS',exhaustive_variable_length_sequences=count,example_source=example,example_output=coded)

def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for path,h in lock['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    src=json.loads(SOURCE.read_text());old=json.loads(NATIVE.read_text());coded=[];allwords=[];receipts=[]
    for section in src['source_sections']:
        words=section['words'];enc=encode(words,ALPHABET);assert decode(enc,ALPHABET)==words;assert encode(decode(enc,ALPHABET),ALPHABET)==enc
        coded.append(dict(ref=section['ref'],words=enc));allwords.extend(tuple(w) for w in enc)
        receipts.append(dict(ref=section['ref'],word_count=len(words),source_sha256=digest(words),encoded_sha256=digest(enc),roundtrip=True))
    lengths=[len(w) for w in allwords];pairs=Counter((a,b) for w in allwords for a,b in zip(w,w[1:]));prev=Counter()
    for (a,b),n in pairs.items():prev[a]+=n
    total=sum(pairs.values());h=-sum(n/total*math.log2(n/prev[a]) for (a,b),n in pairs.items())
    metrics=dict(mean_length=statistics.mean(lengths),sd_length=statistics.pstdev(lengths),conditional_entropy=h)
    types=Counter(allwords);diag=dict(word_types=len(types),type_share=len(types)/len(allwords),top10_count=sum(n for _,n in types.most_common(10)),top10_share=sum(n for _,n in types.most_common(10))/len(allwords))
    cells=[];totals=defaultdict(lambda:dict(samples=0,joint=0,mean_length=0,sd_length=0,conditional_entropy=0))
    for cell in old['cells']:
        row={k:cell[k] for k in ['reader','field','value','eligible_groups','capacity']};checks=[]
        for sample in cell.get('samples',[]):
            target=sample['metrics'];within={k:abs(metrics[k]-target[k])<=({'mean_length':.2,'sd_length':.25}[k]*target[k] if k!='conditional_entropy' else .3) for k in metrics};joint=all(within.values())
            checks.append(dict(seed=sample['seed'],sample_ids_sha256=sample['sample_ids_sha256'],within=within,joint=joint))
            t=totals[cell['reader']];t['samples']+=1;t['joint']+=int(joint)
            for k,v in within.items():t[k]+=int(v)
        row['comparisons']=checks;cells.append(row)
    excluded=all(v['joint']==0 for v in totals.values())
    result=dict(status='FIXED_WORD_COLUMN_SCREEN_EXCLUDED_ALL_READINGS' if excluded else 'NECESSARY_SCREEN_SURVIVES_ONLY',source_words=len(allwords),source_sections=len(coded),source_letters=sum(lengths),within_word_pairs=total,metrics=metrics,frequency_diagnostics=diag,length_histogram=sorted(Counter(lengths).items()),pair_counts=[[a,b,n] for (a,b),n in sorted(pairs.items())],reader_results=dict(totals),cells=cells,section_receipts=receipts)
    (P/'artifacts/CIPHER.json.gz').write_bytes(gzip.compress(json.dumps(coded,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    (P/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (P/'artifacts/RUN_RECEIPT.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lock_sha256=hashlib.sha256((P/'src/REGISTRATION_LOCK.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['cells','pair_counts','section_receipts','length_histogram']},indent=2))
if __name__=='__main__':
    if '--controls' in sys.argv:
        out=controls();(P/'artifacts/CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
    else:main()
