#!/usr/bin/env python3
import json,gzip,hashlib,re,csv
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parents[1];R=P.parents[2]
def load(p):return json.loads(p.read_text())
def out(n,x):
 b=(json.dumps(x,sort_keys=True,ensure_ascii=False,indent=None if n.endswith('.gz') else 2)+'\n').encode();(P/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def main():
 for x in load(P/'src/SOURCE.json')['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 for s,h in load(P/'src/PREREG_LOCK.json')['hashes'].items():assert hashlib.sha256((P/s).read_bytes()).hexdigest()==h
 allow=set(load(R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json')['allowed_selectors']);lines={};groups={};events=[];blocks=load(R/'experiments/yolo/gdt1149_minim_line_entry_control/artifacts/BLOCKS.json');membership={}
 for b in blocks:
  for l in b['loci']:assert (b['edition'],l) not in membership;membership[(b['edition'],l)]=b['id']
 for ed in ('ZL3b','IT2a','RF1b'):
  for split in ('DISCOVERY','EVALUATION'):
   src=load(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{ed}.json')
   for row in src['lines']:
    m=row['metadata'];assert m['page'] in allow and not m['page'].startswith('f84') and m['page']!='f116v'
    if m['kind']!='P':continue
    key=(ed,m['locus']);assert key not in lines;lines[key]=row;gs=[dict(zip(src['group_columns'],g)) for g in row['groups']];groups[key]=gs
    for g in gs:
     if g['ivtff_group_raw']=='ol':events.append({**g,'edition':ed,'page':m['page'],'locus':m['locus'],'paragraph':membership.get(key)})
 cases=[]
 for block in blocks:
  ed=block['edition'];stream=[g for l in block['loci'] for g in groups[ed,l]];idx=[i for i,g in enumerate(stream) if g['ivtff_group_raw']=='ol']
  if not idx:continue
  scorable=all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in stream);fields=[];pairs=[]
  for j in range(0,len(idx)-1,2):
   a,b=idx[j:j+2];fields.append({'open_id':stream[a]['source_group_id'],'close_id':stream[b]['source_group_id'],'content_ids':[g['source_group_id'] for g in stream[a+1:b]],'empty':b==a+1})
  for j in range(len(idx)-1):
   if idx[j+1]==idx[j]+1:pairs.append({'left_id':stream[idx[j]]['source_group_id'],'right_id':stream[idx[j+1]]['source_group_id'],'first_ol_ordinal':j+1,'direction':'OPEN_CLOSE' if j%2==0 else 'CLOSE_OPEN','violating':j%2==0})
  odd=len(idx)%2==1;empty=sum(f['empty'] for f in fields);decision='UNTESTABLE_ANNOTATION' if not scorable else 'CONTRADICTION' if odd or empty else 'COMPATIBLE'
  cases.append({**block,'leaf':int(re.match('f([0-9]+)',block['page']).group(1)),'ol_count':len(idx),'group_count':len(stream),'scorable':scorable,'decision':decision,'ol_events':[{'id':stream[i]['source_group_id'],'paragraph_group_index':i+1,'ol_ordinal':j+1,'role':'OPEN' if j%2==0 else 'CLOSE'} for j,i in enumerate(idx)],'fields':fields,'adjacent_pairs':pairs,'unmatched_open':stream[idx[-1]]['source_group_id'] if odd else None,'empty_fields':empty,'raw_lines':[lines[ed,l] for l in block['loci']]})
 summary={}
 for ed in ('ZL3b','IT2a','RF1b'):
  cc=[c for c in cases if c['edition']==ed];ss=[c for c in cc if c['scorable']];contr=[c for c in ss if c['decision']=='CONTRADICTION'];ee=[x for x in events if x['edition']==ed]
  summary[ed]={'all_P_ol':len(ee),'unbounded_ol':sum(x['paragraph'] is None for x in ee),'complete_paragraphs':sum(b['edition']==ed for b in blocks),'ol_bearing_paragraphs':len(cc),'scorable_paragraphs':len(ss),'scorable_leaves':len(set(c['leaf'] for c in ss)),'paragraph_decisions':dict(Counter(c['decision'] for c in cc)),'scorable_odd_paragraphs':sum(c['unmatched_open'] is not None for c in ss),'scorable_empty_field_paragraphs':sum(c['empty_fields']>0 for c in ss),'scorable_adjacent_pair_paragraphs':sum(bool(c['adjacent_pairs']) for c in ss),'scorable_adjacent_pair_directions':dict(Counter(p['direction'] for c in ss for p in c['adjacent_pairs'])),'decision':'REFUTED_FIXED_PAIRED_FIELD_SCOPE' if contr else 'COMPATIBLE_UNSELECTED' if ss else 'INSUFFICIENT_CAPACITY'}
 primary=[summary[e] for e in ('ZL3b','IT2a')]
 dec='REFUTED_FIXED_PAIRED_FIELD_SCOPE' if any(r['decision']=='REFUTED_FIXED_PAIRED_FIELD_SCOPE' for r in primary) else 'PROVISIONAL_SCOPE_COMPATIBILITY' if all(r['scorable_paragraphs']>=10 and r['scorable_leaves']>=5 and r['scorable_adjacent_pair_paragraphs']>=2 for r in primary) else 'INSUFFICIENT_CAPACITY'
 result={'experiment':'GDT1151','decision':dec,'readers':summary,'confirmed_words':0,'independent_confirmation_capacity':0,'significance':'NOT_CLAIMED'}
 out('PARAGRAPHS.json.gz',cases);out('OCCURRENCES.json',events);out('RESULT.json',result)
 with (P/'artifacts/PARAGRAPH_DECISIONS.tsv').open('w') as f:
  keys=['edition','id','page','line_count','group_count','ol_count','scorable','decision','unmatched_open','empty_fields'];w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader()
  for c in cases:w.writerow({k:c[k] for k in keys})
 with (P/'artifacts/ADJACENT_PAIRS.tsv').open('w') as f:
  keys=['edition','paragraph','scorable','decision','left_id','right_id','first_ol_ordinal','direction','violating'];w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader()
  for c in cases:
   for q in c['adjacent_pairs']:w.writerow({'edition':c['edition'],'paragraph':c['id'],'scorable':c['scorable'],'decision':c['decision'],**q})
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
