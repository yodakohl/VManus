#!/usr/bin/env python3
import collections,csv,gzip,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def save(n,x):(E/'artifacts'/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def parse(w,alphabet):
 paths=[[] for _ in range(len(w)+1)];paths[0]=[[]]
 for i in range(len(w)):
  for u in alphabet:
   if w.startswith(u,i):paths[i+len(u)].extend(p+[u] for p in paths[i])
 return paths[-1][0] if len(paths[-1])==1 and paths[-1][0] else None
def pattern(seq):
 seen={};out=[]
 for x in seq:
  if x not in seen:seen[x]=len(seen)
  out.append(seen[x])
 return out

def main():
 lock=read(E/'src/REGISTRATION_LOCK.json')
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 s=read(E/'src/SPEC.json');allow={r['page'] for r in csv.DictReader((ROOT/s['allowlist']).open(),delimiter='\t')}
 packet={};result={}
 for ed in s['readers']:
  lines=[]
  for phase in s['phases']:
   entry,=[x for x in s['inputs'] if x['path'].endswith(f'SOURCE_{phase}_{ed}.json')]
   raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
   data=json.loads(raw);assert data['group_columns']==s['group_columns']
   for line in data['lines']:
    m=line['metadata'];page=m['page']
    if page not in allow or page in ['f1r','f116v'] or page.startswith('f84'):continue
    if m['kind']!='P' or int(m['source_group_count'])!=9:continue
    assert m['edition']==ed
    lines.append(line)
  lines.sort(key=lambda l:(l['metadata']['page'],l['metadata']['locus']))
  assert len({l['metadata']['locus'] for l in lines})==len(lines)
  cases=[];strictleaves=set();counts=collections.Counter()
  for line in lines:
   m=line['metadata'];gs=[dict(zip(s['group_columns'],r)) for r in line['groups']]
   gs.sort(key=lambda g:int(g['source_group_index']));bad=[]
   if [int(g['source_group_index']) for g in gs]!=list(range(1,10)):bad.append('indices')
   if len({g['source_group_id'] for g in gs})!=len(gs) or any(g['source_group_id']!=f"{ed}|{m['locus']}|G{int(g['source_group_index']):03d}" for g in gs):bad.append('ids')
   if any(a['right_separator']!='DEFINITE_SPACE' or b['left_separator']!='DEFINITE_SPACE' for a,b in zip(gs,gs[1:])):bad.append('seams')
   units=[parse(g['ivtff_group_raw'],s['units']) for g in gs]
   if any(u is None for u in units):bad.append('literal_parse')
   f8=None;pat=None
   if bad:status='UNSCORABLE'
   else:
    strictleaves.add(re.match(r'f\d+',m['page']).group());f8=units[7];pat=pattern(f8)
    status='LENGTH_MISMATCH' if len(f8)!=10 else 'MATCH' if pat==s['pattern'] else 'EQUALITY_PATTERN_MISMATCH'
   counts[status]+=1
   cases.append({'page':m['page'],'locus':m['locus'],'status':status,'failed_gates':bad,'field8_units':f8,'field8_pattern':pat})
  strict=len(lines)-counts['UNSCORABLE'];matches=counts['MATCH']
  status='NO_STRICT_LINE_CAPACITY' if strict==0 else 'NECESSARY_FIELD_CAPACITY_ONLY' if matches else 'NO_FIXED_EPOCH_FIELD_CANDIDATE'
  packet[ed]=lines
  result[ed]={'metadata_lines':len(lines),'strict_lines':strict,'unscorable_lines':counts['UNSCORABLE'],'strict_leaves':len(strictleaves),'matching_lines':matches,'mismatch_counts':{k:counts[k] for k in ['LENGTH_MISMATCH','EQUALITY_PATTERN_MISMATCH']},'status':status,'cases':cases}
 (E/'artifacts/CANDIDATE_LINES.json.gz').write_bytes(gzip.compress((json.dumps(packet,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
 save('RESULT.json',{'status':'NECESSARY_FIXED_EPOCH_FIELD_TEST','primary':'ZL3b','readers':result})
 print(json.dumps({ed:{k:v for k,v in x.items() if k!='cases'} for ed,x in result.items()},indent=2))
if __name__=='__main__':main()
