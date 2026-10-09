#!/usr/bin/env python3
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import gzip,hashlib,json,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
spec=json.loads((D/'src/SPEC.json').read_text());result=json.loads((A/'RESULT.json').read_text())
for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
assert json.loads((ROOT/spec['prior_validation']).read_text())['status']=='PASS'
source=[{'ref':s['ref'],'word_index':i,'word':w}for s in json.loads((ROOT/spec['source_projection']).read_text())['source_sections']for i,w in enumerate(s['words'])]
assert source==json.loads(gzip.decompress((A/'SOURCE_WORDS.json.gz').read_bytes()))
assert len(source)==6288
native=json.loads(gzip.decompress((ROOT/spec['native_runs']).read_bytes()))
saved=json.loads(gzip.decompress((A/'POSITIONAL_SUPPORT.json.gz').read_bytes()))
assert set(saved)=={'LOGICAL','REVERSED'};checked=0;failed_cases=0
for orient in ['LOGICAL','REVERSED']:
    words=[x['word'][::-1]if orient=='REVERSED'else x['word']for x in source]
    assert set(saved[orient])==set(spec['readers'])
    for ed in spec['readers']:
        target=[x for x in native[ed]if x['length']>=3];records=saved[orient][ed];assert len(target)==len(records)
        bad=[]
        for r,out in zip(target,records):
            n=len(r['units']);a=r['start']+1;b=r['start']+r['length']
            assert 0<=a<b<=n and not r['page'].startswith(('f84','f116v'))
            same=[i for i,w in enumerate(words)if len(w)==n]
            hits=[i for i in same if len(set(words[i][a:b]))==1]
            reason='SUPPORTED_NECESSARY_ONLY'if hits else'NO_SOURCE_WORD_OF_LENGTH'if not same else'NO_REQUIRED_POSITIONAL_RUN'
            assert out==r|{'source_indices':hits,'same_length_source_tokens':len(same),'reason':reason}
            if not hits:bad.append(out)
            checked+=1
        unique={x['id']:x for x in bad};form_rows=defaultdict(list)
        for row in unique.values():form_rows[row['ivtff_group_raw']].append(row)
        forms=[]
        for w,rs in sorted(form_rows.items()):
            forms.append({'word':w,'groups':len(rs),'physical_leaves':len({re.match('f[0-9]+',r['page'])[0]for r in rs}),
                          'all_loci':[{k:r[k]for k in ['id','page','locus','source_group_index']}for r in rs]})
        expected={'runs':len(records),'supported_runs':len(records)-len(bad),'unsupported_runs':len(bad),'unsupported_groups':len(unique),'unsupported_forms':forms,
                  'unsupported_by_reason':dict(sorted(Counter(r['reason']for r in bad).items())),
                  'unsupported_by_run_length':{str(k):v for k,v in sorted(Counter(r['length']for r in bad).items())},
                  'status':'SOURCE_ENVELOPE_EXCLUDED'if bad else'NECESSARY_ENVELOPE_INCONCLUSIVE'}
        assert result['cases'][orient][ed]==expected;failed_cases+=bool(bad)
assert result['status']==('ALL_READINGS_BOTH_ORIENTATIONS_EXCLUDED'if failed_cases==6 else'MIXED_OR_INCONCLUSIVE')
toy=json.loads((A/'FIXTURES.json').read_text())['words']
for a,k,expect in [(1,2,[0,1,3]),(0,3,[0,3]),(1,3,[1,3]),(0,5,[3]),(1,5,[])]:
    assert [i for i,w in enumerate(toy)if a+k<=len(w)and len(set(w[a:a+k]))==1]==expect
v={'experiment':'GDT1239','status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'direct_support_checks':checked,'failed_cases':failed_cases,
   'checks':['frozen hashes and prior validated source','all full source words and exact order','all selected native runs, both orientations','direct same-length source slicing versus index','every support index, failure reason and whole-form provenance','longer-run and position fixtures'],
   'limits':'Independent implementation by same root author; not independent manuscript or semantic evidence.'}
(A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
