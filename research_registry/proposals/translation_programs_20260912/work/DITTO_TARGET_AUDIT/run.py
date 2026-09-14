"""Retrospective raw-source audit, no semantic decoder."""
import csv, hashlib, io, json, subprocess
from pathlib import Path
B=Path(__file__).resolve().parent
R=B.parents[4]
OLD=Path('experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv')
CORPUS=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json')
cmd=[str(R/'vmanus-exp'),'query-tsv',str(R/OLD),'--selector','page']
for page in ['f10r','f81v','f82r','f83r']: cmd+=['--allow',page]
cmd+=['--columns','page,record_unit_id,event_id,locus,statement_id,surface_display,joint_tuple_id']
projection=subprocess.check_output(cmd,text=True)
events=list(csv.DictReader(io.StringIO(projection),delimiter='\t'))
targets=[e for e in events if e['joint_tuple_id']=='4d4559019a961b834aa1']
assert [e['event_id'] for e in targets]==['E003','E031','E105','E199','E238']
corpus=json.loads((R/CORPUS).read_text()); audit=[]; packets={}
for e in targets:
 i=events.index(e); n=events[i+1]
 row={**e,'selected_next_locus':n['locus'],'selected_next_surface':n['surface_display'],'readings':{}}
 for edition in ['ZL3b','IT2a']:
  hits=[]
  for p in corpus[edition]:
   for li,line in enumerate(p['lines']):
    if line['locus']!=e['locus']:continue
    packets[edition+'|'+p['id']]={'edition':edition,**p}
    matches=[j for j,w in enumerate(line['words']) if w==e['surface_display']]
    occurrences=[]
    for j in matches:
     prev=line['words'][j-1] if j else None
     nxt=line['words'][j+1] if j+1<len(line['words']) else None
     successor=(line['locus'],nxt) if nxt is not None else ((p['lines'][li+1]['locus'],p['lines'][li+1]['words'][0]) if li+1<len(p['lines']) else (None,None))
     occurrences.append({'position':j+1,'left':prev,'right_same_line':nxt,'symmetric':prev is not None and prev==nxt,'source_successor':successor,'selected_successor_matches':list(successor)==[n['locus'],n['surface_display']]})
    hits.append({'paragraph':p['id'],'locus':line['locus'],'words':line['words'],'source_ids':line['source_ids'],'paragraph_start':line['start'],'paragraph_end':line['end'],'anchor_eligible':line['anchor_eligible'],'occurrences':occurrences})
  row['readings'][edition]=hits
 audit.append(row)
(B/'AUDIT.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
(B/'PARAGRAPHS.json').write_text(json.dumps(list(packets.values()),ensure_ascii=False,separators=(',',':'))+'\n')
source={'audit_kind':'retrospective','sealed':['f84','f84r'],'sources':{str(p):hashlib.sha256((R/p).read_bytes()).hexdigest() for p in [OLD,CORPUS,Path("experiments/yolo/sidequest_semantic_same_card_four_hundred_seventeenth/build_four_hundred_seventeenth.py"),Path("experiments/yolo/sidequest_semantic_same_card_four_hundred_seventeenth/FOUR_HUNDRED_SEVENTEENTH_REPORT.md"),Path("experiments/yolo/sidequest_semantic_whole_card_reduction_four_hundred_fifty_eighth/FOUR_HUNDRED_FIFTY_EIGHTH_REPORT.md")]},'projection_sha256':hashlib.sha256(projection.encode()).hexdigest(),'decision_sha256':hashlib.sha256((B/'DECISION.md').read_bytes()).hexdigest()}
(B/'SOURCE.json').write_text(json.dumps(source,indent=2)+'\n')
for row in audit:
 print(row['event_id'],row['locus'],row['surface_display'])
 for ed,hits in row['readings'].items():
  print(ed,[(h['words'],h['occurrences']) for h in hits])
