import argparse,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def inspect(a,b):
 defects=[]
 if a[3] not in {'DEFINITE_SPACE','LINE_START'}:defects.append('TARGET_LEFT_BOUNDARY')
 if b is None:return defects+['NO_FOLLOWER']
 if int(b[1])-int(a[1])!=1:defects.append('INDEX_GAP')
 if {a[4],b[3]}!={'DEFINITE_SPACE'}:defects.append('INTERNAL_SEAM')
 if b[4] not in {'DEFINITE_SPACE','LINE_END'}:defects.append('FOLLOWER_RIGHT_BOUNDARY')
 if not b[2] or any(c<'a' or c>'z' for c in b[2]):defects.append('FOLLOWER_NOT_PLAIN_ASCII')
 return defects
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args();x=['a','1','qo','LINE_START','DEFINITE_SPACE'];y=['b','2','qokain','DEFINITE_SPACE','LINE_END'];assert inspect(x,y)==[] and inspect(x,None)==['NO_FOLLOWER'];assert inspect(x,['b','3','@167;','UNCERTAIN_SMALL_SPACE','UNKNOWN'])==['INDEX_GAP','INTERNAL_SEAM','FOLLOWER_RIGHT_BOUNDARY','FOLLOWER_NOT_PLAIN_ASCII'];assert inspect(['a','1','qo','UNKNOWN','DEFINITE_SPACE'],y)==['TARGET_LEFT_BOUNDARY']
 if a.controls:print('INDEPENDENT CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());expected=[];known={};summary={};allkeys=[]
 for ed,q in s['sources'].items():
  raw=(ROOT/q['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==q['sha256'];source=json.loads(raw);assert source['group_columns']==s['group_columns'];loci=[line['metadata']['locus'] for line in source['lines']];assert len(set(loci))==len(loci), 'Duplicate locus records';local=[];known[ed]=[]
  for line in source['lines']:
   m=line['metadata'];assert m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84') and m['edition']==ed
   if m['locus']=='f111v.21':known[ed].append(line)
   if m['kind']!='P':continue
   groups=line['groups']
   for index in range(len(groups)):
    g=groups[index]
    if g[2]!='qo':continue
    follow=groups[index+1] if index+1<len(groups) else None;defects=inspect(g,follow);eligible=len(defects)==0;local.append(dict(edition=ed,line=line,group=g,follower=follow,eligible=eligible,echo=eligible and follow[2][:2]=='qo',ineligibility_reasons=defects,coordinate=[m['locus'],int(g[1]),follow[2]] if follow else None))
  expected+=local;counts=dict(occurrences=len(local),eligible=0,echo=0,non_echo=0,unscorable=0,exposed_line_count=len(known[ed]));keys=set()
  for row in local:
   if not row['eligible']:counts['unscorable']+=1
   else:
    counts['eligible']+=1;counts['echo' if row['echo'] else 'non_echo']+=1;keys.add(tuple(row['coordinate']))
  summary[ed]=counts;allkeys.append(keys)
 common=sorted(k for k in allkeys[0] if all(k in ks for ks in allkeys[1:]));negative=[list(k) for k in common if k[2][:2]!='qo'];result=dict(status='STRICT_ECHO_COUNTEREXAMPLE' if negative else 'NO_ALL_READER_HARD_COUNTEREXAMPLE',summary=summary,all_reader_eligible_coordinates=[list(k) for k in common],all_reader_non_echo_coordinates=negative,known_locus='f111v.21')
 for n,v in [('OCCURRENCES.json',expected),('EXPOSED_LINES.json',known),('RESULT.json',result)]:assert json.loads((E/'artifacts'/n).read_text())==v,n
 v=dict(status='PASS',independent_eligibility_and_concordance=True,source_hash_scope_full_line_parity=True,occurrences_checked=len(expected),controls='PASS');(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(v))
if __name__=='__main__':main()
