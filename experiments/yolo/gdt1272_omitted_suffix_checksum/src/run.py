import collections, datetime, hashlib, json, math, statistics, sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
SOURCE='experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json'
NATIVE='experiments/yolo/gdt1229_fixed_wordbook_branch_rank/artifacts/RESULT.json'
SPEC='experiments/yolo/gdt1229_fixed_wordbook_branch_rank/src/SPEC.json'
ALPHABET='אבגדהוזחטיכלמנסעפצקרשת'

def key(word, alphabet):
    rank={x:i+1 for i,x in enumerate(alphabet)}
    return (word[:2],len(word)-2,sum((i+1)*rank[c] for i,c in enumerate(word[2:]))%19)

def buckets(lexicon, alphabet):
    d=collections.defaultdict(list)
    for w in sorted(lexicon):
        if len(w)>=4:d[key(w,alphabet)].append(w)
    return dict(d)

def encode(word, lexicon, groups, alphabet):
    indices=[alphabet.index(c) for c in word]
    k=key(word,alphabet) if len(word)>=4 else None
    if word in lexicon and k and indices[0]!=21 and k[1]<=21 and len(groups[k])==1:
        return indices[:2]+[k[1],k[2]], 'short'
    return [21]+indices,'literal'

def decode(code, groups, alphabet):
    if not code or any(not isinstance(c,int) or c<0 or c>=22 for c in code):raise ValueError('label')
    if code[0]==21:
        if len(code)==1:raise ValueError('empty literal')
        return ''.join(alphabet[c] for c in code[1:])
    if len(code)!=4 or code[2]<2 or code[3]>=19:raise ValueError('short shape')
    k=(''.join(alphabet[c] for c in code[:2]),code[2],code[3]); candidates=groups.get(k,[])
    if len(candidates)!=1:raise ValueError('ambiguous or absent')
    return candidates[0]

def metrics(words):
    n=len(words); lens=[len(w) for w in words]; types=collections.Counter(tuple(w) for w in words)
    glyphs=collections.Counter(x for w in words for x in w); pairs=collections.Counter((a,b) for w in words for a,b in zip(w,w[1:])); before=collections.Counter()
    for (a,b),c in pairs.items():before[a]+=c
    total=sum(glyphs.values()); npairs=sum(pairs.values())
    return {'mean_length':statistics.mean(lens),'sd_length':statistics.pstdev(lens),'top10_share':sum(c for _,c in types.most_common(10))/n,'type_ratio':len(types)/n,'glyph_entropy':-sum(c/total*math.log2(c/total) for c in glyphs.values()),'conditional_entropy':-sum(c/npairs*math.log2(c/before[a]) for (a,b),c in pairs.items())}

def controls():
    abc='ABCDEFGHIJKLMNOPQRSTUV'; lex=set(['AACA','AAAB','ABCD','VABC','A','AB','ABC']); groups=buckets(lex,abc)
    assert key('AACA',abc)==key('AAAB',abc)==('AA',2,5)
    records=[]
    for w in sorted(lex|{'BAAA'}):
        code,mode=encode(w,lex,groups,abc);assert decode(code,groups,abc)==w
        records.append({'word':w,'code':code,'mode':mode})
    assert encode('ABCD',lex,groups,abc)==([0,1,2,11],'short')
    assert all(encode(w,lex,groups,abc)[1]=='literal' for w in ['AACA','AAAB','VABC','BAAA','A','AB','ABC'])
    rejected=0
    for c in [[],[21],[0,0,2,5],[0,1,1,11],[0,1,2,19],[0,1,2],[-1],[22]]:
        try:decode(c,groups,abc)
        except ValueError:rejected+=1
        else:raise AssertionError(c)
    out={'status':'PASS','records':records,'malformed_rejected':rejected}
    (P/'artifacts/CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for f,h in lock['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
    source=json.loads((ROOT/SOURCE).read_text()); native=json.loads((ROOT/NATIVE).read_text()); tolerance=json.loads((ROOT/SPEC).read_text())['metrics']
    words=[w for s in source['source_sections'] for w in s['words']]; assert len(words)==6288
    lex=set(words); groups=buckets(lex,ALPHABET); payload=[]; flat=[]; modes=collections.Counter(); pertype=[]
    for w in sorted(lex):
        code,mode=encode(w,lex,groups,ALPHABET)
        pertype.append({'word':w,'code':code,'mode':mode})
    for section in source['source_sections']:
        enc=[]
        for w in section['words']:
            code,mode=encode(w,lex,groups,ALPHABET);assert decode(code,groups,ALPHABET)==w
            enc.append(code);flat.append(code);modes[mode]+=1
        payload.append({'ref':section['ref'],'words':enc})
    assert sorted(collections.Counter(words).values())==sorted(collections.Counter(tuple(w) for w in flat).values())
    met=metrics(flat); totals=collections.defaultdict(lambda:{'samples':0,'joint':0,**{k:0 for k in met}}); cells=[]
    for cell in native['cells']:
        row={k:cell[k] for k in ['reader','field','value','eligible_groups','capacity']}; checks=[]
        for sample in cell.get('samples',[]):
            within={k:abs(met[k]-sample['metrics'][k])<=(amount*sample['metrics'][k] if mode=='relative' else amount) for k,(mode,amount) in tolerance.items()}
            joint=all(within.values());checks.append({'seed':sample['seed'],'sample_ids_sha256':sample['sample_ids_sha256'],'within':within,'joint':joint})
            t=totals[cell['reader']];t['samples']+=1;t['joint']+=joint
            for k,v in within.items():t[k]+=v
        row['comparisons']=checks;cells.append(row)
    collision_buckets=[{'prefix':k[0],'suffix_length':k[1],'checksum':k[2],'words':v} for k,v in sorted(groups.items()) if len(v)>1]
    result={'status':'FIXED_CHECKSUM_SCREEN_EXCLUDED_ALL_READINGS' if all(t['joint']==0 for t in totals.values()) else 'NECESSARY_SCREEN_SURVIVES_ONLY', 'source_words':len(words),'source_sections':len(payload),'wordbook_types':len(lex),'wordbook_letters':sum(map(len,lex)),'indexed_buckets':len(groups),'collision_buckets':len(collision_buckets),'collision_types':sum(len(x['words']) for x in collision_buckets),'collision_tokens':sum(len(w)>=4 and len(groups[key(w,ALPHABET)])>1 for w in words),'source_letters':sum(map(len,words)),'escape_only_letters':sum(map(len,words))+len(words),'encoded_letters':sum(map(len,flat)),'mode_tokens':dict(modes),'mode_types':dict(collections.Counter(x['mode'] for x in pertype)),'metrics':met,'reader_results':dict(totals),'cells':cells,'length_histogram':sorted(collections.Counter(map(len,flat)).items()),'canonical_frequency_multiset_equal':True}
    for name,obj in [('CIPHER',payload),('WORDBOOK',pertype),('COLLISIONS',collision_buckets),('RESULT',result)]:
        (P/f'artifacts/{name}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    (P/'artifacts/RUN_RECEIPT.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'lock_sha256':hashlib.sha256((P/'src/REGISTRATION_LOCK.json').read_bytes()).hexdigest()},indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['cells','length_histogram']},indent=2))
if __name__=='__main__':
    controls() if '--controls' in sys.argv else main()
