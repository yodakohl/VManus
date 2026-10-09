#!/usr/bin/env python3
"""Necessary feedback run capacity; no table fitting or native decoding."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import groupby, permutations, product
import gzip, hashlib, json, re

D=Path(__file__).resolve().parents[1]; ROOT=D.parents[2]; A=D/'artifacts'

def save(name, value):
    data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    (A/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)

def runs(seq):
    offset=0
    for glyph, group in groupby(seq):
        size=sum(1 for _ in group)
        yield {'start':offset,'glyph':glyph,'length':size}
        offset+=size

def fixtures(max_length):
    cases=0; strict=0
    for row0,row1 in product(list(permutations(range(2))),repeat=2):
        table=[row0,row1]
        for entry in range(2):
            for n in range(1,max_length+1):
                for source in product(range(2),repeat=n):
                    state=entry; output=[]
                    for x in source:
                        state=table[state][x]; output.append(state)
                    sr=max(r['length'] for r in runs(source)); yr=max(r['length'] for r in runs(output))
                    assert yr<=sr+1
                    assert max(r['length'] for r in runs(source[::-1]))==sr
                    for r in runs(output):
                        if r['length']>=2:
                            tail=source[r['start']+1:r['start']+r['length']]
                            assert len(set(tail))==1
                    cases+=1; strict+=yr==sr+1
    source=[0,1]*4; output=[0]*8
    assert max(r['length'] for r in runs(output))>max(r['length'] for r in runs(source))+1
    return {'binary_permutation_cases':cases,'attained_plus_one_cases':strict,
            'max_source_length':max_length,'noninjective_null':{'source':source,'output':output,'violates':True},
            'manual_edge_example':{'rows':[[1,0],[0,1]],'entry':1,'source':[0,1,1,1],'output':[0,0,0,0]}}

def supports(rows):
    grouped=defaultdict(list)
    for r in rows:grouped[r['ivtff_group_raw']].append(r)
    return [{'word':w,'tokens':len(rs),'physical_leaves':len({re.match(r'f\d+',r['page']).group() for r in rs}),
             'all_loci':[{'page':r['page'],'locus':r['locus'],'id':r['id'],'source_group_index':r['source_group_index']}for r in rs]}
            for w,rs in sorted(grouped.items())]

def main():
    assert not(A/'RESULT.json').exists()
    started=datetime.now(timezone.utc).isoformat(); s=json.loads((D/'src/SPEC.json').read_text())
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert json.loads((ROOT/s['native_validation']).read_text())['status']=='PASS'
    save('FIXTURES.json',fixtures(s['fixture_max_length']))
    source=json.loads((ROOT/s['source_projection']).read_text())['source_sections']
    source_runs=[]; source_hist=Counter(); source_word_max=Counter(); word_count=0; letters=0
    source_max_seen=0; source_maximal=[]
    for section in source:
        for index,word in enumerate(section['words']):
            assert word and set(word)<=set(s['source_alphabet'])
            rs=list(runs(word)); word_count+=1; letters+=len(word)
            source_word_max[max(r['length'] for r in rs)]+=1
            for r in rs:
                source_hist[r['length']]+=1
                record={'ref':section['ref'],'word_index':index,'word':word,**r}
                if r['length']>=2:source_runs.append(record)
                if r['length']>source_max_seen:source_max_seen=r['length'];source_maximal=[]
                if r['length']==source_max_seen:source_maximal.append(record)
    assert word_count==6288 and len(source)==71 and letters==24668
    source_max=max(source_hist)
    source_summary={'words':word_count,'sections':len(source),'letters':letters,'max_run':source_max,
                    'run_histogram':dict(sorted(source_hist.items())),'word_max_histogram':dict(sorted(source_word_max.items())),
                    'maximal_witnesses':source_maximal}
    save('SOURCE_RUNS.json.gz',source_runs)
    cache=json.loads(gzip.decompress((ROOT/s['native_groups']).read_bytes()))
    assert set(cache)==set(s['readers'])
    reader_results={}; all_native={}
    for ed in s['readers']:
        rows=cache[ed]; assert len(rows)==s['native_expected_groups'][ed]
        assert len({r['id']for r in rows})==len(rows)
        records=[]; hist=Counter(); word_hist=Counter(); maxima={}
        for r in rows:
            assert r['edition']==ed and r['kind']=='P'
            assert not r['page'].startswith(('f84','f116v'))
            assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
            units=r['units']; assert units and set(units)<=set(s['working_units'])
            assert ''.join(units)==r['ivtff_group_raw']
            rr=list(runs(units)); m=max(x['length'] for x in rr); maxima[r['id']]=m; word_hist[m]+=1
            for x in rr:
                hist[x['length']]+=1
                if x['length']>=2:
                    records.append({k:r[k]for k in ['edition','id','page','locus','source_group_index','ivtff_group_raw','units']}|x)
        maximum=max(hist)
        maximum_rows=[r for r in rows if maxima[r['id']]==maximum]
        offending=[r for r in rows if maxima[r['id']]>source_max+1]
        reader_results[ed]={'groups':len(rows),'units':sum(map(lambda r:len(r['units']),rows)),
            'run_histogram':dict(sorted(hist.items())),'word_max_histogram':dict(sorted(word_hist.items())),
            'max_run':maximum,'necessary_source_max_run':max(1,maximum-1),
            'maximum_bearing_forms':supports(maximum_rows),'source_output_max_bound':source_max+1,
            'offending_groups':len(offending),'offending_forms':supports(offending),
            'decision':'DEOT_FORM_ENVELOPE_EXCLUDES_SOME_GROUPS'if offending else'RUN_BOUND_INCONCLUSIVE'}
        all_native[ed]=records
    save('NATIVE_RUNS.json.gz',all_native)
    excluded=sum(x['offending_groups']>0 for x in reader_results.values())
    status='DEOT_FORM_ENVELOPE_EXCLUDED_ALL_READINGS'if excluded==3 else'SOME_READINGS_OUTSIDE_DEOT_ENVELOPE'if excluded else'RUN_BOUND_INCONCLUSIVE_ALL_READINGS'
    result={'experiment':'GDT1238','status':status,'source':source_summary,'readers':reader_results,
            'claim_ceiling':s['claim_ceiling'],'comparison':'Per-form capacity only; no unequal-denominator frequency comparison or source/native alignment.'}
    save('RESULT.json',result)
    save('RUN_RECEIPT.json',{'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
        'new_native_raw_queries':0,'images_viewed':0,'tables_fitted':0,'fixed_native_cache_passes':1,'fixed_source_projection_passes':1})
    print(json.dumps({'status':status,'source_max_run':source_max,'readers':{ed:{k:x[k]for k in ['max_run','necessary_source_max_run','offending_groups','decision']}for ed,x in reader_results.items()}},indent=2))

if __name__=='__main__':main()
