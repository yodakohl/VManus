"""Verify the derived bound against old report tables; no native group parsing."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3]
BASE=Path('research_registry/proposals/production_origin_supply_20261003')
p=ROOT/BASE/'BINARY_WORD_RANK_BOUND_20261011.json';note=json.loads(p.read_text())
for name,sha in note['input_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
old=json.loads((ROOT/'experiments/yolo/gdt1319_cross_word_endpoint_state/artifacts/RESULT.json').read_text())['readers']
table={}
for line in (ROOT/'experiments/yolo/gdt1312_binary_whole_code_capacity/REPORT.md').read_text().splitlines():
 cells=[v.strip() for v in line.split('|')[1:-1]]
 if len(cells)==4 and cells[0] in ['m','n','n,m']:
  table[frozenset(cells[0].split(','))]=[int(re.match(r'\d+',s).group()) for s in cells[1:]]
assert len(table)==3
alphabet=set('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split());checks=0
for column,ed in enumerate(['ZL3b','IT2a','RF1b']):
 r=note['readers'][ed];heads={s.split(':',1)[1] for s in old[ed]['active_nodes'] if s.startswith('I:')};possible=sorted(alphabet-heads);assert r['required_one_drawings']==sorted(heads) and r['candidate_zero_drawings']==possible and r['strict_groups']==old[ed]['groups'];expected={}
 for mask in range(1,2**len(possible)):
  zero=frozenset(possible[i] for i in range(len(possible)) if mask&(1<<i));assert not zero&heads;expected[zero]=table[zero][column]
 actual={frozenset(x['necessary_zero_set']):x['old_full_panel_distinct_bitstrings'] for x in r['necessary_candidates_not_validated_keys']};assert actual==expected;assert r['observed_source_rank_upper_bound']==max(expected.values());checks+=len(expected)
out={'status':'PASS','necessary_zero_sets_verified':checks,'reader_upper_bounds':{ed:r['observed_source_rank_upper_bound'] for ed,r in note['readers'].items()},'scope':'Old hash-bound head summaries and separately parsed published1312table; no native census, complete-head claim, attainable-key claim or word meaning.'}
(ROOT/BASE/'BINARY_WORD_RANK_BOUND_VALIDATION_20261011.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
