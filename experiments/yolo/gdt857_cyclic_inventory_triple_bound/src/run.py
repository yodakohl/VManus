import argparse,hashlib,itertools,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x,check=False):
 p=E/'artifacts'/n
 if check:assert p.read_text()==enc(x),n
 else:p.write_text(enc(x))
def scan(source,allowed):
 hits=[];lines=[];candidate=0;eligible=0
 for line in source['lines']:
  m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
  if m['kind']!='P':continue
  groups=[dict(zip(source['group_columns'],g)) for g in line['groups']];found=False
  indices=[int(g['source_group_index']) for g in groups];assert all(1<=i<=int(m['source_group_count']) for i in indices) and all(a<b for a,b in zip(indices,indices[1:]))
  for start in range(len(groups)-2):
   candidate+=1;gs=groups[start:start+3];first,last=gs[0],gs[-1]
   if not all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs):continue
   if not all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:])):continue
   if int(first['source_group_index'])!=1 and first['left_separator']!='DEFINITE_SPACE':continue
   if int(last['source_group_index'])!=int(m['source_group_count']) and last['right_separator']!='DEFINITE_SPACE':continue
   eligible+=1
   if len({g['ivtff_group_raw'] for g in gs})!=1:continue
   found=True;hits.append(dict(edition=m['edition'],locus=m['locus'],page=m['page'],physical_folio=re.match(r'f[0-9]+',m['page'])[0],start_index=first['source_group_index'],raw=first['ivtff_group_raw'],source_ids=[g['source_group_id'] for g in gs],source_indices=[g['source_group_index'] for g in gs],groups=gs,metadata=m))
  if found:lines.append(line)
 summary=dict(candidate_P_windows=candidate,eligible_plain_windows=eligible,triple_windows=len(hits),unique_forms=sorted({h['raw'] for h in hits}),physical_folios=sorted({h['physical_folio'] for h in hits}))
 return hits,lines,summary
def fixture_source(words,kind='P',indices=None,locus='f2r.1'):
 indices=indices or list(range(1,len(words)+1));groups=[]
 for i,(w,n) in enumerate(zip(words,indices)):groups.append([f'ZL3b|{locus}|G{n:03d}',str(n),w,'LINE_START' if i==0 else 'DEFINITE_SPACE','LINE_END' if i==len(words)-1 else 'DEFINITE_SPACE'])
 return dict(group_columns=['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator'],lines=[dict(metadata=dict(edition='ZL3b',page='f2r',locus=locus,kind=kind,source_group_count=str(max(indices))),groups=groups)])
def controls():
 cases=[]
 def check(name,source,n):
  h,lines,summary=scan(source,{'f2r'});assert len(h)==n;cases.append(dict(name=name,source=source,expected=n,summary=summary))
 check('plain_AAA',fixture_source(['a']*3),1);check('raw_uncertainty',fixture_source(['a?']*3),0);check('index_gap',fixture_source(['a']*3,indices=[1,2,4]),0);check('non_P',fixture_source(['a']*3,kind='L'),0)
 for group,field in [(0,4),(1,3),(1,4),(2,3)]:
  src=fixture_source(['a']*3);src['lines'][0]['groups'][group][field]='UNCERTAIN_SMALL_SPACE';check(f'internal_{group}_{field}',src,0)
 src=fixture_source(['b','a','a','a']);src['lines'][0]['groups'][1][3]='UNCERTAIN_SMALL_SPACE';check('uncertain_outer_left',src,0)
 src=fixture_source(['a','a','a','b']);src['lines'][0]['groups'][2][4]='UNCERTAIN_SMALL_SPACE';check('uncertain_outer_right',src,0)
 src=fixture_source(['a','a']);src['lines']+=fixture_source(['a','a'],locus='f2r.2')['lines'];check('no_cross_line',src,0)
 simulations=[]
 for n in [2,3]:
  perms=list(itertools.permutations('abc'[:n]));tested=0
  for cycles in itertools.product(perms,repeat=3):
   seq=''.join(''.join(c) for c in cycles)
   for phase in range(n):assert all(not(seq[i]==seq[i+1]==seq[i+2]) for i in range(phase,len(seq)-2));tested+=1
  simulations.append(dict(pool_size=n,three_cycle_phase_cases=tested))
 assert 'baab'==''.join(('ba','ab')) and 'aaa'==''.join(('a','a','a'))
 return dict(status='PASS_TOY_CYCLES_AND_SOURCE_ELIGIBILITY_CONTROLS',cases=cases,cycle_checks=simulations,mathematical_proof='METHOD.md; finite controls are not a proof')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
 if a.controls:save('CONTROLS.json',controls(),a.check);print('CONTROLS_PASS_NO_MANUSCRIPT_READ');return
 s=json.loads((E/'src/SPEC.json').read_text());hits=[];witnesslines={};summary={}
 for src in s['sources']:
  raw=(ROOT/src['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==src['sha256'];data=json.loads(raw);assert data['group_columns']==s['group_columns'];assert all(l['metadata']['edition']==src['edition'] for l in data['lines']);hh,ll,ss=scan(data,set(s['allowed_selectors']));hits+=hh;witnesslines[src['edition']]=ll;summary[src['edition']]=ss
 coordinates=[{(h['locus'],h['start_index'],h['raw']) for h in hits if h['edition']==src['edition']} for src in s['sources']];common=sorted(set.intersection(*coordinates));result=dict(status='NONSINGLETON_CYCLIC_POOL_COUNTEREXAMPLE_FOUND' if hits else 'NO_COUNTEREXAMPLE_IN_FIXED_SCOPE',summary=summary,reader_windows=len(hits),all_reader_coordinates=[list(x) for x in common],independent_manuscripts=False)
 save('HITS.json',hits,a.check);save('WITNESS_LINES.json',dict(group_columns=s['group_columns'],by_edition=witnesslines),a.check);save('RESULT.json',result,a.check);print(enc(result))
if __name__=='__main__':main()
