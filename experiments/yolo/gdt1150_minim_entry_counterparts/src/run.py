#!/usr/bin/env python3
import gzip,json,hashlib,re
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(n,x):
 b=(json.dumps(x,sort_keys=True,ensure_ascii=False,indent=None if n.endswith('.gz') else 2)+'\n').encode();(P/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def main():
 for x in load(P/'src/SOURCE.json')['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
 for n,h in load(P/'src/PREREG_LOCK.json')['hashes'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h
 old=ROOT/'experiments/yolo/gdt1149_minim_line_entry_control/artifacts'
 cases=load(old/'CASES.json.gz');base={x['source_group_id']:x for x in cases if x['class'] in ('BARE_MINIM','D_MINIM')}
 allowed=set(load(ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json')['allowed_selectors'])
 records=[];seen=set();pure=re.compile(r'^[a-z]+$')
 for ed in ('ZL3b','IT2a','RF1b'):
  for split in ('DISCOVERY','EVALUATION'):
   s=load(ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{ed}.json')
   for row in s['lines']:
    m=row['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page']!='f116v'
    if m['kind']!='P':continue
    gs=[dict(zip(s['group_columns'],g)) for g in row['groups']]
    for i,g in enumerate(gs):
     gid=g['source_group_id']
     if gid not in base:continue
     assert gid not in seen;seen.add(gid);c=base[gid];raw=g['ivtff_group_raw'];reasons=[]
     if c['scope']!='PRIMARY':reasons.append(c['scope'])
     following=gs[i+1:i+3]
     if len(following)!=2:reasons.append('FEWER_THAN_TWO_FOLLOWING_GROUPS')
     else:
      if not all(pure.fullmatch(q['ivtff_group_raw']) for q in following):reasons.append('ANNOTATED_FOLLOWING_GROUP')
      if not all(q['left_separator']=='DEFINITE_SPACE' for q in following):reasons.append('NONDEFINITE_GAP')
     records.append({**c,'tail':raw[1:] if raw.startswith('d') else raw,'form_class':'D' if raw.startswith('d') else 'BARE','following':[q['ivtff_group_raw'] for q in following],'eligible':not reasons,'exclusion_reasons':reasons,'source_line':row})
 assert seen==set(base)
 records.sort(key=lambda x:x['source_group_id']);partners=[];counts={}
 for ed in ('ZL3b','IT2a','RF1b'):
  rr=[x for x in records if x['edition']==ed];internal=[x for x in rr if x['eligible'] and x['position']=='INTERNAL'];targets=[x for x in rr if x['eligible'] and x['position']=='CONTINUATION_START' and x['form_class']=='D'];tot={s:Counter() for s in ('paragraph','leaf')}
  for t in targets:
   out={'target_id':t['source_group_id'],'edition':ed,'tail':t['tail'],'following':t['following'],'paragraph':t['paragraph'],'leaf':t['leaf']}
   for scope in ('paragraph','leaf'):
    hits=[x for x in internal if x[scope]==t[scope] and x['tail']==t['tail'] and x['following']==t['following']]
    bb=[x['source_group_id'] for x in hits if x['form_class']=='BARE'];dd=[x['source_group_id'] for x in hits if x['form_class']=='D']
    category='BOTH' if bb and dd else 'BARE_ONLY' if bb else 'D_ONLY' if dd else 'NEITHER';tot[scope][category]+=1
    out[scope]={'category':category,'BARE':bb,'D':dd}
   partners.append(out)
  counts[ed]={'all_targets':len(rr),'eligible':sum(x['eligible'] for x in rr),'eligible_D_continuation':len(targets),'exclusions':dict(Counter(y for x in rr for y in x['exclusion_reasons'])),'counterparts':{s:dict(v) for s,v in tot.items()}}
 available=[sum(counts[e]['counterparts']['paragraph'].get(k,0) for k in ('BARE_ONLY','BOTH'))>0 for e in ('ZL3b','IT2a')]
 decision='LOCAL_COUNTERPARTS_AVAILABLE' if all(available) else 'READING_SENSITIVE_COUNTERPARTS' if any(available) else 'NO_LOCAL_COUNTERPARTS'
 result={'experiment':'GDT1150','decision':decision,'readers':counts,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':'NOT_CLAIMED'}
 write('WINDOWS.json.gz',records);write('PARTNERS.json',partners);write('RESULT.json',result)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
