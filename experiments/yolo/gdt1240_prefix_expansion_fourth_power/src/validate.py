#!/usr/bin/env python3
"""Independent direct inequalities and source/proof replay; no runner imports."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
from itertools import product
import gzip,hashlib,json,sys
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'

def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.name.endswith('.gz')else b)

def enumerate_powers(w):
    answer=[]
    for left in range(1,len(w)):
        for right in range(left+4,len(w)):
            span=right-left
            if span%4:continue
            step=span//4
            if all(w[j]==w[j+step]for j in range(left,right-step)):
                answer.append({'start':left,'period':step,'X':w[:left],
                               'U':w[left:left+step],'Y':w[right:]})
    return sorted(answer,key=lambda x:(x['period'],x['start']))

def small_checks():
    count=0
    for n in range(13):
        for letters in product('ab',repeat=n):
            w=''.join(letters);got=enumerate_powers(w);expected=[]
            for m in range(1,n//4+1):
                for a in range(1,n-4*m):
                    x,u,y=w[:a],w[a:a+m],w[a+4*m:]
                    if x+u+u+u+u+y==w:expected.append((a,m))
            assert [(r['start'],r['period'])for r in got]==expected
            rev=enumerate_powers(w[::-1])
            assert sorted((len(w)-r['start']-4*r['period'],r['period'])for r in got)==sorted((r['start'],r['period'])for r in rev)
            count+=1
    assert enumerate_powers('iiii')==[]
    assert enumerate_powers('.iiii.')==[{'start':1,'period':1,'X':'.','U':'i','Y':'.'}]
    return count

def main():
    if '--fixtures'in sys.argv:
        print(json.dumps({'status':'PASS','binary_cases_and_reversal':small_checks()}));return
    spec=read(D/'src/SPEC.json');lock=read(A/'REGISTRATION_LOCK.json')
    for path,h in lock['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    fixture_count=small_checks();assert read(A/'FIXTURES.json')['exhaustive_binary_words']==fixture_count
    native=read(ROOT/spec['native_groups']);proof=read(A/'NATIVE_PROOF.json');events_checked=0
    for ed in spec['readers']:
        rows=native[ed];panel=proof[ed];saved={}
        for row in panel['proof_events']:
            eid=row['event_id'];parents=row['parents'];w=row['units']
            if parents is None:
                matches=[r for r in rows if r['units']==w]
                assert row['source_ids']==[r['id']for r in matches]
                assert row['occurrences']==len(matches)
                assert row['pages']==sorted({r['page']for r in matches})
                assert row['support']==len(row['pages'])
                for r in matches:
                    assert r['kind']=='P'and r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
                    assert not r['page'].startswith(('f84','f116v'))
                    assert ''.join(r['units'])==r['ivtff_group_raw']
            else:
                assert all(p in saved and p<eid for p in parents)
                a,b=[saved[p]for p in parents]
                assert a['units']+w==b['units']and w
                assert row['support']==min(a['support'],b['support'])
            saved[eid]=row;events_checked+=1
        for glyph,eid in panel['singleton_root_events'].items():
            assert saved[eid]['units']==[glyph]
            assert panel['singleton_selector_support'][glyph]==saved[eid]['support']
        assert set(panel['singleton_root_events'])==set(spec['required_singletons'])
        matches=[r for r in rows if r['ivtff_group_raw']==spec['native_witness']]
        assert matches==panel['whole_witness_occurrences']
        assert panel['witness_count']==len(matches)
        assert panel['witness_distinct_selectors']==len({r['page']for r in matches})
        for r in matches:
            assert r['units']==spec['native_witness_units']
            assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
    source_a=read(ROOT/spec['recipe_source']);source_b=read(ROOT/spec['hebrew_source'])
    hits=read(A/'SOURCE_POWER_WITNESSES.json');result=read(A/'RESULT.json');tokens_checked=0;decision=[]
    for collection in spec['collections']:
        records=source_b['source_sections']if collection=='deot'else source_a[collection]
        tokens=[];expected_hits=[]
        for ordinal,record in enumerate(records):
            if collection!='deot':assert record['words']==record['text'].split()
            assert all(isinstance(w,str)and w and not any(c.isspace()for c in w)for w in record['words'])
            rid=record['ref']if collection=='deot'else record['id']
            for wi,word in enumerate(record['words']):
                tokens.append(word);fs=enumerate_powers(word)
                if fs:
                    expected_hits.append({'record_index':ordinal,'record_id':rid,'word_index':wi,'word':word,'factorizations':fs})
                    for f in fs:assert f['X']and f['U']and f['Y']and f['X']+f['U']*4+f['Y']==word
        assert expected_hits==hits[collection]
        stat={'records':len(records),'source_tokens':len(tokens),'source_types':len(Counter(tokens)),
              'maximum_word_codepoints':max(map(len,tokens)),'supporting_tokens':len(expected_hits),
              'supporting_types':len({h['word']for h in expected_hits}),
              'factorizations':sum(len(h['factorizations'])for h in expected_hits),
              'status':'NECESSARY_ENVELOPE_INCONCLUSIVE'if expected_hits else'SOURCE_ENVELOPE_EXCLUDED'}
        assert stat==result['sources'][collection];tokens_checked+=len(tokens);decision.append(not expected_hits)
    expected_status='ALL_FIVE_SOURCE_EXPANSION_ENVELOPES_EXCLUDED'if all(decision)else'MIXED_OR_INCONCLUSIVE_EXPANSION_ENVELOPES'
    assert result['status']==expected_status
    out={'status':'PASS','completed_utc':datetime.now(timezone.utc).isoformat(),
         'source_tokens_checked':tokens_checked,'native_proof_events_checked':events_checked,
         'binary_fixture_cases':fixture_count,'scope':'Frozen source-cache/proof bindings; all strict interior powers independently enumerated; no new raw source reconstruction or independent meaning/palaeography.'}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
