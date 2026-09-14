#!/usr/bin/env python3
import csv,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def write_json(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def extract():
 spec=json.loads((E/'src/SPEC.json').read_text());lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 lines={};occ=[];fams=set(map(tuple,spec['families']))
 for source in spec['sources']:
  d=json.loads((ROOT/source).read_text())
  for ln in d['lines']:
   m=ln['metadata'];assert not m['page'].startswith('f84') and m['page']!='f116v'
   if m['kind']!='P':continue
   key=(m['edition'],m['locus']);assert key not in lines
   groups=[dict(zip(d['group_columns'],g)) for g in ln['groups']]
   lines[key]=dict(metadata=m,groups=groups,source=source)
   for i,(a,b) in enumerate(zip(groups,groups[1:])):
    wa,wb=a['ivtff_group_raw'],b['ivtff_group_raw']
    if not all(re.fullmatch('[a-z]+',w) and w[-1] in 'rl' for w in [wa,wb]):continue
    if (wa[:-1],wb[:-1]) not in fams:continue
    if int(b['source_group_index'])!=int(a['source_group_index'])+1 or a['right_separator']!=b['left_separator'] or a['right_separator']!='DEFINITE_SPACE':continue
    occ.append(dict(edition=m['edition'],locus=m['locus'],page=m['page'],family=wa[:-1]+'/'+wb[:-1],cell=wa[-1]+wb[-1],words=[wa,wb],ids=[a['source_group_id'],b['source_group_id']],group_count=len(groups)))
 selected=[]
 for fam in spec['families']:
  rows=[o for o in occ if o['edition']=='ZL3b' and o['family']=='/'.join(fam)]
  pairs=[(a,b) for a in rows if a['cell']=='rr' for b in rows if b['cell']=='ll' and re.match(r'f\d+',a['page'])[0]!=re.match(r'f\d+',b['page'])[0]]
  if not pairs:continue
  a,b=min(pairs,key=lambda pair:(sum(o['group_count'] for o in pair),tuple((o['page'],o['locus'],o['ids']) for o in pair)))
  selected.extend([dict(family='/'.join(fam),cell=o['cell'],locus=o['locus'],page=o['page']) for o in [a,b]])
 loci={s['locus'] for s in selected};packet=[v for (ed,locus),v in sorted(lines.items()) if locus in loci]
 allkeys={(o['edition'],o['locus']) for o in occ}
 write_json(E/'artifacts/ALL_OCCURRENCES.json',occ)
 write_json(E/'artifacts/ALL_MATCHING_LINES.json',[lines[k] for k in sorted(allkeys)])
 write_json(E/'artifacts/SOURCE_PACKET.json',dict(selection=selected,lines=packet))
 out=['# Selected complete physical lines (hypothesis development)','','Chosen by frozen length/leaf rule, not semantic fit. Physical lines are not proven sentences.','']
 for ln in packet:
  m=ln['metadata'];out += [f"## {m['edition']} {m['locus']}",'','`'+' '.join(g['ivtff_group_raw'] for g in ln['groups'])+'`','']
 (E/'artifacts/SOURCE_PACKET.md').write_text('\n'.join(out).rstrip()+'\n')
 return dict(selection=selected,occurrences=len(occ),complete_lines=len(allkeys),reading_lines=len(packet))
if __name__=='__main__':print(json.dumps(extract(),indent=2))
