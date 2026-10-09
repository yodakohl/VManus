#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict,Counter
from itertools import groupby
from datetime import datetime,timezone
import gzip,hashlib,json,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'

def save(name,obj):
    b=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
    (A/name).write_bytes(gzip.compress(b,mtime=0)if name.endswith('.gz')else b)

def index_words(words):
    index=defaultdict(list);by_length=Counter(map(len,words))
    for wi,word in enumerate(words):
        pos=0
        for glyph,run in groupby(word):
            size=sum(1 for _ in run)
            for a in range(pos,pos+size):
                for length in range(2,pos+size-a+1):index[(len(word),a,length)].append(wi)
            pos+=size
    return index,by_length

def summarize(records):
    bad=[x for x in records if not x['source_indices']];groups={x['id']:x for x in bad};by_word=defaultdict(list)
    for x in groups.values():by_word[x['ivtff_group_raw']].append(x)
    forms=[{'word':w,'groups':len(rs),'physical_leaves':len({re.match(r'f\d+',r['page'])[0]for r in rs}),
            'all_loci':[{k:x[k]for k in ['id','page','locus','source_group_index']}for x in rs]}
           for w,rs in sorted(by_word.items())]
    return {'runs':len(records),'supported_runs':len(records)-len(bad),'unsupported_runs':len(bad),
            'unsupported_groups':len(groups),'unsupported_forms':forms,
            'unsupported_by_reason':dict(sorted(Counter(x['reason']for x in bad).items())),
            'unsupported_by_run_length':dict(sorted(Counter(x['length']for x in bad).items())),
            'status':'SOURCE_ENVELOPE_EXCLUDED'if bad else'NECESSARY_ENVELOPE_INCONCLUSIVE'}

assert not(A/'RESULT.json').exists()
started=datetime.now(timezone.utc).isoformat();spec=json.loads((D/'src/SPEC.json').read_text())
for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
assert json.loads((ROOT/spec['prior_validation']).read_text())['status']=='PASS'
toy=['aaabc','baaac','abcaa','aaaaa','abcde'];idx,_=index_words(toy)
assert idx[(5,1,2)]==[0,1,3]and idx[(5,0,3)]==[0,3]and idx[(5,1,3)]==[1,3]
assert idx[(5,0,5)]==[3]and not idx[(5,1,5)]
save('FIXTURES.json',{'words':toy,'status':'PASS','covers':'inside longer maximal runs, different positions and absent windows'})
source=[]
for section in json.loads((ROOT/spec['source_projection']).read_text())['source_sections']:
    for i,w in enumerate(section['words']):source.append({'ref':section['ref'],'word_index':i,'word':w})
assert len(source)==6288
save('SOURCE_WORDS.json.gz',source)
native=json.loads(gzip.decompress((ROOT/spec['native_runs']).read_bytes()))
assert set(native)==set(spec['readers'])
all_records={};summaries={}
for orientation in ['LOGICAL','REVERSED']:
    words=[x['word']if orientation=='LOGICAL'else x['word'][::-1]for x in source]
    index,by_length=index_words(words);all_records[orientation]={};summaries[orientation]={}
    for ed in spec['readers']:
        records=[]
        for r in native[ed]:
            if r['length']<3:continue
            assert not r['page'].startswith(('f84','f116v'))
            n=len(r['units']);hits=index.get((n,r['start']+1,r['length']-1),[])
            reason='SUPPORTED_NECESSARY_ONLY'if hits else'NO_SOURCE_WORD_OF_LENGTH'if not by_length[n]else'NO_REQUIRED_POSITIONAL_RUN'
            records.append(r|{'source_indices':hits,'same_length_source_tokens':by_length[n],'reason':reason})
        all_records[orientation][ed]=records;summaries[orientation][ed]=summarize(records)
save('POSITIONAL_SUPPORT.json.gz',all_records)
status='ALL_READINGS_BOTH_ORIENTATIONS_EXCLUDED'if all(v['unsupported_runs']for eds in summaries.values()for v in eds.values())else'MIXED_OR_INCONCLUSIVE'
save('RESULT.json',{'experiment':'GDT1239','status':status,'source_words':len(source),'cases':summaries,'claim_ceiling':spec['claim_ceiling']})
save('RUN_RECEIPT.json',{'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'new_raw_queries':0,'images':0,'keys_fitted':0})
print(json.dumps({'status':status,'cases':{o:{ed:{k:v[k]for k in ['runs','unsupported_runs','unsupported_groups','unsupported_by_reason','unsupported_by_run_length']}for ed,v in es.items()}for o,es in summaries.items()}},indent=2))
