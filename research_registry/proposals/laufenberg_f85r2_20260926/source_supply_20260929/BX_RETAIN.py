#!/usr/bin/env python3
"""Retain scoped, guard-selected evidence for a native exploratory label reading."""
import csv,hashlib,io,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
LOCI=[f'f83r.{n}' for n in (45,46,47,48,49,50,51,52,53,54,55)]
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def query(path,selector,allows,columns):
 cmd=['./vmanus-exp','query-tsv',path,'--selector',selector]
 for v in allows:cmd+=['--allow',v]
 cmd+=['--columns',columns]
 r=subprocess.run(cmd,cwd=ROOT,check=True,text=True,capture_output=True)
 return dict(command=cmd,stderr=r.stderr,rows=list(csv.DictReader(io.StringIO(r.stdout),delimiter='\t')),input_sha256=sha(path))
queries=[
 query('experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv','source_selector',['f83r'],'page_ordinal,physical_page,source_selector'),
 query('experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_27_LABEL_OWNER_ATLAS.tsv','page',['f83r'],'page,locus,label_surface,panel_id,component_id,owner_class,local_position,attachment_relation,evidence_basis,semantic_ceiling'),
 query('experiments/semantic_assumptions/results/source_separator_transcription.tsv','locus',LOCI,'source_group_id,edition,locus,page,kind,grammar_scope,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw')]
assert len(queries[0]['rows'])==1 and len(queries[1]['rows'])==4
rows=queries[-1]['rows'];assert {r['edition'] for r in rows}=={'ZL3b','IT2a','RF1b'}
assert all(r['locus'] in LOCI for r in rows)
queries += [query('experiments/semantic_assumptions/results/source_separator_transcription.tsv','locus',[f'f75v.{n}' for n in range(1,43)]+['f82r.35'],'source_group_id,edition,locus,page,kind,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw')]
packet=dict(schema='bx-exploratory-four-label-source-v1',scope=LOCI,queries=queries,
 image=dict(path='experiments/yolo/gdt996_f83r_candidate_seam_consequences/artifacts/YALE_1006224_ORIGINAL.jpg',sha256=sha('experiments/yolo/gdt996_f83r_candidate_seam_consequences/artifacts/YALE_1006224_ORIGINAL.jpg'),existing_admission='GDT791 f83r',prior_exposure=True),
 new_data_admission=False,reserves_opened=False,independent_confirmation_capacity=0)
(BASE/'BX_SOURCE.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n')
by={}
for r in rows:by.setdefault((r['edition'],r['locus']),[]).append(r)
lines=['# BX retained complete embedded contexts and all four labels','', 'Raw spellings, entities, separators and native flags retained in BX_SOURCE.json. GDT790 owner labels are a separate model, not normalization of the current readers.','']
for (e,locus),r in sorted(by.items()):
 r.sort(key=lambda x:int(x['source_group_index']))
 assert [int(x['source_group_index']) for x in r]==list(range(1,len(r)+1))
 assert all(int(x['source_group_count'])==len(r) for x in r)
 raw=' '.join(x['ivtff_group_raw'] for x in r)
 lines += [f'- {e} {locus}: `{raw}`; kind={r[0]["kind"]}, start={r[0]["paragraph_start"]}, end={r[-1]["paragraph_end"]}.']
(BASE/'BX_CONTEXTS.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
