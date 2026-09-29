#!/usr/bin/env python3
"""Exploratory AFTER-result display counts and two retained nonedge contexts."""
import csv,json
from pathlib import Path
from run import R,E,read,table
rows=list(csv.DictReader((E/'artifacts/OCCURRENCES.tsv').open(),delimiter='\t'))
post={'status':'EXPLORATORY_POST_RESULT_NOT_REGISTERED_SELECTOR','based_on':'artifacts/OCCURRENCES.tsv','by_reader':{}}
for ed in ['ZL3b','IT2a','RF1b']:
 rr=[r for r in rows if r['edition']==ed]
 post['by_reader'][ed]={'all':len(rr),'before_physical_line_end':sum(r['right_separator']=='LINE_END' for r in rr),'before_drawing_interruption':sum(r['right_separator']=='DRAWING_INTERRUPTION' for r in rr),'other_ids':[r['source_group_id'] for r in rr if r['right_separator'] not in ['LINE_END','DRAWING_INTERRUPTION']],'line_end_READY_with_following_paragraph_groups':sum(r['right_separator']=='LINE_END' and r['eligibility']=='READY' and int(r['available_right'])>0 for r in rr)}
post.update(significance=False,meaning_selected=False,s_sy_equivalence_established=False,new_image_access=False)
(E/'artifacts/POST_RESULT_LAYOUT.json').write_text(json.dumps(post,indent=2)+'\n')
m=json.loads((E/'src/MODEL.json').read_text());allow=set(read(m['allow_source'])['allowed_selectors']);cuts=[]
for path in m['sources']:
 d=read(path)
 for line in d['lines']:
  meta=line['metadata']
  assert meta['page'] in allow and not meta['page'].startswith('f84')
  if meta['locus'] not in ['f5v.2','f83r.33']:continue
  for g in line['groups']:
   group=dict(zip(d['group_columns'],g))
   cuts.append({k:meta[k] for k in ['edition','page','locus']}|{k:group[k] for k in ['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']})
assert len({(r['edition'],r['locus']) for r in cuts})==6
(E/'artifacts/POST_RESULT_BOUNDARIES.tsv').write_text(table(cuts))
print(json.dumps(post['by_reader']))
