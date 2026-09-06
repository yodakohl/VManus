"""Independently classify all cached witnesses; no new source observation."""
import collections,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
a=json.loads((E/'src/SOURCE_AUDIT.json').read_text());r=json.loads((E/'artifacts/RESULT.json').read_text());counts=collections.Counter();seen=set()
for case in a['case_evidence']:
 key=(case['page'],case['locus'],case['surface']);assert key not in seen;seen.add(key)
 assert case['n']==1 and len(case['source_groups'])==1
 source=case['source_groups'][0];raw=source['ivtff_group_raw'];assert source['kind']=='P'
 assert source['clean_ascii_fragments']==case['surface'] and source['clean_ascii_fragment_count']=='1'
 assert raw!=case['surface']
 if raw.startswith('<@'):
  category='INLINE_METADATA';clean=re.sub(r'<[^>]+>','',raw)
 elif '[' in raw:
  category='BRACKET_ALTERNATIVE';clean=re.sub(r'\[([^:\]]+):[^\]]*\]',r'\1',raw)
 else:
  category='BRACE_REMOVAL';clean=re.sub(r'\{[^}]*\}','',raw)
 assert clean==case['surface'],case
 counts[category]+=1
assert dict(counts)=={'BRACKET_ALTERNATIVE':10,'BRACE_REMOVAL':2,'INLINE_METADATA':1}
assert r['old_count']-r['exact_raw_count']==len(seen)==sum(counts.values())==13
assert r['category_counts']==dict(counts)
out={'status':'PASS','scope':'Cached source witnesses, independent annotation reduction and arithmetic; no fresh source or vision validation.','witness_count':13,'classification_counts':dict(counts),'metadata_case':'f115r.13'}
(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('PASS')
