"""Independent line-window enumeration and direct source-witness checks."""
import argparse,hashlib,itertools,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(n):return json.loads((E/'artifacts'/n).read_text())
def enumerate_source(source,allowed):
 output=[];witness_lines=[];candidate=0;plain=0
 for line in source['lines']:
  m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
  if m['kind']!='P':continue
  rows=[dict(zip(source['group_columns'],g)) for g in line['groups']];linehit=False
  indices=[int(g['source_group_index']) for g in rows];assert all(1<=i<=int(m['source_group_count']) for i in indices) and indices==sorted(set(indices))
  for end in range(2,len(rows)):
   candidate+=1;triple=[rows[end-2],rows[end-1],rows[end]];nums=[int(g['source_group_index']) for g in triple]
   if nums[1]-nums[0]!=1 or nums[2]-nums[1]!=1:continue
   if any(re.fullmatch(r'[a-z]+',g['ivtff_group_raw']) is None for g in triple):continue
   seam_values=[triple[0]['right_separator'],triple[1]['left_separator'],triple[1]['right_separator'],triple[2]['left_separator']]
   if any(v!='DEFINITE_SPACE' for v in seam_values):continue
   if nums[0]!=1 and triple[0]['left_separator']!='DEFINITE_SPACE':continue
   if nums[2]!=int(m['source_group_count']) and triple[2]['right_separator']!='DEFINITE_SPACE':continue
   plain+=1
   a,b,c=[g['ivtff_group_raw'] for g in triple]
   if a!=b or b!=c:continue
   linehit=True;output.append(dict(edition=m['edition'],locus=m['locus'],page=m['page'],physical_folio='f'+re.match(r'f([0-9]+)',m['page'])[1],start_index=triple[0]['source_group_index'],raw=a,source_ids=[g['source_group_id'] for g in triple],source_indices=[g['source_group_index'] for g in triple],groups=triple,metadata=m))
  if linehit:witness_lines.append(line)
 return output,witness_lines,dict(candidate_P_windows=candidate,eligible_plain_windows=plain,triple_windows=len(output),unique_forms=sorted({h['raw'] for h in output}),physical_folios=sorted({h['physical_folio'] for h in output}))
def check_controls():
 c=read('CONTROLS.json')
 for case in c['cases']:
  hits,lines,summary=enumerate_source(case['source'],{'f2r'});assert len(hits)==case['expected'] and summary==case['summary']
 for n in [2,3]:
  permutations=list(itertools.permutations(range(n)));count=0
  for x in permutations:
   for y in permutations:
    for z in permutations:
     stream=x+y+z
     for phase in range(n):
      assert all(len(set(stream[i:i+3]))!=1 for i in range(phase,len(stream)-2));count+=1
  assert next(x['three_cycle_phase_cases'] for x in c['cycle_checks'] if x['pool_size']==n)==count
 assert ('b','a')+('a','b')==tuple('baab') and ('a',)*3==tuple('aaa')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args();check_controls()
 if a.controls:print('INDEPENDENT_CONTROLS_PASS_NO_MANUSCRIPT_READ');return
 s=json.loads((E/'src/SPEC.json').read_text());expected=[];lines={};summary={};allsource={}
 for src in s['sources']:
  raw=(ROOT/src['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==src['sha256'];data=json.loads(raw);assert data['group_columns']==s['group_columns'];assert all(l['metadata']['edition']==src['edition'] for l in data['lines']);hh,ll,ss=enumerate_source(data,set(s['allowed_selectors']));expected+=hh;lines[src['edition']]=ll;summary[src['edition']]=ss
  for l in data['lines']:
   for values in l['groups']:
    g=dict(zip(data['group_columns'],values));assert g['source_group_id'] not in allsource;allsource[g['source_group_id']]=(g,l['metadata'])
 actual=read('HITS.json');assert actual==expected
 for h in actual:
  assert len(set(h['source_ids']))==3
  for sid,g in zip(h['source_ids'],h['groups']):assert allsource[sid]==(g,h['metadata'])
 assert read('WITNESS_LINES.json')==dict(group_columns=s['group_columns'],by_edition=lines)
 union={tuple([h['locus'],h['start_index'],h['raw']]) for h in actual};common=sorted(c for c in union if all(any(h['edition']==ed and (h['locus'],h['start_index'],h['raw'])==c for h in actual) for ed in ['ZL3b','IT2a','RF1b']))
 r=read('RESULT.json');assert r==dict(status='NONSINGLETON_CYCLIC_POOL_COUNTEREXAMPLE_FOUND' if actual else 'NO_COUNTEREXAMPLE_IN_FIXED_SCOPE',summary=summary,reader_windows=len(actual),all_reader_coordinates=[list(c) for c in common],independent_manuscripts=False)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_TRIPLE_ENUMERATION_AND_DIRECT_SOURCE_WITNESSES',reader_windows=len(actual),all_reader_coordinates=len(common),native_image_validation=False,semantic_validation=False),indent=2)+'\n');print('PASS')
if __name__=='__main__':main()
