"""Exact admitted labels and existing fixed descriptive priors. No training."""
from pathlib import Path
import csv,datetime,hashlib,importlib.util,io,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from tools import word_profiles
D=Path(__file__).resolve().parents[1]
go=json.loads((D/'artifacts/TEXT_QUERY_GO.json').read_text())
assert go['all_native_records_frozen'] is True
for n in ('GB23_NATIVE_READING.json','C2_NATIVE_READING.json','INDEPENDENT_NATIVE_READING.json'):
    if not (D/'artifacts'/n).is_file(): raise SystemExit('Native freeze missing: '+n)
source='experiments/semantic_assumptions/results/source_separator_transcription.tsv'
cmd=['./vmanus-exp','query-tsv',source,'--selector','locus','--allow','f102r2.21','--allow','f102r2.22','--allow','f102v1.17','--columns',','.join(word_profiles.SOURCE_COLUMNS),'--forbid-prefix','f84','--forbid-prefix','f84r']
p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
(D/'artifacts/CACHED_LABELS.tsv').write_text(p.stdout)
rows=list(csv.DictReader(io.StringIO(p.stdout),delimiter='\t'))
assert len(rows)==9
forms=sorted({row['ivtff_group_raw'] for row in rows})
conn=word_profiles.ensure_cache()
cards=[word_profiles.profile(conn,f,limit=3) for f in forms]
conn.close()
(D/'artifacts/WORD_PROFILES.json').write_text(json.dumps(cards,indent=2)+'\n')
fixed=ROOT/'experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py'
spec=importlib.util.spec_from_file_location('gdt605_fixed_separator',fixed);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
merges=ROOT/'experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv'
with merges.open() as f:rules=[(row['left'],row['right'],row['merged'],int(row['train_occurrences'])) for row in csv.DictReader(f,delimiter='\t')]
units=[]
for form in forms:
    if re.fullmatch('[a-z]+',form):
        collapsed=mod.collapse(form); units.append({'form':form,'collapsed':collapsed,'fixed605_units':list(mod.apply_bpe(collapsed,rules)),'status':'FORMAL_FIXED_MODEL_PROJECTION_NOT_MORPHOLOGY'})
    else:units.append({'form':form,'status':'RAW_ENTITY_OR_UNCERTAINTY_NOT_SILENTLY_NORMALIZED'})
role_path=ROOT/'experiments/yolo/gdt608_compositional_stem_orientation/artifacts/unit_profiles.tsv'
tree_path=ROOT/'experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv'
with role_path.open() as f:role_rows=list(csv.DictReader(f,delimiter='\t'))
with tree_path.open() as f:tree_rows=list(csv.DictReader(f,delimiter='\t'))
for item in units:
    projected=set(item.get('fixed605_units',[]))
    item['fixed608_unit_profiles']=[r for r in role_rows if r['unit'] in projected]
    item['fixed608_merge_nodes']=[r for r in tree_rows if r['merged'] in projected]
(D/'artifacts/FIXED_COMPOSITION.json').write_text(json.dumps(units,indent=2)+'\n')
inputs=[source,'tools/word_profiles.py',str(fixed.relative_to(ROOT)),str(merges.relative_to(ROOT)),str(word_profiles.ALLOWLIST),str(role_path.relative_to(ROOT)),str(tree_path.relative_to(ROOT))]
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exact_command':cmd,'guard_statistics_stderr':p.stderr,'rows':len(rows),'forms':forms,'cache_selector_count':179,'cache_matching':'exact_raw_group','target_labels_not_added_to179':True,'input_hashes':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in inputs},'query_GO_sha256':hashlib.sha256((D/'artifacts/TEXT_QUERY_GO.json').read_bytes()).hexdigest(),'native_freeze_hashes':{n:hashlib.sha256((D/'artifacts'/n).read_bytes()).hexdigest() for n in ('GB23_NATIVE_READING.json','C2_NATIVE_READING.json','INDEPENDENT_NATIVE_READING.json')},'no_new_parser_or_training':True}
(D/'artifacts/TEXT_QUERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'forms':forms,'fixed_units':units}))
