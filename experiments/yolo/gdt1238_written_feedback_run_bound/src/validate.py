#!/usr/bin/env python3
"""Independent run boundaries, full raw source projection and fixture enumeration."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip, hashlib, html, json, re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
s=json.loads((D/'src/SPEC.json').read_text());result=json.loads((A/'RESULT.json').read_text())
for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
assert json.loads((ROOT/s['native_validation']).read_text())['status']=='PASS'

def spans(seq):
    stops=[0]+[i for i in range(1,len(seq))if seq[i]!=seq[i-1]]+[len(seq)]
    return [{'start':a,'glyph':seq[a],'length':b-a}for a,b in zip(stops,stops[1:])]

# Reconstruct the previously defined lossy edition from all raw chapter files.
old=json.loads((ROOT/s['source_spec']).read_text())
point=re.compile('[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]')
finals={'ך':'כ','ם':'מ','ן':'נ','ף':'פ','ץ':'צ'};sections=[]
for chapter,path in enumerate(old['hebrew_files'],1):
    obj=json.loads((ROOT/path).read_text());assert obj['sections']==[str(chapter)]and not obj['warnings']
    versions=obj['versions'];assert len(versions)==1 and versions[0]['versionTitle']=='Torat Emet 363'
    for j,raw in enumerate(versions[0]['text'],1):
        text=html.unescape(re.sub(r'</?small(?:\s[^>]*)?>','',raw));assert '<'not in text and '>'not in text
        text=point.sub('',text).replace('"','').replace("'",'')
        words=[''.join(finals.get(c,c)for c in w)for w in re.findall('[א-ת]+',text)]
        assert words;sections.append({'ref':f'{chapter}:{j}','words':words})
assert sections==json.loads((ROOT/s['source_projection']).read_text())['source_sections']
source_records=[];hist=Counter();word_hist=Counter();words=[]
for section in sections:
    for i,word in enumerate(section['words']):
        words.append(word);records=spans(word);word_hist[max(x['length']for x in records)]+=1
        for run in records:
            hist[run['length']]+=1
            source_records.append({'ref':section['ref'],'word_index':i,'word':word,**run})
        assert sorted(r['length']for r in spans(word[::-1]))==sorted(r['length']for r in records)
maximum=max(hist)
expected={'words':len(words),'sections':len(sections),'letters':sum(map(len,words)),'max_run':maximum,
          'run_histogram':{str(k):v for k,v in sorted(hist.items())},'word_max_histogram':{str(k):v for k,v in sorted(word_hist.items())},
          'maximal_witnesses':[r for r in source_records if r['length']==maximum]}
assert result['source']==expected
assert json.loads(gzip.decompress((A/'SOURCE_RUNS.json.gz').read_bytes()))==[r for r in source_records if r['length']>=2]
assert len(words)==6288 and len(sections)==71 and sum(map(len,words))==24668

# Independent source generation uses integer bit strings and XOR row switches.
fixtures=json.loads((A/'FIXTURES.json').read_text());cases=0;plus_one=0
for flips in [(0,0),(0,1),(1,0),(1,1)]:
    for start in range(2):
        for length in range(1,s['fixture_max_length']+1):
            for number in range(1<<length):
                source=[int(x)for x in f'{number:0{length}b}'];state=start;out=[]
                for x in source:state=x^flips[state];out.append(state)
                sx=max(r['length']for r in spans(source));sy=max(r['length']for r in spans(out))
                assert sy<=sx+1
                for run in spans(out):
                    if run['length']>=2:
                        tail=source[run['start']+1:run['start']+run['length']]
                        assert all(c==tail[0]for c in tail)
                cases+=1;plus_one+=sy==sx+1
assert fixtures['binary_permutation_cases']==cases
assert fixtures['attained_plus_one_cases']==plus_one and plus_one>0
assert fixtures['max_source_length']==s['fixture_max_length']
null=fixtures['noninjective_null']
assert max(x['length']for x in spans(null['output']))>max(x['length']for x in spans(null['source']))+1
assert null['violates']
example=fixtures['manual_edge_example'];state=example['entry'];out=[]
for x in example['source']:state=example['rows'][state][x];out.append(state)
assert out==example['output'] and out==[0,0,0,0]

cache=json.loads(gzip.decompress((ROOT/s['native_groups']).read_bytes()))
saved=json.loads(gzip.decompress((A/'NATIVE_RUNS.json.gz').read_bytes()))
assert set(cache)==set(saved)==set(s['readers']);excluded=0

def forms(rows):
    by_word=defaultdict(list)
    for row in rows:by_word[row['ivtff_group_raw']].append(row)
    out=[]
    for word in sorted(by_word):
        rs=by_word[word]
        leaves={re.match('f[0-9]+',r['page'])[0]for r in rs}
        out.append({'word':word,'tokens':len(rs),'physical_leaves':len(leaves),
                    'all_loci':[{k:r[k]for k in ['page','locus','id','source_group_index']}for r in rs]})
    return out

for edition in s['readers']:
    rows=cache[edition];assert len(rows)==s['native_expected_groups'][edition]
    records=[];counts=Counter();wm=Counter();per_row=[];units_total=0
    assert len({r['id']for r in rows})==len(rows)
    for r in rows:
        assert r['edition']==edition and r['kind']=='P'
        assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
        assert not r['page'].startswith(('f84','f116v'))
        units=r['units'];assert ''.join(units)==r['ivtff_group_raw'] and set(units)<=set(s['working_units'])
        rr=spans(units);m=max(x['length']for x in rr);per_row.append(m);wm[m]+=1;units_total+=len(units)
        for span in rr:
            counts[span['length']]+=1
            if span['length']>=2:
                records.append({k:r[k]for k in ['edition','id','page','locus','source_group_index','ivtff_group_raw','units']}|span)
    assert records==saved[edition]
    peak=max(counts);peak_rows=[row for row,m in zip(rows,per_row)if m==peak]
    bad=[row for row,m in zip(rows,per_row)if m>maximum+1]
    decision='DEOT_FORM_ENVELOPE_EXCLUDES_SOME_GROUPS'if bad else'RUN_BOUND_INCONCLUSIVE'
    expected={'groups':len(rows),'units':units_total,'run_histogram':{str(k):v for k,v in sorted(counts.items())},
              'word_max_histogram':{str(k):v for k,v in sorted(wm.items())},'max_run':peak,'necessary_source_max_run':max(1,peak-1),
              'maximum_bearing_forms':forms(peak_rows),'source_output_max_bound':maximum+1,
              'offending_groups':len(bad),'offending_forms':forms(bad),'decision':decision}
    assert result['readers'][edition]==expected;excluded+=bool(bad)
status='DEOT_FORM_ENVELOPE_EXCLUDED_ALL_READINGS'if excluded==3 else'SOME_READINGS_OUTSIDE_DEOT_ENVELOPE'if excluded else'RUN_BOUND_INCONCLUSIVE_ALL_READINGS'
assert result['status']==status
validation={'experiment':'GDT1238','status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),
            'checks':['frozen input/script hashes','all7rawchapters reconstruct the fixed projection','independent maximal-run boundary reconstruction for every word/group','full run records and per-form support','source reversal invariance','exhaustive binary feedback permutations and manual edge case','noninjective counterexample','all three per-reader source-envelope decisions'],
            'binary_cases':cases,'source_tokens':len(words),'native_groups':{ed:len(cache[ed])for ed in s['readers']},
            'limits':'Separate implementation by the same root author; producer checked proof before counts. No independent native transcription or semantics.'}
(A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps(validation,indent=2))
