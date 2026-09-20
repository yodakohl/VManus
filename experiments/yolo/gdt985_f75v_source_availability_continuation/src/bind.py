import argparse,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');args=p.parse_args()
up=['experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json','experiments/yolo/gdt982_reciprocal_flow_clause_readings/REPORT.md','experiments/yolo/gdt982_reciprocal_flow_clause_readings/src/CANDIDATES.json','experiments/yolo/gdt982_reciprocal_flow_clause_readings/artifacts/RESULT.json','research_registry/proposals/translation_programs_20260912/work/W56/REPORT.md','research_registry/proposals/translation_programs_20260912/work/W58/REPORT.md','research_registry/proposals/translation_programs_20260912/work/W59/REPORT.md','research_registry/proposals/raw_f80r_plane_mirror_assertions.json','research_registry/proposals/raw_f17r_seed_extraction_sowing.json','experiments/yolo/gdt943_solkain_second_leaf_complete_clause/REPORT.md','experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/REPORT.md','experiments/yolo/gdt768_chor_shor_part_identity_tournament/REPORT.md','experiments/yolo/gdt813_f17_content_word_transfer/REPORT.md']
up += [f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{ed}.json' for ed in ['ZL3b','IT2a','RF1b'] for split in ['DISCOVERY','EVALUATION']]
lock=E/'PREREG_LOCK.json'
if args.register:
 assert not lock.exists()
 paths=[p for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts]+[R/n for n in up]
 dump(lock,{'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'CONDITIONAL_SAME_PORTION_SOURCE_AVAILABILITY','files':{p.relative_to(R).as_posix():sha(p) for p in paths}})
for n,h in json.loads(lock.read_text())['files'].items():assert sha(R/n)==h,n
m=json.loads((E/'experiment.json').read_text());rr=E/'artifacts/RESULT.json';vv=E/'artifacts/VALIDATION.json';rel=E.relative_to(R).as_posix()
m.update(title='Conditional source availability in the complete f75v continuation',question='Which shared whole-word location effects are forced by a new same-portion/source-check reading of the complete f75v40-42 continuation?',status=json.loads(rr.read_text())['status'] if rr.exists() else 'REGISTERED_UNEXECUTED',claim_ceiling='Conditional exposed-text role obligation; no selected meaning, full paragraph translation, independent relation, significance or reserve opening.',dependencies=['GDT768','GDT796','GDT813','GDT915','GDT928','GDT943','GDT982'],inputs=[{'path':n,'sha256':sha(R/n),'role':'fixed_input'} for n in up],outputs=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'role':'primary_report' if p.name=='REPORT.md' else 'source_or_artifact'} for p in sorted(E.rglob('*')) if p.is_file() and p.name!='experiment.json' and '__pycache__' not in p.parts],validation={'status':json.loads(vv.read_text())['status'] if vv.exists() else 'NOT_RUN','artifact':rel+'/artifacts/VALIDATION.json' if vv.exists() else None})
dump(E/'experiment.json',m);print(m['status'])
